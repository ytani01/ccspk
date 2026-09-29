# TODO-036 確認の依頼（main → verifier）

目的: 読み間違いの自動の点検（`src/ccspk/check.py`、`hook.py`・`user_dict.py` の変更）が、設計どおりに動くかを実際に動かして確かめる。
設計は `archives/agents/TODO-036/brief.md`、その後の直しは `implementer-report-2.md` と、main が足した
「登録できなかった単語の知らせに読みも入れる」（`check.py` の `failed.append`）。

## 環境（全部の確認で共通）

- `XDG_STATE_HOME`・`XDG_CONFIG_HOME`・`XDG_RUNTIME_DIR` をスクラッチの一時ディレクトリに向ける。本物の `~/.local/state/ccspk/`・
  `~/.config/ccspk/`・`$XDG_RUNTIME_DIR/ccspk.*` は触らない
- PATH の先頭に偽の `claude`（引数・標準入力・環境変数 `CCSPK_SPEAK` をファイルに残し、決まった行を返すシェルスクリプト）と、
  偽の `pw-play`（`cat >/dev/null`）を置く
- エンジンの辞書は本物。登録する表記は英字の架空語（例: `Zqxverifyword`）だけにし、最後に消す。
  始める前と終わった後の `ccspk dict export` を `diff` して、差が無いことを報告に書く
- 手順は 1 本のスクリプトにまとめ、`archives/agents/TODO-036/verify.sh` に残す

## 確かめること（各 1 回でよい）

1. `uv run ccspk test` が通る
2. 壊すと落ちるか: 次をそれぞれ 1 か所ずつ壊し、`uv run ccspk test` が落ちることを確かめて元に戻す（`git diff` で戻ったことを確かめる）
   - `pending()` の比較（`<=` ↔ `<` など）
   - `parse()` のカタカナの判定
   - `extract()` の名詞の条件
   - `record()` の切り詰め
3. 通し: `ccspk hook` に Stop の入力（`{"hook_event_name":"Stop","last_assistant_message":"Zqxverifyword を見る。"}`）を渡す
   （`CCSPK_SPEAK=1`、エンジンが動いていること）。点検の子プロセスが終わるのを待ってから（`check.lock` と `ps` で）:
   `spoken.txt`・`checked.txt`・`added.tsv` の中身、偽 `claude` に渡った引数（`--setting-sources ""` があるか）と `CCSPK_SPEAK=0`、
   `ccspk dict kana Zqxverifyword` が偽 `claude` の返した読みになったか
4. 新しい文が無い Stop をもう 1 回: 点検を起こさない（偽 `claude` が呼ばれない）
5. 失敗: 偽 `claude` を終了コード 1 にして新しい文の Stop → `failed.txt` ができる。次の Stop の標準出力が `systemMessage` の JSON で、
   `failed.txt` が消える。`checked.txt` の mtime が変わらない
6. 登録の失敗: 偽 `claude` がエンジンに断られる読みを返す場合を 1 つ作れるなら作り（作れなければ、そう書く）、`failed.txt` に表記と読みが
   出ること、`checked.txt` は更新されることを見る
7. `ccspk dict auto` の表示と `ccspk dict auto --remove`、`ccspk dict remove` で `added.tsv` から外れること
8. `CCSPK_SPEAK=0` の Stop では何もしない（`failed.txt` もそのまま）
9. 本物の `claude -p` を 1 回だけ: `check.py` の `PROMPT` と、`表記<TAB>エンジンの kana` の一覧 5 行ほど（誤りを 1 つ含める。例:
   `README<TAB>リ'イドメ`）を、`check.py` と同じ引数で渡し、返答が `parse()` で読めるか。**登録はしない**（`parse()` の結果を表示するだけ）。
   料金と時間（`--output-format json` の `total_cost_usd`・`duration_ms`）を報告に書く
10. 文書の突き合わせ: `README.md` の「1. 特徴」の最初の 2 項目と「合成は手元の…」、`docs/UsersGuide.md` の「2.3」と「3.12 ccspk dict auto」に
    書かれたコマンド・ファイル名・出力の例を、実際の動き（3・7 の結果）と比べる。一致したものは 1 行、食い違いだけ詳しく

## 見なくてよいもの

最初の音までの時間（reviewer が import の時間を測った）、コードの良し悪し、文書の言い回し。

## 報告

コードは直さない。境界線上の判断は報告だけ（「実害は未確認」と添える）。
`archives/agents/TODO-036/verifier-report.md` に、項目ごとに「実行したコマンド・得た値・一致/食い違い」。一致したものは 1 行。
返事は 5 行以内（終わったか・報告のパス・食い違いの数）。
