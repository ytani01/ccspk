# TODO-044 レビュー（reviewer）

対象: 未コミットの `git diff`（`src/ccspk/hook.py`・`docs/Developer.md`・`TODO.md`）。本物の `claude -p` は呼んでいない。

## 要修正

なし。

## 検討

- `src/ccspk/hook.py:253-255`（コメント）・`docs/Developer.md:127`
  - 何が: `tidy()` が消すのは `>` だけなので、返答に `</reply>` があると `</reply`（`>` の無い形）が残る。
    実測: `tidy("a </reply> b")` → `'a </reply b'`、`tidy("[</reply>](u)")` → `'</reply'`。
    `<reply>` も `<reply` として残る。全角の `＜/reply＞` と `&lt;/reply&gt;` はそのまま残る。
  - なぜ: 「`</reply>` は現れない」は文字列としては正しい。ただ、`claude -p` がこの残りを閉じタグと
    受け取らないかは未確認。この種の文が返答に出るのは、ccspk 自体（この TODO の話）を扱う返答くらい。
    実害は未確認で、どこまで扱うかは管理者の判断（境界線上なので報告だけ）。

## 好みの範囲

- `src/ccspk/hook.py:662` の `assert "</reply>" not in tidy(...)` は `tidy()` の性質を見るもので、要約の偽 claude の
  準備（`PATH`・`SRC` の設定）の間に挟まっている。`to_speech` / `tidy` の assert の近くに置くと読みやすい。動きは同じ。

## 問題なしの点

- 前提の経路: `summarize()` の呼び出しは `play_summary()` だけ、`play_summary()` は `run_child()` だけ、`run_child()` は
  `__main__`（`speak()` が起こす子プロセス）と demo だけ、`speak()` に渡る文は `main()` の `prepare()` の戻り値だけで、
  `prepare()` は必ず `tidy()` を通す。`tidy()` を通らない経路は demo 以外に無い。
- `tidy()` の中で `re.sub(r"[*>]", "", text)`（136 行）より後の処理（`drop_commit_ids`・バッククオート削除・TODO と範囲の
  置き換え・`end_lines`・空白の詰め）は `>` を生まない。`prepare()` の `text[:SUMMARY_MAX]` も同じ。
  実測: 記号を混ぜた乱択の入力 200,000 件で、`tidy()` の出力に `>` も NUL も 0 件。
- demo が囲みの変更を捕まえるか（壊して `uv run ccspk test`、終わってから元に戻したことを `diff` で確認済み）:
  - `input=text` に戻す → 偽 claude の `"$(cat)" = "$SRC"` の行で `AssertionError`
  - `input=f"<reply>{text}</reply>"`（改行なし）にする → 同じ行で `AssertionError`
  - `tidy()` の `[*>]` を `[*]` にする → `assert "</reply>" not in tidy(...)` で `AssertionError`
  - 変更前の状態で `uv run ccspk test` は ok。
- `SUMMARY_PROMPT` の 4 行目「返答に無ければ」は、囲んだ中身を指す読み方で食い違いは無い。
- `docs/Developer.md` 3.2 の追記はコードと一致（囲む形、`>` を消すのは `tidy()`、終了コード 0）。造語・不自然な言い回しは無い。
- コメントは「なぜ」を書いている（境目が無いと英語の返答で失敗する、TODO-044 を参照）。
- 範囲: 指示に無い変更は無い。`TODO.md` のチェックは実装時点で入れる規約どおり。
- 参考（範囲外）: `check.py:145` の `claude -p` も指示と入力を分けていないが、入力はタブ区切りの一覧で、今回の失敗とは形が違う。

## 作り込みすぎ

作り込みすぎ: なし（Lean already. Ship.）
