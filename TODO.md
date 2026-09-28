# TODO

**残っている項目: TODO-020・TODO-021・TODO-023・TODO-025。** これまでに 21 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-026` から。**

---

## TODO-020. dict add の優先度の既定を 7 にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `dict add` で新しい単語を登録するとき、`--priority` を省くと 7 にする
  （`src/ccspk/user_dict.py` の `add`。今はエンジンの既定 5 に任せている）
- [ ] `--priority` の help と `docs/UsersGuide.md` の優先度の説明を直す

登録済みの単語は変えない（書き換えで `--priority` を省いたときは今の優先度のまま、も変えない）。
`dict add` で足す単語は、エンジン標準の読みより優先させたいもの、と見なす。
7 は「節」「語」「sh」で実際に効いた値。「節」「語」を 7 にしても
「物語」「単語」「英語」「季節」「調節」の読みは崩れなかった（2026-09-29 に確かめた）。

---

## TODO-021. 辞書を ~/.config に置き、エンジンの起動時に読み込む

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] 辞書のファイルを `~/.config/ccspk/user_dict.json` とする
  （`$XDG_CONFIG_HOME` があればそちらを使う）
- [ ] `dict add`・`remove`・`import` が成功したら、エンジンの辞書をこのファイルへ書き出す
  （`export` と同じ形。一時ファイルに書いてから置き換える）
- [ ] `systemd/voicevox-engine.service` に `ExecStartPost` を足す。エンジンが応答するまで待ち、
  ファイルがあれば `dict import` する。失敗してもエンジンは止めない
- [ ] `voicevox/user_dict.json` をリポジトリから外す。消す前に中身を `~/.config` へ移す
- [ ] `docs/UsersGuide.md` の「辞書をリポジトリに保存する」「リポジトリの辞書を読み込む」と、
  `CLAUDE.md` の `dict export` の注意を書き直す

エンジンは辞書を `~/.local/share/voicevox-engine/user_dict.json` に持っていて、再起動では
消えない。それを直接使わず `~/.config` に別に持つのは、エンジンの版や入れ直しに左右されず、
表記も半角で読めるようにするため（利用者が決めた。2026-09-29）。
`import` は上書きと追加だけをする。ファイルに無い単語がエンジンにあっても消さない（今と同じ）。
TODO-022 の改名を先にやる（パスが `~/.config/ccspk/` になるため）。

---

## TODO-023. 文書を読む人ごとに整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き直し）+ reviewer（Opus 5.5 / high） |

- [ ] `README.md` を、特徴と主な機能の概要にまとめる（初めて見る人向け）
- [ ] `README.md` の「ファイル」の表を `docs/Developer.md` へ移す。`docs/Developer.md` の
  「ファイル」（実行時のファイルの表）と名前がぶつかるので、どちらかの見出しを変える
- [ ] `README.md` の「TODO の番号」を、開発者向けとして `docs/Developer.md` へ移す
  （`CLAUDE.md` からの参照先も直す）
- [ ] 残りの節を読む人で振り分ける。使う人向けは `docs/UsersGuide.md`、手を入れる人向けは
  `docs/Developer.md`、Claude 向けの注意は `CLAUDE.md`。同じ説明が 2 か所にあれば 1 か所にして、
  もう片方からはリンクする（今は「動き方」が `README.md` と `docs/Developer.md` の両方にある）

TODO-021・TODO-022 のあとにやる（どちらも `README.md` と `docs/` の同じ節を書き換えるため）。
文書を移す項目なので reviewer を付け、移す元が今のコードと合っているか、同じ説明が
2 か所に残っていないか、リンクが切れていないかを見させる。コマンドの例は書き換えないので
verifier は置かない（書き換えることになったら、その再現は verifier に分ける）。

---

## TODO-025. 2 文目も短く切る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `chunks()`（`src/ccspk/hook.py`）で、2 文目にも `split_first()` をかける。3 文目以降は文ごとのまま
- [ ] `demo()` の「2 文目以降を切らない」テストを、「2 文目は切り、3 文目は切らない」に直す
- [ ] `docs/Developer.md` の説明（「1 文目はさらに前後 2 つに切り」の段落）と、関数の表の
  `split_first()`・`chunks()` の行を直す

1 文目の後半を鳴らしている間に長い 2 文目の合成が終わらず、継ぎ目で待つのを減らすため
（利用者の依頼。2026-09-29）。切った所で抑揚が文末のように下がるのは、2 文目にも出る。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
