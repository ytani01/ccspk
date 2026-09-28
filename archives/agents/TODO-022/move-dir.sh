#!/bin/sh
# TODO-022: 手元のディレクトリを ~/work/claudecodespeak から ~/work/ccspk へ移す。
# Claude Code を終了してから走らせる。
set -eu

OLD="$HOME/work/claudecodespeak"
NEW="$HOME/work/ccspk"
OLD_PROJ="$HOME/.claude/projects/-home-ytani-work-claudecodespeak"
NEW_PROJ="$HOME/.claude/projects/-home-ytani-work-ccspk"
UNIT_DIR="$HOME/.config/systemd/user"

die() { echo "move-dir.sh: $*" >&2; exit 1; }

# 先に確かめる。外れたら何も変えずに止まる
[ -d "$OLD" ] || die "$OLD がない"
[ ! -e "$NEW" ] || die "$NEW が既にある"
[ ! -e "$NEW_PROJ" ] || die "$NEW_PROJ が既にある"

\mv "$OLD" "$NEW"
if [ -d "$OLD_PROJ" ]; then
    \mv "$OLD_PROJ" "$NEW_PROJ"
fi

cd "$NEW"
\rm -rf .venv
uv sync
uv tool install --reinstall .

# 旧いパスを指す symlink を張り直す。エンジンは止めない
\rm -f "$UNIT_DIR/voicevox-engine.service" "$UNIT_DIR/default.target.wants/voicevox-engine.service"
systemctl --user daemon-reload
systemctl --user link "$NEW/systemd/voicevox-engine.service"
systemctl --user enable voicevox-engine.service

echo "command -v ccspk: $(command -v ccspk || true)"
echo "command -v claudecodespeak: $(command -v claudecodespeak || true)"
ccspk status
