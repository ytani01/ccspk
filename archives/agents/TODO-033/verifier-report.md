# TODO-033 確認（verifier）

## 1. ccspk test
`.venv/bin/ccspk test` -> 出力 `ok` `ok`、終了コード 0。

## 2. 壊すと落ちるか（archives/agents/TODO-033/mutate.py）
hook.py を一時ディレクトリへコピーして 1 つずつ置換し、`demo()` を実行。ベースラインは PASS。
9 通りすべて `AssertionError` で落ちた（落ちなかったものは無い）。

1 規則1 でした外す / 2 規則1 全角：外す / 3 規則3 `(?<=[（(])` 外す / 4 規則4 に外す /
5 規則5 先読み緩める / 6 `[*>]` を drop の後へ / 7 規則4 先頭 `[ \t]*` 外す /
8 規則1 否定クラスから「、」外す / 9 規則1 コミットは→は
（どの assert が落ちたかは見ていない。「狙った分岐だけが落ちる」かは未確認）

## 3. UsersGuide 2.2 の例を to_speech に通した
16 例すべて書いてあるとおり。
- ID だけ消す 3 例、件名 2 例、文ごと消す 2 例（`- **…**: ` 付きと範囲も）、消さない 2 例（ほか docs 外の TODO の 2 例も）
  一致。読まれる例は `fd36df8に注釈付きタグを付けました` のように英数字と日本語のスペースが詰まるのみ（対象外）。
- 「、」を含む文は残る: `2 つに分けたため、コミットは 1acb1bf です。`
- 食い違いなし。

## 4. TODO.md の「消さない」4 例
- `` `fd36df8` に注釈付きタグ `v0.1.0` を付けました `` -> `fd36df8に注釈付きタグ v0.1.0を付けました`
- `` `origin/master` は `7a526e0`（TODO-006 のコミット）を指していて `` -> ID 残る
- `` `a1a9b44` より前の 5 件 `` -> `a1a9b44より前の 5件`
- `` `88ef11d` の記録どおり `` -> `88ef11d の記録どおり`
4 例とも ID は読まれるまま。

## 変更ファイル（git status）
M TODO.md / M docs/UsersGuide.md / M src/ccspk/hook.py /
?? archives/agents/TODO-033/reviewer-report.md / ?? archives/agents/TODO-033/mutate.py（今回追加）。
指示の範囲内。TODO.md、docs、hook.py の diff 内容の良し悪しは見ていない。

## 判断できなかったこと
なし。境界線上（reviewer 報告 4）は見ていない。
