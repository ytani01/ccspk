# claudecodespeak

Claude Code の返答の冒頭を、手元の VOICEVOX で読み上げる Stop フック。

## ファイル

| ファイル | 中身 |
|---|---|
| `hooks/speak-response.py` | Stop フック。返答の冒頭を VOICEVOX で読み上げる |
| `systemd/voicevox-engine.service` | VOICEVOX のエンジンを常駐させる user unit |
| `voicevox/user_dict.json` | VOICEVOX のユーザー辞書の元（読み間違える語の読み） |
| `docs/UsersGuide.md` | 読み上げの辞書の扱い方 |

## 動き方

`Stop` フックで `hooks/speak-response.py` が動き、Claude の返答の冒頭を
VOICEVOX（夜語トバリ・明るい）で読み上げる。合成は手元のエンジンで行うので、
返答が外に送られることはない。

- 環境変数 `CLAUDE_TTS_SPEAK` が `1` のときだけ鳴る。`~/.claude/settings.json` の
  `env` に書いてあるので、その行を消せば止まる
- 読み上げるのは整形した先頭 180 文字（30 秒ほど）。超えるときは、文の途中で
  切らないよう、180 字目から 240 字目までで最初の文末まで読む。文末が無ければ
  読点まで、それも無ければ 180 字で切る。コードブロックは
  「コード省略」に置き換え、表・Markdown の記号・リンクの URL は消す
- 読み間違いを減らすため、記号を「から」に置き換え、数字の直後のスペースを
  消す。語の読みはエンジンの辞書で直す。どちらも
  [docs/UsersGuide.md](docs/UsersGuide.md#読み上げの辞書) にある
- 文ごとに合成し、1 文目ができたらすぐ鳴らす。2 文目以降は鳴らしている
  間に合成する。短い文の直後に長い文が来ると、継ぎ目で数秒待つことがある
- 1 文目はさらに前後 2 つに切り、前半ができたらすぐ鳴らす。切るのは 8 字より
  後ろで最初に現れる読点・閉じ括弧・コロンの後ろか、開き括弧の前。それらが
  30 字以内に無いときだけ、その手前のスペースで切り、スペースも無ければ
  30 字より後ろの区切りで切る。後半が句点だけになる所や、`12:30`・`name()` の
  ような語の中の半角「:」「(」では切らない。切った所は抑揚が文末のように
  下がる。最初の音までは、エンジンが空いていれば 1.2〜2.5 秒ほど
- 再生中に次の返答が来たら、前の再生を止めて新しいほうを読む
- サブエージェントの報告では鳴らない（`SubagentStop` は登録していない）
- エンジンが動いていないときは、何も鳴らさずに終わる

## 入れ方

エンジンは公式リリースの Linux 単体版を使う（約 1.8 GB、展開後 2.2 GB）。
夜語トバリは 0.25.2 からなので、AUR の `voicevox-engine`（0.24.1）では鳴らない。
`.vvpp` の中身は zip で、`7z` で展開できる。

```sh
mkdir -p ~/.local/share/voicevox-engine && cd ~/.local/share/voicevox-engine
gh release download 0.25.2 -R VOICEVOX/voicevox_engine \
  -p 'voicevox_engine-linux-cpu-x64-0.25.2.vvpp'
7z x -o0.25.2 voicevox_engine-linux-cpu-x64-0.25.2.vvpp
chmod +x 0.25.2/run
rm voicevox_engine-linux-cpu-x64-0.25.2.vvpp
systemctl --user link ~/work/claudecodespeak/systemd/voicevox-engine.service
systemctl --user enable --now voicevox-engine.service
curl -s http://127.0.0.1:50021/version   # "0.25.2" が返れば起動している
```

再生には `pw-play`（PipeWire）を使う。版を上げるときは、展開先と
unit ファイルのパスを揃えて書き換え、`systemctl --user daemon-reload` してから
再起動する。

読み間違える語（`TODO`、`README`、`CLAUDE`、`JSON` など）は、エンジンの
ユーザー辞書で読みを直している。辞書の元は `voicevox/user_dict.json`。
語の足し方と、エンジンを入れ直したときの戻し方は
[docs/UsersGuide.md](docs/UsersGuide.md#読み上げの辞書) にある。

整形の自己テストは次で走る。

```sh
python3 ~/work/claudecodespeak/hooks/speak-response.py --test
```

## Claude Code につなぐ

`~/.claude/settings.json` の `hooks` に Stop フックを足し、`env` で
`CLAUDE_TTS_SPEAK` を `1` にする。clone していないマシンでは何もしない。

```json
"env": {
  "CLAUDE_TTS_SPEAK": "1"
},
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "f=\"$HOME/work/claudecodespeak/hooks/speak-response.py\"; [ ! -f \"$f\" ] || python3 \"$f\"",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## TODO の番号

`~/.claude`（dotfiles-claude）から分けたときに付け替えた。`archives/todo/` の
各ファイルに旧番号を書いてある。git の履歴のコミットメッセージは旧番号のまま。
