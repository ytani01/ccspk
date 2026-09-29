#!/usr/bin/env bash
# TODO-036 verifier: 項目 3-8（通し・失敗・dict auto・CCSPK_SPEAK=0）。項目 1・2・9 は別に手で実行
set -u
cd /home/ytani/work/ccspk
S=${S:-/tmp/claude-649/-home-ytani-work-ccspk/772ff60c-0e7a-4dd5-990d-650701c56a8b/scratchpad/v36}
rm -rf "$S"; mkdir -p "$S"/{state,config,run,bin,fake}
export XDG_STATE_HOME=$S/state XDG_CONFIG_HOME=$S/config XDG_RUNTIME_DIR=$S/run FAKE=$S/fake
cat > $S/bin/claude <<'EOS'
#!/usr/bin/env bash
{ echo "ARGS:"; printf '[%s]\n' "$@"; echo "SPEAK=${CCSPK_SPEAK-unset}"; echo "STDIN:"; cat; echo ---; } >> $FAKE/calls.log
echo x >> $FAKE/count
[ -f $FAKE/fail ] && { echo "fake failure" >&2; exit 1; }
cat $FAKE/reply
EOS
printf '#!/bin/sh\ncat >/dev/null\n' > $S/bin/pw-play
chmod +x $S/bin/*
export PATH=$S/bin:$PATH PIPEWIRE_REMOTE=fake  # 偽の pw-play しか使わないので、PipeWire の接続確認を飛ばす
CC=.venv/bin/ccspk
ST=$S/state/ccspk
n() { wc -l < $FAKE/count 2>/dev/null || echo 0; }
wait_check() { sleep 0.5; for i in $(seq 60); do flock -n $ST/check.lock true 2>/dev/null && { sleep 0.3; return; }; sleep 0.5; done; echo "TIMEOUT waiting check"; }
stop() { printf '{"hook_event_name":"Stop","last_assistant_message":"%s"}' "$1" | CCSPK_SPEAK=${SPK:-1} $CC hook; echo "[hook exit=$?]"; }
show() { for f in spoken.txt checked.txt added.tsv failed.txt; do echo "-- $f"; cat $ST/$f 2>&1; done; }
$CC dict export $S/before.json >/dev/null 2>&1
echo "== engine dict before: $(wc -c < $S/before.json) bytes"

echo "== 3 通し"
printf 'Zqxverifyword\tズクスベリファイワード\n' > $FAKE/reply
stop "Zqxverifyword を見る。"
wait_check; show
echo "-- calls.log"; cat $FAKE/calls.log
echo "-- kana"; $CC dict kana Zqxverifyword
echo "-- ps"; pgrep -f "python.* -m ccspk.check" || echo none
echo "-- checked mtime vs spoken"; stat -c '%Y %n' $ST/spoken.txt $ST/checked.txt
C3=$(n)

echo "== 4 新しい文なし"
stop "Zqxverifyword を見る。"   # LAST 5秒以内か? 同じ文
sleep 6
stop "Zqxverifyword を見る。"
wait_check
echo "claude calls: before=$C3 after=$(n)"; echo "-- spoken lines"; wc -l < $ST/spoken.txt

echo "== 5 失敗"
touch $FAKE/fail
M0=$(stat -c %Y.%N $ST/checked.txt)
sleep 1
stop "Zqxfailword を見る。"
wait_check
echo "-- failed.txt"; cat $ST/failed.txt
echo "checked mtime before=$M0 after=$(stat -c %Y.%N $ST/checked.txt)"
rm $FAKE/fail
sleep 6
echo "-- next stop stdout"
stop "全然別の文を読む。" | tee $S/next.out
[ -e $ST/failed.txt ] && echo "failed.txt STILL EXISTS" || echo "failed.txt removed"
wait_check
echo "== 5b 次の点検（やり直し）"; show

echo "== 8 CCSPK_SPEAK=0"
echo "手で残した" > $ST/failed.txt
SPK=0 stop "Zqxspkzero を見る。"
sleep 1
[ -e $ST/failed.txt ] && echo "failed.txt kept (ok)" || echo "failed.txt REMOVED"
wc -l < $ST/spoken.txt
rm -f $ST/failed.txt
