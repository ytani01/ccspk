# TODO-030. 英単語と日本語の間の空白を詰める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 22,184 | 54,025 | 66% |
| reviewer | Opus 5.5 | high | 6,891 | 74,432 | 31% |
| verifier | Sonnet 5.5 | medium | 637 | 44,319 | 3% |
| 合計 |  |  | 29,712 | 172,776 | 概算 $3.2 |

- 立てた直後に TODO-031 を立てて着手したので、`--since '2026-09-29 07:05:35'`（この項目に着手した時刻）で数えた
- TODO-031 と並行したので、main・reviewer・verifier の数字には TODO-031 の分（決着の作業、TODO-031 の
  reviewer・verifier の途中から）が混ざっている。時刻では切り分けられない
- reviewer・verifier はサブエージェントのログが少なめに出る（`todo-workflow` skill）

## きっかけ

英単語と日本語の間のスペースの前後に間が入る（`reviewer の指摘` → レビュウタ'ントウ、ノ'、
`同じ reviewer に` → オナジ'、レビュウタ'ントウ、ニ'）。

背景（決めたこと）:

- 英→日（`reviewer の`）と日→英（`同じ reviewer`）の両方向を詰める。英単語同士（`Claude Code`）の空白は残す
- `split_first` は区切りが 30 字以内に無い文を空白で切っている（最初の音を早めるため）ので、
  `to_speech` では詰めず、`chunks` で切った後に塊ごとに詰める

## やったこと

- `src/ccspk/hook.py` に `squeeze` を足し、`chunks` が返す塊ごとに通すようにした。英単語の側は `[A-Za-z]` だけ。
  数字を入れると、行をまたいだ「手順 1\n次へ」（`to_speech` がわざと詰めていない）が「1次」になるため
- `demo()` に例を足した（両方向、英単語同士・数字は残す、スペースで切った塊、続くスペース）
- 詰める前後の読みを `dict kana` で比べた（[kana.md](../agents/TODO-030/kana.md)）。6 例とも間が消えた。
  `3 files を` は「ファイルエス、オ」が「ファイルズオ」になった
- `docs/UsersGuide.md` の「記号と数字」に書き足した。reviewer の指摘で数字の書き方を上の箇条と揃え、
  verifier の指摘で「切るのに使ったスペースの所には間が残る」を足した

## 確かめたこと

- reviewer が `squeeze` を 11 通り壊して、どれも `demo()` が落ちることを確かめた
  （[reviewer-report.md](../agents/TODO-030/reviewer-report.md)）
- verifier が、`ccspk test` が通ること、UsersGuide.md の例、kana.md の 6 行の再現を確かめた
  （[verifier-report.md](../agents/TODO-030/verifier-report.md)）
- TODO-031 のフックで、`squeeze` の入った版が自動で入れ直されたことを `uv tool list` と入ったファイルで確かめた

## 残ること

どれも実害は未確認なので、このままにした。

- 行をまたいだ「日本語の行末＋英単語の行頭」も詰めるので、行の間の「、」の間が消える。読み違いは出ていない
- 1・2 文目を `split_first` が英単語と助詞の間のスペースで切ると、そこには間が残る
  （`reviewer の指摘。` → `reviewer` / `の指摘。`）。決めたとおりの動き
- 全角英字（`Ａｐｉ を`）、アクセント付きの字（`café の`）、`foo() を` の `)` の後ろは詰めない

## 分担の振り返り

- reviewer は UsersGuide.md の食い違い（数字の扱い）と、docstring の「数字の後ろ」の誤りを見つけた。
  日本語の文字の範囲の書き方が `to_speech` と違うという指摘は、表示で `\u` が字に置き換わって見えたための
  誤りだった。verifier は、1 文だけの短い文では UsersGuide.md の例どおりの 1 つの文字列にならないことを見つけた
- 見込みどおりの編成だった
- 次に `split_first` の後で塊を整える項目では、main が文書の例を `chunks(to_speech(...))` に 1 文だけで
  通して確かめてから書く。verifier が見つけた食い違いは、この確かめ方で先に分かった
