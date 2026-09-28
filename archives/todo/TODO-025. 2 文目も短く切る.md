# TODO-025. 2 文目も短く切る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 5,347 | 17,735 | 61% |
| reviewer | Opus 5.5 | high | 443 | 36,446 | 30% |
| verifier | Sonnet 5.5 | medium | 401 | 23,730 | 9% |
| 合計 |  |  | 6,191 | 77,911 | 概算 $0.9 |

- サブエージェントの分は少なめに出ている（`subagents/` のログの取りこぼし）

## きっかけ

TODO-003 で 1 文目だけを前後 2 つに切るようにした。利用者から、2 文目も短く切るよう
依頼があった（2026-09-29）。1 文目の後半を鳴らしている間に長い 2 文目の合成が終わらず、
継ぎ目で待つのを減らすため。

## やったこと

- `src/ccspk/hook.py` の `chunks()` で、1・2 文目に `split_first()` をかけ、3 文目以降は文ごとにした。
  `split_first()` の docstring、`CUT` のコメントも「1 文目」から直した
- `demo()` の「1 文目だけ切る」テストを「2 文目まで切り、3 文目は切らない」にし、
  1 文だけの返答が切れるテストを足した（reviewer の指摘）
- `docs/Developer.md` の「動き方」と、関数・定数の表を直した

`split_first` の名前は残した（「最初の区切りで切る」とも読めるため）。

## 確かめたこと

- `uv run ccspk test` が通る
- 変更前の式・全部の文を切る式・1 文のとき切らない式に書き換えると、テストが落ちる（reviewer）
- 3 文の例は 5 個、1 文は 2 個、2 文目が 8 字より短い例は 3 個に分かれた。エンジンを使った
  `ccspk say` は 3 文で終了コード 0・10.55 秒（verifier）

## 分担の振り返り

- reviewer: 1 文だけで切る例がテストに無く、式を書き換えても通る穴（変更前からある）と、
  docstring の言い回しを見つけた。どちらも直した
- verifier: 食い違いは見つけなかった。エンジンを使った通しで、合成と再生が最後まで動くことを押さえた
- 見込みどおりで食い違いは無い
- 次に同じ規模（数行の式と 1 つのテスト）の項目をやるなら、同じ組み方でよいが、verifier の
  `chunks()` の出力確認は reviewer の変異テストと重なるので、verifier にはエンジンを使った通しだけを頼む
- 分担は [archives/agents/TODO-025/](../agents/TODO-025/README.md)
