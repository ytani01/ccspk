# TODO

**残っている項目: TODO-013。** これまでに 12 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-014` から。**

---

## TODO-013. Developer.md の定数の表を hook.py に合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書の修正）+ verifier（Sonnet 5 / medium） |

- [ ] 表に `MODULE`、`PARTS_KEEP`、`SAME_WITHIN` を足す
- [ ] `PLAY` の行を直す（`stop_playing()` は `--play` と `MODULE` の両方で見分ける。`hook.py:144`）

wording で推敲したときに見つかった（2026-09-28）。表の定数は
`src/claudecodespeak/hook.py` の 32〜47 行目と同じ。`PARTS_KEEP`（59 行目）と
`SAME_WITHIN`（62 行目）は「流れ」の本文には出てくるが、表には無い。
パスの定数（`PIDFILE`、`LOCK` など）は「ファイル」の表にあるので、この表には足さない。

verifier には、表の各行を `hook.py` の値・コメントと突き合わせさせる
（書いたとおりに確かめられるものがあるので main が確認しない）。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
