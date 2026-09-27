#!/usr/bin/env python3
"""Stop hook: Claude の最後の返答を VOICEVOX で読み上げる。

環境変数 CLAUDE_TTS_SPEAK が 1 のときだけ鳴らす。
再生中に次の返答が来たら、前の再生を止めてから読む。
voicevox-engine が動いていないときは、何も鳴らさずに終わる。
"""

import json
import os
import queue
import re
import signal
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path

LIMIT = 180  # 合成に時間がかかるので、読み上げるのはここまで
SPEAKER = 119  # 夜語トバリ（明るい）
ENGINE = "http://127.0.0.1:50021"
PLAY = "--play"  # 合成と再生を受け持つ子プロセスの目印
PIDFILE = (
    Path(os.environ["XDG_RUNTIME_DIR"]) / "claude-tts.pid"
    if os.environ.get("XDG_RUNTIME_DIR")
    else Path(f"/tmp/claude-tts-{os.getuid()}.pid")
)


def to_speech(text):
    """読み上げ用に整える。"""
    # コードブロックと表は中身を読まない。閉じていないブロックは末尾まで
    text = re.sub(r"^\s*(```|~~~).*?(?:^\s*\1|\Z)", " コード省略。 ", text, flags=re.S | re.M)
    text = re.sub(r"^\s*\|.*$", "", text, flags=re.M)
    # リンクは表示文字だけ残し、裸の URL は消す
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    # Markdown の記号。_ は識別子の切れ目なので空白にする
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", text, flags=re.M)
    text = text.replace("_", " ")
    text = re.sub(r"[`*~>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:LIMIT]


def stop_playing():
    """前の再生をプロセスグループごと止める。"""
    try:
        pid = int(PIDFILE.read_text())
        PIDFILE.unlink()
        # 再生が終わった後に番号が別のプロセスへ使い回されていたら触らない
        args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        if PLAY.encode() not in args or not any(a.endswith(Path(__file__).name.encode()) for a in args):
            return
        os.killpg(pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass


def sentences(text):
    """文に分ける。句点などの後ろで切り、句点は前の文に残す。"""
    return [s for s in re.split(r"(?<=[。！？!?])\s*", text) if s]


def synthesize(sentence):
    """1 文を合成して wav のバイト列を返す。"""
    query = urllib.request.urlopen(
        urllib.request.Request(
            f"{ENGINE}/audio_query?speaker={SPEAKER}&text=" + urllib.parse.quote(sentence),
            method="POST",
        ),
        # エンジンは要求を 1 つずつ処理し、止めた前の返答の合成も最後まで続ける。
        # その後ろに並ぶと 10 秒近く待つので、短くすると黙って諦めてしまう
        timeout=60,
    ).read()
    return urllib.request.urlopen(
        urllib.request.Request(
            f"{ENGINE}/synthesis?speaker={SPEAKER}",
            data=query,
            headers={"Content-Type": "application/json"},
        ),
        timeout=60,
    ).read()


def play(text):
    """1 文目ができたらすぐ鳴らし、2 文目以降は鳴らしている間に合成する。"""
    wavs = queue.Queue()

    def produce():
        # エンジンが動いていない、応答が途中で切れた、など何で止まっても、
        # 鳴らす側が待ち続けないよう終わりの印は必ず入れる
        try:
            for s in sentences(text):
                wavs.put(synthesize(s))
        finally:
            wavs.put(None)

    threading.Thread(target=produce, daemon=True).start()
    while (wav := wavs.get()) is not None:
        subprocess.run(["pw-play", "-"], input=wav, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def speak(text):
    """合成と再生を子プロセスに投げ、その PID を残す。"""
    p = subprocess.Popen(
        [sys.executable, __file__, PLAY, text],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    PIDFILE.parent.mkdir(mode=0o700, exist_ok=True)
    PIDFILE.write_text(str(p.pid))


def demo():
    src = (
        "## 見出し\n"
        "`foo.py` を **直した**。\n"
        "```python\nprint(1)\n```\n"
        "| a | b |\n| - | - |\n"
        "- [詳細](https://example.com/x) を見る\n"
        "https://example.com/y\n"
    )
    got = to_speech(src)
    assert got == "見出し foo.py を 直した。 コード省略。 詳細 を見る", got
    assert len(to_speech("あ" * 500)) == LIMIT
    assert to_speech("```\nonly code\n```") == "コード省略。"
    assert to_speech("") == ""
    assert to_speech("CLAUDE_TTS_SPEAK を足す") == "CLAUDE TTS SPEAK を足す"
    assert to_speech("説明\n```python\nsecret()\n") == "説明 コード省略。"
    assert to_speech("前\n~~~\ncode\n~~~\n後") == "前 コード省略。 後"
    assert sentences("直した。確かめる？ はい! 終わり") == ["直した。", "確かめる？", "はい!", "終わり"]
    assert sentences("句点なし") == ["句点なし"]
    assert sentences("") == []
    print("ok")


def main():
    if sys.argv[1:2] == ["--test"]:
        demo()
        return
    if sys.argv[1:2] == [PLAY]:
        play(sys.argv[2])
        return
    if os.environ.get("CLAUDE_TTS_SPEAK") != "1":
        return
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    text = to_speech(payload.get("last_assistant_message") or "")
    stop_playing()
    if text:
        speak(text)


if __name__ == "__main__":
    main()
