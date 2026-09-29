"""TODO-036: 判定の仕方を比べる。正解付きの例（正しく見つけるべき 6、誤判定の 21、読みが難しいが正しい 4）を
claude -p に渡し、登録に回る行（parse と same を通ったもの）を数える。
  uv run python archives/agents/TODO-036/judge.py {sonnet|opus} {word|context}
"""

import json
import subprocess
import sys

from ccspk.check import PROMPT, parse, same
from ccspk.user_dict import query

# (表記, 登録前のエンジンの読み（None なら今のエンジンに聞く）, 出てきた文, 正しい読み（誤りでなければ None）)
CASES = [
    ("採番", None, "コミットごとに番号を採番する。", "サイバン"),
    ("TODO", "ティ'イオオディイオオ", "TODO.md に項目を足す。", "トゥードゥー"),
    ("CLAUDE", "シ'イエルエエユウディイイイ", "CLAUDE.md の注意を読む。", "クロード"),
    ("README", "ア'アルイイエエディイエムイイ", "README の特徴に書く。", "リードミー"),
    ("JSON", "ジェ'エエスオオエヌ", "JSON で標準出力に出す。", "ジェイソン"),
    ("文目", "アヤメ'", "2 文目も短く切る。", "ブンメ"),
    ("dict", None, "ccspk dict add で登録する。", None),
    ("auto", None, "ccspk dict auto で見直す。", None),
    ("Claude", None, "Claude に判定させる。", None),
    ("Code", None, "Claude Code の返答を読む。", None),
    ("XDG", None, "XDG STATE HOME を一時ディレクトリに向ける。", None),
    ("tr", None, "tr がマルチバイトを壊したので Python で比べ直す。", None),
    ("ok", None, "3 行とも ok が出た。", None),
    ("no-op", None, "余計な置き換えは no-op だった。", None),
    ("先頭", None, "特徴の先頭に 1 項目足す。", None),
    ("返答", None, "返答のたびに裏で動く。", None),
    ("手元", None, "合成は手元のエンジンで行う。", None),
    ("測定", None, "実装前の測定を記録する。", None),
    ("分岐", None, "分岐が変わるのでレビューを入れる。", None),
    ("条件", None, "起こす条件を関数に分ける。", None),
    ("扱い", None, "失敗の扱いを見る。", None),
    ("変数", None, "環境変数で切り替える。", None),
    ("背景", None, "決めたことを背景に書く。", None),
    ("正規", None, "正規表現で切り出す。", None),
    ("母音", None, "エンジンは長音を母音で書く。", None),
    ("長音", None, "エンジンは長音を母音で書く。", None),
    ("経緯", None, "直した経緯を報告に書く。", None),
    ("冪等", None, "何度流しても冪等になる。", None),
    ("閾値", None, "閾値を 64 KiB にする。", None),
    ("疎通", None, "エンジンとの疎通を確かめる。", None),
    ("突合", None, "文書と実装を突合する。", None),
]
CONTEXT = PROMPT.replace("各行は「表記<TAB>読み」。", "各行は「表記<TAB>読み<TAB>その単語が出てきた文」。文は読み方を決める手がかりです。")

model, mode = sys.argv[1], sys.argv[2]
kana = {s: k or query(s)["kana"] for s, k, _, _ in CASES}
lines = "".join(f"{s}\t{kana[s]}" + (f"\t{c}" if mode == "context" else "") + "\n" for s, _, c, _ in CASES)
p = subprocess.run(
    ["claude", "-p", "--model", model, "--setting-sources", "", "--tools", "", "--no-session-persistence",
     "--output-format", "json", CONTEXT if mode == "context" else PROMPT],
    input=lines, capture_output=True, text=True, timeout=600, cwd="/tmp",
)
out = json.loads(p.stdout)
table = {s: kana[s] for s, _, _, _ in CASES}
got = {s: r for s, r in parse(out["result"], table) if not same(query(r)["kana"], table[s])}
truth = {s: r for s, _, _, r in CASES if r}
hit = [s for s in truth if s in got and same(query(got[s])["kana"], query(truth[s])["kana"])]
false = [f"{s}→{r}" for s, r in got.items() if s not in truth]
print(f"{model} {mode}: 見つけた {len(hit)}/{len(truth)}（{' '.join(hit)}）、誤判定 {len(false)}（{' '.join(false)}）、"
      f"${out['total_cost_usd']:.3f}、{out['duration_ms'] / 1000:.1f} 秒")
print("  返答:", out["result"].replace("\n", " / "))
