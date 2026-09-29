# TODO-045 verifier 報告

計測: `zsh archives/agents/TODO-045/verify.sh [項目番号]`（補助 `monitor.py`。0.1 秒ごとに、一時ディレクトリの
`XDG_RUNTIME_DIR` を環境変数に持つ pw-play の pgid を記録）。本物の VOICEVOX（0.25.2）・PipeWire を使用。
毎回 `mktemp -d`、偽の `claude` を PATH 先頭に置いた。コードは変更していない。
時刻は monitor 開始からの秒。1 つの子プロセスは塊ごとに pw-play を起こし直すので、pid は変わるが pgid は子プロセスの PID のまま。

1. OK（2 回とも）。PIDFILE=A,B,C = 389310,389317,389322。鳴った pgid の順 389310（1.28〜7.81）→389317（8.44〜15.70）→389322（16.64〜23.38）。
   常に n<=1（同時 2 つ以上なし）。2 回目も 389566→389573→389578 で同じ形（1.27〜7.79 / 8.42〜15.67 / 16.62〜23.35）。hook 3 回の所要は 0.96 秒。
2. OK。stop 前は 3 つとも生存、`ccspk stop` が「止めた」を出し rc=0。1 秒後に子プロセス 0・pw-play 0・PIDFILE 無し。pw-play は 389874 のみ 1.37〜2.53 で消えた。
3. OK。空 Stop（rc=0）で 2 と同じ結果。子プロセス 0・pw-play 0・PIDFILE 無し（pgid 389986 が 1.27〜2.52）。
4. OK。queue off。A の PIDFILE=390090。B 後は 390105 の 1 行。pw-play は 390090（1.27〜1.69 で切れる）→390105（3.06〜10.31）。A と B は重ならない。
5. OK。CCSPK_SUMMARY=1・queue on、A（狐を含み要約 4 秒）・B（すぐ返る）。PIDFILE=390212,390219。鳴った順 390212（4.76〜6.10）→390219（6.63〜8.07）。
   A の最初の音は要約の 4 秒後（4.76）、B は A の後。B の要約が先にできても A→B。
6. OK。引数なし=`off`・ファイル無し、`on`=`on`・ファイル有り、`off`=`off`・ファイル無し。すべて rc=0。`ccspk queue foo` は rc=2（Invalid value for '[on|off]'）。
7. OK。`uv run ccspk test` は ok を 3 回、rc=0。

## 変更ファイル（git status）
CLAUDE.md, README.md, TODO.md, docs/Developer.md, docs/UsersGuide.md, pyproject.toml, src/ccspk/cli.py, src/ccspk/hook.py, uv.lock、
未追跡は archives/agents/TODO-045/。指示に無いファイルは見当たらない（内容の是非は見ていない）。

## 確かめなかったこと
- 項目 1 は文章 3 つで、実際の再生が 3〜7 秒（塊ごとに pw-play が分かれる）。文の読み方は見ていない。
- 項目 5 で偽の `claude` を使ったので、要約の中身は固定文。順番だけ見た。
- 判断が要る点は無い。期待と違う観測は無し。
