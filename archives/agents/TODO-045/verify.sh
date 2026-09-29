#!/bin/zsh
# TODO-045 実機確認。リポジトリ直下から: zsh archives/agents/TODO-045/verify.sh [項目番号...]
D=${0:A:h}; R=${D:h:h:h}; cd $R
A="狐は静かな森の奥でゆっくりと歩きながら、遠くに見える古い山の頂を眺めていました。"
B="海辺の小さな町では、朝早くから漁師たちが大きな網を丸めて、港の船に積み込んでいます。"
C="図書館の窓際の席に座って、雨の音を聞きながら分厚い本の最初の頁をそっとめくりました。"
setup() { tmp=$(mktemp -d); mkdir -p $tmp/bin $tmp/ccspk
  cat > $tmp/bin/claude <<'F'
#!/bin/sh
in=$(cat)
case "$in" in *狐*) sleep 4;; esac
echo "要約の文です。"
F
  chmod +x $tmp/bin/claude
  export XDG_RUNTIME_DIR=$tmp XDG_STATE_HOME=$tmp XDG_CONFIG_HOME=$tmp PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u) CCSPK_SPEAK=1 CCSPK_SUMMARY=0
  export PATH=$tmp/bin:$PATH; }
feed() { printf '%s' "{\"last_assistant_message\":\"$1\"}" | .venv/bin/ccspk hook; }
mon() { python $D/monitor.py $tmp $1 > $tmp/mon.txt & MON=$!; }
alive() { ps -eo pid,pgid,args | rg "ccspk.hook|pw-play" | rg -v "rg |ps -eo" | rg "$tmp|ccspk.hook --play" ; }
# 自分の子プロセスだけ数える: PIDFILE の PID
kids() { for p in $(cat $tmp/ccspk.pid 2>/dev/null); do [ -d /proc/$p ] && echo $p; done; }
run() { setup; echo "### 項目 $1 tmp=$tmp"; }
sel=("$@"); want() { [ ${#sel} -eq 0 ] || [[ " $sel " == *" $1 "* ]]; }
if want 1; then for n in 1 2; do run 1.$n; touch $tmp/ccspk/queue; mon 40
  T0=$(date +%s.%N); feed $A; sleep .3; feed $B; sleep .3; feed $C
  echo "pidfile:"; cat $tmp/ccspk.pid; echo "hook 完了 $(echo "$(date +%s.%N)-$T0"|bc)s"
  wait $MON; echo "--- monitor"; cat $tmp/mon.txt; rm -rf $tmp; done; fi
if want 2 || want 3; then for m in 2 3; do want $m || continue; run $m; touch $tmp/ccspk/queue; mon 12
  feed $A; sleep .3; feed $B; sleep .3; feed $C; sleep 1.5
  echo "pidfile:"; cat $tmp/ccspk.pid; P=$(cat $tmp/ccspk.pid|tr '\n' ' ')
  echo "止める前の生存: $(kids|tr '\n' ' ')"
  if [ $m = 2 ]; then .venv/bin/ccspk stop; echo "stop rc=$?"; else printf '%s' '{"last_assistant_message":""}' | .venv/bin/ccspk hook; echo "空Stop rc=$?"; fi
  sleep 1; echo "止めた後の子プロセス: [$(for p in ${=P}; do [ -d /proc/$p ] && echo $p; done)]"
  echo "pw-play 残り: [$(python - <<PY
import os
for d in os.listdir('/proc'):
    try:
        if d.isdigit() and open(f'/proc/{d}/comm').read().strip()=='pw-play' and b'XDG_RUNTIME_DIR=$tmp\0' in open(f'/proc/{d}/environ','rb').read(): print(d,end=' ')
    except OSError: pass
PY
)]"
  echo "PIDFILE: $([ -e $tmp/ccspk.pid ] && echo あり || echo 無し)"
  wait $MON; echo "--- monitor"; cat $tmp/mon.txt; rm -rf $tmp; done; fi
if want 4; then run 4; mon 12
  feed $A; sleep 1.5; echo "A の pidfile: $(cat $tmp/ccspk.pid|tr '\n' ' ')"; feed $B; sleep .5
  echo "B の pidfile: $(cat $tmp/ccspk.pid|tr '\n' ' ') 行数=$(wc -l < $tmp/ccspk.pid)"
  wait $MON; echo "--- monitor"; cat $tmp/mon.txt; rm -rf $tmp; fi
if want 5; then run 5; touch $tmp/ccspk/queue; export CCSPK_SUMMARY=1; mon 40
  L=$(python -c "print('狐'+'あいうえお'*40)"); L2=$(python -c "print('海'+'かきくけこ'*40)")
  T0=$(date +%s.%N); feed "$L。"; sleep .3; feed "$L2。"; echo "pidfile: $(cat $tmp/ccspk.pid|tr '\n' ' ')"
  wait $MON; echo "--- monitor (A の要約は 4 秒。A の本文は狐を含む)"; cat $tmp/mon.txt; rm -rf $tmp; fi
if want 6; then run 6
  .venv/bin/ccspk queue; echo "rc=$? file=$([ -e $tmp/ccspk/queue ] && echo あり || echo 無し)"
  .venv/bin/ccspk queue on; echo "rc=$? file=$([ -e $tmp/ccspk/queue ] && echo あり || echo 無し)"
  .venv/bin/ccspk queue; .venv/bin/ccspk queue off; echo "rc=$? file=$([ -e $tmp/ccspk/queue ] && echo あり || echo 無し)"
  .venv/bin/ccspk queue foo; echo "foo rc=$?"; rm -rf $tmp; fi
if want 7; then uv run ccspk test 2>&1 | tail -3; echo "rc=${pipestatus[1]}"; fi
