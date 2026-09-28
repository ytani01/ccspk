# TODO-011 の分担

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | import の時間の実測、実装、文書 | ― |
| reviewer | 差分（移したコードの挙動、click への移し替え、子プロセスの見分け方、文書とコードの突き合わせ） | [reviewer-report.md](reviewer-report.md) |
| verifier | `uv tool install` で入れたコマンドで、文書の手順を書いたとおりに試す | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 起動の仕方と、前の再生を止めるときの見分け方が変わるので、確認とは別に reviewer を入れた
- 入れ方と試し方の手順を書き換えたので、その再現を verifier に分けた。reviewer の後に回した
