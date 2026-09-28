# TODO-030 の分担

- main — 読みの計測（[kana.md](kana.md)）、`squeeze` と `chunks` からの呼び出し、`demo()`、UsersGuide.md
- reviewer（Opus 5.5 / high） — 分岐（正規表現）が変わるので、詰める範囲が背景で決めたとおりか、
  split_first との順序、`demo()` が壊すと落ちるかを見る
- verifier（Sonnet 5.5 / medium） — reviewer の後。自己テスト、UsersGuide.md の例、kana.md の再現

TODO-031 と同じ会話・同じ作業ツリーで並行して進めた。

報告:

- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)（計測は [verify.sh](verify.sh)）
