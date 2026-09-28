# TODO-018. 辞書の表記を半角で表示・書き出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus / high）+ verifier（Sonnet / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 6,433 | 19,251 | 59% |
| reviewer | Opus 5.5 | high | 428 | 34,716 | 23% |
| verifier | Sonnet 5 | medium | 2,155 | 34,634 | 18% |
| 合計 |  |  | 9,016 | 88,601 | 概算 $1.1 |

- どちらの担当もモデルを上書きしていない（定義の `opus` / `sonnet` のまま）

## きっかけ

エンジンは `dict add` で受け取った英数字・記号を全角にして持つ（`ｒｅｖｉｅｗｅｒ`、`／ｅｔｃ／`）。
`dict list` の表示も `voicevox/user_dict.json` も全角になり、読みにくい。
利用者の選択で、表示だけでなく `export` も半角にした。

## やったこと

- 着手前に測った: 半角の表記（`zzqtest`）の JSON を `/import_user_dict` に渡すと、エンジンは
  `ｚｚｑｔｅｓｔ` に直して持ち、読み上げにも効いた。だから `import` は変えていない
- `src/claudecodespeak/user_dict.py` に `halfwidth()` を足した。U+FF01〜U+FF5E を
  `str.translate` で半角へ。NFKC は半角カナなども変えるので使わない。`demo()` に範囲の両端を含む例と、
  半角カナ・全角スペースを変えない例を足した
- `dict list` は半角の表記で表示し、半角の表記で並べる（全角のままだと英字が漢字の後ろに来る）
- `dict export` は表記を半角にして書き出す。`voicevox/user_dict.json` を書き出し直した
- `find()` は NFKC で比べているので変えていない。`docs/UsersGuide.md` には該当する記述が無かった

## 確かめたこと

- `claudecodespeak test` が通り、変換範囲を 1 文字削ると `demo()` が落ちる
- `dict list` と `dict export` の出力に U+FF01〜U+FF5E が 0 件
- 書き出した結果と `voicevox/user_dict.json` が一致し、差分は `"surface"` の行だけ

詳しくは `archives/agents/TODO-018/`。

## 分担の振り返り

- reviewer: 要修正 0 件。`demo()` が変換範囲の両端を通っていないことを見つけ、例を足した
- verifier: 食い違い 0 件。`docs/UsersGuide.md` のチェックが無変更のまま入っていることを指摘し、
  項目に「該当する記述は無い」と書き足した
- 見込みどおりの編成で動いた。import の往復を main が先に測ったので、reviewer と verifier から
  エンジンを叩く作業を外せた
- 次に同じ規模（1 ファイルの表示の変更）をやるなら同じ組み方でよい。reviewer の指摘が
  テストの強さだけだったので、分岐がこれくらい単純なら reviewer を Sonnet にしてよい
