#!/usr/bin/env bash
# TODO-036 verifier 項目 2: check.py を 1 か所ずつ壊して uv run ccspk test が落ちるか見る。終わったら元に戻す
cd /home/ytani/work/ccspk
F=src/ccspk/check.py
O=/tmp/claude-649/check.py.orig
mkdir -p /tmp/claude-649
[ -f $O ] || command cp $F $O
try() { # 名前 sed式
  command cp $O $F; sleep 1.1; sed -i "$2" $F  # uv が mtime で再ビルドを判断するかもしれないので 1 秒空ける
  if cmp -s $F $O; then echo "$1: sed が効いていない"; return; fi
  out=$(uv run ccspk test 2>&1); rc=$?
  echo "$1: exit=$rc  $(echo "$out" | rg -e AssertionError -e Error | head -1)"
}
try "pending >= にする" 's/return spoken > CHECKED/return spoken >= CHECKED/'
try "pending < にする" 's/return spoken > CHECKED/return spoken < CHECKED/'
try "parse カタカナ範囲の始点 ァ→ア" 's/\[ァ-ヴー\]+/[ア-ヴー]+/'
try "parse ー を外す" 's/\[ァ-ヴー\]+/[ァ-ヴ]+/'
try "extract 名詞→動詞" 's/== "名詞" and/== "動詞" and/'
try "extract len >= 2 → >= 1" 's/len(s) >= 2/len(s) >= 1/'
try "extract 漢字条件を外す" 's/ and re.search(KANJI, s)//'
try "record 残す割合 // 2 → // 3" 's|len(lines) // 2|len(lines) // 3|'
try "record 閾値 > → >=" 's/st_size > SPOKEN_MAX/st_size >= SPOKEN_MAX/'
try "record SPOKEN_MAX 64→32 KiB" 's/^SPOKEN_MAX = 64 \* 1024/SPOKEN_MAX = 32 * 1024/'
command cp $O $F
cmp $F $O && echo restored
