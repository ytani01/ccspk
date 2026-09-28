# TODO-011. Python のコードを uv で管理し、`uv tool install .` で入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | 不明 | 28,400 | 68,208 | 65% |
| reviewer | Opus 5.5 | high | 940 | 86,074 | 27% |
| verifier | Sonnet 5 | medium | 2,769 | 46,869 | 8% |
| 合計 |  |  | 32,109 | 201,151 | 概算 $3.9 |

- main の effort は記録に残っておらず、分からない
- 立ててから着手までに TODO-009・TODO-010 を挟んだので、`--since '2026-09-28 09:43:00'` で集計した。
  範囲には、途中で TODO-012 を立てたやり取りも入っている
- reviewer は同じ担当に 2 回目を頼んだ（指摘を反映した後の見直し）

## きっかけ

フックと辞書のスクリプトを、リポジトリのパスで呼ぶのをやめたい。
uv で管理し、`uv tool install` で入れた 1 つのコマンドから使えるようにする。

利用者と決めたこと（2026-09-28）: コマンドは 1 つにまとめてサブコマンドに分ける。
フックの登録は、リポジトリのパスではなく入れたコマンドの名前にする。

## やったこと

- `pyproject.toml` と `uv.lock` を置いた（hatch-vcs、依存は click と loguru）。
  `uv tool install ~/work/claudecodespeak` でコマンド `claudecodespeak` が入る
- `hooks/speak-response.py` を `src/claudecodespeak/hook.py`（`claudecodespeak hook`）へ、
  `voicevox/add-word.py` を `src/claudecodespeak/add_word.py`（`claudecodespeak add-word`）へ移した。
  argparse と `sys.argv` の見分けは click に置き換えた。`--test` と `--play` は残した
- `cli.py` でサブコマンドをまとめた。`click_utils.py`・`mylog.py`・`__init__.py` は
  hyprwhspr-utils から写した（`-d` でデバッグのログが出る）
- 再生の子プロセスは `python -P -m claudecodespeak.hook --play <本文>` で起こし、
  `stop_playing()` は cmdline に `claudecodespeak.hook` と `--play` があるかで見分ける。
  `-P` は reviewer の指摘で足した（作業ディレクトリに `click.py` などがあると、それを
  import して再生が黙って止まった）
- README のファイルの表、UsersGuide の入れ方とフックの登録例
  （`! command -v claudecodespeak >/dev/null || claudecodespeak hook`）、Developer.md の
  仕組みと試し方を書き換えた。UsersGuide には、`PATH` で見つからないと鳴らない旨を 1 行足した

着手してすぐに測った import の時間（Python 3.13、10 回の中央値）: 何も import しない起動 10.1 ms、
click 25.9 ms、loguru 45.7 ms、両方 49.3 ms、mylog.py と click_utils.py 60.1 ms。
今のフックは 72.8 ms。増えるのは 50 ms ほどで、`timeout`（5 秒）に比べて小さいので、フックでも読み込む。

利用者と決めたこと（2026-09-28）:

- `hook` の引数を書き間違えると click が終了コード 2 で終わる（Stop ではブロック扱い）。
  起きるのは登録の書き間違いのときだけなので、そのままにする
- `PATH` に `~/.local/bin` が無いと黙って何もしない件は、UsersGuide に注意を 1 行足すだけにする

## 確かめたこと

- reviewer: 移す前との挙動の違い、click と stdin・終了コード、文書とコードの突き合わせ。
  1 回目は要修正 1 件（`-P`）と Developer.md の古い説明、2 回目は要修正なし
  （[reviewer-report.md](../agents/TODO-011/reviewer-report.md)、
  [reviewer-report-2.md](../agents/TODO-011/reviewer-report-2.md)）
- verifier: 入れたコマンドで UsersGuide・Developer.md の手順を書いたとおりに実行し、すべて一致
  （[verifier-report.md](../agents/TODO-011/verifier-report.md)）

## 残ること

- Developer.md の「最初の音までは 1.2〜2.5 秒ほど」に対し、verifier の実測は 0.77〜0.81 秒だった。
  この項目では直していない

## 分担の振り返り

- reviewer は、作業ディレクトリが `sys.path` に入る件を実測で見つけた。main の手元の確認
  （フックを 2 回呼ぶ）では出ない条件で、reviewer を入れた効果があった。
  「click を通さないので速い」が 2 ms 差しか無いことも測って指摘した
- verifier は食い違いを見つけなかった（文書の数値の古さだけ）。手順の再現としては要った
- 見込みとの食い違いは reviewer が 2 回になったことだけ。料金の 27% が reviewer で、
  cache_creation は main より多い。次に同じ規模なら、移す前と後のコードの差分
  （`git diff -M`）だけを読ませ、写しただけのファイルは対象外とはっきり書く（今回も書いた）。
  2 回目は反映した箇所だけを名指しして頼めば足りる
