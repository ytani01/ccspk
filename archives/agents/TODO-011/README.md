# TODO-011 の分担

[TODO-011](../../todo/TODO-011.%201%20文目を短く切って、最初の音をさらに早める.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、直す前と後の実測、利用者との聞き比べ | [main-measure.md](main-measure.md)、測定は [measure.py](measure.py) |
| reviewer（2 回、同じ担当に続けて依頼） | split_first の分岐と境界、区切りの文字、テストの強さ | [reviewer-report.md](reviewer-report.md)、[reviewer-report-2.md](reviewer-report-2.md) |
| verifier | テストの強さ、最初の音、本物の Stop hook、差し替え | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 実装は 1 ファイルの小さい関数なので main が持った
- 分岐と境界（8 字・30 字）が増えるので reviewer を入れた
- 継ぎ目の聞こえ方は機械で判定できないので、main が利用者に鳴らして決めてもらい、
  verifier には時間とプロセスだけを測らせた
