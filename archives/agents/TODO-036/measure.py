"""TODO-036 の 1 つ目の項目: 形態素解析の候補を比べる。

会話ログ（~/.claude/projects/-home-ytani-work-ccspk/*.jsonl）の返答を to_speech() で整え、
英字を含む単語と漢字の単語を切り出す。候補ごとに、読み込みの時間・切り出しの時間・切り出した単語を出す。
  venv/bin/python measure.py [件数]
"""

import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.expanduser("~/work/ccspk/src"))
from ccspk.hook import to_speech  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
texts = []
for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/-home-ytani-work-ccspk/*.jsonl")), key=os.path.getmtime)[::-1]:
    for line in open(f):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        for c in d.get("message", {}).get("content", []):
            if c.get("type") == "text" and c["text"].strip():
                texts.append(to_speech(c["text"]))
    if len(texts) >= N:
        break
texts = texts[:N]
print(f"文: {len(texts)} 件、{sum(map(len, texts))} 字")

KANJI = re.compile(r"[一-鿿々〆]")
LATIN = re.compile(r"[A-Za-z]")


def regex(text):
    # 英字を含む塊（識別子・ファイル名）と、漢字の連なり
    return re.findall(r"[A-Za-z][A-Za-z0-9._+-]*[A-Za-z0-9]|[A-Za-z]", text) + re.findall(r"[一-鿿々〆]+", text)


def pick(surfaces):
    return [s for s in surfaces if KANJI.search(s) or LATIN.search(s)]


results = {}

t = time.perf_counter()
results["regex"] = (0, lambda x: regex(x))

t = time.perf_counter()
from janome.tokenizer import Tokenizer  # noqa: E402
jt = Tokenizer()
results["janome"] = (time.perf_counter() - t, lambda x: pick(tok.surface for tok in jt.tokenize(x)))

t = time.perf_counter()
import fugashi  # noqa: E402
ft = fugashi.Tagger()
results["fugashi+unidic-lite"] = (time.perf_counter() - t, lambda x: pick(w.surface for w in ft(x)))

t = time.perf_counter()
from sudachipy import Dictionary, SplitMode  # noqa: E402
st = Dictionary(dict="core").create()
results["sudachipy(C)"] = (time.perf_counter() - t, lambda x: pick(m.surface() for m in st.tokenize(x, SplitMode.C)))

for name, (load, fn) in results.items():
    t = time.perf_counter()
    words = [w for x in texts for w in fn(x)]
    run = time.perf_counter() - t
    uniq = sorted(set(words))
    print(f"\n## {name}: 読み込み {load:.2f} 秒、切り出し {run:.2f} 秒、{len(words)} 個（異なり {len(uniq)}）")
    print(" ".join(uniq[:120]))

# 漢字の単語だけを並べる（英字は正規表現のほうが素直に切れるため）
print("\n# 漢字の単語")
for name, (load, fn) in results.items():
    uniq = sorted({w for x in texts for w in fn(x) if KANJI.search(w)})
    print(f"\n## {name}: 異なり {len(uniq)}")
    print(" ".join(uniq[:150]))
