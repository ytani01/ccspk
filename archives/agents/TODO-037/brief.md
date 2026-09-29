# TODO-037 実装の依頼（main → implementer）

目的: 整えた文が `LIMIT`（180 字）を超える返答を、`claude -p`（Sonnet）で要約してから読むオプションを足す。
`TODO.md` の TODO-037 の 2〜5 つ目の項目。背景と決めたことは `TODO.md` の TODO-037 と
`archives/agents/TODO-037/main-measure.md` にある。先に読むこと。

## 設計（main が決めた。変えるなら報告で理由を書く）

### 切り替え

- 状態のファイルは `~/.config/ccspk/summary`（`user_dict.DICT_FILE` と同じディレクトリ。`XDG_CONFIG_HOME` に従う）。
  ファイルがあれば入、無ければ切。`ccspk summary on` で作り、`off` で消す。引数なしは今の状態を `on` / `off` で表示する
- 環境変数 `CCSPK_SUMMARY` が `1` なら入、`0` なら切で、ファイルより優先する。ほかの値は無いものとして扱う。
  環境変数で決まっているときは、`ccspk summary`（引数あり・なし）の表示に、環境変数が優先していることを 1 行添える
- コマンドは `hook.py` の `stop`・`status` と同じ並びに置き、`cli.py` に `summary` として足す
- フックは返答のたびに状態を読む（次の返答から効く）

### フック（`main()`）

- 今は `to_speech()` の最後で `clip()` を通している。要約が入っていて、`clip()` の前の文が `LIMIT` を超えるとき
  だけ、切る前の文を子プロセスに渡して要約させる。それ以外は今までどおり（切った文を渡す）
- イベントは問わない（Stop・MessageDisplay・PreToolUse の 3 つとも）
- 2 度読まない仕組み（`LAST`）は、子プロセスに渡す文で比べる。最後の返答は MessageDisplay と Stop から同じ文で来るので、
  要約するときもそのまま効く
- 要約するときは、フックでは `check.record()` を呼ばない（子プロセスが読んだ文を記録する。下を参照）。
  要約しないときは今までどおり

### 子プロセス（`python -m ccspk.hook --play …`）

- 要約するときは、`--play` の後ろに要約の印を付けて起こす（形は任せる。`stop_playing()` が `--play` と `ccspk.hook` で
  見分けるのは変えない）
- 子プロセスの中で `claude -p --model sonnet --setting-sources "" --tools "" --no-session-persistence <プロンプト>` に
  文を標準入力で渡す。`cwd` は空のディレクトリ（`user_dict.STATE` を `mkdir` して使う。`check.py` と同じ）。
  環境変数は `CCSPK_SPEAK=0` を足す。子プロセスは自分のプロセスグループにいるので、`stop_playing()`・`ccspk stop` の
  `killpg` で `claude -p` ごと止まる（`start_new_session` を `claude -p` に付けないこと）
- 時間の上限は 30 秒（Sonnet で 5〜6 秒だった）。時間切れ・終了コードが 0 でない・出力が空・起こせない（`OSError`）の
  どれでも、切った文（`clip()`）を読む。失敗は知らせない
- 要約できたら、`to_speech()` を通して（`clip()` まで）読む。要約は 180 字を少し超えることがある（最大 231 字）
- 読む文（要約、または失敗したときに切った文）を `check.record()` で記録してから鳴らす。`record()` は hook の `LOCK` を
  取ったまま呼ぶ前提なので、子プロセスでも `LOCK` を取ってから呼ぶ
- プロンプトは `archives/agents/TODO-037/prompt.txt` を元にし、字数は `LIMIT` から作る。測定で Sonnet が
  「利用者に頼むことはありません」とプロンプトの言い回しをそのまま返したので、無いことには触れないよう直す

### 変えないもの・保つもの

- 要約が切のとき、超えない返答のときの動きと出力（`demo()` の既存の assert は全部そのまま通ること）
- `stop_playing()` の見分け方、`PIDFILE`・`LAST`・`LOCK` の扱い、TODO-036 の点検の起こし方
- フックに重い import を足さない
- 点検（`check.py`）の `claude -p` 呼び出しと共通化しない（モデル・上限・失敗の扱いが違う）

## demo()

`ccspk test` で走る `demo()` に足す。本物の `claude` は呼ばない（料金がかかる）。
`PATH` の先頭に一時ディレクトリを置き、そこに偽の `claude`（シェルスクリプト）を置いて確かめる。

- 切り替え: ファイルの有無と環境変数の組み合わせ（`XDG_CONFIG_HOME` を一時ディレクトリに向ける）
- 要約するかどうかの分かれ目: 切・入 × `LIMIT` ちょうど・超える
- 要約: 偽の `claude` が返した文を `to_speech()` に通すこと、終了コードが 0 でない・空・時間切れで切った文になること
  （時間切れは上限を差し替えて短くする）

## 文書

- `docs/UsersGuide.md`: 「3. コマンド」に `ccspk summary` の節を足す（ほかのコマンドの節と同じ形）。
  関係する所（「1. インストール」の後の使い方の節など、読み上げの長さに触れている所）から参照する。
  要約すると最初の音が 5〜6 秒ほど遅れること、1 回 1〜1.5 セントほどかかることを書く
- `docs/Developer.md`: 「2. 動き方」「3.1 流れ」「3.2 子プロセス」「3.6 整形と分割」の表、関係する定数の表、
  「3.8 自動の点検」の `record()` の説明（要約のときは子プロセスが記録する）を今の動きに合わせる
- `CLAUDE.md`・`README.md`・`cli.py` のサブコマンドの並びに `summary` を足す

節の番号を変えたら、文書の中のリンク（`#32-ccspk-hook` のような形）を `rg -n '#[0-9]+-' docs README.md` で拾って直す。

## 確かめて報告すること

- `uv run ccspk test` が通る
- 本物の `claude` は呼ばない。本物の `$XDG_RUNTIME_DIR`・`$XDG_STATE_HOME`・`$XDG_CONFIG_HOME` を使わない
  （`CLAUDE.md` の注意）
- 報告は `archives/agents/TODO-037/implementer-report.md` に、変えたこと・確かめたこと・迷ったことだけ書く。
  返事は 5 行以内
