"""TODO-037 の測定: 会話ログから、整えた文（clip 前）が LIMIT を超える返答を拾う。
  uv run python archives/agents/TODO-037/pick.py > samples.json
長さの違うものを 4 件（300・600・1200・2000 字の近く）選ぶ。"""

import glob
import json
import os

from ccspk import hook

LIMIT = hook.LIMIT
hook.LIMIT = 10**9  # clip() で切らない
texts = []
for f in glob.glob(os.path.expanduser("~/.claude/projects/-home-ytani-*/*.jsonl")):
    for line in open(f):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        for c in d.get("message", {}).get("content", []):
            if c.get("type") == "text":
                s = hook.to_speech(c["text"])
                if len(s) > LIMIT:
                    texts.append(s)
texts = sorted(set(texts), key=len)
print(f"超えた返答: {len(texts)} 件", file=__import__("sys").stderr)
picked = [min(texts, key=lambda s: abs(len(s) - n)) for n in (300, 600, 1200, 2000)]
json.dump(picked, open(os.path.join(os.path.dirname(__file__), "samples.json"), "w"), ensure_ascii=False, indent=1)
for s in picked:
    print(len(s), s[:80])
