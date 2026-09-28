# TODO

**残っている項目: TODO-009、TODO-010、TODO-011。** これまでに 8 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-012` から。**

---

## TODO-009. VOICEVOX の辞書に語を簡単に足す CLI を作る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `<表記> <読み>` を引数で渡して、エンジンのユーザー辞書に登録する CLI を作る
      （標準ライブラリだけの Python 1 ファイル）
- [ ] アクセントの位置は、読みのカタカナを `/audio_query` に渡してエンジンに任せる。
      `--accent` で指定もできる
- [ ] 同じ表記が登録済みなら、`PUT /user_dict_word/<ID>` で読みを書き換える
- [ ] 登録後の読み（kana）を表示する。オプションで、登録後に実際に鳴らして確かめられる
- [ ] UsersGuide の「登録する」に使い方を書き足す

利用者と決めたこと（2026-09-28）: 形は引数で渡す CLI。するのはエンジンへの登録だけで、
`voicevox/user_dict.json` への書き戻しとコミットは今までどおり手で行う。

実測（2026-09-28）: 読みのカタカナを `/audio_query` に渡すと、`ハイパーウィスパー`・
`レビュータントウ` はアクセント句が 1 つで、位置（5・4）は手で決めた値と同じ。
`リードミー` は `リ'イ/ド'ミイ` と 2 つに分かれる。分かれたときは先頭の句の位置を使い、
表示した読みを見て `--accent` で直してもらう。

verifier は、書いたコマンドをエンジンに対して実際に試し、試した語は最後に消す。

---

## TODO-010. Stop 以外に、途中の報告の文章も読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] 実装の前に測る: `PreToolUse` と `PostToolUse` のどちらで、直前の文章が
      `transcript_path` のログに書かれているか
- [ ] ツールを呼ぶ前後のフックで、ログから直前の文章を取り出して読み上げる
- [ ] 同じ文章を 2 度読まない（Stop の `last_assistant_message` とも重ねない）
- [ ] UsersGuide のフックの設定と、Developer.md の「動き方」「フックの仕組み」を直す

途中の文章を読むフックは無いので、ツールを呼ぶたびに起動するフックで代わりにする。

利用者と決めたこと（2026-09-28）: 新しい読み上げが始まったら、前の読み上げは
今までどおり止めてよい（途中の文章が続けて来ると、冒頭で切れることは受け入れる）。
子プロセスの扱いは今の `stop_playing()` のまま変えない。

---

## TODO-011. Python のコードを uv で管理し、`uv tool install .` で入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `pyproject.toml` を置き、`uv tool install .` で 1 つのコマンドが入るようにする
      （名前の案は `claudecodespeak`。フックは `claudecodespeak hook`、辞書に足すのは
      `claudecodespeak add-word`。名前は着手時に決め直してよい）
- [ ] 前の再生を止めるときの見分け方（`/proc/<pid>/cmdline` にスクリプトの名前と
      `--play` があるか）を、入れたコマンドでも効くように直す
- [ ] UsersGuide の入れ方とフックの設定例を、入れたコマンドの名前に書き換える
      （利用者の `settings.json` は利用者が直す）
- [ ] README のファイルの表、Developer.md のテストと動作の確かめ方を直す
- [ ] `click_utils.py` と `mylog.py` を写して使う（CLI は click、ログは loguru）。
      元は tmr・hyprwhspr-utils の版（2 つは同じ中身で、いちばん新しい）
- [ ] 着手したら最初に測る: click と loguru を import すると、フックの起動
      （登録の `timeout` は 5 秒、今は 1 ms ほどで判定が終わる）がどれだけ遅くなるか

利用者と決めたこと（2026-09-28）: コマンドは 1 つにまとめてサブコマンドに分ける。
フックの登録は、リポジトリのパスではなく入れたコマンドの名前にする。

TODO-009（`voicevox/add-word.py`）と TODO-010（フックを足す）も、ファイルの場所と
呼び方に関わる。先に済んだ項目の分は、この項目でまとめて移す。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
