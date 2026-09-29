# TODO-039 の分担

- main: 実装（`user_dict.py` の `volume()`・`pw_play()`・`write_config()`・`volume_`、`hook.py` の `play()`、`cli.py`、`demo()` の例、文書）
- reviewer（Opus 5.5 / high）: 範囲の判定と既定値、`write_config()` にまとめた後の `speaker` の書き込み、全部の呼び出し元に効くか、UsersGuide の番号ずらしとアンカー、文書との食い違い → [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 一時の `XDG_CONFIG_HOME` で、コマンドの表示・書き込み・断る値を実測し、`ccspk say` で `pw-play` に `--volume=` が付くことを `pgrep` で確かめる。範囲の判定を壊して `ccspk test` が落ちることも → [verifier-report.md](verifier-report.md)

分担の理由: 引数の検査と、音量を 2 つの呼び出し元（`play()` と `dict add --speak`）に効かせる挙動の変更なので、レビューと実測を分けた。実装は 3 ファイルで小さく、`ccspk speaker`（TODO-043）と同じ形なので main が受け持った。
reviewer を先にし、その指摘（`-0` が `-0.0` で残る）を直した後の差分で verifier に測らせた。
