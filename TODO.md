# TODO

**残っている項目: TODO-020。** これまでに 19 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-021` から。**

---

## TODO-020. dict add の優先度の既定を 7 にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `dict add` で新しい単語を登録するとき、`--priority` を省くと 7 にする
  （`src/claudecodespeak/user_dict.py` の `add`。今はエンジンの既定 5 に任せている）
- [ ] `--priority` の help と `docs/UsersGuide.md` の優先度の説明を直す

登録済みの単語は変えない（書き換えで `--priority` を省いたときは今の優先度のまま、も変えない）。
`dict add` で足す単語は、エンジン標準の読みより優先させたいもの、と見なす。
7 は「節」「語」「sh」で実際に効いた値。「節」「語」を 7 にしても
「物語」「単語」「英語」「季節」「調節」の読みは崩れなかった（2026-09-29 に確かめた）。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
