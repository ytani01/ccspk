# TODO-020 verifier 報告

条件: XDG_CONFIG_HOME / XDG_RUNTIME_DIR は scratchpad の一時ディレクトリ。実行は `.venv/bin/ccspk`。
エンジン（0.25.2、systemd の voicevox-engine）は起動済みで、実行中のものを使った（エンジンは 1 つのため、
エンジン側の辞書には一時的に ZZTEST・ZZTWO が入ったが、remove 済み）。
`dict list` の列は「ID / 表記 / 読み / accent_type / 優先度」。最後の数字が優先度。

1. `ccspk test` → ok、ok（終了コード 0）。一致
2. `dict add ZZTEST ゼットゼットテスト` → `0d028561-...  ZZTEST  ゼットゼットテスト  7  7`。一致（優先度 7）
3. `--priority 3` で add し直す → `...  ZZTEST  ゼットゼットテスト  7  3`。一致。
   続けて `--priority` なしで add し直す → `...  ZZTEST  ゼットゼットテスト  7  3`。一致（3 のまま）
4. `dict add ZZTWO ゼットゼットツー --priority 0` → `4b8be52a-...  ZZTWO  ゼットゼットツー  7  0`。一致（0 が 7 に化けない）
5. `dict add --help` の --priority:「省くと、新しい単語は 7（エンジンの既定 5 より上）、登録済みの単語は今の優先度のまま」。
   UsersGuide.md「単語を登録する」の箇条も同内容（新しい単語は 7、登録済みは今のまま）。上の実測と食い違いなし。
   ただし UsersGuide の「多くはエンジン標準の読みより優先される」等の効果の記述は今回測っていない（TODO.md に 2026-09-29 の確認あり）。

後始末: ZZTEST・ZZTWO を remove、`dict list` に ZZT の行なし。一時ディレクトリ削除済み。

変更ファイル（git status。指示の範囲）: `src/ccspk/user_dict.py`、`docs/UsersGuide.md`、`TODO.md`。
`archives/agents/TODO-020/` は未追跡（本報告）。指示外のファイルの変更なし（`git diff` の src・docs で確認）。

判断できなかったこと・気づき（実害は未確認）:
- 項目 4 の「ZZTWO」の読みが「ズィ'イズィイティイダブリュウオオ」と出たが、これは add 直後の読み確認（`query`）の表示で、
  表記 ZZTWO を英字として読んだもの。今回の優先度の測定とは無関係と思われる（推定）。
