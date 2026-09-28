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

整形が正しく動くかは [`ccspk test`](#ccspk-test) で確認できる。

### Claude Code の設定

`~/.claude/settings.json` の `hooks` に Stop・MessageDisplay・PreToolUse のフックを追加し、
`env` で `CCSPK_SPEAK` を `1` にする。どのフックで何を読むかは [`ccspk hook`](#ccspk-hook)。
途中の文章や質問が要らなければ、MessageDisplay や PreToolUse のフックは追加しない。
`ccspk` をインストールしていないマシンでは何もしない。
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
[`ccspk stop`](#ccspk-stop) を実行する。

### 読み上げが止まったままのとき

フックは、鳴らせないと分かると理由をファイルに記録し、そのファイルがあるあいだは
読み上げずに終わる（[`ccspk hook`](#ccspk-hook)）。エンジンを一時的に止めたときや、
ログイン直後にエンジンが起動し終わる前に返答が来たときも記録される。

1. `ccspk status` で理由を見る（[`ccspk status`](#ccspk-status)）
2. 原因を取り除く
3. `ccspk status --clear` でファイルを消す。次の返答から、フックがまた確認する

## 読み上げの辞書

返答の読み上げで読み間違える単語は、VOICEVOX のエンジンのユーザー辞書で読みを直す。
操作はどれも [`ccspk dict`](#ccspk-dict) のサブコマンドで行う。

1. `ccspk dict kana` で、エンジンが今どう読むかを確認する
2. `ccspk dict add` で表記と読みを登録する。登録後の読みが表示される
3. アクセントが違えば `--accent` で、エンジン標準の読みに負けるなら `--priority` で指定して
   登録し直す
4. 登録した単語は `ccspk dict list` で一覧し、要らなくなったら `ccspk dict remove` で消す

```sh
ccspk dict kana 'README を直す'
ccspk dict add README リードミー --speak
```

### 辞書のファイル

辞書のファイルは `~/.config/ccspk/user_dict.json`（`$XDG_CONFIG_HOME` があれば
`$XDG_CONFIG_HOME/ccspk/user_dict.json`）。表記は半角で書く。

- `dict add`・`dict remove`・`dict import` が成功すると、エンジンの辞書をこのファイルへ
  書き出す。手で書き出す必要は無い
- エンジンが起動するたびに、このファイルを `dict import` で読み込む。エンジンの版を上げたり
  入れ直したりしても、辞書は戻る。エンジンが 10 秒で応答しないときは読み込まずに
  あきらめる（エンジンは止めない）。そのときは `journalctl --user -u voicevox-engine` で理由を見る
- 別のマシンへは、このファイルを写してからエンジンを再起動する（または `dict import` する）

### 記号と数字

辞書で直せないものは、`src/ccspk/hook.py` の `to_speech` で置き換えている。

- 「〜」「～」「→」は「から」にする。前後のスペースも消す（`1 〜 4` → `1から4`）
- 半角の「~」は、数字に挟まれたときだけ「から」にする（`1~4` → `1から4`）
- 数字の直後のスペースは、同じ行で日本語の文字が続くときだけ消す
  （`180 字` → `180字`）。全角数字も同じ

## コマンド

### ccspk

```
ccspk [-d] COMMAND [ARGS]...
ccspk -V
ccspk -h
```

**オプション**

- `-d`, `--debug` — デバッグ用のログを出す
- `-V`, `-v`, `--version` — バージョンを表示して終わる
- `-h`, `--help` — 使い方を表示して終わる。どのサブコマンドにも付けられる

**終了ステータス**（多くのサブコマンドで共通。違うものは各サブコマンドの節に書く）

- `0` — 成功
- `1` — 失敗。理由を標準エラー出力に出す
- `2` — 引数やオプションの誤り

### ccspk hook

```
ccspk hook
```

**説明**

Claude Code の Stop・MessageDisplay・PreToolUse フックとして動く。標準入力からフックの入力
（JSON）を読み、返答の冒頭を読み上げる。何を読むかはフックで違う。

- Stop — 返答の最後の文章
- MessageDisplay — ツールを呼ぶ前などの途中の文章
- PreToolUse（matcher `AskUserQuestion`）— 質問の文（選択肢は読まない）

合成と再生は子プロセスに任せ、すぐに終わる。読み上げの途中で次の返答が来たら、
前の読み上げを止めてから読む。

次のときは読み上げずに終わる。

- 環境変数 `CCSPK_SPEAK` が `1` でない
- 鳴らせない理由のファイル（下の「ファイル」）がある
- サブエージェントの途中の文章や質問（MessageDisplay・PreToolUse で `agent_id` がある）
- 5 秒以内に読んだのと同じ文
- 鳴らせない。`pw-play` が無い、エンジン（127.0.0.1:50021）に接続できない、PipeWire が
  動いていない、のどれか。理由をファイルに記録する。環境変数 `PIPEWIRE_REMOTE` があるときは、
  PipeWire は確認しない（`[a,b]` のような形も取り、つながる先をフックの側で決めきれないため）

**終了ステータス**

- `0` — 読み上げたときも、読み上げずに終わったときも

**ファイル**

- `$XDG_RUNTIME_DIR/ccspk.unusable` — 鳴らせない理由。`$XDG_RUNTIME_DIR` が無い環境では
  `/tmp/ccspk-<uid>.unusable`。`$XDG_RUNTIME_DIR` のファイルは、その利用者のセッションが
  全部終わると消える（`loginctl enable-linger` を有効にしていれば再起動まで残る）。
  `/tmp` のファイルは再起動まで残る

### ccspk say

```
ccspk say TEXT
```

**説明**

`TEXT` を合成して鳴らし、鳴らし終わってから終わる。フックの子プロセスと同じ動きで、
合成と再生だけを試すのに使う。フックと違い、次のことはしない。

- `CCSPK_SPEAK` や鳴らせない理由のファイルを見ない
- `TEXT` を整形しない（記号の置き換えも、長さの上限も無い）
- `ccspk stop` では止まらない（Ctrl-C で止める）

**引数**

- `TEXT` — 読み上げる文

**終了ステータス**

- `0` — 鳴らし終わった。エンジンに接続できないなどで合成に失敗したとき、`pw-play` が失敗したときも `0`
  （合成の失敗はトレースバックが標準エラー出力に出る）
- `1` — `pw-play` が無い。ただし最初の合成ができたときだけで、合成に失敗していれば `0`

**例**

```sh
ccspk say 'こんにちは。読み上げを試す。'
```

### ccspk stop

```
ccspk stop
```

**説明**

鳴っているフックの読み上げを止める（最初の音を待っているあいだも含む）。止めたら「止めた」、
読み上げの途中でなければ「鳴っていない」と表示する。止めるのは再生だけで、
エンジンの合成は止めない。次の返答はいつもどおり読み上げる。

**終了ステータス**

- `0` — 止めたときも、鳴っていなかったときも

**例**

```console
$ ccspk stop
止めた
```

### ccspk status

```
ccspk status [--clear]
```

**説明**

鳴らせない理由のファイルがあれば、そのパスと理由を表示する。無ければ「止まっていない」と表示する。

**オプション**

- `--clear` — 表示したあと、ファイルを消す

**終了ステータス**

- `0`

**ファイル**

- `$XDG_RUNTIME_DIR/ccspk.unusable`（または `/tmp/ccspk-<uid>.unusable`）— [`ccspk hook`](#ccspk-hook) を参照

**例**

```console
$ ccspk status
/run/user/1000/ccspk.unusable: エンジン（127.0.0.1:50021）に接続できない: [Errno 111] Connection refused
$ ccspk status --clear
/run/user/1000/ccspk.unusable: エンジン（127.0.0.1:50021）に接続できない: [Errno 111] Connection refused
消した
$ ccspk status
止まっていない
```

### ccspk test

```
ccspk test
```

**説明**

フックと辞書の処理の自己テスト（`demo()` の `assert`）を走らせる。通れば `ok` を 2 行表示する。
エンジンには接続しない。

**終了ステータス**

- `0` — すべて通った
- `1` — 通らないものがあった

**例**

```console
$ ccspk test
ok
ok
```

### ccspk dict

```
ccspk dict COMMAND [ARGS]...
```

VOICEVOX のエンジンのユーザー辞書を操作する。どのサブコマンドもエンジン（127.0.0.1:50021）に
接続する。エンジンとやり取りできないとき、エンジンが要求を断ったときは、理由を表示して
終了ステータス `1` で終わる。

`dict add`・`dict remove`・`dict import` は、成功すると、エンジンの辞書を
[辞書のファイル](#辞書のファイル)へ書き出し、「書き出した: パス」と表示する。

### ccspk dict kana

```
ccspk dict kana TEXT
```

**説明**

`TEXT` をエンジンに渡し、読みをカナで表示する。`'` は音が下がる位置（その直前の音の後で下がる）、
`/` と `、` はアクセント句の区切り、`_` は無声化する音の印。辞書に登録する前後に、エンジンが
どう読むかを確かめるのに使う。

**引数**

- `TEXT` — 読ませる文

**終了ステータス**

- `0` — 表示した
- `1` — エンジンとやり取りできない

**例**

```console
$ ccspk dict kana 'Ponytail を使う'
ポ'ニテイル、オ'/_ツカウ'
```

### ccspk dict add

```
ccspk dict add [--accent N] [--type TYPE] [--priority N] [--speak] SURFACE PRONUNCIATION
```

**説明**

辞書に単語を登録する。同じ表記の単語があれば、読みを書き換える。登録したら、表記を
エンジンに読ませた結果を「読み:」として表示する。

アクセントの位置は、`--accent` を省くとエンジンに任せる。エンジンは単語 1 つだけでは平板と
尾高（最後の音の後で下がる）を見分けないので、句が 1 つで最後の音で下がるときは平板（`0`）として
登録する。尾高の単語は `--accent <音の数>` で登録し直す。

**引数**

- `SURFACE` — 表記。英字は大文字と小文字を別の単語として扱う。両方直すなら両方登録する（`JSON` と `json`）
- `PRONUNCIATION` — 読み（カタカナ）

**オプション**

- `--accent N` — 音が下がる直前の音が頭から何番目か（`accent_type`）。`1` なら最初の音の後で
  下がる（頭高）、`0` なら下がらない（平板）。省くとエンジンに任せる
- `--type TYPE` — 品詞。`PROPER_NOUN`・`COMMON_NOUN`・`VERB`・`ADJECTIVE`・`SUFFIX` の
  どれか。省くと、新しい単語は `PROPER_NOUN`、登録済みの単語は今の品詞のまま
- `--priority N` — 優先度（`0`〜`10`、大きいほど優先）。省くと、新しい単語は `7`、登録済みの単語は
  今の優先度のまま。`7` はエンジンの既定の `5` より高く、多くはエンジン標準の読みより優先される
  （「節」は `5` ではフシのままで、`7` でセツになった）。それでも表示した読みが変わらないときは、
  さらに上げて登録し直す
- `--speak` — 登録したあと、表記を読み上げる

**終了ステータス**

- `0` — 登録した
- `1` — エンジンとやり取りできない、読みから音が取れない（カタカナでない）、など。
  `--speak` で `pw-play` が無い・失敗したときも `1` だが、登録は済んでいる

**ファイル**

- `~/.config/ccspk/user_dict.json` — 登録したあと書き出す（[辞書のファイル](#辞書のファイル)）

**例**

```console
$ ccspk dict add Ponytail ポニーテール
登録した: Ponytail → ポニーテール（accent_type 4、ID 7dbd9f32-c16b-4bf0-9dd9-94ad79e51910）
書き出した: /home/user/.config/ccspk/user_dict.json
読み: ポニイテ'エル
```

### ccspk dict list

```
ccspk dict list
```

**説明**

登録した単語を、表記順に 1 単語 1 行で表示する。並びは ID・表記・読み・`accent_type`・優先度。

**終了ステータス**

- `0` — 表示した
- `1` — エンジンとやり取りできない

**例**

```console
$ ccspk dict list
…
9962d564-ce38-45c8-9330-51ae914b909e  JSON  ジェイソン  1  5
7dbd9f32-c16b-4bf0-9dd9-94ad79e51910  Ponytail  ポニーテール  4  7
e8587f70-4e27-4017-aa5c-7c5bfdf4251f  README  リードミー  1  5
…
```

### ccspk dict remove

```
ccspk dict remove SURFACE
```

**説明**

表記で指定して、登録した単語を消す。

**引数**

- `SURFACE` — 表記

**終了ステータス**

- `0` — 消した
- `1` — 登録されていない、エンジンとやり取りできない

**ファイル**

- `~/.config/ccspk/user_dict.json` — 消したあと書き出す

**例**

```console
$ ccspk dict remove Ponytail
消した: Ponytail（ID 7dbd9f32-c16b-4bf0-9dd9-94ad79e51910）
書き出した: /home/user/.config/ccspk/user_dict.json
```

### ccspk dict export

```
ccspk dict export [FILE]
```

**説明**

エンジンの辞書を JSON で書き出す。[辞書のファイル](#辞書のファイル)と同じ形で、表記は半角にする。
辞書のファイルとは別の場所へ控えを取るときに使う。

**引数**

- `FILE` — 書き出す先。省くと標準出力

**終了ステータス**

- `0` — 書き出した
- `1` — エンジンとやり取りできない、`FILE` に書けない

**例**

```sh
ccspk dict export backup.json
```

### ccspk dict import

```
ccspk dict import [FILE]
```

**説明**

JSON の辞書をエンジンに読み込む。同じ ID の単語は上書きする。エンジンにあってファイルに無い
単語は消えずに残り、そのまま辞書のファイルにも入る。エンジンの起動時にも、これで
辞書のファイルを読み込む。

**引数**

- `FILE` — 読み込む元。省くと標準入力

**終了ステータス**

- `0` — 読み込んだ
- `1` — エンジンとやり取りできない、エンジンが断った（JSON の形が違う、など）
- `2` — `FILE` が開けない

**ファイル**

- `~/.config/ccspk/user_dict.json` — 読み込んだあと書き出す

**例**

```console
$ ccspk dict import backup.json
読み込んだ
書き出した: /home/user/.config/ccspk/user_dict.json
```
