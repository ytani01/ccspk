# TODO-016 reviewer 報告

対象: `git diff`（`src/claudecodespeak/user_dict.py`、`docs/UsersGuide.md`）。コードは直していない。

## 要修正

なし。

## 検討

なし。

## 好みの範囲

- `src/claudecodespeak/user_dict.py:119` / 新しい語で `extra` を組む 1 行を、`priority=5 if priority is None else priority`
  にして POST に直接渡す書き方もある（PUT の行と形が揃う）。
  根拠: 実測で `urllib.parse.urlencode({"priority": None})` は `priority=None` になるので、None をそのまま渡せず
  何らかの分岐は要る。今の形は「エンジンの既定に任せる」意図がはっきりしていて、既定値 5 をコードに持たない利点もある。
  どちらでもよい。
- `docs/UsersGuide.md:168` / エンジンの `/openapi.json` は priority について「1から9までの値を指定することを推奨」と書いている。
  文書とヘルプは 0〜10 とだけ書いている。0 と 10 を使ったときの実害は未確認。

## 問題が無かった点

- 分岐 4 通り: 指定あり・新規 → POST に priority を渡す / 指定なし・新規 → priority を送らない / 指定あり・登録済み →
  PUT に指定値 / 指定なし・登録済み → PUT に `old["priority"]`。TODO-016 の仕様（`--type` と同じ扱い）どおり。
  `priority is None` で判定しているので `--priority 0` も正しく指定ありになる（`or` にしていない）。
- エンジン（0.25.2）の `/openapi.json`: POST `/user_dict_word`、PUT `/user_dict_word/{word_uuid}` とも priority は
  任意のクエリ引数、integer、minimum 0 / maximum 10。`click.IntRange(0, 10)` と一致。PUT で送らない場合の扱いは
  openapi に既定値が無いので、今の値を毎回送る実装（差分前から）で正しい。
- 新しい語の既定 5: openapi に default の記載は無いが、`voicevox/user_dict.json` の 29 語のうち、priority を指定せずに
  登録した 28 語が 5（7 は `curl` で上げた「節」だけ）。文書・ヘルプ・コメントの「5」と合う。
- 範囲外の拒否（実測、エンジンに届く前に click が止める）: `--priority 11` / `-1` / `1.5` はいずれも
  `Error: Invalid value for '--priority'` で終わる。
- 文書と実装: UsersGuide の「品詞と優先度は、指定しなければ今のまま」「省くと、新しい語は 5、登録済みの語は今の優先度のまま」、
  モジュールの docstring の使い方の行、`--help` の文言が実装と合う。「節」の 5→7 の例は TODO-016 の背景（`88ef11d`）と合う。
- 周りとの揃い: オプションの並び・help の書き方・長い 1 行の書き方は `--type` と揃っている。
- テスト: 足した分岐はエンジンとの通信の引数だけで、`demo()` に足せる純粋な関数は増えていない。CLAUDE.md の
  「整形や分割を変えたら demo() に例を足す」にも当たらない。
- 範囲: 指示外の変更なし。

## 作り込みすぎ

`src/claudecodespeak/user_dict.py:L119: shrink: extra の dict を組む 1 行。priority=5 if priority is None else priority を POST に直接渡す、-1 行（上の「好みの範囲」と同じ）。`

net: -1 lines possible.
