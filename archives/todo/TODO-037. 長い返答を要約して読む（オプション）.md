# TODO-037. 長い返答を要約して読む（オプション）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Opus 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | implementer（Opus 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 32,924 | 136,949 | 47% |
| implementer | Opus 5.5 | medium | 3,671 | 211,831 | 30% |
| reviewer | Opus 5.5 | high | 7,832 | 104,214 | 21% |
| verifier | Sonnet 5.5 | medium | 506 | 40,537 | 2% |
| 合計 |  |  | 44,933 | 493,531 | 概算 $7.4 |

- implementer は定義のモデルが sonnet。子プロセスとフックの流れにまたがるので Opus 5.5 に上書きした
- implementer・reviewer は、指摘の直しと見直しで 2 回ずつ（同じ担当に続けて頼んだ）
- 集計は `--since '2026-09-29 16:50:00'`（立ててから着手まで TODO-036・038 が挟まった）。main の分には、途中で
  TODO-039 を立てたやり取りも入っている
- 表に入らない料金: 測定の `claude -p` 9 回（約 $0.2）、reviewer が誤って走らせた本物の `claude -p` 1 回と、
  verifier の本物の確かめ 1 回（それぞれ 1〜1.5 セントほど）

## きっかけ

180 字（`LIMIT`）を超える返答は切って読むので、後ろにある結論や頼みごとが読まれない。オプションで、要約してから
読めるようにする（2026-09-29 に利用者と決めた）。

決めたこと:

- 既定は切ったまま。`ccspk summary on|off` で切り替え、状態は `~/.config/ccspk/summary` に残す。環境変数
  `CCSPK_SUMMARY`（`1`・`0`）があればファイルより優先する（フックに届く環境変数は settings.json の `env` から来るので、
  コマンドからは変えられない。一時的に切り替えるのに使う）。最初は環境変数だけの案だったが、利用者が CLI で
  切り替えたいとした
- 要約ができてから読む。1 文目を先に読んで残りを要約する形は、要約が間に合わないと継ぎ目で黙り、仕組みも込み入るので採らない
- 子プロセスの面倒を見る範囲: 次の返答が来たら要約ごと止める。失敗・時間切れは切って読む。これより先は見ない
- 着手時に測って決めた（`archives/agents/TODO-037/main-measure.md`）: モデルは Sonnet（5〜6 秒・$0.010〜0.015。
  Haiku はそのままだと考える分で 33〜52 秒、止めれば同じ時間・料金だが経緯を並べがち）。Stop・MessageDisplay・PreToolUse の
  3 つとも要約する（最後の返答は MessageDisplay と Stop から同じ文で来るので、2 度読まない仕組みがそのまま効く）。
  読み間違いの点検（TODO-036）には、読んだ要約を記録する

## やったこと

- `src/ccspk/hook.py`
  - `to_speech()` を `clip(tidy(text))` に分け、`prepare()` で、要約が入っていて `tidy()` の文が `LIMIT` を超えるときだけ、
    切る前の文（先頭 `SUMMARY_MAX` = 20,000 字まで）を子プロセスに渡す。20,000 字で切るのは、argv 1 つの上限
    （131,072 バイト）を超えるとフックが `E2BIG` で落ちるため（reviewer の指摘）
  - 子プロセスは `--play --summarize <本文>` で起こし（`child_args()`・`run_child()`）、`summarize()` で
    `claude -p --model sonnet --setting-sources "" --tools "" --no-session-persistence` を同じプロセスグループのまま起こす。
    時間切れ 30 秒・終了コードが 0 でない・出力が空・起こせないときは `clip()` した文を読む。要約は `to_speech()` を通す
  - 子プロセスが読む文を `LOCK` を取って `check.record()` してから鳴らす。要約するときはフックでは記録しない
  - `summary` コマンド。環境変数が決めているときは、その旨を 1 行添える
  - `demo()`: 切り替えの組み合わせ、要約するかの分かれ目、偽の `claude` での要約・失敗・時間切れ・`claude` が無いとき、
    子プロセスへの振り分け
- `src/ccspk/cli.py`: `summary` を足した
- `docs/UsersGuide.md`: 「1.6 長い返答を要約して読む」「3.6 ccspk summary」を足し、後ろの節を繰り下げた。
  最初の音が 5〜6 秒遅れること、1 回 1〜1.5 セントかかることを書いた
- `docs/Developer.md`: 動き方・流れ・子プロセス・整形の表・定数・点検の記録・自己テストを今の動きに合わせた
- `README.md`・`CLAUDE.md`: サブコマンドの並びに `summary`。`CLAUDE.md` のフックを手で動かすときの注意に、
  要約が入っていればどのイベントでも長い文で本物の `claude -p` が走ることを足した

## 確かめたこと

- `uv run ccspk test` が通る
- reviewer: 分かれ目を `>=` にする、環境変数の優先を逆にする、終了コードを見ない、要約に `to_speech()` を通さない、
  時間の上限を外す、`OSError` を捕まえない、子プロセスへの振り分けを壊す、のどれでも demo が落ちる（壊したコピーで実測）
- verifier（`archives/agents/TODO-037/verify.sh`、一時の XDG・偽の `pw-play`・偽の `claude`）:
  切では `--summarize` が付かず Sonnet を呼ばない。入では 1 回呼び、`spoken.txt` に整えた要約が残る。
  MessageDisplay → Stop で呼ぶのは合わせて 1 回。短い返答と `CCSPK_SUMMARY=0` では呼ばない。
  要約中の `ccspk stop` で python・claude・sleep のグループが空になり、記録もされない。
  `ccspk summary` の出力と終了コードが UsersGuide の例と一致
- 本物の `claude` で 1 回: 要約（206 字。`clip()` で文末まで延ばす範囲）が記録され、終わった後に `claude -p` は残らない

## 残ること

- 2 度読まない仕組み（`LAST`）は、要約するときは切る前の全文で比べる。MessageDisplay でつないだ文と Stop の
  `last_assistant_message` が後ろのほうで違うと、要約を 2 度起こしかける（Stop が前を止めて起こし直す）。
  本物の 2 つのイベントの全文が同じかは確かめていない
- demo は、`main()` が要約するときに `record()` を呼ばない分岐と、`claude -p` に `start_new_session` を付けないことまでは
  見ていない（verifier の実測で確かめた）
- 本物の返答で、最初の音までの遅れは測っていない（`claude -p` だけで 5〜6 秒）

## 分担の振り返り

- 各担当が見つけたこと
  - implementer: 時間切れのとき止まるのは `claude` 本体だけで、その子プロセスが残るかは未確認、と挙げた
  - reviewer: demo が本物の `claude` を起こしていたこと、とても長い文で `E2BIG` になること、demo が子プロセスへの
    振り分けを見ていないこと、環境変数の説明が settings.json の `env` とつながっていないこと。
    見直しでは、時間切れの例が上限を外しても落ちないこと（main が直した）
  - verifier: 食い違いは無かった。偽の `pw-play` だと PipeWire の確認で止まることに気づき、`PIPEWIRE_REMOTE` で飛ばした
- 見込みとの食い違い: 編成は見込みどおり。reviewer の指摘で implementer と reviewer が 2 回ずつになり、implementer の
  cache_creation（211,831）が main を上回った
- 次に同じ規模なら
  - 依頼に「demo で本物の外部コマンドを起こさない。`PATH` は一時ディレクトリだけにする」と書く。今回は reviewer が
    確かめる途中で本物を 1 回走らせた
  - 依頼に「argv で渡す文の長さの上限」のように、切る前の文を扱うようになったときの境界を最初から書く
  - demo で見る範囲（つなぎ目まで見るか）を依頼で決めておく。reviewer の指摘で 2 回目の直しが要った
