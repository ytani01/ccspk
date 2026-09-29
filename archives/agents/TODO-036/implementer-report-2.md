# TODO-036 実装の報告 2（reviewer-report.md の 1・2・3・7・8 の対応）

## 変えた箇所

- 1・4: `src/ccspk/check.py` の `pending()` を新設し、`after_stop()` はそれが偽なら起こさない。
  `SPOKEN` が無ければ偽、`CHECKED` が無ければ真、あれば `SPOKEN` の mtime > `CHECKED` の mtime。
  `demo()` で「どちらも無い・SPOKEN だけ無い・CHECKED だけ無い・CHECKED が古い・同じ・新しい」の 6 つを assert
- 2: `parse()` は、読みが `table` の kana から `'`・`_`・`/`・`、` を除いたものと同じ行を捨てる。
  `demo()` に `fugashi+unidic-lite`（`フ'ガシ/タ'ス/ユ'ニディック、ラ'イト`）の 1 例。前からある例の
  `優先度` の kana を `ユウセ'ンド` から `ユウセンタ'ク` に変えた（返答の `ユウセンド` と同じになり、新しい条件で捨てられるため）
- 3: `check()` で、`claude -p` の後は 1 単語ずつ `register()` を try し、失敗は飛ばして続ける。
  1 単語でも登録できたら `save()` を 1 回（その失敗も同じく飛ばす）。`CHECKED` に追記して mtime を揃えてから、
  失敗があれば `RuntimeError: 登録できなかった単語がある: 表記（理由）、…` を上げ、`main()` が `FAILED` に書く。
  `claude -p` まで・`claude -p` 自体の失敗は前と同じく `CHECKED` を変えない。失敗の文を作る部分を `reason()` に分けた
- 8: `STATE`・`ADDED` を `src/ccspk/user_dict.py` の `DICT_FILE` の下に移し、`check.py` がそこから import する。
  `forget_auto()`・`auto` の関数の中の import を消した
- 7: `docs/UsersGuide.md` の「30 単語ほど」「680 単語ほど」「1 行 1 単語」、`docs/Developer.md` の「1 行 1 単語」
- 文書: UsersGuide 2.3 に 2（同じ読みは登録しない）と 3（一部を登録できなかったときはやり直さない、手で `dict add`）を足した。
  Developer 3.8 の `after_stop()`・流れの 4.・失敗の段落・`STATE` と `ADDED` の置き場所、4.1 の check の `demo()` を直した

CLAUDE.md・TODO.md・README.md は触っていない。

## 試したこと

| 試したこと | 結果 |
|---|---|
| `uv run ccspk test` | `ok` 3 行、終了コード 0 |
| `ruff check src/ccspk/check.py` | 指摘なし |
| `pending()` の `>` を `>=` に壊す | `demo()` が `AssertionError: 200` で落ちる（戻した） |
| `parse()` の同じ読みの条件を `True` に壊す | `demo()` が `AssertionError` で落ちる（戻した） |
| 空の `$XDG_STATE_HOME/ccspk/` で `after_stop()` を 2 回 | ファイルは何もできない（点検を起こさない） |
| 偽の `claude` が 2 単語を返し、`register` を 1 単語で `sys.exit('エンジンが断った（422）: x')` にする | もう 1 単語は登録・`ADDED` に 1 行・`save` 1 回。`failed.txt`: `RuntimeError: 登録できなかった単語がある: Zqxwordtest（エンジンが断った（422）: x）`。`checked.txt` に 2 単語、mtime は `spoken.txt` と一致、`pending()` は False |
| `check_anchors.py` | リンク 35 件 OK。NG は前からある 1 件のみ |

最後の試しは `register`・`save` を Python の中で差し替えたので、エンジンの辞書は変えていない。本物の `claude -p` は呼んでいない。

## 残る懸念

- 2 の比べ方は、reviewer が書いたとおり長音の違い（エンジンは `イ` で返す）は拾えない（`README` の `リ'イドミイ` と `リードミー` は別と見て登録する）。それで正しい向き
- 3 で `ADDED` への追記が `OSError` になったときは、今までどおり全体の失敗になり、`CHECKED` を変えない（登録できた単語は次から登録済みとして除かれるので、`claude -p` を呼び直すのは残りの単語だけ）
