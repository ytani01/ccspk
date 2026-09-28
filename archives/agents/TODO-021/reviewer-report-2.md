# TODO-021 reviewer 報告（2 回目）

対象: 前回の指摘 1〜3 を直した分（`systemd/voicevox-engine.service` の `ExecStartPost` とコメント、
`docs/UsersGuide.md` の待ち時間、`src/ccspk/user_dict.py` の `save()`）。4 は直さないと決まったので見ていない。
実測は 2026-09-29、このマシン（systemd 262、user unit の既定 `TimeoutStartSec` 15 秒）で行った。

## 要修正

（なし）

## 検討

### 1. `systemd/voicevox-engine.service:11-13` 15 秒に収まるのは「待ち 10 秒 + `dict import` が 5 秒未満」のとき。`dict import` 側に上限が無い

- 待つ部分は `timeout 10` で必ず 10 秒で切れる（下の実測）。ただしその後の `exec ccspk dict import` は
  `timeout` の外にあり、中の `call` の上限は HTTP 1 回あたり 60 秒（POST `/import_user_dict` と、
  `save()` の GET `/user_dict` の 2 回）。
- エンジンが 10 秒近くたってから応答し、その直後の import が 5 秒以上かかると 15 秒を超え、前回の実測どおり
  `-` があってもエンジンごと止められる。
- 普段はエンジンが約 1.2 秒で応答する（journal）ので余裕は大きい。`ccspk` の起動は `dict list` で 0.08 秒。
  エンジンの `/import_user_dict` にかかる時間は測っていない（本物の辞書を書き換えるため）。
  **実害は未確認**。コメントの「応答は最長 10 秒待つ」は正しいが、「上限を超えないため」という
  説明は import の時間を含めていない。

## 好みの範囲

（なし）

## 作り込みすぎ

作り込みすぎ: なし（`save()` は前回挙げた書き方そのままで、`tempfile` の import も消えた）。

## 問題なし（1 行ずつ）

- `$$` と引用符: unit の文字列を `systemd-run --user -p "ExecStartPost=…"` にそのまま渡すと
  `argv[]=/bin/sh -c f="$${XDG_CONFIG_HOME:-$$HOME/.config}…` と解釈され、実行時に `"$$f"` が
  `/home/ytani/.config/ccspk/user_dict.json` に展開された（成功の経路で `IMPORT … /home/ytani/.config/ccspk/user_dict.json` が出た）
- 外側の `'…'` の中の `"until …; done"` は、systemd でも外側の sh でもそのまま内側の sh に渡る（中に `$` が無いので展開の問題も無い）
- 行末の `\`: `systemd-analyze --user verify` は警告なし。取り出したスクリプトは `sh -n` を通る
- `%h`: transient unit（`systemd-run -p`）では展開されなかったが、unit ファイルでは展開される。同じファイルの `ExecStart` が既に `%h` で動いている
- 失敗の経路: ポートを 50999（閉じている）、`timeout 3` にして transient unit で実行 → 3.0 秒で「応答しないので…」を出し、本体は `active (running)` のまま（`-` が効いた）。`curl` の残りも無い
- 成功の経路: 2 秒後に `/version` を返すサーバ（`python3 -m http.server`）を相手に、3.0 秒で `exec` へ進んだ
- 待ちの上限は `timeout 10` で決まり、`curl` が返らないとき（`--max-time 1`）も、断られるときも 10 秒で切れる
- `docs/UsersGuide.md:204` 「エンジンが 10 秒で応答しないときは読み込まずにあきらめる（エンジンは止めない）」は上の実測と合う。「60 秒」「90 秒」の残りは無い（`docs/Developer.md` の 60 秒は別の話）
- `save()` の権限: 書き出したファイルは `0o644`（umask どおり。前回は `0o600`）
- `save()` の残骸: `call` が落ちる形で 2 回失敗させても、残るのは `user_dict.tmp` の 1 つだけで、`user_dict.json` は前の中身のまま
- `.venv/bin/ccspk test` は `ok`
