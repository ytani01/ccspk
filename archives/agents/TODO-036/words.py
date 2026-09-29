"""measure.py と同じ文から、英字は正規表現、漢字は sudachipy（C）で切り出し、
エンジンの読みを付けて「表記<TAB>読み」で出す。  venv/bin/python words.py [件数] > words.tsv"""

import json
import re
import sys
import urllib.parse
import urllib.request

sys.argv[1:] = sys.argv[1:] or ["200"]
exec(open(__file__.replace("words.py", "measure.py")).read().split("KANJI =")[0])  # texts を作る
from sudachipy import Dictionary, SplitMode  # noqa: E402

st = Dictionary(dict="core").create()
words = {}
for x in texts:
    for w in re.findall(r"[A-Za-z][A-Za-z0-9._+-]*[A-Za-z0-9]|[A-Za-z]", x):
        words.setdefault(w)
    for m in st.tokenize(x, SplitMode.C):
        if re.search(r"[一-鿿々〆]", m.surface()):
            words.setdefault(m.surface())
for w in words:
    q = urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:50021/audio_query?speaker=119&text=" + urllib.parse.quote(w), method="POST"), timeout=60).read()
    print(f"{w}\t{json.loads(q)['kana']}")
