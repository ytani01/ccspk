"""Stop / MessageDisplay / PreToolUse hook: Claude の返答を VOICEVOX で読み上げる。

Stop では最後の返答を、MessageDisplay ではツールを呼ぶ前などの途中の文章を、
PreToolUse（AskUserQuestion）では質問の文を読む。
環境変数 CCSPK_SPEAK が 1 のときだけ鳴らす。
再生中に次の返答が来たら、前の再生を止めてから読む。
pw-play が無い、エンジンに接続できない、PipeWire が動いていない、のどれかなら
鳴らさずに終わり、理由を UNUSABLE に書いて覚える。ファイルがあるあいだは確かめもせずに終わる。
"""

import fcntl
import json
import os
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

import click

from . import check
from .mylog import getLogger

LIMIT = 180  # 読み上げるのはおよそここまで。超えるときは次の文末（無ければ読点）まで
# 延ばすのはここまで。句点の無い英語の返答 2,339 字を 1 回で合成しようとして、
# エンジンのメモリが 7.8 GB まで膨らみ kill されたことがある
EXTEND = 60
ENDS = "。！？!?"  # 文末
COMMAS = "、，"  # 読点。半角の「,」は 1,000 のような数字の中にも出るので入れない
SPEAKER = 119  # 夜語トバリ（明るい）
ENGINE = "http://127.0.0.1:50021"
PLAY = "--play"  # 合成と再生を受け持つ子プロセスの目印
MODULE = "ccspk.hook"  # 子プロセスは python -m でこのモジュールを起こす。stop_playing() はこれで見分ける
# 1・2 文目を短く切る区切り。読点・閉じ括弧・コロンの後ろ、開き括弧の前。
# 半角の「,」は 1,000、「:」は 12:30、「(」は name() のように語の中にも出るので、
# 「,」は入れず、「:」は英数字が続くとき、「(」は英数字の直後のときは切らない
CUT = r"[、，：）」』】)]|:(?![0-9A-Za-z])|(?=[（「『【])|(?<![0-9A-Za-z])(?=\()"
CUT_MIN = 8  # これより手前では切らない（「（」だけのような短すぎる塊を作らない）
SPACE_WITHIN = 30  # この字数までに CUT が無いときだけスペースで切る
# 桁ごとに読むときの 0〜9。2・5 は、「ニ」「ゴ」だと前後の桁と句が分かれやすいので伸ばす
DIGITS = "ゼロ イチ ニー サン ヨン ゴー ロク ナナ ハチ キュウ".split()
RUNTIME = os.environ.get("XDG_RUNTIME_DIR")
BASE = Path(RUNTIME, "ccspk") if RUNTIME else Path(f"/tmp/ccspk-{os.getuid()}")
PIDFILE = BASE.with_suffix(".pid")
# 使えないと分かった理由。$XDG_RUNTIME_DIR ならセッションが全部終わるまで、/tmp なら再起動まで残る
UNUSABLE = BASE.with_suffix(".unusable")
# 最後に読んだ文。返答の最後の文章は MessageDisplay と Stop の両方から来るので、2 度読まない
LAST = BASE.with_suffix(".last")
LOCK = BASE.with_suffix(".lock")  # フックは並んで走るので、PARTS・LAST・PIDFILE を触るあいだは 1 つずつ通す（ccspk stop も取る）
# MessageDisplay は 1 つの文章を index ごとに分けて渡し、最後の分に final が付く。
# フックは並んで走り、後ろの分が先に届くこともあるので、分けてここに置き、そろったらつなぐ
PARTS = BASE.with_suffix(".parts")
PARTS_KEEP = 600  # そろわないまま残った分は、この秒数で消す
# 読んでからこの秒数のうちに同じ文が来たら読まない。MessageDisplay と Stop は 0.01 秒差で来た。
# 長くすると、続けて同じ返答（「はい。」など）が来たときに黙ってしまう
SAME_WITHIN = 5

_log = getLogger("hook")


def unusable():
    """鳴らせない理由を返す。鳴らせるなら None。"""
    if not shutil.which("pw-play"):
        return "pw-play が無い"
    # エンジンは接続できるかだけ見る（1 ms かからない）
    url = urllib.parse.urlsplit(ENGINE)
    host, port = url.hostname, url.port
    try:
        socket.create_connection((host, port), timeout=1).close()
    except OSError as e:
        return f"エンジン（{host}:{port}）に接続できない: {e}"
    # PIPEWIRE_REMOTE は [a,b] のような形も取り、解釈を合わせきれないので、あれば確かめない
    if os.environ.get("PIPEWIRE_REMOTE"):
        return None
    sock = Path(os.environ.get("PIPEWIRE_RUNTIME_DIR") or RUNTIME or "/nonexistent", "pipewire-0")
    try:
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(1)
            s.connect(str(sock))
    except OSError as e:
        return f"PipeWire（{sock}）に接続できない: {e}"
    return None


def to_speech(text):
    """読み上げ用に整える。"""
    # コードブロックと表は中身を読まない。閉じていないブロックは末尾まで
    text = re.sub(r"^\s*(```|~~~).*?(?:^\s*\1|\Z)", " コード省略。 ", text, flags=re.S | re.M)
    text = re.sub(r"^\s*\|.*$", "", text, flags=re.M)
    # リンクは表示文字だけ残し、裸の URL は消す
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    # Markdown の記号。_ は識別子の切れ目なので空白にする
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", text, flags=re.M)
    text = text.replace("_", " ")
    # エンジンが読まない記号。「~」は範囲にも使うので下で扱う。`TODO-013` の件 のように
    # 囲まれた番号の後ろのスペースを TODO の置き換えで消せるよう、ここで消す。
    # ` はコミット ID を見分けるのに使うので、その後で消す
    text = re.sub(r"[*>]", "", text)
    text = drop_commit_ids(text)
    text = text.replace("`", "")
    # TODO-027 は「トゥードゥー ゼロニーナナ」と桁ごとに読む。「-」を残すと間が入り、消すと
    # TODO-100 が「ヒャク」になるのでカナにする。TODO-020〜022 の後ろの番号も同じ。
    # 直後のスペースは、下の数字と同じく日本語が続くときだけ消す
    text = re.sub(
        r"(?<![0-9A-Za-z])TODO-([0-9]+)(?:[ \t]*[〜～~→][ \t]*([0-9]+))?(?:[ \t]+(?=[\u3041-\u30ff\u4e00-\u9fff]))?",
        lambda m: "TODO" + "から".join("".join(DIGITS[int(c)] for c in g) for g in m.groups() if g),
        text,
    )
    # 範囲の記号（1〜4 → イチ、ヨン）。半角の「~」は取り消し線や ~/ にも
    # 出て下で消すので、数字に挟まれたときだけ。前後のスペースは「から」の後に間が入るので消す
    text = re.sub(r"(?<=[0-9０-９])[ \t]*~[ \t]*(?=[0-9０-９])", "から", text)
    text = text.replace("~", "")
    text = re.sub(r"[ \t]*[〜～→][ \t]*", "から", text)
    # 数字と単位の間のスペースで区切って読む（180 字 → ヒャクハチジュウ、ジ）ので、
    # 同じ行で日本語が続くときだけ消す。英語が続くとき（3 files）は 1 語と読まれないよう残す
    text = re.sub(r"(?<=[0-9０-９])[ \t]+(?=[\u3041-\u30ff\u4e00-\u9fff])", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return clip(text)


def drop_commit_ids(text):
    """`0b7c291` のように ` で囲んだ 16 進 7 桁（`596eeac..4cbdc8c` も）をコミット ID と見て消す。
    8 桁はセッション ID などなので含めない。消すと文が壊れるもの（`fd36df8` にタグを付けた）は残す。"""
    cid = r"`[0-9a-f]{7}(?:\.\.[0-9a-f]{7})?`"
    # ID のほかに中身が無い文は、文ごと消す（コミットは `d774e35` です。 / 最新のコミット: `a1a9b44`）。
    # 「、」でつながる文は中身があるので残す
    text = re.sub(
        rf"(?:^|(?<=[。！？!?]))[^。！？!?\n、]*?(?:コミットは[ \t]*{cid}[ \t]*(?:です|でした)|[:：][ \t]*{cid})[ \t]*(?:。|$)",
        "", text, flags=re.M,
    )
    # （`0b7c291`）・（`37c1c3b`、`6e985ac`）はカッコごと、（`773c552`、push はしていません）は ID だけ
    text = re.sub(rf"[ \t]*[（(][ \t]*{cid}(?:[ \t]*[、,][ \t]*{cid})*[ \t]*[）)]", "", text)
    text = re.sub(rf"(?<=[（(])[ \t]*{cid}[ \t]*[、,。][ \t]*", "", text)
    # `b54297d` でコミットしました → コミットしました
    text = re.sub(rf"[ \t]*{cid}[ \t]*(?:で|に|として)[ \t]*(?=コミット)", "", text)
    # 件名が続くもの（`343f827` feat(bin): … / `eb0763a feat(ghostty): …`）は件名だけ読む
    return re.sub(r"`[0-9a-f]{7}`?[ \t]+(?=[a-z]+(?:\([^)\n]*\))?!?:[ \t])", "", text)


def questions(payload):
    """PreToolUse で AskUserQuestion の質問の文を改行でつなぐ。選択肢は読まない。"""
    if payload.get("tool_name") != "AskUserQuestion":
        return ""
    tool_input = payload.get("tool_input")
    items = tool_input.get("questions") if isinstance(tool_input, dict) else None
    if not isinstance(items, list):
        return ""
    return "\n".join(q["question"] for q in items if isinstance(q, dict) and isinstance(q.get("question"), str))


def clip(text):
    """LIMIT 字を超えるときは、文の途中で切らないよう、LIMIT 字目から LIMIT + EXTEND 字目
    までで最初の文末まで読む。文末が無ければ読点まで、それも無ければ LIMIT 字で切る。"""
    window = text[: LIMIT + EXTEND]
    for chars in (ENDS, COMMAS):
        m = re.compile(f"[{chars}]").search(window, LIMIT - 1)
        if m:
            return text[: m.end()]
    return text[:LIMIT]


def stop_playing():
    """前の再生をプロセスグループごと止める。止めたら True を返す。"""
    try:
        pid = int(PIDFILE.read_text())
        PIDFILE.unlink()
        # 再生が終わった後に番号が別のプロセスへ使い回されていたら触らない
        args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        if PLAY.encode() not in args or MODULE.encode() not in args:
            return False
        os.killpg(pid, signal.SIGTERM)
        return True
    except (OSError, ValueError):
        return False


def assemble(payload):
    """MessageDisplay の分を置き、全部そろったら 1 つにつないで返す。そろうまでは None。

    LOCK を取ってから呼ぶ。そろわないまま PARTS_KEEP 秒たった分は消す。
    """
    mid, index, delta = payload.get("message_id"), payload.get("index"), payload.get("delta") or ""
    if not mid or not isinstance(index, int):
        return None
    PARTS.mkdir(exist_ok=True)
    for q in PARTS.iterdir():
        if time.time() - q.stat().st_mtime > PARTS_KEEP:
            q.unlink(missing_ok=True)
    Path(PARTS, f"{mid}.{index}").write_text(delta)
    final = Path(PARTS, f"{mid}.final")
    if payload.get("final"):
        final.write_text(str(index))
    try:
        last = int(final.read_text())
        parts = [Path(PARTS, f"{mid}.{i}") for i in range(last + 1)]
    except (OSError, ValueError):
        return None
    if not all(q.exists() for q in parts):
        return None
    text = "".join(q.read_text() for q in parts)
    for q in [*parts, final]:
        q.unlink(missing_ok=True)
    return text


def sentences(text):
    """文に分ける。句点などの後ろで切り、句点は前の文に残す。"""
    return [s for s in re.split(f"(?<=[{ENDS}])\\s*", text) if s]


def split_first(sentence):
    """文を、音を早めるために前後 2 つに切る。切れなければそのまま。

    スペースは日本語の返答では英語や識別子の前後に出て、語と助詞の間で切れて
    しまうので、ほかの区切りが SPACE_WITHIN 字までに無いときだけ使う。
    後半が句点や空白だけになる所（「…（続き）。」の閉じ括弧の後ろなど）では切らない。
    """

    def ok(i):
        return i >= CUT_MIN and re.search(r"[^\s。！？!?]", sentence[i:])

    cuts = [m.end() for m in re.finditer(CUT, sentence) if ok(m.end())]
    first = cuts[0] if cuts else len(sentence)
    space = next((i for i in range(CUT_MIN, first) if sentence[i] == " " and ok(i + 1)), None)
    if cuts and (first <= SPACE_WITHIN or space is None):
        return [sentence[:first], sentence[first:]]
    if space is not None:
        return [sentence[:space], sentence[space + 1 :]]
    return [sentence]


def chunks(text):
    """合成する単位。1・2 文目は split_first で切り、3 文目以降は文ごと。
    2 文目も切るのは、1 文目を鳴らしている間に長い 2 文目の合成が終わらず、継ぎ目で待つのを減らすため。"""
    ss = sentences(text)
    return [squeeze(c) for c in [c for s in ss[:2] for c in split_first(s)] + ss[2:]]


def squeeze(chunk):
    """英単語と日本語の間のスペースを詰める。スペースの前後に間が入る（reviewer の → レビュウタ'ントウ、ノ'）。
    英単語同士（Claude Code）と数字の前後（行をまたいだ「手順 1 次へ」）は残す。
    split_first がスペースで切るので、to_speech ではなく切った後の塊ごとに詰める。"""
    return re.sub(
        r"(?<=[A-Za-z])[ ]+(?=[ぁ-ヿ一-鿿])|(?<=[ぁ-ヿ一-鿿])[ ]+(?=[A-Za-z])", "", chunk
    )


def synthesize(sentence):
    """1 文を合成して wav のバイト列を返す。"""
    query = urllib.request.urlopen(
        urllib.request.Request(
            f"{ENGINE}/audio_query?speaker={SPEAKER}&text=" + urllib.parse.quote(sentence),
            method="POST",
        ),
        # エンジンは要求を 1 つずつ処理し、止めた前の返答の合成も最後まで続ける。
        # その後ろに並ぶと 10 秒近く待つので、短くすると黙って諦めてしまう
        timeout=60,
    ).read()
    return urllib.request.urlopen(
        urllib.request.Request(
            f"{ENGINE}/synthesis?speaker={SPEAKER}",
            data=query,
            headers={"Content-Type": "application/json"},
        ),
        timeout=60,
    ).read()


def play(text):
    """1 文目ができたらすぐ鳴らし、2 文目以降は鳴らしている間に合成する。"""
    wavs = queue.Queue()

    def produce():
        # エンジンが動いていない、応答が途中で切れた、など何で止まっても、
        # 鳴らす側が待ち続けないよう終わりの印は必ず入れる
        try:
            for s in chunks(text):
                wavs.put(synthesize(s))
        finally:
            wavs.put(None)

    threading.Thread(target=produce, daemon=True).start()
    while (wav := wavs.get()) is not None:
        subprocess.run(["pw-play", "-"], input=wav, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def speak(text):
    """合成と再生を子プロセスに投げ、その PID を残す。"""
    p = subprocess.Popen(
        # -P: 作業ディレクトリを sys.path に入れない（そこに click.py などがあると、それを import してしまう）
        [sys.executable, "-P", "-m", MODULE, PLAY, text],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    PIDFILE.parent.mkdir(mode=0o700, exist_ok=True)
    PIDFILE.write_text(str(p.pid))


def demo():
    src = (
        "## 見出し\n"
        "`foo.py` を **直した**。\n"
        "```python\nprint(1)\n```\n"
        "| a | b |\n| - | - |\n"
        "- [詳細](https://example.com/x) を見る\n"
        "https://example.com/y\n"
    )
    got = to_speech(src)
    assert got == "見出し foo.py を 直した。 コード省略。 詳細 を見る", got
    # 上限を超えるときは、EXTEND 字までの間の次の文末まで。無ければ読点まで、
    # それも無ければ LIMIT 字で切る
    a = "あ"
    assert clip(a * LIMIT) == a * LIMIT
    assert clip(a * (LIMIT - 1) + "。いう。") == a * (LIMIT - 1) + "。"  # ちょうど LIMIT 字目が文末
    s = a * (LIMIT - 2) + "。" + a * 50  # LIMIT - 1 字目の文末は、延ばす先に使わない
    assert clip(s) == s[:LIMIT]
    assert clip(a * (LIMIT - 1) + "い。う。") == a * (LIMIT - 1) + "い。"
    assert clip(a * (LIMIT + 5) + "、い！う") == a * (LIMIT + 5) + "、い！"  # 読点より文末を優先
    assert clip(a * LIMIT + "い?う") == a * LIMIT + "い?"
    assert clip(a * (LIMIT + 20) + "、いう") == a * (LIMIT + 20) + "、"
    assert clip(a * (LIMIT + 5) + "，いう") == a * (LIMIT + 5) + "，"
    assert clip(a * (LIMIT + EXTEND - 1) + "。いう") == a * (LIMIT + EXTEND - 1) + "。"  # 延ばせる最後の字
    assert clip(a * (LIMIT + EXTEND) + "。いう") == a * LIMIT  # それより後ろの文末は使わない
    assert clip(a * 500) == a * LIMIT
    # to_speech の最後で clip を通す
    assert to_speech(a * 300) == a * LIMIT
    assert to_speech(a * (LIMIT + 5) + "。いう") == a * (LIMIT + 5) + "。"
    assert to_speech("```\nonly code\n```") == "コード省略。"
    assert to_speech("") == ""
    assert to_speech("CCSPK_SPEAK を足す") == "CCSPK SPEAK を足す"
    assert to_speech("説明\n```python\nsecret()\n") == "説明 コード省略。"
    assert to_speech("前\n~~~\ncode\n~~~\n後") == "前 コード省略。 後"
    # 記号の置き換えと、数字の直後のスペース
    assert to_speech("1〜4 秒、12～14 行目") == "1から4秒、12から14行目"
    assert to_speech("2 行 → 1 行、1 〜 4") == "2行から1行、1から4"
    assert to_speech("1~4 秒、2 ~ 3、~/a、a~b") == "1から4秒、2から3、/a、ab"
    assert to_speech("~100 件、1 ~/a") == "100件、1 /a"  # 数字が片側だけなら置き換えない
    assert to_speech("180 字、2 つ、TODO-013 の件") == "180字、2つ、TODOゼロイチサンの件"
    # TODO-NNN の番号は桁ごとのカナにする。範囲の後ろの番号も
    assert to_speech("TODO-100 と TODO-025") == "TODOイチゼロゼロと TODOゼロニーゴー"
    assert to_speech("TODO-020〜022、TODO-001 ~ 003 files、TODO-7→8") == (
        "TODOゼロニーゼロからゼロニーニー、TODOゼロゼロイチからゼロゼロサン files、TODOナナからハチ")
    assert to_speech("`TODO-013` の件、**TODO-020**～`022` の件、TODO-001 ～ 002 の件") == (
        "TODOゼロイチサンの件、TODOゼロニーゼロからゼロニーニーの件、TODOゼロゼロイチからゼロゼロニーの件")
    assert to_speech("PR-12、XTODO-1、TODO-1〜a") == "PR-12、XTODO-1、TODOイチからa"  # TODO- のほかは変えない
    assert to_speech("3 files と 1 ファイル、v1 A") == "3 files と 1ファイル、v1 A"
    assert to_speech("x 1  字、**2** 行、１８０ 字") == "x 1字、2行、１８０字"
    assert to_speech("手順 1\n次へ") == "手順 1 次へ"  # 行をまたぐときはつなげない
    # コミット ID は ` で囲んだ 16 進 7 桁。ID だけ消す
    assert to_speech("コミットしました（`0b7c291`）。") == "コミットしました。"
    assert to_speech("決着させました（`773c552`、push はしていません）（`536abc9`。未 push）。") == (
        "決着させました（push はしていません）（未 push）。")
    assert to_speech("どちらも（`37c1c3b`、`6e985ac`）。push できました (`596eeac..4cbdc8c`)。") == (
        "どちらも。push できました。")
    assert to_speech("`b54297d` でコミットし、`2c730d0` としてコミットしました") == "コミットし、コミットしました"
    assert to_speech("辞書を `960ac07` でコミットし、master に `44735a6` にコミットした") == (
        "辞書をコミットし、master にコミットした")  # 前のスペースも消す
    assert to_speech("`abc1234`、`def5678` を push した") == "abc1234、def5678を push した"  # カッコの外は残す
    assert to_speech("- `343f827` feat(bin): hook の設定\n- 最新は `f428514 feat(docs): 振り分ける`") == (
        "feat(bin): hook の設定 最新は feat(docs): 振り分ける")
    # ID のほかに中身が無い文は文ごと消す
    assert to_speech("済みました。コミットは `d774e35` です。次へ") == "済みました。次へ"
    assert to_speech("- **最新のコミット**: `a1a9b44`。\n- cachyos-admin: `487c1ac..424f0b7`\n以上") == "以上"
    assert to_speech("済み。前のコミットは **`abc1234`** でした。最新：`a1a9b44`。次へ") == "済み。次へ"
    # 「、」でつながる文や、「コミットは」でない文は残す
    assert to_speech("2 つに分けたため、コミットは `1acb1bf` です。PID は `1234567` です。") == (
        "2つに分けたため、コミットは 1acb1bf です。PID は 1234567です。")
    # 消すと文が壊れるものは残す
    assert to_speech("`fd36df8` に注釈付きタグ `v0.1.0` を付けました") == "fd36df8に注釈付きタグ v0.1.0を付けました"
    assert to_speech("`origin/master` は `7a526e0`（TODO-006 のコミット）を指していて") == (
        "origin/master は 7a526e0（TODOゼロゼロロクのコミット）を指していて")
    assert to_speech("`a1a9b44` より前の 5 件。`88ef11d` の記録どおり") == "a1a9b44より前の 5件。88ef11d の記録どおり"
    assert to_speech("`a5216c7` main と同じ") == "a5216c7 main と同じ"  # 件名の形でなければ読む
    # 8 桁・大文字・` で囲まないものは ID と見ない
    assert to_speech("（`a1b2c3d4`）（`6E985AC`）（6e985ac）") == "（a1b2c3d4）（6E985AC）（6e985ac）"
    assert sentences("直した。確かめる？ はい! 終わり") == ["直した。", "確かめる？", "はい!", "終わり"]
    assert sentences("句点なし") == ["句点なし"]
    assert sentences("") == []
    # 文の切り方
    assert split_first("reviewer の指摘を受けて挙動が変わったので、同じ reviewer に見てもらう。") == [
        "reviewer の指摘を受けて挙動が変わったので、", "同じ reviewer に見てもらう。"]
    assert split_first("はい、分かりました。") == ["はい、分かりました。"]  # 8 字より手前では切らない
    assert split_first("設定を見直しました（TODO-008 の続き）。") == ["設定を見直しました", "（TODO-008 の続き）。"]
    assert split_first("settings.json の登録は通りました。") == ["settings.json", "の登録は通りました。"]
    s = "あいうえおかきくけこ さしすせそたちつてとなにぬねのはひふへほまみむめも、やゆよ。"
    assert split_first(s) == ["あいうえおかきくけこ", "さしすせそたちつてとなにぬねのはひふへほまみむめも、やゆよ。"]
    s = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめも、やゆよ。"
    assert split_first(s) == ["あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめも、", "やゆよ。"]
    assert split_first("直した。") == ["直した。"]
    a = "あ"
    # 8 字の境界: ちょうど 8 字目の後ろなら切る。7 字目なら切らない
    assert split_first(a * 7 + "、いう。") == [a * 7 + "、", "いう。"]
    assert split_first(a * 6 + "、いう。") == [a * 6 + "、いう。"]
    assert split_first(a * 8 + " いう。") == [a * 8, "いう。"]
    assert split_first(a * 7 + " いう。") == [a * 7 + " いう。"]
    # 30 字の境界: 区切りが 30 字目までならそこ、31 字目ならその手前のスペース
    assert split_first(a * 10 + " " + a * 18 + "、いう。") == [a * 10 + " " + a * 18 + "、", "いう。"]
    assert split_first(a * 10 + " " + a * 19 + "、いう。") == [a * 10, a * 19 + "、いう。"]
    # スペースは最初の区切りより後ろのものを使わない
    assert split_first(a * 35 + "、いいいいい うえ。") == [a * 35 + "、", "いいいいい うえ。"]
    # 後半が句点や空白だけになる所では切らない
    assert split_first(a * 10 + "、") == [a * 10 + "、"]
    assert split_first("直した内容は「対応しない」。") == ["直した内容は「対応しない」。"]
    # 区切りの文字ごと
    for d in "、，：）」』】)":
        assert split_first(a * 9 + d + "いう。") == [a * 9 + d, "いう。"], d
    for d in "（「『【(":
        assert split_first(a * 9 + d + "いう）。") == [a * 9, d + "いう）。"], d
    assert split_first(a * 9 + ":いう。") == [a * 9 + ":", "いう。"]
    # 語の中の半角「:」「(」では切らない
    assert split_first("明日の会議は 12:30 からです。") == ["明日の会議は 12:30", "からです。"]
    assert split_first(a * 9 + "hasCell() を足した。")[0] == a * 9 + "hasCell()"
    assert chunks("見直しが終わったので、確かめてください。") == ["見直しが終わったので、", "確かめてください。"]
    assert chunks("直しました、確かめてください。次です。") == ["直しました、確かめてください。", "次です。"]
    # 切るのは 2 文目まで
    assert chunks("見直しが終わったので、確かめてください。二つ目の文ですが、ここも切る。三つ目の文ですが、ここは切らない。") == [
        "見直しが終わったので、", "確かめてください。", "二つ目の文ですが、", "ここも切る。", "三つ目の文ですが、ここは切らない。"]
    assert chunks("") == []
    # 英単語と日本語の間のスペースは、切った後に詰める。英単語同士と数字の前後は残す
    assert chunks("reviewer の指摘を受けて挙動が変わったので、同じ reviewer に見てもらう。") == [
        "reviewerの指摘を受けて挙動が変わったので、", "同じreviewerに見てもらう。"]
    assert chunks("settings.json の登録は通りました。") == ["settings.json", "の登録は通りました。"]
    assert chunks("一。二。Claude Code の 3 files を見る。") == ["一。", "二。", "Claude Codeの 3 filesを見る。"]
    assert chunks(to_speech("手順 1\n次へ")) == ["手順 1 次へ"]
    assert squeeze("ア  a") == "アa"  # 続くスペースもまとめて詰める

    # 質問の文だけをつなぐ。AskUserQuestion のほかは読まない
    ask = {"tool_name": "AskUserQuestion", "tool_input": {"questions": [
        {"question": "どちらにしますか？", "options": [{"label": "A案"}]},
        {"question": "範囲は？"}]}}
    assert to_speech(questions(ask)) == "どちらにしますか？ 範囲は？"
    assert questions({**ask, "tool_name": "Bash"}) == ""
    assert questions({"tool_name": "AskUserQuestion"}) == ""
    assert questions({"tool_name": "AskUserQuestion", "tool_input": "壊れた入力"}) == ""
    assert questions({"tool_name": "AskUserQuestion", "tool_input": {"questions": [{"question": 1}]}}) == ""

    # MessageDisplay の分をつなぐ。後ろの分が先に来ても、そろうまでは None
    global PARTS
    saved, PARTS = PARTS, Path(tempfile.mkdtemp(), "parts")
    try:
        def part(mid, index, delta, final=False):
            return assemble({"message_id": mid, "index": index, "delta": delta, "final": final})

        assert part("a", 1, "後半。", final=True) is None
        assert part("a", 0, "前半。\n\n") == "前半。\n\n後半。"
        assert list(PARTS.iterdir()) == []  # つないだ分は消す
        assert part("b", 0, "1 つだけ。", final=True) == "1 つだけ。"
        assert part("c", 0, "途中。") is None
        assert part("d", 2, "抜けがある。", final=True) is None  # 1 が来ていない
        assert assemble({"index": 0, "delta": "ID が無い。", "final": True}) is None
        old = Path(PARTS, "c.0")
        os.utime(old, (0, 0))
        part("e", 0, "次の文。")
        assert not old.exists()  # 古い分は消す
    finally:
        shutil.rmtree(PARTS.parent)
        PARTS = saved
    print("ok")


@click.command()
def main():
    """Stop・MessageDisplay・PreToolUse フック。標準入力のフックの入力を読み、返答の冒頭を読み上げる。"""
    if os.environ.get("CCSPK_SPEAK") != "1" or UNUSABLE.exists():
        return
    if reason := unusable():
        try:
            UNUSABLE.write_text(reason + "\n")
        except OSError:
            pass
        return
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    event = payload.get("hook_event_name")
    display = event == "MessageDisplay"
    ask = event == "PreToolUse"
    _log.debug(f"event={event}")
    if (display or ask) and payload.get("agent_id"):
        return
    try:
        lock = open(LOCK, "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    except OSError:
        lock = None
    try:
        if display:
            try:
                raw = assemble(payload)
            except OSError:
                return
            if raw is None:
                return
        elif ask:
            raw = questions(payload)
        else:
            raw = payload.get("last_assistant_message") or ""
        text = to_speech(raw)
        if (display or ask) and not text:
            return  # 表だけの途中の文章などで、読んでいる返答を止めない
        try:
            if text and LAST.read_text() == text and time.time() - LAST.stat().st_mtime < SAME_WITHIN:
                return
        except OSError:
            pass
        stop_playing()
        if text:
            try:
                LAST.write_text(text)
            except OSError:
                pass
            speak(text)
            check.record(text)
    finally:
        if lock:
            lock.close()
        if not (display or ask):
            check.after_stop()  # 同じ文を 2 度読まないで返るときも（MessageDisplay が記録した分がある）


@click.command()
@click.argument("text")
def say(text):
    """合成と再生だけを試す（子プロセスと同じ動き）。"""
    play(text)


@click.command()
def stop():
    """鳴っている読み上げを止める（エンジンの合成は止めない）。"""
    # フックが子プロセスを起こして PIDFILE を書き換えている途中に読まない
    try:
        lock = open(LOCK, "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    except OSError:
        lock = None
    print("止めた" if stop_playing() else "鳴っていない")
    if lock:
        lock.close()


@click.command()
@click.option("--clear", is_flag=True, help="UNUSABLE を消す")
def status(clear):
    """鳴らせないと覚えている理由（UNUSABLE）を表示する。無ければ「止まっていない」と表示する。"""
    if UNUSABLE.exists():
        print(f"{UNUSABLE}: {UNUSABLE.read_text().rstrip()}")
        if clear:
            UNUSABLE.unlink()
            print("消した")
    else:
        print("止まっていない")


if __name__ == "__main__":
    # speak() が起こす子プロセス。click と loguru の設定を通さない
    if sys.argv[1:2] == [PLAY]:
        play(sys.argv[2])
