# TODO

**残っている項目: TODO-008。** これまでに 7 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-009` から。**

---

## TODO-008. 「動き方」の詳細を Developer.md へ移す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（移す）+ reviewer（Opus 5.5 / high） |

- [ ] README の「動き方」の細かい決まり（読み上げる範囲、1 文目の切り方、
      読み間違いの直し方、使えないと覚える条件など）を `docs/Developer.md` へ移す
- [ ] README の「動き方」は、特徴の概要（5〜6 行の箇条書き）と、
      Developer.md・UsersGuide への案内だけにする
- [ ] Developer.md・UsersGuide から README の「動き方」へ張っているリンクを直す

利用者の指示（2026-09-28）: 詳細は Developer.md に、README は特徴の概要だけ。

書いたとおりに試せるコマンドは増えないので verifier は置かない。移す元が
今のコードと合っているか、移して抜けが無いかを reviewer に見させる。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
