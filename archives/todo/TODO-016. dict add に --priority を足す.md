# TODO-016. dict add に --priority を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 5,695 | 53,779 | 68% |
| reviewer | Opus 5.5 | high | 437 | 30,099 | 18% |
| verifier | Sonnet 5 | medium | 1,674 | 31,197 | 14% |
| 合計 |  |  | 7,806 | 115,075 | 概算 $1.2 |

- 立ててから着手までに TODO-015 の決着が挟まったので、`--since '2026-09-29 00:03:40'`（`78ee90e` の時刻）で切った
- reviewer と verifier はモデルを定義どおりに指定した。effort は `~/.claude/agents/*.md` の値
- サブエージェントの分は少なめに出る（reviewer の output 437 は明らかに少ない）

## きっかけ

「節」をセツで登録しても、優先度 5 ではエンジン標準の「フシ」に負けた。`curl` で 7 に
上げてセツになった（`88ef11d`）。`dict add`（旧 `add-word`）には優先度を渡す手段が無かった。

## やったこと

- `src/claudecodespeak/user_dict.py`: `dict add` に `--priority N`（`click.IntRange(0, 10)`）を足した。
  省いたときは `--type` と同じ扱いで、新しい語は POST に priority を渡さずエンジンの既定（5）に任せ、
  登録済みの語は PUT に今の優先度を渡す
- `docs/UsersGuide.md` の「単語を登録する」に、優先度の意味と、読みが変わらないときに上げる使い方を書いた

## 確かめたこと

verifier が一時的な語 `ゾゾテスト` で実際に動かし、すべて仕様どおりだった
（`archives/agents/TODO-016/verifier-report.md`）。

- 新規・指定なし → 5、登録済み・指定なし → 5 のまま、登録済み・`--priority 8` → 8、
  その後の指定なし → 8 のまま、新規・`--priority 3` → 3
- `--priority 11` は click が弾いて終了コード 2
- 前後の `dict export` に差分なし。`uv run claudecodespeak test` が通る

## 分担の振り返り

- **reviewer** は要修正 0 件。好みの範囲で 2 件（POST で `extra` を組まず 5 を直接渡す、エンジンが
  1〜9 を推奨していることを文書に書く）。前者はエンジンの既定に任せる意図を残すため、後者は 0 と 10 の
  実害を確かめていないため、どちらも直していない
- **verifier** は 6 通りすべて一致。文書の「節」の例は再現の対象外と報告した（`88ef11d` の記録どおり）
- 見込みと食い違いは無い
- 次に同じ規模（1 ファイルに 1 オプション、分岐 2×2）をやるなら同じ組み方でよい。料金の 7 割は main で、
  reviewer はエンジンの openapi を読む分が主だった。API の仕様を main が先に引いて依頼に書いておけば、
  reviewer の読む量を減らせる
