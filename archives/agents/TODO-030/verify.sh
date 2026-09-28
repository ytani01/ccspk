#!/bin/sh
# TODO-030 確認: 項目 2, 3, 4 をまとめて実測する
cd /home/ytani/work/ccspk
echo "== 2: UsersGuide の例"
.venv/bin/python - <<'PY'
from ccspk.hook import chunks, to_speech
for s in ["同じ reviewer に見てもらう。", "Claude Code を使う。", "手順 1 に進む。", "全部で 180 字です。"]:
    print(repr(s), "->", chunks(to_speech(s)))
PY
echo "== 3: 同じ reviewer に見てもらう。"
.venv/bin/ccspk dict kana '同じ reviewer に見てもらう。'
.venv/bin/python -c "
from ccspk.hook import chunks
print(chunks('同じ reviewer に見てもらう。'))"
.venv/bin/ccspk dict kana '同じreviewerに見てもらう。'
echo "== 4: kana.md の詰めた後"
.venv/bin/python - <<'PY'
import subprocess
from ccspk.hook import squeeze
rows = {
 "reviewer の指摘を受けて": "レビュウタ'ントウノ/_シテキオ'/ウケ'テ",
 "同じ reviewer に見てもらう。": "オナジ'/レビュウタ'ントウニ/ミ'テ/モラウ'",
 "Claude Code の 3 files を見る。": "クロ'オド/コ'オドノ、サン'、ファ'イルズオ/ミ'ル",
 "hook.py を直した。": "フ'ックドットパイオ/ナオシ'タ",
 "ccspk test が落ちた": "シイシイエ_スピイケイ'/テ'_ストガ/オチ'タ",
 "uv tool install で入れる": "ユ'ウ/ブ'イ/トゥ'ウル/イ'ンストオルデ/イレル'",
}
for src, want in rows.items():
    sq = squeeze(src)
    got = subprocess.run([".venv/bin/ccspk","dict","kana",sq],capture_output=True,text=True).stdout.strip()
    print("OK " if got==want else "NG ", repr(sq), "|", got, "|", want)
PY
