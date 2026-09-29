"""TODO-037 の測定: samples.json の返答を claude -p で要約させ、モデルごとに時間・料金・字数を出す。
  python measure.py haiku sonnet > measure.out
空のディレクトリで、利用者の設定を読まずに（--setting-sources ""）走らせる。"""

import json
import os
import subprocess
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
samples = json.load(open(os.path.join(here, "samples.json")))
prompt = open(os.path.join(here, "prompt.txt")).read()
cwd = tempfile.mkdtemp()
for model in sys.argv[1:]:
    for s in samples:
        t = time.perf_counter()
        p = subprocess.run(
            ["claude", "-p", "--model", model, "--setting-sources", "", "--tools", "",
             "--no-session-persistence", "--output-format", "json", prompt],
            input=s, capture_output=True, text=True, cwd=cwd, timeout=120,
            env={**os.environ, "CCSPK_SPEAK": "0"},
        )
        wall = time.perf_counter() - t
        try:
            r = json.loads(p.stdout)
        except ValueError:
            print(f"## {model} {len(s)} 字: 失敗 {p.returncode} {p.stderr[-200:]}")
            continue
        out = r.get("result", "")
        u = r.get("usage", {})
        print(f"## {model} / 元 {len(s)} 字 → {len(out)} 字 / {wall:.1f} 秒 / ${r.get('total_cost_usd', 0):.4f}"
              f" / in {u.get('input_tokens')} cc {u.get('cache_creation_input_tokens')} out {u.get('output_tokens')}")
        print(out, "\n", flush=True)
