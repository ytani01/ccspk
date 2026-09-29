# TODO-036 実装の依頼（main → implementer）

目的: 読み上げた文から読み間違いを見つけ、辞書に自動で登録する。`TODO.md` の TODO-036 の 2〜6 つ目の項目。
決まったこと（背景）は `TODO.md` の TODO-036 と `archives/agents/TODO-036/main-measure.md` にある。先に読むこと。

## 設計（main が決めた。変えるなら報告で理由を書く）

### ファイル（状態のディレクトリ）

`STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "ccspk"`

| ファイル | 中身 |
|------|------|
| `spoken.txt` | 読み上げた文（`to_speech()` の結果）を 1 行 1 文で追記。64 KiB を超えたら後ろ半分の行だけ残す |
| `checked.txt` | 点検に回した単語（1 行 1 語）。誤りでなかったものも入れる。自動で登録した単語を利用者が消しても、ここに残るので登録し直さない |
| `added.tsv` | 自動で登録した単語。`日時<TAB>表記<TAB>正しい読み<TAB>エンジンの元の読み` |
| `failed.txt` | 点検の失敗の内容。次の Stop フックが `systemMessage` で知らせて消す |
| `check.lock` | 点検が 1 つだけ走るようにするロック |

### フック（`src/ccspk/hook.py` の `main()`）

- 鳴らす文（`speak(text)` を呼ぶとき）を `spoken.txt` に追記する。イベントは問わない（Stop・MessageDisplay・PreToolUse）
- Stop のとき（`display` でも `ask` でもない）だけ、ロックの節を抜けた後で:
  - `failed.txt` があれば、中身を `{"systemMessage": "ccspk の読みの点検が失敗した: …"}` で標準出力に出して消す
  - `spoken.txt` が `checked.txt` より新しい（`checked.txt` が無ければ `spoken.txt` があれば）ときだけ、
    点検の子プロセスを起こす: `[sys.executable, "-P", "-m", "ccspk.check"]`、`start_new_session=True`、
    標準入出力は DEVNULL、`cwd=STATE`
  - 同じ文を 2 度読まない（`LAST`）で return する Stop でも、この 2 つは行う（MessageDisplay が記録した分があるため）
- `CCSPK_SPEAK` が 1 でない、`UNUSABLE` がある、`unusable()` がだめ、の早い return はそのまま（点検も起こさない）
- 状態のファイルの読み書きの `OSError` でフックを落とさない
- フックに重い import を足さない（sudachipy は `check.py` だけで import する）

### 点検（新しいファイル `src/ccspk/check.py`、`python -m ccspk.check` で動く）

1. `check.lock` を `fcntl.LOCK_EX | LOCK_NB` で取る。取れなければ何もせず終わる（前の点検が走っている）
2. `spoken.txt` を読み、単語を切り出す（下の「切り出し」）。`checked.txt` の単語と、エンジンの辞書に
   登録済みの単語（`user_dict.find` と同じく NFKC で揃えて比べる）を除く
3. 残りが無ければ、`checked.txt` の mtime を更新して終わる
4. 各単語の読みを `/audio_query` の `kana` で取り、`表記<TAB>読み` の一覧にする
5. `claude -p --model sonnet --setting-sources "" --tools "" --no-session-persistence <プロンプト>` に一覧を標準入力で渡す。
   環境変数は `CCSPK_SPEAK=0` に上書きして渡す。タイムアウトは 300 秒。プロンプトは
   `archives/agents/TODO-036/prompt.txt` を元に、ファイル名・パス・16 進の ID のような単語でないものは出さない、を足す
6. 返答の各行を `表記<TAB>正しい読み` として読む。表記が渡した一覧に無い行、読みがカタカナ（`ァ-ヴー`）だけでない行は捨てる
7. 残った行を登録する（アクセントは `accent_of` に任せる、品詞・優先度は `dict add` の既定と同じ）。
   `added.tsv` に追記する
8. 渡した単語を全部 `checked.txt` に追記する（これで mtime も新しくなる）
- どこで失敗しても（例外、`claude` の終了コードが 0 でない、タイムアウト、`user_dict.call` の `sys.exit`）
  `failed.txt` に 1〜2 行で理由を書いて終わる。`checked.txt` は更新しない（次の Stop でやり直す）

### 切り出し

- 英字: `[A-Za-z][A-Za-z0-9._+-]*[A-Za-z0-9]`（1 字は除く）
- 漢字: sudachipy + sudachidict_core の `SplitMode.C`。品詞の先頭が `名詞`、漢字を含み、2 字以上
- 依存関係に `sudachipy`、`sudachidict_core` を足す（`uv add`）

### 辞書（`src/ccspk/user_dict.py`）

- `add` の中身を関数に切り出し、`dict add` と点検の両方から呼ぶ。表示（`print`）は今の `dict add` の出力を変えない
- 自動で登録した単語の見直し: `ccspk dict auto` で `added.tsv` を表示、`ccspk dict auto --remove` で
  載っている単語を全部エンジンから消し（無いものは飛ばす）、`added.tsv` を空にする。書き出し（`save()`）は最後に 1 回
- `dict remove`・`dict add`（手で）をした単語は `added.tsv` から消す（手で直したものは自動の一覧から外す）

## 保つもの

- `ccspk hook` の読み上げの挙動と、最初の音までの時間（フックに足すのは追記と Popen だけ）
- `dict add` などの既存の出力と引数
- `demo()` の既存の assert

## 完了条件

- `check.py` に `demo()` を置き、`ccspk test` から呼ぶ。少なくとも、切り出し（英字・漢字の名詞・活用形と 1 字を除く）、
  返答の行の読み取り（捨てる行）、`spoken.txt` の上限での切り詰めを assert する
- `uv run ccspk test` が通る
- `docs/UsersGuide.md` に、自動の点検の説明（何をいつ点検し、どこに何を残すか、料金の目安、止め方＝`CCSPK_SPEAK`）と
  `ccspk dict auto` の節を足す。`docs/Developer.md` に `check.py` と状態のファイルを足す。
  `docs/Developer.md` の「2. 動き方」の既存の文は TODO-035 で直すので書き換えない（足すのはよい）
- `CLAUDE.md` のコマンドの一覧に `dict auto` が要るなら足す
- 本物の `claude -p` は呼ばない（料金がかかる）。通しで試すなら、PATH の先頭に偽の `claude`（決まった行を返す
  シェルスクリプト）を置き、`XDG_STATE_HOME`・`XDG_CONFIG_HOME`・`XDG_RUNTIME_DIR` を一時ディレクトリに向ける。
  エンジンの辞書は本物なので、登録する表記は実在しない語（例: `試験用語ぬ`）にし、終わったら消す

## 報告

`archives/agents/TODO-036/implementer-report.md` に、変えたファイル、設計から変えた点と理由、試したこと（コマンドと結果）、
残る懸念。返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。コミットはしない。
