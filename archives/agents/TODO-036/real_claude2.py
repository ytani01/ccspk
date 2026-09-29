"""TODO-036 verifier 2 項目 4: 本物の claude -p を 1 回。登録はしない。parse() のあと same()（query() を通す）で残る行を数える。"""
import json, os, subprocess, tempfile
from ccspk.check import PROMPT, parse, same
from ccspk.user_dict import query
words = "先頭 返答 変数 背景 正規 計算 経緯 条件 分岐 測定".split()
table = {w: query(w)["kana"] for w in words}
p = subprocess.run(["claude", "-p", "--model", "sonnet", "--setting-sources", "", "--tools", "", "--no-session-persistence",
                    "--output-format", "json", PROMPT], input="".join(f"{w}\t{k}\n" for w, k in table.items()),
                   capture_output=True, text=True, timeout=300, env={**os.environ, "CCSPK_SPEAK": "0"}, cwd=tempfile.mkdtemp())
print("exit", p.returncode, p.stderr[-300:])
j = json.loads(p.stdout)
print("table:", table)
print("result raw:", repr(j["result"]))
print("cost", j.get("total_cost_usd"), "duration_ms", j.get("duration_ms"))
rows = list(parse(j["result"], table))
print("parse:", rows)
left = [(s, r, query(r)["kana"], table[s]) for s, r in rows if not same(query(r)["kana"], table[s])]
print("registration candidates:", len(left), left)
