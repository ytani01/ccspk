# TODO-006 の分担

[TODO-006](../../todo/TODO-006.%20読み上げが使えない環境では、早々にあきらめて覚えておく.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、README から UsersGuide への移し替え | ― |
| reviewer（2 回、同じ担当に続けて依頼） | 分岐と条件式、誤って使えないと覚える場面、文書と実装の食い違い、移す元から落ちた内容 | [reviewer-report.md](reviewer-report.md)、[reviewer-report-2.md](reviewer-report-2.md) |
| verifier | 10 ケースの実測、UsersGuide の手順の再現 | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 実装は 1 ファイルの小さい関数なので main が持った
- 鳴らすかどうかの分岐が増えるので reviewer を入れた
- 本物の覚えるファイルを残すと利用者の読み上げが止まるので、verifier には
  一時ディレクトリで試させ、エンジンのサービスは止めさせなかった
