# TODO-007. 開発者用の文書 Developer.md を作る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（下書き）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（下書き）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 12,384 | 21,605 | 56% |
| reviewer | Opus 5.5 | high | 4,066 | 58,085 | 31% |
| verifier | Sonnet 5 | medium | 1,683 | 31,348 | 13% |
| 合計 |  |  | 18,133 | 111,038 | 概算 $1.6 |

- subagents のログは少なめに出る（todo-workflow skill）
- 見出しの `docs/Developer.md` は `/` がファイル名に使えないので、決着のときに
  `Developer.md` に縮めた

## きっかけ

利用者から、開発者用の文書を `docs/Developer.md` に作るよう頼まれた（2026-09-28）。

利用者と決めたこと: 書くのはフックの仕組みと、テストと動作の確かめ方。
開発の進め方（TODO.md・archives）と、これまでの設計判断のまとめは書かない。
README・UsersGuide と同じことを書く所は、どちらかへの案内で済ませる。

## やったこと

- `docs/Developer.md` を足した
  - フックの仕組み: `main()` の 3 つの起動のされ方と Stop フックとしての順、
    `--play` の子プロセスと `play()` の合成・再生の分担、`stop_playing()`、
    `unusable()`、`PIDFILE`・`UNUSABLE` の場所、整形と分割の関数、定数の意味
  - テストと動作の確かめ方: `--test`、一時ディレクトリで Stop を手で再現する
    手順（使える / `pw-play` 無し）、`--play` を直接起こす切り分け、最初の音まで
    の時間の測り方（一時ディレクトリで、子プロセスのグループの `pw-play` を
    60 秒まで待つ）
- README の「ファイル」の表に `docs/Developer.md` の行を足した

## 確かめたこと

詳しくは [archives/agents/TODO-007/](../agents/TODO-007/README.md)。

- reviewer: 要修正 2 件（`PATH` を空にすると mise の shim の python3 が落ちる、
  測り方のループに上限が無い）と、検討 7 件、好みの範囲 2 件。測り方が本物の
  `$XDG_RUNTIME_DIR` を使い、鳴っている読み上げを止めてしまう点も含め、すべて直した。
  README・UsersGuide と重なる数字と説明は案内に置き換えた
- verifier: 直した後の 6 項目（`--test`、手での再現 2 つ、`--play`、測り方、
  bash へのコピーと貼り付け）がすべて文書どおり。最初の音まで 0.74 秒。
  本物の `claude-tts.unusable` と `claude-tts.pid` は変わっていない

## 分担の振り返り

- reviewer は、main が試さずに書いた手順の欠陥（mise の shim、上限の無い
  ループ、本物のファイルを使う測り方）を実測とコードから見つけた。verifier は、
  直した後の手順で食い違いを見つけなかった
- 見込みとの食い違いは無い
- 次に手順を含む文書を書くときは、main が下書きの時点で各ブロックを 1 回
  走らせてから reviewer に回す。今回の要修正 2 件はそれで防げ、reviewer は
  記述とコードの突き合わせに絞れた
