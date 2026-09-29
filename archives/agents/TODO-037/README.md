# TODO-037 の分担

| 担当 | モデル | やったこと | 報告 |
|------|--------|-----------|------|
| main | Opus 5.5 | 実装の前の測定（`pick.py`・`measure.py`・`prompt.txt`・`samples.json`）、設計、依頼、`CLAUDE.md` の直し、demo の時間切れの例の直し | `main-measure.md`・`brief.md`・`verifier-brief.md` |
| implementer | Opus 5.5 | 実装・demo・文書、reviewer の指摘の直し | `implementer-report.md`・`implementer-report-2.md` |
| reviewer | Opus 5.5 | 差分のレビュー、直しの見直し | `reviewer-report.md`・`reviewer-report-2.md` |
| verifier | Sonnet 5.5 | 一時の XDG・偽の `claude` でフックを動かし、本物の `claude` で 1 回 | `verifier-report.md`・`verify.sh` |

分担の理由: 子プロセスとフックの流れにまたがり、demo・文書もまとめて要るので、実装を implementer（Opus）に分けた。
分岐（要約するかの分かれ目・2 度読まない仕組み）が変わるので reviewer を入れ、verifier は reviewer の後に回した。
