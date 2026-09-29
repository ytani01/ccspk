# TODO-042 reviewer 報告

対象: `git diff`（src/ccspk/hook.py の `synthesize()`、docs/Developer.md の「3.2 子プロセス」、TODO.md のチェック）

## 要修正

なし

## 検討

なし

## 好みの範囲

- `src/ccspk/hook.py:381` と `docs/Developer.md:147` / 「？」で終わる文、とだけ書いている /
  半角の「?」でも同じく疑問文として扱われる（実測: エンジン 0.25.2 の `/audio_query`、話者 119 で
  「そうですか?」も `is_interrogative: true`。「そうですか？」」のように閉じ括弧が後ろに付いても true）。
  TODO.md の項目は「？」「?」と両方書いている。コードの動きは変わらないので、文書の表記だけの話

## 問題が無かった点

- 引数の仕様: エンジンの openapi.json で `/synthesis` の query に `enable_interrogative_upspeak`（boolean、既定 true、
  「疑問系のテキストが与えられたら語尾を自動調整する」）がある。`false` の文字列で受け付ける
- 効き目（最小限の確認のみ）: 「そうですか？」の同じ query で、引数なし 52780 バイト、`=true` 52780、`=false` 45612。
  HTTP 200。既定は有効で、`false` で語尾の 1 音が落ちる。聞いての確認は verifier の担当
- 他の `/synthesis` 呼び出し: `src/ccspk/user_dict.py:188`（`dict add --speak`）が残る。登録した単語の表記だけを
  読むので、表記が「？」で終わらない限り差は出ない（実害は未確認。単語の読みの確認用なので揃えなくてよいと見る）
- 疑問文の扱いへの影響: `ENDS`（hook.py:40）で文を区切る処理は変えていない。「？」を置き換える案を採らなかった
  背景とも合う
- 文書とコードの一致: Developer.md の説明（`/synthesis` に渡す、渡さないと「ァ」を 1 音足す）はコードと合う
- コメント: 「なぜ」（「かぁ」と伸びて聞こえる）を書いている
- 範囲: 指示どおりの 3 ファイルだけ。余計な変更なし
- 書式: Developer.md:147 は 77 桁で、ファイル内の他の行（最大 180）と並べて外れていない
- テスト: エンジンへの HTTP 呼び出しの引数 1 つで、`demo()` の対象（整形や分割）ではない。足さなくてよい
- TODO.md: 実装できた時点でチェックを入れる規則どおり

## 作り込みすぎ

作り込みすぎ: なし（query 文字列に 1 引数足しただけ。Lean already. Ship. net: -0 lines possible.）
