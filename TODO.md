# TODO

**残っている項目: TODO-014。** これまでに 13 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-015` から。**

---

## TODO-014. CLAUDE.md の仕組みの説明を Developer.md へ移し、文書の重複を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書の修正）+ reviewer（Opus 5.5 / high） |

- [ ] CLAUDE.md の「仕組み」の節を消し、Developer.md を参照する 1 行にする
- [ ] 「エンジンと話者は `hook.py` と `add_word.py` で揃える」を Developer.md の「定数」へ移す
- [ ] 「個別に走らせる手段は無い」「lint の設定は無い」を Developer.md の「自己テスト」へ移す。CLAUDE.md にはコマンドの一覧だけ残す
- [ ] CLAUDE.md の「手で確かめるとき」「辞書」「TODO」を、注意 1 行と参照に縮める
- [ ] 見出しを直し、リンクのアンカーも合わせる
  - Developer.md「使えないと覚える」→「鳴らせるかを確かめる」
  - Developer.md「Stop を手で再現する」→「フックを手で動かす」
  - UsersGuide.md「使えないと覚えたとき」→「読み上げが止まったままのとき」
  - UsersGuide.md「戻す」→「リポジトリから読み込む」

利用者の指摘（2026-09-28）: CLAUDE.md に仕組みの話が多い。Developer.md に書くことは
Developer.md へ移し、重複はどちらを正とするか決め、見出しも自然な日本語にする。

正とする文書は次のとおり決めた。CLAUDE.md は毎回読まれるので、Claude が守る注意と
コマンドの一覧だけを残し、説明は参照先に任せる。

| 内容 | 正 |
|---|---|
| フックの流れ、子プロセス、状態のファイル、鳴らせない環境 | Developer.md |
| テストの走らせ方と、手で確かめる手順 | Developer.md |
| 辞書を書き出してコミットする手順 | UsersGuide.md |
| TODO の旧番号 | README.md |

README・Developer・UsersGuide の間の重複は、README が要約で詳細へリンクする形で
食い違いも無いので直さない。

reviewer には、移した説明が `hook.py`・`add_word.py` と合っているか、同じ説明が
2 か所に残っていないか、見出しを変えたあとアンカーが切れていないか
（`rg -n '使えないと覚え|Stop を手で|#戻す' -g '*.md' -g '!archives/**'`）を見させる。
TODO-013 も Developer.md の「定数」の節を触るので、先に済んだほうに合わせる。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
