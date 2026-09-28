# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げるフック。コマンドは
`claudecodespeak`（`hook`・`say`・`status`・`test`・`dict` のサブコマンド。`cli.py` がまとめる）。
仕組みとテストは `docs/Developer.md`、インストールと辞書は `docs/UsersGuide.md` にある。

## コマンド

```sh
uv sync                          # .venv に入れる
uv run claudecodespeak test      # hook・dict の自己テスト（demo() の assert）
.venv/bin/claudecodespeak say '文'  # 合成と再生だけを試す
uv tool install .                # 利用者の環境へ入れる
```

## 注意

- 整形や分割を変えたら `demo()` に例を足す
- フックを手で動かすときは、本物の `$XDG_RUNTIME_DIR` を使わない（読み上げが止まったままに
  なったり、鳴っている読み上げを止めたりする）。手順は `docs/Developer.md` の「フックを手で動かす」
- `dict add` で語を足したら、`dict export` でエンジンから `voicevox/user_dict.json` に
  書き出してコミットする（`docs/UsersGuide.md` の「辞書をリポジトリに保存する」）
- git のコミットメッセージにある TODO の番号は旧番号（`README.md` の「TODO の番号」）
