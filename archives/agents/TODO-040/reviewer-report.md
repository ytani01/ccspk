# TODO-040 reviewer 報告

対象: `git diff src/ccspk/hook.py`（`tidy()` の先頭で NUL を消す 2 行と、`demo()` の例 1 行）

## 要修正

なし

## 検討

なし

## 好みの範囲

なし

## 観点ごとの結果

- **消す位置: 問題なし。** `rg -n "tidy\(|to_speech\(|prepare\(|speak\(|play\(|record\(" src` で呼び出し元を洗った。
  - フックの 3 つのイベントは、どれも `main()` で `prepare(raw)`（hook.py:723）→ `tidy()` を通ってから `LAST`・`speak()`・`check.record()` に渡る。`raw` をそのまま使う所は無い（`assemble()` の hook.py:309 は NUL を含む `delta` をファイルに書くが、ファイルへの書き込みは NUL で落ちない）
  - 要約: `prepare()` の `text[:SUMMARY_MAX]`（hook.py:239）は `tidy()` の後の文。`summarize()` は `claude -p` の出力を `to_speech()`（hook.py:263）に通し、失敗時の `clip(text)` も親で `tidy()` 済みの文。`play_summary()` の `check.record()`・`play()` に届くのはこのどちらか
  - `ccspk say`（hook.py:748-751）は argv から来るので、OS の段階で NUL を含められない。`tidy()` を通さないのは今までどおり
  - `check.record()` の呼び出し元は hook.py:275・739 と、check.py:242・244（`demo()` の中）だけ
  - NUL を足すのは `mark_wrapped()` の `WRAP`（hook.py:76）だけで、`end_lines()` が `s[1:]` か `lstrip(WRAP)` で必ず外す。消した後で NUL が混じる道は無い
- **WRAP と整形の意味: 問題なし。** 空文字に置き換えるので、NUL が無かった場合と同じ結果になる（実測、下の表）。空白に置き換えると、行頭の NUL が字下げに化けて前の行につながる（`"a\0b\n\0c"` → `'a b c'`）ので、空文字が正しい。`^\s*` などの正規表現は NUL を空白と見ないので、消す前後で他の置き換えの当たり方が変わるのは「NUL が行頭の記号の前にあった」場合だけで、そのときは NUL が無い文と同じに整う
- **demo() の例の強さ: 十分。** 直す前のコード（`git show HEAD:src/ccspk/hook.py` を別名で読み込んで実測）では `'a\x00b c'` が返り、`"ab。 c"` と食い違って落ちる。NUL が残ることと、行頭の NUL を WRAP と見てつなぐことの両方を捕まえる。空白に置き換える直し方でも `'a b c'` で落ちる
- **コメント: 問題なし。** 「argv に渡せず、WRAP とも見分けられない」と理由を書いている
- **範囲: 問題なし。** hook.py の差分は上の 3 行だけ
- **規約: 問題なし。** `demo()` に例を足している（CLAUDE.md「整形や分割を変えたら demo() に例を足す」）
- 作り込みすぎ: なし（Lean already. Ship.）

## 実測

`.venv/bin/python` で、HEAD の hook.py（old）と作業ツリーの hook.py（new）の `to_speech()` を比べた。

| 入力 | old | new |
|------|-----|-----|
| `"a\0b\n\0c"` | `'a\x00b c'` | `'ab。 c'` |
| `"a\0b"` | `'a\x00b'` | `'ab'` |
| `"前\n\0  字下げ"` | `'前 字下げ'` | `'前 字下げ'` |
| `"\0- 項目\n次"` | `'- 項目。 次'` | `'項目。 次'` |
| `"\0# 見出し"` | `'# 見出し'` | `'見出し'` |

`speak()` の `Popen` が NUL で `ValueError` になること自体は実行していない（未確認。verifier の担当）。
