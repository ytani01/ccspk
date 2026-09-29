# TODO-036 レビューの報告（reviewer）

対象: `git diff`（README.md・TODO.md・docs・src・pyproject.toml・uv.lock）と `src/ccspk/check.py`（新規）。
実測は、状態のディレクトリを scratchpad の一時ディレクトリに向けて行った。エンジンの辞書は書き換えていない
（`/audio_query` の読み出しだけ）。本物の `claude -p` は呼んでいない。

## 要修正（1 件）

### 1. `check.py:64` — `checked.txt` も `spoken.txt` も無いと点検を起こし、毎回「失敗した」と出る

- 何が問題か: `CHECKED.exists() and SPOKEN.stat()...` なので、`CHECKED` が無いときは `SPOKEN` の有無を
  見ずに Popen する。brief の条件は「`checked.txt` が無ければ `spoken.txt` があれば」で、これと違う
- 起きる条件: 状態のディレクトリはあるが、2 つとも無いとき（利用者が `*.txt` を消して点検をやり直させた、など）。
  起こされた点検は `SPOKEN.stat()` で落ち、`failed.txt` に `FileNotFoundError` を書く。次の Stop でそれを
  `systemMessage` で出し、また起こして同じ失敗を書く。読み上げた Stop では `record()` が先に `spoken.txt` を
  作るので止まるが、`LAST` で 2 度読まない Stop や空の返答の Stop では続く
- 根拠（実測）: 空の `$XDG_STATE_HOME/ccspk/` で `check.after_stop()` を 2 回呼ぶと、1 回目で
  `failed.txt` に `FileNotFoundError: [Errno 2] No such file or directory: '.../spoken.txt'`、2 回目で
  `{"systemMessage": "ccspk の読みの点検が失敗した: FileNotFoundError: ..."}` が出た
- 重さ: 直すべき（頻度は低い。条件の順を入れ替えれば brief どおりになる）

## 検討（7 件）

### 2. `check.py:94-100` — エンジンの読みと同じ読みの登録を防いでいない

- 実装の報告の 5 のとおり。返答の読みが `table[surface]` と同じでも `register()` する
- 起きる条件: Sonnet が「誤り」として、エンジンと同じ読みを返したとき。辞書に `PROPER_NOUN`・優先度 7 で
  入り、`accent_of` でアクセントも変わりうる。以降のすべての読み上げに効く（実害は未確認）
- 比べるときの注意（実測）: `/audio_query` の `kana` は `'`・`_` のほかに、アクセント句の区切りの `/` と `、` を含む
  （`fugashi+unidic-lite` → `フ'ガシ/タ'ス/ユ'ニディック、ラ'イト`、`リンク先` → `リン_クサキ'`）。
  また長音が `イ` で返る（`README.md` → `リ'イドミイドット…`）ので、記号を除いて完全一致で比べても
  `ー` との違いは拾えない
- 重さ: 任意（brief に無い。入れるかは main の判断）

### 3. `check.py:131-137` — 登録の途中で失敗すると、`claude -p` を Stop のたびに呼び直す

- 何が問題か: `claude -p` が成功した後で `register()` が `sys.exit` すると、`CHECKED` を更新しないので、
  次の Stop で同じ一覧を `claude -p` に渡し直す（料金がかかる）。失敗が続く限り、返答のたびに
  料金と `systemMessage` が繰り返される。登録できた単語は次から「登録済み」で除かれるが、断られた単語は残る
- 起きる条件: エンジンが読みを断るとき。`parse()` は `[ァ-ヴー]+` を通すが、エンジン（0.25.2）が
  捨て仮名の連続（`ァィ`・`ッッ` など）を 422 で断るかは**未確認**（エンジンの辞書を書き換えるので試していない）。
  エンジンが一時的に落ちたときは、フックの `unusable()` が先に止めるはずなので当たらない（未確認）
- 実装の報告の 4（`claude` が無い・認証切れで毎回失敗）も同じ根で、そちらは料金はかからない
- 重さ: 任意（brief は「どこで失敗しても `CHECKED` は更新しない」なので、brief どおり。1 語ずつ失敗を
  飛ばすかは設計の判断）

### 4. `check.py` の `demo()` — mtime の条件と点検の流れが、壊しても落ちない

- `after_stop()` の `<=`、`check()` の `os.utime` で `CHECKED` の mtime を控えた値に揃える処理
  （実装者が brief から変えた点）、`forget_auto()` の NFKC 比較は、`demo()` から通らない。
  例えば `os.utime` の行を消しても、`<=` を `<` にしても `ccspk test` は通る（コードを読んだ判断。壊して試してはいない）
- 切り出し・`parse`・切り詰めの assert は、壊すと落ちる強さがある（名詞の条件・2 字以上・`KANJI`・
  表に無い表記・カタカナの判定・`strip`・半分に切る位置を、それぞれ assert が押さえている）
- 重さ: 任意（brief の完了条件は満たしている。`after_stop()` は Popen を起こすので、条件の式だけ
  関数に分けないと demo で試せない）

### 5. `CLAUDE.md:23-24` — 手でフックを動かすときの注意に `XDG_STATE_HOME` と料金が無い

- 実装の報告の 2 のとおり。Stop として手で渡すと、裏で本物の `claude -p` が走る（料金がかかる）。
  `docs/Developer.md` の 4.2 には書いたが、`CLAUDE.md` の注意は「読み上げが止まったまま」「鳴っている
  読み上げを止める」の 2 つだけを理由に挙げている
- `docs/Developer.md` の 4.3（最初の音までの時間）も Stop で動かすので、測るたびに一時の `STATE` で
  `最初` などを本物の `claude -p` に渡す。4.3 には注意が無い（4.2 の注意を「上と同じく」で引くだけ）
- 重さ: 任意

### 6. `TODO.md` — 実装した項目のチェックが入っていない

- TODO-036 の 2〜6 つ目は実装済みだが `[ ]` のまま。利用者全体の `CLAUDE.md` は「チェックボックスは
  実装できた時点で入れる（確認の担当に回す前）」
- 重さ: 任意（main の作業）

### 7. `docs/UsersGuide.md:180,192`、`docs/Developer.md:234` — 「語」

- 「1 行 1 語」「30 語ほど」「680 語ほど」。利用者の記録（辞書に登録するものは「単語」と書く）に
  合わせるなら「単語」。同じ文書の 3.12（:537）は「1 単語 1 行」なので、表記も揃っていない
- 重さ: 任意

### 8. `user_dict.py:136,223` — `ADDED` を読むための関数の中の import

- `check` が `user_dict` を import するので、`user_dict` は `check.ADDED` を関数の中で読んでいる（2 か所）。
  `STATE`・`ADDED` を `user_dict.py` に置いて `check.py` が import すれば、循環も関数の中の import も要らない
  （`DICT_FILE` と同じく、辞書まわりのパスを 1 か所に置く形）
- 重さ: 任意（今の形で動く）

## 問題の無かった観点

- フックの最初の音: `check.record()` は `speak()` の後、`after_stop()` は `LOCK` を放した後。`check` の import は
  `-X importtime` で実質 0.4 ms（14 ms の大半は loguru で、hook がもともと読む）。sudachipy はフックから読まない
- フックの早い return: `CCSPK_SPEAK`・`UNUSABLE`・`unusable()`・入力の JSON が読めない、は `try` の前で返り、
  点検を起こさない。`LAST` で 2 度読まない Stop・空の返答の Stop・`OSError` は `finally` で `after_stop()` を通る。brief どおり
- Stop の判定: `not (display or ask)` は、既存の「MessageDisplay でも PreToolUse でもなければ Stop として読む」と同じ分け方
- 同時に 1 つ: `check.lock` を `LOCK_NB` で取り、`check()` の間ずっと持つ。取れなかった点検の分は、
  `CHECKED` の mtime が古いままなので次の Stop で拾われる
- `CHECKED` の mtime: 控えた `SPOKEN` の mtime に揃えるので、点検中の追記は次に回る。float の往復で `SPOKEN`
  のほうが新しく見えることは 2,000 回で 0 回（ext4、実測）
- `spoken.txt` の切り詰め: フックの `LOCK` の中で追記・切り詰めをし、一時ファイルから `replace` するので、
  点検の読み出しとぶつかっても壊れない
- 失敗の拾い方: `except (Exception, SystemExit)` で `user_dict.call` の `sys.exit` も拾う。タイムアウトの文も短い
- `claude -p` がフックを走らせない: `--setting-sources ""` と `CCSPK_SPEAK=0`。`--tools` は可変長の引数だが、
  直後に `--no-session-persistence` があるのでプロンプトは食われない（`claude --help` で確認）
- 誤った登録: 渡していない表記（`surface in table`）とカタカナでない読みは捨てる。demo が押さえている
- `/audio_query` の負荷: 30 語で 0.075 秒（実測）。点検が読み上げの合成と重なっても目立たない
- `user_dict.py`: `dict add`・`dict remove` の引数と出力は変わらない（`register()` は元の行をそのまま移した）。
  循環 import は関数の中の import で避けていて、`ccspk test`・`ccspk hook` の import は通る
- `dict auto --remove`: 無い単語は飛ばし、`save()` は最後に 1 回
- 文書: `docs/Developer.md` の「2. 動き方」は既存の文を変えず 1 項目を足しただけ。章の番号を変えた
  3.13・3.14 へのリンクは、リポジトリ（archives を除く）に無い。UsersGuide の「5 秒以内」は `SAME_WITHIN = 5` と一致。
  `ccspk test` の `ok` 3 行も一致
- 範囲: 指示に無い変更は無い（README.md は TODO-036 の 7 つ目の項目）

## 作り込みすぎ

作り込みすぎ: なし（8. は置き場所の話で、消せる行は 4 行ほど）。
