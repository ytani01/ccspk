# TODO

**残っている項目: TODO-015。** これまでに 14 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-016` から。**

---

## TODO-015. サブコマンドを整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（調査・設計）+ implementer（Sonnet 5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `hook --play '文'` を `say '文'` にする
- [ ] `hook --test` と `add-word --test` を `test` 1 本にまとめ、両方の自己テストを走らせる
- [ ] `add-word` を `dict add` にする
- [ ] `dict kana TEXT` を足す（エンジンの読みをアクセント記号付きのカナで表示する）
- [ ] `dict list` を足す（ID・表記・読みを一覧する）
- [ ] `dict remove SURFACE` を足す（表記で指定して消す）
- [ ] `dict export [FILE]` と `dict import [FILE]` を足す（省くと標準出力・標準入力）
- [ ] `status` と `status --clear` を足す（`claude-tts.unusable` の理由を表示する・消す）
- [ ] `README.md`・`CLAUDE.md`・`docs/` のコマンド例を書き換え、`curl` や `rm` の手順を
      サブコマンドに置き換える

整理したあとのサブコマンド:

| サブコマンド | 今の形 |
|---|---|
| `hook` | そのまま |
| `say TEXT` | `hook --play TEXT` |
| `test` | `hook --test`・`add-word --test` |
| `dict add SURFACE PRON` | `add-word`（`--accent`・`--type`・`--speak` はそのまま） |
| `dict kana TEXT` | `curl … /audio_query \| jq .kana` |
| `dict list` | `curl … /user_dict \| jq` |
| `dict remove SURFACE` | `curl -X DELETE …/user_dict_word/<ID>` |
| `dict export [FILE]` | `curl … /user_dict \| jq -S . > voicevox/user_dict.json` |
| `dict import [FILE]` | `curl -X POST … /import_user_dict?override=true` |
| `status [--clear]` | `cat`・`rm` で `claude-tts.unusable` を見る・消す |

背景（決まったこと）:

- 古い書き方（`add-word`、`hook --play`、`hook --test`）は別名として残さず消す
- `hook` はフック専用として残す。`settings.json` から呼ぶ形（`claudecodespeak hook`）は変えない
- `dict export` / `dict import` のファイルは引数で渡す。リポジトリの場所を前提にしない
- 子プロセスの目印の `--play`（`python -m claudecodespeak.hook --play`、`hook.py` の `PLAY`）は
  残す。`stop_playing()` がこれで自分の子プロセスかを見分けている。消すのは click の
  オプションとしての `--play` だけ

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
