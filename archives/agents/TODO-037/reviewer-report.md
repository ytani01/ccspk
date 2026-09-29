# TODO-037 レビューの報告（reviewer）

対象: 未コミットの `git diff`（`src/ccspk/hook.py`・`cli.py`・`docs/`・`README.md`・`CLAUDE.md`）。
書き換えて確かめるときは `src/` を scratchpad にコピーし、`PYTHONPATH` でそちらを読ませた（作業ツリーは触っていない）。
`XDG_RUNTIME_DIR`・`XDG_STATE_HOME`・`XDG_CONFIG_HOME` はすべて一時ディレクトリに向けた。

**知らせること: 確かめている途中で、本物の `claude -p`（Sonnet）を 1 回呼んでしまった。** 下の 1 の書き換え
（`timeout=` を外す）で demo を走らせたとき、「`claude` が無い」の例が本物に届き、最後まで走った（約 8 秒）。
入力は demo の `a * 300`、`cwd` は demo の一時ディレクトリ、`--setting-sources ""`・`CCSPK_SPEAK=0` 付き。
料金は 1 回分（1〜1.5 セントほど）と見込むが、額は確かめていない。

## 要修正

### 1. `ccspk test` が本物の `claude` を起こす

- どこ: `src/ccspk/hook.py:576`・`:593-594`（demo の「`claude` が無い」の例）
- 何が問題か: `PATH` を `f"{tmp}:{saved[4]}"`（一時ディレクトリ＋元の `PATH`）にしているので、偽の `claude` を
  消した後の `summarize(src)` は、元の `PATH` にある本物（`~/.local/bin/claude`）を起こす。コメントの
  「PATH に tmp だけ」と食い違う。`SUMMARY_TIMEOUT = 0.5` で殺されるので assert は通る
- 確かめた方法: `PATH` を「記録だけする偽の `claude`（空を返す）:/usr/bin:/bin」にして元のままの demo を走らせると、
  その偽物が `-p --model sonnet … <プロンプト>` で呼ばれた記録が残り、demo は `ok` で通った
- 起きる条件: `claude` が `PATH` にある環境で `ccspk test` を走らせるたび（`src/` を変えた返答の終わりに Stop フックが
  走らせる分も含む）。0.5 秒のうちに API へ要求が出て料金がかかるかは**未確認**。時間切れで殺された `claude` の
  孫プロセスが残るかも**未確認**
- あわせて: この例は `except OSError` の道を確かめていない（上のとおり、`claude` が見つかって空を返しても通る）。
  `summarize()` の `except` から `OSError` を外しても、`claude` が `PATH` にある限り demo は落ちない（頭の中での
  判断。上の記録で `claude` が見つかる道を通ることは実測）

### 2. 要約が入っていて返答がとても長いと、フックが落ちて何も読まない

- どこ: `src/ccspk/hook.py:372`（`speak()` が本文を argv で渡す）、`:646`・`:660`（`main()`）
- 何が問題か: 要約させるときは `clip()` 前の文をそのまま argv 1 つで渡す。Linux の argv 1 つの上限
  （131,072 バイト）を超えると `Popen` が `OSError: [Errno 7] Argument list too long` を出し、`main()` は捕まえない
- 確かめた方法: `/bin/true` に `あ` を 43,000 字（129,000 バイト）は通り、44,000 字で `OSError`。
  フックを MessageDisplay・`CCSPK_SUMMARY=1`・偽の `pw-play`/`claude`・一時の XDG で、`あいう。` × 11,000 の
  delta を渡すと、トレースバックで終了コード 1、子プロセスは起きず、`ccspk.last` が 132,000 バイトで残った
- 起きる条件: 要約が入っていて、整えた文が 131,071 バイトを超えるとき（日本語でおよそ 43,000 字、英字で 131,000 字）。
  変更前は `clip()` 後の 240 字以内を渡していたので起きなかった。決めた動き（失敗したら切った文を読む）と違う。
  Claude Code が終了コード 1 のフックをどう表示するかは**未確認**

## 検討

### 3. demo は、フックと子プロセスのつなぎ目を壊しても落ちない

- どこ: `src/ccspk/hook.py` の demo（545-606 行）
- 何が問題か: 下の書き換えを 1 つずつ入れて demo を走らせた結果。上の 2 つは依頼の例
  - 落ちた: `prepare()` の `>` を `>=`／`summary_on()` をファイル優先に（`(True, '0')` で落ちる）／環境変数を見ない／
    `prepare()` が整える前の文を渡す／`timeout=` を外す（1 の本物の `claude` の結果で落ちたもので、偽の
    `sleep 5` の例では落ちない。空を返して `clip()` と同じになるため）／終了コードを見ない／要約に `to_speech()` を
    通さない／`CCSPK_SPEAK=0` を付けない
  - 落ちなかった: `claude -p` に `start_new_session=True` を付ける／`main()` が要約させるときも `record()` を呼ぶ／
    `speak()` が `--summarize` を付けない／`__main__` がいつも `play(sys.argv[2])` にする／`play_summary()` が
    `record()` を呼ばない／`main()` が `prepare()` の代わりに `to_speech()` を使う（要約が効かなくなる）
- 起きる条件: 上の「落ちなかった」のどれか。特に `speak()` が `--summarize` を付けなくなると、子プロセスは
  切っていない文を丸ごと `play()` する（`LIMIT`・`EXTEND` のコメントにある、エンジンのメモリが膨らんだ場合と同じ形）。
  `start_new_session` を付けると `ccspk stop` で `claude -p` が残る。どこまで demo で見るかは管理者の判断

### 4. `LAST` の比べ方が、切る前の全文になった

- どこ: `src/ccspk/hook.py:646-660`
- 何が問題か: 要約させるときは `tidy()` の全文を `LAST` と比べる。変更前は切った後の 240 字以内で比べていたので、
  MessageDisplay の分をつないだ文と Stop の `last_assistant_message` が 180 字より後ろで違っていても同じと見ていた。
  全文で同じになるかは**未確認**（TODO-010 の verifier は同じ入力を両方に渡して確かめている。本物の 2 つのイベントの
  全文を比べたものは見つからなかった）
- 起きる条件: 要約が入っていて、2 つのイベントの整えた文が後ろのほうで違うとき。Stop が 0.01 秒後に子プロセスを
  止めて起こし直すので、`claude -p` が 2 度起きかける。実害は**未確認**

### 5. `ccspk summary` の注記は、ターミナルの環境変数しか見ない

- どこ: `src/ccspk/hook.py:714-715`、`docs/UsersGuide.md:380`・例（`CCSPK_SUMMARY=0 ccspk summary`）
- 何が問題か: `summary_env()` はコマンドを打ったシェルの環境変数を見る。フックの環境変数が `settings.json` の `env`
  から来ているときは見えないので、`ccspk summary on` が `on` と表示してもフックは切のまま、ということがある。
  また UsersGuide の「フックに届く環境変数は `settings.json` の `env` から来るので、一時的に切り替えるのに使う」は、
  TODO.md の背景にある「コマンドから直接は変えられない」が抜けて、理由と結論がつながっていない
- 起きる条件: `CCSPK_SUMMARY` を `settings.json` の `env` に書き、シェルには無いとき

### 6. `CLAUDE.md` の注意が、要約で本物の `claude -p` が走る場合を含まない

- どこ: `CLAUDE.md:24`（「Stop として動かすと裏で本物の `claude -p` が走り」）
- 何が問題か: 要約が入っていると、MessageDisplay・PreToolUse でも 180 字を超える文で本物が走る。
  `docs/Developer.md` の 4.2 には書いてあり、`CLAUDE.md` はそこを指しているので、足すかは判断
- 起きる条件: 利用者の `~/.config/ccspk/summary` があるときに、4.2 の手順で `XDG_CONFIG_HOME` を向けずに試すとき

### 7. demo の時間の上限 0.5 秒が、通るべき例にもかかる

- どこ: `src/ccspk/hook.py:591`（ループの中で毎回 0.5 にしている）
- 何が問題か: 偽の `claude` が `cat` と `test` を走らせて返す例も 0.5 秒で打ち切られる。重いときに落ちるかは**未確認**
  （手元では demo 全体が 1.1 秒で通った）

## 好みの範囲

- `docs/UsersGuide.md` 3.2 の失敗の並び（`claude` が無い・終了コード・出力が空・30 秒）に、「整えると空」
  （表だけの出力など）が無い。`docs/Developer.md` 3.2 には書いてある

## 作り込みすぎ

- `hook.py:231-245`: shrink: `LOCK` を取るコードが `main()`・`stop()`・`play_summary()` で 3 つ目になった。
  `contextlib.contextmanager` の関数 1 つにまとめられる（既存の 2 か所も触るので、この項目でやるかは判断）。好みの範囲
- `hook.py:596-604`: stdlib: `CCSPK_SUMMARY`・`PATH`・`STATEDIR`・`SRC` を手で戻している。`with unittest.mock.patch.dict(os.environ):`
  で囲めば戻す 8 行が消える。好みの範囲

net: -10 lines possible.

## 問題の無かった観点

- 分かれ目: 切のとき・超えないときの `prepare()` は `clip(tidy(raw))` で、変更前の `to_speech(raw)` と同じ。`LAST`・`record()` の扱いも同じ。`summary_on()` は超えたときだけ読む
- `LAST`: 同じ文が 2 つのイベントから来れば、要約させる場合もそのまま効く（全文が同じ前提。4 を参照）
- `stop_playing()`: `--summarize` を足しても cmdline に `--play` と `ccspk.hook` が残り、`claude -p` には `start_new_session` が無いので同じグループ（コードで確認。止まることは implementer が実測）
- 失敗・時間切れ: `OSError`・`TimeoutExpired`・終了コード 0 以外・空はどれも `clip(text)`（demo で確認。`OSError` は 1 のとおり demo では通っていない）
- `play_summary()` の `LOCK`: 持つのは `record()` の間だけ。`flock` で待っている間に `killpg` されても、死ねば放されるので詰まらない。記録が Stop より後になり点検が次の Stop に回ることは文書にある
- `__main__`: `len(sys.argv) == 4` で、要約しない本文が `--summarize` のときに取り違えない
- 依頼の 2 例（`>` → `>=`、優先順を逆）は demo で落ちた（3 を参照）
- 文書: 節の繰り下げとリンクは、4 ファイルの `](…#…)` を見出しから作ったアンカーと突き合わせて、切れたもの 0。定数・関数の表、3.1 の手順 7・8・10、3.2、3.8 はコードと一致
- 規約・範囲: 指示に無い変更は無い。重い import は増えていない（`user_dict` は `check` が既に読んでいる）。`check.py` の呼び出しと共通化していない
