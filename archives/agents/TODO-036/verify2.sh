#!/usr/bin/env bash
# TODO-036 verifier: 項目 6・7 と後始末。verify.sh のあとに、同じ一時ディレクトリで走らせる
set -u
cd /home/ytani/work/ccspk
S=${S:-/tmp/claude-649/-home-ytani-work-ccspk/772ff60c-0e7a-4dd5-990d-650701c56a8b/scratchpad/v36}
export XDG_STATE_HOME=$S/state XDG_CONFIG_HOME=$S/config XDG_RUNTIME_DIR=$S/run FAKE=$S/fake PIPEWIRE_REMOTE=fake PATH=$S/bin:$PATH
CC=.venv/bin/ccspk; ST=$S/state/ccspk
wait_check() { sleep 0.5; for i in $(seq 60); do flock -n $ST/check.lock true 2>/dev/null && { sleep 0.3; return; }; sleep 0.5; done; echo "TIMEOUT"; }
stop() { printf '{"hook_event_name":"Stop","last_assistant_message":"%s"}' "$1" | CCSPK_SPEAK=1 $CC hook; }
echo "== 6 登録の失敗（読み ー はエンジンが断る）"
printf 'Zqxbadword\tー\n' > $FAKE/reply
M0=$(stat -c %Y $ST/checked.txt); sleep 1.2
stop "Zqxbadword を見る。"; wait_check
echo "-- failed.txt"; cat $ST/failed.txt
echo "-- checked.txt"; cat $ST/checked.txt
echo "checked mtime before=$M0 after=$(stat -c %Y $ST/checked.txt) spoken=$(stat -c %Y $ST/spoken.txt)"
echo "-- added.tsv"; cat $ST/added.tsv
sleep 6; echo "-- next stop stdout"; stop "別の文。"; wait_check
echo "claude calls total: $(wc -l < $FAKE/count)"
echo "== 7 dict auto"
printf 'Zqxsecond\tズクスセカンド\n' > $FAKE/reply
sleep 6; stop "Zqxsecond を見る。"; wait_check
echo "-- dict auto"; $CC dict auto
echo "-- dict remove Zqxverifyword"; $CC dict remove Zqxverifyword
echo "-- added.tsv"; cat $ST/added.tsv
echo "-- dict auto --remove"; $CC dict auto --remove
echo "-- added.tsv (empty?)"; wc -c < $ST/added.tsv
echo "-- dict auto"; $CC dict auto
echo "-- checked.txt"; cat $ST/checked.txt
echo "== cleanup"
for w in Zqxverifyword Zqxsecond Zqxbadword Zqxfailword Zqxprobe Zqxspkzero; do $CC dict remove $w 2>&1 | tail -1; done
$CC dict export $S/after.json >/dev/null 2>&1
diff $S/before.json $S/after.json && echo "dict export diff: none"
