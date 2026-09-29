# TODO-036. 読み間違いを見つけて辞書に登録するのを自動にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Opus 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | implementer（Opus 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 99,166 | 220,603 | 57% |
| implementer | Opus 5.5 | medium | 10,048 | 250,856 | 17% |
| reviewer | Opus 5.5 | high | 14,666 | 370,954 | 21% |
| verifier | Sonnet 5.5 | medium | 5,798 | 222,351 | 5% |
| 合計 |  |  | 129,678 | 1,064,764 | 概算 $18.3 |

- implementer は定義のモデルが sonnet。設計が込み入る（子プロセス・ロック・mtime）ので Opus 5.5 に上書きした
- reviewer は 4 回、verifier は 3 回、同じ担当に続けて頼んだ（立て直していない）
- 集計は `--since '2026-09-29 15:53:00'`（TODO-037・TODO-038 を立てたやり取りも少し入っている）
- 表のほかに、`claude -p` の料金がかかった: main の測定（$0.11）と判定の比べ（`judge.py`、5 回で約 $0.08）、
  verifier の本物の `claude -p`（3 回で約 $0.04）、途中の版が本物のフックで動いた分（数回、未集計）

## きっかけ

読み間違える単語は、利用者が聞いて気づき、`ccspk dict add` で 1 つずつ登録していた。読み上げた文を記録し、
Claude に判定させて、登録までを自動にしたい（2026-09-29 に利用者と決めた）。

## やったこと

- 実装の前に測った（`archives/agents/TODO-036/main-measure.md`）。形態素解析は sudachipy + sudachidict_core の
  C 単位（複合語を 1 語にまとめる）を選んだ。英字は正規表現で切る（解析器は `README.md` やコミット ID を細かく割る）。
  漢字は名詞で 2 字以上に絞った（活用形と 1 字の漢字は文脈で読みが変わる）。点検の `claude -p` には
  `--setting-sources ""` を付け、利用者のフックと `CCSPK_SPEAK` を入れない（`--bare` は OAuth を読まない）
- `src/ccspk/check.py`（新規）: 読み上げた文を `~/.local/state/ccspk/spoken.txt` に追記し（64 KiB で後ろ半分を残す）、
  Stop のたびに新しい記録があれば、裏で点検を起こす。点検は単語を切り出し、点検済み・登録済みを除き、
  エンジンの読みと単語の前後 30 字を添えて `claude -p --model opus` に渡す。誤りとされた単語を登録し、
  `added.tsv` に残す。同時に 1 つだけ（`check.lock`）。失敗は `failed.txt` に書き、次の Stop が `systemMessage` で知らせる
- 登録の前に、Claude の読みもエンジンに通して発音で比べ（`same()`）、同じなら登録しない。エンジンは長音を
  母音で書き（先頭 → セントオ）、カタカナの「エイ」は字のとおり読む（ケイサン）ので、その違いを同じとみなす
- `src/ccspk/hook.py`: 読み上げる文を記録し、Stop で `check.after_stop()` を呼ぶ（2 行ずつ）
- `src/ccspk/user_dict.py`: `dict add` の中身を `register()` に切り出した。`ccspk dict auto [--remove]` を足した。
  手で `dict add`・`dict remove` した単語は `added.tsv` から外す。状態のディレクトリ（`STATE`・`ADDED`）もここに置く
- `ccspk test` に `check.demo()` を足した
- 文書: `README.md`（特徴の先頭、外に送るもの）、`docs/UsersGuide.md`（2.3 読み間違いの自動の点検、3.12 dict auto）、
  `docs/Developer.md`（3.8 自動の点検ほか）、`CLAUDE.md`（手でフックを動かすときの `XDG_STATE_HOME` と料金）
- 途中で判定を Sonnet・単語だけから Opus・文ありに変えた（下の「確かめたこと」）

## 確かめたこと

- reviewer（4 回）: `checked.txt` が無いと毎回失敗を出す条件の誤り、同じ読みの登録、登録の失敗で `claude -p` を
  呼び直すこと、発音の比べ方の置き換えをエンジン側にもかけていたこと、入力が 8 倍に膨らむこと、を見つけて直した
- verifier（3 回）: 偽の `claude` と一時ディレクトリでの通し（登録・失敗の知らせ・`dict auto`・`CCSPK_SPEAK=0`）、
  壊すと `ccspk test` が落ちるか、本物の `claude -p` の返答が読めるか。最後は全部一致
- 本物のフックで動いた途中の版（Sonnet・単語だけ）が、本物の辞書に 22 単語を登録し、ほぼ全部が誤りだった
  （エンジンと同じ発音の書き換え 18、`母音` → ボインイン・`tr` → トランスレート・`no-op` → ノーオペ）。
  利用者の了解を得て、`it` を残して消した
- 正解付きの 31 単語（正しく見つけるべき 6、誤判定の 21、読みが難しいが正しい 4。`judge.py`）で比べた:
  Sonnet・単語だけは 0/6（1 回）、Sonnet・文ありは 6/6 で誤判定 1（2 回とも）、Opus・文ありは 6/6 で誤判定 0（2 回とも）。
  利用者と決めて Opus・文ありにした。変えてからの本物の点検は、誤った登録を出していない

## 残ること

- 自動の点検だけを止める手段は無い（止めるのは `CCSPK_SPEAK` だけ）
- 点検の失敗が続くと（`claude` が無い、認証切れ）、返答のたびに `systemMessage` が出る
- 登録した読みに「エイ」が残ると、字のとおり「エ・イ」と読まれるおそれがある（辞書を書き換えるので未確認）
- `save()` に失敗した後、書き出す前にエンジンが起動し直すと、登録は消えても `dict auto` には出たままになる（未確認）
- `checked.txt` は上限なしで伸びる（単語は重ならないので伸びは遅い）
- `record()` の上限の `>` と `>=` の違いは `demo()` で見ていない

## 分担の振り返り

- implementer: 設計どおりに実装し、偽の `claude` で失敗の経路まで試した。`CHECKED` の mtime を点検の始めの
  `SPOKEN` の mtime に揃える点を自分で足した。判定の質（Claude が何を誤りとするか）は、偽の `claude` では見えなかった
- reviewer: 条件の誤り（`checked.txt` が無いとき）を実測で再現し、登録の失敗で料金がかかり直すこと、発音の比べ方の
  ずれ（経緯）、入力の膨らみ（8.2 倍）を見つけた。4 回とも直すべき指摘を出した
- verifier: 通しと壊し方を 3 回とも実測で返した。本物の辞書の差（`変数` のアクセント）を報告し、本物のフックの
  誤登録に気づくきっかけになった
- 見込みとの食い違い: 担当の組み方は見込みどおり。食い違ったのは回数で、判定の質を実装の前に測らなかったため、
  本物の辞書に誤登録が出てから測り直し、reviewer・verifier を 1 回ずつ余分に回した
- 次に同じ規模の項目をやるなら: **Claude の判定に頼る機能は、実装の前に正解付きの例で判定の質を測る**
  （今回は料金と時間だけを測り、判定の中身を「Claude に任せる」で済ませた）。本物のフックに入る変更は、
  このリポジトリの Stop フックが入れ直すので、レビューの前に本物で動き出すことを前提に、途中で本物の状態
  （`added.tsv`）を見る
