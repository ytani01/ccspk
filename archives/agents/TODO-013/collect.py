"""過去の返答のうち読み上げる範囲（to_speech 後）から、読み間違えそうな語を数える。"""
import collections, glob, importlib.util, json, re, sys
spec = importlib.util.spec_from_file_location("sp", "/home/ytani/.claude/hooks/speak-response.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
pats = {
    "upper": r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]+(?:\.[a-z]+)?(?![A-Za-z0-9])",
    "ext": r"(?<![A-Za-z0-9])\.?[\w-]*\.(?:json|md|py|sh|js|ts|toml|yaml|yml|txt|html|css|el|service|jsonl|mp4|png|pdf|wav)(?![A-Za-z0-9])",
    "alnum": r"(?<![A-Za-z0-9])(?=[A-Za-z0-9-]*[A-Za-z])(?=[A-Za-z0-9-]*[0-9])[A-Za-z][A-Za-z0-9-]*[0-9][A-Za-z0-9-]*",
    "sym": r"[〜~→←⇒/＆&%#@=+<>|≒≈×]",
}
cnt = {k: collections.Counter() for k in pats}
n = 0
for f in glob.glob("/home/ytani/.claude/projects/*/*.jsonl"):
    last = None
    for line in open(f, errors="ignore"):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get("message") or {}
        if d.get("type") == "assistant":
            c = m.get("content")
            if isinstance(c, list):
                t = "".join(x.get("text", "") for x in c if x.get("type") == "text")
                if t.strip(): last = t
        elif d.get("type") == "user" and last:
            # 返答の区切りごとに読み上げ範囲を取る
            s = sp.to_speech(last); n += 1; last = None
            for k, p in pats.items():
                cnt[k].update(re.findall(p, s))
    if last:
        s = sp.to_speech(last); n += 1
        for k, p in pats.items(): cnt[k].update(re.findall(p, s))
print("replies", n)
for k in pats:
    print("--", k)
    for w, c in cnt[k].most_common(40): print(c, w)
