# TODO

**残っている項目: TODO-016。** これまでに 15 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-017` から。**

---

## TODO-016. dict add に --priority を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `dict add` に `--priority N`（0〜10）を足す
- [ ] `docs/UsersGuide.md` の `dict add` の説明に、優先度の意味と使いどころを書く

背景（決まったこと）:

- 「節」をセツで登録しても、優先度 5 ではエンジン標準の「フシ」に負けた。`curl` で 7 に
  上げてセツになった（`88ef11d`）。`add-word` には優先度を渡す手段が無かった
- 省いたときは `--type` と同じ扱いにする。新しい語はエンジンの既定（5）、登録済みの語は今の優先度のまま
- TODO-015 で `add-word` が `dict add` になってから着手する

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
