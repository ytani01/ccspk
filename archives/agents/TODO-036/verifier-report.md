# TODO-036 確認の報告（verifier）

スクリプト: `verify.sh`（3〜5・8）、`verify2.sh`（6・7・後始末）、`break.sh`（2）、`real_claude.py`（9）。
環境は依頼どおり（`XDG_*` を scratchpad の `v36/` に、偽 `claude`・偽 `pw-play`）。
追加の手当て: 偽の `pw-play` だけだと `unusable()` が PipeWire のソケットを見つけられず読み上げずに終わるので、
`PIPEWIRE_REMOTE=fake` を設定して接続確認を飛ばした（最初の実行はこれで空振りし、直して再実行）。

## 1. `uv run ccspk test`
`ok` が 3 行、終了コード 0。一致。

## 2. 壊すと落ちるか（`break.sh`。check.py は 1 か所ずつ壊して元に戻し、`cmp` と `git status` で戻りを確認）
| 壊し方 | 結果 |
|---|---|
| `pending()` `>` → `>=` | 落ちた（`AssertionError: 200`） |
| `pending()` `>` → `<` | 落ちた（`AssertionError: 100`） |
| `parse()` `[ァ-ヴー]` を `[ア-ヴー]` | **落ちない（exit 0）** |
| `parse()` `ー` を外す | 落ちた（`AssertionError`） |
| `extract()` 名詞 → 動詞 | 落ちた |
| `extract()` `len(s) >= 2` → `>= 1` | 落ちた |
| `extract()` 漢字の条件を外す | 落ちた |
| `record()` `// 2` → `// 3` | 落ちた |
| `record()` 閾値 `>` → `>=` | **落ちない（exit 0）** |
| `record()` `SPOKEN_MAX` 64→32 KiB | 落ちた |

食い違い（境界線上。実害は未確認）:
- `parse()` のカタカナ判定の始点（`ァ`）は、`demo()` の例に小さい「ァ」を含む読みが無く、テストが見ていない。
- `record()` の `>` と `>=` の違いは、`demo()` が 63,063 バイトと 66,066 バイトしか試さず、ちょうど 65,536 バイトを試さないため見えない。

（最初の実行では、壊す→戻す→壊すを同じ秒に行ったため、1 件で前の壊れ方の結果が混ざったように見えた。
`break.sh` に 1.1 秒の待ちを入れて再実行し、上の表は再実行の結果。`ccspk` は editable で `src` を直接読んでいる。）

## 3. 通し（`CCSPK_SPEAK=1`、Stop に `Zqxverifyword を見る。`）
- `spoken.txt`: `Zqxverifyword を見る。`。`checked.txt`: `Zqxverifyword`
- `added.tsv`: `2026-09-29 16:25:02<TAB>Zqxverifyword<TAB>ズクスベリファイワード<TAB>ズ'クスヴェリファイワアド`
- 偽 `claude` の引数: `-p`、`--model sonnet`、`--setting-sources ""`（空の引数として渡っている）、`--tools ""`、
  `--no-session-persistence`、`PROMPT`。`SPEAK=0`。標準入力は `Zqxverifyword<TAB>ズ'クスヴェリファイワアド`。一致
- 登録後 `ccspk dict kana Zqxverifyword` → `ズ_クスベリファイワ'アド`（偽 `claude` が返した「ズクスベリファイワード」の読みになった）。一致
- `checked.txt` と `spoken.txt` の mtime は同じ（1790666701）。一致
- 点検の子プロセスは `check.lock` が取れる状態になるのを待って確認した（`pgrep` の出力は自分のシェルを拾ったので使わなかった）

## 4. 新しい文が無い Stop
同じ文を 5 秒以内にもう 1 回 → 記録されず、偽 `claude` は呼ばれない（呼び出し 1 回のまま）。
その後 6 秒空けて同じ文を出したところ、これは新しい文として読み直され（`spoken.txt` が 2 行）、点検は起きたが
単語が全部点検済み・登録済みなので偽 `claude` は呼ばれなかった（呼び出し 1 回のまま）。一致。
（「記録が増えない Stop で子プロセスを起こさない」ことそのものは、`pending()` の `demo()` とこの前半で見ている。）

## 5. 失敗
偽 `claude` を終了コード 1 にして `Zqxfailword` の Stop:
- `failed.txt`: `RuntimeError: claude -p が終了コード 1 で終わった: fake failure`。一致
- `checked.txt` の mtime は変わらない（前後とも 1790666709）、`Zqxfailword` は入らない。一致
- 次の Stop の標準出力: `{"systemMessage": "ccspk の読みの点検が失敗した: RuntimeError: claude -p が終了コード 1 で終わった: fake failure"}`。
  `failed.txt` は消えた。一致
- 直後の点検で `Zqxfailword` が `checked.txt` に入った（失敗した分のやり直し）。一致

## 6. 登録の失敗
`ccspk dict add` で試し、読み `ー` がカタカナの判定（`parse()`）を通り、エンジンに断られることを確かめて使った
（`ッ`・`ンー`・`ァ` は通る）。偽 `claude` が `Zqxbadword<TAB>ー` を返す:
- `failed.txt`: `RuntimeError: 登録できなかった単語がある: Zqxbadword → ー（読みから音が取れない。カタカナで渡す）`。表記と読みが出た。一致
- `checked.txt` に `Zqxbadword` が入り、mtime は `spoken.txt` と同じ（1790666745、前は 1790666718）。更新された。一致
- `added.tsv` には増えない。一致
- 次の Stop で `systemMessage` に同じ文が出た。一致

## 7. `dict auto`
- `ccspk dict auto`: `2026-09-29 16:25:02  Zqxverifyword  ズクスベリファイワード  ズ'クスヴェリファイワアド` と `Zqxsecond` の行（2 行、登録順）。一致
- `ccspk dict remove Zqxverifyword` → `added.tsv` から外れた。一致
- `ccspk dict auto --remove` → `Zqxsecond` の行、`消した: Zqxsecond（ID …）`、`書き出した: …`。`added.tsv` は 0 バイト。
  続く `dict auto` は `自動で登録した単語は無い`。一致
- `checked.txt` には 4 語（`Zqxsecond` 含む）が残る。UsersGuide の「消した単語は点検済みのまま」と一致
- 確かめていない: `dict add` で自動登録の単語を上書きしたとき一覧から外れること、`--remove` で「登録されていない（飛ばした）」の分岐（コードを読んだだけ）

## 8. `CCSPK_SPEAK=0`
手で置いた `failed.txt` はそのまま残り、`spoken.txt` も増えない（4 行のまま）。一致

## 9. 本物の `claude -p`（登録なし。`real_claude.py`）
入力 5 行: README（`リ'イドメ`）・pytest（`ピュ'テスト`）・`Zqxverifyword`・変数・優先度。
- 返答: `README\tリードミー` と `Zqxverifyword\tズクスヴェリファイワード` の 2 行。`parse()` で 2 件取れた
- 料金 `total_cost_usd` 0.0136022、`duration_ms` 1450。終了コード 0
- 参考: 依頼文の誤りの例（README）は見つけたが、UsersGuide の例にある pytest（`ピュ'テスト`）は返さなかった（「迷うもの」に当たったのだろう。推定）。
  Zqxverifyword の読みは、1 回だけの試行なので安定するかは分からない

## 10. 文書の突き合わせ
- README 1. 特徴の最初の 2 項目と「合成は手元の…」: `dict auto` で見直せる・まとめて消せる（`--remove`）、
  返答のたびに裏で動く（3・4）、外へ出すのは単語と読みの一覧だけ（偽 `claude` の標準入力がその形）。一致
- UsersGuide 2.3: ファイル名と中身（`spoken.txt`・`checked.txt`・`added.tsv` の列・`failed.txt`・`check.lock`）、
  失敗時の動き（5）、登録失敗は飛ばしてやり直さない（6）、`CCSPK_SPEAK` を消すと止まる（8）、
  「点検した単語を消しても登録し直さない」（7）。一致。料金の数字（$0.02・7 秒など）は測り直していない
  （今回の 5 語は $0.0136・1.45 秒で、桁は合う）
- UsersGuide 3.12: 出力の形（列を空白 2 つで区切る）、`消した: …`、`書き出した: …`、無いときの文言。一致
- UsersGuide の「`ok` を 3 行」: 一致。「エンジンに無い単語は飛ばす」と `dict add` の一覧からの外れは未確認（7 に同じ）

## 変更されたファイル
`git status`: 変更は CLAUDE.md・README.md・TODO.md・docs/Developer.md・docs/UsersGuide.md・pyproject.toml（sudachipy・sudachidict-core を追加）・
src/ccspk/cli.py・hook.py・user_dict.py・uv.lock、未追跡は src/ccspk/check.py と archives/agents/TODO-036/。
brief の範囲との照合は、brief を読んでいないため「判断できない」。src 側は check.py（新規）・hook.py（`record`・`after_stop`）・
user_dict.py（`register`・`forget_auto`・`auto`・`remove` の後始末）・cli.py（`check_demo`）で、依頼文の説明と矛盾は無い。
今回の確認で src は変更していない（`break.sh` のあと `cmp` で元と一致）。

## 後始末と、判断できなかったこと
- 登録した `Zqx*` は全部消した。`dict export` の前後の差は **1 か所あった**: `変数` の `accent_type` が 1 → 2
  （before.json の 327 行目）。今回の操作は `Zqx*` だけで、本物の `~/.config/ccspk/user_dict.json` は
  16:25:50 に別の者が書き換えていた（私は `XDG_CONFIG_HOME` を一時ディレクトリにしていた）。
  1 回目の実行の `before` は 35,748 バイトで、2 回目は 36,227 バイトと、すでに差があった。
  このため、差は今回の確認が原因ではないと考えるが、断定はできない（実害は未確認）
- ほかに判断できなかったことは無い
