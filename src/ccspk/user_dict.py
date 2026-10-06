"""VOICEVOX のエンジンのユーザー辞書を操作する（ccspk dict）。

  ccspk dict add <表記> <読み（カタカナ）> [--accent N] [--type TYPE] [--priority N] [--speak]
  ccspk dict kana <文>
  ccspk dict list
  ccspk dict remove <表記>
  ccspk dict auto [--remove [表記...]]
  ccspk dict export [FILE]
  ccspk dict import [FILE]
  ccspk speaker [番号 | 名前 [スタイル]] [--list]
  ccspk volume [音量]

`add` はアクセントの位置を、読みを /audio_query に渡してエンジンに任せる。
同じ表記が登録済みなら、読みを書き換える。登録後の読みを表示し、--speak で鳴らす。
`add`・`remove`・`import`・`auto --remove` が成功したら、エンジンの辞書を DICT_FILE
（~/.config/ccspk/user_dict.json）へ書き出す。エンジンの起動時に systemd がこれを `import` する
（systemd/voicevox-engine.service の ExecStartPost）。
`speaker` は読み上げの話者を SPEAKER_FILE に残す。フック・say・dict add --speak・読み間違いの点検が使う。
`volume` は読み上げの音量（pw-play --volume）を VOLUME_FILE に残す。フック・say・dict add --speak が使う。
`remote`（hook.py）で REMOTE_FILE にホストを残すと、pw-play を ssh 先で走らせ、DICT_FILE の代わりに
ssh 先の ~/.config/ccspk/user_dict.json へ書き出す。エンジンへは ~/.ssh/config の LocalForward でつなぐ。
"""

import io
import json
import math
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import click

from .mylog import getLogger

_log = getLogger("dict")

ENGINE = "http://127.0.0.1:50021"
SPEAKER = 119  # 夜語トバリ（明るい）。ccspk speaker で決めていないときの話者
DICT_FILE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "ccspk" / "user_dict.json"
SPEAKER_FILE = DICT_FILE.parent / "speaker"  # ccspk speaker で決めた話者の番号
VOLUME_FILE = DICT_FILE.parent / "volume"  # ccspk volume で決めた音量（0〜1.0）
REMOTE_FILE = DICT_FILE.parent / "remote"  # ccspk remote で決めた ssh 先のホスト
# 自動の点検（check.py）の状態のディレクトリと、自動で登録した単語の一覧
# （日時<TAB>表記<TAB>正しい読み<TAB>エンジンの元の読み）
STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "ccspk"
ADDED = STATE / "added.tsv"
# 品詞。エンジンは word_type を品詞の組にして持つので、書き換えるときはここから引き戻す
TYPES = {
    ("名詞", "固有名詞"): "PROPER_NOUN",
    ("名詞", "一般"): "COMMON_NOUN",
    ("動詞", "自立"): "VERB",
    ("形容詞", "自立"): "ADJECTIVE",
    ("名詞", "接尾"): "SUFFIX",
}


def call(method, path, data=None, **params):
    url = f"{ENGINE}{path}?" + urllib.parse.urlencode(params)
    headers = {"Content-Type": "application/json"} if data else {}
    # 捕まえるのはエンジンとの通信だけ。export の書き込みの失敗などは、そのまま上げる
    try:
        return urllib.request.urlopen(urllib.request.Request(url, data, headers, method=method), timeout=60).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"エンジンが断った（{e.code}）: {e.read().decode(errors='replace')}")
    except OSError as e:  # URLError と、読み出し中の TimeoutError
        sys.exit(f"エンジン（{ENGINE}）とやり取りできない: {getattr(e, 'reason', e)}")


def query(text):
    return json.loads(call("POST", "/audio_query", speaker=speaker(), text=text))


def speaker():
    """話者の番号。SPEAKER_FILE が無い・読めない・数でないときは SPEAKER。"""
    try:
        return int(SPEAKER_FILE.read_text())
    except (OSError, ValueError):
        return SPEAKER


def volume():
    """pw-play に渡す音量。VOLUME_FILE が無い・読めない・0〜1.0 の数でないときは 1.0。"""
    try:
        v = float(VOLUME_FILE.read_text())
    except (OSError, ValueError):
        return 1.0
    return v if 0 <= v <= 1 else 1.0  # nan もここで 1.0 になる


def remote():
    """ccspk remote で決めたホスト。REMOTE_FILE が無い・読めない・空のときは None。"""
    try:
        return REMOTE_FILE.read_text().strip() or None
    except OSError:
        return None


def ssh(host, script):
    """host で script を sh に走らせる ssh の引数。パスワードを聞きに止まらないよう BatchMode にする。"""
    return ["ssh", "-o", "BatchMode=yes", host, "sh", "-c", shlex.quote(script)]


def watched(args):
    """args を走らせ、標準出力の先が閉じたらプロセスグループごと止める sh のスクリプト。終了コードは args のもの。
    ssh を止めても、リモートの pw-play は標準入力を読み終えているので鳴り続ける（SIGTERM でも SIGKILL でも）。
    見張りが 0.1 秒ごとに標準出力へ書き、接続が切れて書けなくなったら止める。args が終われば見張りも止める。
    グループごと止めるのは、sshd がコマンドを自分のセッション（グループ）で走らせるため。"""
    return f'(trap "" PIPE; while sleep 0.1; do echo 2>/dev/null || kill 0; done) & w=$!; {shlex.join(args)}; r=$?; kill $w; exit $r'


def pw_play():
    """wav を標準入力から鳴らす pw-play の引数。remote() があれば ssh 先で鳴らす。"""
    args = ["pw-play", f"--volume={volume()}", "-"]
    host = remote()
    return ssh(host, watched(args)) if host else args


def write_config(path, value):
    """書いている途中に読まれても、前の値で読むように、別のファイルに書いてから置き換える。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(f"{value}\n")
    tmp.replace(path)


def styles():
    """エンジンの話者を (番号, 名前, スタイル) で、エンジンの並び順に返す。"""
    return [(s["id"], p["name"], s["name"]) for p in json.loads(call("GET", "/speakers")) for s in p["styles"]]


def pick(args, found):
    """番号 1 つか、名前（とスタイル）から、found（styles() の形）にある番号を返す。無ければ None。
    スタイルを省いたら、その話者の最初のスタイル。"""
    if len(args) == 1 and args[0].isdecimal():
        return next((i for i, _n, _s in found if i == int(args[0])), None)
    name, style = args[0], args[1] if len(args) > 1 else None
    return next((i for i, n, s in found if n == name and style in (None, s)), None)


def accent_of(phrases):
    """/audio_query のアクセント句から、辞書の accent_type を決める。

    エンジンは単語 1 つだけのとき、平板の単語も「最後の音の後で下がる」として返し、尾高と
    見分けられない（後ろに「が」を付けると、カタカナの区切り方が変わってしまう）。
    ponytail: 句が 1 つで最後の音なら平板（0）とする。尾高の単語は --accent で直す
    句に分かれたときは、先頭の句の位置を使う。
    """
    if not phrases:
        sys.exit("読みから音が取れない。カタカナで渡す")
    first = phrases[0]
    if len(phrases) == 1 and first["accent"] == len(first["moras"]):
        return 0
    return first["accent"]


# 全角の英数字・記号（！〜～）を半角へ。NFKC は半角カナなども変えるので使わない
HALF = {c: c - 0xFEE0 for c in range(0xFF01, 0xFF5F)}


def halfwidth(text):
    """エンジンが全角にして持つ表記を、表示・書き出し用に半角へ戻す。"""
    return text.translate(HALF)


def find(surface):
    """同じ表記の単語の (ID, 中身)。エンジンは英数字を全角にして持つので、NFKC で揃えて比べる。"""
    words = json.loads(call("GET", "/user_dict"))
    key = unicodedata.normalize("NFKC", surface)
    return next(((i, w) for i, w in words.items() if unicodedata.normalize("NFKC", w["surface"]) == key), (None, None))


def dump(file):
    """エンジンの辞書を JSON で書く。表記は半角にする（import するとエンジンが全角に直す）。"""
    words = json.loads(call("GET", "/user_dict"))
    for w in words.values():
        w["surface"] = halfwidth(w["surface"])
    json.dump(words, file, indent=2, sort_keys=True, ensure_ascii=False)
    file.write("\n")


def save():
    """エンジンの辞書を DICT_FILE へ書き出す。書きかけで落ちても前のファイルが残るよう、一時ファイルから置き換える。
    remote() があれば、ssh 先のエンジンが起動時に読む ssh 先のファイルへ書き出す（手元には書かない）。"""
    if host := remote():
        buf = io.StringIO()
        dump(buf)
        data = buf.getvalue().encode()
        d = '"${XDG_CONFIG_HOME:-$HOME/.config}/ccspk"'
        # 送っている途中で切れても cat は正常に終わるので、大きさがそろったときだけ置き換える
        script = f'mkdir -p {d} && cat > {d}/user_dict.tmp && [ "$(wc -c < {d}/user_dict.tmp)" -eq {len(data)} ] && mv {d}/user_dict.tmp {d}/user_dict.json'
        try:
            failed = subprocess.run(ssh(host, script), input=data, timeout=30).returncode
        except subprocess.TimeoutExpired:  # 裏の点検（check.py）を止めたままにしない
            failed = True
        if failed:
            sys.exit(f"{host} へ書き出せなかった（エンジンの辞書は変わっている）")
        print(f"書き出した: {host}:~/.config/ccspk/user_dict.json")
        return
    DICT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DICT_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        dump(f)
    tmp.replace(DICT_FILE)
    print(f"書き出した: {DICT_FILE}")


def register(surface, pronunciation, accent=None, type_=None, priority=None):
    """単語を足す。同じ表記が登録済みなら書き換える。書き出し（save()）はしない。

    accent を省くとエンジンに任せる。type_ を省くと、新しい単語は PROPER_NOUN、登録済みの単語は
    今の品詞のまま。priority を省くと、新しい単語は 7、登録済みの単語は今の優先度のまま。
    """
    accent = accent if accent is not None else accent_of(query(pronunciation)["accent_phrases"])
    word = dict(surface=surface, pronunciation=pronunciation, accent_type=accent)
    _log.debug(f"word={word}")
    uuid, old = find(surface)
    if uuid:
        kept = TYPES.get((old["part_of_speech"], old["part_of_speech_detail_1"]), "PROPER_NOUN")
        call("PUT", f"/user_dict_word/{uuid}", **word, word_type=type_ or kept, priority=old["priority"] if priority is None else priority)
        print(f"書き換えた: {surface} → {pronunciation}（accent_type {accent}、ID {uuid}）")
    else:
        uuid = json.loads(call("POST", "/user_dict_word", **word, word_type=type_ or "PROPER_NOUN", priority=7 if priority is None else priority))
        print(f"登録した: {surface} → {pronunciation}（accent_type {accent}、ID {uuid}）")


def forget_auto(surface):
    """手で登録・削除した単語を、自動で登録した単語の記録（ADDED）から外す。"""
    key = unicodedata.normalize("NFKC", surface)
    try:
        rows = ADDED.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError:
        return
    kept = [r for r in rows if unicodedata.normalize("NFKC", (r.split("\t") + [""])[1]) != key]
    if len(kept) != len(rows):
        ADDED.write_text("".join(kept), encoding="utf-8")


def demo():
    def ph(accent, moras):
        return {"accent": accent, "moras": [{}] * moras}

    assert accent_of([ph(5, 8)]) == 5  # ハイパーウィスパー
    assert accent_of([ph(4, 4)]) == 0  # トモダチ（平板）
    assert accent_of([ph(1, 2), ph(1, 3)]) == 1  # リードミー（リ'イ/ド'ミイ）
    assert accent_of([ph(2, 2), ph(1, 3)]) == 2  # 先頭の句の最後でも、句が 2 つなら平板にしない
    assert halfwidth("！／ｅｔｃ／ＴＯＤＯ－０１～") == "!/etc/TODO-01~"  # 範囲の両端も
    assert halfwidth("ｶﾅ　語") == "ｶﾅ　語"  # 半角カナと全角スペースは変えない
    found = [(2, "四国めたん", "ノーマル"), (0, "四国めたん", "あまあま"), (118, "夜語トバリ", "ノーマル"), (119, "夜語トバリ", "明るい")]
    assert pick(("119",), found) == 119 and pick(("１１８",), found) == 118 and pick(("0",), found) == 0
    assert pick(("5",), found) is None  # エンジンに無い番号
    assert pick(("夜語トバリ", "明るい"), found) == 119 and pick(("四国めたん",), found) == 2  # 省くと最初のスタイル
    assert pick(("夜語トバリ", "あまあま"), found) is None and pick(("夜語",), found) is None
    rows = [["t1", "pytest", "パイテスト", "x"], ["t2", "ＣＬＩ", "シーエルアイ", "x"], ["t3", "優先度", "ユウセンド", "x"]]
    assert auto_rows(rows, ("pytest", "CLI")) == ([rows[0], rows[1]], [])  # 全角で記録されていても半角で選べる
    assert auto_rows(rows, ("pytest", "nope")) == ([rows[0]], ["nope"])
    # 話者のファイル。無い・数でないときは SPEAKER
    global SPEAKER_FILE
    saved, SPEAKER_FILE = SPEAKER_FILE, Path(tempfile.mkdtemp()) / "speaker"
    try:
        assert speaker() == SPEAKER
        SPEAKER_FILE.write_text("3\n")
        assert speaker() == 3
        SPEAKER_FILE.write_text("x\n")
        assert speaker() == SPEAKER
    finally:
        shutil.rmtree(SPEAKER_FILE.parent)
        SPEAKER_FILE = saved
    # 音量のファイル。無い・範囲の外・数でないときは 1.0
    global VOLUME_FILE, REMOTE_FILE
    saved, VOLUME_FILE = VOLUME_FILE, Path(tempfile.mkdtemp()) / "volume"
    saved_remote, REMOTE_FILE = REMOTE_FILE, VOLUME_FILE.parent / "remote"  # 本物の remote を読むと ssh の引数になる
    try:
        assert volume() == 1.0 and pw_play() == ["pw-play", "--volume=1.0", "-"]
        write_config(VOLUME_FILE, 0.6)
        assert volume() == 0.6 and pw_play() == ["pw-play", "--volume=0.6", "-"]
        for bad in ("1.5", "-0.1", "nan", "x"):
            VOLUME_FILE.write_text(bad)
            assert volume() == 1.0, bad
        VOLUME_FILE.write_text("0")
        assert volume() == 0.0
    finally:
        shutil.rmtree(VOLUME_FILE.parent)
        VOLUME_FILE, REMOTE_FILE = saved, saved_remote
    # ssh 先で鳴らす。ホストが無い・空なら手元
    saved, REMOTE_FILE = REMOTE_FILE, Path(tempfile.mkdtemp()) / "remote"
    try:
        assert remote() is None and pw_play()[0] == "pw-play"
        REMOTE_FILE.write_text("\n")
        assert remote() is None
        write_config(REMOTE_FILE, "ytlenovo")
        assert pw_play() == ["ssh", "-o", "BatchMode=yes", "ytlenovo", "sh", "-c", shlex.quote(watched(["pw-play", f"--volume={volume()}", "-"]))]
    finally:
        shutil.rmtree(REMOTE_FILE.parent)
        REMOTE_FILE = saved
    # 見張り。標準出力の先が閉じたら止め、鳴り終われば見張りも終わる
    p = subprocess.Popen(["sh", "-c", watched(["sleep", "30"])], stdout=subprocess.PIPE, start_new_session=True)
    p.stdout.read(1)
    p.stdout.close()
    assert p.wait(3) == -signal.SIGTERM, p.returncode
    for code in (0, 3):
        r = subprocess.run(["sh", "-c", watched(["sh", "-c", f"exit {code}"])], stdout=subprocess.PIPE, start_new_session=True, timeout=3)
        assert r.returncode == code, r.returncode
    print("ok")


@click.group("dict")
def dict_group():
    """VOICEVOX のユーザー辞書を操作する。"""


@dict_group.command("add")
@click.argument("surface")
@click.argument("pronunciation")
@click.option("--accent", type=int, help="音が下がる直前の音が頭から何番目か。0 は平板。省くとエンジンに任せる")
@click.option("--type", "type_", type=click.Choice(list(TYPES.values())), help="品詞。省くと、新しい単語は PROPER_NOUN、登録済みの単語は今の品詞のまま")
@click.option("--priority", type=click.IntRange(0, 10), help="優先度（0〜10）。エンジン標準の読みに負けるときに上げる。省くと、新しい単語は 7（エンジンの既定 5 より上）、登録済みの単語は今の優先度のまま")
@click.option("--speak", is_flag=True, help="登録後に表記を読み上げて確かめる")
def add(surface, pronunciation, accent, type_, priority, speak):
    """VOICEVOX のユーザー辞書に単語を足す。

    SURFACE は表記（英字は大文字と小文字を別の単語として扱う）、PRONUNCIATION は読み（カタカナ）。
    """
    register(surface, pronunciation, accent, type_, priority)
    forget_auto(surface)
    save()
    q = query(surface)
    print(f"読み: {q['kana']}")
    if speak:
        player = pw_play()
        if not shutil.which(player[0]):
            sys.exit(f"{player[0]} が無いので鳴らせない（登録は済んだ）")
        wav = call("POST", "/synthesis", data=json.dumps(q).encode(), speaker=speaker())
        # ssh 先で鳴らすときは、見張りの改行が標準出力に来るので捨てる
        if subprocess.run(player, input=wav, stdout=subprocess.DEVNULL).returncode:
            sys.exit(f"{player[0]} が失敗した（登録は済んだ）")


@dict_group.command("kana")
@click.argument("text")
def kana(text):
    """TEXT をエンジンに渡し、読み（アクセント記号付きのカナ）を表示する。"""
    print(query(text)["kana"])


@dict_group.command("list")
def list_():
    """登録した単語を、表記順に 1 単語 1 行で一覧する（ID・表記・読み・accent_type・優先度）。"""
    words = json.loads(call("GET", "/user_dict"))
    for uuid, w in sorted(words.items(), key=lambda kv: halfwidth(kv[1]["surface"])):
        print(f"{uuid}  {halfwidth(w['surface'])}  {w['pronunciation']}  {w['accent_type']}  {w['priority']}")


@dict_group.command("remove")
@click.argument("surface")
def remove(surface):
    """SURFACE（表記）で指定して、登録した単語を消す。"""
    uuid, _old = find(surface)
    if not uuid:
        sys.exit(f"登録されていない: {surface}")
    call("DELETE", f"/user_dict_word/{uuid}")
    print(f"消した: {surface}（ID {uuid}）")
    forget_auto(surface)
    save()


@dict_group.command("auto")
@click.option("--remove", "remove_", is_flag=True, help="一覧の単語をエンジンから消し、一覧から外す。SURFACES（表記）を渡せばその単語だけ")
@click.argument("surfaces", nargs=-1)
def auto(remove_, surfaces):
    """自動の点検で登録した単語を一覧する（日時・表記・正しい読み・エンジンの元の読み）。"""
    if surfaces and not remove_:
        raise click.UsageError("表記を渡すときは --remove を付ける")
    try:
        rows = [r.split("\t") for r in ADDED.read_text(encoding="utf-8").splitlines() if r]
    except FileNotFoundError:
        rows = []
    if surfaces:
        rows, missing = auto_rows(rows, surfaces)
        if missing:
            sys.exit(f"自動で登録した単語に無い: {'、'.join(missing)}")
    if not rows:
        print("自動で登録した単語は無い")
        return
    if not surfaces:
        for r in rows:
            print("  ".join(r))
    if not remove_:
        return
    for r in rows:
        uuid, _old = find(r[1])
        if uuid:
            call("DELETE", f"/user_dict_word/{uuid}")
            print(f"消した: {r[1]}（ID {uuid}）")
        else:
            print(f"登録されていない（飛ばした）: {r[1]}")
        forget_auto(r[1])
    save()


def auto_rows(rows, surfaces):
    """自動で登録した単語の記録の行から、SURFACES の行を選ぶ。(選んだ行, 記録に無い表記)。表記は NFKC で比べる。"""
    keys = {unicodedata.normalize("NFKC", s): s for s in surfaces}
    picked = [r for r in rows if unicodedata.normalize("NFKC", r[1]) in keys]
    found = {unicodedata.normalize("NFKC", r[1]) for r in picked}
    return picked, [s for k, s in keys.items() if k not in found]


@dict_group.command("export")
@click.argument("file", type=click.File("w", encoding="utf-8"), default="-")
def export(file):
    """辞書を書き出す。FILE を省くと標準出力。~/.config/ccspk/user_dict.json と同じ形にする。

    表記は半角にする（import するとエンジンが全角に直す）。
    """
    dump(file)


@dict_group.command("import")
@click.argument("file", type=click.File("rb"), default="-")
def import_(file):
    """辞書を読み込む。FILE を省くと標準入力。同じ ID の単語は上書きする。"""
    call("POST", "/import_user_dict", data=file.read(), override="true")
    print("読み込んだ")
    save()


@click.command()
@click.argument("args", nargs=-1)
@click.option("--list", "show_list", is_flag=True, help="エンジンの話者を番号・名前・スタイルで一覧する")
def speaker_(args, show_list):
    """読み上げの話者を、番号か、名前とスタイルで決める（例: 119、夜語トバリ 明るい）。

    スタイルを省くと、その話者の最初のスタイル。引数なしは今の話者を表示する。次の読み上げから効く。
    """
    if len(args) > 2 or (show_list and args):
        raise click.UsageError("引数は、番号 1 つか、名前とスタイル。--list とは一緒に使えない")
    found = styles()
    if show_list:
        for i, n, s in found:
            print(f"{i}  {n}  {s}")
        return
    if args:
        sid = pick(args, found)
        if sid is None:
            sys.exit(f"エンジンの話者に無い: {' '.join(args)}（ccspk speaker --list で一覧する）")
        write_config(SPEAKER_FILE, sid)
    sid = speaker()
    print(next((f"{i}  {n}  {s}" for i, n, s in found if i == sid), f"{sid}  （エンジンの話者に無い）"))


@click.command()
@click.argument("value", required=False, type=click.FloatRange(0, 1))
def volume_(value):
    """読み上げの音量を 0〜1.0 で決める（例: 0.6）。引数なしは今の音量を表示する。次の読み上げから効く。"""
    if value is not None:
        if math.isnan(value):  # FloatRange は nan を通す
            raise click.BadParameter("nan は音量にできない", param_hint="VALUE")
        write_config(VOLUME_FILE, abs(value))  # -0 を 0.0 にする
    print(volume())
