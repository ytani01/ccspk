# TODO-044 の分担

- main: 実装（`summarize()`・`demo()`・`docs/Developer.md`）。1 関数と文書 1 節なので分けない
- reviewer（Opus 5.5 / high）: 分岐は変えないが、渡す文と指示が変わり「`</reply>` は現れない」という前提に頼るので入れた。
  報告は [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 本物の `claude -p` で要約できるかを試す。報告は [verifier-report.md](verifier-report.md)
- reviewer を先、verifier を後に回した。verifier には reviewer が挙げた `</reply>` を含む文も試させた
