# TODO-034 reviewer 報告

対象: `git diff -- docs/`（`docs/Developer.md`・`docs/UsersGuide.md`）と `TODO.md` のチェック。
要修正 0 件、検討 2 件、好みの範囲 2 件。

## 要修正

なし。

## 検討

### 1. CLAUDE.md の「注意」と Developer.md の 4.4 に、Stop フックの説明が 2 か所ある

- `CLAUDE.md:21-23` / `docs/Developer.md:283-287`
- 何が問題か: 4.4 を書き足したことで、同じ仕組み（`src/` か `pyproject.toml` が新しければ
  `ccspk test`、通ったら入れ直す、落ちたら `systemMessage`、入れていなければ何もしない）が
  ほぼ同じ文で 2 か所に並んだ。しかも中身が少し食い違う。
  CLAUDE.md は「落ちたら入れ直さず」だけで、入れ直しに失敗したとき（`.claude/settings.json:8` の
  `elif ! out=$(uv tool install -q --reinstall . 2>&1); then m='ccspk を入れ直せなかった'`）を
  書いていない。4.4 はそちらも書いている（コードと合っているのは 4.4）。
- なぜ問題か: CLAUDE.md は冒頭（`CLAUDE.md:7`）で「仕組みとテストは `docs/Developer.md`」と委ねて
  いる。片方だけ直すと食い違いが広がる。CLAUDE.md 側を「`src/` を変えると Stop フックが
  テストして入れ直す（`docs/Developer.md` の「4.4 入れ直し」）」程度に縮める手はあるが、
  CLAUDE.md は TODO-034 の対象に挙がっていない。範囲に入れるかは管理者の判断。実害は未確認。

### 2. 「2. 動き方」の「記号と数字は置き換え」が、今の置き換えの範囲より狭い

- `docs/Developer.md:30`（差分の外）
- 何が問題か: リンク先（UsersGuide の 2 章）は、見出しを「辞書で直せないもの」に変えた理由のとおり、
  英単語と日本語の間のスペースを詰めることとコミット ID を消すことまで含む。30 行目は
  「記号と数字は置き換え」のままで、TODO-034 の 5 項目目（見出しと中身が合っていない）と同じ
  ずれが残っている。3.6 の後ろの文（`docs/Developer.md:163`）は「記号や数字などの置き換え」に
  直してあるので、揃っていない。
- `rg -n '記号と数字' -g '!archives' -g '!TODO.md'` で出たのは 30 行目と 154 行目の 2 か所。
  154 行目（`to_speech()` の行の「記号と数字の読みを整え」）は、`drop_commit_ids()` を別に挙げた
  後の残り（`hook.py:111-126` の TODO 番号・範囲の記号・数字の後ろのスペース）を指していて、
  コードと合っている。
- 旧見出しへのリンク（`#22-記号と数字`）は残っていない。HEAD の時点でも Developer.md の 160 行目の
  1 か所だけだった（`git show HEAD:docs/Developer.md` で確認）。TODO の「2 か所」は、
  29 行目の「記号と数字」（リンク先は `#2-読み上げの辞書`）を数えたものと思われる（推測）。
- 30 行目を直すかどうかは管理者の判断。実害は未確認。

## 好みの範囲

### 3. 3.7 の表で `DIGITS` の位置がコードの並びと違う

- `docs/Developer.md:177`
- 表はほかの行がコードの定義順（`hook.py:32-64`）に並んでいる。`DIGITS` はコードでは
  `SPACE_WITHIN` の後ろ（`hook.py:49`）だが、表では `MODULE` と `CUT` の間に入っている。

### 4. 4.4 の「落ちたときや入れ直せなかったときは入れ直さず」

- `docs/Developer.md:286`
- 入れ直せなかったときに「入れ直さず」は重複している。意味はコードと合っているので、
  言い回しの話（TODO-035 の範囲）。

## コードと合っていたもの

- 3.6 `to_speech()` の行: 処理の順（コードブロック、表、リンクと URL、Markdown の記号、
  `drop_commit_ids()`、記号と数字、`clip()`）が `hook.py:96-128` と合う
- 3.6 `drop_commit_ids()` の行: 「` で囲んだ ID を消す、壊れるものは残す」が `hook.py:131-147` と合う
- 3.6 `chunks()` の行: 3 文目以降も含めて全部の塊に `squeeze()` を通す（`hook.py:246`）と合う
- 3.6 `squeeze()` の行: 英単語と日本語の間だけ詰める、切った後に通す理由が `hook.py:249-255` と合う
- 3.7 `DIGITS`: 値 `ゼロ イチ ニー …`、0〜9、TODO 番号（範囲の後ろの番号も）に使う（`hook.py:49,116`）と合う
- 4.1 hook の `demo()`: 挙げた 7 関数・`questions()`・`assemble()`（一時ディレクトリ）を確かめている
  （`hook.py:311-470`）。`drop_commit_ids` は直接呼ばず `to_speech` を通して確かめている（`hook.py:361-387`）が、
  「確かめている」の記述としては合う
- 4.1 dict の `demo()`: `accent_of` と `halfwidth` だけ（`user_dict.py:114-124`）。「全角から半角へ戻す」は
  `user_dict.py:84` の docstring と合う
- 4.1 `uv run ccspk test` のコメント「hook と dict の demo() を両方」: `cli.py:26-29` と合う。
  「通れば ok」は UsersGuide 3.6 の「ok を 2 行」と矛盾しない
- 4.4: receipt の場所（`$(uv tool dir)/ccspk/uv-receipt.toml`）、`src`・`pyproject.toml` の新しさ、
  `uv run ccspk test`、`uv tool install --reinstall .`、2 通りの失敗で出力の最後 5 行を `systemMessage`、
  receipt が無ければ何もしない（`.claude/settings.json:8`）と合う
- 1. ファイルの表の `.claude/settings.json` の行: 4.4 と合う
- UsersGuide 2.2 の見出しと書き出し: 見出し変更と「`to_speech` で」を外したのは TODO どおり。
  中身（`chunks` で詰める、`drop_commit_ids` の規則）は `hook.py` と合う
- 3.6 と UsersGuide 2.2 の重なり: 3.6 は関数ごとの 1 行とリンクで、規則の詳しい説明は 2.2 だけにある。
  `squeeze()` を切った後に通す理由だけ両方にあるが、3.6 の 1 行に収まる程度
- アンカー: `rg -n '\]\([^)]*#' docs README.md CLAUDE.md` の 20 件すべてが、GitHub の見出しアンカー
  の規則（小文字化、英数字・かな漢字・`-`・空白以外を除く、空白を `-`）で実在する見出しに当たる。
  `#22-辞書で直せないもの`・`#44-入れ直し` も当たる（スクリプトで確認。README.md・CLAUDE.md には該当リンク無し）
- TODO.md の TODO-034 の 6 項目: いずれも満たしている（上の検討 2 は 5 項目目と同じ種類のずれが
  別の行に残っている指摘で、項目の文面そのものは満たしている）
- 範囲: 変更は `docs/` の 2 ファイルと `TODO.md` のチェックだけ。指示に無い変更は無い

## 作り込みすぎ

- `CLAUDE.md:21-23`: delete: Developer.md 4.4 と同じ説明。4.4 への 1 行の参照に置き換えられる
  （検討 1 と同じ。重大度は「検討」）

net: -2 lines possible.
