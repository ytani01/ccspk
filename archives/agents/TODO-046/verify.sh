#!/bin/zsh
# TODO-046 verifier 手順 3。使い方: cd リポジトリ && zsh archives/agents/TODO-046/verify.sh
R=$PWD; T=$(mktemp -d)
export XDG_RUNTIME_DIR=$T/run XDG_CONFIG_HOME=$T/cfg XDG_STATE_HOME=$T/st PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u) CCSPK_SPEAK=1 CCSPK_SUMMARY=0
mkdir -p $XDG_RUNTIME_DIR $XDG_CONFIG_HOME/ccspk $XDG_STATE_HOME/ccspk; chmod 700 $XDG_RUNTIME_DIR
SP=$XDG_STATE_HOME/ccspk/spoken.txt
run() { # $1=label $2=body
  \rm -f $SP
  python3 -c 'import json,sys;print(json.dumps({"hook_event_name":"MessageDisplay","message_id":sys.argv[2],"index":0,"final":True,"delta":sys.argv[1]}))' "$2" "$3" | $R/.venv/bin/ccspk hook
  echo "hook exit=$?"
  s=$(date +%s.%N)
  for i in {1..300}; do [ -s $SP ] && break; sleep 0.1; done
  echo "[$1] 記録まで $(printf %.1f $(( $(date +%s.%N) - s ))) 秒"; echo "--- spoken.txt"; cat $SP; echo
  # 子プロセス終了待ち
  for i in {1..300}; do p=$(cat $XDG_RUNTIME_DIR/ccspk.pid 2>/dev/null); [ -z "$p" ] && break; for q in ${=p}; do [ -d /proc/$q ] && continue 2; done; break; done
  sleep 6
}
EN=$'Today I fixed the bug in `hook.py` (TODO-046). Here is the patch:\n\n```python\nprint("hello")\nx = 1\n```\n\nPlease run the tests and tell me if they pass.'
JA='設定ファイルを修正しました。テストも通っています。'
touch $XDG_CONFIG_HOME/ccspk/translate
run "翻訳on 英文" "$EN" m1
run "翻訳on 日本語" "$JA" m2
\rm $XDG_CONFIG_HOME/ccspk/translate
run "翻訳off 英文" "$EN" m3
touch $XDG_CONFIG_HOME/ccspk/translate
mkdir -p $T/bin; printf '#!/bin/sh\nexit 1\n' > $T/bin/claude; chmod +x $T/bin/claude
PATH=$T/bin:$PATH run "翻訳on 偽claude失敗 英文" "$EN" m4
