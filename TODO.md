# TODO

**残っている項目: TODO-048、TODO-055。** これまでに 53 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-056` から。**

---

## TODO-048. 公開用のリポジトリを分け、履歴と TODO を見せずに公開する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（スクリプト・`.gitattributes`・文書）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `.gitattributes` の `export-ignore` で、公開しないもの（`TODO.md`・`archives/`・`.claude/`・`CLAUDE.md`）を指定する
- [ ] 公開用のリポジトリへ写すスクリプトを置く。`git archive` で今のタグの中身を書き出し、公開用の作業コピーに
  1 コミットとして入れ、同じタグを付ける。push はしない（利用者が行う）
- [ ] 公開するファイル（README.md・`docs/`・`src/` など）から、`TODO-NNN` の参照や `docs/Developer.md` の「5. TODO の番号」など、
  公開しないものを指す記述を除くか書き直す
- [ ] 手順（GitHub での非公開化・改名・新しいリポジトリの作成、写し方）を `docs/Developer.md` に書く

背景（2026-09-29 に利用者と決めた）:

- 外に見せたいが、細かい履歴・TODO・サブエージェントの報告は見せたくない。自分用には今のまま要る
- 今の `github.com/ytani01/ccspk` は PUBLIC。private にして `ccspk-dev` に改名し、`ccspk` の名前で公開用を新しく作る。
  GitHub の操作（非公開化・改名・作成）は外に出る操作なので、利用者が行うか、その都度確かめてから行う
- 公開側には `CLAUDE.md` も含めない（自分の作業の規則なので）
- 写すのは利用者が好きなときに手でスクリプトを走らせる。リリースのたびに自動では写さない
- 見送った案: `git filter-repo` で今の履歴を書き換える案は、自分用の履歴まで消えるので採らない。同じリポジトリで公開用の
  ブランチだけ分ける案は、GitHub では全ブランチが見えるので採らない
- 公開側の版とタグは、写したときのタグに揃える（`hatch-vcs` が版を決めるため、公開側にもタグが要る）
- verifier には、スクリプトで一時ディレクトリの公開用リポジトリへ写させ、除いたファイルが無いこと、写した中身から
  `uv tool install` と `ccspk test` が通ること、版がタグと合うことを確かめさせる

---

## TODO-055. rewrite() の claude -p の止まり方の説明を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | main（文書）+ verifier（Sonnet 5.5 / medium） |

- [ ] `docs/Developer.md` の「3.2 子プロセス」で TODO-054 に足した段落の「`CCSPK_SPEAK=0` は念のためで、これだけでは止まらない」を直す。
  この `claude -p` は `--setting-sources ""` で `settings.json` を読まないので、`0` はそのまま届く。効かないのは
  `settings.json` を読む `claude -p` の場合だけ、と分けて書く
- [ ] その段落を `rewrite()` の手順 1 の途中（「`stop_playing()` で一緒に止まる」と「終了コードが 0 なら」の間）から、
  番号付きの手順の後ろへ独立した段落として移す（「点検の `claude -p`（`check.py`）も同じ」は手順と関係ないため）
- [ ] verifier は、`CCSPK_SPEAK=0 claude -p --setting-sources "" …` の子プロセスで `printenv CCSPK_SPEAK` が `0` になることを
  1 回実測し、移した前後で手順 1〜5 の文が欠けたり重なったりしていないことを `git diff` で確かめる

背景（2026-09-30。TODO-054 の決着後に、利用者が別に取ったレビューで指摘された）:

- 手順 1 の途中に入れたので流れが切れ、「これだけでは」がこの `claude -p` のことに読める
- `docs/UsersGuide.md` の追記は問題ないので変えない

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
