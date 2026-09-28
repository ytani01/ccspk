# TODO-022 verifier 報告

全項目 一致。食い違いなし。

1. 旧名: rg（-g '!uv.lock' 付き）の出力は TODO.md の TODO-022 節（55-96 行）だけ。uv.lock は rg -c で該当なし（rc=1）。
   - 参考: 環境変数 `CLAUDE_TTS_SPEAK` は改名されていない（`claude-tts` のパターンに合わないため rg に出ない）。src/ccspk/hook.py と docs に残る。項目の対象外かどうかは判断できない。
2. `uv run ccspk test`: `ok` `ok`、rc=0。
3. フック: 一時ディレクトリで `~/.local/bin/ccspk hook`（Stop の JSON）rc=0。`find` の結果は ccspk.pid / ccspk.last / ccspk.lock。ccspk.unusable なし。
   - settings.json: 69・80 行が `! command -v ccspk >/dev/null || ccspk hook`。
   - `command -v claudecodespeak` は空（rc=1）。
   - 実際に音が鳴ったかは聞いていない。
4. move-dir.sh: HOME を一時ディレクトリにし、uv / systemctl / ccspk を偽物にして実行。rc=0。
   - work/ccspk に移動。.venv は消えた。プロジェクトのメモリも -home-ytani-work-ccspk へ移動。symlink 2 本は消え、旧ディレクトリなし。
   - 記録された呼び出しは、順に `uv sync`、`uv tool install --reinstall .`、`systemctl --user daemon-reload`、`systemctl --user link <HOME>/work/ccspk/systemd/voicevox-engine.service`、`systemctl --user enable voicevox-engine.service`、`ccspk status`。TODO.md の説明どおり。
   - 最後の `command -v claudecodespeak` は空。
   - 偽物なので、本物の uv / systemctl の挙動は確かめていない。
5. 前提外れ: HOME/work/ccspk を先に作って実行。「... work/ccspk が既にある」を出して rc=1。実行前後の find の diff が空。calls.log なし（偽コマンドは呼ばれていない）。他の 2 つの前提（旧ディレクトリなし、NEW_PROJ あり）は試していない。

git status: 変更は CLAUDE.md, README.md, TODO.md, docs/*, pyproject.toml, uv.lock, src の git mv、archives/agents/TODO-022/。指示の範囲内。

## 追加の確認（CCSPK_SPEAK）

1. 旧名の rg: TODO.md 58 行（TODO-022 節）だけ。他になし。settings.json の env は `"CCSPK_SPEAK": "1"`（10 行）、CLAUDE_TTS なし。
2. `uv run ccspk test`: `ok` `ok`、rc=0。
3. フック（一時 XDG_RUNTIME_DIR、`~/.local/bin/ccspk hook`、各 1 回）:
   - CCSPK_SPEAK=1: rc=0、ccspk.pid / ccspk.last / ccspk.lock ができた。
   - CLAUDE_TTS_SPEAK=1 のみ（CCSPK_SPEAK は unset）: rc=0、ファイルなし（鳴らない）。
   - 音が鳴ったかは聞いていない。
