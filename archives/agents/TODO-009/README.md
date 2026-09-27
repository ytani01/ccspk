# TODO-009 の分担

[TODO-009](../../todo/TODO-009.%20返答の読み上げで、最初の音が出るまでを縮める.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、直す前と後の実測 | [main-measure.md](main-measure.md)、測定は [measure.py](measure.py) |
| reviewer | スレッドとキュー、子プロセスの止まり方、文の分け方 | [reviewer-report.md](reviewer-report.md) |
| verifier（2 回、同じ担当に続けて依頼） | 最初の音、継ぎ目、差し替え、本物の Stop hook、エンジン停止 | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 実装は 1 ファイルの書き換えなので main が持った
- 子プロセスの中にスレッドを持ち、プロセスグループごと止める作りに変わるので
  reviewer を入れた
- 最初の音までの時間は数字で判定できるので、測定スクリプトを main が 1 本作り、
  verifier にも同じものを使わせた
