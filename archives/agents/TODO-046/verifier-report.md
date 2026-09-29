# verifier 報告（TODO-046）

## 検証
- `uv run ccspk test`: 終了コード 0（末尾 ok）
- 変更ファイル: CLAUDE.md README.md TODO.md docs/Developer.md docs/UsersGuide.md src/ccspk/cli.py src/ccspk/hook.py と archives/agents/TODO-046/（指示範囲内と見た。CLAUDE.md の変更は指示の有無を判断できない）
- 計測スクリプト: `verify.py`（手順 2）、`verify.sh`（手順 3）。出力は `verify-out.txt`・`verify-sh-out.txt`。verify.py は `SUMMARY_TIMEOUT` を 90 秒に延ばして走らせた（既定 30）

## 手順 2（本物の claude -p、各 2 回。本文は verify.py 内。翻訳の本文は prepare() の 3 つ目の値）
注: 長い英文は要約が入っていると要約に回る（仕様どおり）ので、翻訳の測定では CCSPK_SUMMARY=0 で prepare() した。

出力全文:

```
=== TRANSLATE 本文 (子プロセスに渡す) ===
Today I made the fix. It was a painful bug, and the config took a hard look to track down.
Yesterday I went to the other machine and conducted the same check there. The way you set the timeout was the cause,
and the person who wrote it confirmed the setting. Please decide the scope of the change and the way to proceed.

Here is the patch for `src/ccspk/hook.py` (TODO-046):
```
```

| file | result |
|------|--------|
| hook.py | fixed |
| cli.py | unchanged |

After that, run `uv run ccspk test` and confirm that `load_config` works wi
=== end ===

### SUMMARY run 1
設定ファイルの修正はすでに済んでいて、確認だけが残っています。テストは12件中10件が通り、残る2件は環境の設定が原因のようです。あなたに決めていただくのは、修正の範囲と、確認を今日(きょう)行うか明日行うかです。どちらで進めるか教えてください。

### SUMMARY run 2
設定ファイルを修正し、テストを実行したところ、12件中10件が通りました。残りの2件は、環境の設定が原因のようです。修正はすでに済んでいて、確認だけが残っています。あなたに決めていただくのは、修正の範囲と、確認をきょう行うかあした行うかです。どちらで進めるか教えてください。

### TRANSLATE run 1
きょうは修正を行いました。辛いバグで、config を突き止めるのに苦労しました。 きのう、別のマシンに行って、そこでも同じ確認を行いました。原因は timeout の設定方法で、それを書いた方も設定を確認してくれました。変更の範囲と進め方を決めてください。 src/ccspk/hook.py のパッチです（TODOゼロヨンロク）。 コード省略。 そのあと、uv run ccspk test を実行して、load config が正しく動くことを確認してください。

### TRANSLATE run 2
今日（きょう）は修正を行いました（おこないました）。辛い（つらい）バグで、原因を突き止めるには config をじっくり調べる必要がありました。 昨日は別のマシンに行って（いって）、そこでも同じ確認を行いました（おこないました）。原因は timeout の設定の仕方で、書いた方（かた）が設定を確認してくれました。変更の範囲と進め方を決めてください。 こちらが src/ccspk/hook.py のパッチです（TODOゼロヨンロク）。
```

### 判定（いずれも実害は未確認、境界線上は報告のみ）
- 出力はすべて日本語
- 要約 1: 今日→「今日(きょう)」（漢字のまま残り、括弧で読みを添えた形）。辛い・行った・方は要約に残らず判定できない
- 要約 2: 今日→「きょう」、明日→「あした」（読みは 1 つに決まらない語ではないが、ひらがな化。境界線上）。ほか漢字のまま: なし該当
- 翻訳 1: 今日→きょう、昨日→きのう（ひらがな化）、辛い→漢字のまま、行って→漢字のまま、行いました→漢字のまま、方（書いた方）→漢字のまま。「TODOゼロヨンロク」は to_speech() の変換
- 翻訳 2: 今日（きょう）・辛い（つらい）・行って（いって）・行いました（おこないました）・方（かた）と、漢字のあとに括弧で読みを付けた形。読み上げでは漢字と読みの二重になる可能性がある（音は未確認）
- 読みが 1 つに決まる漢字（修正・確認・設定・変更・範囲・進め方）はいずれの出力でもひらがなにされていない。ひらがなにされた単語: 昨日→きのう、明日→あした、今日（境界線上）
- コード: 翻訳 1 は「コード省略」、翻訳 2 は出力がコードの手前で終わり（末尾の文が無い。「コード省略」が無い）。表: どちらも飛ばされている
- 識別子: config・timeout・src/ccspk/hook.py・uv run ccspk test は残った。load_config は翻訳 1 で「load config」に変わった
- 翻訳 2 は末尾（After that … 以降）が訳されていない（渡した本文が TRANSLATE_MAX で `wi` で切れているので、その分は仕様の範囲。コード省略が無い理由は判断できない）

## 手順 3（verify.sh の出力は verify-sh-out.txt）
- 翻訳 on・英文（コードブロックと TODO-046 入り）: 記録まで 4.4 秒、日本語の訳が記録された
  `きょうは hook.py のバグを修正しました（TODOゼロヨンロク）。パッチは次の通りです。 コード省略。 テストを実行して、通るかどうかを教えてください。`
- 翻訳 on・日本語: 0.0 秒でそのまま記録（claude -p は呼ばれていない）
- 翻訳 off・英文: 英文のまま記録
- 翻訳 on・偽 claude（exit 1）・英文: 0.1 秒で英文を整えたものが記録、エラー表示なし

## 確かめなかったこと
- 音の良し悪し、括弧つきの読みが実際にどう読まれるか
- 「ひらがなにすべきか」の境界の判断
