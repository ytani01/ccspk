# TODO-043 verifier 報告

結果: 指示 1〜7 はすべて一致。食い違いなし。出力全文は `verify.out`、スクリプトは `verify.sh`・`anchors.py`（同じディレクトリ）。
XDG_* はすべて scratchpad の一時ディレクトリ。`dict add`/`remove`/`import`/`auto --remove`・`hook` は実行していない。

1. `uv run ccspk test`: `ok` 3 行、終了 0。
2. 引数なし `119  夜語トバリ  明るい`。`speaker 3` -> `3  ずんだもん  ノーマル`（ファイル 3）、`speaker ずんだもん` -> 同じ 3、`speaker 夜語トバリ 呆れ` -> `121  夜語トバリ  呆れ`（ファイル 121）。ディレクトリは `ccspk/speaker` のみで `.tmp` は残らない。すべて終了 0。
3. `99999`・`存在しない名前`・`夜語トバリ ツンツン` は終了 1、`a b c`・`--list 3` は終了 2。各実行の後、ファイルは 121 のまま。
4. `--list` の行数 127 = `/speakers` のスタイル総数 127。
5. ファイルが `x` -> 引数なしが `119  夜語トバリ  明るい`。
6. ファイル 3: `play("テスト。")` の最初の URL は `.../audio_query?speaker=3&...`、`query("テスト")` の引数は `speaker: 3`。ファイル無し: どちらも 119。
   （差し替えた urlopen が投げた例外が produce スレッドの traceback として stderr に出る。想定どおり。）
7. `](#...)` 38 件、対応する見出しの無いものは 0。3.9 節の例（引数なし・`ずんだもん` -> `3  ずんだもん  ノーマル`・`夜語トバリ 明るい` -> 119）と実出力が一致。`--list` の先頭 2 行（`2  四国めたん  ノーマル`、`0  四国めたん  あまあま`）も一致。

## 変更ファイル（git status）
CLAUDE.md、README.md、TODO.md、docs/Developer.md、docs/UsersGuide.md、src/ccspk/cli.py、hook.py、user_dict.py。未追跡は archives/agents/TODO-043/。
TODO-043 の範囲（コマンド追加・SPEAKER の一本化・文書）に沿う。指示に無いファイルの変更は無い。

## 確かめていないこと
- 実際の音声出力（鳴らしていない）。
- 見なくてよいと指示されたもの（文体、設計、エンジンに無い番号がファイルにあるときの挙動）。
- アンカーの規則は自作スクリプトによる GitHub 規則の近似。
