#!/bin/sh
# TODO-031 確認: Stop フックのコマンドを worktree + 一時の UV_TOOL_DIR で実測する
S=/tmp/claude-649/-home-ytani-work-ccspk/e4bc7a2b-d082-485f-a808-a530d0693f1d/scratchpad/verify031
SET=/home/ytani/work/ccspk/.claude/settings.json
export UV_TOOL_DIR=$S/tools UV_TOOL_BIN_DIR=$S/bin CLAUDE_PROJECT_DIR=$S/wt
rm -rf "$S"; mkdir -p "$S"
git -C /home/ytani/work/ccspk worktree add "$S/wt" HEAD >/dev/null 2>&1
cd "$S/wt" || exit 1
R=$UV_TOOL_DIR/ccspk/uv-receipt.toml
P=$(echo $UV_TOOL_DIR/ccspk/lib/python*/site-packages/ccspk)
jq -r '.hooks.Stop[0].hooks[0].command' $SET > "$S/cmd.sh"
uv tool install -q . || echo "INSTALL FAILED"
run() { echo "== $1"; b=$(stat -c %Y "$R" 2>/dev/null); out=$(sh "$S/cmd.sh"); rc=$?
  a=$(stat -c %Y "$R" 2>/dev/null)
  echo "rc=$rc mtime_before=$b mtime_after=$a changed=$([ "$a" = "$b" ] && echo no || echo yes)"
  echo "stdout=[$out]"; echo "$out" | jq . >/dev/null 2>&1 && echo "stdout is valid JSON"; }
run "1 変更なし"
sleep 1; echo '# verify' >> src/ccspk/cli.py
run "2 変更あり"
echo "installed cli.py tail: $(tail -n1 $P/cli.py)"
run "3 直後にもう一度"
echo "find src -newer receipt:"; find src -newer "$R"
echo "find src pyproject.toml (pycache除外) -newer:"; find src pyproject.toml -name __pycache__ -prune -o -newer "$R" -print
ls src/ccspk/__pycache__/*.pyc >/dev/null 2>&1 || .venv/bin/python -c 'import ccspk.hook'
sleep 1; touch src/ccspk/__pycache__/*.pyc
run "4 pycache のみ"
cp $P/hook.py "$S/hook.installed.before"
sleep 1; sed -i 's/assert clip(a \* LIMIT) == a \* LIMIT/assert clip(a * LIMIT) != a * LIMIT/' src/ccspk/hook.py
git diff --stat -- src/ccspk/hook.py
run "5 テスト失敗 (1回目)"
cmp $P/hook.py "$S/hook.installed.before" && echo "installed hook.py unchanged"
run "5b テスト失敗 (2回目)"
uv tool uninstall ccspk >/dev/null 2>&1
run "6 未インストール"
cd /; git -C /home/ytani/work/ccspk worktree remove --force "$S/wt"; \rm -rf "$S/tools" "$S/bin"
