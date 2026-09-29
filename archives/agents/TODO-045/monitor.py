"""0.1 秒ごとに、環境変数 XDG_RUNTIME_DIR=$1 を持つ pw-play の (pgid, pid) を記録する。$2 秒で終わる。標準出力へ: 時刻 pgid pid 本数"""
import os, sys, time
tmp, dur = sys.argv[1].encode(), float(sys.argv[2])
t0 = time.time(); last = None
while time.time() - t0 < dur:
    cur = []
    for d in os.listdir("/proc"):
        if not d.isdigit(): continue
        try:
            if open(f"/proc/{d}/comm").read().strip() != "pw-play": continue
            if b"XDG_RUNTIME_DIR=" + tmp + b"\0" not in open(f"/proc/{d}/environ", "rb").read(): continue
            cur.append((os.getpgid(int(d)), int(d)))
        except OSError: pass
    cur.sort()
    if cur != last:
        print(f"{time.time()-t0:6.2f} n={len(cur)} {cur}", flush=True); last = cur
    time.sleep(0.1)
