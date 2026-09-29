#!/usr/bin/env bash
# TODO-036 verifier 3 項目 3: --model opus、標準入力の 3 列、3 列で返されても登録される。verify.sh のあとに走らせる
set -u
cd /home/ytani/work/ccspk
S=${S:-/tmp/claude-649/-home-ytani-work-ccspk/772ff60c-0e7a-4dd5-990d-650701c56a8b/scratchpad/v36}
export XDG_STATE_HOME=$S/state XDG_CONFIG_HOME=$S/config XDG_RUNTIME_DIR=$S/run FAKE=$S/fake PIPEWIRE_REMOTE=fake PATH=$S/bin:$PATH
CC=.venv/bin/ccspk; ST=$S/state/ccspk
wait_check() { sleep 0.5; for i in $(seq 60); do flock -n $ST/check.lock true 2>/dev/null && { sleep 0.3; return; }; sleep 0.5; done; echo "TIMEOUT"; }
rm -f $FAKE/fail $ST/failed.txt; : > $ST/added.tsv; sed -i "/^Zqxlongword$/d" $ST/checked.txt; : > $FAKE/calls.log
$CC dict export $S/before4.json >/dev/null 2>&1
printf 'Zqxlongword\tズクスロンゴウォド\tなんでもよい文\n先頭\tセントー\tx\n' > $FAKE/reply
A=$(printf 'あ%.0s' $(seq 45)); B=$(printf 'い%.0s' $(seq 45))
sleep 6
printf '{"hook_event_name":"Stop","last_assistant_message":"%s Zqxlongword %s。先頭も見る。"}' "$A" "$B" | CCSPK_SPEAK=1 $CC hook; wait_check
echo "-- calls.log"; rg -n -A3 -e '^\[--model' $FAKE/calls.log | head -5; sed -n '/^STDIN/,/^---/p' $FAKE/calls.log
echo "-- 3列目の長さ(字)と単語を含むか"
sed -n '/^STDIN/,/^---/p' $FAKE/calls.log | rg '\t' | python3 -c "
import sys
for l in sys.stdin:
    c=l.rstrip('\n').split('\t'); print(len(c), len(c[2]), c[0] in c[2])"
echo "-- added.tsv"; cat $ST/added.tsv; echo "-- failed.txt"; cat $ST/failed.txt 2>&1
$CC dict remove Zqxlongword 2>&1 | tail -1
$CC dict export $S/after4.json >/dev/null 2>&1; diff $S/before4.json $S/after4.json && echo "dict diff: none"
