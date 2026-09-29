# TODO-042 の分担

- main: `synthesize()` の 1 行と `docs/Developer.md` の説明を書いた
- reviewer（Opus 5.5 / high）: 挙動が変わる変更なので付けた。引数がエンジンの仕様どおりか、ほかに `/synthesis` を呼ぶ所が無いかを見させた → [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 合成した wav の長さで、語尾の「ァ」が消えたかを測らせた。reviewer の後に回した → [verifier-report.md](verifier-report.md)
