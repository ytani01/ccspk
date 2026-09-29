# TODO-045 reviewer 報告

対象: 依頼時の `git diff`（hook.py・cli.py・pyproject.toml・uv.lock・docs・README.md・CLAUDE.md・TODO.md）。
コードは直していない。壊して試した hook.py は元に戻し、`git diff` が依頼時と同じことを `cmp` で確かめた
（途中で HEAD が 9f393fb「TODO-046 として立てる」に進んだため、TODO.md の `index` 行の blob だけ変わっている。中身の差分は同じ）。

自己テストは一時ディレクトリの `XDG_RUNTIME_DIR`・`XDG_STATE_HOME`・`XDG_CONFIG_HOME` で `uv run ccspk test` を走らせた（ok）。

## 要修正

なし。

## 検討

### 1. demo() が speak() と main() の queue の分岐を捕まえない

- 場所: `src/ccspk/hook.py:455-483`（`speak()`）、`hook.py:824-826`（`main()` の `if not (queued and text)`）
- 内容: 次のように壊しても `uv run ccspk test` は `ok` のまま通った（実測。1 件ずつ差し替えて走らせ、元に戻した）。

  | 壊し方 | 結果 | 壊れると起きること |
  |---|---|---|
  | `pass_fds=...` を消す | 通る | 子プロセスの `--after=N` が開いていない fd になり、`select()` が `OSError` で落ちて読まない（未確認） |
  | `os.pidfd_open(before[-1])` を `before[0]` に | 通る | 3 つ目以降が 1 つ目だけを待ち、2 つ目と同時に鳴る |
  | `PIDFILE` に新しい PID だけ書く | 通る | `ccspk stop` が待っている分を止められない |
  | `before = playing() if queued else []` を `before = []` に | 通る | queue on でも待たずに重なって鳴る |
  | 開いた後の `ours()` の確かめを消す | 通る | 番号が使い回されたとき関係の無いプロセスを待つ |
  | `main()` の条件を `if True:`（常に止める） | 通る | queue on でも前を止める |
  | `main()` の条件を `if False:`（止めない） | 通る | queue off でも止めない・空の Stop で止めない |

- なぜ: 要件の中心（来た順・全部止める）がこの 2 か所にあり、demo() は `run_child()`・`wait_for()`・`stop_playing()`・`playing()` しか通らない。
  verifier の実機確認で拾えるものが多いが、実機で「重なって鳴った」を聞き分けるのは確かめ方次第。
  実害は未確認。テストを足すかどうかは管理者の判断。

### 2. stop_playing() の「後ろから止める」を demo() が捕まえない

- 場所: `hook.py:311-316`、demo の `hook.py:746-774`
- 内容: `reversed(pids)` を `pids`（前から）にしても通った（実測）。1 つだけ止める（`pids[-1:]`・`pids[:1]`）は `TimeoutExpired` で落ちた（実測）。
  demo の偽の子プロセスは互いを待っていないので、順番の違いが出ない。
- 補足: 前から止めても、SIGTERM は既定の動作で即座に殺すので、待っていた子プロセスが鳴り出す隙は極めて短いはず（未確認）。
  コメントと `Developer.md` 3.3 の「前から送ると、…鳴り出してしまう」は実測ではなく見立てに読める。実害は未確認。

### 3. queue on の Stop と MessageDisplay の文が食い違うと 2 度読む

- 場所: `hook.py:818-826`
- 内容: 今までは `SAME_WITHIN` を外れても、後から来た Stop が前の読み上げを止めて読み直すので、聞こえるのは実質 1 回だった。
  queue on では両方を順に読むので、返答の最後の文章の `assemble()` の結果と `last_assistant_message` を整えた文が
  1 文字でも違うと 2 度読む。違うことがあるかは確かめていない（未確認）。要件（`SAME_WITHIN` は残す）の範囲内で、実害は未確認。

### 4. 「4.2 フックを手で動かす」に queue の試し方が無い

- 場所: `docs/Developer.md` の 4.2（今回の差分の外）
- 内容: `QUEUE` は `XDG_CONFIG_HOME` の下にあるので、4.2 の手順のままだと利用者が `ccspk queue on` にしているかで動きが変わる。
  queue を試すには `XDG_CONFIG_HOME` も一時ディレクトリに向けて `queue` を置く必要があるが、書いていない。
  「`ccspk.pid` の PID は変わらない」も 1 行 1 つになった今は「中身は変わらない」のほうが合う。
  verifier に渡す手順にも関わる。依頼の文書の範囲（2・3.x・4.1）の外なので報告だけ。

## 好みの範囲

- `hook.py:46` の `MODULE` のコメント「stop_playing() はこれで見分ける」。見分けるのは `ours()` になった（`playing()` と `speak()` からも使う）
- `hook.py:851` の `stop` の docstring（`--help` に出る）が「鳴っている読み上げを止める」のまま。UsersGuide 3.4 と `Developer.md` の表は「待っている分も」に直してある

## 作り込みすぎ

- `hook.py:700`: delete: 偽の `play` が記録する `time.time()` はどの assert も使っていない。`("play", t)` で足りる（`[c[:2] for c in calls]` は summary 側の 3 要素のために残る）
- `hook.py:700-701`: delete: `# noqa: E731` は効いていない（`ruff check` が RUF100 Unused noqa を出す。HEAD には無かった指摘）。元の 1 行のタプル代入に戻せば noqa も要らない
- `hook.py:458-467`: shrink: `after = None` → `if before:` → `try` の 3 段。`try: after = os.pidfd_open(before[-1]) if before else None` / `except OSError: after = None` にすると 2 行減る

net: -4 lines possible.

## 問題なしの観点（1 行ずつ）

- `ours()`・`playing()`: 動いていない PID・使い回された番号・`x` のような壊れた行を除く（demo で実測。`playing()` から `ours()` を外すと落ちる）
- `wait_for()`: 何もしない関数にすると demo が落ちる（実測）。pidfd は `select()` のあと閉じる。EINTR は PEP 475 で再試行される
- `run_child()`: 本文が `--summarize`・`--after=3` で始まっても本文は最後の引数なので旗と取り違えない（demo にある）。`--after` を無視すると落ちる（実測）
- `speak()` の fd: `pidfd_open` の失敗・`ours()` で外したとき・`Popen` が例外を出したとき、どれも閉じる。二重に閉じる経路は無い
- pidfd を `pass_fds` で渡した子が、同じ番号の fd で前のプロセスの終わりを待てることを `.venv` の Python で実測（1 秒の `sleep` に対して 1.0 秒待った）
- `play_summary()`: 要約と記録を済ませてから待つ。待つ位置を要約の前にしても順番は崩れない（demo も通る）ので、ここは速さのための順で、要件は満たす
- LOCK: hook の `playing()`〜`PIDFILE` 書き換えと `ccspk stop` の読み取り〜`unlink` は同じ LOCK の中。子プロセスは LOCK を持ったまま待たないので、待ちと LOCK で詰まることは無い
- 要約中に前が終わった場合: `wait_for()` はすぐ返り、そのまま鳴る
- off に切り替えた直後: 待っている分はそのまま鳴り、次の文章（または空の Stop）で `stop_playing()` が全部止める。文書の「次の文章から効く」と合う
- 空の Stop・空の MessageDisplay: 空の MessageDisplay・PreToolUse は止める前に返り、空の Stop だけが queue on でも全部止める。`Developer.md` の手順 9 と合う
- `SAME_WITHIN`: queue の分岐より前にあり、このモードでも残る
- 要件の範囲: 待ちの数・時間の上限、フックが落ちた後の掃除は足していない。`switch()` の切り出しは `summary` と `queue` の 2 か所で使うので妥当
- `requires-python >=3.14`: `uv` の 3.13.14 と 3.11 に `os.pidfd_open` が無く、システムと `uv` の 3.14.7 にはあることを実測。入れてある `ccspk` の Python は 3.14.7
- 文書: Developer.md の 2・3.1 の表・手順 9/10・3.2・3.3・3.5・3.7・4.1、UsersGuide.md の 1.7・3.2・3.4・3.7 はコードと合う。UsersGuide の節番号のずらしで、内部リンク（`#37`〜`#314` など）は全部、実在する見出しを指している。README・Developer.md から UsersGuide の 3.x を指すリンクは無い
- 範囲: 指示に無い変更は無い（`summary` の `switch()` 化は queue と共通にするため）
