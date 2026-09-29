# TODO

**残っている項目: TODO-048、TODO-057、TODO-058。** これまでに 55 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-059` から。**

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

## TODO-057. CLAUDE.md の ccspk test の説明に check を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | main のみ |

- [ ] `CLAUDE.md` の「コマンド」の `uv run ccspk test` のコメントを「hook・dict・check の自己テスト（demo() の assert）」にする

背景（2026-09-30。`/claude-api prompt-audit` で見つかった）:

- `src/ccspk/cli.py` の `test` は `hook_demo()`・`dict_demo()`・`check_demo()` の 3 つを走らせるが、`CLAUDE.md` には hook・dict しか書いていない
- 定義ファイルの文だけを直す項目で、確かめることは `cli.py` と合っているかだけなので、確認は main が行う

---

## TODO-058. 要約・翻訳の claude -p の effort を下げると速くなるか測る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | 測定: verifier（Sonnet 5.5 / medium）。変えるなら main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] verifier が、`rewrite()` と同じ引数の `claude -p` で、`--effort` 無し（既定の `high`）・`--effort medium`・`--effort low` の 3 つを比べる。
  要約 3 件（短い・中くらい・長い返答）と翻訳 1〜2 件を、それぞれの設定で 1 回ずつ。見るのは `time` の実時間と出力の中身
  （頼みごと・決めることが抜けていないか、`KANA_NOTE` のひらがな化が守られているか、訳の抜け）。
  あわせて、`--effort` を付けない `claude -p` の起動だけにかかる時間の目安も 1 回測る（effort で縮まない分を見るため）
- [ ] 結果を見て、変えるかどうかを利用者と決める
- [ ] 変えるなら: `rewrite()` の `claude -p` に `--effort <決めた値>` を足す。`demo()` の偽の `claude`（`hook.py` の `"$1 $3"` と `"$9"`）は
  引数の位置で確かめているので合わせて直す。`docs/Developer.md`（3.2 の `rewrite()` の手順 1）と `docs/UsersGuide.md`（要約・翻訳の
  遅れの秒数とトークン量）も直す

背景（2026-09-30。`/claude-api prompt-audit` の flag から）:

- `hook.py:310` の `claude -p --model sonnet` は `--effort` を付けていないので、Sonnet 5.5 の既定の `high` で動く。
  `claude --help` に `--effort <level>`（low〜max）がある
- 要約と翻訳の両方を対象にする（同じ `rewrite()` から呼ぶので、引数 1 か所で両方に効く。利用者と決めた）
- `hook.py:80` の「要約は Sonnet で 5〜6 秒だった」と `docs/UsersGuide.md` の秒数・トークン量は、どのモデルで測ったか書いていない。
  測定の既定の側の値で、今の値として確かめる
- 測る材料は、`~/.claude/projects/` の会話ログから利用者の返答を取る。本物の `$XDG_RUNTIME_DIR`・`$XDG_STATE_HOME` は使わない
  （`CLAUDE.md` の「注意」）。本物の `claude -p` を 15 回ほど呼ぶので料金が少しかかる
- 決めること: effort を下げるか、下げるなら `medium` か `low` か。測定の結果が出た後に聞く。速さの差が小さい、または品質が落ちるなら変えない

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
