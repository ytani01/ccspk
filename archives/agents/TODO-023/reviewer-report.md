# TODO-023 reviewer の報告

対象: `git diff`（CLAUDE.md・README.md・docs/Developer.md。TODO.md はチェックだけ）。
移す前は `git show HEAD:README.md`。

## 要修正

### 1. docs/Developer.md:279 付け替えた範囲が TODO-001〜005 になっている

- 何が: 「TODO-001〜005 は、…分けたときに付け替えた」とあるが、TODO-006 も付け替えている
- 根拠:
  - `archives/todo/TODO-006. 読み上げが使えない環境では、早々にあきらめて覚えておく.md:3` に
    「旧番号: dotfiles-claude（`~/.claude`）の TODO-010。このリポジトリに分けたときに付け替えた。」
  - `a1a9b44` の本文に「TODO の番号を付け替え（TODO-001〜005 が決着済み、TODO-006 が残り）」
  - `rg -n 旧番号 archives/todo` で旧番号の行があるのは TODO-001〜006 の 6 件
- どう直すとよいか: 「TODO-001〜006 は、…」にする。残りの 2 文（旧番号は各ファイルにある、
  `a1a9b44` より前のコミットは旧番号のまま）は実際と合っている（下の「確かめたこと」）

## 検討

### 2. README.md:10 「鳴らせない環境では何もせずに終わる」が、実際の動きと README:18 に合わない

- 何が: 実際は、鳴らせないと分かると理由を `UNUSABLE` に書き、そのファイルを消すまで
  確かめもせずに終わる（`src/ccspk/hook.py:391-397`）。環境が戻っても自然には鳴らない。
  「何もせずに終わる」では、この「覚える」ことが落ちている。README:18 の
  「読み上げが止まったままになった理由を見る」は、覚えることを知らないとつながらない
- 移す前の README には「使えないことを覚えて、次からは確かめもせずに終わる」とあった
- どう直すとよいか: 例「鳴らせない環境では読み上げずに終わり、そのことを覚えておく
  （戻し方は UsersGuide）」。書き方は判断に任せる

### 3. docs/Developer.md:28-30 と docs/UsersGuide.md:224-227 で記号と数字の置き換えの決まりが 2 か所にある

- 何が: Developer.md の「動き方」に「「〜」「→」などを「から」に置き換え、数字の後に日本語が続く
  ときは間のスペースを消す」と決まりそのものが書かれ、UsersGuide.md の「記号と数字」に
  同じ決まりが詳しく書かれている。Developer.md:160 からも「記号と数字」へリンクしている
- 今回の差分で入ったものではない（HEAD の Developer.md にもある）が、TODO-023 の 4 つ目の
  チェック項目「同じ説明が 2 か所にあれば 1 か所に」の範囲に入る
- どう直すとよいか: Developer.md:28-30 を「記号と数字の置き換えと単語の読みは
  [UsersGuide.md](UsersGuide.md#読み上げの辞書) にある」程度に縮める。実害は未確認

### 4. docs/Developer.md:52-53・128-131 と docs/UsersGuide.md:118-120 で「鳴らせない 3 条件」が 3 か所にある

- 何が: 「`pw-play` が無い、エンジンに接続できない、PipeWire が動いていない」が
  Developer.md の「動き方」、同じファイルの「鳴らせるかを確かめる」、UsersGuide.md の
  「読み上げが止まったままのとき」にある。短い列挙で、利用者向けの要点と実装の詳細の
  関係とも読めるので境界線上。今回の差分で入ったものではない
- どう直すとよいか: 残すなら現状のまま。減らすなら Developer.md:52-53 を
  「鳴らせないときは…（下の「鳴らせるかを確かめる」）」のように同じファイルの節へ寄せる。
  境界線上の判断なので報告だけ。実害は未確認

## 好みの範囲

### 5. docs/Developer.md:11-19 「ファイル」の表に `src/ccspk/__init__.py` が無い

- `git ls-files src` にあり、`__version__` をパッケージのメタデータから取るだけのファイル
  （`cli.py` が `--version` に使う）。載せないのも一つの判断。載せるなら
  「`__version__`（`--version` で出す版）」の 1 行

### 6. docs/Developer.md:279-281 同じ番号が別の項目を指すことに触れていない

- 分ける前のコミットの TODO-008〜013 と、分けた後の TODO-008〜013 は別の項目
  （例: `97eadcc` の TODO-012 は今の TODO-004、`9926f3b` の TODO-012 は今の TODO-012）。
  「`a1a9b44` より前は旧番号」で読み分けられるので、足さなくても誤りではない

## 観点ごとの結果

- 1. コードとの照合: 上の 1（番号）、2（README:10）以外は合っている。
  「ファイル」の表は `git ls-files src systemd pyproject.toml` と突き合わせて、不足は
  `__init__.py` だけ（上の 5）。各行の説明は `cli.py`（`test` がある）、`hook.py`
  （`main`・`say`・`stop`・`status` の click コマンド）、`click_utils.py`
  （`--version`・`--debug`・`--help`）、`mylog.py`、`voicevox-engine.service`
  （`ExecStartPost` で `dict import`、ファイルがあるときだけ）、`pyproject.toml`
  （`[project.scripts]`）と合う。README「特徴」「主な機能」の各行は、`LIMIT = 180`、
  `SPEAKER = 119  # 夜語トバリ（明るい）`、Developer.md の「動き方」、UsersGuide.md の
  `stop`・`dict`・`status` の節と合う
- 2. TODO の番号: 上の 1 のほかは合っている。`git log` で `a1a9b44` より前の 5 件
  （`a9283f6` TODO-008 〜 `7f306fc` TODO-013）は旧番号、`a1a9b44` は
  「dotfiles-claude の TODO-014」と明記、`7a526e0`（TODO-006）以降は新番号。
  CLAUDE.md:26 の「`~/.claude` から分ける前のコミットメッセージ…は旧番号」も合っている
- 3. 重複: 今回の差分で新しく生まれた重複は無い。README の「特徴」は要点だけで、字数の延ばし方や
  切り方の決まりは Developer.md の「動き方」だけにある。前からある重複は上の 3・4
- 4. リンクと参照: 切れているものは無い。README の 2 つのリンク、Developer.md の
  `#動き方`・`UsersGuide.md#読み上げの辞書`・`#読み上げが止まったままのとき`・`#記号と数字`、
  UsersGuide.md の `#辞書のファイル` は、どれも見出しがある。CLAUDE.md の
  「フックを手で動かす」「辞書のファイル」「TODO の番号」も見出しがある。
  旧見出し「### ファイル」（`#ファイル`）へのリンクは archives の外に無い
  （`rg -n '#ファイル' --glob '!archives/**'` が 0 件）
- 5. 日本語: 造語・直訳調は見当たらない。既存の言い回し（「鳴らす」「読み上げが止まったまま」
  「単語」）に合っている
- 範囲: 差分は CLAUDE.md・README.md・docs/Developer.md・TODO.md（チェック）だけで、指示どおり
- 作り込みすぎ: なし

## 再確認

直した 1〜5 だけを `git diff` で見た。どれも指摘に合っている。新しく切れたリンクや食い違いは無い。

- 1: 合っている。docs/Developer.md:279 が「TODO-001〜006」になり、`rg -n 旧番号 archives/todo` の 6 件、`a1a9b44` の本文と合う
- 2: 合っている。README.md:10-11 の「そのことを覚えて、次からは確かめもせずに終わる」は
  `hook.py:391-397` の動きと合い、README.md:18 の `ccspk status` の行ともつながる
- 3: 合っている。docs/Developer.md:29 から決まりが消え、リンク先の `UsersGuide.md#読み上げの辞書` は
  「記号と数字」を含む節（docs/UsersGuide.md:145・220）なので、行の内容と合う。決まりは UsersGuide.md だけに残る
- 4: 合っている。docs/Developer.md:52 のリンク `#鳴らせるかを確かめる` の見出しは docs/Developer.md:124 にある。
  3 条件は Developer.md では「鳴らせるかを確かめる」だけに残る
  - 好みの範囲: 「鳴らせないときは（下の「鳴らせるかを確かめる」）鳴らさずに終わり」は括弧の位置が
    少し読みにくい。「鳴らせないとき（条件は下の「鳴らせるかを確かめる」）は、鳴らさずに終わり」の
    ほうが自然。「終わり、…終わる」の重なりは前からある
- 5: 合っている。`__init__.py` の `__version__` は `cli.py` が `click_common_opts(__version__)` で
  `--version` に渡している。「版」は UsersGuide.md:204 の「エンジンの版」と揃う
