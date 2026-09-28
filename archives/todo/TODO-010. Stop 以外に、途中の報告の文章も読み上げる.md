# TODO-010. Stop 以外に、途中の報告の文章も読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実測・実装）+ claude-code-guide（Haiku 4.5）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 71,096 | 104,423 | 75% |
| reviewer | Opus 5.5 | high | 17,627 | 117,058 | 18% |
| verifier | Sonnet 5 | medium | 5,203 | 89,578 | 5% |
| claude-code-guide | Haiku 4.5 | 組み込み | 2,226 | 46,511 | 1% |
| 合計 |  |  | 96,152 | 357,570 | 概算 $10.1 |

- claude-code-guide は見込みに無かった。フックの仕様を公式の文書で確かめるために足した（組み込みの定義、Haiku は effort に対応しない）
- reviewer は、実測で分けて届くと分かって直した分と、指摘を反映した分を、同じ担当に続けて頼んだ
- main の分には、同じ時間に立てた TODO-011、辞書への語の追加（別のコミット）、hyprwhspr などの質問への返答も入っている

## きっかけ

読み上げは Stop で返答の最後の文章だけを読んでいた。ツールを呼ぶ前などに書く途中の報告も
読んでほしい、という利用者の依頼（2026-09-28）。


- [x] 実装の前に測る: `PreToolUse` と `PostToolUse` のどちらで、直前の文章が
      `transcript_path` のログに書かれているか（どちらでも書かれていない。下の実測）
- [x] `MessageDisplay` フックで、途中の文章を読み上げる（ログから拾う形は、測った結果やめた）
- [x] 同じ文章を 2 度読まない（Stop の `last_assistant_message` とも重ねない）
- [x] UsersGuide のフックの設定と、Developer.md の「動き方」「フックの仕組み」、README を直す

途中の文章を読むフックは無いので、ツールを呼ぶたびに起動するフックで代わりにする。

利用者と決めたこと（2026-09-28）: 新しい読み上げが始まったら、前の読み上げは
今までどおり止めてよい（途中の文章が続けて来ると、冒頭で切れることは受け入れる）。
子プロセスの扱いは今の `stop_playing()` のまま変えない。

実測（2026-09-28、Claude Code 2.1.283）:
- `PreToolUse`・`PostToolUse` の入力に文章は無い。`transcript_path` のログにも、そのツールの
  直前の文章はまだ書かれておらず、次のツールを呼ぶときに書かれている
- `MessageDisplay` というフックがある。入力は `message_id`・`index`・`delta`・`final`。
  短い文章は `index` 0・`final` true の 1 回で全文が来る。長い文章は分けて来た
  （48 字が `index` 0・`final` false、残りの 511 字が `index` 1・`final` true）。
  フックは並んで走り、`index` 1 のほうが先に、Stop と同じ時刻に届いた。つないだ 559 字は
  Stop の `last_assistant_message` と同じ長さ。途中の文章での起動は `PreToolUse` の 0.8 秒ほど後
- 実際に登録すると、途中の文章（目印の文章その 8）が読まれた。読まれない途中の文章もあった
- ただし起動しない文章がある。目印の文章 7 つのうち起動したのは 2 つ。起動しなかった文章は
  ログにも残っていなかった。起動する条件は分かっていない

利用者と決めたこと（2026-09-28、測った後）: `MessageDisplay` で読む。起動しない文章が
読まれないことは受け入れる。Stop は残し、同じ文章を 2 度読まない。
reviewer の指摘を受けて決めたこと（2026-09-28）: 同じ文を読まないのは、読んでから 5 秒のうちだけ。
整えると空になる途中の文章では、前の再生を止めない。そろわないまま残った分は 10 分で消す。

## やったこと

- 測定用のフックを `.claude/settings.local.json` に一時的に入れて、`PreToolUse`・`PostToolUse`・
  `MessageDisplay`・`Stop` の入力と時刻を記録した（上の実測）。測り終えて外した
- `hooks/speak-response.py` を `MessageDisplay` でも動くようにした。分けて届く分を
  `claude-tts.parts/` に置き、最後の分と前の分がそろったらつないで読む（`assemble()`）
- フックが並んで走るので、分を置く所から読み始めるまでを `claude-tts.lock`（`fcntl.flock`）で 1 つずつ通す
- 読んでから 5 秒のうちに同じ文が来たら読まない（`claude-tts.last`）。返答の最後の文章が
  `MessageDisplay` と `Stop` の両方から来るため
- 整えると空になる途中の文章では前の再生を止めない。そろわないまま 10 分たった分は消す
- `demo()` に `assemble()` の assert を足した
- README・UsersGuide（フックの設定例に `MessageDisplay`）・Developer.md を直した
- 利用者の依頼で `~/.claude/settings.json` に `MessageDisplay` フックを足した（dotfiles-claude の `3c1f693`）

## 確かめたこと

- 利用者が、実際のセッションで途中の文章（目印の文章その 8）が読まれたのを聞いた。
  読まれない途中の文章もあった（`MessageDisplay` が起動しない。条件は分かっていない）
- reviewer が 2 回見た。1 回目は要修正 3 件（Developer.md とコードの食い違い）と検討 7 件、
  2 回目は 0 件。`assemble()` をわざと壊すと `--test` が落ちることを確かめた
  （[1 回目](../agents/TODO-010/reviewer-report.md)、[2 回目](../agents/TODO-010/reviewer-report-2.md)）
- verifier が一時ディレクトリで、同時に 3 つ起動して 1 回だけ読む（3 回）、5 秒のうちは読まず
  過ぎたら読む、表だけの途中の文章で止めない、`agent_id` で読まない、古い分を消す、を確かめた
  （[報告](../agents/TODO-010/verifier-report.md)）
- LOCK を外しても、reviewer の試験では 3 回とも同じ結果だった。LOCK が要ることは試験では示せていない

## 残ること

- `MessageDisplay` が起動しない途中の文章があり、その条件は分かっていない
- TODO-011 で、フックを `claudecodespeak hook` に移す

## 分担の振り返り

- main の実測で、「分けて届く」「後ろの分が先に届く」を見つけたのは、実装した後に最後の返答の
  入力を記録したときだった。最初の実測で長い文章を 1 つ混ぜていれば、実装を 1 回でやり直さずに済んだ
- reviewer は 1 回目で文書の食い違い 3 件と、LAST がターンをまたぐ・空の途中の文章で止める・
  分が残る、の 3 つの判断事項を見つけた。どれも利用者に聞いて直す形になった
- verifier は食い違いを見つけなかった。辞書の変更を範囲外として挙げた（別のコミットで済んでいた）
- claude-code-guide は `MessageDisplay` の名前を挙げたが、中身は推測だった。実測で確かめる前提なら、
  次は聞かずに測定用のフックで総当たりしたほうが早い
- 見込みとの差は、claude-code-guide を足したことと、reviewer が 2 回になったこと。
  main の料金が 75% と大きいのは、実測を main でやったことと、同じ時間にほかの依頼を受けたため
- 次にフックの入力を測る項目では、実装の前に「短い文・長い文・続けて来る文」を測定用のフックで
  記録し、入力の形が固まってから reviewer に回す
