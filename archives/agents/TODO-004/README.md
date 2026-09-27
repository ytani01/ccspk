# TODO-004 の分担

[TODO-004](../../todo/TODO-004.%20読み上げの文字数の上限で、文の途中で切らない.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、壊して落ちるかの確認 | — |
| reviewer（2 回。TODO-003 と同じ担当に続けて依頼） | clip の境界、延ばした後の長さ、テストの強さ | [reviewer-report.md](reviewer-report.md)、[reviewer-report-2.md](reviewer-report-2.md) |
| verifier（TODO-003 と同じ担当に続けて依頼） | テストの強さ、日本語・英語の長い本文、エンジンのメモリ | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 実装は 1 関数なので main が持った
- 境界の分岐なので reviewer を入れた。直前の TODO-003 で同じファイルを見ていたので、
  同じ担当に続けて頼んだ（verifier も同じ）
- reviewer の 1 回目の実験がエンジンと利用者のサービスを OOM で落としたので、
  2 回目と verifier には「エンジンに 300 字を超える文を投げない」と書いた
