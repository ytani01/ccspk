# TODO

**残っている項目: TODO-017。** これまでに 16 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-018` から。**

---

## TODO-017. 辞書の 1 件を「語」でなく「単語」と書く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換え）+ verifier（Sonnet 5 / medium） |

- [ ] `src/` の docstring・help と `docs/`・`README.md`・`CLAUDE.md` の「語」を「単語」にする

背景（決まったこと）:

- エンジンの API の `word`（`UserDictWord`・`/user_dict_word`）の訳。「登録語」「エントリ」も
  候補に挙げたが、見出しがすでに「単語を登録する」なので「単語」に揃える
- 対象は `rg -n -P '(?<![単用言敬国英])語(?!り)' src docs README.md CLAUDE.md` で拾い、
  辞書の 1 件を指すものだけ変える（「日本語」「用語」などは変えない）
- 変えるのは文言だけ。挙動は変えないので reviewer は付けない。verifier は拾い残しと、
  `dict add --help` などの表示を確かめる。`archives/` は書き換えない

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
