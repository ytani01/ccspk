# TODO

**残っている項目: TODO-015。** これまでに 14 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-016` から。**

---

## TODO-015. サブコマンドを整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（調査・設計）+ implementer（Sonnet 5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] 今のサブコマンドとオプション、手で繰り返している作業を洗い出し、`dict` の下に
      `add` 以外を足すかを決める
- [ ] `hook --play '文'` を `say '文'` にする
- [ ] `hook --test` と `add-word --test` を `test` 1 本にまとめ、両方の自己テストを走らせる
- [ ] `add-word` を `dict add` にする
- [ ] `README.md`・`CLAUDE.md`・`docs/` のコマンド例を書き換える

背景（決まったこと）:

- 古い書き方（`add-word`、`hook --play`、`hook --test`）は別名として残さず消す
- `hook` はフック専用として残す。`settings.json` から呼ぶ形（`claudecodespeak hook`）は変えない

決めること: `dict` に `add` 以外（エンジンの辞書を `voicevox/user_dict.json` へ書き出す
`export` など）を足すか。選択肢は「足さない / `export` を足す / 調査で見つかった他の操作も
足す」。洗い出しが済んだ時点で聞く。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
