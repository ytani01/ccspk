# verifier の報告（TODO-004）

対象: `git diff`（hooks/speak-response.py の EXTEND・clip）。本体は直していない
（scratch にコピーして壊した）。エンジンには 300 字を超える文を直接投げていない
（すべて hook 経由。hook 内の `to_speech` が渡す前に `clip` で縮める）。

## 1. `python3 hooks/speak-response.py --test`

```
$ python3 hooks/speak-response.py --test
ok
exit=0
```

仕様どおり。

## 2. 壊すと落ちるか

scratch に本体をコピーし、1 か所ずつ変更して `--test` を実行。2 つとも `AssertionError` で落ちた。

- (a) `search(window, LIMIT - 1)` を `LIMIT - 2` に:
  `assert clip(s) == s[:LIMIT]`（`s` は LIMIT-2 字目に句点があるケース）で `AssertionError`
- (b) `window = text[: LIMIT + EXTEND]` を `window = text`に:
  `assert clip(a * (LIMIT + EXTEND) + "。いう") == a * LIMIT  # それより後ろの文末は使わない` で `AssertionError`

## 3. 日本語（200 字目あたりに「。」がある 260 字ほどの本文）

本文: `"あ" * 199 + "。" + "い" * 60`（260 字、200 字目が句点）を hook に JSON で渡し、
子（`--play`）の `/proc/<pid>/cmdline` の最後の要素（読み上げる本文）を確認。

```
子の本文の長さ: 200
末尾5字: 'ああああ。'
240 字以下: True
```

文末（句点）で終わり、240 字以下。仕様どおり（180 字目から 240 字目までで最初の文末＝
200 字目まで延びた）。

## 4. 英語（句点の無い 1,000 字）

本文: 句点・読点を含まない英単語の繰り返しを 1,000 字にしたもの
（`the quick brown fox jumps over the lazy dog ...` を 1,000 字に切ったもの、`.` `、` `，` を含まない）。

安全装置として、hook 起動と並行して子の argv を 0.05 秒ごとに監視し、240 字を
超えたら即座にそのプロセスグループを kill するスレッドを立てて実行（発火しなかった）。

```
子の本文の長さ: 180
末尾: 'ck brown f'
killed: False
```

180 字ちょうどで切れている（文末・読点が無いので `clip` は `text[:LIMIT]` に落ちる）。仕様どおり。

エンジン（`run`、VOICEVOX ENGINE の実行体）の RSS を、鳴っている間 0.5 秒ごとに測った最大値:

```
max RSS: 839,800 KB = 0.80 GB
```

1.5 GB 未満。仕様どおり。

## 5. 終わった後

```
$ pgrep -af 'spea[k]-response.py'
（一致なし、rc=1）
$ pgrep -a pw-play
（一致なし、rc=1）
$ systemctl --user is-active voicevox-engine hyprwhspr
active
active
```

`--play` の子・`pw-play` は残っておらず、両サービスとも active。仕様どおり。

## 変更ファイルの範囲

`git diff` で見た変更は `hooks/speak-response.py` の `LIMIT` のコメント・`EXTEND`・`ENDS`・
`COMMAS`・`clip`・`sentences` の書き換え・`demo` の追加のみ。指示の範囲（EXTEND・clip）と合っている。
`TODO.md` は TODO-004 のチェックが入った状態。指示に無いファイルの変更は無い。

## 確かめられなかったこと・判断できなかったこと

- 特になし。5 項目とも実測でき、すべて仕様どおりだった。
