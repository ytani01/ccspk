# TODO-020. dict add の優先度の既定を 7 にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 5,210 | 46,127 | 66% |
| reviewer | Opus 5.5 | high | 403 | 33,619 | 24% |
| verifier | Sonnet 5.5 | medium | 164 | 28,031 | 10% |
| 合計 |  |  | 5,777 | 107,777 | 概算 $1.0 |

- 立ててから着手まで空いたので、`--since '2026-09-29 05:47:00'`（着手した会話の始まり）で集計した
- サブエージェントの分は少なめに出ている（`subagents/` のログの取りこぼし）

## きっかけ

`dict add` で足した単語が、エンジンの既定の優先度 5 ではエンジン標準の読みに負けることがあった
（「節」はフシのままで、7 でセツになった）。`dict add` で足す単語は、エンジン標準の読みより
優先させたいものと見なし、既定を 7 にする。「節」「語」を 7 にしても「物語」「単語」「英語」
「季節」「調節」の読みは崩れなかった（2026-09-29 に確かめた）。

## やったこと

- `src/ccspk/user_dict.py` の `add`: 新しい単語で `--priority` を省くと 7 を渡す。
  登録済みの単語の書き換えで省いたときは今の優先度のまま（変えていない）
- `--priority` の help を、新しい既定に合わせた
- `docs/UsersGuide.md` の「単語を登録する」: 既定を 7 と書き、7 でも読みが変わらなければ
  さらに上げる、とした。reviewer の指摘で「優先される」の言い切りを「多くは優先される」に弱めた
- `dict import` は書き出したファイルの優先度をそのまま戻すので変えていない

## 確かめたこと

- `ccspk test` が ok
- 一時ディレクトリの辞書で、`--priority` なしの新規登録は 7、`--priority 3` で書き換えると 3、
  続けて `--priority` なしで書き換えても 3 のまま、`--priority 0` の新規登録は 0
  （verifier、[報告](../agents/TODO-020/verifier-report.md)）
- reviewer は `call` を差し替えて同じ分岐を確かめ、要修正は無し
  （[報告](../agents/TODO-020/reviewer-report.md)）

## 分担の振り返り

分担の理由は [archives/agents/TODO-020/README.md](../agents/TODO-020/README.md)。

- reviewer は文書の言い切りと次の文との食い違いを 1 件見つけた（直した）。分岐の誤りは無かった
- verifier は食い違いを見つけなかった。見込みどおりで、編成も見込みと同じ
- 次に同じ規模（数行で既定値を変える）なら、reviewer は effort medium で足りる。reviewer が
  `call` の差し替えで分岐を確かめたため verifier の実測と重なったので、reviewer には
  「分岐の実行確認は verifier が行う」と書いて静的なレビューに絞らせる
