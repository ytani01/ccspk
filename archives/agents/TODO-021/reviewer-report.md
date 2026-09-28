# TODO-021 reviewer 報告

対象: `git diff HEAD`（ステージ済みの `voicevox/user_dict.json` の削除を含む）。
実測は 2026-09-29、このマシン（systemd 262、CachyOS）で行った。

## 要修正

### 1. `systemd/voicevox-engine.service:8-12` 起動の上限は 90 秒ではなく 15 秒。待ちが上限を超えるとエンジンごと止まる

- **何が問題か**: コメントは「起動の上限 TimeoutStartSec の 90 秒より短く」とし、
  `docs/UsersGuide.md:204-206` は「応答を 60 秒待っても読み込めないときは読み込まずに
  あきらめる（エンジンは止めない）」と書く。しかしこのマシンの user manager の既定は 15 秒で、
  unit は `TimeoutStartSec` を指定していない。
- **根拠（実測）**:
  - `systemctl --user show -p DefaultTimeoutStartUSec` → `15s`。出どころは
    `/usr/lib/systemd/user.conf.d/00-timeout.conf`（`DefaultTimeoutStartSec=15s`）。
    今読み込まれている unit も `TimeoutStartUSec=15s`
  - `Type=simple` なので、起動のジョブが終わるのは `ExecStartPost` が終わったとき。
    `ExecStartPost` はこの 15 秒の対象になる
  - 先頭の `-` は終了コードの失敗しか無視しない。タイムアウトでは main も止まる。
    一時的な unit で確かめた:
    `systemd-run --user -p TimeoutStartSec=3 -p Restart=no -p 'ExecStartPost=-/bin/sleep 10' /bin/sleep 100`
    → `start-post operation timed out. Terminating.`、`Result=timeout`、`MainPID=0`
    （本体の `sleep 100` も止められた）
  - 待ちのループは、ポートが閉じているとき 1 回あたり約 1.0 秒で 30 回、約 30 秒
    （ポートを 50999 に替え、回数を 3 にして 3.02 秒）。応答が返らずに止まるときは最長約 60 秒。
    どちらも 15 秒を超える
- **起きること**: エンジンが 15 秒以内に `/version` へ応答しないと、読み込みを諦めるより前に
  systemd がエンジンを止め、起動は失敗になる。`Restart=on-failure` で起動し直しを繰り返す
  可能性がある（繰り返すかどうかは未確認）。普段はエンジンの起動が約 1.2 秒
  （journal の `Started` → `Uvicorn running`）なので、この経路を通るのは遅いときだけ。
  **実害は未確認**（実機で遅い起動を再現していない）。
- 上限は環境の既定に依存するので、90 秒を前提にしたコメントと文書は、どちらにしても合っていない。

## 検討

### 2. `src/ccspk/user_dict.py:105-111`（`save`）一時ファイルが 0600 で作られ、置き換えた後の辞書のファイルも 0600 になる

- `tempfile.NamedTemporaryFile` は `mkstemp` と同じく 0600 で作る。`os.replace` でそのまま
  置き換わるので、利用者の umask（今のファイルは 0644）によらず 0600 になる。
- 実測: `XDG_CONFIG_HOME` を scratchpad に向け、`call` を差し替えて `save()` →
  `mode 0o600`。
- 読むのは本人と systemd の user unit だけなので、実害は無さそう（未確認）。
  `~/.config/ccspk` は `../dot.files/ccspk` へのシンボリックリンクで、dotfiles として
  扱われている。

### 3. `src/ccspk/user_dict.py:107-110`（`save`）書き出しの途中で落ちると `.tmp` が残り、名前が毎回違うので溜まる

- `delete=False` で、`dump` の中の `call` が `sys.exit` すると（エンジンが途中で落ちたなど）、
  `os.replace` に届かず一時ファイルが残る。前の `user_dict.json` は無事（置き換えの目的は満たす）。
- 実測: `call` を `SystemExit` を上げる関数に差し替えて `save()` →
  ディレクトリに `tmpvay83lz1.tmp` が残った。
- 頻度は低い。下の「作り込みすぎ」の書き換えで、名前が固定になり溜まらなくなる。

### 4. `src/ccspk/user_dict.py:156, 191` エンジンを変えた後に `save()` が失敗すると、エンジンとファイルが食い違う

- `add` / `remove` はエンジンを先に変え、その後で `save()` する。`save()` だけ失敗すると
  （`~/.config` に書けない、エンジンがその間に落ちた）、ファイルは古いまま。
  `remove` の場合、次にエンジンを起動したときの `dict import` で、消した単語が戻る。
- 書き込みの失敗は `call` のコメント（「export の書き込みの失敗などは、そのまま上げる」）どおり
  traceback で上がるので、気づかれないことは無い。頻度は低い。実害は未確認。

### 5. `docs/UsersGuide.md:204-205` 「応答を 60 秒待っても」は、ポートが閉じている場合は約 30 秒

- 1 の実測どおり、接続を断られるときは `curl` がすぐ返るので、ループ全体で約 30 秒。
  60 秒は応答が返らないときの上限。1 を直すときに一緒に合わせる話。

## 好みの範囲

（なし）

## 作り込みすぎ

- `user_dict.py:L105-111`: stdlib: `tempfile.NamedTemporaryFile(delete=False)` + `os.replace`。
  `tmp = DICT_FILE.with_suffix(".tmp")`、`with tmp.open("w", encoding="utf-8") as f: dump(f)`、
  `tmp.replace(DICT_FILE)` で足りる。`import tempfile` が消え、2（0600）と 3（溜まる）も
  解消する。同時に 2 つの `dict add` を走らせると同じ一時ファイルを取り合うが、手で打つ
  コマンドなので起きない前提でよい（重大度: 検討）
- `voicevox-engine.service:L10-12`: native: `for`/`seq`/`sleep` のループは
  `curl --retry 30 --retry-delay 1 --retry-connrefused` で 1 行になる。ただし `--max-time` と
  リトライの合計時間の関係は未確認で、1 を直すと待ち時間ごと変わるので、そのときに決める
  （重大度: 好みの範囲）

net: -3 lines possible.

## 問題なし（1 行ずつ）

- `save()` の時機: `add` は `--speak` の前（`query` より前）、`remove` / `import` は成功の後。
  `call` の失敗は `sys.exit` なので、失敗したときは書き出さない
- 置き換え: 一時ファイルを同じディレクトリに作ってから `os.replace` するので、ファイルシステムを
  またがず、書きかけのファイルが `user_dict.json` の名前で見えることは無い
- `DICT_FILE`: `XDG_CONFIG_HOME` が空文字のときも `~/.config` になる（実測）
- unit の `$$`・`%h`: `$$` を `$`、`%h` をホームに置き換えて取り出したスクリプトが `sh -n` を通る。
  `systemd-analyze --user verify` も警告なし。`HOME` は user manager の環境にある
- unit の `XDG_CONFIG_HOME`: user manager にもシェルにも無く、どちらも `~/.config` を見る（実測）
- ファイルが無いとき: `[ -f "$f" ] || exit 0` で成功として終わる
- `ccspk` が無いとき: `exec` が 127 で終わり、`-` で無視される（タイムアウトではないので 1 には当たらない）
- 起動時の `dict import` が `save()` で同じファイルを書き直すのは、ファイルを読み終えた後なので問題ない
- `export` と `save` が `dump` を共有していて、形は揃っている
- `voicevox/user_dict.json` の中身: HEAD の 30 単語はすべて `~/.config/ccspk/user_dict.json` にある
  （こちらは 40 単語。増えた 10 はエンジン側にあった分）
- 古い記述の残り: 指定の `rg` の結果は `TODO.md` の項目の文と、新しい文書の `dict export` の説明だけ
- `README.md` の表、`CLAUDE.md` の注意、`docs/UsersGuide.md` の節の書き換えは、今のコードと合っている
  （5 を除く）。インストールの手順は `uv tool install` が先で、`~/.local/bin/ccspk` を前提にする
  記述と矛盾しない
- TODO.md の要件: 5 項目とも差分で満たしている（「失敗してもエンジンは止めない」は 1 を除く）
- テスト: `save` はエンジンが要り、`demo()` は純粋な関数だけを見る作りなので、足さなくてよい
- 範囲: 指示に無い変更は無い
- コメント: `save` の docstring と unit のコメントは「なぜ」を書いている（unit の 90 秒は 1）
