# TODO-029 の分担

- main — 読みの計測（`kana.py`・`kana.tsv`）、`to_speech` の置き換えと `demo()`、UsersGuide.md
- reviewer（Opus 5.5 / high） — 分岐（正規表現）が変わるので、置き換える範囲が背景で決めたとおりか、
  ほかの整形との順序で壊れるものが無いかを見る
- verifier（Sonnet 5.5 / medium） — reviewer の後。自己テスト、テストを壊すと落ちるか、
  UsersGuide.md の例を `to_speech` と `dict kana` で試す

報告:

- [reviewer-report.md](reviewer-report.md)
- [reviewer-report-2.md](reviewer-report-2.md)（指摘を直した後の再レビュー）
- [verifier-report.md](verifier-report.md)
