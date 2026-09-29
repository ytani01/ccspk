# TODO-058. 要約・翻訳の claude -p の effort を下げると速くなるか測る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | 測定: verifier（Sonnet 5.5 / medium）。変えるなら main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 既定 | 測定: verifier（Sonnet 5.5 / medium）。実装: main + reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 既定（medium） | 54 | 11,253 | 65,172 | 1,908,861 | 75% |
| verifier | Sonnet 5.5 | medium | 28 | 676 | 61,565 | 340,582 | 15% |
| reviewer | Opus 5.5 | high | 16 | 2,284 | 37,066 | 212,134 | 10% |
| 合計 |  |  | 98 | 14,213 | 163,803 | 2,461,577 | 計 2,639,691 |

- verifier は測定と実装の確認の 2 回起こした。行は 2 回の合計。モデルは定義（`~/.claude/agents/verifier.md`）のまま
- reviewer も定義（`~/.claude/agents/reviewer.md`）のまま
- 集計の終点は決着のコミットの前（現在時刻まで）。サブエージェントの分は少なめに出る

## きっかけ

`/claude-api prompt-audit` で、`rewrite()` の `claude -p --model sonnet` が `--effort` を付けておらず、
Sonnet 5.5 の既定の `high` で動くと分かった。下げれば要約・翻訳を待つ時間が縮むかを測る。

## やったこと

- verifier が、`rewrite()` と同じ引数で `--effort` 無し・`medium`・`low` を、要約 3 件・翻訳 2 件で 1 回ずつ測った
  （[verifier-report.md](../agents/TODO-058/verifier-report.md)）。
  設定による一貫した速さの差は無く、1 回 4〜5 秒のうち 3.2 秒は起動にかかっていた。品質の差もはっきりしなかった
- 推奨は「変えない」だったが、利用者が `medium` にすると決めた（2026-09-30）
- `src/ccspk/hook.py`: `rewrite()` の `claude -p` に `--effort medium` を足した。`demo()` の偽の `claude` が見る引数の位置を
  `"$1 $3 $5"`（`-p sonnet medium`）と `"${11}"`（指示）に直した。`SUMMARY_TIMEOUT` のコメントの秒数を測定値にした
- `docs/Developer.md`（概要の 2 か所と 3.2 の手順 1）と `docs/UsersGuide.md`（要約・翻訳のコマンド、要約の遅れを 4〜8 秒に）を直した
- トークン量は測っていないので、文書の値は変えていない

## 確かめたこと

- reviewer: 引数の位置が偽の `claude` と合うことを `sh -c` で確かめた。直すべき点は無し。
  概要の書き方の不揃いの指摘を受けて `docs/Developer.md` の 2 か所にも足した（[reviewer-report.md](../agents/TODO-058/reviewer-report.md)）
- verifier: `ccspk test` が通る。`--effort medium` を消したときと `low` にしたとき、どちらも `demo()` の assert で落ちる。
  本物の `rewrite()` は約 4.1 秒で要約を返した。`--effort` の記述は 6 か所で漏れ無し
  （[verifier-check-report.md](../agents/TODO-058/verifier-check-report.md)）

## 残ること

- 「4〜8 秒」の上の端は 1 回だけの 7.6 秒から来ていて、外れ値かもしれない
- 文書の「最初の音が遅れる」は、「要約します。」が `claude -p` を待たずに鳴るので、正しくは本文の音の遅れ（前からの書き方。今回は直していない）

## 分担の振り返り

- 測定の verifier は、effort で縮むのは 1 秒未満で、起動が大半を占めることを見つけた。reviewer は文書の書き方の不揃いと、
  秒数の範囲が 1 回の測定に頼っていることを見つけた。確認の verifier は、テストが引数を見張っていることを壊して確かめた
- 見込みどおりの編成だった。「変えるなら」の側に進んだのは、推奨と違う決定を利用者がしたため
- 次に同じ「測ってから決める」項目をやるなら、測定の依頼に 1 回ずつでなく 3 回ずつを最初から入れる。
  1 回では外れ値の見分けがつかず、文書の値の根拠が弱くなった。回数を増やした分の `claude -p` の呼び出しは、
  担当の会話のトークンにはほぼ効かない
