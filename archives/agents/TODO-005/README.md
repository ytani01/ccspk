# TODO-005 の分担

- main: 候補の語の収集、利用者との相談、辞書の登録、`to_speech` と文書の実装
- reviewer（Opus 5.5 / high）: 正規表現の分岐が変わるので、レビューを別にした。
  1 回目の指摘で直した後、同じ担当に再レビューを頼んだ。報告は `reviewer-report.md`
- verifier（Sonnet 5 / medium）: 読みの一覧の再現と、UsersGuide のコマンドを
  書いたとおりに叩く確認。報告は `verifier-report.md`

ほかのファイル: `readings.md`（直す前と後の読み）、`collect.py`（過去の返答から
候補を数える）、`kana.py`・`words.txt`（読みを取る）、verifier が作った突き合わせの
スクリプト。
