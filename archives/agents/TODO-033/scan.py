#!/usr/bin/env python3
"""全プロジェクトの会話ログから、Claude の返答のうちコミット ID らしきものを含む文を出す。
TODO-033 の調査に使った。規則を変えたら、この出力を to_speech に通して確かめる。"""
import glob, json, os, re

HEX = re.compile(r"`[0-9a-f]{7,8}(\.\.[0-9a-f]{7})?[` ]|（[0-9a-f]{7}[）、]|コミット ?[0-9a-f]{7}")
seen = set()
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    for line in open(f, errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant":
            continue
        for c in d.get("message", {}).get("content") or []:
            if c.get("type") != "text":
                continue
            for s in re.split(r"(?<=。)|\n", c["text"]):
                s = s.strip()
                if HEX.search(s) and s not in seen:
                    seen.add(s)
                    print(s)
