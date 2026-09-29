# TODO-051 verifier 報告

- 1. `uv run ccspk test`: ok が 3 回、終了コード 0
- 2. to_speech の実測（すべて指示どおり）
  - `v1.7.0 を出した` -> `vイチテンナナテンゼロを出した`
  - `v2` -> `vニー` / `v1.25` -> `vイチテンニーゴー` / `` `v0.1.0` `` -> `vゼロテンイチテンゼロ`
  - `v1.2.3b` `v1.2-rc1` `xv1.2` `V1.2` -> 変わらない
  - `v1~2` -> `vイチから2` / `v1.6.0..v1.7.0` -> `vイチテンロクテンゼロ..vイチテンナナテンゼロ`（両方置換）
- 3. extract("v1.7.0 v2 v1.2.3b README.md") -> キーは `v1.2.3b` と `README.md` のみ。v1.7.0・v2 は出ない
- 4. 新旧比較（HEAD を git archive で一時ディレクトリへ）: 同じ出力
  `TODOゼロニーゼロからゼロニーニー、1から2、3 files、2026年9月29日、1.5倍、PR-12`
- 5. UsersGuide 2.2 の例 `v1.7.0` -> `vイチテンナナテンゼロ` は手順 2 の実測と一致
- 変更ファイル: TODO.md, docs/Developer.md, docs/UsersGuide.md, src/ccspk/check.py, src/ccspk/hook.py（未追跡は archives/agents/TODO-051/ のみ）。
  指示の範囲との照合は、範囲の記述を読んでいないため判断できない
- 未確認: エンジンでの発音、フックの実運用
