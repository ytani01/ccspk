# TODO-006 verifier report

対象: hooks/speak-response.py（未コミット差分）、README.md、docs/UsersGuide.md、TODO.md。
コードは直していない。原因の切り分け・境界線上の判断はしていない（該当する食い違いも無かった）。

## 実測結果（ケース 1〜10）

すべて `/tmp/tts006-*` の一時ディレクトリ、または `/tmp/claude-tts-649.*`
（case 5〜7、終了後に削除済み）で実施。本物の `/run/user/649/claude-tts.unusable` は
作らず、作業終了時に一時ファイルはすべて削除済み（`command ls` で残存なしを確認）。
エンジンの systemd サービスは操作していない（起動したまま、ポート変更はコピーした
スクリプトで実施）。

- **ケース 1（使える）**: `XDG_RUNTIME_DIR` を一時ディレクトリにし、`pipewire-0` を
  本物へのシンボリックリンクにして実行。`claude-tts.unusable` は作られず、
  `claude-tts.pid` が作られた（pid 73737）。`pgrep -af` で直後に該当プロセスが
  存在し、3 秒後には終了していた（再生完了）。仕様どおり
- **ケース 2（pw-play が無い）**: `PATH=/nonexistent` で実行。
  `claude-tts.unusable` の中身は `pw-play が無い`。pidfile は作られず。仕様どおり
- **ケース 3（エンジン未接続）**: `hooks/speak-response.py` を一時ディレクトリへ
  コピーし、`ENGINE` を `sed` で `127.0.0.1:50099` に書き換えたもので実行
  （本物のサービスは触っていない）。中身は
  `エンジン（127.0.0.1:50099）に接続できない: [Errno 111] Connection refused`。
  pidfile は作られず。仕様どおり
- **ケース 4（PipeWire が無い）**: 空の一時 `XDG_RUNTIME_DIR` で実行。中身は
  `PipeWire（<tmpdir>/pipewire-0）に接続できない: [Errno 2] No such file or directory`。
  pidfile は作られず。仕様どおり
- **ケース 5（`XDG_RUNTIME_DIR` を unset）**: `env -u XDG_RUNTIME_DIR PATH=/nonexistent`
  で実行。`/tmp/claude-tts-649.unusable` が作られ、中身は `pw-play が無い`。
  終了時に該当ファイルは削除済み。仕様どおり
- **ケース 6（ファイルがあるときは即終わる）**: ケース 5 の直後、`XDG_RUNTIME_DIR`
  unset のまま（`PATH` は通常に戻して）再実行。所要時間は
  `elapsed: .041194179` 秒。ファイルの中身は書き換わっていなかった
  （`pw-play が無い` のままではなく、実行時の理由〈PipeWire 未接続〉になる点は後述）。
  pidfile は作られず。**注記**: この 2 回目の実行は `PATH` を戻したため
  `pw-play` は見つかる状態になっており、`unusable()` を呼べば別の理由
  （PipeWire 未接続）になるはずだが、`UNUSABLE.exists()` の分岐が先に来て
  `unusable()` 自体を呼ばずに即 return するため、**ファイルの中身は最初に
  書いた「pw-play が無い」のまま変わらなかった**。これは「ファイルがあるあいだは
  確かめもせずに終わる」という仕様どおりの挙動
- **ケース 7（ファイルを消して使える環境で再実行）**: ケース 6 のファイルを消し、
  `PIPEWIRE_RUNTIME_DIR=/run/user/649`（`XDG_RUNTIME_DIR` は unset のまま）を
  付けて再実行。`claude-tts.unusable` は作られず、`claude-tts.pid` が作られた。
  `pgrep` で該当プロセスを確認後、後始末で pidfile を削除。仕様どおり
- **ケース 8（`PIPEWIRE_REMOTE` 付き、PipeWire 無し環境）**: ケース 4 と同じ空の
  `XDG_RUNTIME_DIR` に `PIPEWIRE_REMOTE=anything` を追加。`claude-tts.unusable` は
  作られず、pidfile が作られた（子プロセスが起きた）。仕様どおり
- **ケース 9（`CLAUDE_TTS_SPEAK` 無し）**: `env -u CLAUDE_TTS_SPEAK` で実行。
  終了コード 0、何も出力せず、ファイルも作られなかった。仕様どおり
- **ケース 10（`--test`）**: `python3 hooks/speak-response.py --test` → `ok`。
  終了コード 0。仕様どおり

## UsersGuide.md「入れ方」節の再現

- エンジンのダウンロード・展開・`systemctl link/enable` は実行していない（指示どおり）
- パスの整合: `~/.local/share/voicevox-engine/0.25.2/run` は実在し実行権限あり。
  `~/.config/systemd/user/voicevox-engine.service` はリポジトリ内の
  `systemd/voicevox-engine.service` への symlink になっており、パスは一致
- `curl -s --max-time 5 http://127.0.0.1:50021/version` → `"0.25.2"`（一致）
- `git ls-remote git@github.com:ytani01/claudecodespeak.git`（20 秒 timeout）→
  `HEAD` と `refs/heads/master` が返り、正常に引けた
- フックの設定文字列: `~/.claude/settings.json` の `command` は UsersGuide の
  コードブロックと文字どおり一致（`f="$HOME/work/claudecodespeak/hooks/speak-response.py"; [ ! -f "$f" ] || python3 "$f"`）。
  この文字列をそのまま `sh -c` に渡し、`XDG_RUNTIME_DIR` を一時ディレクトリ
  （本物の pipewire-0 へのシンボリックリンク付き）にして実行 → 終了コード 0、
  `claude-tts.unusable` は作られず、`claude-tts.pid` が作られた（動いた）
- 「使えないと覚えたとき」の `cat` と `rm` のコマンド: 一時 `XDG_RUNTIME_DIR` で
  `pw-play` を無くして `unusable` ファイルを作らせたあと、ガイドどおりの
  `cat "$XDG_RUNTIME_DIR/claude-tts.unusable"` で中身（`pw-play が無い`）が
  読め、`rm "$XDG_RUNTIME_DIR/claude-tts.unusable"` で消えた（終了コード 0、
  消去後は存在しない）

## 見なかったもの（指示どおり）

- 整形・分割（`to_speech`、`clip`、`split_first`）
- 音質、辞書の手順（`docs/UsersGuide.md` の「読み上げの辞書」節、
  「戻す」リンク先の辞書インポート）

## 確かめられなかったこと・判断できないこと

- `docs/UsersGuide.md` の「入れ方」節にある
  「エンジンを入れたら、読み間違える語の辞書を読み込む（[戻す](#戻す) の手順）」
  というリンクは、辞書の手順に触れる内容なので、指示にある「辞書の手順は
  見なくてよい」に従いリンク先の内容や妥当性は確かめていない。
  リンクの整合性（アンカーが存在するか）自体は文書の書式に属する話であり、
  今回の実測対象（読み上げ機能の挙動）には入らないと判断したが、
  この判断自体が指示の範囲内かは管理者の判断を仰ぎたい
- `loginctl enable-linger` の有無による `$XDG_RUNTIME_DIR` ファイルの残存挙動
  （ガイドに書かれている内容）は、実際にログアウト・再起動を伴う検証はしていない
  （実行環境上できないため）。文面の記述自体は `speak-response.py` の
  ロジックとは無関係（OS 側の仕様の説明）なので、コードとの食い違いは無い
- 変更されたファイル（README.md, docs/UsersGuide.md, hooks/speak-response.py,
  TODO.md）は、いずれも TODO-006 の指示範囲（機能の実装・文書の分割・TODO の
  チェック）に収まっており、範囲外のファイルの変更は無かった
