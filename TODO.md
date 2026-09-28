# TODO

**残っている項目: TODO-028、TODO-030、TODO-031。** これまでに 28 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-032` から。**

---

## TODO-028. 文書の見出しに章・節の番号を付ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換え）+ verifier（Sonnet 5.5 / medium） |

- [ ] README.md・docs/UsersGuide.md・docs/Developer.md の `##` 以下の見出しに、
      `1.`・`1.1`・`1.1.1` の形で番号を付ける（文書の題名の `#` には付けない）
- [ ] 番号でアンカーが変わるので、文書の中と文書のあいだのリンク（CLAUDE.md の「辞書のファイル」の
      ような見出し名での参照も含む）を書き換える

背景（決めたこと）:

- 対象は README.md と docs/ の 2 つ。CLAUDE.md・TODO.md・archives は変えない
- TODO-027（UsersGuide.md の書き直し）を決着させてから着手する

分担:

- 内容を変えず番号を付けるだけなので reviewer は付けない
- リンクは試せるので、verifier に確かめさせる（番号の抜けや重複が無いか、`](…#…)` の張り先の
  見出しがすべてあるか。GitHub のアンカーの作り方で見出しからアンカーを作り、スクリプトで照合する）

---

## TODO-030. 英単語と日本語の間の空白を詰める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `chunks` で切り分けた後、塊ごとに英単語と日本語の間の空白を詰める。`demo()` に例を足す
- [ ] 詰める前後の読みを `dict kana` で比べ、記録を残す
- [ ] UsersGuide.md の「記号と数字」に書き足す

背景（決めたこと）:

- 空白があると、その前後に間が入る（`reviewer の指摘` → レビュウタ'ントウ、ノ'、`同じ reviewer に` →
  オナジ'、レビュウタ'ントウ、ニ'）。詰めると間が消える
- 英→日（`reviewer の`）と日→英（`同じ reviewer`）の両方向を詰める。英単語同士（`Claude Code`）の空白は残す
- `split_first` は区切りが 30 字以内に無い文を空白で切っている（最初の音を早めるため）ので、
  `to_speech` では詰めず、`chunks` で切った後に塊ごとに詰める

---

## TODO-031. コードを直したら ccspk を自動で入れ直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `.claude/settings.json` に Stop フックを足す。`src/` か `pyproject.toml` が前回のインストールより
      新しいときだけ、`ccspk test` を走らせ、通ったら `uv tool install --reinstall .` で入れ直す
- [ ] テストが落ちたら入れ直さず、`systemMessage` で知らせる
- [ ] CLAUDE.md の「コマンド」か「注意」に、自動で入れ直すことを書く

背景（決めたこと）:

- 返答の終わりに 1 回だけ入れ直す（編集の途中の状態を入れないため）。editable インストールにはしない
- 設定は `.claude/settings.json`（リポジトリに入れる）。`.claude/settings.local.json` は変えない
- `--reinstall` を付ける見込み。hatch-vcs の版は未コミットの変更があると日付付きになり、同じ日の
  2 回目の変更では版が変わらず、`--reinstall` 無しでは入れ直さない可能性がある（UsersGuide.md も
  `--reinstall` と書いている）。着手時に確かめる

分担:

- 条件（更新の判定・テストの成否）で動きが変わるので reviewer を付ける
- verifier には、`UV_TOOL_DIR`・`UV_TOOL_BIN_DIR` を一時ディレクトリに向けて、変更なし・変更あり・
  テスト失敗の 3 通りでフックのコマンドを手で動かし、入れ直したか・知らせたかを確かめさせる

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
