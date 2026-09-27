# TODO

**残っている項目: TODO-007。** これまでに 6 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-008` から。**

---

## TODO-007. 開発者用の文書 docs/Developer.md を作る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（下書き）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] フックの仕組みを書く（`hooks/speak-response.py` の流れ、親プロセスと
      `--play` の子プロセス、PID のファイル、使えないと覚えるファイル、
      整形と分割、定数の意味）
- [ ] テストと動作の確かめ方を書く（`--test`、本物の `$XDG_RUNTIME_DIR` を
      汚さずに Stop を手で再現する手順、最初の音までの時間の測り方）
- [ ] README の「ファイル」の表から案内する

利用者と決めたこと（2026-09-28）: 開発の進め方（TODO.md・archives）と、
これまでの設計判断のまとめは書かない。README・UsersGuide と同じことを書く
所は、食い違わないよう、どちらかへの案内で済ませる。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
