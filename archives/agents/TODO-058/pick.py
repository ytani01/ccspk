"""会話ログから assistant の返答テキストを集め、候補の長さを一覧する。"""
import glob, json, os, sys
sys.path.insert(0, "/home/ytani/work/ccspk/src")
from ccspk.hook import english, tidy
out = []
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    for line in open(f, errors="ignore"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "assistant": continue
        c = d.get("message", {}).get("content")
        if not isinstance(c, list): continue
        t = "\n".join(b.get("text", "") for b in c if b.get("type") == "text").strip()
        if t: out.append((f, t))
json.dump([(f, t) for f, t in out], open("/tmp/claude-649/-home-ytani-work-ccspk/a8963d2b-6748-4cdc-a6c0-d60307cdadf3/scratchpad/all.json", "w"))
print(len(out))
