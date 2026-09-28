# TODO-017. 辞書の 1 件を「語」でなく「単語」と書く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換え）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（書き換え）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 3,505 | 9,165 | 74% |
| verifier | Sonnet 5 | medium | 1,233 | 34,788 | 26% |
| 合計 |  |  | 4,738 | 43,953 | 概算 $0.6 |

- verifier のモデルは定義どおり。effort は `~/.claude/agents/verifier.md` の値

## きっかけ

TODO-016 の報告で「新しい語」「登録済みの語」と書いたのを、利用者が「『単語』のほうがわかりやすい」と言った。
元の英語はエンジンの API の `word`（`UserDictWord`・`/user_dict_word`）。「登録語」「エントリ」も候補に
挙げたが、`docs/UsersGuide.md` の見出しがすでに「単語を登録する」なので「単語」に揃えた。

## やったこと

辞書の 1 件を指す「語」を「単語」にした。「1 語だけ」は「単語 1 つだけ」、「1 語 1 行」は「1 単語 1 行」。

- `src/claudecodespeak/user_dict.py`: docstring と `--type`・`--priority` の help（10 か所）
- `docs/UsersGuide.md`（8 か所）、`docs/Developer.md`（1 か所）、`README.md`（2 か所）、`CLAUDE.md`（1 か所）

文の区切りやトークンを指す「語」（`hook.py` の 4 か所、`docs/Developer.md` の「語の中の半角「:」」）は変えていない。
一括置換で「日本語」が「日本単語」になり、`user_dict.py` に余分な空白が入ったのは、main が直してから確認に回した。

## 確かめたこと

verifier が確かめ、食い違いは無かった（`archives/agents/TODO-017/verifier-report.md`）。

- `rg` の残りに、辞書の 1 件を指す「語」は無い。残した箇所の判断とも食い違わない
- 差分に巻き込み・壊れた語・余分な空白が無い
- `dict` の各サブコマンドの `--help` に「単語」が出て崩れていない。`uv run claudecodespeak test` が通る

## 分担の振り返り

- **verifier** は食い違いを見つけなかった。巻き込み（「日本単語」）は main が差分を読んで先に見つけていた
- 見込みとの食い違いは無い
- 次に同じ規模（文言だけの置換、20 か所前後）をやるなら同じ組み方でよい。置換は正規表現で一括にせず、
  対象の行の語を列挙してから置き換えれば、巻き込みの直しの手間が要らない
