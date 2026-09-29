# TODO-052 の分担

- main: 実装（`hook.py` の `play_rewritten()`・`rewrite()`・`NAMES`・`demo()`）と文書
- reviewer（Opus 5.5 / high）: 差分のレビュー。挙動（裏のスレッドで `claude -p` を走らせる順番）が変わるので入れた。2 回
- verifier（Sonnet 5.5 / medium）: 偽の `claude`・偽の `pw-play` と本物のエンジンでフックを動かし、時刻の並びで順番を測った

報告: [reviewer-report.md](reviewer-report.md)、[verifier-report.md](verifier-report.md)。計測スクリプトは [verify.sh](verify.sh)。
