# verifier 報告 TODO-040

1. `uv run ccspk test`: 通る (ok x3, exit=0)
2. 壊すと落ちる: replace 行を sed で消して実行 -> exit=1
   `hook.py line 464, in demo: assert to_speech("a\0b\n\0c") == "ab。 c" ... AssertionError`
   戻した後 `git diff --stat src/` は 3 insertions、`replace("\0"` の行は 118 行にある。戻し済み。
3. 直す前: `Popen(["true","a\0b"])` -> `ValueError: embedded null byte`
4. 直した後 (XDG_* は一時ディレクトリ、CCSPK_SUMMARY=0): prepare("前\0置き\n\0続き") = ('前置き。 続き', False)、NUL 無し。
   child_args を入れた Popen(...).wait() = 0、ValueError 無し。speak()/main() は呼んでいない。
- 変更ファイル: src/ccspk/hook.py (+3)、TODO.md (管理者の更新)。未追跡は archives/agents/TODO-040/。指示の範囲内。
- 確かめられなかったこと: なし。
