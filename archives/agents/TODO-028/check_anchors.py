import re, sys, os
DOCS = ["README.md", "docs/UsersGuide.md", "docs/Developer.md"]
ALL = DOCS + ["CLAUDE.md"]
def heads(path):
    out, fence = [], False
    for i, l in enumerate(open(path, encoding="utf-8"), 1):
        if l.lstrip().startswith("```"): fence = not fence; continue
        if fence: continue
        m = re.match(r"^(#{1,6}) (.*?)\s*$", l)
        if m: out.append((i, len(m[1]), m[2]))
    return out
def anchor(t):
    t = t.lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")
bad = 0
print("== 1. numbering")
for p in DOCS:
    n = h = 0; ok = True
    for i, lv, t in heads(p):
        if lv == 1:
            if re.match(r"\d", t): print("NG title numbered", p, i, t); bad += 1
        elif lv == 2:
            m = re.match(r"(\d+)\. ", t); n += 1; h = 0
            if not m or int(m[1]) != n: print("NG", p, i, t, "expected", n); bad += 1; ok = False
        elif lv == 3:
            m = re.match(r"(\d+)\.(\d+) ", t); h += 1
            if not m or int(m[1]) != n or int(m[2]) != h: print("NG", p, i, t, "expected", f"{n}.{h}"); bad += 1; ok = False
        else: print("NOTE deeper heading", p, i, t)
    print(p, "h2 =", n, "OK" if ok else "NG")
print("== 2. links")
anchors = {}
for p in DOCS:
    seen = {}; s = set()
    for _, lv, t in heads(p):
        a = anchor(t); k = seen.get(a, 0); seen[a] = k + 1
        s.add(a if k == 0 else f"{a}-{k}")
    anchors[os.path.normpath(p)] = s
cnt = 0
for p in ALL:
    fence = False
    for i, l in enumerate(open(p, encoding="utf-8"), 1):
        for m in re.finditer(r"\]\(([^)#\s]*)#([^)\s]*)\)", l):
            cnt += 1
            f = os.path.normpath(os.path.join(os.path.dirname(p), m[1])) if m[1] else os.path.normpath(p)
            if f not in anchors: print("NG file", p, i, m[0]); bad += 1
            elif m[2] not in anchors[f]: print("NG anchor", p, i, m[0]); bad += 1
print("links checked:", cnt)
print("== 3. 「」 (ref = matches a heading text after number removed, or full)")
full = {}; bare = {}
for p in DOCS:
    for i, lv, t in heads(p):
        full[t] = p; bare[re.sub(r"^[\d.]+\s+", "", t)] = t
for p in ALL:
    for i, l in enumerate(open(p, encoding="utf-8"), 1):
        for m in re.finditer(r"「([^」]*)」", l):
            s = m[1]
            if s in full: print("OK ", p, i, s)
            elif s in bare: print("NG old-name", p, i, s, "->", bare[s]); bad += 1
            else: print("?? not a heading", p, i, s)
print("bad =", bad)
