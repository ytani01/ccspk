# TODO-056. カッコの中の、` で囲まないコミット ID も読まない

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 既定 | main（実装）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 既定 | 46 | 10,086 | 22,024 | 2,009,578 | 72% |
| reviewer | Opus 5.5 | high | 36 | 2,109 | 54,000 | 576,849 | 22% |
| verifier | Sonnet 5.5 | medium | 14 | 561 | 25,672 | 131,948 | 6% |
| 合計 |  |  | 96 | 12,756 | 101,696 | 2,718,375 | 計 2,832,923 |

- reviewer・verifier は定義（`~/.claude/agents/`）のまま。reviewer は opus / high、verifier は sonnet / medium
- main の effort は指定していない

## きっかけ

`AskUserQuestion` の質問に「コミット済み（fd93278）で」と ` で囲まずに書き、ID がそのまま読まれた。
`drop_commit_ids()` は ` で囲んだものだけを ID と見ていた。利用者と決めて、カッコの中だけ囲まないものも見ることにした。
カッコの外は英単語（`deadbee`）や 7 桁の数字と見分けられないので今のまま読む。

## やったこと

- `src/ccspk/hook.py`: `drop_commit_ids()` に `pid` を足し、カッコの 2 つの置き換え（カッコごと消す・`（…、` の ID だけ消す）で、
  ` で囲んだ ID か、囲まない小文字 16 進 7 桁（`..` の範囲も）を ID と見る。reviewer の指摘で、半角 `(` の直前が
  英数字か `_`・`.` のもの（`f(abc1234)`・`range(1000000)`）は見ないようにした
- `demo()`: 消える例（`（fd93278）`・`(fd93278)`・`（fd93278、…`・`（fd93278..2cdfe32）`）と、残る例（カッコの外・8 桁・関数の呼び出し）を足した。
  囲まない `（6e985ac）` を残すとしていた例は、今回の決定で大文字の `（6E985AC）` に置き換えた（残していた理由は archives に無かった）
- `docs/UsersGuide.md`・`docs/Developer.md`: コミット ID の説明を今の条件に合わせた

## 確かめたこと

- verifier: `ccspk test` が通る。`pid` を `cid` に戻す・後読みを消す・囲まない範囲を消す、のどれでも `demo()` が落ちる（655・659・658 行）。
  `docs/UsersGuide.md` の条件と、`（fd93278）`・`f(abc1234)`・`v1.3.0(fd93278)` の結果が合う（報告は `archives/agents/TODO-056/verifier-report.md`）
- reviewer: ` で囲んだ ID の挙動は変わっていない（報告は `archives/agents/TODO-056/reviewer-report.md`）

## 残ること

関数の呼び出しの見分けは、半角 `(` の直前の 1 字だけで決めている。次の形はまれなので受け入れた。

- 消えてしまう: `f (abc1234)`・`f( abc1234)`・`g()(abc1234)`・`a[0](abc1234)`・全角の `x（abc1234）`
- 残ってしまう: `master(fd93278)`・`v1.3.0(fd93278)` のように、半角 `(` の直前が英数字の ID

## 分担の振り返り

- reviewer は 1 回目で、インラインコードの関数の呼び出し（`range(1000000)` → `range`）まで消えること、囲まない範囲を壊しても
  `demo()` が落ちないこと、前後の境界が効いていないことを見つけた。2 回目で、新しい条件をすり抜ける形と、文書の書き方が条件と合わないことを見つけた。
  どれも main の実装では気づいていなかった
- verifier は、壊すと落ちることを 3 か所で確かめた。食い違いは見つけなかった
- 見込みとの違いは reviewer が 2 回になったこと。1 回目の指摘で条件を足したため
- 次に正規表現で範囲を広げる項目では、実装の前に、コードの中（インラインコードや関数の呼び出し）に同じ形が出ないかを main が
  実例で流してから reviewer に回す。それで reviewer の 2 回目を省ける見込みがある
