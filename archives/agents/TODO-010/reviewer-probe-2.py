import importlib.util, io, json, os, sys, tempfile, time
os.environ["XDG_RUNTIME_DIR"] = tempfile.mkdtemp(); os.environ["CLAUDE_TTS_SPEAK"] = "1"
spec = importlib.util.spec_from_file_location("sr", sys.argv[1]); sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
calls = []
sr.unusable = lambda: None; sr.stop_playing = lambda: calls.append("stop"); sr.speak = lambda t: calls.append(("speak", t))
def run(p):
    calls.clear(); sys.argv = ["x"]; sys.stdin = io.StringIO(json.dumps(p)); sr.main(); return list(calls)
MD = lambda mid, **k: {"hook_event_name": "MessageDisplay", "message_id": mid, "index": 0, "final": True, **k}
print("MD read          ", run(MD("m1", delta="確認です。")))
print("Stop same <5s    ", run({"hook_event_name":"Stop","last_assistant_message":"確認です。"}))
t = time.time() - 6; os.utime(sr.LAST, (t, t))
print("Stop same >5s    ", run({"hook_event_name":"Stop","last_assistant_message":"確認です。"}))
t = time.time() - 4.9; os.utime(sr.LAST, (t, t))
print("Stop same 4.9s   ", run({"hook_event_name":"Stop","last_assistant_message":"確認です。"}))
print("MD table only    ", run(MD("m2", delta="| a | b |")))
print("MD url only      ", run(MD("m3", delta="https://example.com/x")))
print("Stop empty       ", run({"hook_event_name":"Stop","last_assistant_message":""}))
print("Stop table only  ", run({"hook_event_name":"Stop","last_assistant_message":"| a |"}))
print("parts left       ", sorted(p.name for p in sr.PARTS.iterdir()))
# 他のプロセスの分: 新しい分は残るか、600 秒を超えた分だけ消えるか
run({"hook_event_name":"MessageDisplay","message_id":"x","index":0,"final":False,"delta":"途中、"})
t = time.time() - 599; os.utime(sr.PARTS / "x.0", (t, t))
run(MD("y", delta="別。"))
print("599s part kept   ", (sr.PARTS / "x.0").exists())
t = time.time() - 601; os.utime(sr.PARTS / "x.0", (t, t))
run(MD("z", delta="別の二。"))
print("601s part gone   ", not (sr.PARTS / "x.0").exists())
