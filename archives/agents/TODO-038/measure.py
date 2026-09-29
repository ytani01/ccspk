"""TODO-038 確認用。usage: measure.py <old_src> [--synth]
実際の返答から 6 件選び、HEAD(old) と今の to_speech/chunks を並べる。"""
import sys, json, glob, os, re, io, wave, importlib
old_src = sys.argv[1]; synth = "--synth" in sys.argv
def load(path):
    for m in [m for m in sys.modules if m.startswith("ccspk")]: del sys.modules[m]
    sys.path.insert(0, path); import ccspk.hook as h; sys.path.pop(0); return h
new = load("/home/ytani/work/ccspk/src"); old = load(old_src)
assert old.__file__.startswith(old_src) and new.__file__.startswith("/home/ytani/work/ccspk/src")
texts = []
for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/-home-ytani-work-ccspk/*.jsonl"))):
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") != "assistant": continue
        for c in d["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "text" and c["text"].count("\n") >= 3:
                texts.append(c["text"])
ind = re.compile(r"^[ \t]+\S", re.M)
pick = []
def add(pred, n):
    for t in texts:
        if len(pick) >= n: break
        if t not in pick and pred(t) and len(t) < 900: pick.append(t)
add(lambda t: re.search(r"^[ \t]+[-*]?\s*\S", t, re.M) and re.search(r"^- ", t, re.M) and re.search(r"^ +[^-\s*\d>|`]", t, re.M), 2)
add(lambda t: "```" in t, 3)
add(lambda t: re.search(r"^#+ ", t, re.M), 4)
add(lambda t: re.search(r"^\d+\. ", t, re.M), 5)
add(lambda t: re.search(r"^[-*] ", t, re.M), 6)
for i, t in enumerate(pick):
    print(f"===== {i}\n--- src\n{t}\n--- old\n{old.to_speech(t)}\n--- new\n{new.to_speech(t)}")
    print(f"--- old tidy\n{old.tidy(t)}\n--- new tidy\n{new.tidy(t)}")
    cs = new.chunks(new.to_speech(t)); print("--- chunks"); 
    for c in cs:
        line = repr(c)
        if synth:
            w = wave.open(io.BytesIO(new.synthesize(c))); line += f"  {w.getnframes()/w.getframerate():.2f}s"
        print(line)

# --- 全件の字の増減と、読む字の無い塊、字下げした続きの行の例
strip = lambda s: re.sub(r"[\s。]", "", s)
bad = empty = 0; ex = []
for t in texts:
    o, n = old.tidy(t), new.tidy(t)
    if strip(o) != strip(n): bad += 1; print("CHARDIFF", repr(t[:80]))
    for c in new.chunks(new.tidy(t)):
        if not re.search(r"[0-9A-Za-zぁ-ヿ一-鿿]", c): empty += 1; print("EMPTYCHUNK", repr(c))
    if re.search(r"[^。！？!?、，：:.\s）」)]\n[ \t]+[^-*+\d>|`\s#]", t) and len(ex) < 3: ex.append(t)
print(f"texts={len(texts)} chardiff={bad} emptychunks={empty}")
for t in ex[:2]:
    print("--- INDENT EX src\n" + t[:500] + "\n--- old\n" + old.tidy(t)[:400] + "\n--- new\n" + new.tidy(t)[:400])
# --- 読む字の無い塊が HEAD にもあるか
E = re.compile(r"[0-9A-Za-zぁ-ヿ一-鿿]")
for t in texts:
    ne = [c for c in new.chunks(new.tidy(t)) if not E.search(c)]
    oe = [c for c in old.chunks(old.tidy(t)) if not E.search(c)]
    if ne or oe:
        print("EMPTY new", ne, "old", oe)
        for c in ne:
            i = new.tidy(t).find(c); print("   ctx:", repr(new.tidy(t)[max(0,i-40):i+20]))
# --- 字下げした続きの行（前の行が句読点で終わらない）の実例
pat = re.compile(r"^[-*] [^\n]*[^。！？!?、，：:.\s\n]\n[ \t]+[^-*+\d>|`\s#][^\n]*", re.M)
n = 0
for t in texts:
    m = pat.search(t)
    if m and n < 2:
        n += 1; print("--- WRAP EX src", repr(m.group(0))); print("   old", repr(old.tidy(m.group(0)))); print("   new", repr(new.tidy(m.group(0) + "\n次")))
print("wrap examples", n)
