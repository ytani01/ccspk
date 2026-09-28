# TODO-031. コードを直したら ccspk を自動で入れ直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 24,404 | 80,179 | 67% |
| reviewer | Opus 5.5 | high | 3,628 | 85,881 | 30% |
| verifier | Sonnet 5.5 | medium | 260 | 23,879 | 3% |
| 合計 |  |  | 28,292 | 189,939 | 概算 $2.9 |

- 途中から TODO-030 を同じ会話で並行して進めたので、main と reviewer の数字には TODO-030 の分
  （実装と、TODO-030 の reviewer の途中まで）が混ざっている。時刻では切り分けられない
- reviewer・verifier はサブエージェントのログが少なめに出る（`todo-workflow` skill）

## きっかけ

コードを直すたびに `uv tool install --reinstall .` を手で打たないと、読み上げのフックが古い版のまま動く。

背景（決めたこと）:

- 返答の終わりに 1 回だけ入れ直す（編集の途中の状態を入れないため）。editable インストールにはしない
- 設定は `.claude/settings.json`（リポジトリに入れる）。`.claude/settings.local.json` は変えない

## やったこと

- 着手時に測った（一時の `UV_TOOL_DIR` と worktree）
  - `--reinstall` が無くても、同じ版のまま 2 回目の変更が入った。それでも UsersGuide.md に合わせて付けた
    （0.8 秒）
  - `$(uv tool dir)/ccspk/uv-receipt.toml` は入れ直すたびに mtime が新しくなるので、前回のインストールの印に使う
  - 入れ直しても venv は作り直されない（`bin/python` の inode はそのまま）
- `.claude/settings.json` に Stop フックを足した（中身は [cmd.sh](../agents/TODO-031/cmd.sh) を 1 行につないだもの）
  - receipt が無ければ何もしない（`ccspk` を入れていない環境）
  - `find src pyproject.toml -name __pycache__ -prune -o -newer <receipt>` で何か出たときだけ、
    `uv run ccspk test` を走らせ、通ったら `uv tool install -q --reinstall .`
  - テストか入れ直しが失敗したら、出力の末尾 5 行を付けて `systemMessage` で知らせる（`jq` で JSON にする）
  - 書き込みは auto mode に止められたので、main が用意したファイルを利用者が置いた
- CLAUDE.md の「注意」に、自動で入れ直すことを書いた

## 確かめたこと

verifier が確かめた（[verifier-report.md](../agents/TODO-031/verifier-report.md)）。6 通りとも期待どおり。

- 変更なし・入れ直した直後・`__pycache__` だけの変更では入れ直さない（テストやビルドが `src/` に書かない）
- `src/` を変えると入れ直し、入ったファイルに変更が載る
- テストが落ちると入れ直さず、`AssertionError` を含む `systemMessage` を出す。次の返答でも同じく知らせる
- 入れていない環境では何もしない。どの場合も終了コードは 0

## 残ること

reviewer が挙げた検討（[reviewer-report.md](../agents/TODO-031/reviewer-report.md)）。どれも実害は未確認なので、
このままにした。

- サブエージェントが裏で `src/` を直している間にも main の Stop は来るので、テストが通れば途中の状態が入る。
  次の Stop で判定し直すので最後は正しい版になる。利用者は、フックを置いた後の作業途中のコードが入ることを承知している
- `--reinstall` は click などの依存関係も入れ直す。読み上げのフックと重なると import が一瞬ファイルを
  見失いうる（見えない時間は合計 1ms 未満）。`--reinstall-package ccspk` にすれば範囲が狭まる
- find からの receipt の書き込みまで（約 0.5 秒）に書かれた変更は、別のファイルが変わるまで入れ直されない
- 入れ直しが失敗する分岐（`ccspk を入れ直せなかった`）は試していない
- `systemMessage` の先頭がトレースバックの途中の行から始まる（`AssertionError` は含まれる）

## 分担の振り返り

- reviewer は、裏の担当の編集中に入れ直しうること、`--reinstall` が依存関係まで入れ替えること、
  判定と receipt の書き込みの間の取りこぼしを見つけた。どれも要修正ではなかった。verifier は食い違いを
  見つけなかった
- 見込みどおりの編成だった。`.claude/settings.json` を main が書けなかったので、置いてもらう手間が 1 回増えた
- 次に `.claude/` の設定を足す項目では、auto mode に止められる前提で、中身を archives に作って利用者に置いて
  もらう段取りを最初から組む。reviewer は置く前の中身を見ればよいので、順序は変えなくてよい
