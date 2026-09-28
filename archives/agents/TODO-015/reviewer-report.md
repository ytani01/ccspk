# TODO-015 レビュー報告（reviewer）

対象: `git diff HEAD -M`（`add_word.py` → `user_dict.py` の改名を含む）。
動作の実測はしていない（verifier の担当）。`jq -S .` との一致だけは、エンジンを使わずに
Python と jq 1.8.2 で出力を比べた。

## 要修正

なし。

## 検討

### 1. `src/claudecodespeak/user_dict.py:97-98` — エンジン以外の `OSError` も「エンジンとやり取りできない」と出る

- 内容: `_guarded` は `OSError` をすべて
  `エンジン（http://127.0.0.1:50021）とやり取りできない: …` にして終了コード 1 で終わる。
  これを全サブコマンドに掛けたので、エンジンと関係の無い `OSError` も同じ文言になる。
  - `dict export FILE` の書き込み中の失敗（`ENOSPC` など）
  - `dict list` / `dict kana` / `dict export` を `| head` などにつないだときの `BrokenPipeError`
    （出力がバッファに収まる大きさなら、関数の外の終了時の flush で起き、ここには来ない）
- 理由: 旧 `add-word` の `try` が囲んでいたのはエンジンとの通信と `pw-play` だけで、
  ローカルのファイルや標準出力へ書く処理は無かった。今回 `export` と `list` が加わり、
  範囲が広がった。ファイルを開くときの失敗は、click の `LazyFile.open()` が
  `click.FileError`（`OSError` ではない）にするので、この文言にはならない
  （click 8.5.0 のソースで確認）。
- 実害は未確認。原因の文言が違うだけで、終了コードは 1 のまま。

### 2. `docs/UsersGuide.md` の「読み上げの辞書」冒頭 —「下のコマンドはどれもリポジトリの直下で走らせる」

- 内容: この節の直下にあるのは `dict kana`・`dict add`・`dict list`・`dict remove`・
  `dict export`・`dict import`。リポジトリの直下が要るのは、相対パスでファイルを渡す
  `export` と `import` だけ。
- 理由: 設計（`README.md` の「文書」）は「`dict export` / `dict import` の例は
  リポジトリの直下で走らせる形」としていて、他のサブコマンドまでは言っていない。
  `uv tool install` で入れた利用者が、`dict add` にもリポジトリが要ると読める。
  TODO.md の背景にも「リポジトリの場所を前提にしない」とある。

### 3. `TODO.md` の TODO-015 — チェックボックスが 1 つも入っていない

- 内容: 設計の完了条件は「`TODO.md` の TODO-015 のチェックボックスを、実装できたものから
  入れる」。実装担当の報告は「指示（管理者が入れる）どおり触っていない」で、食い違っている。
- 理由: 利用者の `CLAUDE.md` は「チェックボックスは実装できた時点で入れる（確認の担当に
  回す前）」。どちらが入れるにせよ、verifier に回す前に入っている必要がある。

## 好みの範囲

- `docs/Developer.md:172`「通れば `ok` と出る」— `test` は `ok` を 2 行出すようになった。
  「`ok` が 2 行出る」のほうが正確。
- `src/claudecodespeak/hook.py:451`（`status --clear` の help「UNUSABLE を消す」）と `status` の
  docstring — `--help` を読む利用者には `UNUSABLE` という定数名は見えない。
  `claude-tts.unusable` などファイル名のほうが通じる。

## 問題の無かった観点

- hook.py の子プロセスの目印: `PLAY`・`MODULE`・`speak()`・`stop_playing()`・`__main__` の
  ブロックは差分に入っていない（hunk は `main` のオプション削除と `say`・`status` の追加だけ）。
- `hook` の動き: `main()` の本体はオプション分岐の削除だけで、以降は同じ。`cli.py` の
  `hook` の登録名も同じ。
- `say`: `play(text)` を呼ぶだけで旧 `--play` と同じ。起動の cmdline に `claudecodespeak.hook` が
  入らないので、旧と同じく `stop_playing()` の対象にはならない。
- `status`: ある・ない・`--clear` の分岐、どれも終了コード 0。設計どおり。
- `dict` の各サブコマンドの引数・終了コード: `remove` で見つからなければ `sys.exit` で 1、
  HTTP の失敗は 1、引数の誤りは click の 2。`add` の引数・オプション・表示は旧 `main` と同じ。
- `_guarded` の位置: `@click.command` より内側に掛かっており、`functools.wraps` で docstring
  （help）も保たれる。`HTTPError` を `OSError` より先に捕まえている。
- `export` の FILE: `click.File("w")` は遅延で開くので、エンジンに繋がらないときに既存の
  ファイルを空にしない（旧 `curl … | jq -S . > FILE` はシェルが先に空にしていた）。
- `export` と `jq -S .` の一致: `{}` と、非 ASCII・入れ子の空配列と空オブジェクト・整数・
  `1.0` は一致した。食い違ったのは DEL（`\u007f`）と指数表記の数（`1e3`）だけで、
  今の `voicevox/user_dict.json` の値は `str` と `int` だけなので当たらない。
- `import` の FILE 省略時: `click.File("rb")` の `-` で標準入力をバイトで読む。空の入力は
  `Content-Type` 無しで送られるが、エンジンが断れば `HTTPError` で 1 になる。
- 旧い書き方の残り: `archives/` の外で出るのは、TODO.md の TODO-015 の本文、
  `unusable()`・`UNUSABLE`・`.unusable` のファイル名、子プロセスの `--play`、
  エンジンの起動確認の `curl …/version`、一時ディレクトリの `rm -r $tmp`、
  vvpp の `rm` だけで、どれも残してよいもの。
- 文書とコードの食い違い: 上の検討 2 と好みの範囲 1 のほかは無し（サブコマンド名、`list` の
  列と並び、`import` の上書きの説明、`ENGINE`/`SPEAKER` の置き場所、README の表）。
- 範囲: 指示に無い変更は無い。
- テスト: `demo()` は両方残り、`test` から両方走る。追加されたサブコマンドはエンジンか
  実行時のディレクトリが要り、中身は API 呼び出しと `json.dump` だけなので、`demo()` に
  足すものは無い。
- コメント: 追加分は「なぜ」（`_guarded` の目的、`export` の形）を書いている。

## 作り込みすぎ

なし。`_guarded` は設計で指示された「関数 1 つかデコレータ 1 つ」で、`test` も 2 行。
