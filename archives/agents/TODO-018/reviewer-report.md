# TODO-018 reviewer 報告

対象: `git diff` の `src/claudecodespeak/user_dict.py` と `voicevox/user_dict.json`（未コミット）。
エンジンは叩いていない。手元の Python で `halfwidth()` と並び順だけ試した。

要修正: 0 件 / 検討: 1 件 / 好みの範囲: 1 件

## 検討

### `src/claudecodespeak/user_dict.py:99` — `demo()` が変換範囲の両端を確かめていない

- 何が問題か: 例が `／ｅｔｃ／ＴＯＤＯ－０１` だけで、範囲の両端（U+FF01 `！` と U+FF5E `～`）を通らない。
- 根拠（実測）: `HALF` を `range(0xFF01, 0xFF5E)`（上端を 1 つ削る）や
  `range(0xFF02, 0xFF5F)`（下端を 1 つ削る）に変えても、`demo()` はどちらも `ok` を出した。
  いまの範囲そのものは正しい（94 文字、0xff01〜0xff5e、`halfwidth("！～＼｀") == "!~\\`"`）。
- 両端の文字を 1 つずつ例に足せば、範囲の書き間違いで落ちるようになる。

## 好みの範囲

### `src/claudecodespeak/user_dict.py:75` — コメントの「！〜～」

範囲を表す波ダッシュ「〜」（U+301C）と、範囲の端の全角チルダ「～」（U+FF5E）が並んでいて、
見分けにくい。`TODO.md` のように `U+FF01〜U+FF5E` と書くほうが誤読しにくい。

## 問題なしの観点

- 変換範囲: U+FF01〜U+FF5E から 0xFEE0 を引くと 0x21〜0x7E。全角スペース（U+3000）と半角カナは変えない。正しい。
- `list` の並び順: 全角どうしの前後は変わらず、英数字・記号が仮名・漢字より前に来るようになる（以前は後ろ）。docstring の「表記順」とは合っている。
- 往復で表記がぶつかるか: エンジンが持つ表記には 0x21〜0x7E が無い（全角に直すため）ので、半角に戻しても 2 つの単語が同じ表記になることはない。ぶつからない。
- `find()` の NFKC 比較との食い違い: U+FF01〜U+FF5E は NFKC でも同じ半角になる。`list` に出た表記を `remove`・`add` に渡しても `find()` で見つかる。食い違いなし。
- エンジンが半角に戻すのが 0x21〜0x7E ちょうどか（スペースを変えるか）は、エンジンのソースが手元に無く未確認。変えていても表示が全角のまま残るだけで、実害は未確認。
- docstring・コメント: `halfwidth()` と `export` の docstring は実態と合っている。
- `voicevox/user_dict.json`: 差分は `"surface"` の行だけ（25 行ずつ）。書き出し後の JSON に U+FF01〜U+FF5E の文字は残っていない。
- `docs/UsersGuide.md`: 全角・半角に触れた記述は無く、直す箇所は無い。
- テスト: `uv run claudecodespeak test` は通る（`ok`）。`list`・`export` はエンジンが要るので `demo()` に無いのは妥当。
- 範囲: 指示に無い変更は無い。

## 作り込みすぎ

作り込みすぎ: なし（`str.translate` と表 1 つ。`str.maketrans` に替えても行数は同じ）。
