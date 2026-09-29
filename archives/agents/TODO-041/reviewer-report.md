# TODO-041 reviewer の報告

対象: `git diff -- docs/`（言い回しの直し 4 つ、mermaid の図 4 枚、3.1 の図の前に足した 1 文）。
突き合わせたコード: `src/ccspk/hook.py`（`main()` 893-955、`prepare()` 271、`rewrite()` 288、`play_rewritten()` 320、
`chunks()` 429、`play()` 467、`run_child()` 490、`speak()` 504）、`src/ccspk/check.py`（`after_stop()` 54、
`pending()` 77、`check()` 133、`main()` 190）、`src/ccspk/user_dict.py`（`save()` 109、`register()` 119）。

要修正: 0 件。検討: 3 件。好みの範囲: 1 件。

## 検討

### 1. Developer.md:404 `K->>V: save()（辞書を user_dict.json へ書き出す）`

- 何が違うか: 矢印がエンジンへ向いているので、エンジンがファイルを書き出すように読める。実際は、点検のプロセスが
  エンジンから `GET /user_dict` で辞書を読み、自分で `user_dict.json` に書く。UsersGuide.md:16 の構成図は
  `CK -- "辞書を書き出す" --> UD`（点検からファイルへ）なので、2 枚の図で向きが食い違う
- 根拠: `user_dict.py:109-116`（`save()` が `dump()` を呼び、一時ファイルに書いて `replace`）、
  `user_dict.py:100-102`（`dump()` が `call("GET", "/user_dict")`）
- 書き方の例（直すかは管理者の判断）: `K->>V: GET /user_dict` と `Note over K: save() で user_dict.json へ書き出す` に分ける

### 2. Developer.md:406 `mtime を SPOKEN に揃える`

- 何が違うか: 揃える先は「点検の始めに控えた `SPOKEN` の mtime」で、今の `SPOKEN` の mtime ではない。
  図の書き方だと今の mtime に揃えるように読め、同じ節の 5.（「2. で控えた `SPOKEN` の mtime に揃える。
  点検のあいだに足された文があれば…次の Stop で点検し直す」）の要点が落ちる
- 根拠: `check.py:134`（最初に `mtime = SPOKEN.stat().st_mtime`）、`check.py:177`・`check.py:181`（その値で `os.utime`）
- 書き方の例: 「mtime を、始めに控えた SPOKEN の mtime に揃える」

### 3. Developer.md:387-395 単語が無いときの分岐が無い

- 何が違うか: 図では毎回 `/audio_query` の繰り返しと `claude -p` を呼ぶように見えるが、`CHECKED` と登録済みの単語を
  除いて何も残らなければ、エンジンにも `claude -p` にも問い合わせず、`CHECKED` の mtime を揃えるだけで終わる。
  README で裏の `claude -p` のトークン量を書いた（TODO-050）ので、毎回呼ぶと読まれると誤解を招く。
  同じ節の文章（3.）にもこの分岐は書かれていない。実害は未確認
- 根拠: `check.py:139`（`if words:`）、`check.py:180-181`（無ければ `touch` と `utime` だけ）
- 書き方の例: `extract()` の後から `opt` の前までを `opt 残った単語があるとき` で囲む

## 好みの範囲

### 4. UsersGuide.md:13 `Stop のとき、読んだ文があれば`

- `after_stop()` が点検を起こす条件は `pending()`（`SPOKEN` が `CHECKED` より新しい）で、「まだ点検していない読んだ文があれば」。
  一度読めば `SPOKEN` は残り続けるので、今の言い方だと Stop のたびに点検が走るとも読める。利用者向けの概略図なので
  このままでもよい。根拠: `check.py:62`・`check.py:77-86`

## 問題なし

- Developer.md「2. 動き方」合成の箇条書き: 前（「1 文目ができたらすぐ鳴らす」）より今のコードに合う。最初に鳴るのは `chunks()` の 1 つ目の塊（`hook.py:429-433`、`play()` 467-482）。書き換えで意味は変わっていない（前の 2 行目にあった「1 文目の前半」に揃えた）
- 同・切り方の箇条書き: 足した「1 文目を切るのは最初の音を早めるため」は `split_first()` の docstring（`hook.py:409`）と合う。切り方の決まり、抑揚、最初の音までの秒数は分けただけで中身は同じ
- 同・「空の `Stop` では、前の再生を止める」: 意味は前と同じで、`hook.py:944-945`（`if not (queued and text): stop_playing()`）と合う。順番に読むモードでも止めることは同じ節の上（Developer.md:65 付近）にある
- UsersGuide.md「1.2」フックのコマンドの文: 書いたコマンドは同じ節の JSON（UsersGuide.md:80・91・103）と一致。`ccspk` が無ければ `! command -v` が真になり、終了コード 0 で終わる。意味は変わらず、主語がはっきりした
- UsersGuide.md「3.3 ccspk say」: `say()` は `play()` を呼び、`play()` は `pw-play` の繰り返しが終わるまで戻らない（`hook.py:958-961`・`467-482`）。意味は同じ
- 3.1 の図の前に足した 1 文: `main()` の `finally`（`hook.py:952-955`）と合う。`LOCK` を取る前に返る 1.〜4. では呼ばない点も図と合う
- 3.1 の flowchart: 1.〜10. の順、途中で終わる分岐、9. の `QUEUE` の分岐、`after_stop()` の位置はすべてコードと一致。描いていないのは `assemble()` の `OSError`（`hook.py:920-921`、終わるだけ）で、誤解は招かない
- 3.2 の sequenceDiagram: 書き直し → `check.record()` → `wait_for()` → `play()` の順（`hook.py:320-334`、`run_child()` 498-502）、`claude -p` が sonnet であること（`hook.py:297`）、合成と鳴らすの並行（`hook.py:467-482`）は一致。書き直しに失敗したときの戻り（`to_speech(text)`）は図に無いが、直後の文章の 2. にある
- 3.8 の sequenceDiagram のうち上に挙げた以外: `after_stop()` の順（`FAILED` を出してから `pending()`、`check.py:56-75`）、`check.lock` を `LOCK_NB` で取る（`check.py:192-196`）、`GET /user_dict` が `extract()` より前（`check.py:137-138`）、`claude -p` が opus、`parse()` の後にもう一度 `same()` で比べて `register()`・`ADDED` 追記（`check.py:155-167`）は一致
- UsersGuide.md 冒頭の flowchart と前の 1 文: エンジンの宛先 `127.0.0.1:50021`（`hook.py:44`）、systemd の user unit（UsersGuide.md:45-46）、起動のたびに `user_dict.json` を読み込む（UsersGuide.md:54）と合う
- 規約（造語・自然な日本語）: 「塊」は `hook.py:51`・Developer.md 3.2 で既に使っている語。造語は見当たらない。
  「語の中の半角」（Developer.md:54）の「語」は差分の前からある言い回しで、辞書に登録する単語の話ではないので対象外と判断した

## 範囲外で気づいたこと

- `hook.py:468` の `play()` の docstring が「1 文目ができたらすぐ鳴らし」のままで、今回 Developer.md で直した食い違いがコードの側に残っている。TODO-041 は文書だけの項目なので報告だけ

## 作り込みすぎ

作り込みすぎ: なし（文書だけの差分。3.1 の図は番号付きの手順と重なるが、図を入れること自体が TODO-041 の中身）
