# TODO-057. CLAUDE.md の ccspk test の説明に check を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | main のみ |
| 実施 | Opus 5.5 / effort 既定 | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 既定（medium） | 14 | 1,370 | 34,578 | 347,802 | 100% |
| 合計 |  |  | 14 | 1,370 | 34,578 | 347,802 | 計 383,764 |

- 立ててから着手まで TODO-058 を挟んだので、`--since '2026-09-30 01:38:00'` で集計した

## きっかけ

`/claude-api prompt-audit` で、`src/ccspk/cli.py` の `test` が `hook_demo()`・`dict_demo()`・`check_demo()` の 3 つを
走らせるのに、`CLAUDE.md` には hook・dict しか書いていないと分かった（2026-09-30）。

## やったこと

- `CLAUDE.md` の「コマンド」の `uv run ccspk test` のコメントを「hook・dict・check の自己テスト（demo() の assert）」にした

## 確かめたこと

- `src/ccspk/cli.py` の `test`（docstring「hook・dict・check の自己テストを走らせる。」と、`check_demo()` の呼び出し）と合っている
- 定義ファイルの文だけの変更なので、確認は main が行った
