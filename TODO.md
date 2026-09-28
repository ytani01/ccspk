# TODO

**残っている項目: TODO-011、TODO-012。** これまでに 10 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-013` から。**

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

## TODO-012. 質問してくるときも、質問の文を読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] `AskUserQuestion` を呼ぶ直前（`PreToolUse`、matcher `AskUserQuestion`）に、
      `tool_input` の `questions[].question` を読み上げる。選択肢は読まない
- [ ] UsersGuide のフックの設定例に `PreToolUse` を足す
- [ ] Developer.md の動き方の説明を直す

利用者と決めたこと（2026-09-28）: 読むのは質問の文だけ。TODO-011 が済んでから着手する
（入れたコマンドの形で足す）。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
