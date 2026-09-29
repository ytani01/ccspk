# TODO-039 reviewer の報告

対象: 未コミットの `git diff` 全体（2026-09-29 時点）。コードは直していない。
実測は `XDG_CONFIG_HOME`・`XDG_STATE_HOME`・`XDG_RUNTIME_DIR` を一時ディレクトリに向け、`.venv/bin/ccspk` で行った。

## 要修正

なし。

## 検討

### 1. `src/ccspk/user_dict.py:374`（`volume_` の引数）負の値が「範囲の外」ではなく「無いオプション」として断られる

- 何が: `ccspk volume -0.1` は `Error: No such option '-0'.`、`ccspk volume -inf` は `No such option '-i'.` になる（実測、終了コード 2）。
  範囲の判定まで届かず、click が `-` で始まる語をオプションとして読んでいる
- なぜ: 断ること・終了コード 2 は UsersGuide 3.10 の記述（「範囲の外や数でない値は断る」「`2` — 引数の誤り（範囲の外、または数でない）」）と合っているが、
  メッセージが範囲の誤りだと分からない。`ccspk volume -- -0.1` なら `-0.1 is not in the range 0<=x<=1.` と出る（実測）。
  実害は未確認（利用者が負の値を打つかどうか次第）

### 2. `src/ccspk/user_dict.py:377-378` nan を断る分岐を確かめるテストが無い

- 何が: `volume_` の `math.isnan` の分岐を消しても、`ccspk test` は落ちない（`demo()` が見ているのは `volume()`・`pw_play()` だけ）。
  消すと `ccspk volume nan` はファイルに `nan` を書き、`volume()` の読み取りで 1.0 に戻るので、`1.0` を表示して終了コード 0 になる
  （`FloatRange(0, 1).convert("nan")` が `nan` を返すことは実測で確かめた）
- なぜ: TODO-039 の要件「数でない値は断る」を支えているのはこの分岐だけ。`demo()` は関数の assert だけの作りなので、
  CLI まで足すかは判断が要る。今の分岐そのものは正しく動く（`nan`・`NaN` とも終了コード 2、ファイルは書き換わらない。実測）

### 3. `-0` が通り、`-0.0` と表示・保存される（好みの範囲に近い）

- 何が: `ccspk volume -- -0` は `-0.0` を表示し、ファイルにも `-0.0` を書く。ファイルに `-0` と書いてあっても `volume()` は `-0.0`、
  `pw_play()` は `--volume=-0.0` を返す（実測）。`0 <= -0.0` が真のため
- なぜ: 鳴らす上では 0 と同じはずだが、`pw-play` が `-0.0` をどう読むかは未確認（実機の再生は verifier の範囲）。
  同じく `ccspk volume 0.00001` は `1e-05` と保存され、`--volume=1e-05` で渡る。`pw-play` が指数表記を読めるかも未確認

## 好みの範囲

- `src/ccspk/user_dict.py:378` nan のときだけメッセージの形が `Invalid value for VALUE:` になり、
  ほかの誤り（`Invalid value for '[VALUE]':`）と揃わない（実測）。`param_hint` の違いによる

## 問題なしの点

- `volume()` の既定値: 無い・空・`inf`・`-inf`・`nan`・`1.5`・`-0.1`・`x`・不正な UTF-8・ディレクトリ・読めない権限は 1.0、`  0.5  ` は 0.5、`0`・`1` はそのまま（実測）
- `volume_` の引数: `inf`・`1.5`・`x`・2 つ渡しは終了コード 2 で、ファイルは書き換わらない。`0`・`1`・`0.6` は書いて表示（実測）
- `write_config()` への共通化: `speaker_` の書き込みは、書く文字列（`f"{sid}\n"`）・一時ファイル名（`speaker.tmp`）・`mkdir`・`replace` とも前と同じ
- `hook.py` の `play()`: `pw_play()` を初めに 1 回だけ呼び、ループでは使い回す。`play()` を通る経路（子プロセス 502 行、`say` 961 行、`play_rewritten`）はすべてこれを通る。`pw-play` を直接呼ぶ箇所は他に無い
- `dict add --speak`: `pw_play()` を使うように変わっている（`user_dict.py:273`）
- UsersGuide の見出しとアンカー: 文書内のリンク 59 件がすべて見出しに解決する（見出しから slug を作って突き合わせた）。旧番号を本文で参照している箇所も無い
- 文書とコードの食い違い: UsersGuide 1.10・3.10、Developer 1・3.7・4.1、README、CLAUDE.md、`user_dict.py` の docstring、`--help` の出力が一致
- 規約: 行長は既存と同程度。`demo()` に例を足している。`ccspk test` は `ok` ×3（実測）。範囲外の変更は無い
- 設計: 定数・関数の置き場所（`user_dict.py` の `SPEAKER_FILE`・`speaker()` の隣）、`volume_` の名前と `add_command(name=...)` は `speaker_` に揃っている

## 作り込みすぎ

作り込みすぎ: なし（`pw_play()`・`write_config()` とも呼び出し元が 2 つ以上あり、`math.isnan` の分岐は要件のために要る）
