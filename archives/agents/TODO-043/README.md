# TODO-043 の分担

- main: 実装（`user_dict.py` の `speaker()`・`styles()`・`pick()`・`speaker_`、`hook.py` の `SPEAKER` の置き換え、`cli.py`、`demo()` の例、文書）
- reviewer（Opus 5.5 / high）: 分岐（`pick()`・引数の検査・終了ステータス）、話者が全部の呼び出し元に効くか、文書との食い違い、テストの強さ → [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 本物のエンジン相手にコマンドの表示・書き込み・断る場合を実測し、`play()` と `query()` が決めた話者で要求を出すかを差し替えで確かめる → [verifier-report.md](verifier-report.md)（`verify.sh`・`verify.out`・`anchors.py`）

分担の理由: 引数で分岐が増え、話者を 4 つの呼び出し元に効かせる変更なので、レビューと実測を分けた。実装は 3 ファイルで小さいので main が受け持った。
reviewer を先にし、その指摘（Developer.md の 4.1、エンジンに無い番号のときの文書、書き込みを置き換えにする）を直した後の差分で verifier に測らせた。
`impl.diff` は verifier に渡した時点の差分。
