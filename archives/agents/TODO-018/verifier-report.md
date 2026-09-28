# TODO-018 verifier report

## 1. `uv run claudecodespeak test`

通った。

```
$ uv run claudecodespeak test
ok
ok
EXIT:0
```

壊すと落ちるかの確認: `src/claudecodespeak/user_dict.py` の `HALF` の range を
`range(0xFF01, 0xFF5F)` → `range(0xFF02, 0xFF5F)` に一時的に変えて再実行。

```
$ uv run claudecodespeak test
ok
Traceback (most recent call last):
  ...
  File "/home/ytani/work/claudecodespeak/src/claudecodespeak/user_dict.py", line 99, in demo
    assert halfwidth("！／ｅｔｃ／ＴＯＤＯ－０１～") == "!/etc/TODO-01~"  # 範囲の両端も
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
EXIT:1
```

狙った assert（範囲の両端を確かめている行）で落ちた。その後ファイルを元に戻し、
`git diff --stat -- src/claudecodespeak/user_dict.py` で差分が変更前と同じ
（19 insertions, 3 deletions、意図した差分のまま）であることを確認し、
再度 `uv run claudecodespeak test` が通ることも確かめた。

## 2. `dict list` の表示

エンジン（VOICEVOX、`curl http://127.0.0.1:50021/version` → `"0.25.2"`）が
動いていたので実行できた。

```
$ .venv/bin/claudecodespeak dict list | rg -n '[！-～]' | wc -l
0
```

先頭 5 行:

```
cd5eef0a-5e1b-4c85-9985-bf59d70f6227  .md  ドットエムディー  4
67516aa0-9393-4f2d-ae3e-90905601600a  /  スラッシュ  2
b5b54622-a0dc-4d40-9312-a691f03dd138  /etc  スラッシュエトセ  6
50e54cae-ac40-40a5-86c3-cd0257267c30  /etc/  スラッシュエトセスラッシュ  9
5c48dfa4-6b02-4843-9ae5-3ca19ffc11a2  CLAUDE  クロード  1
```

一致。全角の英数字・記号（U+FF01〜U+FF5E）は 0 件。

## 3. `dict export` の書き出し

```
$ .venv/bin/claudecodespeak dict export <scratchpad>/exported_user_dict.json
$ diff <scratchpad>/exported_user_dict.json voicevox/user_dict.json
（差分なし、diff の終了コード 0）
$ rg -n '[！-～]' <scratchpad>/exported_user_dict.json | wc -l
0
```

一致。

## 4. `git diff voicevox/user_dict.json` の変わった行

全 27 か所の変更行を目視で確認した。すべて `"surface": "..."` の行で、
全角英数字・記号を半角に置き換えているだけ（例:
`"ｉｍｐｌｅｍｅｎｔｅｒ"` → `"implementer"`、`"／ｅｔｃ／"` → `"/etc/"`）。
`surface` 以外のキー（`pronunciation`・`yomi`・`priority` など）や、
単語の追加・削除は無い。一致。

## 変更ファイルと指示の範囲

`git status` は次のとおり。

```
 M TODO.md
 M src/claudecodespeak/user_dict.py
 M voicevox/user_dict.json
?? archives/agents/TODO-018/
```

- `src/claudecodespeak/user_dict.py`・`voicevox/user_dict.json` — 指示どおりの範囲（上記で確認済み）。
- `TODO.md` — TODO-018 の 6 項目すべてにチェックが付いている。うち
  「半角のままでは効かなかったら import で全角に戻す」は取り消し線付きで
  「測定で不要と分かった」と注記されており、実装ではなく判断の記録として
  妥当に見える（この判断自体の当否は verifier の範囲外）。
- `archives/agents/TODO-018/` には `reviewer-report.md` のみ存在（このファイルを追加）。

## docs/UsersGuide.md（TODO.md の項目にあるが diff には出てこない点）

TODO.md には「`docs/UsersGuide.md` に全角・半角の記述があれば合わせる」に
チェックが付いているが、`docs/UsersGuide.md` は git diff に出てこない
（変更されていない）。`rg '全角|半角' docs/UsersGuide.md` で見ると、該当箇所は
`say` の読み上げ整形（`~` や全角数字の扱い）についての既存の記述のみで、
辞書の `surface` 表示・書き出しに関する記述は見当たらなかった。つまり
「合わせるべき記述が無かったので変更しなかった」という状況と整合しているように
見えるが、これが正しい判断かどうかは境界線上で、verifier としては判断できない
（実害は未確認）。

## 確かめられなかったこと

- `dict import` の往復（依頼で対象外と指定されたため実行していない）。
- TODO.md の「測定で不要と分かった」という判断（import で全角に戻す必要が
  無いという結論）自体の妥当性は、依頼の範囲外として確かめていない。
