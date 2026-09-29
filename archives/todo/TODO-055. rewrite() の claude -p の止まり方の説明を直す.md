# TODO-055. rewrite() の claude -p の止まり方の説明を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort 既定 | main（文書）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 既定 | main（文書）+ verifier（Sonnet 5.5 / medium）+ wording（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 既定（medium） | 40 | 6,240 | 48,207 | 1,140,778 | 88% |
| verifier | Sonnet 5.5 | medium | 8 | 329 | 18,379 | 62,154 | 6% |
| wording | Sonnet 5.5 | medium | 8 | 210 | 21,073 | 57,798 | 6% |
| 合計 |  |  | 56 | 6,779 | 87,659 | 1,260,730 | 計 1,355,224 |

- 集計は `--since '2026-09-30 01:11:45'`（TODO-056 の決着のコミットの時刻）。立ててから着手までに TODO-056 を挟んだため
- wording は利用者の指示で足した
- 決着の作業の分は、集計の後なので入っていない

## きっかけ

TODO-054 の決着後に、利用者が別に取ったレビューで指摘された（2026-09-30）。

- `docs/Developer.md` の「3.2 子プロセス」で、TODO-054 に足した段落を `rewrite()` の手順 1 の途中に入れたので流れが切れ、
  「`CCSPK_SPEAK=0` は念のためで、これだけでは止まらない」がこの `claude -p` のことに読める
- 実際には、この `claude -p` は `--setting-sources ""` で `settings.json` を読まないので、`0` はそのまま届く

`docs/UsersGuide.md` の追記は問題ないので変えない。

## やったこと

- `docs/Developer.md` の「3.2 子プロセス」から、手順 1 の途中の 4 行を抜き、手順 1〜5 の後ろへ独立した段落として置いた
- 「念のためで、これだけでは止まらない」を、「`settings.json` を読まないので `CCSPK_SPEAK=0` もそのまま届く。
  効かないのは `settings.json` を読む `claude -p` の場合」と書き分けた
- wording が、手順の外に出た段落の「この `claude -p`」を「要約・翻訳の `claude -p`」に直した
- 決着の後、利用者の指摘で、段落の最後の「点検の `claude -p`（`check.py`）も同じ。」を消し、書き出しを
  「要約・翻訳と点検（`check.py`）の `claude -p` で…」にした。直前の「効かないのは…」の文に続くので、
  点検でも効かないと読めたため（`check.py` も `--setting-sources ""` を付け、`CCSPK_SPEAK=0` を渡している）

## 確かめたこと

verifier（報告は `archives/agents/TODO-055/verifier-report.md`）:

- `CCSPK_SPEAK=0 claude -p … --setting-sources "" …` の子プロセスで `printenv CCSPK_SPEAK` が `0` を返した（1 回）
- `git diff` で、消したのは手順 1 の 4 行、足したのは手順 5 の後ろの段落だけで、手順 1〜5 に欠けも重なりも無い。
  手順 1 は「終了コードが 0 なら…」に続いている

## 分担の振り返り

- verifier は、依頼のコマンドがそのままでは動かないこと（`--allowedTools` が可変長で、後ろのプロンプトまで取り込む）を見つけ、
  プロンプトを前に出して測った。文書の主張は実測で合った
- wording は 1 か所（指す先の明示）を直した。見込みに無かったのは、利用者が推敲を頼んだため
- 次に同じ規模の文書の移動をやるなら: 実測のコマンドは依頼の前に形を確かめる（`--allowedTools` のような可変長の
  オプションの後ろに引数を置かない）。段落を別の場所へ移すときは、指示語が移した先で何を指すかを main が先に見る。
  見ていれば wording の 1 か所は main で直せた
