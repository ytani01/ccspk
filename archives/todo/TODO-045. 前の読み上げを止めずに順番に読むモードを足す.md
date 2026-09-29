# TODO-045. 前の読み上げを止めずに順番に読むモードを足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 40,469 | 130,350 | 73% |
| reviewer | Opus 5.5 | high | 4,343 | 90,235 | 24% |
| verifier | Sonnet 5.5 | medium | 347 | 39,595 | 3% |
| 合計 |  |  | 45,159 | 260,180 | 概算 $4.7 |

- reviewer・verifier とも、モデルと effort は定義（`~/.claude/agents/`）のまま
- main の分には、途中で TODO-046・TODO-047 を立てたやり取りも入っている
- verifier の分は少なめに出ている見込み（`subagents/` のログに最終行が残らないことがある）

## きっかけ

フックは文章が来るたびに `stop_playing()` で前の子プロセスを止めてから読んでいた。途中の文章が続くと前の文章が冒頭で
切れるので、止めずに来た順に全部読むモードが欲しかった。

決めたこと（2026-09-29 に利用者と）:

- `ccspk summary` と同じ形（`~/.config/ccspk/queue` の有無）。環境変数での上書きは付けない
- 待ちの数や時間に上限は付けない。子プロセスの面倒を見る範囲は、来た順・全部止める・上限なし、まで
- 5 秒のうちに同じ文章が来たら読まない決まり（`SAME_WITHIN`）は残す
- 前の子プロセスの終わりは pidfd で待つ。`uv` の Python 3.13 に `os.pidfd_open` が無かったので、
  利用者の指示で `requires-python` を `>=3.14` に上げた（システムの 3.14 にも `uv` の 3.14 にもあることを確かめた）

## やったこと

- `hook.py`
  - `ccspk queue [on|off]`（`queue_`）。`summary` と共通の `switch()` でファイルを作る・消す
  - `PIDFILE` を 1 行 1 PID に。`ours()`（`/proc/<pid>/cmdline` で再生の子プロセスか見る）と `playing()`（動いているものを起こした順に）を足した
  - `stop_playing()` は `PIDFILE` の全部を後ろから止める
  - `speak(text, to_summarize, queued)`: queue なら動いている子プロセスを残し、最後のものを `os.pidfd_open()` で開いてから
    `ours()` で確かめ、`--after=<fd>` と `pass_fds` で新しい子プロセスに渡す
  - 子プロセス（`run_child()`・`play_summary()`）は、要約と記録を済ませてから `wait_for()` で pidfd を `select()` し、前が終わってから鳴らす
  - `main()`: queue で文が空でないときだけ止めない。空の `Stop` は queue でも全部止める
  - `demo()`: 引数の振り分け（`--after=`）、pidfd の相手が終わるまで鳴らさないこと、`playing()`・`stop_playing()`（偽の子プロセスで）、
    `speak()` が最後の子プロセスの pidfd を渡し `PIDFILE` に足すこと（`Popen` を差し替えて）、`switch()`
- `cli.py` に `queue` を登録。`pyproject.toml`・`uv.lock` を Python 3.14 に
- 文書: `docs/UsersGuide.md` に「1.7」と「3.7 ccspk queue」を足し、後ろの節番号と内部リンクをずらした。「3.2」「3.4」も直した。
  `docs/Developer.md` の 2・3.1・3.2・3.3・3.5・3.7・4.1・4.2、README.md、CLAUDE.md のサブコマンドの並び

## 確かめたこと

- `uv run ccspk test` が ok
- reviewer: 要修正 0 件。`speak()` と `main()` の分岐を壊しても `demo()` が通ると指摘を受け、`speak()` のテストを足した
  （渡す pidfd を最初の子プロセスにする・`pass_fds` を外す、のどちらで壊しても落ちることを main が確かめた）。
  `main()` の分岐は verifier の実機で確かめた。4.2 に `XDG_CONFIG_HOME` の手順を足した
- verifier（実機）: 7 項目とも期待どおり
  - queue on で 3 つを 0.3 秒おきに渡すと、`PIDFILE` の順に 1 つずつ最後まで鳴り、同時に 2 つ鳴ることは無かった（2 回）
  - 鳴っている間の `ccspk stop` と空の `Stop` で、子プロセス・`pw-play` が全部消え、`PIDFILE` も消えた
  - queue off では前が切れて新しいほうだけ鳴り、`PIDFILE` は 1 行
  - 要約を入れ、後の文の要約が先にできても、前の文から鳴った
  - `ccspk queue` の表示と、範囲外の引数で終了コード 2

## 残ること

- queue on のとき、返答の最後の文章は MessageDisplay と Stop の両方から来る。整えた文が 1 字でも違うと 2 度読む
  （今までは後から来たほうが前を止めていた）。違うことがあるかは確かめていない。使っていて 2 度読むようなら項目を立てる

## 分担の振り返り

- reviewer は、`speak()` と `main()` の queue の分岐を壊しても `demo()` が通ること（7 通り実測）と、4.2 の手順の不足、
  MessageDisplay と Stop の食い違いで 2 度読む恐れを見つけた。どれも main が見落としていた。verifier は食い違いを見つけなかった
- 見込みと実施は食い違わなかった。料金の 7 割は main で、途中で `uv` の 3.13 に `os.pidfd_open` が無いと分かり、ポーリングに書き換えてから
  3.14 で pidfd に戻した分が重い。実装の前に、使う API が `.venv` の Python にあるかを 1 行で確かめておけば避けられた
- 次に子プロセスの扱いを変える同じ規模の項目では、同じ 3 役でよい。main は、分岐を変える関数（今回の `speak()`・`main()`）を
  `demo()` で通すテストを最初から書き、reviewer の「壊しても通る」の指摘を 1 巡目で出させないようにする
