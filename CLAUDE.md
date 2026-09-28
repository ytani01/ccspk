# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げるフック。コマンドは
`ccspk`（`hook`・`say`・`stop`・`status`・`test`・`dict` のサブコマンド。`cli.py` がまとめる）。
仕組みとテストは `docs/Developer.md`、インストールと辞書は `docs/UsersGuide.md` にある。

## コマンド

```sh
uv sync                   # .venv に入れる
uv run ccspk test         # hook・dict の自己テスト（demo() の assert）
.venv/bin/ccspk say '文'  # 合成と再生だけを試す
uv tool install .         # 利用者の環境へ入れる
```

## 注意

- 整形や分割を変えたら `demo()` に例を足す
- `src/` か `pyproject.toml` が前回のインストールより新しければ、返答の終わりに Stop フック
  （`.claude/settings.json`）が `ccspk test` を走らせ、通ったら `uv tool install --reinstall .` で
  入れ直す。落ちたら入れ直さず、`systemMessage` で知らせる。`ccspk` を入れていない環境では何もしない
- フックを手で動かすときは、本物の `$XDG_RUNTIME_DIR` を使わない（読み上げが止まったままに
  なったり、鳴っている読み上げを止めたりする）。手順は `docs/Developer.md` の「フックを手で動かす」
- 辞書はリポジトリに置かない。`dict add`・`remove`・`import` が `~/.config/ccspk/user_dict.json` へ
  書き出し、エンジンの起動時に読み込む（`docs/UsersGuide.md` の「辞書のファイル」）。
  試すときは `XDG_CONFIG_HOME` を一時ディレクトリに向ける
- `~/.claude` から分ける前のコミットメッセージにある TODO の番号は旧番号（`docs/Developer.md` の「TODO の番号」）
