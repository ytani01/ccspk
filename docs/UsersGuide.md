# 使い方

## インストール

リポジトリは `~/work/ccspk` に clone する（下の手順のコマンドは、
このパスを前提にしている）。コマンド `ccspk` は `uv tool install` でインストールする。

```sh
git clone git@github.com:ytani01/ccspk.git ~/work/ccspk
uv tool install ~/work/ccspk
```

コードを直したら、`uv tool install --reinstall ~/work/ccspk` で再インストールする。

### VOICEVOX エンジン

エンジンは公式リリースの Linux 単体版を使う（約 1.8 GB、展開後 2.2 GB）。
夜語トバリは 0.25.2 からなので、AUR の `voicevox-engine`（0.24.1）では使えない。
`.vvpp` の中身は zip で、`7z` で展開できる。

```sh
mkdir -p ~/.local/share/voicevox-engine && cd ~/.local/share/voicevox-engine
gh release download 0.25.2 -R VOICEVOX/voicevox_engine \
  -p 'voicevox_engine-linux-cpu-x64-0.25.2.vvpp'
7z x -o0.25.2 voicevox_engine-linux-cpu-x64-0.25.2.vvpp
chmod +x 0.25.2/run
rm voicevox_engine-linux-cpu-x64-0.25.2.vvpp
systemctl --user link ~/work/ccspk/systemd/voicevox-engine.service
systemctl --user enable --now voicevox-engine.service
curl -s http://127.0.0.1:50021/version   # "0.25.2" が返れば起動している
```

再生には `pw-play`（PipeWire）を使う。バージョンを上げるときは、展開先と
unit ファイルのパスを揃えて書き換え、`systemctl --user daemon-reload` してから
再起動する。

エンジンが起動するたびに、`~/.config/ccspk/user_dict.json` があれば辞書に読み込む
（unit ファイルの `ExecStartPost`。`~/.local/bin/ccspk` を使うので、先に `ccspk` を
インストールしておく）。詳しくは [辞書のファイル](#辞書のファイル)。

整形が正しく動くかは、次の自己テストで確認できる。

```sh
ccspk test
```

### Claude Code の設定

`~/.claude/settings.json` の `hooks` に Stop・MessageDisplay・PreToolUse のフックを追加し、
`env` で `CCSPK_SPEAK` を `1` にする。`ccspk` をインストールしていないマシンでは何もしない。
Stop は返答の最後の文章を、MessageDisplay はツールを呼ぶ前などの途中の文章を読む。
PreToolUse（matcher `AskUserQuestion`）は、Claude が質問してくるときに質問の文を読む
（選択肢は読まない）。途中の文章や質問が要らなければ、そのフックは追加しない。
`ccspk` は `PATH` から探すので、インストールしたのに音が出ないときは、Claude Code を
起動するシェルで `command -v ccspk` が見つかるかを確認する。

```json
"env": {
  "CCSPK_SPEAK": "1"
},
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "! command -v ccspk >/dev/null || ccspk hook",
          "timeout": 5
        }
      ]
    }
  ],
  "MessageDisplay": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "! command -v ccspk >/dev/null || ccspk hook",
          "timeout": 5
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "AskUserQuestion",
      "hooks": [
        {
          "type": "command",
          "command": "! command -v ccspk >/dev/null || ccspk hook",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 読み上げを無効にする

`env` の `CCSPK_SPEAK` の行を消す。フックの登録は残してよい
（何もせずに終わる）。

### 鳴っている読み上げを止める

Claude Code で Esc を押して返答を中断しても、読み上げは止まらない。止めるときは
次を実行する。

```sh
ccspk stop
```

読み上げの途中なら（最初の音を待っているあいだも含む）止めて「止めた」、そうでなければ「鳴っていない」と表示する。
止めるのは再生だけで、次の返答はいつもどおり読み上げる。

### 読み上げが止まったままのとき

`pw-play` が無い、エンジン（127.0.0.1:50021）に接続できない、PipeWire が
動いていない、のどれかなら、フックは読み上げずに終わり、理由を次のファイルに
記録する。ファイルがあるあいだは、鳴らせるかを確認せずにすぐ終わる。
環境変数 `PIPEWIRE_REMOTE` があるときは、PipeWire は確認しない（`[a,b]` のような
形も取り、つながる先をフックの側で決めきれないため）。

- `$XDG_RUNTIME_DIR/ccspk.unusable`
- `$XDG_RUNTIME_DIR` が無い環境では `/tmp/ccspk-<uid>.unusable`

理由は `status` で分かる。

```sh
ccspk status
```

`$XDG_RUNTIME_DIR` のファイルは、その利用者のセッションが全部終わると消える
（`loginctl enable-linger` を有効にしていれば再起動まで残る）。`/tmp` のファイルは
再起動まで残る。

エンジンを一時的に止めたときや、ログイン直後にエンジンが起動し終わる前に
返答が来たときも記録されるので、原因を取り除いたら、ファイルを消す。次の返答から、
フックがまた確認する。

```sh
ccspk status --clear
```

## 読み上げの辞書

返答の読み上げ（`ccspk hook`）で読み間違える単語は、VOICEVOX の
エンジンのユーザー辞書で読みを直す。登録・一覧・削除・書き出し・読み込みは、
どれも `ccspk dict` のサブコマンドで行う。辞書の中身は `~/.config/ccspk/user_dict.json` にも
書き出していて、エンジンの起動時にそこから読み込む（[辞書のファイル](#辞書のファイル)）。

### 読みを確認する

登録する前後に、エンジンがどう読むかを確認する。

```sh
ccspk dict kana 'TODO.md を直す'
```

`'` の直前の音の後で、音が下がる。

### 単語を登録する

`ccspk dict add` に表記と読みを渡す。アクセントの位置はエンジンに任せ、
登録後の読みを表示する。同じ表記が登録済みなら、読みを書き換える（品詞と優先度は、
指定しなければ今のまま）。

```sh
ccspk dict add README リードミー --speak
```

- `--speak` を付けると、登録後に表記を読み上げる
- 表示した読みのアクセントが違えば、`--accent` で位置を指定して登録し直す。
  `accent_type` は、音が下がる直前の音が頭から何番目か。1 なら最初の音の後で
  下がる（頭高）、0 なら下がらない（平板）
- エンジンは、単語 1 つだけでは平板と尾高（最後の音の後で下がる）を見分けない。
  そのため `dict add` は、句が 1 つで最後の音で下がるときは平板（`0`）として
  登録する。尾高の単語は `--accent <音の数>` で登録し直す
- 品詞は `--type`。省くと、新しい単語は `PROPER_NOUN`、登録済みの単語は今の品詞のまま
- 優先度は `--priority`（0〜10、大きいほど優先）。省くと、新しい単語は 7、登録済みの単語は
  今の優先度のまま。7 はエンジンの既定の 5 より高く、多くはエンジン標準の読みより優先される
  （「節」は 5 ではフシのままで、7 でセツになった）。それでも表示した読みが変わらないときは、
  優先度をさらに上げて登録し直す
- 英字は大文字と小文字を別の単語として扱う。両方直すなら両方登録する
  （`JSON` と `json`）

### 登録した単語を一覧・削除する

```sh
ccspk dict list
ccspk dict remove README
```

`dict list` は ID・表記・読み・`accent_type`・優先度を表記順に並べる。読みを変えるときは、
`dict add` に同じ表記で渡す。

### 辞書のファイル

辞書のファイルは `~/.config/ccspk/user_dict.json`（`$XDG_CONFIG_HOME` があれば
`$XDG_CONFIG_HOME/ccspk/user_dict.json`）。表記は半角で書く。

- `dict add`・`dict remove`・`dict import` が成功すると、エンジンの辞書をこのファイルへ
  書き出す（`dict export` と同じ形）。手で書き出す必要は無い
- エンジンが起動するたびに、このファイルを `dict import` で読み込む。エンジンの版を上げたり
  入れ直したりしても、辞書は戻る。エンジンが 10 秒で応答しないときは読み込まずに
  あきらめる（エンジンは止めない）。そのときは `journalctl --user -u voicevox-engine` で理由を見る
- 別のマシンへは、このファイルを写してからエンジンを再起動する（または `dict import` する）

`dict import` は、同じ ID の単語があれば上書きする。エンジンにあってファイルに無い単語は
消えずに残り、そのまま次の書き出しでファイルにも入る。

ファイルとは別の場所へ書き出す・読み込むときは、`dict export` と `dict import` にパスを渡す
（省くと標準出力・標準入力）。

```sh
ccspk dict export backup.json
ccspk dict import backup.json
```

### 記号と数字

辞書で直せないものは、`src/ccspk/hook.py` の `to_speech` で置き換えている。

- 「〜」「～」「→」は「から」にする。前後のスペースも消す（`1 〜 4` → `1から4`）
- 半角の「~」は、数字に挟まれたときだけ「から」にする（`1~4` → `1から4`）
- 数字の直後のスペースは、同じ行で日本語の文字が続くときだけ消す
  （`180 字` → `180字`）。全角数字も同じ
