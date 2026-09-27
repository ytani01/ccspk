# 使い方

## 入れ方

リポジトリは `~/work/claudecodespeak` に clone する（フックの設定と下の手順の
コマンドは、このパスを前提にしている）。

```sh
git clone git@github.com:ytani01/claudecodespeak.git ~/work/claudecodespeak
```

### エンジン

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

エンジンを入れたら、読み間違える語の辞書を読み込む
（[戻す](#戻す) の手順）。

整形の自己テストは次で走る。

```sh
python3 ~/work/claudecodespeak/hooks/speak-response.py --test
```

### Claude Code のフック

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

### 止める

`env` の `CLAUDE_TTS_SPEAK` の行を消す。フックの登録は残してよい
（何もせずに終わる）。

### 使えないと覚えたとき

`pw-play` が無い、エンジン（127.0.0.1:50021）に接続できない、PipeWire が
動いていない、のどれかなら、フックは鳴らさずに終わり、理由を次のファイルに
書いて覚える。ファイルがあるあいだは、確かめもせずにすぐ終わる。
環境変数 `PIPEWIRE_REMOTE` があるときは、PipeWire は確かめない（`[a,b]` のような
形も取り、つながる先をフックの側で決めきれないため）。

- `$XDG_RUNTIME_DIR/claude-tts.unusable`
- `$XDG_RUNTIME_DIR` が無い環境では `/tmp/claude-tts-<uid>.unusable`

理由はファイルの中身で分かる。

```sh
cat "$XDG_RUNTIME_DIR/claude-tts.unusable"
```

`$XDG_RUNTIME_DIR` のファイルは、その利用者のセッションが全部終わると消える
（`loginctl enable-linger` を入れていれば再起動まで残る）。`/tmp` のファイルは
再起動まで残る。

エンジンを一時的に止めたときや、ログイン直後にエンジンが起動し終わる前に
返答が来たときも覚えるので、鳴るように直したら、ファイルを消す。次の返答から
確かめ直す。

```sh
rm "$XDG_RUNTIME_DIR/claude-tts.unusable"
```

## 読み上げの辞書

返答の読み上げ（`hooks/speak-response.py`）で読み間違える語は、VOICEVOX の
エンジンのユーザー辞書で読みを直す。辞書はエンジンの中にあり、その元を
`voicevox/user_dict.json` に置いている。

GUI の VOICEVOX エディタは入れていないので、登録はエンジンの API で行う。
ブラウザから操作するなら `http://127.0.0.1:50021/docs`、コマンドなら `curl`。

### 読みを確かめる

登録する前後に、エンジンがどう読むかを見る。

```sh
curl -s -X POST -G http://127.0.0.1:50021/audio_query \
  --data-urlencode speaker=119 --data-urlencode 'text=TODO.md を直す' | jq -r .kana
```

`'` の直前の音の後で、音が下がる。

### 登録する

```sh
curl -s -X POST -G http://127.0.0.1:50021/user_dict_word \
  --data-urlencode surface=README \
  --data-urlencode pronunciation=リードミー \
  --data-urlencode accent_type=1 \
  --data-urlencode word_type=PROPER_NOUN
```

- `pronunciation` はカタカナ。`--data-urlencode` を使わないと、日本語が
  そのまま URL に入って `Invalid HTTP request received.` で失敗する
- `accent_type` は、音が下がる直前の音が頭から何番目か。1 なら最初の音の後で
  下がる（頭高）、0 なら下がらない（平板）
- 英字は大文字と小文字を別の語として扱う。両方直すなら両方登録する
  （`JSON` と `json`）
- 返ってくる文字列（UUID）が、その語の ID

ブラウザでは、`/docs` の `POST /user_dict_word` を開き、「Try it out」で
同じ値を入れて「Execute」。

### 一覧を見る・消す

```sh
curl -s http://127.0.0.1:50021/user_dict \
  | jq -r 'to_entries[] | "\(.key)  \(.value.surface)  \(.value.pronunciation)"'
curl -s -X DELETE http://127.0.0.1:50021/user_dict_word/<ID>
```

読みを変えるときは、消して登録し直す（`PUT /user_dict_word/<ID>` でもよい）。

### リポジトリに残す

登録や削除をしたら、辞書の元を書き直してコミットする。

```sh
curl -s http://127.0.0.1:50021/user_dict | jq -S . > ~/work/claudecodespeak/voicevox/user_dict.json
```

### 戻す

エンジンを入れ直したときや、別のマシンでは、辞書の元を読み込む。

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  -d @$HOME/work/claudecodespeak/voicevox/user_dict.json \
  'http://127.0.0.1:50021/import_user_dict?override=true'
```

`override=true` は、同じ ID の語があれば上書きする。辞書にあってファイルに
無い語は消えずに残る。

### 記号と数字

辞書で直せないものは、`hooks/speak-response.py` の `to_speech` で置き換えている。

- 「〜」「～」「→」は「から」にする。前後のスペースも消す（`1 〜 4` → `1から4`）
- 半角の「~」は、数字に挟まれたときだけ「から」にする（`1~4` → `1から4`）
- 数字の直後のスペースは、同じ行で日本語の文字が続くときだけ消す
  （`180 字` → `180字`）。全角数字も同じ
