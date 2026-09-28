# TODO

**残っている項目: TODO-019。** これまでに 18 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-020` から。**

---

## TODO-019. dict list に優先度を表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `dict list` の各行の末尾に優先度を足す（`src/claudecodespeak/user_dict.py` の `list_`）
- [ ] `list_` の docstring と `docs/UsersGuide.md` の「`dict list` は ID・表記・読み・
  `accent_type` を…」を合わせて直す

エンジンの `GET /user_dict` は各単語の `priority` を返しているが、`dict list` は
表示していない。既定の 5 のままか、上げた単語（「節」「語」は 7）かを一覧で
見分けられるようにする。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
