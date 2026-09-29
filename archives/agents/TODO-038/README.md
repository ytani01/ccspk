# TODO-038 の分担

| 担当 | モデル | やったこと | 報告 |
|------|--------|-----------|------|
| main | Opus 5.5 | 実装・demo・文書、reviewer の指摘の直し | `reviewer-brief.md`・`verifier-brief.md` |
| reviewer | Opus 5.5 | 差分のレビュー 3 回（直しのたびに同じ担当へ続けて頼んだ） | `reviewer-report.md`・`-2.md`・`-3.md` |
| verifier | Sonnet 5.5 | 実際の返答（会話ログの 154 件）で HEAD と今を比べ、本物のエンジンで合成 | `verifier-report.md`・`measure.py` |

分担の理由: 変更は `tidy()` の中の 1 か所で、実装は main で足りる。改行の扱いという分岐が変わるので reviewer を入れ、
verifier は reviewer の後に回した。
