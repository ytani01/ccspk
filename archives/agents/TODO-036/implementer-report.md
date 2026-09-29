# TODO-036 実装の報告（implementer）

## 変えたファイル

- `src/ccspk/check.py`（新規）
  - `STATE` と状態のファイルの定数、`PROMPT`（`prompt.txt` に「ファイル名・パス・16 進の ID のように、単語でないものは出さないでください。」を足した）
  - `record()`（:40）: `SPOKEN` に追記し、`SPOKEN_MAX` を超えたら後ろ半分の行を一時ファイル経由で置き換える
  - `after_stop()`（:55）: `FAILED` を `systemMessage` で出して消す。`SPOKEN` が `CHECKED` より新しければ（`<=` なら起こさない）`python -P -m ccspk.check` を起こす
  - `extract()`（:78）: 英字は `ALPHA`、漢字は sudachipy の C 単位（名詞・漢字を含む・2 字以上）。sudachipy は関数の中で import。1 行ずつ渡す（49,149 バイトを超えると `SudachiError`）
  - `parse()`（:94）、`check()`（:107）、`main()`（:144）、`demo()`（:158）
- `src/ccspk/hook.py:31`（`from . import check`）、`:527`（`speak()` の後に `check.record(text)`）、`:531-532`（`finally` で lock を閉じた後、Stop なら `check.after_stop()`）
- `src/ccspk/user_dict.py`
  - `:115` `register()`: `add` の中身を切り出した。表示は今の `dict add` と同じ
  - `:134` `forget_auto()`: `ADDED` から表記（NFKC で比べる）の行を外す。`check` を関数の中で import（循環を避ける）
  - `:173` `add`: `register()` → `forget_auto()` → `save()` → 読みの表示（出力は前と同じ）
  - `:208` `remove`: 消した後に `forget_auto()`
  - `:219` `dict auto [--remove]`、モジュールの docstring に 1 行
- `src/ccspk/cli.py`: `test` から `check_demo()` を呼ぶ
- `pyproject.toml`・`uv.lock`: `uv add sudachipy sudachidict_core`（sudachipy 0.7.0、sudachidict-core 20260723.1）
- `docs/UsersGuide.md`: 1.3 に 1 文、「2.3 読み間違いの自動の点検」を新設、2.1・3.2・3.6・3.7・3.9・3.11 に追記、「3.12 ccspk dict auto」を新設（export・import は 3.13・3.14 へ。この 2 つへのリンクは無かった）
- `docs/Developer.md`: 冒頭の依存、1 のファイルの表、2 の最後に 1 項目を足した（既存の文は変えていない）、「3.8 自動の点検」を新設、4.1 に check の demo、4.2・4.3 の手順に `XDG_STATE_HOME` と、Stop で本物の `claude -p` が走る注意
- `CLAUDE.md` は変えていない（`dict auto` は `dict` のサブコマンドなので、冒頭の一覧に足すものは無い）

## 設計から変えた点・足した点

- `CHECKED` の mtime は、点検の始めに控えた `SPOKEN` の mtime に揃える（`os.utime`）。点検は最長 300 秒かかり、その間に足された文を点検済みと見なさないため。`after_stop()` はそのため `SPOKEN <= CHECKED` で飛ばす
- タイムアウトの `TimeoutExpired` の文にはプロンプト全文が入り 1〜2 行に収まらないので、`claude -p が 300 秒で終わらなかった` に置き換えた
- `check.py` の関数名は `record`・`after_stop`（brief に名前の指定は無かった）

## 試したこと

すべて `XDG_STATE_HOME`・`XDG_CONFIG_HOME`・`XDG_RUNTIME_DIR` をスクラッチの一時ディレクトリに向け、PATH の先頭に偽の `claude`（引数と標準入力を保存し、決まった 2 行を返す）と偽の `pw-play`（`cat >/dev/null`。音を出さない）を置いた。

| 試したこと | 結果 |
|---|---|
| `uv run ccspk test` | `ok` 3 行、終了コード 0 |
| `python -P -m ccspk.check`（`Zqxwordtest を見る。`） | 登録された（`ズクスワードテスト`）。`added.tsv` に 1 行、`checked.txt` に単語、`user_dict.json` を一時の場所へ書き出し。`checked.txt` と `spoken.txt` の mtime が一致。偽 `claude` に渡った環境変数 `CCSPK_SPEAK=0`、引数 `-p --model sonnet --setting-sources "" --tools "" --no-session-persistence <PROMPT>` |
| 偽 `claude` が一覧に無い表記（`README`。登録済みで除外された）を返す | 捨てた |
| `試験用語ぬ` | sudachipy が `試験`・`用語`・`ぬ` に割るので 1 語にならない。英字の架空語（`Zqxwordtest`・`Qzvtestword`・`Wqzfailword`）で試した |
| フック: MessageDisplay → 同じ文の Stop（5 秒以内） | MessageDisplay で `spoken.txt` に記録、`failed.txt` は残る。Stop（2 度読まない）で `{"systemMessage": "ccspk の読みの点検が失敗した: boom"}` を出し `failed.txt` を消し、点検を起こして `Qzvtestword` が `checked.txt` に入った |
| 続けて同じ Stop（新しい記録なし） | 点検を起こさない |
| `CCSPK_SPEAK=0` の Stop | `failed.txt` はそのまま（何もしない） |
| `claude` が終了コード 3 | `failed.txt`: `RuntimeError: claude -p が終了コード 3 で終わった: auth error`。`checked.txt` の mtime は変わらない |
| `claude` が無い（`PATH=/nonexistent`） | `FileNotFoundError: [Errno 2] No such file or directory: 'claude'` |
| タイムアウト（`TIMEOUT=1`、偽 `claude` が `sleep 5`） | `RuntimeError: claude -p が 1 秒で終わらなかった` |
| エンジンに届かない（`ENGINE` を `:1` に） | `エンジン（http://127.0.0.1:1）とやり取りできない: [Errno 111] Connection refused` |
| `check.lock` を別プロセスが持っている | 終了コード 0、`failed.txt` も `checked.txt` の追記も無し |
| `dict add Zqxwordtest …`（手で） | `added.tsv` から外れた |
| `dict auto --remove`（登録済み 1・無い 1） | 1 つ消し、もう 1 つは「登録されていない（飛ばした）」。`added.tsv` は 0 バイト、書き出し 1 回 |
| `dict remove Zqxwordtest`（`added.tsv` は全角の `Ｚｑｘｗｏｒｄｔｅｓｔ`） | NFKC で一致して外れ、ほかの行は残った |
| 後片付け | `ccspk dict export` と本物の `~/.config/ccspk/user_dict.json` が一致（`diff` の差分なし） |
| `ruff check src/ccspk/check.py` | 指摘なし。ほかのファイルの指摘は前からあるもの（`user_dict.py` の C408 は、移した行が前からあったもの） |
| `archives/agents/TODO-028/check_anchors.py` | リンク 35 件すべて OK。NG は前からある 1 件（UsersGuide の「ファイル」） |

本物の `claude -p` は呼んでいない。

## 判断が要る点・範囲外で気づいたこと

1. **このリポジトリの Stop フック（`.claude/settings.json`）が、次の返答の終わりに `ccspk` を入れ直す。** 入れ直した時点から本物のフックが `~/.local/state/ccspk/` に記録を始め、次の Stop から本物の `claude -p` が走る（料金がかかる）。コミット前に動き始めてよいか
2. `CLAUDE.md` の注意「フックを手で動かすときは、本物の `$XDG_RUNTIME_DIR` を使わない」に、`XDG_STATE_HOME` と「Stop で本物の `claude -p` が走る」を足したほうがよい（`CLAUDE.md` は触っていない。Developer.md の 4.2 には書いた）
3. 点検だけを止める手段は無い（止めるのは `CCSPK_SPEAK` だけ、は brief どおり）。4.3 の最初の音を測る手順も、Stop なので 1 回ごとに点検を起こす（`最初` などを本物の `claude -p` に渡す）
4. 点検の失敗が続くと（`claude` が無い、認証切れ）、Stop のたびに点検を起こして失敗し、毎回 `systemMessage` が出る
5. 返答の読みがエンジンの読み（' と _ を除く）と同じでも登録する。捨てるかは brief に無いので入れていない
6. `checked.txt` は上限なしで伸びる（単語は重ならないので伸びは遅い）
7. 点検を起こした `claude -p` が走っている最中に 300 秒のタイムアウトで殺すのは `claude` 本体だけ（孫プロセスは見ていない。`--tools ""` なので起こさないはず。未確認）
8. 点検の子プロセスには loguru の DEBUG が標準エラーに出るが、捨てている（`loggerInit` を通さないため）
