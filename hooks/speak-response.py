#!/usr/bin/env python3
"""Stop hook: Claude の最後の返答を VOICEVOX で読み上げる。

環境変数 CLAUDE_TTS_SPEAK が 1 のときだけ鳴らす。
再生中に次の返答が来たら、前の再生を止めてから読む。
voicevox-engine が動いていないときは、何も鳴らさずに終わる。
"""

import json
import os
import queue
import re
import signal
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path

LIMIT = 180  # 合成に時間がかかるので、読み上げるのはここまで
SPEAKER = 119  # 夜語トバリ（明るい）
ENGINE = "http://127.0.0.1:50021"
PLAY = "--play"  # 合成と再生を受け持つ子プロセスの目印
# 1 文目を短く切る区切り。読点・閉じ括弧・コロンの後ろ、開き括弧の前。
# 半角の「,」は 1,000、「:」は 12:30、「(」は name() のように語の中にも出るので、
# 「,」は入れず、「:」は英数字が続くとき、「(」は英数字の直後のときは切らない
CUT = r"[、，：）」』】)]|:(?![0-9A-Za-z])|(?=[（「『【])|(?<![0-9A-Za-z])(?=\()"
CUT_MIN = 8  # これより手前では切らない（「（」だけのような短すぎる塊を作らない）
SPACE_WITHIN = 30  # この字数までに CUT が無いときだけスペースで切る
PIDFILE = (
    Path(os.environ["XDG_RUNTIME_DIR"]) / "claude-tts.pid"
    if os.environ.get("XDG_RUNTIME_DIR")
    else Path(f"/tmp/claude-tts-{os.getuid()}.pid")
)


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
    text = re.sub(r"[`*~>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:LIMIT]


def stop_playing():
    """前の再生をプロセスグループごと止める。"""
    try:
        pid = int(PIDFILE.read_text())
        PIDFILE.unlink()
        # 再生が終わった後に番号が別のプロセスへ使い回されていたら触らない
        args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        if PLAY.encode() not in args or not any(a.endswith(Path(__file__).name.encode()) for a in args):
            return
        os.killpg(pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass


def sentences(text):
    """文に分ける。句点などの後ろで切り、句点は前の文に残す。"""
    return [s for s in re.split(r"(?<=[。！？!?])\s*", text) if s]


def split_first(sentence):
    """1 文目を、最初の音を早めるために前後 2 つに切る。切れなければそのまま。

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
    """合成する単位。1 文目だけ split_first で切り、2 文目以降は文ごと。"""
    ss = sentences(text)
    return split_first(ss[0]) + ss[1:] if ss else []


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
        [sys.executable, __file__, PLAY, text],
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
    assert len(to_speech("あ" * 500)) == LIMIT
    assert to_speech("```\nonly code\n```") == "コード省略。"
    assert to_speech("") == ""
    assert to_speech("CLAUDE_TTS_SPEAK を足す") == "CLAUDE TTS SPEAK を足す"
    assert to_speech("説明\n```python\nsecret()\n") == "説明 コード省略。"
    assert to_speech("前\n~~~\ncode\n~~~\n後") == "前 コード省略。 後"
    assert sentences("直した。確かめる？ はい! 終わり") == ["直した。", "確かめる？", "はい!", "終わり"]
    assert sentences("句点なし") == ["句点なし"]
    assert sentences("") == []
    # 1 文目の切り方
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
    assert chunks("直しました、確かめてください。次です。") == ["直しました、確かめてください。", "次です。"]
    # 切るのは 1 文目だけ
    assert chunks("見直しが終わったので、確かめてください。二つ目の文ですが、ここは切らない。") == [
        "見直しが終わったので、", "確かめてください。", "二つ目の文ですが、ここは切らない。"]
    assert chunks("") == []
    print("ok")


def main():
    if sys.argv[1:2] == ["--test"]:
        demo()
        return
    if sys.argv[1:2] == [PLAY]:
        play(sys.argv[2])
        return
    if os.environ.get("CLAUDE_TTS_SPEAK") != "1":
        return
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    text = to_speech(payload.get("last_assistant_message") or "")
    stop_playing()
    if text:
        speak(text)


if __name__ == "__main__":
    main()
