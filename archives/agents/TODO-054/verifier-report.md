# TODO-054 verifier report

実行は cwd=/tmp、`--model haiku`。変更ファイルは TODO.md, docs/Developer.md, docs/UsersGuide.md のみ（文書だけ。指示の範囲内）。コード・文書は直していない。

## 1. CCSPK_SPEAK=0 の環境変数 → 中では 1: 一致
`CCSPK_SPEAK=0 claude -p "printenv CCSPK_SPEAK を実行して、出力だけを返して" --model haiku --allowedTools 'Bash(printenv:*)'` → 出力 `1`

## 2. --settings で上書き → 0: 一致
`claude -p "<同上>" --model haiku --settings '{"env":{"CCSPK_SPEAK":"0"}}' --allowedTools 'Bash(printenv:*)'` → 出力 `0`

注: 依頼どおりの引数順（`--allowedTools` の後ろにプロンプト）だと、`--allowedTools` が可変長でプロンプトを飲み込み
`Error: Input must be provided either through stdin or as a prompt argument when using --print` で落ちる。プロンプトを先に置いて実行した。

## 3. --setting-sources "" でフックが出ない: 一致（ただし依頼の `--debug` 標準出力では見えない）
- `--debug` は stdout/stderr に何も出さなかった（`2>&1` で 1〜3 行、応答文のみ）。`--debug-file` に切り替えて比較した。
- `claude -p '1+1 は?' --model haiku --setting-sources "" --debug-file da.log`（rc=0）
  - `Registered 0 hooks from 2 plugins` / `Hooks: Found 0 total hooks in registry` / `settingsEnv keys: none`
  - `Hook SessionStart ... success` の行は無い
- 無しの場合 `--debug-file db.log`（rc=0）
  - `Registered 3 hooks from 4 plugins` / `Hook SessionStart:startup (SessionStart) success:...` が出る / `settingsEnv keys: EDITOR,CLAUDE_CODE_ENABLE_TODO_TOOLS,CCSPK_SPEAK`
- 見分けられる。`hook` を単純に grep すると両方にヒットする（plugin の hooks module の行）ので、`Hook SessionStart ... success`、`Registered N hooks`、`settingsEnv keys` で見分ける。

## 4. UsersGuide のコマンド例の JSON: 一致
UsersGuide.md 1.3: `claude -p --settings '{"env":{"CCSPK_SPEAK":"0"}}' '…'` は 2 で実行した JSON と文字単位で同じ。

## 確かめられなかったこと（境界線上、報告のみ）
- cwd=/tmp で実行したため、ccspk リポジトリの Stop フック（ccspk hook）が実際に動いた行は 3 では見ていない。
  「フックが登録されないから読み上げが起きない」は、ユーザー設定のフックが 0 件になることまでの確認。
- Developer.md の「`CCSPK_SPEAK=0` は念のためで、これだけでは止まらない」は 1 の結果と整合する。
- `--debug` の標準出力が空だったのは、この環境の claude のバージョン挙動。文書に `--debug` の記述があるかは見ていない。
