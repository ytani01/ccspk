# TODO-046 レビュー（reviewer）

対象: 未コミットの `git diff`（`src/ccspk/hook.py`・`cli.py`・`docs/UsersGuide.md`・`docs/Developer.md`・README.md・CLAUDE.md・TODO.md）。
`uv run ccspk test` は通った（ok ×3）。本物の `claude -p` は呼んでいない。英文の見分けは `XDG_*` を一時ディレクトリに向けて
`prepare()` に値を渡して測った。壊すと落ちるかは、`src/` を一時ディレクトリへ写して書き換え、`demo()` を走らせて確かめた（リポジトリは触っていない）。

## 要修正

### 1. 英文の返答でも、コードブロック・`TODO-NNN`・`→`・範囲の `~` があると訳されない

- 場所: `src/ccspk/hook.py:255-257`（`english()`）、`:260-269`（`prepare()`）
- 内容: `english()` は `tidy()` の後の文を見るが、`tidy()` 自身が日本語を差し込む（コードブロック →「コード省略。」、
  `TODO-046` →「TODOゼロヨンロク」、`→`・`〜`・数字に挟まれた `~` →「から」）。そのため、英文の返答でもこれらを含むと
  かな・漢字があるとみなされ、訳さずに英文のまま読む。Claude の英文の返答はコードブロックを含むことが多いので、使う場面の
  かなりの部分で効かない見込み（頻度は未確認）
- 根拠（実測。`CCSPK_SUMMARY=0`、translate を入にして `prepare()` の印を見た）:

  | 入力 | `tidy()` の結果 | 印 |
  |---|---|---|
  | `Fixed the bug:\n```py\nx=1\n```\nAll tests pass.` | `Fixed the bug: コード省略。 All tests pass.` | `None` |
  | `Updated TODO-046. Tests pass.` | `Updated TODOゼロヨンロク. Tests pass.` | `None` |
  | `Ran 3 → 5 tests.` | `Ran 3から5 tests.` | `None` |
  | `Steps 1~3 done.` | `Steps 1から3 done.` | `None` |

- 補足: 仕様（TODO.md）は「整えた文に…1 字も無ければ」と書いているので、字面どおりではある。`demo()` の
  `prepare("```\nonly code\n```") == ("コード省略。", None)`（`hook.py:733`）はコードだけの返答を訳さないことを確かめているが、
  英文とコードブロックが混ざった返答は例に無い。**仕様の意図（英文の返答を訳す）と合っているかは利用者の判断が要る。**
  このままにするなら、UsersGuide の 1.8・3.2・3.8 に「コードブロックなどを含む英文は訳さない」ことを書かないと、利用者から見て
  「英文なのに訳されない」になる

## 検討

### 2. 印から指示を引く `PROMPTS` を入れ替えても `demo()` が落ちない

- 場所: `src/ccspk/hook.py:101`（`PROMPTS`）、`:299`（`play_rewritten()` の `rewrite(text, PROMPTS[flag])`）
- 内容: 次の 2 つに書き換えても `demo()` は通った（実測）。翻訳させたいのに要約の指示を渡す、という取り違えを捕まえられない
  - `PROMPTS = {SUMMARIZE: TRANSLATE_PROMPT, TRANSLATING: SUMMARY_PROMPT}`
  - `play_rewritten()` の `rewrite(text, PROMPTS[flag])` を `rewrite(text)`（常に要約の指示）
- 根拠: `run_child()` の例（`hook.py:741`）は `play_rewritten` を差し替えているので `PROMPTS[flag]` を通らない。`rewrite()` の例は
  指示を直接渡している。`PROMPTS[TRANSLATING] is TRANSLATE_PROMPT` のような 1 行か、偽の `claude` で `play_rewritten()` を
  通す例があれば落ちる
- ほかの書き換えは落ちた（実測）: `prepare()` の要約と翻訳の順の入れ替え、`TRANSLATE.exists()` を外す、
  `text[:TRANSLATE_MAX]` を `clip(text)` にする、`rewrite()` が `prompt` を無視する、`TRANSLATE_PROMPT` から `KANA_NOTE` を外す、
  `english()` からカタカナの範囲を外す、`run_child()` が `--summarize` しか見ない

### 3. 途中の文章・質問・コマンドだけの文でも、英字だけなら毎回 `claude -p` を呼ぶ

- 場所: `src/ccspk/hook.py:265`（`prepare()`）、`docs/UsersGuide.md:125-129`（1.8）・`:467-`（3.8）
- 内容: 要約は 180 字を超える文だけだったが、翻訳は字数を問わず、イベントも問わない。英語で作業するセッションでは、
  MessageDisplay の「Let me read the file.」のような途中の文章や AskUserQuestion の質問のたびに 1 セント前後かかり、最初の音が
  5 秒ほど遅れる。訳しても変わらない文も回る（実測: `` `git push origin develop` ``→`git push origin develop`、`123`、
  表の後の `Only a table` がどれも `--translate`）。文書は「英文の返答」「訳す返答では 1 回に 1 セント」と書いていて、
  途中の文章や質問も訳すことは読み取りにくい
- 根拠: `main()`（`hook.py:885`）はイベントを問わず `prepare()` を呼ぶ。仕様は字数・イベントを限っていないので境界線上。
  実害（料金と遅れの積み上がり）は未確認。報告だけ

### 4. `KANA_NOTE` の「読みが 1 つに決まる漢字」は、字ごとに読むと範囲が広がる

- 場所: `src/ccspk/hook.py:88-89`
- 内容: 前の文は「単語」で絞っているのに、後ろの文は「読みが 1 つに決まる**漢字**はそのまま漢字で」と字の単位になっている。
  漢字 1 字はたいてい読みが複数ある（「実行」の「行」など）ので、字面どおりに受け取ると「漢字のまま残す」の範囲が狭まり、
  ひらがなにする単語が増える向きに働く。「読みが 1 つに決まる単語は漢字のまま書いてください」なら前の文と単位が揃う
- 根拠: 静的に読んだだけ。本物の `claude -p` がどう受け取るかは未確認（verifier の実測で分かる）
- ほかは仕様どおり: 例（今日・辛い・行った・方）は TODO.md と同じ、全部をひらがなにさせない旨もある。`SUMMARY_PROMPT`・
  `TRANSLATE_PROMPT` の両方の終わりに付いている

### 5. `TRANSLATE_MAX = LIMIT * 3` は単語の途中で切る

- 場所: `src/ccspk/hook.py:78-79`、`:266`
- 内容: 540 字で機械的に切るので、単語や文の途中で切れる。`TRANSLATE_PROMPT` に「途中で切れている文は、切れたところまで訳して」
  とあるので扱いは考えてある。英日の字数の比（3 分の 1）が外れて訳が `LIMIT` に届かなくても、読む量が少し減るだけで
  壊れはしない。520〜540 字あたりの最後の文末で切れば途中の単語を渡さずに済むが、実害は未確認。報告だけ
- 判断そのもの（要約の `SUMMARY_MAX` と違い、料金と遅れを抑えるために訳した後の長さから逆算する）は妥当と読んだ

## 好みの範囲

### 6. `demo()` が印に `False` を渡している

- 場所: `src/ccspk/hook.py:754` `run_child(child_args("後。", False, os.pidfd_open(sleeper.pid)))`
- 内容: 印は `str | None` になったが、ここだけ旧来の `False` のまま。動きは同じ（`if flag`）。`None` に揃えると読み違えない

### 7. CLAUDE.md のタグのルールの文面

- 場所: `CLAUDE.md:29-31`
- 内容: `git tag v1.4.0` が具体の版なので、決まった版を付けると読める余地がある。「直前のタグ（`git describe --tags --abbrev=0`）から
  上げた版」のように、どこから数えるかが書いてあると迷わない。「版は `hatch-vcs` がタグから決めるので」は「タグを付ける理由」
  だが、続く minor・patch の決め方の理由のようにも読める。既存のタグ（v1.0.0〜v1.3.0）は注釈なしで、「注釈なし」と合っている

## 作り込みすぎ

- `hook.py:272`: yagni: `rewrite(text, prompt=SUMMARY_PROMPT)` の既定値を使うのは `demo()` だけ。既定値を外し、`demo()` で
  `SUMMARY_PROMPT` を渡す（好みの範囲）
- それ以外は無し。`PROMPTS` の辞書は印から指示を引く 1 か所で使い、`translate` コマンドは既存の `switch()` を使っている

net: -0 lines possible.（行数は減らない。上の 1 件は既定値を外すだけ）

## 問題なしの観点

- 振り分け: 要約が入っていて長い文なら英文でも `SUMMARIZE`（1 回）、短い英文は `TRANSLATING`、それ以外は `clip()`。仕様どおり（`demo()` と実測）
- 訳の失敗: `rewrite()` は失敗・時間切れ・空・`OSError` で `clip(元の英文)` を返し、知らせない。仕様どおり
- `ccspk queue` との組み合わせ: `child_args()` が `--after=` と印を両方付け、`run_child()` が両方読む。書き直しは待つ前に済ませる（`demo()` の `child_args("本文。", TRANSLATING, 7)` で確かめている）
- 記録: 翻訳のときもフックでは `check.record()` を呼ばず、子プロセスが訳を記録する。要約と同じ
- 子プロセスの止め方: `claude -p` は同じプロセスグループで、`stop_playing()` で止まる。変わっていない
- 切り替え: `TRANSLATE` の有無だけで決め、環境変数は無い。仕様どおり
- 文書とコード: Developer.md（動き方・3.1 の表・main の手順・3.2・定数と関数の表・4.x）、UsersGuide（1.8・2.3 の表・3.2・3.8）、README、CLAUDE.md、`cli.py` の docstring は、コードと突き合わせて食い違い無し（540 字・180 字・30 秒・`--translate`・`PROMPTS`・`KANA_NOTE`）。ただし上の 1・3 の書き足しは要る
- UsersGuide の見出しとアンカー: 3.8〜3.17 の見出しと、`#39-ccspk-test`・`#310-ccspk-dict`・`#312`・`#314`・`#315` のリンクは合っている。README・Developer.md から UsersGuide の 3.8 以降を指すリンクは無い
- 旧名（`summarize`・`play_summary`・`to_summarize`）の残り: archives を除き無し
- 範囲: 指示に無い変更は無し（TODO.md はチェックだけ、CLAUDE.md のタグのルールは利用者の指示）
- コメント: 「なぜ」が書いてある（`KANA_NOTE`・`TRANSLATE_MAX`）
