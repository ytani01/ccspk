# TODO-042. 疑問文の語尾を伸ばさずに読む

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 4,010 | 12,367 | 66% |
| reviewer | Opus 5.5 | high | 373 | 28,301 | 27% |
| verifier | Sonnet 5.5 | medium | 74 | 20,588 | 7% |
| 合計 |  |  | 4,457 | 61,256 | 概算 $0.8 |

- 担当のモデルと effort は定義（`~/.claude/agents/`）のまま。サブエージェントの分は少なめに出る

## きっかけ

質問を読むと「…しますか」の語尾が「かぁ」と伸びて聞こえる、と利用者が気づいた（2026-09-29）。
エンジンは「？」「?」で終わる文を合成するとき、語尾に上げ調子の「ァ」を 1 音足す
（`/synthesis` の `enable_interrogative_upspeak` の既定が有効）。`audio_query` の `moras` には現れない。
2 通りを聞き比べてもらい、語尾を上げないほうに決めた。

## やったこと

- `src/ccspk/hook.py` の `synthesize()` で、`/synthesis` に `enable_interrogative_upspeak=false` を渡す
- `docs/Developer.md` の「3.2 子プロセス」に、渡す理由を書いた
- 「？」を「。」に置き換える案は採らなかった。文の区切り（`ENDS`）と `LAST` の比較に関わり、影響が広い

## 確かめたこと

- `synthesize()` で「着手してよいですか？」「…?」「…。」がどれも 1.493 秒。引数なしの「？」は 1.643 秒（話者 119）
- `uv run ccspk test` が通る
- 聞こえ方は、直す前に同じ 2 通りを鳴らして利用者が聞き比べた

## 残ること

- `user_dict.py` の `dict add --speak` の `/synthesis` には引数を付けていない。単語は「？」で終わらないので差は出ない（実害は未確認）

## 分担の振り返り

- reviewer は、半角の「?」でも語尾が上がるのにコメントと文書が「？」しか挙げていないことを見つけた（直した）。
  `dict add --speak` にも `/synthesis` があることを挙げた。verifier は測った値で合格とし、食い違いは見つけなかった
- 見込みと食い違わなかった
- 1 行の変更で、reviewer の料金が main の半分近かった。次に同じ規模（URL の引数 1 つ）なら、reviewer を Sonnet 5.5 にし、
  verifier の実測はそのまま残す
