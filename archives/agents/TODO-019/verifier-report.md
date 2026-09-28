# verifier-report TODO-019

- 変更ファイル: docs/UsersGuide.md, src/claudecodespeak/user_dict.py（ほか TODO.md, archives/agents/TODO-019/）。指示の範囲と一致
- 1. `dict list` 終了 0。33 行すべて 5 列（ID・表記・読み・accent_type・優先度）。優先度 7 は「節」「語」「sh」の 3 行、他 30 行は 5
- 突き合わせ: `voicevox/user_dict.json` は 30 件。json にある 30 件は priority が全件一致（不一致 0）
- 食い違い（実害は未確認）: エンジンの辞書には json に無い 3 件（bash, sh, zsh）がある。`sh` が 7 なのはエンジン側の値で、json では確かめられていない。依頼の「節」「語」だけが 7 という前提とも違う。`dict export` の未実施の可能性（境界線上の判断は報告のみ）
- 2. `uv run claudecodespeak test` 終了 0（ok ok）
- 3. UsersGuide.md（「ID・表記・読み・`accent_type`・優先度」）と docstring は実際の列の並びと一致
- 確かめなかったこと: 変更前に戻してのテスト確認（demo() に list の assert は無く、対象外の変更）
