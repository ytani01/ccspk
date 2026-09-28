# TODO-016 の分担

| 担当 | 受け持ち | 理由 |
|------|----------|------|
| main | 実装（`user_dict.py` と `docs/UsersGuide.md`） | 1 ファイルに 1 オプション。込み入ったロジックは無い |
| reviewer（Opus 5.5 / high） | 差分のレビュー | 指定あり/なし × 新規/登録済みで分岐が変わる |
| verifier（Sonnet 5 / medium） | 実際のエンジンで 4 通り＋範囲外を確かめる | reviewer の後に回す |

報告: `reviewer-report.md`、`verifier-report.md`
