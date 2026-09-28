# TODO-031 verifier 報告

スクリプト: `archives/agents/TODO-031/verify.sh`（worktree と一時の UV_TOOL_DIR / UV_TOOL_BIN_DIR で実行。後片付け済み）。
コマンドは `jq -r '.hooks.Stop[0].hooks[0].command' .claude/settings.json` で取り出して `sh -c` 相当で実行。

| # | 場合 | 期待 | 実測 |
|---|---|---|---|
| 1 | 変更なし | 出力なし・rc 0・mtime 不変 | 一致（rc=0, stdout 空, mtime 1790633361 のまま） |
| 2 | 変更あり | 出力なし・receipt 更新・入った cli.py に `# verify` | 一致（rc=0, stdout 空, 1790633361 -> 1790633362, 入った cli.py 末尾 `# verify`） |
| 3 | 直後に再実行 | 入れ直さない | 一致（mtime 1790633362 のまま）。`find src -newer receipt` は空、pycache 除外の find も空 |
| 4 | pycache のみ touch | 入れ直さない | 一致（mtime 不変, stdout 空, rc 0） |
| 5 | demo() の assert を偽に | systemMessage の JSON・AssertionError を含む・rc 0・receipt 不変・入った hook.py 不変・再実行でも知らせる | 一致（下記出力、rc=0, mtime 1790633362 のまま, `cmp` で入った hook.py 不変, 2 回目も同じ出力） |
| 6 | 未インストール | 出力なし・rc 0 | 一致（rc=0, stdout 空） |

食い違いなし。

## 5 の実出力（1 回目・2 回目とも同じ）
```
{
  "systemMessage": "ccspk test が落ちたので、入れ直さなかった:     ~~~~~~~~~^^\n  File \".../verify031/wt/src/ccspk/hook.py\", line 294, in demo\n    assert clip(a * LIMIT) != a * LIMIT\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError"
}
```
`jq .` で読めた。tail -n 5 のため、先頭が途中のトレースバック行（`~~~~~~~~~^^`）から始まる。実害は未確認。

## 補足
- スクリプトの「valid JSON」表示は、出力が空のときも `jq .` が成功するため出る。1・2・3・4・6 では意味を持たない（stdout が空であることは `stdout=[]` で確認）。
- worktree は HEAD なので、作業ツリーで変更中の hook.py（未コミットの差分）は対象外。
- 変更したファイルは archives/agents/TODO-031/ 内のみ（verify.sh、本報告）。

## 確かめなかったこと
- 入れ直しに失敗する場合（`ccspk を入れ直せなかった` の分岐）。指示に無いため。
- 所要時間、実環境（本物の UV_TOOL_DIR）での動作。
