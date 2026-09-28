# TODO-032 の分担

- main — `to_speech` の置き換え、`demo()` の例、UsersGuide.md。指摘を受けて `demo()` に 2 つ足した
  （改行をスペースに数えない例、`(` の直後にスペースが無い例）
- reviewer（Opus 5.5 / high） — 正規表現の条件で読みが変わるので、誤検出・取りこぼし、ほかの置き換えとの順序、
  `demo()` の強さを見る
- verifier（Sonnet 5.5 / medium） — reviewer の後。正規表現に 10 通りの変異を入れて `ccspk test` が落ちるか、
  UsersGuide.md の例が `to_speech` の結果と合うかを試す

報告:

- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)
