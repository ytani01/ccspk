#!/bin/zsh
# TODO-027 確認。エンジンは止めない。本物の設定・実行ディレクトリは触らない。
S=/tmp/claude-649/-home-ytani-work-ccspk/b57b11af-812f-4265-af7b-e787609cbfa6/scratchpad/verify
mkdir -p $S/cfg $S/run; chmod 700 $S/run
export XDG_CONFIG_HOME=$S/cfg XDG_RUNTIME_DIR=$S/run
C=/home/ytani/work/ccspk/.venv/bin/ccspk
r() { echo "\$ ccspk $*"; $C "$@"; echo "rc=$?"; echo; }

r dict export $S/backup.json
echo "--- list before"; $C dict list | rg -c . ; $C dict list | rg 'Ponytail' || echo "Ponytail 未登録"
r dict kana 'Ponytail を使う'
r dict add Ponytail ポニーテール
r dict list
r dict add
r dict add 'Bad' 'ボ！'
$C dict list | rg 'Bad' || echo "Bad 未登録"
r dict export $S/nodir/x.json
r dict import $S/none.json
echo '[1]' > $S/a.json; echo '{"x":1}' > $S/b.json
r dict import $S/a.json
r dict import $S/b.json
r dict import $S/backup.json
r dict remove Ponytail
r dict remove Ponytail
r dict remove NoSuchWord123

echo "--- status"
r status
echo 'テスト理由' > $S/run/ccspk.unusable
r status
r status --clear
r status
r stop
r test
echo "--- hook"
echo '{}' | $C hook; echo "rc=$? (no CCSPK_SPEAK)"
echo 'テスト理由' > $S/run/ccspk.unusable
echo '{"hook_event_name":"Stop","last_assistant_message":"テストです。"}' | CCSPK_SPEAK=1 $C hook; echo "rc=$? (unusable)"
rm -f $S/run/ccspk.unusable
r say 'テスト。'
echo "--- options"
r -V; r -h; r dict add -h; r hook -h

echo "--- final diff"
$C dict export $S/after.json; echo "rc=$?"
python3 -m json.tool --sort-keys $S/backup.json > $S/b.norm
python3 -m json.tool --sort-keys $S/after.json > $S/a.norm
diff $S/b.norm $S/a.norm && echo "DICT SAME"
