# TODO

**残っている項目: TODO-020、TODO-021、TODO-022。** これまでに 19 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-023` から。**

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
- [ ] リポジトリの外の残り（下の「利用者がやること」）は、コミットのあと利用者がやる

`archives/` と過去のコミットメッセージの旧名は、記録なので直さない。
挙動は名前以外変わらないので reviewer は置かない。verifier には、旧名が残っていないこと、
`ccspk test` が通ること、入れ替えたあとのフックで読み上げが鳴ることを確かめさせる。
切り替えの瞬間に鳴っている旧名の読み上げは、新しいフックから止められない（`stop_playing()` は
`MODULE` で見分ける。一度きりなので対処しない）。

### 利用者がやること

Claude の作業（上の 4 つ）のコミットが済んでから、この順にやる。**1 の前に Claude Code を
終了する**（作業ディレクトリが消えるため）。

1. GitHub のリポジトリを改名し、remote を向け直す

   ```sh
   cd ~/work/claudecodespeak
   gh repo rename ccspk -R ytani01/claudecodespeak
   git remote set-url origin git@github.com:ytani01/ccspk.git
   git remote -v   # ytani01/ccspk.git になっていること
   ```

2. 手元のディレクトリと、Claude Code のプロジェクトのディレクトリ（メモリの置き場所）を改名する

   ```sh
   \mv ~/work/claudecodespeak ~/work/ccspk
   \mv ~/.claude/projects/-home-ytani-work-claudecodespeak ~/.claude/projects/-home-ytani-work-ccspk
   ```

3. `.venv` を作り直す（中のスクリプトの 1 行目が `/home/ytani/work/claudecodespeak/.venv/bin/python`
   を指しているため）

   ```sh
   cd ~/work/ccspk
   \rm -rf .venv && uv sync
   ```

4. `uv tool` を入れ直す（`~/.local/share/uv/tools/ccspk/uv-receipt.toml` が旧いディレクトリを
   指したままになるため）

   ```sh
   uv tool install --reinstall .
   ```

5. systemd の unit を張り直す。今は次の 2 つが旧いパスを指している
   - `~/.config/systemd/user/voicevox-engine.service`
   - `~/.config/systemd/user/default.target.wants/voicevox-engine.service`

   ```sh
   \rm ~/.config/systemd/user/voicevox-engine.service ~/.config/systemd/user/default.target.wants/voicevox-engine.service
   systemctl --user daemon-reload
   systemctl --user link ~/work/ccspk/systemd/voicevox-engine.service
   systemctl --user enable voicevox-engine.service
   systemctl --user status voicevox-engine.service   # active (running) のまま
   ```

   エンジンは動いたままでよい（unit ファイルの中身は変わらない）。

6. 確かめる

   ```sh
   command -v ccspk            # ~/.local/bin/ccspk
   command -v claudecodespeak  # 何も出ない
   ccspk status
   ```

   Claude Code を `~/work/ccspk` で起動し直し、返答が読み上げられること。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
