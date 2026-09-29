# TODO-036 確認の報告 3（verifier）

`PYTHONDONTWRITEBYTECODE=1` を付けた。コードは直していない。スクリプト: `verify.sh`・`verify2.sh`（再実行）、`verify4.sh`（項目 3、新規）。
`judge.py` は依頼どおり `uv run python archives/agents/TODO-036/judge.py opus context`。

## 1. `uv run ccspk test`
`ok` が 3 行、終了コード 0。

## 2. `verify.sh`・`verify2.sh` の流し直し
前回一致した項目（通し・新しい文なし・失敗・やり直し・`CCSPK_SPEAK=0`・登録の失敗・`dict auto`・`dict remove`・`--remove`）は変わらない。
違いは、偽 `claude` の引数が `--model opus` になり、標準入力が 3 列になったこと（意図した変更）。`verify2.sh` の `dict export` の前後の差は無し。

## 3. 偽 claude の通し（`verify4.sh`）
文: 全角「あ」45 字 + `Zqxlongword` + 「い」45 字。先頭も含む。
- 引数: `-p --model opus --setting-sources "" --tools "" --no-session-persistence PROMPT`。`--model opus` あり。一致
- 標準入力は 3 列（表記・エンジンの kana・前後の文）。`Zqxlongword` の 3 列目は 71 字（30 + 11 + 30）で単語を含む。
  `先頭` の 3 列目は 36 字（行末までなので短い）で単語を含む。一致
- 偽 `claude` が `Zqxlongword<TAB>ズクスロンゴウォド<TAB>なんでもよい文` と 3 列で返した → `added.tsv` に
  `Zqxlongword  ズクスロンゴウォド  ズ'クスロングワアド` が入った。一致
- `dict export` の前後の差は無し。`Zqxlongword` は消した
- 手違い 1 点: 最初の 2 回は「登録されない」に見えた。1 回目は偽 `claude` の読みがエンジンの読みと同じ発音で `same()` が正しく落とし、
  2 回目は `Zqxlongword` が前の実行で `checked.txt` に入っていたため。どちらもコードの不具合ではない。
  3 回目は `checked.txt` から手で該当の行を消して通した。`verify4.sh` のその行を消す 1 行は効いておらず、
  スクリプトだけでは 2 回目以降の実行で登録が起きない（再実行するなら `checked.txt` から `Zqxlongword` を消す）

## 4. 本物の claude（`judge.py opus context`、登録なし）
`opus context: 見つけた 6/6（採番 TODO CLAUDE README JSON 文目）、誤判定 0（）、$0.009、4.4 秒`。
返答は 6 行とも 2 列（`採番 サイバン` など）。見つけた数・誤判定・料金は判定スクリプトの出力のまま。

## 5. 文書との突き合わせ
- README「1. 特徴」の 1 項目め（拾う・判定・登録・裏で動く・`dict auto`）: 一致
- README 4 項目め（外へ出すのは単語・読みと前後 30 字）: 3 の標準入力が、表記・読み・前後 30 字（71 字）の 3 列で一致
- UsersGuide 2.3: 「Claude（Opus）」「`--model opus`」「表記・読み・前後 30 字の一覧」「返された読みもエンジンに通し同じ発音なら登録しない」
  は 3 と一致。「エンジンの読みと同じ発音なら登録しない」は 3 の 1 回目の手違いで実際に見えた。
  料金の数字（$0.01〜0.04・5〜7 秒）は、今回の Opus の測定（$0.009・4.4 秒）と桁が合う（範囲の下限より少し安い）
- 依頼にあった 3.8 は読んでいない（依頼の確認項目に入っていなかったため）。判断できない

## 辞書の前後
本物のエンジンの `dict export` を、この確認の開始前と終了後で取って `diff` した: 差は無し。
`verify.sh` の前後（`Zqx*` のみ）も差は無し。
