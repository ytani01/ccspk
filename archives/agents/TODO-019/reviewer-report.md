# TODO-019 reviewer 報告

対象: `git diff`（`src/claudecodespeak/user_dict.py` の `list_`、`docs/UsersGuide.md` 182 行、`TODO.md` のチェック）

## 要修正

なし。

## 検討

なし。

## 好みの範囲

- `src/claudecodespeak/user_dict.py:155` / 行末に `accent_type` と優先度が
  どちらも裸の整数で並ぶ（実測: `... ドットエムディー  4  5`）。/ 見出しが無いので、
  どちらがどちらかは docstring か `docs/UsersGuide.md:182` の並び順で読むしかない。
  文書に順が書いてあるので、このままでもよい。

## 問題なし（1 行ずつ）

- 出力・docstring（152 行）・`docs/UsersGuide.md:182` の並び（ID・表記・読み・accent_type・優先度）が一致。
- 直し漏れ: `rg -n "dict list|accent_type" docs README.md src` の他の箇所（モジュール先頭の使い方 5 行目、`UsersGuide.md` 162・178 行、`add` の表示）は列の説明を持たず、直す所なし。
- `priority` が無い単語で落ちうるか: 落ちるのは `KeyError` だが、実測でエンジンの `GET /user_dict` は 33 件すべてに `priority` を返し、`voicevox/user_dict.json` も 30 件すべてに持つ。`add` の 127 行も同じく `old["priority"]` を無条件で読んでおり、既存の作りと揃っている。欠ける場合の実害は未確認。
- テスト: 表示の f-string に 1 列足しただけで、`demo()` に足すべき分岐は無い。
- 範囲: 指示外の変更なし。`TODO.md` はチェックを入れただけ。
- 書式: 155 行は長いが、同ファイルの 113・114 行も同程度の長さで、規約に行長の定めなし。

## 作り込みすぎ

なし（Lean already. Ship.）
