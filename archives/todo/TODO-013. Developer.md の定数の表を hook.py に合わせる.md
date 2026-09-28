# TODO-013. Developer.md の定数の表を hook.py に合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書の修正）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（文書の修正）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 3,036 | 9,740 | 74% |
| verifier | Sonnet 5 | medium | 2,270 | 30,334 | 26% |
| 合計 |  |  | 5,306 | 40,074 | 概算 $0.5 |

- 立ててから着手までに TODO-014 を立てたので、`--since '2026-09-28 14:35:05'` で集計した

## きっかけ

wording で推敲したときに見つかった（2026-09-28）。`PARTS_KEEP` と `SAME_WITHIN` は
「流れ」の本文には出てくるが表に無く、`MODULE` も無かった。`PLAY` の行は、
`stop_playing()` が `--play` だけで見分けるように読めた。

## やったこと

`docs/Developer.md` の「定数」の表:

- `MODULE`・`PARTS_KEEP`・`SAME_WITHIN` の行を足した
- `PLAY` の行を「`stop_playing()` は `MODULE` と合わせて見分ける」に直した

パスの定数（`PIDFILE`、`LOCK` など）は「ファイル」の表にあるので足していない。

## 確かめたこと

verifier が、表の全行を `src/claudecodespeak/hook.py` の値・コメント、`stop_playing()` の
判定、「流れ」「前の再生を止める」の記述と突き合わせ、食い違いは無かった
（[報告](../agents/TODO-013/verifier-report.md)）。

## 分担の振り返り

- verifier は食い違いを見つけなかった。表以外に漏れている定数も無かった
- 見込みと実施は同じだった
- 表の数行を直すだけの項目なら、次も main が直して Sonnet の verifier 1 人で突き合わせる。
  突き合わせる対象が 15 行ほどで判断も要らないので、Haiku でも足りた可能性がある
