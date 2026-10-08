"""読み上げた文から読み間違いを見つけ、辞書に登録する（python -m ccspk.check）。

フック（hook.py）は読み上げた文を SPOKEN に追記し、Stop のたびに、SPOKEN が CHECKED より
新しければこのモジュールを裏で起こす。ここでは、SPOKEN から英字の単語と漢字の名詞を切り出し、
点検済み（CHECKED）と登録済みの単語を除いて、エンジンの読みと出てきた文を並べた一覧を claude -p（Opus）に
渡す。誤りとされた単語は正しい読みで登録し、ADDED に残す（ccspk dict auto で見直す）。
失敗したら理由を FAILED に書き、次の Stop でフックが知らせる。
"""

import fcntl
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path  # demo() で使う

from .user_dict import ADDED, STATE, call, google, query, register, save

SPOKEN = STATE / "spoken.txt"  # 読み上げた文。1 行 1 文
SPOKEN_MAX = 64 * 1024  # これを超えたら後ろ半分の行だけ残す
CHECKED = STATE / "checked.txt"  # 点検に回した単語。mtime は点検した SPOKEN の mtime に揃える
FAILED = STATE / "failed.txt"  # 点検が失敗した理由
LOCK = STATE / "check.lock"  # 点検は 1 つずつ
ALPHA = r"[A-Za-z][A-Za-z0-9._+-]*[A-Za-z0-9]"  # 英字の単語（1 字は除く）
KANJI = r"[一-鿿々〆]"
VERSION = r"v[0-9]+(?:\.[0-9]+)*"  # 版の番号（v1.7.0）。hook.py が読み方を決めるので点検しない
TIMEOUT = 300  # claude -p を待つ秒数
PROMPT = """音声合成エンジン VOICEVOX が、ソフトウェア開発の会話に出た単語をどう読んだかの一覧です。
各行は「表記<TAB>読み<TAB>その単語が出てきた文」。文は読み方を決める手がかりです。読みはエンジンのカナで、' はアクセントの位置、_ は無声化を表します（どちらも正誤に関係しません）。
読みが明らかに誤っている単語だけを、「表記<TAB>正しい読み（カタカナのみ、記号なし）」の形で 1 行ずつ出してください。
エンジンのカナは長音を母音で書きます（先頭 → セントオ、Claude → クロオド、背景 → ハイケエ）。発音が同じなら誤りとしないでください。
英字の単語は、開発者が普通に口にする読み（例: README → リードミー、pytest → パイテスト）を正しいとします。
ファイル名・パス・16 進の ID のように、単語でないものは出さないでください。
迷うもの、どちらでも通じるもの、1 文字だけの英字は出さないでください。誤りが無ければ何も出さないでください。説明は不要です。"""


def record(text):
    """読み上げた文を SPOKEN に追記する。フックが LOCK（hook.py）を取ったまま呼ぶ。"""
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        with SPOKEN.open("a", encoding="utf-8") as f:
            f.write(text + "\n")
        if SPOKEN.stat().st_size > SPOKEN_MAX:
            lines = SPOKEN.read_text(encoding="utf-8").splitlines(keepends=True)
            tmp = SPOKEN.with_suffix(".tmp")
            tmp.write_text("".join(lines[len(lines) // 2 :]), encoding="utf-8")
            tmp.replace(SPOKEN)
    except OSError:
        pass


def after_stop():
    """Stop のフックから呼ぶ。前の点検の失敗を知らせ、新しく読んだ文があれば点検を裏で起こす。"""
    try:
        msg = FAILED.read_text(encoding="utf-8").strip()
        FAILED.unlink()
        print(json.dumps({"systemMessage": f"ccspk の読みの点検が失敗した: {msg}"}, ensure_ascii=False))
    except OSError:
        pass
    # google のときはエンジンが止まっていることもある。読んだ文は SPOKEN に溜め、voicevox に戻したら点検する
    if google() or not pending():
        return
    try:
        subprocess.Popen(
            [sys.executable, "-P", "-m", "ccspk.check"],
            cwd=STATE,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def pending():
    """点検していない文があるか。SPOKEN が CHECKED より新しいか、CHECKED が無くて SPOKEN があれば真。"""
    try:
        spoken = SPOKEN.stat().st_mtime
    except OSError:
        return False
    try:
        return spoken > CHECKED.stat().st_mtime
    except OSError:
        return True


def extract(text):
    """英字の単語と、漢字を含む 2 字以上の名詞を、出てきた順に重ねずに、最初に出てきた行と組にして返す（{単語: 行}）。"""
    from sudachipy import Dictionary, SplitMode  # 重いので、フックからは読まない

    tok = Dictionary(dict="core").tokenizer()
    words = {}
    for line in text.splitlines():  # sudachipy は 49,149 バイトより長い入力を断る
        for w in re.findall(ALPHA, line):
            if not re.fullmatch(VERSION, w):
                words.setdefault(w, line)
        for m in tok.tokenize(line, SplitMode.C):
            s = m.surface()
            if m.part_of_speech()[0] == "名詞" and len(s) >= 2 and re.search(KANJI, s):
                words.setdefault(s, line)
    return words


def around(line, word, width=30):
    """line の中の word の前後 width 字。行を丸ごと単語ごとに渡すと、入力が 8 倍ほどに膨らむ。"""
    i = line.find(word)
    return line[max(0, i - width) : i + len(word) + width]


def parse(out, table):
    """claude の返答から (表記, 正しい読み) を取り出す。一覧に無い表記、カタカナだけでない読み、
    エンジンの読みと発音が同じ読み（same() で比べる）は捨てる。"""
    for line in out.splitlines():
        surface, reading = ([f.strip() for f in line.strip().split("\t")] + [""])[:2]  # 3 列目（文）を返されても読む
        if surface in table and re.fullmatch("[ァ-ヴー]+", reading) and not same(reading, table[surface]):
            yield surface, reading


def same(reading, kana):
    """Claude の読み reading が、エンジンの読み kana と同じ発音か。' _ / 、 は除いて比べる。
    エンジンは 計算 を ケエサン と書くが、カタカナの ケイサン は字のとおり読むので、reading の側だけ
    エ段の後の「イ」を「エ」にした形とも比べる（kana の側にかけると、経緯 の ケエイ が ケエエ になってずれる）。
    「ウ」と「ー」は、読みをエンジンに通せばエンジンが揃える（ソウサ・ソーサ → ソオサ）。"""
    reading, kana = (re.sub("['_/、]", "", k) for k in (reading, kana))
    return kana in (reading, re.sub("(?<=[エケセテネヘメレゲゼデベペェ])イ", "エ", reading))


def nfkc(s):
    return unicodedata.normalize("NFKC", s)


def check():
    mtime = SPOKEN.stat().st_mtime  # 読んでいる間に足された文は、次の点検に回す
    text = SPOKEN.read_text(encoding="utf-8")
    done = set(CHECKED.read_text(encoding="utf-8").splitlines()) if CHECKED.exists() else set()
    registered = {nfkc(w["surface"]) for w in json.loads(call("GET", "/user_dict")).values()}
    words = {w: line for w, line in extract(text).items() if w not in done and nfkc(w) not in registered}
    if words:
        table = {w: query(w)["kana"] for w in words}
        try:
            p = subprocess.run(
                ["claude", "-p", "--model", "opus", "--setting-sources", "", "--tools", "",
                 "--no-session-persistence", PROMPT],
                input="".join(f"{w}\t{k}\t{around(words[w], w)}\n" for w, k in table.items()),
                capture_output=True,
                check=False,
                text=True,
                timeout=TIMEOUT,
                env={**os.environ, "CCSPK_SPEAK": "0"},
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"claude -p が {TIMEOUT} 秒で終わらなかった") from None
        if p.returncode:
            tail = (p.stderr or p.stdout).strip().splitlines()[-1:] or [""]
            raise RuntimeError(f"claude -p が終了コード {p.returncode} で終わった: {tail[0]}")
        # ここから先は claude -p を呼び直さないよう、登録に失敗した単語は飛ばして CHECKED を更新する
        failed, added = [], 0
        for surface, reading in parse(p.stdout, table):
            try:
                # エンジンは長音を母音で書く（先頭 → セントオ）ので、Claude は同じ発音を誤りとしがち。
                # Claude の読みもエンジンに通して比べ、同じ発音なら登録しない
                if same(query(reading)["kana"], table[surface]):
                    continue
                register(surface, reading)
            except (Exception, SystemExit) as e:  # noqa: BLE001  user_dict.call は sys.exit で抜ける
                failed.append(f"{surface} → {reading}（{reason(e)}）")  # 手で dict add できるよう読みも残す
                continue
            added += 1
            with ADDED.open("a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{surface}\t{reading}\t{table[surface]}\n")
        if added:
            try:
                save()
            except (Exception, SystemExit) as e:  # noqa: BLE001
                failed.append(f"辞書のファイルへの書き出し（{reason(e)}）")
        with CHECKED.open("a", encoding="utf-8") as f:
            f.write("".join(w + "\n" for w in words))
        os.utime(CHECKED, (mtime, mtime))
        if failed:
            raise RuntimeError(f"登録できなかった単語がある: {'、'.join(failed)}")
    CHECKED.touch()
    os.utime(CHECKED, (mtime, mtime))


def reason(e):
    return e.code if isinstance(e, SystemExit) else f"{type(e).__name__}: {e}"


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return  # 前の点検が走っている
        try:
            check()
        except (Exception, SystemExit) as e:  # noqa: BLE001  user_dict.call は sys.exit で抜ける
            FAILED.write_text(f"{reason(e)}\n", encoding="utf-8")


def demo():
    import shutil
    import tempfile

    got = extract("README.md と a を直した。優先度を試さないで行を読む。作業中のリンク先 v1.2 と v2、v1.2.3b と C++ と x\n次の行は優先度")
    assert list(got) == ["README.md", "v1.2.3b", "優先度", "作業中", "リンク先"], got  # 版の番号は拾わない
    assert got["優先度"].startswith("README.md と")  # 最初に出てきた行
    assert around("あ" * 40 + "語" + "い" * 40, "語") == "あ" * 30 + "語" + "い" * 30
    assert around("短い語の文", "語") == "短い語の文"
    table = {"README": "リ'イドメ", "優先度": "ユウセンタ'ク", "fugashi+unidic-lite": "フ'ガシ/タ'ス/ユ'ニディック、ラ'イト", "リンク先": "リン_クサキ'"}
    out = "README\tリードミー\tREADME を直す\nREADME\tファイル\n- 優先度\tユウセンド\n優先度\tゆうせんど\n知らない\tシラナイ\nREADME\tリード・ミー\n\n優先度\tユウセンド \n"
    assert list(parse(out, table)) == [("README", "リードミー"), ("README", "ファイル"), ("優先度", "ユウセンド")]  # ァ も通す
    assert list(parse("fugashi+unidic-lite\tフガシタスユニディックライト\n", table)) == []  # エンジンと同じ読み
    assert list(parse("リンク先\tリンクサキ\n", table)) == []  # 無声化の _ も除いて比べる
    assert list(parse("計算\tケイサン\n", {"計算": "ケエサン'"})) == []  # エ段の後のイはエと同じ
    assert same("メイセイ", "メ'エセエ") and same("ケイイ", "ケ'エイ") and same("メイン", "メ'イン")  # 経緯・メイン
    assert not same("ケイサ", "ケエサン") and not same("メエン", "メ'イン")

    global STATE, SPOKEN, CHECKED
    saved = STATE, SPOKEN, CHECKED
    STATE = Path(tempfile.mkdtemp(), "ccspk")
    SPOKEN, CHECKED = STATE / "spoken.txt", STATE / "checked.txt"
    try:
        # 点検を起こすのは、SPOKEN があって CHECKED が無いか古いときだけ
        assert not pending()  # どちらも無い
        STATE.mkdir()
        CHECKED.touch()
        assert not pending()  # SPOKEN が無い
        CHECKED.unlink()
        SPOKEN.touch()
        assert pending()  # CHECKED が無い
        CHECKED.touch()
        for c, want in ((100, True), (200, False), (300, False)):  # CHECKED が古い・同じ・新しい
            os.utime(SPOKEN, (200, 200))
            os.utime(CHECKED, (c, c))
            assert pending() is want, c
        SPOKEN.unlink()
        lines = [f"{i:02}" + "あ" * 1000 for i in range(22)]  # 1 行 3,003 バイト
        for s in lines[:21]:
            record(s)
        assert SPOKEN.read_text(encoding="utf-8").splitlines() == lines[:21]  # 63,063 バイトなら切らない
        record(lines[21])
        assert SPOKEN.read_text(encoding="utf-8").splitlines() == lines[11:]  # 超えたら後ろ半分
    finally:
        shutil.rmtree(STATE.parent)
        STATE, SPOKEN, CHECKED = saved
    print("ok")


if __name__ == "__main__":
    main()
