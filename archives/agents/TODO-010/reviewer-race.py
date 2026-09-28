import json, os, random, subprocess, sys, tempfile
S = os.path.dirname(os.path.abspath(__file__))
def trial(nolock):
    d = tempfile.mkdtemp(); log = os.path.join(d, "log")
    env = {**os.environ, "SNAP": f"{S}/../../../hooks/speak-response.py", "LOG": log, "XDG_RUNTIME_DIR": d, "CLAUDE_TTS_SPEAK": "1"}
    if nolock: env["NOLOCK"] = "1"
    import time; env["START"] = str(time.time() + 1.0)
    parts = ["一つ目、", "二つ目、", "三つ目。"]
    ps = [dict(hook_event_name="MessageDisplay", message_id="m", index=i, final=(i == 2), delta=t) for i, t in enumerate(parts)]
    ps.append(dict(hook_event_name="Stop", last_assistant_message="".join(parts)))
    random.shuffle(ps)
    procs = [subprocess.Popen([sys.executable, f"{S}/reviewer-race-worker.py"], stdin=subprocess.PIPE, env=env, text=True) for _ in ps]
    for p, pl in zip(procs, ps): p.stdin.write(json.dumps(pl)); 
    for p in procs: p.stdin.close()
    for p in procs: p.wait()
    out = open(log).read().split("\n") if os.path.exists(log) else []
    left = sorted(os.listdir(os.path.join(d, "claude-tts.parts")))
    return [l for l in out if l.startswith("speak")], left
for nolock in (False, True):
    for _ in range(3):
        print("nolock" if nolock else "lock  ", *trial(nolock))
