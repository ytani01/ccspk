# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げるフック。コマンドは
`claudecodespeak`（`hook` と `add-word` のサブコマンド。`cli.py` がまとめる）。

## コマンド

```sh
uv sync                                   # .venv に入れる
uv run claudecodespeak hook --test        # 整形・分割・assemble・questions の自己テスト（demo() の assert）
uv run claudecodespeak add-word --test    # accent_of の自己テスト
.venv/bin/claudecodespeak hook --play '文'  # 合成と再生だけを試す
uv tool install .                         # 利用者の環境へ入れる
```

テストは pytest ではなく、各モジュールの `demo()` にある `assert`。個別に走らせる
手段は無い。整形や分割を変えたら `demo()` に例を足す。lint の設定は無い。

## 仕組み

- `hook.py` は Stop・MessageDisplay・PreToolUse（`AskUserQuestion`）で起動され、
  標準入力の JSON から文を取り出して整え、`python -P -m claudecodespeak.hook --play`
  の子プロセス（新しいセッション）に合成と再生を任せてすぐ終わる。
  前の再生は PID ファイルのプロセスグループに `SIGTERM` を送って止める
- 状態は `$XDG_RUNTIME_DIR` のファイル（PID、使えない理由、最後に読んだ文、ロック、
  MessageDisplay の分）で持つ。フックは並んで走るので、ロックで 1 つずつ通す
- 鳴らせない環境（`pw-play` が無い、エンジンや PipeWire に接続できない）では理由を
  ファイルに書き、次からは確かめずに終わる
- VOICEVOX のエンジンは `127.0.0.1:50021`、話者は 119。`hook.py` と `add_word.py` で揃える

流れ・定数・切り方の決まりは `docs/Developer.md`、入れ方と辞書は `docs/UsersGuide.md`。

## 手で確かめるとき

本物の `$XDG_RUNTIME_DIR` で試すと、`claude-tts.unusable` が残って読み上げが止まったり、
いま鳴っている読み上げを止めたりする。`XDG_RUNTIME_DIR` を一時ディレクトリに向け、
`PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u)` で PipeWire だけ本物を指す
（手順は `docs/Developer.md` の「Stop を手で再現する」）。

## 辞書

`add-word` はエンジンの辞書に足すだけで、`voicevox/user_dict.json` には書き戻さない。
語を足したら、エンジンから書き出してコミットする（`docs/UsersGuide.md` の「リポジトリに残す」）。

## TODO

`TODO.md` と `archives/`。番号は `~/.claude` から分けたときに付け替えたので、
git のコミットメッセージにある番号は旧番号（各 `archives/todo/` のファイルに旧番号がある）。
