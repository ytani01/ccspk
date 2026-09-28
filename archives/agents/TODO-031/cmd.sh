cd "$CLAUDE_PROJECT_DIR" || exit 0
r="$(uv tool dir)/ccspk/uv-receipt.toml"
[ -f "$r" ] || exit 0
[ -n "$(find src pyproject.toml -name __pycache__ -prune -o -newer "$r" -print -quit)" ] || exit 0
if ! out=$(uv run ccspk test 2>&1); then m='ccspk test が落ちたので、入れ直さなかった'
elif ! out=$(uv tool install -q --reinstall . 2>&1); then m='ccspk を入れ直せなかった'
else exit 0; fi
jq -n --arg m "$m: $(printf '%s' "$out" | tail -n 5)" '{systemMessage: $m}'
