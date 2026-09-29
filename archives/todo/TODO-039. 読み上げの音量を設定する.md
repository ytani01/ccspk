# TODO-039. 読み上げの音量を設定する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 50 | 11,415 | 65,870 | 1,627,300 | 64% |
| reviewer | Opus 5.5 | high | 34 | 2,583 | 55,976 | 679,270 | 28% |
| verifier | Sonnet 5.5 | medium | 16 | 328 | 30,871 | 179,240 | 8% |
| 合計 |  |  | 100 | 14,326 | 152,717 | 2,485,810 | 計 2,652,953 |

- 立ててから着手まで別の項目（TODO-041〜050）を挟んだので、`--since '2026-09-29 22:25:00'`（着手したセッションの始め）で集計した
- reviewer・verifier は定義（`~/.claude/agents/`）のモデルと effort のまま

## きっかけ

システムの音量とは別に、読み上げの音量だけを決めたい。

背景（2026-09-29 に利用者と決めた）:

- `pw-play --volume`（0〜1.0）を使う
- 見送った案: PipeWire のミキサー（pavucontrol など）でアプリごとの音量として調整する案（`pw-play -P` で
  `application.name` を付ける）。コマンドで変えたいので採らない。VOICEVOX の `volumeScale` は `--volume` と効果が
  ほぼ同じなので採らない
- 環境変数での上書きは付けない。`ccspk summary`（TODO-037）と違い、一時的に切り替えるものではないため

## やったこと

- `ccspk volume [音量]` を足した（`user_dict.py` の `volume_`、`cli.py`）。0〜1.0 を `click.FloatRange` で受け、
  `FloatRange` が通す nan は別に断る。`-0` は `abs()` で `0.0` にして残す。引数なしは今の値を表示する
- 値は `~/.config/ccspk/volume`（`VOLUME_FILE`）に残す。`volume()` が読み、無い・0〜1.0 の数でないときは 1.0
- `pw_play()` が `["pw-play", "--volume=…", "-"]` を作り、`hook.py` の `play()`（フックと `ccspk say`）と
  `dict add --speak` が使う。`play()` は話者と同じく初めに 1 回だけ読む
- `speaker` の書き込み（別のファイルに書いてから置き換える）を `write_config()` にまとめ、`volume` と共用にした
- `demo()` に、ファイルが無い・範囲の外・nan・数でないときの既定と、`pw_play()` の引数の例を足した
- `docs/UsersGuide.md` に「1.10 音量を変える」と「3.10 ccspk volume」を足し、3.10 以降の節の番号とアンカーをずらした。
  `docs/Developer.md`・`README.md`・`CLAUDE.md` にも書いた

## 確かめたこと

- `ccspk test` が通る。範囲の判定を外すと `ccspk test` が落ちる（verifier）
- 断る値（`1.5`・`abc`・`nan`・`inf`・`-0.1`）はどれも終了コード 2 で、ファイルは変わらない（verifier）
- `ccspk say` を 1.0 と 0.2 で鳴らし、`pw-play` の引数に `--volume=1.0`・`--volume=0.2` が付くことを `pgrep` で確かめた。
  指数表記（`1e-05`）も `pw-play` が受け付けた（verifier）
- UsersGuide のアンカーは 59 件すべて解決する（reviewer）

## 残ること

- `ccspk volume -0.1` は、範囲の誤りではなく `No such option '-0'.` で断られる（終了コード 2 なので文書とは合う）。
  負の数を断るのは同じなので、このままにした
- `volume_` の nan を断る分岐は `demo()` では確かめていない（CLI の分岐のため。verifier が手で確かめた）

## 分担の振り返り

- reviewer: `-0` が `-0.0` で残ること（直した）、負の数が option の誤りとして断られること、nan の分岐がテストに無いこと、
  指数表記を `pw-play` が読めるかが未確認なことを見つけた。番号ずらしの漏れは無かった
- verifier: 食い違いは、0.2 の 1 回目の `pgrep` で別のセッションの読み上げ（`--volume=1.0`）を拾ったことだけ。
  親プロセスで絞って測り直すと 0.2 だった。指数表記が通ることを実測した
- 見込みと実施は食い違わなかった
- 次に同じ規模（`ccspk speaker` と同じ形の設定のサブコマンド）をやるなら、同じ組み方でよい。verifier の依頼には、
  `pgrep` は自分の子プロセスに絞る（`ppid` で見る）ことを最初から書いておく。測り直しの分を減らせる
