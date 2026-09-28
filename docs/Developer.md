# 開発者向け

フックのコードは `hooks/speak-response.py` の 1 ファイルだけ（辞書に語を足す
`voicevox/add-word.py` は別に動く）。依存は Python の標準ライブラリ、
VOICEVOX のエンジン（`127.0.0.1:50021`）、`pw-play`。読み上げの範囲や切り方など、
利用者から見た動きは下の「動き方」、入れ方と辞書は
[UsersGuide](UsersGuide.md) にある。

## 動き方

- 環境変数 `CLAUDE_TTS_SPEAK` が `1` のときだけ鳴る
- 読み上げるのは整形した先頭 180 文字（30 秒ほど）。超えるときは、文の途中で
  切らないよう、180 字目から 240 字目までで最初の文末まで読む。文末が無ければ
  読点まで、それも無ければ 180 字で切る。コードブロックは
  「コード省略」に置き換え、表・Markdown の記号・リンクの URL は消す
- 読み間違いを減らすため、「〜」「→」などを「から」に置き換え、数字の後に
  日本語が続くときは間のスペースを消す。語の読みはエンジンの辞書で直す。どちらも
  [UsersGuide.md](UsersGuide.md#読み上げの辞書) にある
- 文ごとに合成し、1 文目ができたらすぐ鳴らす。2 文目以降は鳴らしている
  間に合成する。短い文の直後に長い文が来ると、継ぎ目で数秒待つことがある
- 1 文目はさらに前後 2 つに切り、前半ができたらすぐ鳴らす。切るのは 8 字より
  後ろで最初に現れる読点・閉じ括弧・コロンの後ろか、開き括弧の前。それらが
  30 字以内に無いときだけ、その手前のスペースで切り、スペースも無ければ
  30 字より後ろの区切りで切る。後半が句点だけになる所や、`12:30`・`name()` の
  ような語の中の半角「:」「(」では切らない。切った所は抑揚が文末のように
  下がる。最初の音までは、エンジンが空いていれば 1.2〜2.5 秒ほど
- 返答の最後の文章に加えて、ツールを呼ぶ前などの途中の文章も読む（`MessageDisplay`）。
  ただし `MessageDisplay` が起動しない文章があり、それは読まない。起動する条件は分かっていない
- 再生中に次の文章が来たら、前の再生を止めて新しいほうを読む。途中の文章が続けて来ると、
  前の文章は冒頭で切れる
- 読んでから 5 秒のうちに同じ文章が来たら読まない。返答の最後の文章は `MessageDisplay` と
  `Stop` の両方から（実測では 0.01 秒差で）来るので、2 度読まないため
- 表だけ・URL だけのように、整えると空になる途中の文章では、前の再生を止めない。
  `Stop` が空のときは、今までどおり止める
- サブエージェントの報告では鳴らない（`SubagentStop` は登録せず、`MessageDisplay` も
  `agent_id` があれば読まない）
- `pw-play` が無い、エンジンに接続できない、PipeWire が動いていない、のどれかなら
  鳴らさずに終わり、使えないことを覚えて、次からは確かめもせずに終わる。
  戻し方は [UsersGuide.md](UsersGuide.md#使えないと覚えたとき) にある

## フックの仕組み

### 流れ

Claude Code は、返答を終えるたびに Stop フックとして、文章を表示するたびに
MessageDisplay フックとしてこのスクリプトを起動し、標準入力に JSON を渡す。
使うのは、Stop なら `last_assistant_message`（最後の返答の本文）、MessageDisplay なら
`message_id`・`index`・`delta`・`final`。MessageDisplay は 1 つの文章を `index` ごとの分
（`delta`）に分けて渡し、最後の分に `final: true` が付く。フックは並んで走り、後ろの分が
先に届くこともある。`agent_id` があるとき（サブエージェント）は読まない。

`main()` は引数で 3 つに分かれる。

| 起動のされ方 | 動き |
|---|---|
| `--test` | `demo()` の自己テストを走らせる |
| `--play <本文>` | 子プロセスとして、合成と再生をする（`play()`） |
| 引数なし | フックとして動く（下の順） |

フックとしては、次の順に進む。どこかで条件を満たさなければ、そこで終わる。

1. 環境変数 `CLAUDE_TTS_SPEAK` が `1` か
2. 使えないと覚えたファイル（`UNUSABLE`）が無いか。あれば確かめもせずに終わる
3. `unusable()` で鳴らせるかを確かめる。だめなら理由を `UNUSABLE` に書いて終わる
4. 標準入力の JSON を読む。MessageDisplay で `agent_id` があれば終わる
5. `LOCK` を取る。ここから先は、同時に来たフックを 1 つずつ通す
6. MessageDisplay なら、`assemble()` で分を `PARTS` に置く。最後の分とそれより前の分が
   そろっていなければ終わる。そろったらつなぎ、置いた分を消す。`PARTS_KEEP` 秒より古い分もここで消す
7. `to_speech()` で読み上げる文に整える。MessageDisplay で空になったら終わる
8. 整えた文が `LAST`（最後に読んだ文）と同じで、書いてから `SAME_WITHIN` 秒のうちなら終わる
9. `stop_playing()` で前の再生を止める
10. 文が空でなければ、`LAST` に書き、`speak()` で子プロセスを起こし、その PID を `PIDFILE` に書く

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

どれも `$XDG_RUNTIME_DIR` に置く。`$XDG_RUNTIME_DIR` が無い環境では `/tmp` に、
利用者の uid を名前に入れて置く。

| 定数 | 場所 | 中身 |
|---|---|---|
| `PIDFILE` | `claude-tts.pid`（`/tmp/claude-tts-<uid>.pid`） | 再生中の子プロセスの PID |
| `UNUSABLE` | `claude-tts.unusable`（`/tmp/claude-tts-<uid>.unusable`） | 鳴らせない理由 |
| `LAST` | `claude-tts.last`（`/tmp/claude-tts-<uid>.last`） | 最後に読んだ文（整えた後） |
| `LOCK` | `claude-tts.lock`（`/tmp/claude-tts-<uid>.lock`） | 同時に来たフックを 1 つずつ通すためのロック |
| `PARTS` | `claude-tts.parts/`（`/tmp/claude-tts-<uid>.parts/`） | MessageDisplay の分。`<message_id>.<index>` と、最後の分の番号を書いた `<message_id>.final` |

### 整形と分割

| 関数 | すること |
|---|---|
| `to_speech()` | コードブロックを「コード省略」に置き換え、Markdown の記号・表・URL を除き、記号と数字の読みを整え、最後に `clip()` を通す |
| `clip()` | `LIMIT` 字を超えるときに、文の途中で切らないように縮める |
| `sentences()` | 文末（`ENDS`）の後ろで文に分ける |
| `split_first()` | 1 文目を、最初の音を早めるために前後 2 つに切る |
| `chunks()` | 合成する単位。1 文目だけ `split_first()` で切り、2 文目以降は文ごと |

どこで切るかの決まりは [「動き方」](#動き方) に、
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
python3 voicevox/add-word.py --test   # アクセントの位置の決め方（accent_of）
```

MessageDisplay の分をつなぐ `assemble()` も、一時ディレクトリで確かめている。
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

使えると判定して子プロセスを起こせば、`$tmp/claude-tts.pid`・`$tmp/claude-tts.last`・
`$tmp/claude-tts.lock` ができる。MessageDisplay として試すなら、
`{"hook_event_name":"MessageDisplay","message_id":"m1","index":0,"final":true,"delta":"…"}` を渡す
（`$tmp/claude-tts.parts/` もできる）。5 秒のうちに同じ文を渡すと、`claude-tts.pid` の PID は
変わらない（2 度読まない）。JSON に `\n` を入れるときは、zsh の `echo` は改行に変えてしまうので
`printf '%s'` で渡す。
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

目安は [「動き方」](#動き方) にある。
