"""TODO-058: claude -p の --effort ごとの時間と出力を測る。実行: .venv/bin/python archives/agents/TODO-058/measure.py"""
import os, subprocess, sys, tempfile, time, json
from pathlib import Path
sys.path.insert(0, "/home/ytani/work/ccspk/src")
from ccspk.hook import FENCE, SUMMARY_MAX, SUMMARY_PROMPT, TRANSLATE_MAX, TRANSLATE_PROMPT, unwrap, tidy
D = Path(__file__).parent
CFG = {"none": [], "medium": ["--effort", "medium"], "low": ["--effort", "low"]}
ORDER = [("none", "medium", "low"), ("medium", "low", "none"), ("low", "none", "medium")]
MATS = ["sum-short", "sum-mid", "sum-long", "tr-short", "tr-long"]

def run(prompt, raw, extra, cwd):
    args = ["claude", "-p", "--model", "sonnet", "--setting-sources", "", "--tools", "", "--no-session-persistence", *extra, prompt]
    t = time.monotonic()
    try:
        p = subprocess.run(args, input=f"<reply>\n{unwrap(raw)}\n</reply>", capture_output=True, text=True, timeout=120, cwd=cwd, env={**os.environ, "CCSPK_SPEAK": "0"})
        return time.monotonic() - t, p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return time.monotonic() - t, "timeout", "", ""

def main():
    cwd = tempfile.mkdtemp(prefix="ccspk058-")
    rows = []
    s, rc, out, err = run("OK とだけ返してください", "\n", [], cwd)
    rows.append(("startup", "none", round(s, 1), len(out), rc)); (D / "outputs/startup-none.txt").write_text(out)
    for i, m in enumerate(MATS):
        raw = (D / f"inputs/{m}.txt").read_text()
        if m.startswith("sum"): prompt, inp = SUMMARY_PROMPT, raw[:SUMMARY_MAX]
        else: prompt, inp = TRANSLATE_PROMPT, FENCE.sub("```\n```", raw)[:TRANSLATE_MAX]
        for c in ORDER[i % 3]:
            s, rc, out, err = run(prompt, inp, CFG[c], cwd)
            (D / f"outputs/{m}-{c}.txt").write_text(out)
            rows.append((m, c, round(s, 1), len(tidy(out)), rc))
            print(rows[-1], err[:200], flush=True)
    json.dump(rows, open(D / "results.json", "w"))
main()
