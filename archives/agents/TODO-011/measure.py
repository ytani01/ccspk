#!/usr/bin/env python3
"""hook を起動してから pw-play が起動するまで（最初の音が出るまで）を測る。

使い方: python3 measure.py <文の名前> [回数]
文の名前は space（1 文目がスペースでしか切れない）か comma（1 文目が読点で切れる）。
TODO-009 の measure.py をコピーし、文を選べるようにしたもの。
"""
import json, os, subprocess, sys, time
from pathlib import Path

HOOK = Path.home() / ".claude/hooks/speak-response.py"
TEXTS = {
    "space": ("settings.json の登録は通りました。エンジンが入ったので、起動と話者を確認します。"
              "uvicorn だけ足りません。AUR パッケージの依存漏れです。これを入れてください。"
              "その間に TODO.md のチェックを進めます。自己テストは通っています。"),
    "comma": ("reviewer の指摘を受けて挙動が変わったので、同じ reviewer に差分を見直してもらいます。"
              "完了の通知を待ちます。その後 verifier で実測し、コミットします。"),
}
TEXT = TEXTS[sys.argv[1]]
PIDFILE = Path(os.environ["XDG_RUNTIME_DIR"]) / "claude-tts.pid"


def pwplay_in(pgid):
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            if os.getpgid(int(d.name)) == pgid and (d / "cmdline").read_bytes().split(b"\0")[0].endswith(b"pw-play"):
                return True
        except OSError:
            pass
    return False


def once():
    t0 = time.monotonic()
    subprocess.run(["python3", HOOK], input=json.dumps({"last_assistant_message": TEXT}),
                   text=True, env={**os.environ, "CLAUDE_TTS_SPEAK": "1"}, check=True)
    pgid = int(PIDFILE.read_text())
    while time.monotonic() - t0 < 60:
        if pwplay_in(pgid):
            return time.monotonic() - t0
        # 測っている間に別の Stop（この会話の main など）が来ると、今の回は止められる
        try:
            if int(PIDFILE.read_text()) != pgid:
                return "差し替え"
        except (OSError, ValueError):
            pass
        time.sleep(0.02)
    return None


n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
for i in range(n):
    r = once()
    if r == "差し替え":
        print(f"{i + 1} 回目: 測っている間に別の Stop に差し替えられた")
    else:
        print(f"{i + 1} 回目: 最初の音まで {r:.2f} 秒" if r else f"{i + 1} 回目: 60 秒以内に鳴らない")
    # 鳴り終わるのを待たず、次の回の hook で前の再生を止めさせる。
    # 環境変数 GAP で間をあけると、止めた回の合成をエンジンが終えてから次を送れる
    time.sleep(float(os.environ.get("GAP", "1")))
# 最後の再生を止める
subprocess.run(["python3", HOOK], input=json.dumps({"last_assistant_message": ""}),
               text=True, env={**os.environ, "CLAUDE_TTS_SPEAK": "1"})
