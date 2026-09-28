# claudecodespeak

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げる Stop フック。

## ファイル

| ファイル | 中身 |
|---|---|
| `hooks/speak-response.py` | Stop フック。返答の冒頭を VOICEVOX で読み上げる |
| `systemd/voicevox-engine.service` | VOICEVOX のエンジンを常駐させる user unit |
| `voicevox/user_dict.json` | VOICEVOX のユーザー辞書の元（読み間違える語の読み） |
| `voicevox/add-word.py` | VOICEVOX のユーザー辞書に語を足す |
| `docs/UsersGuide.md` | 入れ方、フックの設定、止め方、読み上げの辞書の扱い方 |
| `docs/Developer.md` | 動き方の細かい決まり、フックの仕組み、テストと動作の確かめ方 |

## 動き方

`Stop` フックで `hooks/speak-response.py` が動き、Claude の返答の冒頭を
VOICEVOX（夜語トバリ・明るい）で読み上げる。合成は手元のエンジンで行うので、
返答が外に送られることはない。

- 環境変数 `CLAUDE_TTS_SPEAK` が `1` のときだけ鳴る
- 読むのは冒頭の 180 字ほど。なるべく文末で切り、コードブロックは「コード省略」と読み、表は飛ばす
- 1 文目ができたらすぐ鳴らし、残りは鳴らしている間に合成する
- 読み間違えやすい記号・数字・語は、置き換えとエンジンの辞書で直す
- 再生中に次の返答が来たら、前の再生を止めて新しいほうを読む
- 鳴らせない環境では、使えないことを覚えて、次からは確かめもせずに終わる

細かい決まりは [docs/Developer.md](docs/Developer.md#動き方)、辞書と
使えないと覚えたときの戻し方は [docs/UsersGuide.md](docs/UsersGuide.md) にある。

## 入れ方

エンジンの入れ方、Claude Code のフックの設定、止め方は
[docs/UsersGuide.md](docs/UsersGuide.md#入れ方) にある。

## TODO の番号

`~/.claude`（dotfiles-claude）から分けたときに付け替えた。`archives/todo/` の
各ファイルに旧番号を書いてある。git の履歴のコミットメッセージは旧番号のまま。
