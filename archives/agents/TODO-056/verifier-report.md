# TODO-056 verifier-report

結論: 全項目が指示どおり。食い違いなし。

1. `uv run ccspk test` → 終了コード 0（ok が 3 行）
2. 壊すと落ちるか（各 1 回。実ファイルを壊し、`\cp` で元に戻した）
   - a. `{pid}` → `{cid}`（sed で全置換）: `hook.py` line 655 の assert で AssertionError（`済み（fd93278）で…` の例）
   - b. 後読み `(?<![0-9A-Za-z_.]\()` を消す: line 659 の assert で AssertionError（`f(abc1234) と range(1000000)` の例）。消えたことは diff で確認
   - c. `pid` の囲まない側の `(?:\.\.[0-9a-f]{7})?` だけ消す: line 658 の assert で AssertionError（`（fd93278..2cdfe32）` の例）
   - 終了コードは、シェルの PIPESTATUS の取り方が zsh で空になり記録できなかった。AssertionError の traceback は出ている
3. UsersGuide.md 219 行と `to_speech` の結果（`.venv/bin/python` で 1 回）
   - `（fd93278）` → `''`（消える）: 合う
   - `f(abc1234)` → `f(abc1234)`（残る）: 合う
   - `v1.3.0(fd93278)` → `vイチテンサンテンゼロ(fd93278)`（残る）: 直前が `0`（英数字）なので条件どおり。合う

変更ファイル: 試す前後の `git diff` 全体を `cmp` で比べ、同一。
指示の範囲: `git status` の変更は TODO.md・docs/Developer.md・docs/UsersGuide.md・src/ccspk/hook.py と archives/agents/TODO-056/。この項目の対象外の変更は見つからなかった（TODO.md と docs 2 件の中身は見ていない）。

確かめられなかったこと: 上記の終了コードのみ。判断が要る点はなし。
