# TODO-033 の分担

- main — `drop_commit_ids`、`demo()` の例、UsersGuide.md。ログの調べ方は `scan.py`
- reviewer（Opus 5.5 / high） — 正規表現の条件で読みが変わるので、誤検出・取りこぼし、置き換えの順序、
  `demo()` の強さ、ログでの当たり方を見る
- verifier（Sonnet 5.5 / medium） — reviewer の指摘を直した後。9 通りの壊し方で `demo()` が落ちるか、
  UsersGuide.md の例が `to_speech` の結果と合うかを試す

報告:

- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)
- [mutate.py](mutate.py) — verifier の壊し方のスクリプト
