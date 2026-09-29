"""TODO-050: claude -p 1 回あたりのトークン量の実測（9 回）。
使い方: cd /home/ytani/work/ccspk && uv run python archives/agents/TODO-050/measure.py
結果は同じ場所の result.json に書く。claude を直接呼ぶ（ccspk hook・check() は呼ばない）。"""
import json, os, subprocess, tempfile, pathlib, datetime
from ccspk import hook, check

HERE = pathlib.Path(__file__).parent

def ja(topic, items, n):
    """日本語 Markdown の返答。見出し・箇条書き・コードブロックを含む。n 節ぶん。"""
    out = [f"# {topic}の調査結果\n"]
    for i in range(n):
        it = items[i % len(items)]
        out.append(f"## {i+1}. {it}について\n")
        out.append(f"{topic}の{it}を確認した。現状では処理の流れが複数のファイルにまたがっており、"
                   f"変更の影響範囲を把握しにくい。まず呼び出し元を洗い出し、次に{it}の前提になっている"
                   "設定値と戻り値の扱いを整理した。結果として、二重に書かれていた条件分岐を一か所にまとめられる見込みである。\n")
        out.append(f"- {it}の入力は文字列で、空の場合は何もせず戻る\n- 失敗したときは例外を握りつぶさず、ログに残してから続ける\n"
                   f"- {topic}に関する既存のテストは通るが、境界の値を試すものが足りない\n")
        out.append(f"```python\ndef handle_{i}(x):\n    if not x:\n        return None\n    return x.strip()\n```\n")
    return "\n".join(out)

JA = [ja("キャッシュ機構", ["読み込み", "書き込み", "失効", "統計", "設定"], 6),
      ja("認証まわり", ["ログイン", "トークン更新", "権限確認", "監査ログ"], 7),
      ja("ビルド手順", ["依存関係", "テスト実行", "成果物", "版番号", "配布", "掃除"], 8)]

EN = [
 "I looked at the retry logic in the upload client. It currently retries every failed request three times with a fixed one second delay, which hammers the server when it is already overloaded. I replaced the fixed delay with exponential backoff and added a small random jitter so that many clients do not retry at the same moment. The change is limited to the send function and its tests. All existing tests still pass, and I added two new ones that cover the timeout path and the case where the server answers with a 503 status. One thing to decide is whether the maximum delay should be configurable.",
 "The build was failing because the lock file and the manifest disagreed about the version of the parser library. The manifest asked for anything above 2.0, while the lock file pinned 1.9.4 from an older resolution. I regenerated the lock file, checked that the parser tests pass with 2.3.1, and updated the changelog. I also noticed that the continuous integration cache key does not include the lock file, so stale dependencies can survive between runs. That is a separate problem, so I left it alone and only noted it here. Let me know if you want it handled in the same change or in a follow up.",
 "Here is a summary of the review. The new configuration loader reads the file once at startup and keeps the result in a module level dictionary, which is simple and fast. However, reloading the configuration at runtime is not possible without restarting the process. The error messages are clear, but they do not mention which file was being read. I suggest adding the path to every message and writing a short test that feeds a malformed file to the loader. Apart from that, the naming is consistent, the functions are small, and the documentation matches the behavior. I would approve this after the two small fixes."]

def words(n):
    base = [("燐光", "リンコウ", "淡い燐光が漂う。"), ("黒鉄", "クロガネ", "黒鉄の扉を開けた。"), ("雲丹", "ウニ", "雲丹の握りを食べた。"),
            ("生憎", "ショウジョウ", "生憎の雨だった。"), ("兎角", "トカク", "兎角この世は住みにくい。"), ("凡例", "ボンレイ", "凡例を見る。"),
            ("靄", "アイ", "朝の靄が晴れた。"), ("蟠り", "ワダカマリ", "蟠りが解けた。"), ("俯瞰", "フカン", "全体を俯瞰する。"),
            ("暫定", "ザンテイ", "暫定の版を出す。")]
    ws = []
    for i in range(n):
        w, k, s = base[i % 10]
        w2 = w if i < 10 else f"{w}{i}"
        ws.append(f"{w2}\t{k}\t{s}\n")
    return "".join(ws)

RUNS = [("要約", hook.SUMMARY_PROMPT, "sonnet", f"<reply>\n{t}\n</reply>", f"{len(t)}字") for t in JA] + \
       [("翻訳", hook.TRANSLATE_PROMPT, "sonnet", f"<reply>\n{t[:hook.TRANSLATE_MAX]}\n</reply>", f"{len(t[:hook.TRANSLATE_MAX])}字") for t in EN] + \
       [("点検", check.PROMPT, "opus", words(n), f"{n}単語") for n in (10, 20, 30)]

if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    res = []
    for kind, prompt, model, inp, size in RUNS:
        p = subprocess.run(["claude", "-p", "--model", model, "--setting-sources", "", "--tools", "",
                            "--no-session-persistence", prompt, "--output-format", "json"],
                           input=inp, capture_output=True, text=True, timeout=300, cwd=tmp,
                           env={**os.environ, "CCSPK_SPEAK": "0"})
        try:
            j = json.loads(p.stdout)
            res.append(dict(kind=kind, size=size, usage=j.get("usage"), cost=j.get("total_cost_usd"),
                            sec=j["duration_ms"] / 1000, rc=p.returncode))
        except Exception:
            res.append(dict(kind=kind, size=size, rc=p.returncode, out=p.stdout[:500], err=p.stderr[:500]))
        print(res[-1], flush=True)
    (HERE / "result.json").write_text(json.dumps(dict(at=datetime.datetime.now().isoformat(), runs=res), ensure_ascii=False, indent=1))
