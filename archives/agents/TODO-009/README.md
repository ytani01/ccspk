# TODO-009 の分担

[TODO-009](../../todo/TODO-009.%20VOICEVOX%20の辞書に語を簡単に足す%20CLI%20を作る.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、文書、指摘の反映 | ― |
| reviewer | 分岐と決めたことの突き合わせ、エラー処理、API の使い方、文書、テストの強さ | [reviewer-report.md](reviewer-report.md) |
| verifier | エンジンに対して登録・書き換え・エラー・`--speak`・片付けを実際に試す | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 分岐（アクセントの見なし、登録済みの判定）があるので、確認とは別に reviewer を入れた
- 書いたとおりに試せるコマンドがあるので、再現を verifier に分けた。reviewer の指摘で
  コードが変わるので、verifier は後に回した
