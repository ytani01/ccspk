import importlib.util, io, json, os, sys, tempfile
os.environ["XDG_RUNTIME_DIR"] = tempfile.mkdtemp()
os.environ["CLAUDE_TTS_SPEAK"] = "1"
spec = importlib.util.spec_from_file_location("sr", sys.argv[1])
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
calls = []
sr.unusable = lambda: None
sr.stop_playing = lambda: calls.append("stop")
sr.speak = lambda t: calls.append(("speak", t))
def run(p):
    calls.clear(); sys.argv = ["x"]; sys.stdin = io.StringIO(json.dumps(p)); sr.main(); return list(calls)
MD = lambda **k: {"hook_event_name": "MessageDisplay", **k}
print("doc example (no id)", run(MD(final=True, delta="確認です。")))
print("final=false idx0   ", run(MD(message_id="m1", index=0, final=False, delta="前半、")))
print("final idx1         ", run(MD(message_id="m1", index=1, final=True, delta="後半。")))
print("out of order: 1 fin", run(MD(message_id="m2", index=1, final=True, delta="後。")))
print("out of order: 0    ", run(MD(message_id="m2", index=0, final=False, delta="先、")))
print("single final       ", run(MD(message_id="m3", index=0, final=True, delta="確認です。")))
print("Stop same          ", run({"hook_event_name":"Stop","last_assistant_message":"確認です。"}))
print("next turn same     ", run({"hook_event_name":"Stop","last_assistant_message":"確認です。"}))
print("agent_id           ", run(MD(message_id="m4", index=0, final=True, agent_id="a", delta="x。")))
print("MD table only      ", run(MD(message_id="m5", index=0, final=True, delta="| a | b |")))
print("Stop empty         ", run({"hook_event_name":"Stop","last_assistant_message":""}))
print("index str          ", run(MD(message_id="m6", index="0", final=True, delta="y。")))
print("leftover files     ", sorted(p.name for p in sr.PARTS.iterdir()), sorted(p.name for p in sr.BASE.parent.iterdir()))
