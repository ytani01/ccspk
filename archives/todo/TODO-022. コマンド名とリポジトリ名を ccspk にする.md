# TODO-022. コマンド名とリポジトリ名を ccspk にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium。追加の確認で 2 回） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 8,771 | 50,037 | 87% |
| verifier | Sonnet 5.5 | medium | 699 | 30,019 | 13% |
| 合計 |  |  | 9,470 | 80,056 | 概算 $1.1 |

- 項目を立ててから着手まで、書き直しのやり取りがあったので `--since '2026-09-29 04:57:43'` で切った
- 終点は `5b7c577`。そのあとの GitHub の改名の反映と、ディレクトリを移したあとの決着の分は入っていない
- verifier の effort は `~/.claude/agents/verifier.md` の値。モデルは定義どおり sonnet

## きっかけ

コマンド名 `claudecodespeak` が長い。TODO-021 で辞書を `~/.config/ccspk/` に置くので、
その前にコマンド名とリポジトリ名を `ccspk` にそろえる。

## やったこと

- `src/claudecodespeak/` を `src/ccspk/` へ `git mv`。`pyproject.toml` の `name` と
  `[project.scripts]`、`hook.py` の `MODULE` を直し、`uv sync` で `uv.lock` を作り直した
- 実行時のファイル名 `claude-tts`（`hook.py` の `BASE`）を `ccspk` にした
- 環境変数 `CLAUDE_TTS_SPEAK` を `CCSPK_SPEAK` にした。立てたときの対象（`rg` の式）に
  入っていなかったものを verifier が見つけ、利用者が改名を選んだ
- `README.md`・`CLAUDE.md`・`docs/`・`TODO.md` の旧名を直した
- `~/.claude/settings.json` のフック 2 か所を `ccspk hook` に、`env` を `CCSPK_SPEAK` にした。
  `uv tool install .` のあと `uv tool uninstall claudecodespeak`
- `archives/agents/TODO-022/move-dir.sh` を作った。ディレクトリとメモリの置き場所を移し、
  `.venv` を作り直し、`uv tool install --reinstall .`、systemd の symlink を張り直す
- GitHub の改名（`gh repo rename`）と `git remote set-url` は、auto mode の分類器に止められたので
  利用者が `!` で実行した
- `move-dir.sh` は、Claude Code を終了したあとに利用者が走らせた

## 確かめたこと

verifier（`archives/agents/TODO-022/verifier-report.md`）:

- `claudecodespeak`・`claude-tts`・`CLAUDE_TTS` が、`TODO.md` の TODO-022 節（改名の説明）の
  ほかに残っていない
- `uv run ccspk test` が通る
- 一時ディレクトリを `XDG_RUNTIME_DIR` にしてフックを動かすと、`CCSPK_SPEAK=1` で `ccspk.pid` が
  でき、`CLAUDE_TTS_SPEAK=1` だけでは鳴らない
- `move-dir.sh` を、`HOME` を一時ディレクトリにし、偽物の `uv`・`systemctl`・`ccspk` で走らせた。
  移すべきものが移り、呼ぶべきコマンドが順に呼ばれる。前提が外れたとき（`~/work/ccspk` が先にある）は
  0 以外で止まり、何も変わらない

利用者:

- `move-dir.sh` の最後の表示が手順どおり（`command -v ccspk` が `~/.local/bin/ccspk`、
  `command -v claudecodespeak` が空、`ccspk status` が使える）
- `~/work/ccspk` で起動し直した Claude Code で、返答が読み上げられる
- メモリが `~/.claude/projects/-home-ytani-work-ccspk/memory/` に引き継がれている

## 分担の振り返り

- verifier は、対象の `rg` の式から漏れていた環境変数 `CLAUDE_TTS_SPEAK` を見つけた。
  音が実際に鳴るかは見られず（pid ファイルまで）、利用者の確認に任せた
- 見込みとの食い違いは、verifier を追加の確認でもう一度呼んだことだけ。同じ担当に続けて頼んだので、
  2 回目の手順の組み直しは要らなかった
- 環境変数の改名は、名前を変えただけでも挙動の条件（どの変数で鳴るか）が変わる。次に同じ規模の
  改名をやるときは、立てる時点で `rg` の式に旧名の略し方（`CLAUDE_TTS`）も入れ、条件が変わるなら
  reviewer を入れるかを見込みの段階で決めておく
- 外部に出る操作（`gh repo rename`・`git remote set-url`）は、auto mode で止められることがある。
  立てるときに「利用者が `!` で走らせる」と書いておけば、やり取りが 1 往復減る
