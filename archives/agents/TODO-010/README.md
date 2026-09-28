# TODO-010 の分担

[TODO-010](../../todo/TODO-010.%20Stop%20以外に、途中の報告の文章も読み上げる.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実測（測定用のフック）、実装、文書、指摘の反映 | ― |
| claude-code-guide | 途中の文章を受け取れるフックが公式の文書にあるか | ―（返事だけ） |
| reviewer | 分岐、同時に来たときの競合、文書とコードの突き合わせ。反映の後にもう一度 | [reviewer-report.md](reviewer-report.md)、[reviewer-report-2.md](reviewer-report-2.md) |
| verifier | 一時ディレクトリでフックを手で起動し、同時・5 秒・空の文・古い分を試す | [verifier-report.md](verifier-report.md) |

`reviewer-*.py` は reviewer が試すのに使ったスクリプト。

## 分担にした理由

- 並んで走るフックの競合と、2 度読まない判定があるので、確認とは別に reviewer を入れた
- 手で再現できる手順があるので、再現を verifier に分けた。reviewer の後に回した
- フックの仕様は Claude Code 自体の話なので claude-code-guide に聞いた
