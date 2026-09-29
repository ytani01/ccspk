# TODO-036 の分担

- main — 実装前の測定（`main-measure.md`、`measure.py`、`words.py`、`prompt.txt`）、設計（`brief.md`）、
  レビュー後の小さな直し（知らせに読みを入れる、`same()`、Opus・文あり、前後 30 字）、判定の比べ（`judge.py`、`judge.out`）
- implementer（Opus 5.5 / medium） — `check.py` と `hook.py`・`user_dict.py`・文書。子プロセス・ロック・mtime が
  込み入るので Opus に上書きした
- reviewer（Opus 5.5 / high） — 起こす条件・失敗の扱い・誤った登録を防げるかが変わるので入れた。4 回
- verifier（Sonnet 5.5 / medium） — reviewer の後。偽の `claude` と一時ディレクトリでの通し、壊し方、本物の `claude -p` 1 回。3 回

報告:

- [implementer-report.md](implementer-report.md)、[implementer-report-2.md](implementer-report-2.md)
- [reviewer-report.md](reviewer-report.md)、[reviewer-report-2.md](reviewer-report-2.md)、
  [reviewer-report-3.md](reviewer-report-3.md)、[reviewer-report-4.md](reviewer-report-4.md)
- [verifier-report.md](verifier-report.md)、[verifier-report-2.md](verifier-report-2.md)、[verifier-report-3.md](verifier-report-3.md)
- 依頼: [brief.md](brief.md)、[reviewer-brief.md](reviewer-brief.md)、[verifier-brief.md](verifier-brief.md)
- verifier のスクリプト: `verify.sh`〜`verify4.sh`、`break.sh`、`real_claude.py`、`real_claude2.py`
