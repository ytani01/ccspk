# TODO-009 reviewer の報告

対象: 未コミットの差分（README.md / TODO.md / docs/Developer.md / docs/UsersGuide.md）と
`voicevox/add-word.py`。プロジェクトに `CLAUDE.md` は無いので、TODO-009 の節、
UsersGuide、Developer.md、`hooks/speak-response.py` の書き方を基準にした。
辞書を書き換える要求は送っていない（最後の件数も 11 件のまま）。

## 要修正

なし。

## 検討

### 1. `add-word.py:22,74,83` 登録済みの語を書き換えると、品詞が `PROPER_NOUN` に戻る

- `--type` の既定が `PROPER_NOUN` で、PUT でもいつもこれを送る。登録済みの語の品詞は
  引き継がない
- `voicevox/user_dict.json` を見ると、`ｒｅｖｉｅｗｅｒ`・`ｖｅｒｉｆｉｅｒ`・
  `ｉｍｐｌｅｍｅｎｔｅｒ` は `part_of_speech_detail_1 = 一般`（`COMMON_NOUN`）。
  読みを直そうと `add-word.py reviewer レビュータントウ` と打つと、黙って
  固有名詞になる
- 同じく PUT は `priority` を送らない。エンジンの既定に戻るはず（未確認）。今は
  11 語とも 5 なので影響は出ない
- UsersGuide の「同じ表記が登録済みなら、読みを書き換える」は、品詞も変わることを
  書いていない
- 読み上げへの実害は未確認

### 2. `add-word.py:43` 句が 0 個のとき `IndexError` の traceback で落ちる

実測: `python3 voicevox/add-word.py ZZZTEST ー` で
`IndexError: list index out of range`（終了コード 1）。`/audio_query` は
`""`・`ー`・`!` で `accent_phrases` が `[]` を返す（curl で確認）。辞書を書く前に
落ちるので辞書は壊れないが、読みの打ち間違いが traceback で返る。`--accent` を
付けた場合はエンジンに送られ、エンジンが断るかは未確認。

### 3. `add-word.py:92` `pw-play` が無いと、登録した後に `FileNotFoundError` の traceback

実測（`call` を差し替えた一時スクリプトで、`PATH=/nonexistent`）:
`FileNotFoundError: [Errno 2] No such file or directory: 'pw-play'`。
登録は済んでいて「登録した: …」は先に出るので、結果は分かる。`check=True` で
`pw-play` が失敗したときも `CalledProcessError` の traceback になる（未確認、コードから）。
フックは `shutil.which("pw-play")` で先に見ている（`hooks/speak-response.py:48`）。
エンジンの応答が遅く読み出し中に時間切れになった場合の `TimeoutError` も、
`URLError` に包まれずに traceback になる（未確認、コードから）。

### 4. 平板の見なしを TODO-009 に記録していない

`accent_of()` の「句が 1 つで最後の音なら 0」は、TODO-009 の「決めたこと」にも
「実測」にも無い（実測に書いてあるのは 5・4 と、分かれたら先頭の句）。
見なしそのものは実測と合っている。`サクラ`（平板）も `オトコ`（尾高）も
`(accent 3, moras 3)` で返り、見分けられない（`/audio_query` を curl で確認）。
決めたことと実測として TODO-009 に残すかを、管理者が判断する。

### 5. `docs/UsersGuide.md:131-133` 平板の見なしの箇条が、利用者への指示にも読める

「句が 1 つで最後の音で下がるときは平板（`0`）として登録する」は、主語が無く、
「そう登録しなさい」とも「スクリプトがそう登録する」とも読める。直前が
`--accent` の説明なので前者に読みやすい。尾高の語は `--accent <音の数>` で直す、
という逆向きの手順も書いていない。

### 6. `docs/Developer.md:135-147` 自己テストの節に `add-word.py --test` が無い

`add-word.py` にも `demo()` があるが、「自己テスト」の節は
`python3 hooks/speak-response.py --test` だけを挙げている。冒頭で
`add-word.py` に触れたので、テストの節にも 1 行あると辿れる。

## 好みの範囲

- `docs/UsersGuide.md:166` 「読みを変えるときは、消して登録し直す（`PUT … でもよい`）」は、
  `add-word.py` でも書き換えられるようになった後も、そのまま残っている
- `add-word.py:28,53,79,80` は 106〜111 字。フックの最長は 105 字
  （`hooks/speak-response.py:187`）。行の長さの決まりは見当たらない

## 一致したもの

- `accent_of()`: 句が 1 つで最後の音 → 0、句が複数 → 先頭の句の位置。TODO-009 の実測
  （`ハイパーウィスパー` 5/8、`レビュータントウ` 4/7、`リードミー` `[(1,2),(1,3)]`）と、curl で測った値が一致
- `find()`: NFKC で比べ、大文字と小文字は別。`call` を差し替えて確かめた。
  `README` と `ＲＥＡＤＭＥ` → 既存の ID で PUT。辞書に `ｊｓｏｎ` だけがあるときの
  `JSON`・`Json` → POST
- 登録済みなら `PUT /user_dict_word/{uuid}`。引数（surface / pronunciation / accent_type /
  word_type を query で渡す）は openapi.json（エンジン 0.25.2）と一致。応答 204 の空の本文も `.read()` で問題ない
- `--accent 0`: `is not None` で `/audio_query` を飛ばし、0 のまま送る（差し替えで確認）
- `--speak`: `/audio_query` で表記を読み、`/synthesis` に JSON を渡して `pw-play -`
- 接続できないとき: ポートを 1 に変えた一時コピーで
  `エンジン（http://127.0.0.1:1）に接続できない: [Errno 111] Connection refused`、終了コード 1
- エンジンが断ったとき: 話者を 999999 にした一時コピーで `エンジンが断った（500）: {"detail":…}`。
  `HTTPError` を `URLError` より先に捕まえている。422 も同じ経路を通る（422 そのものは送っていない）
- `call()` の Content-Type: 本文があるとき（`/synthesis`）だけ `application/json`。フックと同じ
- `SPEAKER = 119` はフックと同じ
- README の表、Developer.md の冒頭は `add-word.py` の動きと合っている
- 範囲: 指示に無い変更は無い。TODO.md はチェックボックスだけ

## テストの強さ（`--test`）

`python3 voicevox/add-word.py --test` → `ok`。一時コピーで `accent_of()` を壊した結果:

| 壊し方 | 結果 |
|---|---|
| 平板の見なしを消す（`return first["accent"]`） | AssertionError |
| `len(phrases) == 1 and` を消す | AssertionError |
| いつも 0 を返す | AssertionError |
| 先頭ではなく最後の句を使う | AssertionError |
| `len(moras) - 1` と比べる | AssertionError |
| `len(phrases) <= 2` にする | AssertionError |
| `==` を `>=` にする | ok（通る） |
| 比べる先を全部の句の音の数の合計にする | ok（通る） |

通った 2 つは、どちらも今の入力では同じ結果になる書き換え（accent は音の数を超えない。
句が 1 つなら合計と同じ）なので、テストが弱いとは言えない。`find()` の NFKC の比べ方は
`demo()` で確かめていない（エンジンの辞書を読むため）。

## 作り込みすぎ

- `add-word.py:82-87`: shrink: 同じ形の `print` が 2 つ。`verb = "書き換えた" if uuid else "登録した"` のあと 1 つの `print` にできる。-1 行。好みの範囲

net: -1 lines possible.
