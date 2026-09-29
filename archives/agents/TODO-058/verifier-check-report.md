# TODO-058 確認報告（verifier-check）

1. `uv run ccspk test`: 終了コード 0。末尾は `ok` `ok` `ok`。
2. 壊すと落ちるか（どちらも終了コード 1）。終わったあと `git diff src/ccspk/hook.py` は元の差分と一致（diff で確認）。
   - (a) `"--effort", "medium", ` を削除: 落ちた。
   - (b) `"medium"` を `"low"` に変更: 落ちた。
   - どちらも同じメッセージ（hook.py 898 行 `demo()`）:
     `AssertionError: [ "$(cat)" = "$SRC" ] && [ "$1 $3 $5" = "-p sonnet medium" ] && [ "$CCSPK_SPEAK" = 0 ] && [ "$PWD" = "$STATEDIR" ] && echo "**要約**、TODO-7 の件。"`
3. 本物 1 回（STATE は `mktemp -d`）: 成功。約 4.1 秒（`time` の total）。
   返り値（114 字）: `きょうは TODOゼロゴーハチの作業をしました。要約と翻訳で使う claude -p の effort を medium に下げると速くなるかを測り、そのための引数を追加しました。テストと文書も更新しています。次はコミットです。`
4. `rg -n -e '--effort' src docs`: hook.py:310 の 1 か所、UsersGuide.md 439・527、Developer.md 36・39・209。指示どおり。
5. `git status`: 変更は TODO.md、docs/Developer.md、docs/UsersGuide.md、src/ccspk/hook.py と未追跡の archives/agents/TODO-058/。hook.py の差分は `--effort medium` の追加、SUMMARY_TIMEOUT のコメント、demo() の 2 か所（引数位置 `$1 $3 $5`、翻訳側 `$9` を `${11}` に）。

食い違い・判断が要る点: なし。
補足: (a)(b) は同じ assert で落ちるので、値の違い（medium と low）も引数の有無も要約側のテストが見張っている。翻訳側は `${11}` の位置で引数の個数だけを見張る（値までは見ない）。
