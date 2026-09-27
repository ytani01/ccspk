# TODO-006. 読み上げが使えない環境では、早々にあきらめて覚えておく

旧番号: dotfiles-claude（`~/.claude`）の TODO-010。このリポジトリに分けたときに付け替えた。

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 20,096 | 57,598 | 63% |
| reviewer | Opus 5.5 | high | 893 | 64,225 | 24% |
| verifier | Sonnet 5 | medium | 86 | 63,961 | 13% |
| 合計 |  |  | 21,075 | 185,784 | 概算 $2.6 |

- 項目は dotfiles-claude の TODO-014 のコミットで立てたので、始点のコミットが無い。
  着手した時刻から `--since '2026-09-28 08:01:50'` で集計した
- reviewer は同じ担当に再レビューを続けて頼んだ（1 行にまとめた）
- subagents のログは少なめに出る（todo-workflow skill）

## きっかけ

別のマシンや SSH のセッションでこの設定を使うと、Stop のたびに子プロセスを
起こして失敗していた。`pw-play` が無いときや、音の出力先が無いときでも、
合成までは走る。

利用者と次のように決めた（2026-09-28）。

- 使えないとみなすのは、コマンドが無い・エンジンが応答しない・音の出力先が
  無い、の 3 つすべて
- 覚えておくのは、どれもログアウトまで。`$XDG_RUNTIME_DIR` に置き、無い環境では
  `/tmp` に置く
- 戻すときは、覚えたファイルを消す。仕組みは足さない
- エンジンが一時的に止まっていたときも覚える。承知のうえ

着手してから、入れ方とフックの設定を README から `docs/UsersGuide.md` へ移すことも
この項目に含めた（利用者の指示）。

## やったこと

- `hooks/speak-response.py`
  - `unusable()` を足した。`pw-play` があるか、エンジンに TCP で接続できるか、
    PipeWire のソケット（`$PIPEWIRE_RUNTIME_DIR` か `$XDG_RUNTIME_DIR` の
    `pipewire-0`）に接続できるかを、この順に見て、だめなら理由を返す
  - `main()` で、`CLAUDE_TTS_SPEAK` を見た直後に、`UNUSABLE`
    （`$XDG_RUNTIME_DIR/claude-tts.unusable`、無ければ
    `/tmp/claude-tts-<uid>.unusable`）があれば即終わる。無ければ `unusable()` で
    確かめ、だめなら理由を書いて、子プロセスを起こさずに終わる
  - エンジンは HTTP で問い合わせず、接続だけ見る。当初は「合成中は HTTP の応答が
    待たされる」を理由にしたが、reviewer の実測では合成中も `/version` は 1 ms で
    返った。接続だけ見れば足りるので方法は変えず、コメントの理由を直した
  - `PIPEWIRE_REMOTE` があるときは PipeWire を確かめない。`[a,b]` のような形を
    取ることがあり、1 つのファイル名として扱うと、使えるのに使えないと覚えたため
    （reviewer の指摘）
  - `PIDFILE` と `UNUSABLE` のパスを `BASE` から作るようにまとめた
- `docs/UsersGuide.md` に「入れ方」の節（clone、エンジン、Claude Code のフック、
  止める、使えないと覚えたとき）を足した。README の「入れ方」「Claude Code に
  つなぐ」の中身はこちらへ移し、README には概要と案内だけを残した

## 確かめたこと

詳しくは [archives/agents/TODO-006/](../agents/TODO-006/README.md)。

- reviewer（2 回）: 要修正なし。検討 4 件のうち、コメントの理由、`PIPEWIRE_REMOTE`、
  UsersGuide の「unit ファイルはこのパスを前提」の誤りを直した。移す元から
  落ちた内容が無いこと、README のリンクが見出しと合うことも見た
- verifier: 10 ケースをすべて実測し、食い違いなし。使える / `pw-play` 無し /
  エンジンに接続できない / PipeWire 無し / `XDG_RUNTIME_DIR` 無し（`/tmp` に
  書く）/ ファイルがあるときは 0.04 秒で終わり中身も変えない / 消せば確かめ直す /
  `PIPEWIRE_REMOTE` 付き / `CLAUDE_TTS_SPEAK` 無し / `--test`。UsersGuide の手順が
  指すパス、`/version`、clone の URL、フックの command 文字列、`cat` と `rm` の
  手順も確かめた。エンジンの入れ直しは実行していない
- 本物の `/run/user/649/claude-tts.unusable` が残っていないことを main が確かめた

## 分担の振り返り

- reviewer は、main の前提（合成中は HTTP が待たされる）が誤りなことを実測で
  見つけ、`PIPEWIRE_REMOTE` の誤判定と、移した文書の誤りも見つけた。verifier は
  食い違いを見つけなかった
- 見込みとの食い違いは、途中で文書を移す作業が加わり、reviewer を 2 回にした
  こと。1 回目の報告を待ってから移したので、同じ担当に続けて頼めた
- 次に同じ規模なら同じ組み方でよいが、前提に置いた挙動（今回は HTTP の待ち）は、
  実装の前に main が 1 回測る。測っていれば reviewer の検討が 1 件減った
