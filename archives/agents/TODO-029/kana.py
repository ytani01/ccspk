# TODO-029: TODO-NNN の番号を桁ごとのカナにした文の読みを、2・5 の長音と短音で比べる
import subprocess, sys
L = "ゼロ イチ ニー サン ヨン ゴー ロク ナナ ハチ キュウ".split()
S = "ゼロ イチ ニ サン ヨン ゴ ロク ナナ ハチ キュウ".split()
nums = ["001", "002", "005", "012", "025", "027", "029", "052", "100", "123", "250", "555"]
for tail in ["を立てる", "の件"]:
    for n in nums:
        row = [n + tail]
        for D in (L, S):
            s = "TODO" + "".join(D[int(c)] for c in n) + tail
            k = subprocess.run([".venv/bin/ccspk", "dict", "kana", s], capture_output=True, text=True).stdout.strip()
            row.append(k)
        print("\t".join(row))
