# TODO

**残っている項目: TODO-012。** これまでに 11 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-013` から。**

---

## TODO-012. 質問してくるときも、質問の文を読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `AskUserQuestion` を呼ぶ直前（`PreToolUse`、matcher `AskUserQuestion`）に、
      `tool_input` の `questions[].question` を読み上げる。選択肢は読まない
- [ ] UsersGuide のフックの設定例に `PreToolUse` を足す
- [ ] Developer.md の動き方の説明を直す

利用者と決めたこと（2026-09-28）: 読むのは質問の文だけ。TODO-011 が済んでから着手する
（入れたコマンドの形で足す）。質問が複数あれば全部つないで読む。途中の文章を読んでいる
最中に来たら、今までどおり前を止めて質問を読む。読むのは `AskUserQuestion` だけで、
`ExitPlanMode` や許可待ちは読まない。サブエージェント（`agent_id` あり）は読まない。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
