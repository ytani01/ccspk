"""語ごとに audio_query の kana を並べる。python3 kana.py < words.txt"""
import json, sys, urllib.parse, urllib.request
for w in (l.rstrip("\n") for l in sys.stdin):
    if not w: continue
    q = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:50021/audio_query?speaker=119&text=" + urllib.parse.quote(w), method="POST"), timeout=30))
    print(f"{w}\t{q['kana']}")
