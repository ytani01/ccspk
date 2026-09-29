#!/usr/bin/env bash
# TODO-036 verifier 2 項目 3: 長音だけ違う読みは登録せず、発音の違う読みだけ登録する。verify.sh のあとに走らせる
set -u
cd /home/ytani/work/ccspk
S=${S:-/tmp/claude-649/-home-ytani-work-ccspk/772ff60c-0e7a-4dd5-990d-650701c56a8b/scratchpad/v36}
export XDG_STATE_HOME=$S/state XDG_CONFIG_HOME=$S/config XDG_RUNTIME_DIR=$S/run FAKE=$S/fake PIPEWIRE_REMOTE=fake PATH=$S/bin:$PATH
CC=.venv/bin/ccspk; ST=$S/state/ccspk
wait_check() { sleep 0.5; for i in $(seq 60); do flock -n $ST/check.lock true 2>/dev/null && { sleep 0.3; return; }; sleep 0.5; done; echo "TIMEOUT"; }
rm -f $FAKE/fail; : > $ST/added.tsv; rm -f $ST/failed.txt
$CC dict export $S/before3.json >/dev/null 2>&1
for w in 先頭 計算; do echo "engine kana $w: $($CC dict kana $w | tail -1)  / registered? $(rg -c "\"surface\": \"$w\"" $S/before3.json)"; done
printf '先頭\tセントー\n計算\tケイサン\nZqxnewword\tズクスニュウワード\n' > $FAKE/reply
sleep 6
printf '{"hook_event_name":"Stop","last_assistant_message":"先頭と計算を見る。Zqxnewword を足す。"}' | CCSPK_SPEAK=1 $CC hook; wait_check
echo "-- stdin to fake claude (last)"; tail -8 $FAKE/calls.log
echo "-- added.tsv"; cat $ST/added.tsv
echo "-- checked.txt"; cat $ST/checked.txt
echo "-- failed.txt"; cat $ST/failed.txt 2>&1
$CC dict remove Zqxnewword 2>&1 | tail -1
$CC dict export $S/after3.json >/dev/null 2>&1; diff $S/before3.json $S/after3.json && echo "dict diff: none"
