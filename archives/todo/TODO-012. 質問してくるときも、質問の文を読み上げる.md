# TODO-012. 質問してくるときも、質問の文を読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 14,943 | 65,675 | 68% |
| reviewer | Opus 5.5 | high | 3,204 | 44,468 | 21% |
| verifier | Sonnet 5 | medium | 2,601 | 40,750 | 11% |
| 合計 |  |  | 20,748 | 150,893 | 概算 $2.4 |

- 立ててから着手まで TODO-011 を挟んだので、`--since '2026-09-28 10:03:00'` で集計した
- 担当のモデル・effort は `~/.claude/agents/` の定義のまま（reviewer は opus / high、verifier は sonnet / medium）

## きっかけ

`AskUserQuestion` で質問してくるとき、画面を見ていないと質問に気付かない。

利用者と決めたこと（2026-09-28）: 読むのは質問の文だけで、選択肢は読まない。質問が複数あれば
全部つないで読む。途中の文章を読んでいる最中に来たら、今までどおり前を止めて質問を読む。
読むのは `AskUserQuestion` だけで、`ExitPlanMode` や許可待ちは読まない。
サブエージェント（`agent_id` あり）は読まない。

## やったこと

- `src/claudecodespeak/hook.py`: `PreToolUse` を受ける。`questions()` で
  `tool_input.questions[].question` を改行でつなぐ。`tool_name` が `AskUserQuestion` でないとき、
  入力が壊れているときは空を返す。空なら前の再生を止めずに終わる（`MessageDisplay` と同じ扱い）。
  `agent_id` があれば読まない。`demo()` に例を足した
- `docs/UsersGuide.md`: フックの設定例に `PreToolUse`（matcher `AskUserQuestion`）を足した
- `docs/Developer.md`: 動き方・流れ・自己テスト・手で試す手順を直した
- `README.md`: `hook.py` の説明と「動き方」に質問の読み上げを足した

## 確かめたこと

- reviewer: 要修正は 0 件。`tool_input` が文字列のときなどに `questions()` が例外を出す、
  という指摘を受けて、型を確かめるよう直し、`demo()` に例を 2 件足した
- verifier: 8 項目すべて仕様どおり（`--test`、選択肢を読むように壊すと落ちること、
  質問 2 つをつないで `LAST` に書くこと、`agent_id`・`Bash`・壊れた入力では何もしないこと、
  Stop と MessageDisplay のリグレッション、UsersGuide の設定例が JSON として読めること）
- main: verifier がやらなかった「`tool_name` の確認を外す」壊し方で `--test` が落ち、
  戻すと通ることを確かめた

詳細は `archives/agents/TODO-012/` の報告にある。

## 残ること

- 直前の文章の `MessageDisplay` が `PreToolUse` より後に届くと、質問の読み上げが止まり、
  直前の文章が読まれる。届く順はまだ測っていない（reviewer の指摘）
- 質問を全部つなぐと、180 字の上限（`LIMIT`）で後ろの質問が切れることがある。上限はそのままにした
- 実際に鳴らすには、`uv tool install` で入れ直し、`~/.claude/settings.json` に `PreToolUse` の
  フックを足す必要がある（利用者の手元の設定なので、ここでは触っていない）

## 分担の振り返り

- reviewer は、壊れた入力での例外と、届く順の問題と、字数の上限で切れる件を見つけた。
  1 つ目で実装が変わったので、reviewer を先に回したのが効いた
- verifier は、仕様どおりであることを値付きで示した。壊し方は 2 つ頼んだうち 1 つしか
  試さなかったので、main が残りを試した。見込みとの食い違いは無い
- 次に同じ規模（1 関数と文書 3 つ）なら同じ組み方でよい。ただし verifier への依頼で、
  壊し方は「各 1 回、全部」と書いて、試し漏れを防ぐ。reviewer が料金の 2 割を使ったので、
  分岐が 1 つ増えるだけの変更なら、reviewer の effort を medium に下げて試す
