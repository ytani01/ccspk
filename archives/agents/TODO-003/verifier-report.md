# verifier の報告（TODO-003）

対象: `git diff`（hooks/speak-response.py、README.md、TODO.md）。
本体は直していない（scratch にコピーして壊した）。

## 1. `python3 hooks/speak-response.py --test`

```
$ python3 hooks/speak-response.py --test
ok
exit=0
```

仕様どおり。

## 2. 壊すと落ちるか

scratch（`/tmp/claude-649/.../scratchpad/`）に本体をコピーし、1 か所ずつ変更して `--test` を実行。
3 つとも `AssertionError` で落ちた（本体は無傷）。

- (a) `CUT_MIN = 9`: `assert split_first(a * 7 + "、いう。") == [a * 7 + "、", "いう。"]` で `AssertionError`
- (b) `SPACE_WITHIN = 31`: `assert split_first(a * 10 + " " + a * 19 + "、いう。") == [a * 10, a * 19 + "、いう。"]` で `AssertionError`
- (c) CUT から「：」を消す: `assert split_first(a * 9 + d + "いう。") == [a * 9 + d, "いう。"], d` で `AssertionError: ：`

## 3. 最初の音まで（`GAP=15`、3 回ずつ）

```
$ GAP=15 python3 archives/agents/TODO-003/measure.py comma 3
1 回目: 最初の音まで 1.30 秒
2 回目: 最初の音まで 1.34 秒
3 回目: 最初の音まで 1.29 秒

$ GAP=15 python3 archives/agents/TODO-003/measure.py space 3
1 回目: 最初の音まで 1.01 秒
2 回目: 最初の音まで 2.48 秒
3 回目: 最初の音まで 1.60 秒
```

main の「直した後」（comma 1.62/1.31/1.33、space 1.21/2.52/1.35 秒）と同じ範囲に収まっている
（comma 1.29〜1.34 秒、space 1.01〜2.48 秒）。値の並び（2 回目が高くなる傾向）も一致。

## 4. 本物の Stop hook

`claude -p` でこの会話とは別に子プロセスを起こし、応答を返した直後から
PID ファイル（`/run/user/649/claude-tts.pid`）の更新とそのプロセスグループ内の
`pw-play` の出現をポーリングで待った。

```
pidfile appeared: PID=328835 at 4.31s
pw-play pid=330330 found at 6.12s
```

PID ファイルの番号が新しくなり、そのグループに `pw-play` が更新から約 1.8 秒
（起動全体からは 6.12 秒）で現れた。10 秒以内。仕様どおり。

（1 回目の試行は、`claude -p` の実行と手元の確認コマンドの発行の間に数秒かかり、
その間に短い文の再生が終わっていたため取れなかった。2 回目でコマンドを 1 つに
まとめて即座にポーリングし、上の値を得た。）

## 5. 再生中の差し替え

`hooks/speak-response.py PLAY` を直接呼ばず、hook 本体（`stop_playing` を含む
`main` の経路）に JSON を渡す形で、長い文（読点で切れる comma 相当）を送った 3 秒後に
短い文を送り、その 0.5 秒後に 1 回目のプロセスグループの残数を数えた。

```
pgid1: 332626
pgid2: 332653
group1 count 0.5s after replace: 0
group2 count: 1
```

1 回目のグループは 0 個（`stop_playing` が `os.killpg` で止めている）。仕様どおり。

## 6. 終わった後に子が残っていない

上のすべての測定・実行の後、5 秒以上待ってから確認。

```
$ pgrep -af 'spea[k]-response.py'
（出力なし）
$ pgrep -a pw-play
（出力なし）
```

`--play` の子も `pw-play` も残っていない。

## 変更ファイルの範囲

`git status` / `git diff` で見た変更:

- `hooks/speak-response.py`（CUT・CUT_MIN・SPACE_WITHIN・split_first・chunks・demo の追加）
- `README.md`（「返答の読み上げ」節の 1 文目の切り方の記述）
- `TODO.md`（TODO-003 のチェックが入った状態）
- `archives/agents/TODO-003/`（reviewer の報告、main の実測、measure.py。新規）

指示の範囲（本体は `hooks/speak-response.py` の CUT・CUT_MIN・SPACE_WITHIN・split_first・
chunks、README の該当節）と合っている。指示に無いファイルの変更は無い。

## 確かめられなかったこと・判断できなかったこと

- 項目 4 の「10 秒以内」は満たしたが、1 回しか安定して測れていない（1 回目は途中経過を
  取り損ねた）。仕様が「1 回」としているのでこれで足りるはずだが、値の揺れ（4.31 秒 →
  6.12 秒までの内訳）は 1 回分しか無い
- 継ぎ目の聞こえ方（抑揚など）は「見なくてよいもの」に該当するため確かめていない
- reviewer-report / reviewer-report-2 で「境界線上の判断」「実害は未確認」とされた項目
  （2 文目以降で切れる区切りがある場合の assert の網羅性、閉じ括弧＋句点、半角 (: の前の
  スペースなど）は、reviewer の報告のとおり境界線上の判断であり、verifier としても
  判断できない
