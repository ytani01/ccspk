# claudecodespeak

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げるフック。

## ファイル

| ファイル | 中身 |
|---|---|
| `pyproject.toml` | コマンド `claudecodespeak` の定義（`uv tool install` で入れる） |
| `src/claudecodespeak/hook.py` | `claudecodespeak hook`。Stop・MessageDisplay・PreToolUse フック。返答の冒頭と質問の文を VOICEVOX で読み上げる |
| `src/claudecodespeak/user_dict.py` | `claudecodespeak dict`。VOICEVOX のユーザー辞書を操作する |
| `src/claudecodespeak/cli.py` | サブコマンドをまとめる |
| `systemd/voicevox-engine.service` | VOICEVOX のエンジンを常駐させる user unit |
| `voicevox/user_dict.json` | VOICEVOX のユーザー辞書を書き出したもの（読み間違える語の読み） |
| `docs/UsersGuide.md` | インストール、Claude Code の設定、読み上げの無効化、読み上げの辞書の扱い方 |
| `docs/Developer.md` | 動き方の細かい決まり、フックの仕組み、テストと動作の確かめ方 |

## 動き方

`Stop` と `MessageDisplay` のフックで `claudecodespeak hook` が動き、Claude の返答の冒頭を
VOICEVOX（夜語トバリ・明るい）で読み上げる。`AskUserQuestion` で質問してくるときは、
`PreToolUse` のフックで質問の文を読む。合成は手元のエンジンで行うので、
返答が外に送られることはない。

- 環境変数 `CLAUDE_TTS_SPEAK` が `1` のときだけ鳴る
- 読むのは冒頭の 180 字ほど。なるべく文末で切り、コードブロックは「コード省略」と読み、表は飛ばす
- 1 文目ができたらすぐ鳴らし、残りは鳴らしている間に合成する
- 読み間違えやすい記号・数字・語は、置き換えとエンジンの辞書で直す
- ツールを呼ぶ前などの途中の文章も読む。再生中に次の文章が来たら、前の再生を止めて新しいほうを読む
- 鳴らせない環境では、使えないことを覚えて、次からは確かめもせずに終わる

細かい決まりは [docs/Developer.md](docs/Developer.md#動き方)、辞書と
読み上げが止まったままのときの戻し方は [docs/UsersGuide.md](docs/UsersGuide.md) にある。

## インストール

エンジンのインストール、Claude Code の設定、読み上げを無効にする方法は
[docs/UsersGuide.md](docs/UsersGuide.md#インストール) にある。

## TODO の番号

`~/.claude`（dotfiles-claude）から分けたときに付け替えた。`archives/todo/` の
各ファイルに旧番号を書いてある。git の履歴のコミットメッセージは旧番号のまま。
