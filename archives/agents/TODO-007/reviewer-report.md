# TODO-007 reviewer の報告

対象: 未コミットの `docs/Developer.md`（新規）と `README.md` の 1 行。
プロジェクトの `CLAUDE.md` は無いので、利用者全体の `CLAUDE.md` と TODO-007 節の
決めごと（開発の進め方・設計判断のまとめは書かない、重なる所は案内で済ませる）に照らした。

コードとの突き合わせで合っていたもの（1 行ずつ）:

- `main()` の 3 分岐と、Stop フックとしての 1〜6 の順（`speak-response.py:291-313`）
- `speak()` の起動引数と `start_new_session=True`、`play()` のスレッドとキュー・終わりの印
- `synthesize()` の 2 つの API と `timeout=60`
- `stop_playing()` の「PID を読む → ファイルを消す → cmdline を見る → `killpg(SIGTERM)`」
- `unusable()` の順（`pw-play` → TCP → `PIPEWIRE_REMOTE` なら飛ばす → `pipewire-0`）と場所の決め方
- ファイルの場所（`BASE` / `PIDFILE` / `UNUSABLE`）、関数の表、定数の値（10 個すべて）
- 「3 つ合わせて 1 ms ほど」: `unusable()` を 3 回測って 0.85 / 0.13 / 0.09 ms
- アンカー: `../README.md#動き方` は README の `## 動き方`、`UsersGuide.md#記号と数字` は
  UsersGuide の `### 記号と数字` と一致。README の既存リンクと同じ書き方
- `README.md:13` の 1 行は表の形・語の選び方とも揃っている

## 要修正

### 1. `docs/Developer.md:142-146` `PATH` を空にする手順が、この環境では python が起動しない

- 何が: `PATH=/nonexistent "$(command -v python3)" hooks/speak-response.py` は、
  `command -v python3` が mise の shim（`/home/ytani/.local/share/mise/shims/python3`）を
  返すため、shim が `PATH` から本物の python を探せずに落ちる。
- 根拠（実測）: scratchpad の一時ディレクトリで書かれたとおりに実行すると
  `mise ERROR No version is set for shim: python3`、終了コード 1。
  `claude-tts.unusable` はできない。普段の `python3` は `/usr/bin/python3`
  （`sys.executable`）に解決されている。
- なぜ問題か: 手順の目的（`pw-play が無い` を再現する）が作者自身の環境で果たせない。
  `cat $tmp/claude-tts.unusable` は `No such file` になる。

### 2. `docs/Developer.md:161-171` 測り方のループに上限が無く、鳴らないと止まらない

- 何が: `while pgrep -x pw-play ...: sleep(0.01)` に時間の上限が無い。
  フックが子プロセスを起こさない場合、いつまでも回り続ける。
- 起こる条件（コードから）: 本物の `$XDG_RUNTIME_DIR` に `claude-tts.unusable` が
  **既に**ある（`main()` の 298 行で即終わる）、`unusable()` がだめと判定した、
  合成が失敗した（子は `stderr=DEVNULL` なので黙って終わる）。
  直前の `curl .../version` の確認はエンジンが動いているかしか見ないので、
  1 つ目（既にファイルがある）は防げない。
- 前の測り方（`archives/agents/TODO-003/measure.py`）には 60 秒の上限と、
  PID ファイルのプロセスグループに絞った `pw-play` の探し方があった。今回の版は
  両方が抜けている（archives は仕様ではないので、比較としてだけ挙げる）。
- 実害は未確認（実行はしていない。verifier の範囲）。

## 検討

### 3. `docs/Developer.md:156-176` 測り方だけ本物の `$XDG_RUNTIME_DIR` を使う理由が無く、注意が足りない

依頼の観点「本物を汚さない目的に照らして穴が無いか」への答え。

- `curl` で起動を確かめる注意は「エンジンが止まっている」ときだけを防ぐ。
  上の 2 のとおり、既に `claude-tts.unusable` があるときは測れず（止まらない）、
  PipeWire 側でだめなときは本物に `claude-tts.unusable` が残る。
- 本物の `claude-tts.pid` を書き換え、`stop_playing()` で**そのとき鳴っている本物の
  読み上げを止める**。この副作用が書かれていない。
- 「再生中のほかの `pw-play` があると、そちらを拾うので、止めてから測る」とあるが、
  止め方が書かれていない。また、フック自身の `stop_playing()` が送る `SIGTERM` と
  `pgrep` の間で、止められる途中の `pw-play` を拾う余地がある（実害は未確認）。
- 上の「Stop を手で再現する」と同じ一時ディレクトリ＋`PIPEWIRE_RUNTIME_DIR` の形で
  測れない理由が見当たらない。本物を使う必要があるなら、その理由を書く。

### 4. `docs/Developer.md:138` 「鳴れば、`$tmp/claude-tts.pid` だけができる」

- `speak()` は `Popen` の直後に PID を書く（`speak-response.py:192-200`）。
  子の合成や再生が失敗しても PID ファイルはできる。PID ファイルが分かるのは
  「使えると判定して子を起こした」ところまでで、「鳴った」ではない。
- 子は `stdout`/`stderr` を捨てるので、鳴らないときの原因は見えない。
  150-154 行の `--play` を直接起こす手順がその切り分けになる、と書けば足りそう。

### 5. `docs/Developer.md:142-148` 2 つ目の手順が、1 つ目の `$tmp` を使い回す

- 1 つ目で使えないと判定されていると `$tmp/claude-tts.unusable` が既にあり、
  2 つ目は 298 行で即終わる。`cat` には 1 つ目の理由が出て、`pw-play が無い` を
  再現できたように見えない（または別の理由が出る）。コードから読んだもので、実行はしていない。

### 6. README・UsersGuide と同じことを 2 か所に書いている所

TODO-007 節の「同じことを書く所は、どちらかへの案内で済ませる」に照らして。

| Developer.md | 重なる先 |
|---|---|
| 174 行「エンジンが空いていれば、1.2〜2.5 秒ほど」 | `README.md:36` に同じ数字 |
| 117-119 行の `--test` のコマンド | `docs/UsersGuide.md:37-41`（こちらは絶対パス） |
| 66-68 行の `PIPEWIRE_REMOTE` を確かめない理由 | `docs/UsersGuide.md:77-78` |
| 74-80 行の `UNUSABLE` の場所 | `docs/UsersGuide.md:80-81` |
| 32 行「登録の `timeout` は 5 秒」 | `docs/UsersGuide.md:59` |

- 1 つ目は数字なので、測り直したときに片方だけ変わりやすい。
- 残りは仕組みの説明として置く意味もあり、境界線上。実害は未確認。

### 7. `docs/Developer.md:126` 「そのログインのあいだ読み上げが止まる」

- `docs/UsersGuide.md:89-91` は「セッションが全部終わると消える（linger なら
  再起動まで）」。「そのログインのあいだ」は linger のときと食い違う。
  UsersGuide の「使えないと覚えたとき」への案内にすれば重ならない。

### 8. `docs/Developer.md:86` `to_speech()` の「コードブロック…を除き」

- コードブロックは除くのではなく「コード省略。」に置き換える（`speak-response.py:73`）。
  README の「動き方」は「置き換え」と書いている。

### 9. `docs/Developer.md:38-39` 「新しいプロセスグループにするので、フックが終わっても残り」

- `start_new_session=True` は setsid（新しいセッション、兼プロセスグループ）。
  `Popen` の子は、親が終わるだけなら新しいグループでなくても残る。
  「フックが終わっても残る」理由がグループ分けにあるのか（Claude Code がフックの
  グループを止めるのか）は確かめていない。未確認。後半の「グループごと止められる」は正しい。

## 好みの範囲

### 10. `docs/Developer.md:23` 「どこかで条件を満たさなければ何もせずに終わる」

- 3 番目はだめなとき `UNUSABLE` を書いて終わるので、「何もせずに」と合わない。

### 11. `docs/Developer.md:131-148` コマンドがリポジトリの直下で走らせる前提

- `hooks/speak-response.py` が相対パス。UsersGuide は `~/work/claudecodespeak/...` の
  絶対パスで書いている。前提を 1 行書くか、揃えるか。

## 作り込みすぎ

- `docs/Developer.md:174`: delete: README と同じ 1.2〜2.5 秒。README への案内、または削る（検討の 6）。
- `docs/Developer.md:66-68,74-80`: shrink: UsersGuide と重なる理由と場所。仕組みに要る 1 行と案内に縮められる（検討の 6、境界線上）。
- net: -4 行ほど。

日本語: 全体に自然。直訳調の所は見当たらなかった。
