# TODO

**残っている項目: TODO-039、TODO-048。** これまでに 48 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-051` から。**

---

## TODO-039. 読み上げの音量を設定する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ccspk volume 0.6` で読み上げの音量を決める。引数なしの `ccspk volume` は今の値を表示する。
  値は `~/.config/ccspk/` のファイルに残し、次の読み上げから効く。範囲の外や数でない値は断る
- [ ] `play()` の `pw-play` に `--volume` を渡す。ファイルが無いときは今までどおり（1.0）。
  フックの読み上げと `ccspk say` の両方に効く
- [ ] `demo()` に例を足し、`docs/UsersGuide.md`・`docs/Developer.md` に書く

背景（2026-09-29 に利用者と決めた）:

- システムの音量とは別に、読み上げの音量だけを決めたい。`pw-play --volume`（0〜1.0）を使う
- 見送った案: PipeWire のミキサー（pavucontrol など）でアプリごとの音量として調整する案（`pw-play -P` で
  `application.name` を付ける）。コマンドで変えたいので採らない。VOICEVOX の `volumeScale` は `--volume` と効果が
  ほぼ同じなので採らない
- 環境変数での上書きは付けない。`ccspk summary`（TODO-037）と違い、一時的に切り替えるものではないため
- `ccspk summary` と同じ形にするので、TODO-037 が済んでから着手する

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

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
