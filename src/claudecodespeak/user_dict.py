"""VOICEVOX のエンジンのユーザー辞書を操作する（claudecodespeak dict）。

  claudecodespeak dict add <表記> <読み（カタカナ）> [--accent N] [--type TYPE] [--priority N] [--speak]
  claudecodespeak dict kana <文>
  claudecodespeak dict list
  claudecodespeak dict remove <表記>
  claudecodespeak dict export [FILE]
  claudecodespeak dict import [FILE]

`add` はアクセントの位置を、読みを /audio_query に渡してエンジンに任せる。
同じ表記が登録済みなら、読みを書き換える。登録後の読みを表示し、--speak で鳴らす。
`export`/`import` は voicevox/user_dict.json への書き戻し・読み込みに使う
（docs/UsersGuide.md の「辞書をリポジトリに保存する」）。
"""

import json
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

import click

from .mylog import getLogger

_log = getLogger("dict")

ENGINE = "http://127.0.0.1:50021"
SPEAKER = 119  # 夜語トバリ（明るい）。hook.py と揃える
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

    エンジンは 1 語だけのとき、平板の語も「最後の音の後で下がる」として返し、尾高と
    見分けられない（後ろに「が」を付けると、カタカナの区切り方が変わってしまう）。
    ponytail: 句が 1 つで最後の音なら平板（0）とする。尾高の語は --accent で直す
    句に分かれたときは、先頭の句の位置を使う。
    """
    if not phrases:
        sys.exit("読みから音が取れない。カタカナで渡す")
    first = phrases[0]
    if len(phrases) == 1 and first["accent"] == len(first["moras"]):
        return 0
    return first["accent"]


def find(surface):
    """同じ表記の語の (ID, 中身)。エンジンは英数字を全角にして持つので、NFKC で揃えて比べる。"""
    words = json.loads(call("GET", "/user_dict"))
    key = unicodedata.normalize("NFKC", surface)
    return next(((i, w) for i, w in words.items() if unicodedata.normalize("NFKC", w["surface"]) == key), (None, None))


def demo():
    def ph(accent, moras):
        return {"accent": accent, "moras": [{}] * moras}

    assert accent_of([ph(5, 8)]) == 5  # ハイパーウィスパー
    assert accent_of([ph(4, 4)]) == 0  # トモダチ（平板）
    assert accent_of([ph(1, 2), ph(1, 3)]) == 1  # リードミー（リ'イ/ド'ミイ）
    assert accent_of([ph(2, 2), ph(1, 3)]) == 2  # 先頭の句の最後でも、句が 2 つなら平板にしない
    print("ok")


@click.group("dict")
def dict_group():
    """VOICEVOX のユーザー辞書を操作する。"""


@dict_group.command("add")
@click.argument("surface")
@click.argument("pronunciation")
@click.option("--accent", type=int, help="音が下がる直前の音が頭から何番目か。0 は平板。省くとエンジンに任せる")
@click.option("--type", "type_", type=click.Choice(list(TYPES.values())), help="品詞。省くと、新しい語は PROPER_NOUN、登録済みの語は今の品詞のまま")
@click.option("--priority", type=click.IntRange(0, 10), help="優先度（0〜10）。エンジン標準の読みに負けるときに上げる。省くと、新しい語は 5、登録済みの語は今の優先度のまま")
@click.option("--speak", is_flag=True, help="登録後に表記を読み上げて確かめる")
def add(surface, pronunciation, accent, type_, priority, speak):
    """VOICEVOX のユーザー辞書に語を足す。

    SURFACE は表記（英字は大文字と小文字を別の語として扱う）、PRONUNCIATION は読み（カタカナ）。
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
        extra = {} if priority is None else {"priority": priority}  # 省けばエンジンの既定（5）
        uuid = json.loads(call("POST", "/user_dict_word", **word, **extra, word_type=type_ or "PROPER_NOUN"))
        print(f"登録した: {surface} → {pronunciation}（accent_type {accent}、ID {uuid}）")
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
    """登録した語を、表記順に 1 語 1 行で一覧する（ID・表記・読み・accent_type）。"""
    words = json.loads(call("GET", "/user_dict"))
    for uuid, w in sorted(words.items(), key=lambda kv: kv[1]["surface"]):
        print(f"{uuid}  {w['surface']}  {w['pronunciation']}  {w['accent_type']}")


@dict_group.command("remove")
@click.argument("surface")
def remove(surface):
    """SURFACE（表記）で指定して、登録した語を消す。"""
    uuid, _old = find(surface)
    if not uuid:
        sys.exit(f"登録されていない: {surface}")
    call("DELETE", f"/user_dict_word/{uuid}")
    print(f"消した: {surface}（ID {uuid}）")


@dict_group.command("export")
@click.argument("file", type=click.File("w", encoding="utf-8"), default="-")
def export(file):
    """辞書を書き出す。FILE を省くと標準出力。voicevox/user_dict.json と同じ形にする。"""
    words = json.loads(call("GET", "/user_dict"))
    json.dump(words, file, indent=2, sort_keys=True, ensure_ascii=False)
    file.write("\n")


@dict_group.command("import")
@click.argument("file", type=click.File("rb"), default="-")
def import_(file):
    """辞書を読み込む。FILE を省くと標準入力。同じ ID の語は上書きする。"""
    call("POST", "/import_user_dict", data=file.read(), override="true")
    print("読み込んだ")
