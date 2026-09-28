# TODO

**残っている項目: TODO-020〜TODO-023。** これまでに 19 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-024` から。**

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

## TODO-022. コマンド名とリポジトリ名を ccspk にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |

- [ ] `pyproject.toml` の `name` と `[project.scripts]`、`src/claudecodespeak/` を `ccspk` にする
  （`git mv`。`hook.py` の `MODULE` も）。`uv.lock` は `uv sync` で作り直す
- [ ] 実行時のファイル名 `claude-tts`（`hook.py` の `BASE`）を `ccspk` にする
- [ ] 文書（`README.md`・`CLAUDE.md`・`docs/`・`TODO.md`）とコード中の旧名を直す。
  対象は `rg -n -i -e claudecodespeak -e claude-tts --hidden -g '!.git' -g '!archives'`
- [ ] `~/.claude/settings.json` のフックのコマンド（2 か所）を `ccspk hook` にし、
  `uv tool install .` と `uv tool uninstall claudecodespeak` で入れ替える（Claude がやる）
- [ ] GitHub のリポジトリを改名し、remote を向け直す（Claude がやる。push はしない）
  - `gh repo rename ccspk -R ytani01/claudecodespeak --yes`
  - `git remote set-url origin git@github.com:ytani01/ccspk.git`
- [ ] 手元のディレクトリを移すスクリプト `archives/agents/TODO-022/move-dir.sh` を作る。
  Claude Code の作業ディレクトリそのものを移すので、ここだけは Claude Code を終了してから
  利用者が走らせる。スクリプトがやること:
  - 先に確かめて、どれか外れたら何もせず止まる: `~/work/claudecodespeak` がある、
    `~/work/ccspk` と `~/.claude/projects/-home-ytani-work-ccspk` が無い
  - `~/work/claudecodespeak` → `~/work/ccspk`、
    `~/.claude/projects/-home-ytani-work-claudecodespeak` → `-home-ytani-work-ccspk`（メモリの置き場所）
  - `.venv` を消して `uv sync`（中のスクリプトの 1 行目が旧いパスの python を指すため）
  - `uv tool install --reinstall .`（`~/.local/share/uv/tools/ccspk/uv-receipt.toml` が旧いディレクトリを指すため）
  - 旧いパスを指す symlink 2 本
    （`~/.config/systemd/user/voicevox-engine.service` と `default.target.wants/` の下）を消し、
    `systemctl --user daemon-reload`・`link ~/work/ccspk/systemd/voicevox-engine.service`・
    `enable voicevox-engine.service`。エンジンは止めない（unit ファイルの中身は変わらない）
  - 最後に `command -v ccspk`、`command -v claudecodespeak` が空であること、`ccspk status` を表示する
- [ ] 利用者に、下の「利用者がやること」を伝える

### 利用者がやること

Claude の作業のコミットが済んでから、この順にやる。

1. Claude Code を終了する（`/exit`）
2. 端末で次を走らせる

   ```sh
   ~/work/claudecodespeak/archives/agents/TODO-022/move-dir.sh
   ```

3. 最後の表示を見る
   - `command -v ccspk` が `~/.local/bin/ccspk`
   - `command -v claudecodespeak` が何も出さない
   - `ccspk status` がエンジンを使えると言っている
4. 途中で止まったら、表示されたメッセージを控えて、`~/work/claudecodespeak` か `~/work/ccspk` の
   残っているほうで Claude Code を起動し、そのメッセージを渡す
5. 新しいディレクトリで Claude Code を起動し直す

   ```sh
   cd ~/work/ccspk && claude
   ```

6. 何か話しかけて、返答が読み上げられることを確かめる
7. メモリが引き継がれていることを確かめる。端末で次を走らせ、2 行が出ること

   ```sh
   cat ~/.claude/projects/-home-ytani-work-ccspk/memory/MEMORY.md
   ```

   ```
   - [文書の変更も TODO に立てる](todo-for-doc-changes.md) — 文書だけの作業でも項目を立て、移す作業には reviewer を付ける
   - [「語」でなく「単語」](say-tango-not-go.md) — 辞書に登録するものは「単語」と書く
   ```
8. 確かめた結果を Claude に伝える（Claude が TODO-022 を決着させる）

`archives/` と過去のコミットメッセージの旧名は、記録なので直さない。
挙動は名前以外変わらないので reviewer は置かない。verifier には、旧名が残っていないこと、
`ccspk test` が通ること、入れ替えたあとのフックで読み上げが鳴ることを確かめさせる。
`move-dir.sh` は、`HOME` を一時ディレクトリにし、`uv`・`systemctl` を記録するだけの偽物を
`PATH` の先頭に置いて走らせ、移した先と呼んだコマンドを確かめさせる（本物の環境では走らせない）。
前提が外れたときに何も変えずに止まることも 1 通り確かめさせる。
切り替えの瞬間に鳴っている旧名の読み上げは、新しいフックから止められない（`stop_playing()` は
`MODULE` で見分ける。一度きりなので対処しない）。

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

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
