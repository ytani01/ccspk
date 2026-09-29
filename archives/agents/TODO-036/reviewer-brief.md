# TODO-036 レビューの依頼（main → reviewer）

目的: TODO-036（読み間違いを見つけて辞書に自動で登録する）の差分が、設計と規約に照らして良いかを見る。
「動くか」は後で verifier が見るので、ここでは実行して確かめるより、分岐の意味・壊れ方・余計なものを見る。

読むもの:

- 設計: `archives/agents/TODO-036/brief.md`、決まったこと: `TODO.md` の TODO-036
- 実装の報告: `archives/agents/TODO-036/implementer-report.md`（「判断が要る点」の 1〜8 も）
- 差分: `git diff` と `src/ccspk/check.py`（新規）

特に見るもの:

- フック（`hook.py` の `main()`）: 読み上げの挙動と最初の音までの時間を変えていないか。Stop のときだけ点検を起こす条件
  （早い return・`LAST` で 2 度読まないとき・`OSError`）が brief どおりか
- `check.py`: 同時に 1 つだけ走ること、失敗の拾い方（`sys.exit` を含む）、`CHECKED` の mtime の扱いで点検の漏れ・重複が起きないか、
  `spoken.txt` の切り詰めが追記と競合したときに壊れないか、`claude -p` がフックを走らせない（`--setting-sources ""`・`CCSPK_SPEAK=0`）
- 返答の読み取りで、誤った登録（渡していない表記、カタカナでない読み、エンジンの読みと同じ読み）を防げているか
- `user_dict.py`: `dict add` の出力と引数が変わっていないか、`forget_auto` の循環 import、`dict auto --remove`
- `demo()` の assert が、壊すと落ちる強さか
- 文書（UsersGuide・Developer）が実装と合っているか。`docs/Developer.md` の「2. 動き方」の既存の文を書き換えていないか
- 過剰なもの（要らない抽象・設定・分岐）

見なくてよいもの: ruff の既存の指摘、整形、文書の言い回しの好み。

境界線上の判断は報告だけにする。コードは直さない。「実害は未確認」なら、そう添える。

報告は `archives/agents/TODO-036/reviewer-report.md` に、指摘ごとに「場所・何が問題か・起きる条件・重さ（直すべき／任意）」。
問題の無かった観点は 1 行ずつ。返事は 5 行以内（終わったか・報告のパス・直すべき指摘の数）。
