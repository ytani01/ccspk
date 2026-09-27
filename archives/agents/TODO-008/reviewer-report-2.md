# TODO-008 reviewer 報告（2 回目）

対象: `git diff`（.gitignore, README.md, TODO.md, settings.json）と未追跡の
hooks/speak-response.py, systemd/voicevox-engine.service。前回「問題なし」で変わっていない観点は見ていない。
実測は 2026-09-28、手元の環境で行った。

要修正: 0 件 / 検討: 3 件 / 好みの範囲: 2 件 / 報告だけ: 2 件

## 検討

### 1. hooks/speak-response.py:28 — 行頭が ``` で始まる地の文は、末尾まで「コード省略」になる
- 閉じていないブロックを末尾まで省くようにしたため、フェンスの説明などで行頭に ``` を書いた
  地の文は、それ以降がすべて消える（実測: "``` の中は読まない。\n本文は続く" → "コード省略。"）。
  "~~~取り消し~~~ の話\n続き" も "コード省略。" になる（実測）。
- 4 つのバッククォートで ``` を囲んだ入れ子では、内側の ``` で閉じたと見なし、中身の "inner" を読む（実測）。
- 次のものは意図どおりだった（実測）: 行の途中の ``` は無視して後のブロックだけ省く、
  ``` の中の ~~~ と ~~~ の中の ```（`\1` で種類を合わせている）、ブロック 2 つ、
  リストの中の字下げしたブロック、`x ``` y` のように行の途中にある閉じは閉じと見なさない。
- 実害: 返答の先頭にこの形が来る頻度は低いと思う（未確認）。

### 2. hooks/speak-response.py:42-52 — 読んだら消しても、古い PID への killpg は 1 回残る
- 範囲: PID ファイルは次の Stop が読むまで残るので、「再生が終わってから次の Stop まで」の間に
  その番号が別のプロセスグループの ID になっていれば、そのグループに SIGTERM が 1 回届く。
  今回の変更で防げたのは、text が空の Stop が続いたときに同じ PID へ 2 回目以降を送ることだけ。
  前回の指摘 4 の主な部分（再生終了から次の Stop まで）はそのまま残っている。
  `pid_max` は 4194304 なので見込みは小さい（実害は未確認）。
- 2 つのセッションの Stop がほぼ同時に来たとき: 両方が同じ PID を読み、先に unlink したほうだけが
  killpg し、もう片方は unlink の OSError で return する。止める動作としては 1 回で足りる。
  そのあと両方が鳴らして上書きするので、2 つ重なって鳴る点は前回と同じ（実害は未確認）。

### 3. hooks/speak-response.py:22, 73 — XDG_RUNTIME_DIR が無いときの /tmp/claude-UID は Claude Code 自身の一時ディレクトリと同じ名前
- `/tmp/claude-649` は既にあり、Claude Code がサブエージェントの scratchpad などに使っている
  （`drwx------ ytani`、実測）。そこへ PID ファイルが混ざる。Claude Code が中身を片付けるかは未確認。
- `mkdir(mode=0o700, exist_ok=True)` は既存のディレクトリの持ち主と権限を確かめないので、
  他の利用者が先に作ったディレクトリでも書き込む（mode は新しく作るときだけ効く）。
  同じ名前の通常ファイルがあれば FileExistsError で hook が終了コード 1 になる（Popen の後なので
  再生は始まる。Claude Code の動作は妨げない）。
- 実害: Claude Code は systemd のログインセッションから起動され、`XDG_RUNTIME_DIR=/run/user/649`
  がある（実測）。この経路に入るのは ssh などで XDG_RUNTIME_DIR が無いときだけ。低い。

## 好みの範囲

### 4. エンジンの版ディレクトリをエンジンのユーザーデータの場所に置いている
- `~/.local/share/voicevox-engine/` には、エンジンが書く `presets.yaml`・`installed_libraries`・
  `core_libraries` と、展開した `0.25.2/` が並んでいる（実測）。名前はぶつからず、今のところ害は無い。
  ただ、エンジンのデータを消して作り直すとき（あるいは AUR 版も同じ場所を使うので、その片付けのとき）に
  2.2 GB の本体ごと消しかねない。`~/.local/opt/voicevox-engine/0.25.2` のように、プログラムと
  データを分けておけばこの心配は無い（境界線上の判断。報告だけ）。

### 5. systemd/voicevox-engine.service — 版番号が unit に 2 か所
- `WorkingDirectory` と `ExecStart` の両方に `0.25.2` がある。README の「版を上げるとき」の
  手順で足りる。unit の `%h` は user unit の指定子として正しく、実体
  `~/.local/share/voicevox-engine/0.25.2/run` は ELF で実行権あり、
  `systemctl --user` で active、`/version` は "0.25.2" を返した（実測）。

## 報告だけ（判断は管理者）

- `last_assistant_message` が無い・null・空のとき: `or ""` で空文字になり、`stop_playing()` だけが
  走って前の再生が止まり、何も鳴らない。文字列でない値（数値など）だと `re.sub` の TypeError で
  終了コード 1。どちらも Claude Code の動作は妨げない。空のときに前の再生を止めてよいかは報告だけ。
- AUR の `voicevox-engine 0.24.1-1` と、そのために入れた `uvicorn` はまだ入っている（`pacman -Q`）。
  差分の範囲外だが、README からは消えたので、残すか外すかは利用者次第。

## 問題なしの観点

- `_` を空白にしたこと: `__init__.py` → "init .py"、`_private` → "private"、`snake_case` → "snake case"、
  `__強調__` → "強調"（実測）。語の切れ目が残り、意図どおり。
- `--test` は通る（"ok"）。追加した 3 件（`_`、閉じていないブロック、`~~~`）は出力を完全一致で
  比べているので、正規表現を壊せば落ちる。
- .gitignore: vv-shim の 3 行は消えていて、`hooks/vv-shim/` もディスクに無い。README・TODO.md・unit に
  shim・PYTHONPATH の残りは無い（TODO.md 40 行目の「要らない」という説明だけ）。
- README の手順: `7z` は 7zip パッケージ、`gh` もある。unit のパスと展開先が一致している。
  手順の再現は verifier に任せる。
- 範囲: TODO-008 に関係ない変更は無い。

## 作り込みすぎ

Lean already. Ship.（last_text とシムが消え、前回の指摘分は解消した）
