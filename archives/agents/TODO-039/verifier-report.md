# TODO-039 verifier 報告

条件: `XDG_CONFIG_HOME` は mktemp の一時ディレクトリ。フックは動かしていない。コードは直していない。

| # | 確認 | 結果 |
|---|------|------|
| 1 | `uv run ccspk test` | ok を 3 行、rc=0 |
| 2 | UsersGuide 3.10 の例 | 一致。引数なし `1.0`、`0.6` で `0.6`、ファイルの中身 `0.6` |
| 3 | 断る値 | 下記。すべて rc=2、ファイルは 0.6 のまま |
| 4 | ファイルに `2`・`x`・空 | どれも `1.0` を表示 |
| 5 | say と pw-play の引数 | 下記 |
| 6 | 指数表記 | `ccspk volume 0.00001` → 保存値 `1e-05`。`ccspk say` は rc=0、pw-play の引数は `--volume=1e-05 -`。エラーなし |
| 7 | 範囲判定を `True` に書き換え | `ccspk test` が落ちた（`AssertionError: 1.5`、`user_dict.py` line 238、rc=1）。元に戻し、`git diff` が書き換え前と同一（RESTORED）、`ccspk test` は ok 3 行 |

## 3 の出力
- `1.5`: `Error: Invalid value for '[VALUE]': 1.5 is not in the range 0<=x<=1.` rc=2
- `abc`: `Error: Invalid value for '[VALUE]': 'abc' is not a valid float range.` rc=2
- `nan`: `Error: Invalid value for VALUE: nan は音量にできない` rc=2
- `inf`: `... inf is not in the range 0<=x<=1.` rc=2
- `-0.1`（`--` なし）: `Error: No such option '-0'.` rc=2（オプションと解釈される。範囲の誤りではない。UsersGuide にこの書き方の説明があるかは見ていない）
- `-- -0.1`: `... -0.1 is not in the range 0<=x<=1.` rc=2

## 5 の記録
エンジン稼働（`/version` = 0.25.2）。
- 音量 1.0: `461259 pw-play --volume=1.0 -`
- 音量 0.2（1 回目）: `461298 pw-play --volume=1.0 -`。食い違い。
  ppid を取っていなかったので、自分の `say` の子か、実セッションの別プロセスか区別できない。
  そのとき `ps` に実セッションの `ccspk speaker 118` が見えていたので、実セッションの読み上げを拾った疑いがある（推定。実害は未確認）。
- 音量 0.2（再測、ppid 付きの `ps`）: `461480 461397 pw-play --volume=0.2 -`。461397 は自分の `ccspk say` で、期待どおり。
- 音量 0.00001: `461328 pw-play --volume=1e-05 -`（6 と同じ）

## 変更されたファイル
`git status`: CLAUDE.md, README.md, TODO.md, docs/Developer.md, docs/UsersGuide.md, src/ccspk/cli.py, src/ccspk/hook.py, src/ccspk/user_dict.py が変更、`archives/agents/TODO-039/` が未追跡。
指示の範囲かどうかは、指示の範囲を受け取っていないので判断していない。src は cli.py・hook.py・user_dict.py の 3 つ。`speaker_` の書き込みを `write_config` に切り出す差分も入っている。

## 確かめていないこと
- 音の大きさそのもの（耳で判断できない）
- フック経由の鳴らし方（指示により動かしていない）
- `ccspk dict add --speak` の実行
