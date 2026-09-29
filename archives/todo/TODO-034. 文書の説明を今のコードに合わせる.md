# TODO-034. 文書の説明を今のコードに合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換え）+ reviewer（Opus 5.5 / high） |
| 実施 | Opus 5.5 / effort medium | main（書き換え）+ reviewer（Opus 5.5 / high） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 15,640 | 78,767 | 76% |
| reviewer | Opus 5.5 | high | 3,878 | 62,703 | 24% |
| 合計 |  |  | 19,518 | 141,470 | 概算 $2.4 |

- reviewer は定義のモデル（opus）・effort（high）のまま
- main の分には、途中で受けた質問（読みの確認と辞書登録を自動にできるか）への回答も入っている

## きっかけ

2026-09-29 に README.md・CLAUDE.md・docs/ を `src/` と突き合わせたところ、`docs/Developer.md` の
関数と定数の表、自己テストの説明が今のコードより古く、リポジトリの Stop フック（TODO-031）の説明が
Developer.md に無かった。`docs/UsersGuide.md` の「2.2 記号と数字」は、英単語と日本語の間のスペースと
コミット ID まで扱っていて、見出しと中身が合っていなかった。

## やったこと

- `docs/Developer.md`
  - 「1. ファイル」の表に `.claude/settings.json` を足した
  - 「2. 動き方」の「記号と数字は置き換え」を「辞書で直せないもの（記号や数字など）は置き換え」にした
    （reviewer の指摘。利用者が直すと決めた）
  - 「3.6 整形と分割」の表に `drop_commit_ids()`・`squeeze()` を足し、`to_speech()`・`chunks()` の行から
    それぞれを呼ぶことを書いた。UsersGuide へのリンクを `#22-辞書で直せないもの` に張り替えた
  - 「3.7 定数」の表に `DIGITS` を、コードの並びどおり `SPACE_WITHIN` の後ろに足した
  - 「4.1 自己テスト」を、hook と dict の `demo()` がそれぞれ何を確かめているかの 2 文にまとめた
    （dict 側に `halfwidth` を足した）
  - 「4.4 入れ直し」を新しく書いた
- `docs/UsersGuide.md`: 見出しを「2.2 辞書で直せないもの」にし、書き出しを「`hook.py` で置き換えている」
  にした（スペースを詰めるのは `to_speech` ではなく `chunks` のため）
- `CLAUDE.md`: 「注意」の Stop フックの説明を縮め、詳しくは Developer.md の「4.4 入れ直し」を見るようにした
  （reviewer の指摘。2 か所に同じ説明があり、CLAUDE.md 側は入れ直しに失敗したときが抜けていた。利用者が縮めると決めた）

TODO には旧見出しへのリンクが「2 か所」とあったが、実際は Developer.md の 1 か所だけだった。
もう 1 か所と数えたのは、リンク先が `#2-読み上げの辞書` の「2. 動き方」の行と思われる（上で直した）。

## 確かめたこと

- reviewer（`archives/agents/TODO-034/reviewer-report.md`）: 書いた説明はコードと合っていた。
  文書の中のアンカー 20 件がすべて実在する見出しに当たる。要修正 0 件、検討 2 件、好みの範囲 2 件で、
  4 件とも main が直した（検討の 2 件は利用者が決めた）
- `rg -n '記号と数字' -g '!archives' -g '!TODO.md'` で残るのは、3.6 の `to_speech()` の行
  （`drop_commit_ids()` の後の記号と数字の置き換えを指していて、コードと合う）だけ
- `uv run ccspk test` が通る

## 分担の振り返り

- reviewer は、TODO の範囲の外（CLAUDE.md、差分の外の Developer.md の 30 行目）で同じ種類のずれを 2 件
  見つけた。main は書き換えるときに、TODO に挙がっていた所しか見ていなかった
- 見込みどおりの編成で、食い違いは無い。reviewer の後に main が直した 4 点は reviewer に見直させず、
  main が `rg` と目で確かめた（言い回しと 1 行の移動だけのため）
- 次に同じ規模の文書の項目をやるなら、同じ組み方でよい。ただし書き換える前に main が
  `rg` で同じ言い回しを文書全体から拾い、範囲の外に同じずれが無いかを先に見る。そうすれば
  reviewer の後のやり取り（利用者への確認）が減る
