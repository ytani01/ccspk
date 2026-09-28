# TODO

**残っている項目: TODO-023。** これまでに 25 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-027` から。**

---

## TODO-023. 文書を読む人ごとに整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き直し）+ reviewer（Opus 5.5 / high） |

- [ ] `README.md` を、特徴と主な機能の概要にまとめる（初めて見る人向け）
- [ ] `README.md` の「ファイル」の表を `docs/Developer.md` へ移す。`docs/Developer.md` の
  「ファイル」（実行時のファイルの表）と名前がぶつかるので、どちらかの見出しを変える
- [ ] `README.md` の「TODO の番号」を、開発者向けとして `docs/Developer.md` へ移す
  （`CLAUDE.md` からの参照先も直す）
- [ ] 残りの節を読む人で振り分ける。使う人向けは `docs/UsersGuide.md`、手を入れる人向けは
  `docs/Developer.md`、Claude 向けの注意は `CLAUDE.md`。同じ説明が 2 か所にあれば 1 か所にして、
  もう片方からはリンクする（今は「動き方」が `README.md` と `docs/Developer.md` の両方にある）

TODO-021・TODO-022 のあとにやる（どちらも `README.md` と `docs/` の同じ節を書き換えるため）。
文書を移す項目なので reviewer を付け、移す元が今のコードと合っているか、同じ説明が
2 か所に残っていないか、リンクが切れていないかを見させる。コマンドの例は書き換えないので
verifier は置かない（書き換えることになったら、その再現は verifier に分ける）。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
