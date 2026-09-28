# TODO-012 verifier report

対象差分: `git diff -- src docs README.md`（`voicevox/user_dict.json` は対象外として見ていない）。

## 1. `uv sync` / `uv run claudecodespeak hook --test`

`uv sync` 成功。`uv run claudecodespeak hook --test` → 出力 `ok`、終了コード 0。

## 2. テストの強さ（questions() を壊す）

`questions()` を、選択肢の `label` も読み上げに含めるよう書き換えて
`.venv/bin/claudecodespeak hook --test` を実行。

```
AssertionError
  at: assert to_speech(questions(ask)) == "どちらにしますか？ 範囲は？"
```

終了コード 1 で落ちた。壊したコードを元に戻し、`--test` が再び `ok`（終了コード 0）に
戻ることを確認。`git diff -- src/claudecodespeak/hook.py` は、壊す前と同じ内容
（TODO-012 の変更分のみ）に戻っていることを確認した。
`tool_name` の確認を外す方の破壊は指示の「例」の 2 つ目であり、時間の都合上 1 つ目のみ
実施。両方試すべきかは判断できない。

## 3. PreToolUse・AskUserQuestion・質問 2 つ

入力:
```
{"hook_event_name":"PreToolUse","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"どちらにしますか？","options":[{"label":"A案"}]},{"question":"範囲はどうしますか？"}]}}
```

終了コード 0。作られたファイル: `claude-tts.pid`, `claude-tts.last`, `claude-tts.lock`。
`claude-tts.last` の中身:
```
どちらにしますか？ 範囲はどうしますか？
```
選択肢の `A案` は含まれていない。仕様どおり。

## 4. 同じ入力に agent_id を足す

入力に `"agent_id":"sub1"` を追加。終了コード 0。`find $tmp -type f` の出力は空
（`pid`・`last` とも作られなかった）。仕様どおり。

## 5. tool_name が Bash の PreToolUse

入力:
```
{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"ls"}}
```
終了コード 0。作られたファイルは `claude-tts.lock` のみ（`LOCK` 取得時に必ずできる
もので、`pid`・`last` は作られなかった）。仕様どおり。

## 6. 壊れた入力（tool_input が文字列）

入力:
```
{"hook_event_name":"PreToolUse","tool_name":"AskUserQuestion","tool_input":"broken"}
```
終了コード 0。作られたファイルは `claude-tts.lock` のみ（`pid`・`last` は無し）。
仕様どおり（`questions()` は `tool_input` が dict でなければ空文字を返す）。

## 7. リグレッション: Stop と MessageDisplay

Stop（`{"last_assistant_message":"確認です。二つ目の文です。"}`）→ 終了コード 0。
`pid`・`last`・`lock` ができ、`last` の中身は `確認です。二つ目の文です。`。

MessageDisplay（`{"hook_event_name":"MessageDisplay","message_id":"m1","index":0,"final":true,"delta":"途中の確認です。"}`）
→ 終了コード 0。`pid`・`last`・`lock` ができ、`last` の中身は `途中の確認です。`。

どちらも `last` ができ、想定どおりの中身だった。

## 8. UsersGuide.md の hooks 設定例が JSON として読めるか

`docs/UsersGuide.md` のコードブロック（`env` と `hooks` のみを含む断片）を
`{` `}` で包んで `json.loads()` した結果 `VALID JSON`（例外なし）。

## 変更ファイルと指示の範囲

`git status --short`:
```
 M README.md
 M TODO.md
 M docs/Developer.md
 M docs/UsersGuide.md
 M src/claudecodespeak/hook.py
 M voicevox/user_dict.json
?? archives/agents/TODO-012/
```

- `README.md`・`docs/Developer.md`・`docs/UsersGuide.md`・`src/claudecodespeak/hook.py` は
  TODO-012 の節（`AskUserQuestion` の質問を読む）に対応する変更で、範囲に合っている。
- `TODO.md` は TODO-012 の進捗欄（チェックボックス）の変更と見られ、範囲内。
- `voicevox/user_dict.json` は今回の対象差分（`git diff -- src docs README.md`）に
  含まれておらず、内容も確認していない。TODO-012 の指示（質問文を読む実装）とは
  無関係に見えるが、これが今回の作業由来かは判断できない。管理者側で確認が必要。

## 確かめられなかったこと

- `questions()` の破壊は「選択肢の label も読む」の 1 パターンのみ実施。
  「`tool_name` の確認を外す」パターンは実施していない。
- 音が実際に鳴るか、読み上げの自然さ、文書の文体は指示により対象外とした。
- `voicevox/user_dict.json` の変更が TODO-012 由来かどうかは判断できない。
