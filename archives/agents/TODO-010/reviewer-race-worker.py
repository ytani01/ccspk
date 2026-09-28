# 1 つのフックとして動く。鳴らさず、speak/stop を LOG に 1 行ずつ追記する
import importlib.util, os, sys, fcntl, time
spec = importlib.util.spec_from_file_location("sr", os.environ["SNAP"])
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
log = os.environ["LOG"]
def rec(s):
    with open(log, "a") as f: f.write(s + "\n")
sr.unusable = lambda: None
sr.stop_playing = lambda: rec("stop")
sr.speak = lambda t: (time.sleep(0.02), rec("speak " + t))  # Popen の間を模す
if os.environ.get("NOLOCK"): sr.fcntl.flock = lambda *a: None
t = float(os.environ["START"]); time.sleep(max(0, t - time.time())); sys.argv = ["x"]; sr.main()
