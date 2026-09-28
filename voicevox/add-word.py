#!/usr/bin/env python3
"""VOICEVOX のエンジンのユーザー辞書に語を足す。

  add-word.py <表記> <読み（カタカナ）> [--accent N] [--type TYPE] [--speak]

アクセントの位置は、読みを /audio_query に渡してエンジンに任せる。
同じ表記が登録済みなら、読みを書き換える。登録後の読みを表示し、--speak で鳴らす。
voicevox/user_dict.json への書き戻しはしない（docs/UsersGuide.md の「リポジトリに残す」）。
"""

import argparse
import json
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ENGINE = "http://127.0.0.1:50021"
SPEAKER = 119  # 夜語トバリ（明るい）。hooks/speak-response.py と揃える
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
    return urllib.request.urlopen(urllib.request.Request(url, data, headers, method=method), timeout=60).read()


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


def main():
    if sys.argv[1:] == ["--test"]:
        return demo()
    p = argparse.ArgumentParser(description="VOICEVOX のユーザー辞書に語を足す")
    p.add_argument("surface", help="表記（英字は大文字と小文字を別の語として扱う）")
    p.add_argument("pronunciation", help="読み（カタカナ）")
    p.add_argument("--accent", type=int, help="音が下がる直前の音が頭から何番目か。0 は平板。省くとエンジンに任せる")
    p.add_argument("--type", choices=TYPES.values(), help="品詞。省くと、新しい語は PROPER_NOUN、登録済みの語は今の品詞のまま")
    p.add_argument("--speak", action="store_true", help="登録後に表記を読み上げて確かめる")
    a = p.parse_args()

    try:
        accent = a.accent if a.accent is not None else accent_of(query(a.pronunciation)["accent_phrases"])
        word = dict(surface=a.surface, pronunciation=a.pronunciation, accent_type=accent)
        uuid, old = find(a.surface)
        if uuid:
            kept = TYPES.get((old["part_of_speech"], old["part_of_speech_detail_1"]), "PROPER_NOUN")
            call("PUT", f"/user_dict_word/{uuid}", **word, word_type=a.type or kept, priority=old["priority"])
            print(f"書き換えた: {a.surface} → {a.pronunciation}（accent_type {accent}、ID {uuid}）")
        else:
            uuid = json.loads(call("POST", "/user_dict_word", **word, word_type=a.type or "PROPER_NOUN"))
            print(f"登録した: {a.surface} → {a.pronunciation}（accent_type {accent}、ID {uuid}）")
        q = query(a.surface)
        print(f"読み: {q['kana']}")
        if a.speak:
            if not shutil.which("pw-play"):
                sys.exit("pw-play が無いので鳴らせない（登録は済んだ）")
            wav = call("POST", "/synthesis", data=json.dumps(q).encode(), speaker=SPEAKER)
            if subprocess.run(["pw-play", "-"], input=wav).returncode:
                sys.exit("pw-play が失敗した（登録は済んだ）")
    except urllib.error.HTTPError as e:
        sys.exit(f"エンジンが断った（{e.code}）: {e.read().decode(errors='replace')}")
    except OSError as e:  # URLError と、読み出し中の TimeoutError
        sys.exit(f"エンジン（{ENGINE}）とやり取りできない: {getattr(e, 'reason', e)}")


if __name__ == "__main__":
    main()
