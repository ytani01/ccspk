# TODO-031 の分担

- main — 前提の計測（`--reinstall` の要否、`uv-receipt.toml` の mtime、venv を作り直すか）、
  フックのコマンド（`cmd.sh`・`settings.json`）、CLAUDE.md。`.claude/settings.json` への書き込みは
  auto mode に止められたので、利用者が `settings.json` を写して置いた
- reviewer（Opus 5.5 / high） — 更新の判定とテスト・入れ直しの成否で分岐が変わるので、判定の漏れ・誤検出、
  読み上げのフックとの競合を見る
- verifier（Sonnet 5.5 / medium） — reviewer の後。別の worktree と一時の `UV_TOOL_DIR`・`UV_TOOL_BIN_DIR` で、
  変更なし・変更あり・入れ直した直後・`__pycache__` だけ・テスト失敗・入れていない、の 6 通りを試す
  （作業ツリーでは TODO-030 を並行して進めていたので、`src/` を壊す確認を分けた）

報告:

- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)（計測は [verify.sh](verify.sh)）
