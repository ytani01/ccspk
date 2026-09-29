# TODO-044. 要約させる返答を囲んで渡す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | 不明 | 6,293 | 52,284 | 65% |
| reviewer | Opus 5.5 | high | 527 | 43,461 | 29% |
| verifier | Sonnet 5.5 | medium | 391 | 24,358 | 6% |
| 合計 |  |  | 7,211 | 120,103 | 概算 $1.2 |

- main の effort は記録に残らず、着手時に確かめていない
- reviewer・verifier は定義（`~/.claude/agents/`）のまま。モデルも上書きしていない

## きっかけ

要約を有効にしたところ、英語の返答「Summary is now on, …」（214 字）の要約が「要約する元の返答文が、メッセージに
含まれていません。…」になり、そのまま読まれた。指示は引数、返答は標準入力で、境目が無いため。2 回試して 2 回とも失敗し、
`<reply>` で囲むと 3 回とも要約できた。終了コードは 0 なので失敗と見分けられず、見分ける仕組みは足さない。

## やったこと

- `summarize()`（`src/ccspk/hook.py`）で、標準入力に `<reply>\n本文\n</reply>` を渡す。
  `SUMMARY_PROMPT` の書き出しを「`<reply>` と `</reply>` の間の文は、…」にした
- 返答の中の `</reply>`: `summarize()` に届く文は `tidy()` を通っていて `>` が無いので、閉じタグは現れない。
  手当ては足さず、`demo()` に `tidy()` が `</reply>` を残さない assert を足した
- `demo()` の偽の `claude` が受け取る標準入力の比較を、囲んだ形にした
- `docs/Developer.md` の「3.2 子プロセス」に、囲む理由と `</reply>` が現れない理由を書いた

## 確かめたこと

- `uv run ccspk test` が通る
- reviewer: 呼び出し元を辿り、`tidy()` を通らない経路・`tidy()` の後で `>` を生む処理が無いことを確かめた。
  demo は、囲みを外す・改行を抜く・`tidy()` が `>` を消さないようにする、のどれでも落ちる
- verifier: 本物の `claude -p` で、上の英語の文・日本語の返答・`</reply>` を含む日本語の返答を各 3 回、計 9 回要約させ、
  9 回とも要約になった（聞き返し 0、`clip()` へ戻った 0）

## 分担の振り返り

- reviewer は前提（`>` が無い）を乱択の入力でも確かめ、demo が壊すと落ちることを示した。指摘は 0 件で、
  `</reply>` の `>` だけが消えて `</reply` が残る点を検討として挙げた。verifier はそれを含む文で 3 回とも要約できたことを確かめた
- 見込みどおりの編成で、食い違いは無い
- 次に同じ規模（1 関数と demo と文書 1 節）なら、reviewer は Sonnet でも足りた。料金の 3 割が reviewer で、
  見る範囲が狭く前提も 1 つだった。本物の `claude -p` を呼ぶ verifier はそのままでよい
