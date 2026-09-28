# TODO-015 実装報告（implementer）

## 変更したファイル

- `src/claudecodespeak/add_word.py` → `git mv` で `src/claudecodespeak/user_dict.py` に改名。
  - ロガー名を `"add-word"` → `"dict"` に変更（`user_dict.py:24`）
  - `_test` コールバックと `--test` オプションを削除。`demo()` は残す
  - `main()`（旧 click コマンド）を `click.group("dict")`（`dict_group`、`user_dict.py:105-107`）と
    サブコマンド `add`（`user_dict.py:109-135`。旧 `main` そのまま、`--test` のみ外した）、
    `kana TEXT`（`user_dict.py:138-142`）、`list`（`user_dict.py:145-151`）、
    `remove SURFACE`（`user_dict.py:154-162`）、`export [FILE]`（`user_dict.py:165-171`）、
    `import [FILE]`（`user_dict.py:174-179`）に分割
  - エンジンとのやり取りの例外処理（`HTTPError`・`OSError`）を `_guarded` デコレータ
    （`user_dict.py:93-103`）にまとめ、全サブコマンドに適用（サブコマンドごとの写しは無し）
  - `export` は `json.dump(..., indent=2, sort_keys=True, ensure_ascii=False)` ＋ 末尾改行で、
    `voicevox/user_dict.json` とバイト単位で一致する出力にした（`cmp` で確認）
  - `import` は `click.File("rb")` で受け取り、`POST /import_user_dict?override=true` に送る
- `src/claudecodespeak/hook.py`
  - `main`（`hook.py:385-388` 付近）から `--test`・`--play` オプションを削除し、フック専用にした
  - `say TEXT` コマンドを追加（`play(text)` を呼ぶだけ）
  - `status [--clear]` コマンドを追加。`UNUSABLE` があれば中身とパスを表示し、`--clear` で消す。
    無ければ「止まっていない」。終了コードはどちらも 0
  - `PLAY`・`MODULE`・`speak()`・`stop_playing()`・末尾の `if __name__ == "__main__":` は
    指示どおり変更していない
- `src/claudecodespeak/cli.py`
  - `hook`・`say`・`status`・`dict`（`dict_group`）を登録
  - `test` サブコマンドを `cli.py` に定義し、`hook.demo()` と `user_dict.demo()` を順に呼ぶ
- 文書: `CLAUDE.md`、`README.md`、`docs/Developer.md`、`docs/UsersGuide.md` を、
  `rg -n -e 'add-word' -e 'add_word' -e '--play' -e '--test' -e 'curl' -e 'unusable' -e 'jq'`
  で拾った箇所に沿って書き換えた。辞書操作の `curl`/`jq` はサブコマンドに置き換え、
  `accent_type` の意味と英字の大小を別語として扱う話は `dict add` の説明に残した。
  `dict export`/`dict import` の例はリポジトリ直下で走らせる形にした。
  エンジンの起動確認（`curl …/version`）は指示どおり残した

## 検証

- `uv run claudecodespeak test` → `ok` を 2 行出力（成功）
- `uv run claudecodespeak --help` / `dict --help` / 各サブコマンドの `--help` → 全て正しく表示
- VOICEVOX エンジン（127.0.0.1:50021、本物）に対して実際に動かした:
  - `dict list`・`dict kana` → 正常表示
  - `dict export voicevox/user_dict.json` 相当の出力を `cmp` で `voicevox/user_dict.json` と比較 →
    一致（`MATCH`）
  - `dict add ZZTESTWORD テスト` → 登録 → `dict remove ZZTESTWORD` → 消去を確認
    （消し忘れに気づき、`dict export` との `cmp` で検出して除去。最終的に
    `voicevox/user_dict.json` と再び完全一致することを確認済み）
  - `dict remove NONEXISTENT_ZZ` → `登録されていない: …` で終了コード 1
  - `dict import voicevox/user_dict.json` → 読み込み成功（override=true）
  - `status`／`status --clear`（`XDG_RUNTIME_DIR` を一時ディレクトリに向けて）→
    「止まっていない」「理由の表示」「消した」を確認
  - `hook`（`XDG_RUNTIME_DIR` を一時ディレクトリ、`PIPEWIRE_RUNTIME_DIR` は本物）→
    `claude-tts.pid`・`.last`・`.lock` ができ、実際に音声が鳴った
  - `say '合成と再生の確認です。'` → 実際に音声が鳴った
- `rg` での旧い書き方の確認 → `archives/` の外に残っているのは、意図して残した箇所のみ
  （`unusable()` 関数名、`UNUSABLE`/`.unusable` ファイル名、`--play`/`PLAY` 定数、
  エンジンの起動確認の `curl …/version`）

## 判断・気づいたこと

- 作業直後に管理者から「`voicevox/user_dict.json` を 88ef11d で更新した」と連絡があったが、
  作業ツリーには既にそのコミットが反映されており、`dict export` との `cmp` はその内容で
  一致することを確認済み。このファイル自体は変更していない
- `TODO.md` に TODO-016 が新設されたのを確認したが、範囲外のため触れていない
- `TODO.md` のチェックボックスは、指示（管理者が入れる）どおり触っていない
