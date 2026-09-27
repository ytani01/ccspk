"""readings.md の各語を to_speech に通してから audio_query の kana を取り、
「後」の列と突き合わせる。python3 check-readings.py"""
import importlib.util
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

spec = importlib.util.spec_from_file_location("speak_response", "/home/ytani/.claude/hooks/speak-response.py")
speak_response = importlib.util.module_from_spec(spec)
spec.loader.exec_module(speak_response)
to_speech = speak_response.to_speech

ROWS_RE = re.compile(r"^\| (.+?) \| (.+?) \| (.+?) \|$")


def kana(text):
    q = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:50021/audio_query?speaker=119&text=" + urllib.parse.quote(text),
        method="POST"), timeout=30))
    return q["kana"]


def main():
    path = Path(__file__).with_name("readings.md")
    ok = 0
    bad = []
    for line in path.read_text().splitlines():
        m = ROWS_RE.match(line)
        if not m or m.group(1) in ("語", "---"):
            continue
        word, before, after = m.groups()
        if set(word) == {"-"}:
            continue
        got = kana(to_speech(word))
        if got == after:
            ok += 1
        else:
            bad.append((word, after, got))
    print(f"一致: {ok} 件")
    for word, expected, got in bad:
        print(f"食い違い: {word!r}\n  期待(後): {expected}\n  実際     : {got}")


if __name__ == "__main__":
    main()
