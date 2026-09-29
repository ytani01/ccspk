# TODO-054. 子プロセスの読み上げを止める方法を文書に書く

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5.5 / effort medium | main（文書）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 既定 | main（文書）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 既定 | 38 | 7,451 | 106,545 | 1,014,915 | 82% |
| verifier | Sonnet 5.5 | medium | 22 | 559 | 27,703 | 225,748 | 18% |
| 合計 |  |  | 60 | 8,010 | 134,248 | 1,240,663 | 計 1,382,981 |

- main は利用者が着手前に Opus 5.5 へ切り替えていた。effort は指定していない
- verifier は定義（`~/.claude/agents/verifier.md`）のまま。モデル sonnet、effort medium

## きっかけ

`~/.claude` の TODO-017 で、担当の返事を測る `claude -p` に `CCSPK_SPEAK=0` を環境変数で渡したのに、
子プロセスの読み上げが止まらなかった。子プロセスが `settings.json` の `env` で環境変数を上書きするためで、
これは Claude Code の仕様。`ccspk` の不具合ではない。文書に子プロセスでの止め方が無く、同じ間違いが起きうる。

立てた後、ccspk 自身の `claude -p`（`rewrite()`・点検）で読み上げが起きない理由を「環境変数で足りる」と書いていたのを、
「`--setting-sources ""` でフックが登録されないから。`CCSPK_SPEAK=0` は念のため」に直した。

## やったこと

- `docs/UsersGuide.md` の「1.3 読み上げを無効にする」に、子プロセスの読み上げだけを止めるには
  `--settings '{"env":{"CCSPK_SPEAK":"0"}}'` を使うこと、環境変数では止まらないことと、その理由を足した
- `docs/Developer.md` の `rewrite()` の説明（「3.2 子プロセス」）に、ccspk 自身の `claude -p` は `--setting-sources ""` で
  フックが登録されないので読み上げが起きないこと、`CCSPK_SPEAK=0` だけでは止まらないこと、点検（`check.py`）も同じことを足した

## 確かめたこと

verifier が本物の `claude -p` で実測した（報告は `archives/agents/TODO-054/verifier-report.md`）。

- `CCSPK_SPEAK=0 claude -p` の子プロセスでは `printenv CCSPK_SPEAK` が `1`
- `--settings '{"env":{"CCSPK_SPEAK":"0"}}'` を付けると `0`
- `--setting-sources ""` を付けると `--debug-file` の出力が `Registered 0 hooks` になり、SessionStart のフックが走らない。
  付けないと `Registered 3 hooks` で、フックが走る
- `docs/UsersGuide.md` のコマンド例の JSON は、実測したものと同じ

## 残ること

- `--allowedTools` のように複数の値を取るオプションを足すと、後ろに置いたプロンプトまで値として取り込まれ、
  `Error: Input must be provided...` で落ちる。文書の例は `--settings` だけなので問題ないが、足す人には落とし穴になる。
  文書には書いていない
- `--debug` はこの環境では何も出さず、`--debug-file` で見た。cwd が `/tmp` だったので、ccspk の Stop フックの行そのものは見ていない

## 分担の振り返り

- verifier は、書いた 3 つの主張がすべて実測と一致することを確かめた。あわせて、依頼したコマンドのうち
  `--allowedTools` と `--debug` の引数の順で落ちること、`--debug` が何も出さないことを見つけ、`--debug-file` に切り替えて測った
- 見込みとの食い違いは main のモデルだけ（利用者が Opus 5.5 に切り替えた）。担当の組み方は見込みどおり
- 次に同じ規模の項目なら、同じ組み方でよい。ただし依頼に書くコマンドは、main が 1 回走らせて通ることを見てから渡す。
  今回は引数の順の誤りで verifier が組み直すことになった
