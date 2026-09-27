# 開発者向け

コードは `hooks/speak-response.py` の 1 ファイルだけ。依存は Python の標準ライブラリ、
VOICEVOX のエンジン（`127.0.0.1:50021`）、`pw-play`。読み上げの範囲や切り方など、
利用者から見た動きは [README](../README.md#動き方)、入れ方と辞書は
[UsersGuide](UsersGuide.md) にある。

## フックの仕組み

### 流れ

Claude Code は返答を終えるたびに Stop フックとしてこのスクリプトを起動し、
標準入力に JSON を渡す。使うのは `last_assistant_message`（最後の返答の本文）だけ。

`main()` は引数で 3 つに分かれる。

| 起動のされ方 | 動き |
|---|---|
| `--test` | `demo()` の自己テストを走らせる |
| `--play <本文>` | 子プロセスとして、合成と再生をする（`play()`） |
| 引数なし | Stop フックとして動く（下の順） |

Stop フックとしては、次の順に進む。どこかで条件を満たさなければ、そこで終わる。

1. 環境変数 `CLAUDE_TTS_SPEAK` が `1` か
2. 使えないと覚えたファイル（`UNUSABLE`）が無いか。あれば確かめもせずに終わる
3. `unusable()` で鳴らせるかを確かめる。だめなら理由を `UNUSABLE` に書いて終わる
4. 標準入力の JSON を読み、`to_speech()` で読み上げる文に整える
5. `stop_playing()` で前の再生を止める
6. 文が空でなければ、`speak()` で子プロセスを起こし、その PID を `PIDFILE` に書く

フックはここで終わり、Claude Code を待たせない（登録の `timeout` は 5 秒）。
合成と再生は子プロセスが受け持つ。

### 子プロセス

`speak()` は、同じスクリプトを `--play <本文>` で起動する。
`start_new_session=True` で新しいセッション（兼プロセスグループ）にするので、
子プロセスが起こした `pw-play` まで、グループごと止められる。

`play()` は、合成するスレッドと鳴らすループに分かれる。

- 合成するスレッドは、`chunks()` で分けた塊を順に `synthesize()` し、できた wav を
  キューへ入れる。何で止まっても、最後に終わりの印（`None`）を入れる
- 鳴らすループは、キューから wav を取り出し、1 つずつ `pw-play -` に渡す

1 つ目の塊ができた時点で鳴り始め、2 つ目以降は鳴らしている間に合成する。

`synthesize()` は、エンジンの `/audio_query` と `/synthesis` を続けて呼ぶ。
エンジンは要求を 1 つずつ処理し、止めた前の返答の合成も最後まで続けるので、
その後ろに並ぶと待たされる。タイムアウトを 60 秒と長めにしているのはそのため。

### 前の再生を止める

`stop_playing()` は `PIDFILE` の PID を読み、ファイルを消してから、
そのプロセスグループに `SIGTERM` を送る。再生が終わったあとで PID が別の
プロセスに使い回されていることがあるので、`/proc/<pid>/cmdline` に `--play` と
このスクリプトの名前があるときだけ送る。

### 使えないと覚える

`unusable()` は次の順に見て、最初にだめだったものの理由を返す。

1. `pw-play` が `PATH` にあるか
2. エンジンに TCP で接続できるか。HTTP では問い合わせず、接続できるかだけを見る
3. PipeWire のソケットに接続できるか。場所は `$PIPEWIRE_RUNTIME_DIR`（無ければ
   `$XDG_RUNTIME_DIR`）の `pipewire-0`。`PIPEWIRE_REMOTE` があるときは確かめない
   （理由は [UsersGuide](UsersGuide.md#使えないと覚えたとき)）

使えるときは、3 つ合わせて 1 ms ほどで終わる。

### ファイル

どちらも `$XDG_RUNTIME_DIR` に置く。`$XDG_RUNTIME_DIR` が無い環境では `/tmp` に、
利用者の uid を名前に入れて置く。

| 定数 | 場所 | 中身 |
|---|---|---|
| `PIDFILE` | `claude-tts.pid`（`/tmp/claude-tts-<uid>.pid`） | 再生中の子プロセスの PID |
| `UNUSABLE` | `claude-tts.unusable`（`/tmp/claude-tts-<uid>.unusable`） | 鳴らせない理由 |

### 整形と分割

| 関数 | すること |
|---|---|
| `to_speech()` | コードブロックを「コード省略」に置き換え、Markdown の記号・表・URL を除き、記号と数字の読みを整え、最後に `clip()` を通す |
| `clip()` | `LIMIT` 字を超えるときに、文の途中で切らないように縮める |
| `sentences()` | 文末（`ENDS`）の後ろで文に分ける |
| `split_first()` | 1 文目を、最初の音を早めるために前後 2 つに切る |
| `chunks()` | 合成する単位。1 文目だけ `split_first()` で切り、2 文目以降は文ごと |

どこで切るかの決まりは [README の「動き方」](../README.md#動き方) に、
記号と数字の置き換えは [UsersGuide の「記号と数字」](UsersGuide.md#記号と数字) にある。

### 定数

| 定数 | 値 | 意味 |
|---|---|---|
| `LIMIT` | 180 | 読み上げるのはおよそここまで（字数） |
| `EXTEND` | 60 | 文末を探して延ばすのは、`LIMIT` からこの字数まで。延ばしすぎると、エンジンが 1 回の合成でメモリを使い切る |
| `ENDS` | `。！？!?` | 文末 |
| `COMMAS` | `、，` | 読点。半角の `,` は `1,000` のように数字の中にも出るので入れない |
| `SPEAKER` | 119 | 話者（夜語トバリ・明るい） |
| `ENGINE` | `http://127.0.0.1:50021` | エンジンの URL |
| `PLAY` | `--play` | 子プロセスの目印。`stop_playing()` がこれで見分ける |
| `CUT` | 正規表現 | 1 文目を切る区切り |
| `CUT_MIN` | 8 | これより手前では切らない |
| `SPACE_WITHIN` | 30 | この字数までに `CUT` が無いときだけ、スペースで切る |

## テストと動作の確かめ方

### 自己テスト

整形と分割（`to_speech`、`clip`、`sentences`、`split_first`、`chunks`）は、
`demo()` の `assert` で確かめている。通れば `ok` と出る。

```sh
python3 hooks/speak-response.py --test
```

整形や分割を変えたら、`demo()` に例を足す。`unusable()` と `main()` の分岐は
環境に依るので、`demo()` では確かめていない。下の手順で手で確かめる。

### Stop を手で再現する

コマンドは、どれもリポジトリの直下で走らせる。

本物の `$XDG_RUNTIME_DIR` で試して `claude-tts.unusable` が残ると、ファイルを
消すまで読み上げが止まる（[UsersGuide](UsersGuide.md#使えないと覚えたとき)）。
また、本物の `claude-tts.pid` を使うと、そのとき鳴っている読み上げを止めてしまう。
`XDG_RUNTIME_DIR` を一時ディレクトリに向け、PipeWire の場所だけ
`PIPEWIRE_RUNTIME_DIR` で本物を指す。

```sh
tmp=$(mktemp -d)
echo '{"last_assistant_message":"確認です。二つ目の文です。"}' \
  | CLAUDE_TTS_SPEAK=1 XDG_RUNTIME_DIR=$tmp PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u) \
    python3 hooks/speak-response.py
find $tmp -type f
rm -r $tmp
```

使えると判定して子プロセスを起こせば、`$tmp/claude-tts.pid` だけができる。
使えないと判定したときは、`$tmp/claude-tts.unusable` ができ、中身が理由になる。

`pw-play` が無いときを再現するなら、別の一時ディレクトリで、`PATH` を空にする。
`python3` は、mise などの shim だと `PATH` が空では動かないので、本体のパスで呼ぶ。

```sh
tmp=$(mktemp -d)
py=$(python3 -c 'import sys; print(sys.executable)')
echo '{"last_assistant_message":"確認です。"}' \
  | CLAUDE_TTS_SPEAK=1 XDG_RUNTIME_DIR=$tmp PATH=/nonexistent "$py" hooks/speak-response.py
cat $tmp/claude-tts.unusable   # pw-play が無い
rm -r $tmp
```

子プロセスは出力を捨てるので、PID のファイルができたのに鳴らないときは、
子プロセスを直接起動して、合成と再生だけを試す（整形は通らない）。

```sh
python3 hooks/speak-response.py --play '合成と再生だけを試す。'
```

### 最初の音までの時間

フックを起動してから、子プロセスのグループに `pw-play` が現れるまでを測る。
上と同じく一時ディレクトリで動かす。エンジンが前の合成を続けていると、その分
遅くなるので、読み上げが鳴っていないときに測る。

```sh
python3 - <<'PY'
import json, os, subprocess, tempfile, time
from pathlib import Path

tmp = tempfile.mkdtemp()
env = {**os.environ, "CLAUDE_TTS_SPEAK": "1", "XDG_RUNTIME_DIR": tmp,
       "PIPEWIRE_RUNTIME_DIR": f"/run/user/{os.getuid()}"}
t0 = time.monotonic()
subprocess.run(["python3", "hooks/speak-response.py"], text=True, env=env, check=True,
               input=json.dumps({"last_assistant_message": "最初の音までを測る、短い文です。"}))
pid = Path(tmp, "claude-tts.pid")
if not pid.exists():
    raise SystemExit(Path(tmp, "claude-tts.unusable").read_text())
pgid = pid.read_text()
while subprocess.run(["pgrep", "-g", pgid, "-x", "pw-play"], stdout=subprocess.DEVNULL).returncode:
    if time.monotonic() - t0 > 60:
        raise SystemExit("60 秒たっても鳴らない")
    time.sleep(0.01)
print(f"{time.monotonic() - t0:.2f} 秒")
PY
```

目安は [README の「動き方」](../README.md#動き方) にある。
