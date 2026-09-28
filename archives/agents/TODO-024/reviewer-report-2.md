# TODO-024 reviewer 報告 2（指摘 1・2 の直し方）

対象: 今の `git diff` のうち `src/ccspk/hook.py` の `stop()`、`docs/UsersGuide.md` と
`docs/Developer.md` の文言。測るときは `XDG_RUNTIME_DIR` を scratchpad に向けた。

## 要修正

なし。

## 検討

### 1. `src/ccspk/hook.py:455`: LOCK を開けないと `ccspk stop` が traceback で落ちる

- 何が: `stop()` は `open(LOCK, "w")` を `try` で包んでいない。`main()`（`hook.py:407-411`）は
  `OSError` なら `lock = None` にしてロック無しで進むが、`stop()` はそのまま例外になる。
- 根拠（実測）:
  - `XDG_RUNTIME_DIR` を存在しないディレクトリにして `ccspk stop` →
    `FileNotFoundError: ... nonexistent/ccspk.lock`、終了コード 1
  - `ccspk.lock` を `chmod 000` にして `ccspk stop` → `PermissionError`
- なぜ問題か: どちらのときも PIDFILE は読めない（同じディレクトリ）か、止める対象が
  無いので、本来の答えは「鳴っていない」。利用者に traceback を見せることになる。
  実際にこうなる環境（`$XDG_RUNTIME_DIR` が消えている、`sudo` 越しなど）が起きるかは
  **実害は未確認**。`main()` と同じ扱い（開けなければロック無しで進む）に揃えるかは判断次第。

## 好みの範囲

- `hook.py:55` の `LOCK` のコメント「PARTS と LAST を触るあいだは 1 つずつ通す」と、
  `docs/Developer.md` のファイルの表の `LOCK` の行「同時に来たフックを 1 つずつ通すためのロック」
  は、PIDFILE（`stop_playing()`・`speak()`）と `ccspk stop` を守る用途を書いていない。
  `stop()` のコメントには理由があるので、読んで困ることは少ない。

## 観点ごとの結果

- 指摘 1（競合）の直し方: 足りている。`main()` は `stop_playing()` と `speak()`
  （PIDFILE を書く）を LOCK の内側で呼ぶ（`hook.py:432-437`）ので、`stop()` が同じ LOCK を
  取れば、読む→消すの間に PIDFILE が書き換わることは無い。
- フックが LOCK を長く持つ経路: 無い（コードを読んで確認）。LOCK の内側は `assemble()`
  （PARTS のファイル操作）・`questions()`・`to_speech()`（文字列処理）・`stop_playing()`・
  `speak()`（`Popen` して PIDFILE を書くだけ）で、ネットワークや待ちは無い。
  `unusable()` の接続確認（timeout 1 秒）と `json.load(sys.stdin)` は LOCK の前。
  合成（`urlopen` timeout 60 秒）は子プロセスの中で、子プロセスは `Popen` の既定
  `close_fds=True` で LOCK の fd を受け継がない。
  別プロセスで LOCK を 2 秒持たせたところ、`ccspk stop` はそれが離れるまで待って
  （実測 1.72 秒）「鳴っていない」と出た。待ち方に問題は無い。
- `stop()` が LOCK のファイルを作ること: `main()` と同じ場所・同じ開き方なので問題なし。
- 指摘 2（文言）: UsersGuide の「読み上げの途中なら（最初の音を待っているあいだも含む）
  止めて『止めた』」はコードと合う。Developer.md の表の「`LOCK` を取ってから」も合う。
- 作り込みすぎ: なし。Lean already. Ship.
