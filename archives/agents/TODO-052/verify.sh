#!/bin/zsh
# TODO-052 verifier: 偽の claude / pw-play で順番を時刻で測る。使い方: verify.sh  (リポジトリ直下から)
cd /home/ytani/work/ccspk || exit 1
LONG=$(python3 -c "print('これは長い日本語の返答です。'*20)")
run() {  # run <name> <claude-mode ok|fail> <env...>; stdin=JSON ; 環境は $tmp
  :
}
setup() {
  tmp=$(mktemp -d); mkdir -p $tmp/bin $tmp/ccspk
  log=$tmp/log
  cat > $tmp/bin/claude <<X
#!/bin/sh
cat >/dev/null
echo "\$(date +%s.%N) claude-start" >> $log
sleep 3
echo "\$(date +%s.%N) claude-end" >> $log
[ "\$FAKE_FAIL" = 1 ] && exit 1
echo "要約した文です。"
X
  cat > $tmp/bin/pw-play <<X
#!/bin/sh
echo "\$(date +%s.%N) pw-play-start \$(wc -c)" >> $log
echo "\$(date +%s.%N) pw-play-end" >> $log
X
  chmod +x $tmp/bin/*
}
hook() {  # hook <json> [env...]
  local json=$1; shift
  printf '%s' "$json" | env "$@" PATH=$tmp/bin:$PATH CCSPK_SPEAK=1 XDG_RUNTIME_DIR=$tmp XDG_STATE_HOME=$tmp XDG_CONFIG_HOME=$tmp PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u) .venv/bin/ccspk hook
}
waitpid() {
  for i in $(seq 300); do
    p=$(cat $tmp/ccspk.pid 2>/dev/null); [ -n "$p" ] && kill -0 $p 2>/dev/null || break; sleep 0.1
  done
}
show() { echo "== $1"; sort -n $log; echo "-- spoken.txt"; cat $tmp/ccspk/spoken.txt 2>/dev/null; echo "-- pw-play count: $(rg -c pw-play-start $log)"; }
J=$(python3 -c "import json,sys;print(json.dumps({'last_assistant_message':sys.argv[1]}))" "$LONG")
setup; hook "$J" CCSPK_SUMMARY=1; waitpid; show "1 summary ok"; rm -r $tmp
setup; hook "$J" CCSPK_SUMMARY=1 FAKE_FAIL=1; waitpid; show "2 summary fail"; rm -r $tmp
setup; touch $tmp/ccspk/translate; hook '{"last_assistant_message":"Tests passed and the build is done."}' CCSPK_SUMMARY=0; waitpid; show "3 translate ok"; rm -r $tmp
setup; touch $tmp/ccspk/queue
J2=$(python3 -c "import json,sys;print(json.dumps({'last_assistant_message':sys.argv[1]}))" "$(python3 -c "print('別の長い日本語の返答です。'*20)")")
hook "$J" CCSPK_SUMMARY=1; hook "$J2" CCSPK_SUMMARY=1
sleep 1; waitpid; sleep 8; waitpid; show "4 queue"; rm -r $tmp
