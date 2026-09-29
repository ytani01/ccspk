"""TODO-036 verifier 項目 9: 本物の claude -p を 1 回。登録はしない（parse() の結果を表示するだけ）。"""
import json, os, subprocess, tempfile
from ccspk.check import PROMPT, parse
table = {"README": "リ'イドメ", "pytest": "ピュ'テスト", "Zqxverifyword": "ズ'クスヴェリファイワアド", "変数": "ヘンスー", "優先度": "ユウセンド"}
stdin = "".join(f"{w}\t{k}\n" for w, k in table.items())
p = subprocess.run(["claude", "-p", "--model", "sonnet", "--setting-sources", "", "--tools", "", "--no-session-persistence",
                    "--output-format", "json", PROMPT], input=stdin, capture_output=True, text=True, timeout=300,
                   env={**os.environ, "CCSPK_SPEAK": "0"}, cwd=tempfile.mkdtemp())
print("exit", p.returncode, p.stderr[-300:])
j = json.loads(p.stdout)
print("result raw:", repr(j["result"]))
print("cost", j.get("total_cost_usd"), "duration_ms", j.get("duration_ms"))
print("parse:", list(parse(j["result"], table)))
