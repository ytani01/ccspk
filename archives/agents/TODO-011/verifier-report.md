# TODO-011 verifier 報告

## 準備

- `uv tool install --reinstall ~/work/claudecodespeak` 成功（claudecodespeak 0.1.dev19+gd6c01f11e.d20260928）
- `uv sync` 成功

## 1. UsersGuide.md

- `claudecodespeak hook --test` → `ok`、終了コード 0。一致
- フックの `command` 文字列
  `! command -v claudecodespeak >/dev/null || claudecodespeak hook`
  を `sh -c` で実行:
  - (a) `PATH=/usr/bin:/bin`（claudecodespeak を含めない）→ 出力なし、終了コード 0。一致
  - (b) `PATH=$HOME/.local/bin:/usr/bin:/bin`（claudecodespeak を含む）、`CLAUDE_TTS_SPEAK` 無し、
    JSON を標準入力に渡す → 出力なし、終了コード 0。一致
- `claudecodespeak add-word --test` → `ok`、終了コード 0。一致

## 2. Developer.md「テストと動作の確かめ方」

上から順に実行。本物の `$XDG_RUNTIME_DIR` を使う手順は無く、書いてあるとおり一時ディレクトリを使った。

- 自己テスト: `uv run claudecodespeak hook --test` → `ok`、`uv run claudecodespeak add-word --test` → `ok`。一致
- 「Stop を手で再現する」: 一時ディレクトリ + `PIPEWIRE_RUNTIME_DIR` に本物を指定して実行。
  `$tmp/claude-tts.pid`・`$tmp/claude-tts.last`・`$tmp/claude-tts.lock` ができ、
  `claude-tts.last` の中身は渡した文そのまま。書いてあるとおり。再生完了後
  `pw-play`・`claudecodespeak.hook` の子プロセスが残っていないことも確認した
- MessageDisplay の例（`message_id`・`index`・`final:true`・`delta` を渡す）:
  同じ 3 ファイルに加えて `$tmp/claude-tts.parts/`（中身は空。読み終えた分をその場で
  消すため）ができた。書いてあるとおり
- 「5 秒のうちに同じ文章」の確認（Developer.md 本文の主張。手順には明示のコマンドは無いが、
  実際に確かめた）: 同じ文を続けて渡すと `claude-tts.pid` の PID が変わらないことを確認
  （57707 → 57707）。一致
- `pw-play` が無いときの再現: `PATH=/nonexistent` で実行 → 終了コード 0、
  `$tmp/claude-tts.unusable` の中身は `pw-play が無い`。一致
- `--play` の直接呼び出し: `.venv/bin/claudecodespeak hook --play '合成と再生だけを試す。'`
  → 終了コード 0、エラー無し。実際に音が鳴ったかどうかは目視・耳では確認していない
  （**実害は未確認**。プロセスが正常終了しコンソール出力も無いことしか確認できていない）
- 「最初の音までの時間」: 文書のスクリプトをそのまま 3 回実行。結果は
  0.77 秒 / 0.81 秒 / 0.77 秒（コード自体は書いてあるとおり動き、エラー無く終了コード 0）。
  **食い違い**: Developer.md の「動き方」の目安には「最初の音までは、エンジンが空いていれば
  1.2〜2.5 秒ほど」とあるが、実測はいずれもそれより速い 0.77〜0.81 秒だった。
  このマシン・このタイミングでの実測であり、手順や実装の不具合ではなく、
  文書に書かれた目安の数値と実測が合っていないという点だけを報告する
  （どちらを直すべきかの判断はしていない）

## 3. README.md のファイルの表

`git ls-files` で該当する全 8 パス（pyproject.toml、src/claudecodespeak/{hook,add_word,cli}.py、
systemd/voicevox-engine.service、voicevox/user_dict.json、docs/{UsersGuide,Developer}.md）の
実在を確認。全て一致

## 変更されたファイルと指示の範囲

`git status` / `git diff --stat`:

- 変更: README.md、TODO.md、docs/Developer.md、docs/UsersGuide.md、
  src/claudecodespeak/hook.py、voicevox/user_dict.json
- 追加: pyproject.toml、src/claudecodespeak/{__init__,cli,click_utils,mylog}.py、uv.lock
- 移動（rename 検出）: voicevox/add-word.py → src/claudecodespeak/add_word.py、
  hooks/speak-response.py → src/claudecodespeak/hook.py

TODO-011 の項目（pyproject.toml・構成・UsersGuide/README/Developer の書き換え・
click_utils.py/mylog.py の導入）と範囲が一致している。TODO-011 の見込みに無い
ファイルの変更は無かった

## 確かめられなかったこと・判断できないこと

- `--play` と `demo()` 系での実際の音声出力（音が正しく鳴ったか）は、
  終了コードとファイルの有無でしか確認していない。耳で聞く確認はしていない
- 「最初の音までの時間」の目安（1.2〜2.5 秒）と実測（0.77〜0.81 秒）の食い違いについて、
  文書の目安を直すべきか、たまたま条件が良かっただけかは判断していない（判断が要る点）
- Developer.md 本文の「読んでから 5 秒のうちに同じ文章が来たら読まない」という記述は
  手順のコードブロックには明示のコマンドが無かったため、こちらで追加のコマンドを組んで
  確かめた（範囲外の追加確認だが、依頼文の「ほかにあれば全部」に沿って実施）
