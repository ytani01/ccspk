# TODO-022 の分担

- main（Opus 5.5）: 改名、`~/.claude/settings.json` の書き換え、`move-dir.sh` の作成
- verifier（Sonnet 5.5）: 旧名が残っていないか、テスト、フックの手動実行、`move-dir.sh` を偽の
  `HOME` と偽のコマンドで走らせる確認。報告は `verifier-report.md`

名前を変えるだけで挙動は変わらない見込みだったので、reviewer は置かなかった。
確認は `CLAUDE.md` の決まりどおり別の担当に分けた。
`move-dir.sh` は利用者が走らせたスクリプトそのもの。
