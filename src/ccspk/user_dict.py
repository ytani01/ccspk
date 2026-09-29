"""VOICEVOX のエンジンのユーザー辞書を操作する（ccspk dict）。

  ccspk dict add <表記> <読み（カタカナ）> [--accent N] [--type TYPE] [--priority N] [--speak]
  ccspk dict kana <文>
  ccspk dict list
  ccspk dict remove <表記>
  ccspk dict auto [--remove]
  ccspk dict export [FILE]
  ccspk dict import [FILE]

`add` はアクセントの位置を、読みを /audio_query に渡してエンジンに任せる。
同じ表記が登録済みなら、読みを書き換える。登録後の読みを表示し、--speak で鳴らす。
`add`・`remove`・`import` が成功したら、エンジンの辞書を DICT_FILE
（~/.config/ccspk/user_dict.json）へ書き出す。エンジンの起動時に systemd がこれを `import` する
（systemd/voicevox-engine.service の ExecStartPost）。
"""

import json
import os
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import click

from .mylog import getLogger

_log = getLogger("dict")

ENGINE = "http://127.0.0.1:50021"
SPEAKER = 119  # 夜語トバリ（明るい）。hook.py と揃える
DICT_FILE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "ccspk" / "user_dict.json"
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
    return json.loads(call("POST", "/audio_query", speaker=SPEAKER, text=text))


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
    """エンジンの辞書を DICT_FILE へ書き出す。書きかけで落ちても前のファイルが残るよう、一時ファイルから置き換える。"""
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
        if not shutil.which("pw-play"):
            sys.exit("pw-play が無いので鳴らせない（登録は済んだ）")
        wav = call("POST", "/synthesis", data=json.dumps(q).encode(), speaker=SPEAKER)
        if subprocess.run(["pw-play", "-"], input=wav).returncode:
            sys.exit("pw-play が失敗した（登録は済んだ）")


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
@click.option("--remove", "remove_", is_flag=True, help="一覧の単語を全部エンジンから消し、一覧を空にする")
def auto(remove_):
    """自動の点検で登録した単語を一覧する（日時・表記・正しい読み・エンジンの元の読み）。"""
    try:
        rows = [r.split("\t") for r in ADDED.read_text(encoding="utf-8").splitlines() if r]
    except FileNotFoundError:
        rows = []
    if not rows:
        print("自動で登録した単語は無い")
        return
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
    ADDED.write_text("", encoding="utf-8")
    save()


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
