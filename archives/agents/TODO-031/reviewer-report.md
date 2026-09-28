# TODO-031 レビュー報告（reviewer）

対象: `archives/agents/TODO-031/settings.json`・`cmd.sh`、`git diff` の CLAUDE.md。
`settings.json` の command は `cmd.sh` の各行を `"; "` でつないだものと一致した（awk でつないで diff、差なし）。
以下の行番号は `cmd.sh` のもの。

## 要修正

なし。

## 検討

### 1. 裏で動く担当がいると、返答の終わりに編集途中の状態を入れうる（cmd.sh:4〜7）

- 起きる条件: 管理者がサブエージェントを起動して返答を終えたとき（利用者全体の CLAUDE.md の
  「担当の完了をポーリングしない」どおりの待ち方）。main の Stop は担当の編集中にも来る
- 起きること: 担当が `src/` を途中まで直した状態で `ccspk test` が走る。落ちれば
  「ccspk test が落ちたので…」の `systemMessage` が出る（雑音）。通れば途中の状態を入れ直し、
  次に main の返答が終わるまで、読み上げはその版で動く
- 根拠: TODO-031 の「決めたこと」の「返答の終わりに 1 回だけ入れ直す（編集の途中の状態を入れないため）」。
  Stop は main の返答の区切りで、担当の作業の区切りではない。レビュー中にも `src/ccspk/hook.py` が
  別の作業で書き換わっていた（07:07:21、`git status` に ` M src/ccspk/hook.py`）
- 次の Stop で判定し直すので、最後は正しい版に落ち着く。どこまで許すかは管理者の判断（境界線上なので報告だけ）

### 2. 読み上げのフックと同時に入れ直すと、import が一瞬ファイルを見失いうる（cmd.sh:6。実害は未確認）

- 起きる条件: グローバルの Stop フック `ccspk hook` と並行して動く。こちらは find と test が
  約 0.1 秒で済むので（`uv run ccspk test` 実測 0.08 秒）、入れ直しは Stop から約 0.1〜0.5 秒の間に
  起きる。`ccspk hook` の import（実測 0.11 秒）と、`speak()` が起こす子プロセス
  `python -P -m ccspk.hook` の import が、ちょうどこの時間帯に重なる
- 実測（`UV_TOOL_DIR` を一時ディレクトリに向けた）: `--reinstall` の最中に
  `site-packages/ccspk/hook.py` の有無を 3 秒間ループで見ると、946162 回中 139 回無かった
  （見えない時間は合計 1ms 未満）。同じ入れ直しの間に `import ccspk.hook` を繰り返した約 30 回は全部通った
- `--reinstall` は ccspk だけでなく依存関係も入れ直す。実測で `click/core.py` の inode も変わった。
  `--reinstall-package ccspk` なら click の inode はそのままで、ccspk だけが入れ替わった（所要 0.37 秒。
  `--reinstall` は 0.43 秒）。見失いうるファイルの範囲がそのぶん狭まる。UsersGuide.md との揃え方も
  含めて管理者の判断
- ついでに確かめたこと: `--reinstall` は `--refresh` を含む（`uv tool install --help`）が、
  `UV_OFFLINE=1` でも通った（rc=0）ので、ネットワークが無くても入れ直せる

### 3. テストと入れ直しの間に書かれた変更は、次から検出されない（cmd.sh:4 と 6）

- 起きる条件: find が走ってから receipt が書かれるまで（約 0.5 秒）の間に `src/` が書き換わる。
  receipt のほうが新しくなるので、その変更はそれ以後の Stop でも `-newer` に掛からず、
  別のファイルが変わるまで入れ直されない
- 1 の状況（担当が編集中）で起きやすくなる。確率は低い。実害は未確認

## 好みの範囲

- cmd.sh:8 `jq` が無い環境では、落ちたときの知らせが出ない（jq が 127 で終わり、stderr は通常表示されない）。
  このマシンには `/usr/bin/jq` がある。リポジトリに入れる設定なので、他の環境で使うなら気にする程度
- コミットしただけ（ファイルの変更なし）では入れ直さないので、hatch-vcs の版（`ccspk --version`）は
  コミット前の日付付きの版のまま残る。動作には関係しない

## 問題なし（1 行ずつ）

- find の式: `(-name __pycache__ -a -prune) -o (-newer r -a -print -a -quit)` と解釈され、意図どおり。`-quit` は GNU find にある
- `__pycache__` の除外: ディレクトリごと刈るので中の `.pyc` は見ない。`__pycache__` を新しく作ったときは親の `src/ccspk` の mtime が変わるが、フック内の test（入れ直しの前）で作られる分は receipt より古くなるので空回りしない
- ディレクトリの mtime: ファイルの追加・削除・改名（保存が一時ファイルからの rename の場合を含む）を拾う。削除だけの変更も検出できる。エディタの一時ファイルで余分に入れ直すことはあるが、害は 0.5 秒程度
- 自分で自分を起こさないか: pyproject.toml に hatch-vcs の `version-file` は無く、ビルドで `src/` に書くものは無い（設定を読んで確認。1 の書き換えと重なったため、実測での確認はできなかった）
- 分岐: test が落ちたら入れ直さず、test の出力の末尾 5 行を付けて知らせる。入れ直しが落ちたら、その出力を付けて知らせる。両方通れば何も出さず exit 0。receipt が更新されないので、落ちている間は毎回知らせ続ける（意図どおりと読んだ）
- 終了コードと JSON: どの経路も exit 0（jq が動けば）。stdout に出るのは jq の `{"systemMessage": ...}` だけ（他のコマンドの stdout はすべて `$( )` で取っている）。`decision: block` を使わないので Claude を止めず、Stop のループも起きない。Claude Code の共通出力の `systemMessage`（利用者への警告表示）の使い方に合っている
- receipt が無いとき: cmd.sh:3 で exit 0。test も走らない
- uv が無いとき: `PATH=/usr/bin:/bin` で実行して rc=0、何もしなかった。stderr に `uv: command not found` が 1 行出るだけ
- シェル: `sh`（このマシンでは bash）・`bash`・`zsh` のどれでも `-n` が通った。使っている構文は POSIX の範囲
- timeout 120: 実測の所要は 1 秒未満で十分な余裕がある。uv の解決中に止められても、入れ替えの前なので壊れない（入れ替え中に止められる確率は無視できる）
- CLAUDE.md の書き足し: 条件（`src/` か `pyproject.toml` が前回のインストールより新しい）・test → `--reinstall` で入れ直し・落ちたら `systemMessage`・入れていない環境では何もしない、の 4 点とも実装と一致。行の長さも既存の行（最長 102 字）の範囲。「コマンド」節の `uv tool install .` とも食い違わない
- 範囲: 差分は CLAUDE.md の 3 行と TODO.md のチェック 1 つだけで、指示に無い変更は無い
- テスト: シェルの設定なので `demo()` の対象ではない。3 通りの動作は verifier の担当

## 作り込みすぎ

作り込みすぎ: なし。`cd` はフックの cwd がプロジェクトの直下とは限らないので要る。cmd.sh:3 は find の
`-newer` が無いファイルで失敗して空になるので無くても同じ結果になるが、stderr を汚さないために残す価値がある。
JSON のエスケープに jq を使うのが一番短い。
