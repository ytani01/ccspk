# TODO-013 verifier report

## 検証の実行

コードは変更されていない（文書のみの変更）ため、テストは実行していない
（依頼の「見なくてよいもの」に記載の通り）。

## git diff -- docs/Developer.md

`### 定数` の表に対する差分のみ。`PLAY` の説明を更新し、`MODULE`・
`PARTS_KEEP`・`SAME_WITHIN` の行を追加している。表以外の変更は無い。

## 1. 表の各行と hook.py（32〜62 行目）の突き合わせ

すべて一致。

- `LIMIT` = 180、コメント「読み上げるのはおよそここまで」— 一致
- `EXTEND` = 60、コメント「延ばすのはここまで」（メモリの話も表と本文双方にあり）— 一致
- `ENDS` = `。！？!?` — 一致
- `COMMAS` = `、，`、「半角の `,` は数字の中にも出るので入れない」— 一致
- `SPEAKER` = 119、「夜語トバリ（明るい）」— 一致
- `ENGINE` = `http://127.0.0.1:50021` — 一致
- `PLAY` = `--play`、「子プロセスの目印。`stop_playing()` は `MODULE` と合わせて見分ける」
  — hook.py 40 行目のコメント「合成と再生を受け持つ子プロセスの目印」と、
  41 行目の `MODULE` コメント「stop_playing() はこれで見分ける」を合わせた説明で、
  実装（`stop_playing()` 144 行目、後述）とも一致
- `MODULE` = `claudecodespeak.hook`、「子プロセスが `python -m` で起こすモジュール。
  `stop_playing()` の目印にもなる」— hook.py 41 行目のコメントと一致
- `CUT` = 正規表現、「1 文目を切る区切り」— 一致
- `CUT_MIN` = 8、「これより手前では切らない」— 一致
- `SPACE_WITHIN` = 30、「この字数までに `CUT` が無いときだけ、スペースで切る」— 一致
- `PARTS_KEEP` = 600、「そろわないまま残った MessageDisplay の分は、この秒数で消す」
  — hook.py 59 行目コメント「そろわないまま残った分は、この秒数で消す」、
  56〜58 行目の `PARTS` の説明（MessageDisplay の分を置く）と合わせて一致
- `SAME_WITHIN` = 5、「読んでからこの秒数のうちに同じ文が来たら読まない。
  長くすると、続けて同じ返答（「はい。」など）が来たときに黙ってしまう」
  — hook.py 60〜62 行目のコメントと一致（「MessageDisplay と Stop は 0.01 秒差で来た」
  という追加の経緯コメントは表に無いが、意味の食い違いではない）

## 2. 表に無い定数（パスの定数を除く）

無し。32〜62 行目にある定数のうち、パスの定数（RUNTIME, BASE, PIDFILE, UNUSABLE,
LAST, LOCK, PARTS）を除いた 13 個（LIMIT, EXTEND, ENDS, COMMAS, SPEAKER, ENGINE,
PLAY, MODULE, CUT, CUT_MIN, SPACE_WITHIN, PARTS_KEEP, SAME_WITHIN）は
すべて表に載っている。

## 3. PLAY・MODULE の説明と stop_playing() の実際の判定

`stop_playing()`（hook.py 137〜148 行目）:

```python
args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
if PLAY.encode() not in args or MODULE.encode() not in args:
    return
os.killpg(pid, signal.SIGTERM)
```

`PLAY not in args or MODULE not in args` で戻る、つまり **両方が cmdline に
あるときだけ SIGTERM を送る**。表の説明（PLAY: 「`MODULE` と合わせて見分ける」、
MODULE: 「`stop_playing()` の目印にもなる」）は、この「両方そろって初めて見分ける」
という判定と食い違わない。Developer.md 103〜109 行目の「前の再生を止める」の節
（「`/proc/<pid>/cmdline` に `--play` と `claudecodespeak.hook` があるときだけ送る」）
も同じ内容で、表・本文・実装の三者が一致している。

## 4. Developer.md の他の節との整合

- 「流れ」節（78 行目）「`stop_playing()` で前の再生を止める」— 表の説明と矛盾しない
- 「前の再生を止める」節（103〜109 行目）— 上記 3. の通り、表・実装と一致
- 他に `PARTS_KEEP` や `SAME_WITHIN` に触れている節は見当たらず、表の記述と
  食い違う箇所は無い

## 確かめられなかったこと・判断が要る点

- 無し。今回の対象（表と hook.py・`stop_playing()` の突き合わせ）はすべて
  一致を確認できた。境界線上の判断が必要な箇所も見当たらなかった。
