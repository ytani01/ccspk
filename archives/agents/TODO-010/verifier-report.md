# TODO-010 verifier 報告

対象: `hooks/speak-response.py` の MessageDisplay 対応（未コミット）。
`docs/Developer.md` の「動き方」「フックの仕組み」「Stop を手で再現する」を読んだ上で、
すべて一時ディレクトリ（`XDG_RUNTIME_DIR=$tmp`、`PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u)`、
`CLAUDE_TTS_SPEAK=1`）で手動起動して確かめた。本物の `$XDG_RUNTIME_DIR` は使っていない。
JSON はすべて `printf '%s'` で渡した。

## 変更されたファイルと範囲

```
M README.md
M TODO.md
M docs/Developer.md
M docs/UsersGuide.md
M hooks/speak-response.py
M voicevox/user_dict.json
?? archives/agents/TODO-010/   ← このディレクトリ（今回の報告用に作成）
```

TODO-010 のチェック項目（実装、MessageDisplay 対応、二重読み上げ防止、文書更新）と
一致する。**`voicevox/user_dict.json` の変更（「空になる」の辞書エントリ追加）は
TODO-010 のチェック項目には明記が無い。** 差分の内容自体は「空になる」という語の
読みを直すもので、今回の変更に出てくる文言（UsersGuide の「空の途中の文章」など）に
関係しそうだが、それが TODO-010 の範囲内かどうかは判断できない（管理者の確認が要る）。

## 1. `python3 hooks/speak-response.py --test`

`ok` を出力。終了コード 0。

## 2. Developer.md「Stop を手で再現する」の Stop 例 + MessageDisplay の例

- Stop 例（`確認です。二つ目の文です。`）: `claude-tts.pid`（PID 43529）・
  `claude-tts.last`（中身 `確認です。二つ目の文です。`）・`claude-tts.lock` ができた。
- 続けて MessageDisplay 例（`message_id:"m1", index:0, final:true, delta:"途中の文章です。"`）を
  同じ一時ディレクトリへ渡すと、PID が 43529 → 43616 に変わり、`claude-tts.last` が
  `途中の文章です。` に更新され、`claude-tts.parts` ディレクトリもできた。
  文書どおり pid・last・lock・parts のすべてができることを確認した。

## 3. 同時到達（index 1 final・index 0 final=false・つないだ全文の Stop を `&` + `wait`）3 回

各回、同じ message_id の 3 つの入力（index1「後半です。」final、index0「前半です。\n\n」
final=false、Stop で「前半です。\n\n後半です。」）を `&` で同時起動し `wait`。

| 回 | 新しい PID | last の中身 | parts の残り | 同時に立った再生子プロセス数 |
|---|---|---|---|---|
| 1 | 43814 | `前半です。 後半です。` | なし | 1（43814 のみ） |
| 2 | 43898 | `前半です。 後半です。` | なし | 1（43898 のみ、新規） |
| 3 | 43983 | `前半です。 後半です。` | なし | 1（43983 のみ、新規） |

各回とも `to_speech` で整えた文が一致するため、最初に `LOCK` を取って `LAST` を書いた
1 プロセスだけが `speak()` を呼び、残り 2 つは `SAME_WITHIN` の一致判定で終わっている
（`assemble()` の完了と Stop の直接呼び出しの結果が同じ整形後の文字列に収束するため）。
狙いどおり、3 回とも「再生の子プロセスは 1 つだけ、last はつないだ文、parts は空」を満たした。

備考: 前の回で起こした子プロセス（合成・再生に数秒かかる）が次の回の `pgrep` 結果にも
残ることがあったが、各回で**新しく増えたのは 1 プロセスだけ**であることは PID の変化で
確認できている。

## 4. SAME_WITHIN

「確認です。」を渡して pid1=44353。すぐにもう一度渡すと pid2=44353（変わらず）。
`touch -d '-10 seconds' $tmp/claude-tts.last` の後にもう一度渡すと pid3=44396（変わった）。
文書どおりの挙動。

## 5. 表だけの途中の文章

長めの文（子プロセスが再生中になるよう長文）を Stop で読ませ、子プロセスが動いている間に
表だけの MessageDisplay（`| a | b |\n|---|---|\n| 1 | 2 |`）を渡すと、
`claude-tts.pid` は変わらず（pid_before = pid_after = 44555）、`kill -0 44555` が生きていることを
確認した（子プロセスは止まっていない）。
続けて同じ表だけの文章を **Stop** で渡すと、`claude-tts.pid` ファイルが消え、
`kill -0 44555` は失敗（プロセスが止まった）ことを確認した。
文書どおり「`Stop` が空のときは、今までどおり止める」に一致。

## 6. agent_id 付きの MessageDisplay

`agent_id:"sub1"` を付けて渡すと、一時ディレクトリに **何のファイルもできなかった**
（`find $tmp` の結果はディレクトリ自身のみ）。ロックファイルすら作られず、
`agent_id` があると即座に終わる実装（`main()` の早期 return）と一致。

## 7. 古い parts の掃除

`claude-tts.parts/old.0` を作って `touch -d '-11 minutes'`、`recent.0` を `touch -d '-5 minutes'` にし、
別の message_id（`newmsg`）の分（final=false）を渡すと、
- `old.0`（11 分前）は消えた
- `recent.0`（5 分前）は残った
- `newmsg.0` が新しく作られた（`final=false` なのでまだ揃わず、削除されずに残る）

`PARTS_KEEP = 600` 秒（10 分）の境界どおりの挙動を確認した。

## 8. 片付け

使った一時ディレクトリ（`/tmp/tmp.zi7qcH2hGR`、`/tmp/tmp.PQZRcjbFzt`、`/tmp/tmp.qXhK44R59O`、
`/tmp/tmp.kaslxxdC3A`、`/tmp/tmp.TXBuvt8y6R`、`/tmp/tmp.sWKcsWDV9c`）は、確認後すべての
`claude-tts.pid` が消えている（子プロセスが自然に終わっていた）ことを見てから `\rm -rf` で削除した。
削除後に残っていた `speak-response.py --play` プロセス（PID 44958）は、本物のセッション
（このやり取り自体を読み上げている本番の Stop フック）のもので、私の一時ディレクトリを
使ったものではない（コマンドライン文字列がこのタスクへの言及そのものだった）。
そのため kill せずそのままにした。私が起こした一時ディレクトリ由来の子プロセスで
残っていたものは無かった。

## 確かめられなかったこと・判断が要ること

- `voicevox/user_dict.json` の変更が TODO-010 の範囲内かどうかは判断できない。
  チェック項目には明記が無く、範囲外の可能性がある（実害は未確認）。
- コードの設計や整形・分割の妥当性、音の聞こえ方は指示どおり見ていない（reviewer 済み、対象外）。
- 境界線上の判断（`voicevox/user_dict.json` の扱いなど）は報告のみで、直す・含めるの判断はしていない。
