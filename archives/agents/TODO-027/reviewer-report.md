# TODO-027 reviewer の報告

対象: `git diff HEAD -- docs/UsersGuide.md README.md`（旧版は `git show HEAD:docs/UsersGuide.md`）。
根拠は `src/ccspk/cli.py`・`hook.py`・`user_dict.py`・`click_utils.py`、`systemd/voicevox-engine.service`、
`.venv/bin/ccspk <sub> -h` の出力。コマンドは `-h` と引数の誤り（`dict add` の引数なし、
`dict import /nonexistent`）だけ動かした。行番号は作業ツリーの `docs/UsersGuide.md`。

## 要修正

### 1. Developer.md から張られたリンクの先に、理由が無くなった

- `docs/Developer.md:132` — `PIPEWIRE_REMOTE があるときは確かめない（理由は [UsersGuide](UsersGuide.md#読み上げが止まったままのとき)）`
- 理由（`[a,b]` のような形も取り、つながる先を決めきれない）は、旧版では「読み上げが止まったままのとき」に
  あったが、新版では `docs/UsersGuide.md:198-199`（`### ccspk hook`）へ移った。
  新版の「読み上げが止まったままのとき」（104-112 行）には `PIPEWIRE_REMOTE` が出てこない
- 見出しは残っているのでリンクは切れないが、飛んだ先に探している説明が無い。
  張り先を `UsersGuide.md#ccspk-hook` にするかどうかは管理者の判断（Developer.md は今回の差分の外）

他の文書から張られた見出し（`#読み上げの辞書`・`#読み上げが止まったままのとき`・`#記号と数字`、
CLAUDE.md の「辞書のファイル」）はすべて残っている。Developer.md:54・205 の「戻し方」「消すまで止まる」は、
新版の手順（110-112 行）と合っている。

## 検討

### 2. `say` の終了ステータス `1` が付く条件が狭い（233-234 行）

- `hook.py` の `play()` は、合成を別スレッド（`produce`）で行い、1 つ目の wav が来てから
  `subprocess.run(["pw-play", "-"], ...)` を呼ぶ。`pw-play` が無いときの `FileNotFoundError` は
  呼び出し側で捕まえていないので `1` になるが、**1 つ目の合成が成功したときだけ**。
  エンジンに接続できないと `produce` が例外で終わって `None` だけが入り、`pw-play` を一度も呼ばずに
  `0` で終わる（`pw-play` が無くても `0`）
- `pw-play` が 0 以外で終わっても、`returncode` を見ていないので `0`
- 「理由は標準エラー出力に出る」は、どちらも Python のトレースバック（`threading` の既定の
  excepthook と、捕まえていない例外）。`sys.exit(文字列)` の短い文ではない
- コードを読んだだけで、動かしてはいない（verifier の範囲）。書き方を「`pw-play` が無い
  （合成が 1 つ以上できたとき）」のように絞るか、今のままにするかは管理者の判断

### 3. 同じ説明が手順の節とコマンドの節の両方にある

| 説明 | 手順の節 | コマンドの節 |
|------|---------|-------------|
| 止めるのは再生だけで、次の返答はいつもどおり読み上げる | 102 | 251-252（`stop`） |
| `status --clear` のあと、次の返答からフックがまた確かめる | 112 | 277（`status`） |
| `dict add`・`remove`・`import` が成功するとファイルへ書き出す | 136-138（辞書のファイル） | 333-334（`dict`）、399・449・499（各「ファイル」）、468（`export`） |
| エンジンの起動時にファイルを `dict import` で読み込む | 37（インストール、差分の外）、139 | 490-491（`import`） |
| 英字の大文字と小文字は別の単語 | 130 | 376（`dict add` の `SURFACE`） |

- 手順の節に 1 行の要約を残すのは読みやすさのためとも取れる。どこまで削るかは管理者の判断
- 書き出しの説明は 5 か所以上に散っている。`ccspk dict` の前書き（333-334）で言い切っているので、
  各サブコマンドの「ファイル」の行と `export` の 468-469 行は重ねて言っている

### 4. `kana`・`list`・`export`・`import` に「終了ステータス」の小見出しが無い

- `TODO.md` の 1 つ目のチェック項目は「1 つずつ、書式・説明・オプション・終了ステータス・関係するファイル・例
  の順で書く」。`add`（391）・`remove`（442）にはあり、`kana`（336-357）・`list`（410-426）・
  `export`（459-479）・`import`（481-507）には無い
- 中身は `ccspk` の共通（169-173）と `ccspk dict` の前書き（329-331）で足りているので、省いたこと自体は
  筋が通る。揃えるか、項目の書き方の方を合わせるかは管理者の判断

### 5. 例どうしがつながっていない（424-425 行）

- `dict add` の例で `Ponytail` を登録し（403-406）、`dict remove` の例で消している（453-456）が、
  間の `dict list` の例に `Ponytail` が無い
- `dict list` の例の優先度が `5`。手順の節の例（126 行 `ccspk dict add README リードミー --speak`）で
  登録すると、`user_dict.py:140` のとおり新しい単語は `7` になるので、手順どおりにやった人の表示と合わない
- 例は実際の出力を写したものと思われる。実害は未確認

### 6. `hook` が何もせず終わる条件（193-199 行）が全部ではない

- コード（`hook.py:main`）では、ほかに次のときも読まずに終わる: 標準入力が JSON として読めない、
  MessageDisplay・PreToolUse で `agent_id` がある（サブエージェント）、整えると空になる途中の文章や質問、
  5 秒以内の同じ文（`SAME_WITHIN`）、MessageDisplay の分がそろっていない
- 「サブエージェントの報告や質問では鳴らない」は利用者にも見える動きで、今は `docs/Developer.md:50-51` にだけある。
  旧版の UsersGuide にも無かったので、落ちた説明ではない。足すかどうかは管理者の判断

## 好みの範囲

- 197-199 行: 「何もせずに終わる」の見出しの下に「理由をファイルに記録する」が入っていて、
  何かはしている。「読み上げずに終わる」なら食い違わない
- 307 行: `test` の説明は「整形・分割と、辞書のアクセントの決め方」だが、`user_dict.demo()` は
  表記の半角化（`halfwidth`）も、`hook.demo()` は質問の文の取り出しと MessageDisplay の分のつなぎも試している

## 合っていたもの

- `ccspk` のオプション（`-d`/`--debug`、`-V`/`-v`/`--version`、`-h`/`--help`）: `click_utils.py`・`-h` と一致。`-h` はサブコマンドにも効く（`dict add -h` で確認）
- 共通の終了ステータス: `1` は `sys.exit(文字列)`（標準エラー出力）、`2` は click の使い方の誤り（`dict add` 引数なし・`dict import /nonexistent` で実測 `rc=2`）
- `hook`: 3 つのフックと読むもの、子プロセスに任せてすぐ終わる、前の再生を止める、`CCSPK_SPEAK`・理由のファイル・`unusable()` の 3 条件と `PIPEWIRE_REMOTE` の扱い、`ccspk.unusable` のパス（`hook.py` の `BASE`・`UNUSABLE`）: 一致
- `say` がしないこと（`CCSPK_SPEAK`・理由のファイルを見ない、整形しない・上限なし、`stop` で止まらない）: `say` は `play(text)` だけで、`to_speech`・`PIDFILE` を通らない。一致
- `stop`: 「止めた」「鳴っていない」、合成は止めない、ロックを取る: 一致
- `status`・`status --clear`: 表示の形（`{UNUSABLE}: 理由`、「消した」「止まっていない」）が一致
- `test`: `ok` を 2 行、エンジンに接続しない、`assert` の失敗で `1`: 一致
- `dict` の前書き（全サブコマンドがエンジンに接続、`HTTPError`・`OSError` で `1`、書き出して「書き出した: パス」）: `user_dict.py` の `call`・`save` と一致
- `dict kana` の記号（`'`・`/`・`、`・`_`）: VOICEVOX の AquesTalk 風の表記と一致（エンジンの実装はリポジトリに無いので、記号の意味は既知の仕様による）
- `dict add` のアクセント（省くとエンジン、句が 1 つで最後の音なら `0`、尾高は `--accent <音の数>`）: `accent_of` と一致。`--type` の選択肢と既定、`--priority` の範囲と既定 `7`・登録済みは今のまま、`--speak` の失敗で `1` だが登録は済み、表示の順（登録した→書き出した→読み:）: 一致
- `dict list` の並びと表記順、`dict remove` の `1`（登録されていない）と表示、`export` の半角・標準出力、`import` の上書き・残る単語・起動時の読み込み（`voicevox-engine.service` の `ExecStartPost`）: 一致
- 旧版から落ちた説明: 無い（旧版の各段落の行き先を突き合わせた。`dict export と同じ形` は `export` 側の「辞書のファイルと同じ形」、「読みを変えるときは同じ表記で `dict add`」は `add` の説明へ移っている）
- UsersGuide 内のリンク（`#ccspk-test`・`#ccspk-hook`・`#ccspk-stop`・`#ccspk-status`・`#ccspk-dict`・`#辞書のファイル`）: 張り先の見出しがすべてある
- README.md の 1 語: 一覧の書き方と合っている
- 言い回し: 造語・直訳調は見当たらない。「単語」の使い方も揃っている
- 範囲: 差分は UsersGuide.md と README.md の指示どおりの箇所だけ

## 作り込みすぎ

- `docs/UsersGuide.md:399,449,499`: shrink: 各サブコマンドの「ファイル」の節が、前書き 333-334 行の「書き出す」を言い直している。前書きだけで足りる（-9 行）
- `docs/UsersGuide.md:468-469`: delete: `export` の「辞書のファイルは…が書き出すので」は前書きと辞書のファイルの節の繰り返し。「控えを取るときに使う」だけ残す（-1 行）
- `docs/UsersGuide.md:279-281`: shrink: `status` の終了ステータス `0` だけの小見出しは、共通の節で足りる（-3 行。項目の書式に揃えるなら残す）

net: -13 lines possible.
