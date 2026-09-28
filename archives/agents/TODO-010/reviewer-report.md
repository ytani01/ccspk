# TODO-010 reviewer の報告

対象: 未コミットの `git diff`。`hooks/speak-response.py` はレビュー中に 2 度変わったので、
最後の版（sha1 `a4146d36…`、09:17:07）を見た。文書の 4 ファイルは 09:14 のまま。
プロジェクトの `CLAUDE.md` は無いので、利用者全体の `CLAUDE.md` と既存のコードを基準にした。

実測に使ったスクリプトはここに置いた（鳴らさない。`unusable`・`stop_playing`・`speak` を差し替える）。

- `reviewer-probe.py <スクリプトのパス>`: `main()` の分岐を 1 件ずつ通す
- `reviewer-race.py`（`reviewer-race-worker.py` を使う）: 3 つの分と Stop の 4 プロセスを、
  順番を混ぜて同時に起動する

## 要修正

### 1. docs/Developer.md:43-46「流れ」がコードと合っていない

「MessageDisplay なら `delta`（文章の全文）。`final` が true でないとき…は読まない」とあるが、
今のコード（`assemble()`、hooks/speak-response.py:127-151）では、`delta` は 1 つの分で、
`final` でない分は `PARTS` に置き、そろったらつなぐ。同じ段の手順 1〜7（:57-64）にも、
`LOCK` を取ることと、分をつなぐ手順が無い。
根拠: コードを読んだ。probe で `index` 0（final=false）と 1（final=true）を分けて渡すと
「前半、後半。」とつないで読んだ。

### 2. docs/Developer.md:180 の MessageDisplay の例では何も起きない

`{"hook_event_name":"MessageDisplay","final":true,"delta":"…"}` には `message_id` と `index` が
無く、`assemble()` の :134-135 で None を返すので、読まない。
根拠: probe で `doc example (no id) []`（`stop_playing` も `speak` も呼ばれない）。
:181「続けて同じ文を渡すと、PID は変わらない」も、この例では確かめられない。

### 3. docs/Developer.md:105-115「ファイル」、:179 に `LOCK` と `PARTS` が無い

表は `PIDFILE`・`UNUSABLE`・`LAST` だけ。:179「`claude-tts.pid` と `claude-tts.last` ができる」も、
今は `claude-tts.lock`（Stop でも作る）と、MessageDisplay なら `claude-tts.parts/` もできる。
根拠: probe を走らせた後の一時ディレクトリに `claude-tts.last`・`claude-tts.lock`・
`claude-tts.parts` があった。

## 検討

### 4. 直前と同じ文は、次の返答でも読まない（LAST が消えない）

`LAST` はターンをまたいで残るので、続けて同じ返答（「はい。」など）が来たら 2 つ目は読まない。
途中の文章が同じ文面で繰り返されたときも読まない。このとき `stop_playing()` もしない。
根拠: probe で Stop「確認です。」を読んだ後、もう一度 Stop「確認です。」を渡すと `[]`。
TODO.md の「同じ文章を 2 度読まない」をどこまでと読むかで決まる。**判断が要る**
（MessageDisplay と Stop の重なりだけを除きたいのなら、今の作りは広すぎる）。実害は未確認。

### 5. 整えると空になる途中の文章でも、前の再生を止める

表だけ・URL だけの文章は `to_speech()` で空になり、hooks/speak-response.py:369 で
`stop_playing()` だけして何も読まない。前は Stop だけがこう動いたが、今は途中の文章でも起きる。
根拠: probe で表だけの MessageDisplay が `['stop']`、空の Stop も `['stop']`（前と同じ）。
途中で表だけの文章が来ると、読んでいた返答が黙って切れる。実害は未確認。

### 6. final が来ない分、来ない分がある文章のファイルが PARTS に残る

コメント（:131）のとおり final が来ないと残る。加えて、final は来たが途中の分が 1 つ来ない
ときも、`{mid}.0` などと `{mid}.final` が残り、その文章は読まれない。TODO.md の実測では
MessageDisplay が起動しない文章が 7 つ中 5 つあったので、分単位でも起動しないことがあるなら
起きうる。分単位で抜けるかは未確認。1 件あたり数十〜数百バイトで、`$XDG_RUNTIME_DIR` なら
ログアウトで消える。`$XDG_RUNTIME_DIR` が無い環境の `/tmp` では再起動まで残る。
終わった文章の後に同じ `message_id` の分が遅れて来たときも、その分が残る（コードを読んだだけ、未確認）。

### 7. MessageDisplay と Stop で、整えた後の文が一致するかは未確認

2 度読まないのは、つないだ `delta` と `last_assistant_message` を `to_speech()` した結果が
一致するときだけ。分のつなぎ目に空白や改行が入る・入らないで食い違うと、2 度読む
（`to_speech()` は空白の並びを 1 つにするが、有る無しは揃えない）。実物の入力で比べていない。

### 8. `assemble()` と、LAST の読み書きの分岐にテストが無い

`demo()`（`--test`）は整形と分割だけ。docs/Developer.md:157 は「`main()` の分岐は環境に依るので
demo() では確かめていない」とするが、`assemble()` の「順番が入れ替わってもつなぐ」
「そろうまで None」は環境に依らず、一時ディレクトリで確かめられる。確かめる手段が手作業だけになる。

### 9. TODO.md の実測の記述がコードの前提と食い違う

TODO.md の実測は「`delta` に全文、`index`（0）、`final`（true）」。コード（:49-51 のコメントと
`assemble()`）は「index ごとに分けて渡し、後ろの分が先に届く」を前提にしている。後者を測ったなら、
TODO.md に書き足すとよい（archives に移すと、`assemble()` の根拠が残らない）。

### 10. README.md:3・:9 が「Stop フック」のまま

「動き方」（:18）は `Stop` と `MessageDisplay` に直したが、冒頭の 1 行とファイルの表は
「Stop フック」のまま。同じ README の中で言い方が揃っていない。

## 好みの範囲

なし（作り込みすぎの 1 件は下に書いた）。

## 一致したもの

- MessageDisplay で `agent_id` があれば読まない（:346）。probe で `[]`
- 分が 1 つで final のとき、順番どおり、逆順のとき、どれも 1 回だけ読む。probe で確かめた
- `index` が int でない、`message_id` が無いときは読まない。probe で確かめた
- Stop（`hook_event_name` が無い入力も）は前と同じく `last_assistant_message` を読む
- LAST と同じなら、`stop_playing()` の前に終わる（:365-367）。probe の結果も同じ
- 空の Stop は前と同じく `stop_playing()` だけする
- LAST の読み書きの OSError: 読めない（無い・ディレクトリになっている）なら読む、
  書けない（ディレクトリが読み取り専用）でも読む。probe で確かめた
- LOCK の範囲: `assemble()`・LAST の読み書き・`stop_playing()`・`speak()` をまとめて囲む。
  途中の `return`・例外でも `finally` で閉じる。プロセスが終われば flock も外れる
- そろう判定: LOCK の中で、自分の分を書いてから final を読むので、最後に着いたプロセスが必ずつなぐ。
  race で 4 プロセスを同時に起動し、3 回とも 1 回だけ読み、PARTS も空になった。
  ただし LOCK を外しても 3 回とも同じ結果で、この試験では LOCK が要ることは示せていない
- 競合（依頼の 2）: MessageDisplay と Stop が同時に来ても LOCK で 1 つずつ通るので、
  両方が LAST を読んでから書く食い違いは起きない（コードを読んだ。上の race も 1 回だけ）
- docs/UsersGuide.md の JSON: Stop と MessageDisplay で同じ形・同じコマンド。括弧の対応も正しい
- docs/Developer.md の「動き方」（:27-34）の箇条書きはコードと合う
- `python3 hooks/speak-response.py --test` は `ok`

## 作り込みすぎ

- hooks/speak-response.py:348-352, 375-377: shrink（好みの範囲）: LOCK を開けないときに
  ロック無しで続ける分岐。開けないディレクトリでは `PARTS`・`PIDFILE` も書けず（`speak()` の
  `PIDFILE.write_text` は例外を拾わない）、続けても役に立たない。
  `with open(LOCK, "w") as lock:` と `fcntl.flock` にして、OSError なら終わる形にすれば
  `lock = None` と `finally` が要らない。

net: -4 lines possible.
