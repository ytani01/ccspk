"""hook.py を一時コピーして 1 つずつ壊し、demo() が落ちるか見る。リポジトリの hook.py は変えない。"""
import importlib, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src" / "ccspk"
CID = 'cid = r"`[0-9a-f]{7}(?:\\.\\.[0-9a-f]{7})?`"'
MUTS = [
 ("1 規則1 でした を外す", "(?:です|でした)", "(?:です)"),
 ("2 規則1 全角：を外す", "[:：]", "[:]"),
 ("3 規則3 (?<=[（(]) を外す", "(?<=[（(])[ \\t]*{cid}[ \\t]*[、,。]", "[ \\t]*{cid}[ \\t]*[、,。]"),
 ("4 規則4 に を外す", "(?:で|に|として)", "(?:で|として)"),
 ("5 規則5 先読みを緩める", "(?=[a-z]+(?:\\([^)\\n]*\\))?!?:[ \\t])", "(?=[a-z])"),
 ("6 [*>] を drop の後へ", None, None),
 ("7 規則4 先頭の [ \\t]* を外す", 'rf"[ \\t]*{cid}[ \\t]*(?:で|に|として)', 'rf"{cid}[ \\t]*(?:で|に|として)'),
 ("8 規則1 否定クラスから、を外す", "[^。！？!?\\n、]*?", "[^。！？!?\\n]*?"),
 ("9 規則1 コミットは→は", "(?:コミットは[ \\t]*{cid}", "(?:は[ \\t]*{cid}"),
]
ORDER_OLD = '    text = re.sub(r"[*>]", "", text)\n    text = drop_commit_ids(text)\n'
ORDER_NEW = '    text = drop_commit_ids(text)\n    text = re.sub(r"[*>]", "", text)\n'

def run(code):
    d = Path(tempfile.mkdtemp())
    shutil.copytree(SRC, d / "ccspk", ignore=shutil.ignore_patterns("__pycache__"))
    (d / "ccspk" / "hook.py").write_text(code)
    r = subprocess.run([sys.executable, "-c", "from ccspk import hook; hook.demo(); print('PASS')"],
                       cwd=d, capture_output=True, text=True)
    shutil.rmtree(d)
    return r

orig = (SRC / "hook.py").read_text()
print("baseline:", run(orig).stdout.strip())
for name, old, new in MUTS:
    if old is None:
        old, new = ORDER_OLD, ORDER_NEW
    n = orig.count(old)
    if n != 1:
        print(f"{name}: SKIP 置換対象が {n} 個"); continue
    r = run(orig.replace(old, new))
    last = (r.stderr.strip().splitlines() or [""])[-1][:100]
    print(f"{name}: {'落ちた' if r.returncode else '落ちない(PASS)'}  {last}")
