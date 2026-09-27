# TODO-008 reviewer 報告

対象: `git diff`（.gitignore, README.md, TODO.md, settings.json）と未追跡の
hooks/speak-response.py, hooks/vv-shim/pkg_resources.py, systemd/voicevox-engine.service。
実測は Claude Code 2.1.283、/bin/sh = bash の環境で行った（2026-09-28）。

要修正: 0 件 / 検討: 6 件 / 好みの範囲: 2 件

## 検討

### 1. hooks/speak-response.py:25-43, 122-125 — 会話ログを読まずに `last_assistant_message` が使える
- 内容: Stop hook の入力に `last_assistant_message` がある。2.1.283 の本体に
  スキーマ `hook_event_name:"Stop", stop_hook_active, last_assistant_message: string (optional)`、
  説明文 "Text content of the last assistant message before stopping. Avoids the need to
  read and parse the transcript file." があることを確かめた（`rg -a` で本体から抜き出した）。
- 実害: 今の `last_text` には次の弱点がある。どれも実害は未確認。
  - 最後の API 応答に text ブロックが無い終わり方をすると、同じターンの途中の
    text（「ファイルを読みます。」の類い）か、前のターンの返答を読み直す。
    会話ログのレコードの区切り方と、ターンの終わり方次第で決まる。
  - 手元の会話ログではレコードが content ブロック 1 つずつ（thinking / text / tool_use が
    別々のレコード、同じ message.id が複数レコード）になっていた。1 つの応答に text が
    2 つあると最後の 1 つしか読まず、L41 の `"\n".join` は実質使われない。
  - Stop の時点で最後の返答が会話ログに書き終わっているかは未確認（古い版では
    書き込み前に Stop が来る報告があった記憶があるが、未確認）。
- `last_assistant_message` の中身がどう作られるか（tool_use だけで終わったとき空になるか）は
  本体を読み切れず未確認。
- TODO.md のチェック項目は「`transcript_path` の会話ログから取り出す」と書いてあるので、
  替えるなら項目の文言も変わる。判断は管理者。
- 性能は問題なし: 手元で最大の会話ログ（7.0 MB）で `last_text` は 0.039 秒。

### 2. hooks/speak-response.py:57 — `_` を消すと識別子がつながる
- 内容: `[`*_~>]` を空文字に置き換えるので、`CLAUDE_TTS_SPEAK` → `CLAUDETTSSPEAK`、
  `snake_case` → `snakecase`（実測）。`->` は `-`、`2 * 3` は `2 3`、`a > b` は `a b` になる。
- 実害: 読み上げが聞き取りにくくなる程度。空白に置き換えれば語の切れ目は残る。
  この返答は識別子を多く含むので頻度は高いと思う（実害は未確認）。

### 3. hooks/speak-response.py:49 — 閉じていないコードブロック、`~~~` の囲み
- 内容: 閉じの ``` が無いと L49 にかからず、L57 でバッククォートだけ消えて中身を読む
  （`説明\n```python\nsecret_code()` → `説明 python secretcode() more`、実測）。
  `~~~` で囲んだブロックも中身を読む（`code here 後`）。本文中に ``` が単独で出ると
  組み合わせがずれる（`区切りは ``` で書く。次に ```py\nx\n```` → `区切りは コード省略。 py x 終わり`）。
- 実害: 返答が 180 文字で切れるので、先頭付近にある場合だけ。頻度は低いと思う（未確認）。

### 4. hooks/speak-response.py:22, 62-70 — 古い PID ファイルと PID の再利用
- 内容: 再生が終わっても PID ファイルは残り、次の Stop で `os.killpg(古い PID)` を送る。
  その番号がその間に別のプロセスグループの ID として使われていると、無関係なグループに
  SIGTERM が届く。`pid_max` は 4194304（実測）なので、数分おきの Stop の間に一周する
  見込みは小さい。
- 併せて、Claude Code を複数並べているとき、2 つの Stop がほぼ同時に来ると両方が同じ古い PID を
  読んで 2 つ鳴らし、PID ファイルには片方しか残らない（非原子的な読み書き。実害は未確認）。
- `/tmp` の固定名なので、他のローカル利用者が同名のファイルを先に置けば、kill する相手を
  指定できる（`$XDG_RUNTIME_DIR` なら避けられる）。個人の PC なので実害は小さい。
- 実害: いずれも未確認。重さは低め。

### 5. settings.json:10 — `CLAUDE_TTS_SPEAK=1` がすべての起動に効く
- 内容: `env` に置いたので、利用者設定を読むすべての Claude Code の起動（対話・`claude -p`
  の非対話実行・利用者設定を読む SDK 経由の起動）で Stop hook が鳴る。非対話の実行が
  終わるたびに読み上げが入り、対話セッションの再生も止める。
- 別のセッションの Stop でも前の再生を止める。「前を止めて新しいほうを読む」の範囲が
  セッションをまたぐかは TODO.md に書かれていない（境界線上の判断、報告だけ）。
- 実害: 利用者が `claude -p` を定期的に回しているかによる。未確認。

### 6. hooks/speak-response.py:95-109 — `last_text` にテストが無い
- 内容: `--test` は `to_speech` だけを見る。`last_text` の分岐（isSidechain の除外、
  text の無いレコードを飛ばす、JSON でない行）は確かめていない。
- 1. で `last_assistant_message` に替えるなら要らない。

## 好みの範囲

### 7. hooks/vv-shim/ の置き場所
- hook ではないものが `hooks/` の下にある。unit ファイルの隣（`systemd/` の下など）の
  ほうが「エンジン用」と分かる。README に説明があるので実害は無い。

### 8. hooks/speak-response.py:56 — 行頭の `2026. ` も番号付きリストとして消える
- `2026. 年` → `年`（実測）。日本語の文ではまず出ない。

## 問題なしの観点

- killpg で子まで止まるか: `start_new_session=True` で sh がグループの長になり、curl・pw-play は
  同じグループに入る。問題なし。
- kill されたときの一時ファイル: /bin/sh が bash なので、SIGTERM でも EXIT の trap が走って
  wav は消える（合成中・再生中の両方で実測）。SIGKILL では残る（実測）が、送るのは SIGTERM だけ。
  /bin/sh が dash の環境では trap EXIT がシグナルで走らないので残る（この PC では該当しない）。
- シェルへの引数: URL は `urllib.parse.quote`（`&` `#` `?` も符号化）と `shlex.quote` の二重で、
  本文がシェルに解釈される経路は無い。
- hook の 5 秒: `Popen` はすぐ戻り、子の stdin/stdout/stderr は DEVNULL なので Claude Code が
  パイプの終わりを待つことも無い。Python の起動は約 0.01 秒。
- 例外: 捕まえていない例外（不正な UTF-8、content が文字列など）は終了コード 1 になる。
  Stop hook で止める動作になるのは終了コード 2 だけなので、Claude Code の動作は妨げない。
  標準出力にも何も出さない。
- isSidechain: 今の版ではサブエージェントの会話ログは別ファイルなので効く場面はほぼ無いが、
  1 行なので残してよい。
- 行頭の `>`、表の行、見出し、リスト記号、リンク、裸の URL、`~~`、`__`: 意図どおり消える（実測）。
  行頭が `|` の普通の文も消えるが、表と区別できないので仕様の範囲。
- systemd unit: パッケージに実行用のラッパーは無く（`pacman -Ql` で `/usr/lib/VOICEVOX/vv-engine/run`
  のみ）、`python run` で正しい。`%h` も unit の指定子として有効。`127.0.0.1` 限定で外に開かない。
- README の手順: `uvicorn` は extra に実在（0.52.4-1 を確認）、`pw-play` は pipewire-audio が持つ。
  unit のパスと `PYTHONPATH` の説明は unit ファイルと一致。
- .gitignore: `hooks/*` の後で `!hooks/vv-shim/` → `hooks/vv-shim/*` → `!…/pkg_resources.py` の順で、
  `__pycache__` は拾わない。`systemd/` も同じ形。既存の書き方に沿っている。
- コメント: 「なぜ」を書いている（LIMIT の理由、シムの理由）。
- 範囲: TODO-008 に関係ない変更は無い。

## 作り込みすぎ

- hooks/speak-response.py:L25-43, L122-125: native: `last_text` と会話ログのパス確認。
  `payload.get("last_assistant_message") or ""`、1 行（1. と同じ。判断は管理者）。
- hooks/vv-shim/pkg_resources.py:L10-17: shrink: `project_name` は使われない（pyworld 0.3.5 の
  `__init__.py:15` が読むのは `.version` だけ、実測）。
  `get_distribution = lambda name: SimpleNamespace(version=version(name))`、1 行。

net: -22 lines possible.
