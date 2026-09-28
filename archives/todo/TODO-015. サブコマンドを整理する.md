# TODO-015. サブコマンドを整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（調査・設計）+ implementer（Sonnet 5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（調査・設計・レビュー後の修正）+ implementer（Sonnet 5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 21,096 | 41,609 | 47% |
| implementer | Sonnet 5 | medium | 17,399 | 94,503 | 29% |
| reviewer | Opus 5.5 | high | 5,608 | 69,093 | 17% |
| verifier | Sonnet 5 | medium | 3,454 | 40,885 | 7% |
| 合計 |  |  | 47,557 | 246,090 | 概算 $4.0 |

- どの担当もモデルを上書きしていない。effort は `~/.claude/agents/*.md` の値
- main の分には、作業中に割り込んだ「節」の辞書登録（`88ef11d`）と TODO-016 を立てた分が入っている

## きっかけ

サブコマンドが `hook` と `add-word` の 2 つで、試すための機能が `hook --play`・`hook --test`・
`add-word --test` とオプションに散っていた。辞書の一覧・削除・書き出し・読み込みや、
読み上げが止まった記録（`claude-tts.unusable`）の確認は、文書にある `curl`・`jq`・`rm` を手で打っていた。

## やったこと

整理したあとのサブコマンド:

| サブコマンド | 前の形 |
|---|---|
| `hook` | そのまま |
| `say TEXT` | `hook --play TEXT` |
| `test` | `hook --test`・`add-word --test` |
| `dict add SURFACE PRON` | `add-word` |
| `dict kana TEXT` | `curl … /audio_query \| jq .kana` |
| `dict list` | `curl … /user_dict \| jq` |
| `dict remove SURFACE` | `curl -X DELETE …/user_dict_word/<ID>` |
| `dict export [FILE]` | `curl … /user_dict \| jq -S . > voicevox/user_dict.json` |
| `dict import [FILE]` | `curl -X POST … /import_user_dict?override=true` |
| `status [--clear]` | `cat`・`rm` で `claude-tts.unusable` を見る・消す |

- `add_word.py` を `user_dict.py` に改名し、click の group `dict` を置いた。エンジンとの通信の
  例外処理は `call()` の中にまとめた（書き込みの失敗などを「エンジンとやり取りできない」と言わないため）
- `hook.py` の click のコマンドから `--play`・`--test` を外し、`say`・`status` を足した。
  子プロセスの目印の `--play`（`PLAY`・`MODULE`・`stop_playing()`・`__main__`）は変えていない
- `cli.py` に `test` を置き、`hook.demo()` と `user_dict.demo()` を順に呼ぶ
- `dict export` は `jq -S .` と同じ形（`indent=2`・キーの順・非 ASCII のまま・末尾の改行）で書く。
  `dict export` / `dict import` のファイルは引数で渡し、省くと標準出力・標準入力
- 旧い書き方は別名として残していない
- `README.md`・`CLAUDE.md`・`docs/Developer.md`・`docs/UsersGuide.md` のコマンド例を書き換え、
  辞書と `claude-tts.unusable` を `curl`・`jq`・`rm` で操作する手順をサブコマンドに置き換えた。
  エンジンの起動確認（`curl …/version`）は残した

## 確かめたこと

verifier が 11 項目を実際に動かし、すべて設計どおりだった（`archives/agents/TODO-015/verifier-report.md`）。

- `test` が `ok` を 2 行出す。`--help` に `add-word` が無く、`hook --help` に `--play`・`--test` が無い
- ダミー語で `dict add` → `list` → `remove` → 2 度目の `remove` が終了コード 1。最後に
  `dict export` が `voicevox/user_dict.json` と `cmp` で一致（テストの語が残っていない）
- `dict export` は標準出力・ファイルのどちらも `voicevox/user_dict.json` と一致。`dict import` は
  ファイル・標準入力のどちらも通る
- エンジンに届かないときは終了コード 1 で「とやり取りできない」。書き込めないパスへの `export` の
  メッセージに「エンジン」が出ない
- `status` はファイルが無いとき・あるとき・`--clear` の後で出力とファイルの有無が正しい
  （一時ディレクトリの `XDG_RUNTIME_DIR` で）
- フックが起こした子プロセスの `/proc/<PID>/cmdline` に `--play` と `claudecodespeak.hook` が入っている
- 文書のコマンド例のうち、打てるものは打って通った

`dict add --speak` は本物の辞書に語を足すことになるので試していない（`--help` だけ）。

## 分担の振り返り

- **implementer** は設計どおりに実装した。`dict remove` の確認で `&&` の分岐を誤り、ダミー語が
  残ったのを `cmp` の不一致で自分で見つけて消し直した。`TODO.md` のチェックボックスを入れ忘れた
- **reviewer** は要修正 0 件、検討 3 件（通信以外の `OSError` も「エンジンとやり取りできない」になる、
  UsersGuide の「どれもリポジトリの直下で」が広すぎる、チェックボックスが空）。3 件とも main が直した
- **verifier** は 11 項目すべて一致。エンジンが英数字を全角にして持つことに気付いたが、元からの動き
  （`find()` が NFKC で揃えている）
- 見込みとの食い違いは、レビュー後の修正を main が引き受けた点だけ。数行の修正で、implementer を
  もう一度起こすより安い
- 次に同じ規模（コードと文書を合わせて 8 ファイル、込み入ったロジック無し）をやるなら、同じ組み方でよい。
  implementer が料金の 29% を占めたので、依頼に「本物の辞書を試すときの手順」（足して・消して・
  `cmp`）を 1 行で書いておけば、確認のやり直し分を減らせる。チェックボックスを入れることは完了条件に
  書いていたが守られなかったので、返事の 5 行にも「チェックを入れたか」を含めさせる
