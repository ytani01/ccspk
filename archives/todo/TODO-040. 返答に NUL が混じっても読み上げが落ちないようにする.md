# TODO-040. 返答に NUL が混じっても読み上げが落ちないようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 5,363 | 50,655 | 66% |
| reviewer | Opus 5.5 | high | 376 | 40,928 | 26% |
| verifier | Sonnet 5.5 | medium | 470 | 22,244 | 7% |
| 合計 |  |  | 6,209 | 113,827 | 概算 $1.1 |

- reviewer・verifier は `~/.claude/agents/` の定義のモデルと effort のまま

## きっかけ

TODO-038 のレビュー（2026-09-29）で見つけた。返答に NUL（`\0`）が混じると、`speak()` の `Popen` が argv に
NUL を渡せず `ValueError: embedded null byte` になる。TODO-038 で字下げした行の印（`WRAP`）に `"\0"` を
使うようにしたので、行頭の NUL がその印と見分けられないことも重なった。

## やったこと

- `src/ccspk/hook.py` の `tidy()` の最初で NUL を消す。Stop・MessageDisplay・PreToolUse の 3 つのイベントは
  どれも `prepare()` → `tidy()` を通り、要約の経路（`summarize()` → `to_speech()`）と `check.record()` も
  `tidy()` の後の文を受け取るので、ここ 1 か所で足りる。`ccspk say` は argv から来るので NUL を含められない。
  `mark_wrapped()` より前なので、行頭の NUL を `WRAP` と取り違えない
- `demo()` に `to_speech("a\0b\n\0c") == "ab。 c"` を足した

## 確かめたこと

- `uv run ccspk test` が通る
- `tidy()` の 1 行を外すと `demo()` の例で落ちる（`'a\x00b c'` が返る）。空白に置き換える直し方でも落ちる
- 直す前の `Popen(["true", "a\0b"])` は `ValueError: embedded null byte`
- 直した後、`prepare("前\0置き\n\0続き")` は `"前置き。 続き"` を返し、それを `child_args()` に入れた `Popen` は落ちない
  （本物の `speak()` は呼ばず、XDG の各ディレクトリを一時ディレクトリに向けて試した）

詳しくは `archives/agents/TODO-040/`。

## 分担の振り返り

- reviewer は指摘 0 件。全経路が `tidy()` を通ることと、demo の例が直す前に落ちることを確かめた。
  verifier も食い違い 0 件で、直しを外すと落ちること、`prepare()` から `Popen` まで NUL が届かないことを実測した
- 見込みと同じ編成で動いた
- 次に 1 行の直しで経路が 1 つに集まっているとはっきりしている項目なら、reviewer は Sonnet に下げてよい
  （料金の 26% を占めたが、見るべきことは呼び出し元を洗うだけだった）。verifier は省かない
