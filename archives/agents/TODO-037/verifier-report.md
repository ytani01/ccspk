# TODO-037 確認報告（verifier）

スクリプト: `archives/agents/TODO-037/verify.sh`（引数なし = 1〜8、`9` = 本物の claude）。
環境: `XDG_*` は `/tmp/ccspk-verify.*` の一時ディレクトリ。偽の `pw-play`・`claude` を PATH の先頭に置いた。
偽の `pw-play` のため PipeWire 接続の確認が落ちて何も鳴らなかったので、`PIPEWIRE_REMOTE=fake` を環境に足して確認を飛ばした（コードは変えていない）。
偽の `claude` のログを 80 字で切っているため、呼び出し回数は `--model sonnet` の行数。コードは直していない。

| # | 結果 | 測った値 |
|---|------|----------|
| 1 | 一致 | `uv run ccspk test` 終了コード 0 |
| 2 | 一致 | cmdline は `python -P -m ccspk.hook --play <本文>` で `--summarize` 無し。sonnet 0 回。spoken.txt 最後の行 180 字（先頭「ここまで進めました。…」を切った文） |
| 3 | 一致 | cmdline に `--summarize` あり。sonnet 1 回。子の終了まで 3 秒。最後の行 20 字「要約です。TODOナナの件は済みました。」 |
| 4 | 一致 | MessageDisplay → 0.5 秒後 Stop で sonnet 合わせて 1 回（Stop 側は同じ文として読まれず終わった。実害は未確認だが、この 1 回は重複抑止（SAME_WITHIN）による可能性が高い） |
| 5 | 一致 | 短い返答: sonnet 0 回 |
| 6 | 一致 | `CCSPK_SUMMARY=0` で sonnet 0 回。`CCSPK_SUMMARY=0 ccspk summary` は 2 行（`off` と「環境変数 CCSPK_SUMMARY=0 が <path>/summary より優先している」）、終了コード 0 |
| 7 | 一致 | 2 秒後の子は pgid 311799 に 3 プロセス（python・claude・sleep 20）。`ccspk stop` は「止めた」。その後 `ps -g` は空。spoken.txt は 0 行 |
| 8 | 一致 | 引数なし `off`(0)、`on` `on`(0)、`off` `off`(0)、`bad` は Usage と `Invalid value ... 'bad' is not one of 'on', 'off'.` で終了コード 2。文書の例 2 つは表示が一致（パスだけ環境の一時ディレクトリ。文書は `/home/user/...` の例示） |
| 9 | 一致 | 本物の claude 1 回。子の終了まで 18 秒（Stop から 19 秒）。XDG_STATE_HOME は一時ディレクトリだったことを確認済み。最後の行 206 字で要約になっている（「sunshine を user unit として有効にし、…次に verifier が確かめます。」）。終了後 `pgrep -af 'claude -p'` は自分の zsh 以外に無し（要約の claude は残っていない） |

## 気づいたこと（判断はしない）

- 9 の要約は 206 字で、プロンプトの「180 字以内」を超えた。`summarize()` が `to_speech()`（`clip`）を通すので、文末まで延ばす設計の範囲かもしれない。実害は未確認
- 9 の 18 秒は要約の待ちに加え、VOICEVOX での合成・再生分を含む（内訳は測っていない）。文書の「最初の音が 5〜6 秒遅れる」との比較はできていない

## 変更ファイル（git status）

CLAUDE.md, README.md, TODO.md, docs/Developer.md, docs/UsersGuide.md, src/ccspk/cli.py, src/ccspk/hook.py（変更）、archives/agents/TODO-037/（未追跡）。
指示の範囲かは TODO.md の内容を突き合わせていない（実装が hook.py・cli.py に収まっていることだけ確認）。

## 確かめなかったこと

- 1 の出力の中身（終了コードのみ記録）
- 追加した demo() のテストが壊すと落ちるか（依頼に無い）
