# TODO

**残っている項目: TODO-039、TODO-041、TODO-043。** これまでに 40 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-044` から。**

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

## TODO-041. 文書の言い回しを直し、mermaid の図を入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換えと書き足し）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `docs/Developer.md` の「3.1 流れ」に、`main()` の 10 段の進み方と、途中で終わる分岐を `flowchart` で入れる
- [ ] `docs/Developer.md` の「3.2 子プロセス」に、フック → 子プロセス → `claude -p`（要約）→ エンジン → `pw-play` の
  やり取りを `sequenceDiagram` で入れる
- [ ] `docs/Developer.md` の「3.8 自動の点検」に、Stop → `after_stop()` → 点検の起動 → 読みの取得 → `claude -p` →
  辞書に登録、の流れを図で入れる
- [ ] `docs/UsersGuide.md` の冒頭に、Claude Code・`ccspk`・VOICEVOX エンジン・PipeWire のつながりを 1 枚の構成図で入れる
- [ ] `docs/Developer.md` の「2. 動き方」で、「1 文目ができたらすぐ鳴らす」（31 行目）と
  「1 文目の前半ができたらすぐ鳴らす」（33 行目）が食い違って見える。1 つにまとめる。
  同じ項目の終わりの「切った所は抑揚が文末のように下がる」「最初の音までは…1.2〜2.5 秒ほど」は、
  切り方の決まりと別の話なので分ける
- [ ] 同じ節の「`Stop` が空のときは、今までどおり止める」は、変える前の動きを指す言い方なので、
  今の動き（前の再生を止める）で書く
- [ ] `docs/UsersGuide.md` の「1.2 Claude Code の設定」の「`ccspk` をインストールしていないマシンでは
  何もしない」は、何が何もしないのかが分からない。フックのコマンドの話だと分かるように書く
- [ ] `docs/UsersGuide.md` の「3.3 ccspk say」の「鳴らし終わってから終わる」を、「終わる」が
  重ならない言い方にする

背景（2026-09-29 に利用者と決めた）:

- 文書の説明に mermaid の図を入れる規則を `~/.claude/CLAUDE.md` の「日本語の書き方」に足した。この項目はその規則を
  今ある文書に当てはめるもの
- 図は文章の補いで、文章は消さない。図が文章・コードと食い違わないことを reviewer に見させる
  （書き写しでなくコードとの突き合わせ）
- verifier には、各図が mermaid として描けるか（`npx -p @mermaid-js/mermaid-cli mmdc` で SVG にして、エラーが出ないか・
  描けた図に抜けや余計な箱が無いか）を確かめさせる。図の良し悪しは評価させない
- 言い回しの 4 つは TODO-035 から移した（同じ 2 つの文書を触るので、reviewer を 1 回にまとめる）。TODO-034 と同じとき
  （2026-09-29）に見つけたもので、README.md と CLAUDE.md には直すところが無かった。意味を変えない書き換えなので、
  reviewer にはこの分について、書き換えの前後で意味が変わっていないかを見させる
- 言い回しを先に直し、図はその後の文章と食い違わないように描く

---

## TODO-043. 話者を切り替えるコマンドを足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ccspk speaker 3` で話者を番号で決める。`ccspk speaker 夜語トバリ 明るい` のように名前とスタイルでも選べる
  （スタイルを省いたら、その話者の最初のスタイル）。引数なしの `ccspk speaker` は今の話者を番号・名前・スタイルで表示する
- [ ] `ccspk speaker --list` でエンジンの話者を番号・名前・スタイルで一覧する
- [ ] 値は `~/.config/ccspk/` のファイルに残し、次の読み上げから効く。ファイルが無いときは今までどおり 119。
  エンジンの `/speakers` に無い番号・名前は断る
- [ ] `hook.py` と `user_dict.py` に 2 つある `SPEAKER` を 1 つにまとめ、フックの読み上げ・`ccspk say`・`dict add --speak`・
  読み間違いの点検の `audio_query` のすべてに効かせる
- [ ] `demo()` に例を足し、`docs/UsersGuide.md`・`docs/Developer.md` に書く

背景（2026-09-29 に利用者と決めた）:

- 今は話者が `SPEAKER = 119`（夜語トバリ・明るい）の定数で、変えるにはコードを直して入れ直すしかない
- 名前で選べるようにし、一覧も付ける
- TODO-039（音量）と同じく `~/.config/ccspk/` のファイルに残す形なので、TODO-039 と書き方を揃える。どちらか先に済んだほうに合わせる
- 環境変数での上書きは付けない（TODO-039 と同じ理由）

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
