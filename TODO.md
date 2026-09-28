# TODO

**残っている項目: TODO-020・TODO-023。** これまでに 23 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-026` から。**

---

## TODO-020. dict add の優先度の既定を 7 にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `dict add` で新しい単語を登録するとき、`--priority` を省くと 7 にする
  （`src/ccspk/user_dict.py` の `add`。今はエンジンの既定 5 に任せている）
- [ ] `--priority` の help と `docs/UsersGuide.md` の優先度の説明を直す

登録済みの単語は変えない（書き換えで `--priority` を省いたときは今の優先度のまま、も変えない）。
`dict add` で足す単語は、エンジン標準の読みより優先させたいもの、と見なす。
7 は「節」「語」「sh」で実際に効いた値。「節」「語」を 7 にしても
「物語」「単語」「英語」「季節」「調節」の読みは崩れなかった（2026-09-29 に確かめた）。

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
