# TODO-030 verifier report

スクリプト: archives/agents/TODO-030/verify.sh（項目 2〜4。作業ツリーの src は変更していない）

## 1. uv run ccspk test
通った。終了コード 0（出力末尾 `ok` `ok`）。

## 2. UsersGuide.md の例と chunks(to_speech(...)) （食い違いあり）
入力はどれも 1 文だけの短い文。

    '同じ reviewer に見てもらう。' -> ['同じreviewer', 'に見てもらう。']
    'Claude Code を使う。' -> ['Claude Code', 'を使う。']
    '手順 1 に進む。' -> ['手順 1に進む。']
    '全部で 180 字です。' -> ['全部で 180字です。']

- `Claude Code` は残る: 一致
- `手順 1` は残る: 一致
- `180 字` → `180字`: 一致
- **食い違い**: `同じ reviewer に` は文字列としては `同じreviewerに` にならず、
  `['同じreviewer', 'に見てもらう。']` の 2 塊になる。split_first がスペースで
  切った後に squeeze するため、塊をまたぐスペースは詰めようがなく、塊の境目に
  なる（スペースそのものは消える）。UsersGuide の「`同じ reviewer に` → `同じreviewerに`」を
  「1 つの文字列になる」と読むと合わない。「スペースが無くなる」と読めば合う。
  どちらの意図か、実害の有無は未確認。判断は管理者。
  （hook.py の demo() の長い文では 1 塊 `同じreviewerに見てもらう。` になる。）

## 3. dict kana（同じ reviewer に見てもらう。）
- 詰める前（原文）: `オナジ'、レビュウタ'ントウ、ニ'/ミ'テ/モラウ'`（「、」が 2 つ）
- 詰めた文字列 `同じreviewerに見てもらう。`: `オナジ'/レビュウタ'ントウニ/ミ'テ/モラウ'`（「、」なし）
- chunks の結果 `['同じreviewer', 'に見てもらう。']` は 2 塊で合成される。
  塊の間は別々の合成なので、「、」の間は入らない。塊ごとの kana は今回は取っていない
  （見えるのは合成の継ぎ目で、kana では確かめられない）。

## 4. kana.md「詰めた後」6 行
6 行とも、squeeze の結果を dict kana に通した出力が、kana.md の列と文字単位で一致（OK x6）。

## 変更ファイル
git status: M TODO.md, M docs/UsersGuide.md, M src/ccspk/hook.py, ?? archives/agents/TODO-030/。
hook.py は squeeze 追加と chunks の変更、demo() の追加だけ。UsersGuide.md は「記号と数字」に 1 箇条。
指示の範囲と合っている（TODO.md は内容を見ていない）。

## 確かめられなかったこと
- 項目 2 の食い違いが意図どおりか（上記）
