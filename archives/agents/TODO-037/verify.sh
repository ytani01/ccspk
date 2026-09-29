#!/bin/zsh
# TODO-037 確認。使い方: verify.sh [1-8 | 9]。本物の XDG_* は使わない。9 だけ本物の claude を 1 回呼ぶ
R=/home/ytani/work/ccspk
T=$(mktemp -d /tmp/ccspk-verify.XXXX)
export XDG_RUNTIME_DIR=$T/run XDG_STATE_HOME=$T/state XDG_CONFIG_HOME=$T/conf
mkdir -p $XDG_RUNTIME_DIR $XDG_STATE_HOME $XDG_CONFIG_HOME $T/bin
export PIPEWIRE_REMOTE=fake  # 偽の pw-play なので接続確認を飛ばす
mkdir -p $XDG_STATE_HOME/ccspk
echo "T=$T"
[[ $XDG_STATE_HOME == /tmp/ccspk-verify.* ]] || { echo bad env; exit 9 }
printf '#!/bin/sh\ncat >/dev/null\n' > $T/bin/pw-play
fake() { # $1 = sonnet のときの動作
cat > $T/bin/claude <<EOS
#!/bin/sh
echo "\$*" | cut -c1-80 >> $T/claude.log
cat >/dev/null
if [ "\$3" = sonnet ]; then $1; fi
EOS
chmod +x $T/bin/pw-play $T/bin/claude; }
fake 'echo "要約です。TODO-7 の件は済みました。"'
export PATH=$T/bin:$PATH
CC=$R/.venv/bin/ccspk
LONG=$(python3 -c "import json;print(json.load(open('$R/archives/agents/TODO-037/samples.json'))[1])")
stop_p() { python3 -c "import json,sys;print(json.dumps({'hook_event_name':'Stop','last_assistant_message':sys.argv[1]}))" "$1"; }
disp_p() { python3 -c "import json,sys;print(json.dumps({'hook_event_name':'MessageDisplay','message_id':'m1','index':0,'delta':sys.argv[1],'final':True}))" "$1"; }
sonnet() { rg -c -e '--model sonnet' $T/claude.log 2>/dev/null || echo 0; }
reset() { : > $T/claude.log; : > $XDG_STATE_HOME/ccspk/spoken.txt 2>/dev/null; \rm -f $XDG_RUNTIME_DIR/ccspk.last; sleep 0.2 }
waitchild() { local p=$(cat $XDG_RUNTIME_DIR/ccspk.pid 2>/dev/null); local s=$SECONDS; while kill -0 $p 2>/dev/null; do sleep 0.3; done; echo "child_wait=$((SECONDS-s))s"; }
lastline() { tail -n1 $XDG_STATE_HOME/ccspk/spoken.txt | python3 -c "import sys;l=sys.stdin.read().rstrip('\n');print(len(l),l)"; }
hook() { CCSPK_SPEAK=1 $CC hook; }

echo "== 1 test"; (cd $R && uv run ccspk test >/dev/null 2>&1; echo "exit=$?")
if [[ $1 != 9 ]]; then
echo "== 2 off, long"; reset; stop_p "$LONG" | hook
p=$(cat $XDG_RUNTIME_DIR/ccspk.pid); tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | cut -c1-90; echo; rg -c -e --summarize /proc/$p/cmdline 2>/dev/null || echo "summarize_in_cmdline=0"
waitchild; echo "sonnet=$(sonnet)"; lastline
echo "== 3 on, long"; $CC summary on; reset; stop_p "$LONG" | hook
p=$(cat $XDG_RUNTIME_DIR/ccspk.pid); tr '\0' '\n' </proc/$p/cmdline 2>/dev/null | rg -c -x -e --summarize; waitchild; echo "sonnet=$(sonnet)"; lastline
echo "== 4 on, display then stop"; reset; disp_p "$LONG" | hook; sleep 0.5; stop_p "$LONG" | hook; waitchild; sleep 1; echo "sonnet=$(sonnet)"
echo "== 5 on, short"; reset; stop_p "直しました。" | hook; waitchild; echo "sonnet=$(sonnet)"
echo "== 6 env=0"; reset; stop_p "$LONG" | CCSPK_SUMMARY=0 hook; waitchild; echo "sonnet=$(sonnet)"; CCSPK_SUMMARY=0 $CC summary; echo "exit=$?"
echo "== 7 stop while summarizing"; fake 'sleep 20'; reset; stop_p "$LONG" | hook; sleep 2
p=$(cat $XDG_RUNTIME_DIR/ccspk.pid); pg=$(ps -o pgid= -p $p | tr -d ' '); echo "pgid=$pg"; ps -o pid,pgid,cmd -g $pg | cut -c1-90
$CC stop; sleep 1; echo "after:"; ps -o pid,pgid,cmd -g $pg 2>&1 | cut -c1-90; echo "spoken_lines=$(wc -l < $XDG_STATE_HOME/ccspk/spoken.txt)"
echo "== 8 summary cmd"; \rm -f $XDG_CONFIG_HOME/ccspk/summary
for a in "" on off bad; do echo "--- summary $a"; $CC summary $a 2>&1; echo "exit=$?"; done
echo "--- doc example"; $CC summary on; CCSPK_SUMMARY=0 $CC summary
else
echo "== 9 real claude"; \rm -f $T/bin/claude; $CC summary on; reset
echo "claude=$(which claude)"; s=$SECONDS; stop_p "$LONG" | hook; waitchild; echo "total=$((SECONDS-s))s"; lastline; sleep 2; pgrep -af 'claude -p' | cut -c1-100 || echo "no claude -p left"
fi
export PIPEWIRE_REMOTE=fake  # 偽の pw-play なので接続確認を飛ばす
mkdir -p $XDG_STATE_HOME/ccspk
echo "T=$T"
