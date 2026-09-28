# TODO-021 の分担

- main: 実装（`user_dict.py` の `save()`、unit の `ExecStartPost`、辞書の移行、文書）。変更が小さいので実装担当は分けない
- reviewer: 書き出しの時機と置き換え方、`ExecStartPost` の待ち方と失敗の扱い、古い記述の残りを見る → [reviewer-report.md](reviewer-report.md)
- verifier: `XDG_CONFIG_HOME` を一時ディレクトリに向けた `dict add`・`remove`・`import` の書き出しと、エンジンの再起動での読み込みを確かめる → [verifier-report.md](verifier-report.md)

reviewer は指摘を受けて直した分を、同じ担当に続けて見させた → [reviewer-report-2.md](reviewer-report-2.md)

振り返りは `archives/todo/TODO-021. 辞書を ~/.config に置き、エンジンの起動時に読み込む.md`。
