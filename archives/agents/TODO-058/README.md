# TODO-058 の分担

- verifier（Sonnet 5.5 / medium）: `claude -p` を effort 3 通りで測った。手順の決まった測定なので Sonnet にした。
  報告は [verifier-report.md](verifier-report.md)。スクリプトは `measure.py`（材料選びは `pick.py`）、材料は `inputs/`、出力は `outputs/`・`results.json`
- main: 利用者が `medium` に決めた後、`hook.py`・`demo()`・文書を直した（数行の変更なので implementer は分けなかった）
- reviewer（Opus 5.5 / high）: 引数の位置に頼るテストの分岐が変わるので入れた。報告は [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: テストが壊すと落ちるか、本物で 1 回動くかを確かめた。報告は [verifier-check-report.md](verifier-check-report.md)

reviewer を先、verifier を後に回した（`~/.claude/CLAUDE.md`）。
