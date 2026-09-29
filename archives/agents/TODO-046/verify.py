"""TODO-046 verifier: 手順 2。本物の claude -p で rewrite() を要約・翻訳に 2 回ずつ。使い方: cd リポジトリ && .venv/bin/python archives/agents/TODO-046/verify.py"""
import os, sys, tempfile
from pathlib import Path
tmp = Path(tempfile.mkdtemp())
from ccspk import hook
hook.STATE = tmp / "state"
hook.TRANSLATE = tmp / "translate"; hook.TRANSLATE.touch()
hook.SUMMARY = tmp / "summary"; hook.SUMMARY.touch()
hook.SUMMARY_TIMEOUT = 90  # 測定用に延ばした（既定 30）
os.environ["CCSPK_SUMMARY"] = "1"

JA = ("今日は設定ファイルの修正を行いました。確認したところ、辛い出力が出る箇所があり、サーバーの設定を見直す必要があります。"
 "昨日、別のマシンに行ったときも同じ問題が出ていたので、原因は共通だと考えられます。"
 "この方は、設定の確認と修正の手順を丁寧に説明してくれました。今日中に修正して、テストを実行しました。"
 "結果として、確認した 12 件のうち 10 件が通りました。残りの 2 件は辛い状況で、環境の設定が原因のようです。"
 "また、先週別のプロジェクトへ行った担当者の方にも確認を依頼しました。あなたが決めることは、修正の範囲と、確認を今日行うか明日行うかです。"
 "どちらの方法で進めるか、教えてください。設定の修正はすでに済んでいて、確認だけが残っています。")
assert len(JA) > 200
EN = """Today I made the fix. It was a painful bug, and the config took a hard look to track down.
Yesterday I went to the other machine and conducted the same check there. The way you set the timeout was the cause,
and the person who wrote it confirmed the setting. Please decide the scope of the change and the way to proceed.

Here is the patch for `src/ccspk/hook.py` (TODO-046):

```python
import os
def load_config(path):
    data = {}
    with open(path) as f:
        for line in f:
            k, _, v = line.partition("=")
            data[k.strip()] = v.strip()
    return data

def check(data):
    if "timeout" not in data:
        raise KeyError("timeout")
    return int(data["timeout"])

def main():
    data = load_config(os.environ["CFG"])
    print(check(data))

class Runner:
    def run(self):
        main()

if __name__ == "__main__":
    Runner().run()
```

| file | result |
|------|--------|
| hook.py | fixed |
| cli.py | unchanged |

After that, run `uv run ccspk test` and confirm that `load_config` works with the new setting. Today the tests pass, but the last one was hard to fix.
"""
assert hook.english(EN)
os.environ["CCSPK_SUMMARY"] = "0"  # 翻訳の測定: 要約を切る
text, flag, body = hook.prepare(EN)
os.environ["CCSPK_SUMMARY"] = "1"
assert flag == hook.TRANSLATING, flag
print("=== TRANSLATE 本文 (子プロセスに渡す) ===\n" + body + "\n=== end ===")
text2, flag2, body2 = hook.prepare(JA)
assert flag2 == hook.SUMMARIZE, flag2
for i in (1, 2, 3):
    print(f"\n### SUMMARY run {i}\n" + hook.rewrite(body2, hook.SUMMARY_PROMPT))
for i in (1, 2, 3):
    print(f"\n### TRANSLATE run {i}\n" + hook.rewrite(body, hook.TRANSLATE_PROMPT))
