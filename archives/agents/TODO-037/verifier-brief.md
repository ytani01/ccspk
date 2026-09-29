# TODO-037 確認の依頼（main → verifier）

目的: 長い返答を要約して読むオプション（`ccspk summary`）が、フックとして動かしたときに決めたとおりに動くかを実測する。
決めたことは `TODO.md` の TODO-037、実装は `git diff`、説明は `archives/agents/TODO-037/implementer-report.md`・`-2.md`。

## 環境（全項目で守る）

- `XDG_RUNTIME_DIR`・`XDG_STATE_HOME`・`XDG_CONFIG_HOME` は一時ディレクトリに向ける（本物を使わない）
- `PATH` の先頭に一時ディレクトリを置き、偽の `pw-play`（標準入力を捨てて終わる）と偽の `claude` を置く。
  偽の `claude` は、呼ばれた引数を 1 行ずつファイルに追記し、`--model sonnet` なら決まった要約
  （例: `要約です。TODO-7 の件は済みました。`）を、ほかのモデル（点検の `opus`）なら何も出さずに終わる
- フックは `CCSPK_SPEAK=1 .venv/bin/ccspk hook < payload.json` で動かす（Stop は `hook_event_name: "Stop"` と
  `last_assistant_message`、MessageDisplay は `message_id`・`index: 0`・`delta`・`final: true`）
- VOICEVOX エンジンは本物を使ってよい（合成だけ。`pw-play` は偽物なので鳴らない）
- 長い返答は `archives/agents/TODO-037/samples.json` の 2 つ目（598 字）を使う。短い返答は「直しました。」

## 確かめること（各 1 回でよい）

1. `uv run ccspk test` の終了コード
2. 切（`ccspk summary` が `off`）で長い返答の Stop: 子プロセスの cmdline（`/proc/<PIDFILE の PID>/cmdline`）に
   `--summarize` が無い、偽の `claude` の `sonnet` の呼び出しが 0 回、`$XDG_STATE_HOME/ccspk/spoken.txt` の最後の行が
   240 字以内の切った文
3. `ccspk summary on` の後、長い返答の Stop: cmdline に `--summarize` がある、`sonnet` の呼び出しが 1 回、
   子プロセスが終わった後の `spoken.txt` の最後の行が偽の要約を整えた文（`TODOナナ` になっている）
4. 入で、同じ長い返答を MessageDisplay → すぐ Stop（間は 1 秒以内）: `sonnet` の呼び出しが合わせて 1 回
5. 入で、短い返答の Stop: `sonnet` の呼び出しが 0 回
6. ファイルは入のまま `CCSPK_SUMMARY=0` で長い返答の Stop: `sonnet` が 0 回。`CCSPK_SUMMARY=0 ccspk summary` の表示
7. 偽の `claude` を `sonnet` のとき 20 秒眠るものに替え、入で長い返答の Stop → 2 秒後に `ccspk stop`:
   「止めた」と出る、子プロセスのグループ（`ps -o pid,pgid,cmd -g <PGID>`）が空になる、`spoken.txt` に足されない
8. `ccspk summary`（引数なし・`on`・`off`・`bad`）の出力と終了コード。`docs/UsersGuide.md` の「ccspk summary」の節の
   例を書いてあるとおりに打ち、出力が一致するか
9. **本物の `claude` で 1 回だけ**: 偽の `claude` を外し（偽の `pw-play` は残す）、入で長い返答の Stop。
   子プロセスが終わるまでの秒数、`spoken.txt` の最後の行（要約になっているか、字数）。
   終わった後、`pgrep -af 'claude -p'` に要約の `claude` が残っていないこと。**本物を呼ぶのはこの 1 回だけ**
   （点検の `claude -p`（Opus）も走るので、`XDG_STATE_HOME` が一時ディレクトリであることを必ず確かめてから）

見なくてよいもの: TODO-036 の点検の中身、文書の書き方の良し悪し、レイアウト。
コードは直さないこと。境界線上の判断や原因の切り分けはせず、「実害は未確認」と添えて報告だけにする。
`pkill` は使わない（`pgrep` で PID を確かめてから `kill`）。

## 報告

`archives/agents/TODO-037/verifier-report.md` に、項目ごとに測った値（呼び出し回数、字数、秒数、出力）を書く。
一致したものは 1 行、食い違いだけ詳しく。使ったスクリプトは `archives/agents/TODO-037/verify.sh` に残す。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
