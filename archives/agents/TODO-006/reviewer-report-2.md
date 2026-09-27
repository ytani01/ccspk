# TODO-006 reviewer 報告（2 回目）

対象: 前回からの変更だけ（`hooks/speak-response.py` の PipeWire の分岐・コメント・
`BASE`、README から `docs/UsersGuide.md` への移動）。実測は 2026-09-28、
libpipewire 1.6.9。

要修正: 0 件 / 検討: 2 件 / 好みの範囲: 0 件

## 検討

### 1. hooks/speak-response.py:58-59 と docs/UsersGuide.md:74-76 `PIPEWIRE_REMOTE` があると PipeWire を確かめないことが文書に無い

- 分岐自体は意図どおり（実測、`unusable()` の戻り値）:

  | 環境変数 | 結果 |
  |---|---|
  | なし | None |
  | `PIPEWIRE_REMOTE='[pipewire-0-manager,pipewire-0]'` | None（前回の誤判定は消えた） |
  | `PIPEWIRE_REMOTE=`（空） | 確かめる側へ進み None（libpipewire も空は既定扱いなので合う） |
  | `PIPEWIRE_REMOTE=/nonexistent/sock` | None。`pw-cli` は `failed to connect` |
  | `PIPEWIRE_RUNTIME_DIR=/nonexistent` | 使えないと判定 |
  | `XDG_RUNTIME_DIR` なし | 使えないと判定、`/tmp/claude-tts-649.unusable` |

- 4 行目のとおり、`PIPEWIRE_REMOTE` が指す先に PipeWire が無くても「使える」と
  判定し、Stop のたびに子プロセスを起こす。前回は絶対パスなら正しく確かめて
  いたので、そこは確かめなくなった（意味が変わった所はここだけ）。
  UsersGuide の「使えないと覚えたとき」と README:38 は 3 条件を無条件に書いており、
  この例外に触れていない。書くか、例外として受け入れるかの判断。実害は未確認。

### 2. docs/UsersGuide.md:5-6 「フックと unit ファイルはこのパスを前提にしている」

- `systemd/voicevox-engine.service` が参照するのは
  `%h/.local/share/voicevox-engine/0.25.2` だけで、リポジトリのパスは出てこない
  （読んで確かめた）。パスを前提にしているのは、フックの `command` と、
  手順の `systemctl --user link ~/work/claudecodespeak/...`、自己テストと辞書の
  `curl -d @$HOME/work/claudecodespeak/...`。「unit ファイル」は「手順」の
  誤りに見える。

## 食い違い無し（1 行ずつ）

- `BASE`: `PIDFILE` / `UNUSABLE` は、`XDG_RUNTIME_DIR` ありで
  `/run/user/649/claude-tts.{pid,unusable}`、なしで `/tmp/claude-tts-649.{pid,unusable}`。
  前と同じ値（実測）。`--test` は ok。
- `sock = Path(..., "pipewire-0")` は、`PIPEWIRE_REMOTE` が無いときの前の値と同じ。
- コメント 49 行目は「1 ms かからない」だけになった。実測（0.2〜0.8 ms）と合う。
- 移す元（`git show HEAD:README.md` の「入れ方」「Claude Code につなぐ」）のコマンド
  と JSON は、UsersGuide にそのまま移っている（差分で 1 行ずつ照合）。
- 落ちたのは、読み間違える語の例（`TODO`、`README` など）と「辞書の元は
  `voicevox/user_dict.json`」の文。後者は UsersGuide の「読み上げの辞書」冒頭に
  あり、README:26-27 からもリンクがあるので情報は失われていない。
- 「`env` の行を消せば止まる」は UsersGuide の「止める」へ移った。
  「フックの登録は残してよい（何もせずに終わる）」は `main()` の 1 つ目の
  `return` と合う。
- git の remote は `git@github.com:ytani01/claudecodespeak.git` で、clone のコマンドと合う。
- リンク: README の `#入れ方`・`#使えないと覚えたとき`・`#読み上げの辞書`、UsersGuide の
  `#戻す` は、どれも UsersGuide に同じ名前の見出しが 1 つだけある。
- 「セッションが全部終わると消える（linger なら再起動まで）」は前回の指摘 3 どおり。

## 作り込みすぎ

なし。
