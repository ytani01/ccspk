# TODO-012 reviewer 報告

対象: `git diff -- src README.md docs`（`voicevox/user_dict.json` は見ていない）。
プロジェクト直下に `CLAUDE.md` は無いため、規約は利用者全体の `CLAUDE.md` と
既存コード・`docs/Developer.md` の書き方に照らした。

要修正: 0 件 / 検討: 3 件 / 好みの範囲: 1 件

## 検討

### 1. `src/claudecodespeak/hook.py:115-120` `questions()` が壊れた入力で例外を出す

`questions()` を直接呼んで実測した（`uv run python`）。

| 入力 | 結果 |
|---|---|
| `tool_input` が文字列・リスト | `AttributeError: 'str' object has no attribute 'get'` |
| `questions` が数値 | `TypeError: 'int' object is not iterable` |
| `question` が数値・リスト | `TypeError: sequence item 0: expected str instance, int found` |
| `questions` が文字列・dict、`question` が `None` | 例外なし、`""` |

`main()` は `questions()` を `try/finally` の中で呼ぶが `except` が無いので、
`claudecodespeak hook` にそのまま渡すと終了コード 1、標準出力 0 バイト、標準エラーに
traceback が出る（`XDG_RUNTIME_DIR` を一時ディレクトリにして実測。`lock` は `finally` で閉じられる）。

- `isinstance(q, dict)` で 1 段だけ守り、`tool_input` と `questions`、`question` の型は
  守っていない。守り方が段によって揃っていない
- Claude Code の仕様では、PreToolUse で止めるのは終了コード 2 で、それ以外の 0 以外は
  止めない扱いとされている（公式ドキュメントの記述に基づく。この環境で Claude Code から
  起動しての確認はしていない）。**実害は未確認**
- Claude Code が型の違う `tool_input` を PreToolUse に渡すことがあるかも未確認。
  既存の `main()` も `payload` が dict でない JSON（`[]` など）で `payload.get` が落ちるので、
  この差分で新しく増えた性質の問題ではない。直すかどうかは管理者の判断

### 2. PreToolUse と、その直前の文章の MessageDisplay の届く順（未確認）

`docs/Developer.md:53` に「フックは並んで走り、後ろの分が先に届くこともある」とある。
質問の直前に Claude が文章を書いた場合、その文章の MessageDisplay が PreToolUse より
後に `LOCK` を取ると、`stop_playing()` で質問の読み上げが止められ、前の文章が読まれる
ことになる。利用者と決めたのは「途中の文章を読んでいる最中に質問が来たら前を止めて質問を
読む」で、逆順に届いた場合の動きは決めていない。届く順は実測していない。**実害は未確認**。
verifier に、文章＋AskUserQuestion の返答で質問が最後まで読まれるかを見させると確かめられる。

### 3. `docs/Developer.md:30-31` 「質問が複数あれば全部つないで読み」と 180 字の上限

`questions()` の結果も `to_speech()` → `clip()` を通るので、180 字（最大 240 字）で切れる。
60 字ほどの質問 4 つ（計 283 字）で試すと 212 字で切れ、4 つ目は読まれなかった（実測）。
「全部つないで読む」は利用者と決めたことどおりで、上限は同じ節の冒頭（`docs/Developer.md:13`）に
書いてあるので食い違いとまでは言えない。質問は上限を超えないことを前提にするのか、
文書で断るのかは境界線上なので報告だけ。

## 好みの範囲

### 4. `docs/Developer.md:204` 1 行が長い

足した JSON 例の行が 154 字あり、前後の段落の折り返し（90 字前後）と揃っていない。
変更前のこのファイルの最長行は 143 字。JSON を途中で折れないので、JSON だけを
コードブロックに出す手もある。

## 問題なし

- `main()` の分岐: Stop（`display`・`ask` とも偽）は `agent_id` を見ない・空でも `stop_playing()` する、の動きが変わっていない
- MessageDisplay の `agent_id` で読まない、空なら止めない、`assemble()` の流れは変わっていない
- `LAST` による 2 度読み防止は、PreToolUse も同じ条件式を通る（新しい分岐は無い）
- `tool_name` が `AskUserQuestion` 以外（matcher を付けずに登録した場合）は `""` → 空なので止めずに終わる（実測で rc=0、`claude-tts.pid` できず）
- `agent_id` 付きの PreToolUse は `LOCK` も取らずに終わる（実測で rc=0、ファイルが何もできない）
- 標準出力: 正常時も例外時も 0 バイト（実測）。`speak()` の子プロセスは stdout/stderr とも `DEVNULL` なので、フックの出力を握ったままにしない。終了コードは正常時 0 で、ツール呼び出しを止める 2 を返す経路は無い
- `docs/UsersGuide.md` の設定例は `{}` で包むと JSON として正しい（`python -m json.tool` で確認）。コマンドと timeout は既存の 2 つと同じ
- README・UsersGuide・Developer・`hook.py` の docstring の間で、読むもの（質問の文だけ、選択肢は読まない）、対象（`AskUserQuestion` だけ）、`agent_id` で読まない、空なら止めない、の主張は一致している
- `docs/Developer.md` の手順 4・6・7 はコードの順と一致している
- テスト: `demo()` の追加は、選択肢を読まない・他のツールは空・`tool_input` 無しは空、を確かめている。選択肢を読むように壊すと 1 つ目の assert が落ちる。`claudecodespeak hook --test` は `ok`
- ruff の指摘 8 件はすべて変更前からあるもの（HEAD の `hook.py` と比べた）
- 範囲: 指示に無い変更は混ざっていない

## 作り込みすぎ

作り込みすぎ: なし（`questions()` 6 行、`main()` の分岐 1 つの追加で、消せるものは見当たらない。
`tool_name` の確認は matcher と重なるが、matcher 無しで登録されたときの誤読を防ぐので残してよい）
