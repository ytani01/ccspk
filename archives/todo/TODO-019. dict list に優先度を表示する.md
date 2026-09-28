# TODO-019. dict list に優先度を表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 2,644 | 11,007 | 61% |
| reviewer | Opus 5.5 | high | 388 | 23,572 | 27% |
| verifier | Sonnet 5.5 | medium | 296 | 21,641 | 12% |
| 合計 |  |  | 3,328 | 56,220 | 概算 $0.6 |

- verifier は定義のモデル（`sonnet`）が Sonnet 5.5 で動いた。見込みの Sonnet 5 は書き誤り

## きっかけ

`dict add` の優先度の既定（5）が低すぎないかを調べたとき、上げた単語がどれかを
`voicevox/user_dict.json` を集計して見るしかなかった。エンジンの `GET /user_dict` は
`priority` を返しているのに、`dict list` は表示していなかった。

## やったこと

- `src/claudecodespeak/user_dict.py` の `list_`: 各行の末尾に `priority` を足した
  （ID・表記・読み・accent_type・優先度）。docstring も合わせた
- `docs/UsersGuide.md` の `dict list` の説明に「優先度」を足した

## 確かめたこと

- `dict list` の 33 行がすべて 5 列で、優先度がエンジンの値と合う（verifier）
- `uv run claudecodespeak test` が通る
- 文書・docstring と実際の列の並びが一致し、他の記述に直し漏れが無い（reviewer）

## 残ること

- エンジンの辞書にある bash・sh・zsh（sh は優先度 7）が `voicevox/user_dict.json` に無い。
  この項目とは別に登録したもので、`dict export` がまだと見られる（verifier の報告。
  この項目では書き出していない）

## 分担の振り返り

- reviewer: 指摘なし。行末の accent_type と優先度が数字だけで並んで見分けにくい、を
  好みとして挙げた（文書に並び順があるので直さなかった）
- verifier: 列と値の一致を実測した。範囲外だが、エンジンと json の食い違い（bash・sh・zsh）を見つけた
- 見込みとの食い違いは verifier のモデル名の書き誤りだけ
- 次に同じ規模（表示 1 行と文書 1 行）なら: reviewer は料金の 27% を使って指摘 0 だった。
  条件式が変わらない表示だけの変更では reviewer を外し、verifier に「文書との一致」も
  見させる形で足りる
