# TODO-011 reviewer の報告

対象: `git diff --cached -M` と `git diff`（`voicevox/user_dict.json`・TODO-012 の節は除く）。
写しただけの `click_utils.py`・`mylog.py`・`__init__.py` は中身を見ていない。
プロジェクトの `CLAUDE.md` は無いので、利用者全体の `CLAUDE.md` と既存のコード・文書に照らした。

実測は `.venv/bin/claudecodespeak`、`XDG_RUNTIME_DIR` は `mktemp -d`、音を出さないため
`PIPEWIRE_REMOTE=x` と偽の `pw-play`（`cat >/dev/null; sleep 30`）を `PATH` の先頭に置いた。
エンジン（0.25.2）は本物。辞書は書き換えていない（add-word は `query` を差し替えて呼んだ）。

## 要修正

### 1. `src/claudecodespeak/hook.py:242` 子プロセスが、作業ディレクトリの同名モジュールを import する

- 何が問題か: `[sys.executable, "-m", MODULE, PLAY, text]` は `-m` で起こすので、
  子の `sys.path[0]` がカレントディレクトリになる。Popen は `cwd` を渡していないので、
  Claude Code の作業ディレクトリ（利用者のプロジェクト）を引き継ぐ。そこに `click.py`・
  `queue.py`・`json.py` のような名前のファイルがあると、それを import する
- なぜ問題か（実測）: 一時ディレクトリに `click.py`（読み込まれたら印のファイルを書く）を置き、
  そこを cwd にして `claudecodespeak hook` に Stop の JSON を渡した。フックは rc=0 で終わるが、
  印のファイルができ（`click.py in cwd was imported`）、子プロセスのグループは 1 秒後に
  何も残っていなかった（鳴らずに黙って落ちる）。つまり
  - そのプロジェクトでは読み上げが黙って止まる（`UNUSABLE` にも残らない）
  - 開いたリポジトリにある `.py` を、フックの子プロセスが実行する
- 移す前との差: 旧版は `python3 /…/hooks/speak-response.py` で、`sys.path[0]` はスクリプトの
  ディレクトリだったので、この問題は無かった
- 参考（実測）: 同じディレクトリで `.venv/bin/python -P -c 'import click'` は site-packages の
  click を読み、印のファイルはできなかった（`requires-python >= 3.13` なので `-P` は使える）。
  直し方の選択は管理者に任せる（`cwd` を渡す手もある）
- 親（`claudecodespeak` のエントリスクリプト）は `sys.path[0]` が bin ディレクトリなので影響しない

## 検討

### 2. `src/claudecodespeak/hook.py:362-365` 引数を間違えると終了コード 2 になる（Stop では止める扱い）

- 実測: `claudecodespeak hook extra` と `hook --unknown` は usage を stderr に出して rc=2。
  旧版は `python3 speak-response.py extra` で rc=0（引数を見ていなかった）
- なぜ気にするか: Claude Code のフックは終了コード 2 を「ブロック」として扱い、Stop なら
  stderr を Claude に渡して止まらせない。登録の `command` を書き間違えたとき（今後オプションを
  消したとき、settings.json に古い引数が残ったときも）に、読み上げが止まるだけで済まない。
  Claude Code 上での実害は未確認
- 正しく登録していれば起きない。境界線上なので報告だけ

### 3. `docs/UsersGuide.md:63,74` 登録が `PATH` に頼るようになった

- 旧版は `$HOME/work/…` の絶対パスだったが、新しい例は `command -v claudecodespeak` で探す。
  Claude Code を `~/.local/bin` が `PATH` に無い環境（デスクトップのランチャーなど）から
  起こすと、入れてあっても黙って何もしない。例の書き方そのものは「入れていなければ何もしない」の
  とおりに動く（下の 5.）。実害は未確認（この環境の Claude Code の `PATH` は測っていない）
- `~/.local/bin` は `uv tool dir --bin` の値（実測）

### 4. `docs/Developer.md` に、移す前の呼び方の説明が残っている

- `docs/Developer.md:47`「MessageDisplay フックとしてこのスクリプトを起動し」
  → 今は `claudecodespeak hook` を起動する
- `docs/Developer.md:53-58`「`main()` は引数で 3 つに分かれる」の表の `--play <本文>` の行
  「子プロセスとして、合成と再生をする（`play()`）」→ 子プロセスは `main()`（click）を通らず、
  `hook.py:424-427` の `if __name__ == "__main__"` で `play()` に入る。`main()` の `--play` は
  手で試すとき（`claudecodespeak hook --play`）だけ通る
- `docs/Developer.md:80`「`speak()` は、同じスクリプトを `--play <本文>` で起動する」
  → `python -m claudecodespeak.hook --play <本文>`（100-102 行には正しく書いてあり、同じ主張が 2 か所で食い違う）
- 旧パスの検索（`rg -n "speak-response|add-word\.py|hooks/" --glob '!archives/**'`）で出るのは
  `TODO.md:32,40` の「旧 …」の説明だけで、残りは無い

## 好みの範囲

- 移し替えの直後に一度だけ、旧版が起こした再生中の子プロセスを新版は見分けられず止めない
  （cmdline に `claudecodespeak.hook` が無い）。長くても 1 回分（30 秒ほど）鳴り終わるだけ。実測はしていない

## 問題なかったもの

- hook の標準入力: click は stdin を読まない。Stop の JSON を渡すと子が起き、PID・`last`・`lock` ができた。rc=0、stdout/stderr は空
- `CLAUDE_TTS_SPEAK` なし: rc=0、何も出さない
- 子の cmdline は `…/python -m claudecodespeak.hook --play 確認です。二つ目の文です。`。2 回目のフックで前のグループ（python・pw-play・sleep）が消え、新しい子に替わった（`.venv` と、別の `UV_TOOL_DIR` に `uv tool install` したものの両方）
- `hook --test`・`add-word --test`・`uv run claudecodespeak add-word --test`: どれも `ok`、rc=0。`add-word --test a b` も `ok`（旧版は `--test` 単独のときだけ。実害なし）
- add-word の引数の誤り: 引数なし、`--type BAD`、`--accent x` はどれも usage で rc=2（旧 argparse と同じ 2）
- add-word の `sys.exit(文字列)`: click を通っても `SystemExit` のまま出る（`query` を URLError にして `エンジン（…）とやり取りできない: refused` を確認）。rc=1 になる点も旧版と同じ
- `PATH=/nonexistent` の再現手順: rc=0、`unusable` に `pw-play が無い`。shebang が絶対パスなので Developer.md 202 行の説明どおり
- UsersGuide の登録例 `! command -v claudecodespeak >/dev/null || claudecodespeak hook`: `PATH=/usr/bin:/bin`（入っていない）で sh・bash・zsh とも rc=0・出力なし。入っているときは hook の rc がそのまま返る（0）。`/bin/sh` は bash。dash は無いので未確認
- `uv tool install --reinstall` で直したコードが入る（別の `UV_TOOL_DIR` に入れ、docstring を書き換えて `hook -h` の表示が変わるのを確認）
- `pyproject.toml`: src レイアウトは hatchling が自動で拾い、`uv tool install` で動いた。`--version` は `0.1.dev19+gd6c01f11e.d20260928`（hatch-vcs）。`.git` の無いところから入れると版が取れない点は、今の入れ方（clone してから入れる）では起きない
- `cli.py`: `-h`・`-d`・`-V` が効く。`-d hook --test` で DEBUG が stderr に出る
- README の表・UsersGuide の書き換え: コードと合っている
- テスト: `stop_playing()` の見分け方は移す前から `demo()` に無い。今回は上の実測で確かめた

## 作り込みすぎ

- `src/claudecodespeak/cli.py:L11,L19`: delete: `_log` と `_log.debug(f"debug={debug}")`（受けた `-d` をそのまま出すだけ）。消してよい。好みの範囲
- `src/claudecodespeak/cli.py:L26-27`: delete: `if __name__ == "__main__": cli()`。入口は `[project.scripts]` だけで、`python -m claudecodespeak.cli` はどの文書にも無い。好みの範囲
- `.gitignore:L3-5`: delete: `build/`・`dist/`・`*.egg-info/`。uv と hatchling の流れでは `uv build` をしない限りできない（`*.egg-info` は hatchling では作られない）。好みの範囲

net: -7 lines possible.
