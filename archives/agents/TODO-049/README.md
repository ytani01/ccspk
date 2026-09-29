# TODO-049 の分担

- main: 実装（`tidy()` の置き換え、`demo()` の例、`docs/UsersGuide.md` の「2.2」）
- reviewer（Opus 5.5 / high）: 置き場所と前後の処理との関係、テストの強さ → [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 本物のエンジンの `audio_query` で置き換えの前後の `kana` を比べる → [verifier-report.md](verifier-report.md)

分担の理由: 分岐は無いが読みが変わる変更なので、レビューと実測を分けた。実装は 1 か所なので main が受け持った。
reviewer を先にし、その指摘（前後のスペース）を直した後の差分で verifier に測らせた。
`impl.diff` は verifier に渡した時点の差分。
