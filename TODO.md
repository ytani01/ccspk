# TODO

**残っている項目: TODO-020、TODO-021。** これまでに 19 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-022` から。**

---

## TODO-020. dict add の優先度の既定を 7 にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `dict add` で新しい単語を登録するとき、`--priority` を省くと 7 にする
  （`src/claudecodespeak/user_dict.py` の `add`。今はエンジンの既定 5 に任せている）
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

- [ ] 辞書のファイルを `~/.config/claudecodespeak/user_dict.json` とする
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

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
