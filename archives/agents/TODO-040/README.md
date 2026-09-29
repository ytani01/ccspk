# TODO-040 の分担

| 担当 | モデル | やったこと | 報告 |
|------|--------|-----------|------|
| main | Opus 5.5 | 実装・demo | — |
| reviewer | Opus 5.5 | NUL を消す位置が全経路に効くか、demo の例の強さ | `reviewer-report.md` |
| verifier | Sonnet 5.5 | テスト、直しを外すと落ちるか、prepare() から Popen まで NUL が届かないか | `verifier-report.md` |

分担の理由: 変更は `tidy()` の 1 行で、実装は main で足りる。整形の入口が変わるので reviewer を入れ、
verifier は reviewer の後に回した。
