# TODO-046 の分担

- main: 実装（`hook.py`・`cli.py`・文書）。1 ファイルの中の振り分けと子プロセスの扱い、それに合わせた文書なので分けない
- reviewer（Opus 5.5 / high）: 分岐（要約・翻訳・そのまま）と子プロセスに渡す本文が変わるので入れた。2 回。
  報告は [reviewer-report.md](reviewer-report.md)・[reviewer-report-2.md](reviewer-report-2.md)
- verifier（Sonnet 5.5 / medium）: 本物の `claude -p` で要約・翻訳の出力（ひらがなの書き方）を見るのと、一時ディレクトリの `XDG_*` でフックを通す。
  同じ担当に続けて 3 回頼んだ。報告は [verifier-report.md](verifier-report.md)・[verifier-report-2.md](verifier-report-2.md)・
  [verifier-report-3.md](verifier-report-3.md)、計測は [verify.py](verify.py)・[verify.sh](verify.sh)
- reviewer を先、verifier を後に回した。reviewer の 2 回目の指摘を直してから verifier を起こした
