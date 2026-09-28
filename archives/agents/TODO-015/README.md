# TODO-015 の分担

| 担当 | 受け持ち | 理由 |
|------|----------|------|
| main | 設計（この文書） | サブコマンドの形は利用者と決め済み。残るのはファイルの割り振りだけ |
| implementer（Sonnet 5 / medium） | コードと文書の書き換え | 複数のファイルにまたがるが、どれも既存の関数の付け替えと API 呼び出しの追加で、込み入ったロジックは無い |
| reviewer（Opus 5.5 / high） | 差分のレビュー | コマンドの分岐と引数の扱いが変わる |
| verifier（Sonnet 5 / medium） | 実際に動かして確かめる | reviewer の指摘を直した後に回す |

## 設計

目的: `TODO.md` の TODO-015 の表のとおりにサブコマンドを並べ直す。完成形は
`claudecodespeak --help` で `dict`・`hook`・`say`・`status`・`test` が出ること。

### ファイル

- `src/claudecodespeak/add_word.py` → `git mv` で `src/claudecodespeak/user_dict.py` にする
  （`dict.py` は組み込みの `dict` と紛らわしいので避ける）。click の group `dict` を置き、
  下に `add`・`kana`・`list`・`remove`・`export`・`import` を置く。
  - `add`: 今の `main` をそのまま（`--test` は外す）
  - `kana TEXT`: `query(TEXT)["kana"]` を表示する
  - `list`: `GET /user_dict` を 1 語 1 行で `ID  表記  読み  accent_type` と表示する。並びは表記順
  - `remove SURFACE`: `find()` で引いて `DELETE /user_dict_word/<ID>`。無ければ
    `sys.exit("登録されていない: …")`（終了コード 1）
  - `export [FILE]`: `GET /user_dict` を `jq -S .` と同じ形（`indent=2`・`sort_keys=True`・
    `ensure_ascii=False`・末尾に改行）で FILE へ書く。省くと標準出力。
    **今の `voicevox/user_dict.json` とバイト単位で一致する出力にする**（書き出すたびに
    差分が出ないように）
  - `import [FILE]`: FILE（省くと標準入力）を `POST /import_user_dict?override=true` に
    `Content-Type: application/json` で送る。`click.File` を使う
  - エンジンとのやり取りの例外処理（`HTTPError`・`OSError`）は、今 `main` にあるものを
    全サブコマンドで共通にする（関数 1 つかデコレータ 1 つで。サブコマンドごとに写さない）
  - `demo()`（`accent_of` の自己テスト）は残す。`_test` コールバックは消す
  - ロガー名 `"add-word"` は `"dict"` にする
- `src/claudecodespeak/hook.py`:
  - click の `main` から `--test` と `--play` のオプションを外し、フック専用にする
  - `say TEXT` コマンドを足し、`play(TEXT)` を呼ぶ（help は「合成と再生だけを試す（子プロセスと同じ動き）」）
  - `status` コマンド（`--clear` フラグ付き）を足す。`UNUSABLE` があれば中身（理由）とパスを
    表示し、`--clear` なら消して「消した」と表示する。無ければ「止まっていない」と表示する。
    終了コードはどちらも 0
  - **`PLAY = "--play"`・`MODULE`・`speak()`・`stop_playing()`・末尾の
    `if __name__ == "__main__":` は変えない。** フックの子プロセスは click を通らずに
    `python -m claudecodespeak.hook --play TEXT` で動き、`stop_playing()` はこの引数で
    自分の子プロセスかを見分けている
- `src/claudecodespeak/cli.py`: `hook`・`say`・`status`・`test`・`dict` を登録する。
  `test` は `hook.demo()` と `user_dict.demo()` を順に呼ぶ（それぞれ `ok` を出す）。
  `test` の定義は `cli.py` に置いてよい

### 文書

対象は次で拾う。改名なので、旧名が文中に単語として出てくる箇所も書き換える。

```sh
rg -n -e 'add-word' -e 'add_word' -e '--play' -e '--test' -e 'curl' -e 'unusable' -e 'jq' README.md CLAUDE.md docs/
```

- `curl`・`jq`・`rm` で辞書や `claude-tts.unusable` を操作している手順は、サブコマンドに
  置き換える。エンジンの起動確認（`curl …/version`）はサブコマンドが無いので残す
- 辞書の手順のうち、`curl` での登録方法そのものの説明（`--data-urlencode` の注意など）は消す。
  `accent_type` の意味と、英字の大文字と小文字を別の語として扱う話は、`dict add` の説明に
  残す（中身が今も正しいので）
- `dict export` / `dict import` の例はリポジトリの直下で走らせる形
  （`claudecodespeak dict export voicevox/user_dict.json`）にする
- `CLAUDE.md` の「コマンド」は `uv run claudecodespeak test` 1 行と `say` の例にする
- `README.md` のファイルの表は `user_dict.py` に直す

### 変えないもの・保つもの

- `hook` の動き（標準入力を読んで読み上げる）と、`settings.json` から呼ぶ形
- `dict add` の引数・オプション・表示
- `archives/` は書き換えない（過去の記録なので旧名のままでよい）
- 旧名の別名は残さない

### 完了条件

- `uv run claudecodespeak test` が `ok` を 2 行出す
- `uv run claudecodespeak --help` と各サブコマンドの `--help` が出る
- 上の `rg` で、`archives/` の外に旧い書き方（`add-word`・`hook --play`・`hook --test`・
  辞書と unusable の `curl`/`rm`）が残っていない
- `TODO.md` の TODO-015 のチェックボックスを、実装できたものから入れる

報告は `archives/agents/TODO-015/implementer-report.md` に、変更点と、試したこと・試せなかったこと
（エンジンが動いていなければそう書く）を書く。

## レビュー後に main が直したこと

- reviewer の指摘 1: `_guarded` を消し、エンジンとの通信の例外処理を `call()` の中へ移した。
  `export` の書き込みの失敗や `BrokenPipeError` を「エンジンとやり取りできない」と言わないように
- 指摘 2: UsersGuide の「下のコマンドはどれもリポジトリの直下で」を、`dict export` と `dict import` に限った
- 指摘 3: TODO.md の TODO-015 のチェックボックスを入れた
