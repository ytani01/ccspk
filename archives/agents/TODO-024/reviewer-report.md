# TODO-024 reviewer 報告

対象: 未コミットの `git diff`（CLAUDE.md, docs/Developer.md, docs/UsersGuide.md,
src/ccspk/cli.py, src/ccspk/hook.py）。仕様は `TODO.md` の TODO-024。

## 要修正

なし。

## 検討

### 1. `src/ccspk/hook.py:137-149`（`stop_playing()`）/ `hook.py:452-454`（`stop`）: `ccspk stop` が LOCK を取らない

- 何が: `main()` は `LOCK` を持ったまま `stop_playing()` → `speak()`（PIDFILE を書く）と進むが、
  `ccspk stop` は LOCK を取らずに PIDFILE を読む → 消す。
- なぜ: 次の順に並ぶと、新しく起きた子プロセスの PIDFILE を `ccspk stop` が消し、
  止めたのは古い（もう居ない）PID なので「鳴っていない」と出て、新しい読み上げは鳴り続ける。
  さらに PIDFILE が消えているので、次のフックでもその再生を止められず重なる。
  1. `ccspk stop` が PIDFILE を読む（新しい PID を読む前、または読んだ直後）
  2. フックが `speak()` で PIDFILE を書き直す
  3. `ccspk stop` が `unlink()` する
  フック同士は LOCK で 1 つずつ通るので、この競合は `stop` を足したことで初めて生じる
  （コードを読んで確認）。窓はマイクロ秒単位で、**実害は未確認**（再現は試していない）。
  利用者が手で打つコマンドなので、起きる見込みは小さい。

### 2. `docs/UsersGuide.md:112` / `docs/Developer.md:63`: 合成を待っている間も「止めた」と出る

- 何が: 子プロセス（`--play`）は、エンジンの合成を待っていてまだ音が出ていない間も
  生きているので、`ccspk stop` は `True` →「止めた」になる。文書は「鳴っていれば止めて
  『止めた』」と書いている。
- なぜ: 子プロセスを止めればこれから鳴るはずの分も鳴らなくなるので、動きとしては
  利用者の期待どおり（仕様の「止めるのは再生だけ」にも反しない。子プロセスが止まっても
  エンジンの合成は続く、は文書のとおり）。文言の「鳴っていれば」が厳密でないだけ。
  直すかは判断次第。

## 好みの範囲

- `docs/Developer.md:108`: 「送ったら `True` を返す。」を足した行だけ、他の行より長い
  （折り返しを直していない）。送らなかったときに `False` を返すことは書いていないが、
  「送ったら True」で読める。

## 観点ごとの結果

- フック（`main()`）への影響: なし。`hook.py:432` は戻り値を使っておらず、例外の扱い
  （`OSError`・`ValueError` を握りつぶす）も変わっていない。
- True/False の経路: 抜けなし。`killpg` が成功したときだけ `True`。PIDFILE が無い・中身が
  数字でない・`/proc/<pid>` が無い（再生が終わっている）・目印が無い・`killpg` が
  `ProcessLookupError`/`PermissionError` のいずれも `False`（`try` の末尾で暗黙の
  `None` を返す経路は無い）。
- メッセージの出し分け（実測。`XDG_RUNTIME_DIR` を scratchpad に向けて実行）:
  PIDFILE 無し →「鳴っていない」、中身が `garbage` →「鳴っていない」、別プロセスの PID →
  「鳴っていない」（PIDFILE は消える）、`--play` と `ccspk.hook` を argv に持つ `setsid` した
  プロセス →「止めた」でプロセスは消えた、続けてもう一度 →「鳴っていない」。終了コードは
  どれも 0。`ccspk --help` に `stop` が出る。
  なお中身が数字でない PIDFILE は消されずに残る（`int()` が先に落ちるため）。変更前から同じで、
  次の `speak()` が上書きするので実害なし。
- 直し漏れ（指定の `rg`）: なし。CLAUDE.md:6、Developer.md:4・57（「4 つ」は hook・say・stop・
  status で正しい）・63・80・107・160・161、cli.py:1・9 がいずれも stop を足した内容と合う。
  README.md にはサブコマンドの列挙が無い。
- 文書とコードの一致: UsersGuide「鳴っている読み上げを止める」、Developer.md の表・
  「前の再生を止める」とも、コード（`stop` のメッセージ、エンジンの合成は止めない）と一致
  （上の検討 2 の言い回しを除く）。置き場所も「読み上げを無効にする」「読み上げが止まった
  ままのとき」と並びで既存の構成に沿う。
- 規約違反: なし。
- テスト: 足さなくてよい。整形・分割の変更ではなく（CLAUDE.md の「`demo()` に例を足す」の
  対象外）、`stop_playing()` を `demo()` から呼ぶと本物の PIDFILE に触れるので、足すべきでない。
- コメント: docstring の追記（「止めたら True を返す」）で足りる。
- 範囲: 指示に無い変更なし。
- 作り込みすぎ: なし（`stop` は 1 行、`stop_playing()` は `return` を 2 か所足しただけ）。
  Lean already. Ship.
