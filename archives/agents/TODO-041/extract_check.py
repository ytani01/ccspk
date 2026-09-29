#!/usr/bin/env python3
"""docs の mermaid ブロックを抜き出し(.mmd)、SVG の文字と突き合わせる。
使い方: extract_check.py extract OUTDIR / extract_check.py check OUTDIR"""
import re, sys, html, pathlib
mode, out = sys.argv[1], pathlib.Path(sys.argv[2])
names = []
if mode == "extract":
    out.mkdir(parents=True, exist_ok=True)
    for f, tag in (("docs/Developer.md", "dev"), ("docs/UsersGuide.md", "ug")):
        for i, m in enumerate(re.findall(r"```mermaid\n(.*?)```", open(f).read(), re.S), 1):
            (out / f"{tag}{i}.mmd").write_text(m)
            print(f"{tag}{i}.mmd", m.splitlines()[0])
else:
    for p in sorted(out.glob("*.mmd")):
        src = p.read_text(); svg = (out / (p.stem + ".svg")).read_text()
        bad = re.findall(r"Syntax error|Parse error", svg)
        txt = html.unescape(re.sub(r"<[^>]+>", " ", svg))
        txt = re.sub(r"\s+", "", txt)
        strs = []
        for l in src.splitlines()[1:]:
            l = l.strip()
            if not l or l.startswith("%%"): continue
            if l.startswith("sequenceDiagram") or l.startswith("flowchart"): continue
            # ラベル候補: 引用符・括弧内、: の後、participant の as の後
            for m in re.findall(r'"([^"]*)"', l): strs.append(m)
            m = re.match(r"(?:participant|actor)\s+\S+\s+as\s+(.*)", l)
            if m: strs.append(m.group(1))
            m = re.match(r"Note\s+.*?:\s*(.*)", l)
            if m: strs.append(m.group(1))
            m = re.match(r"[\w-]+\s*(?:-->|->>|-->>|->|--x|-x|==>)+\s*\S+?\s*:\s*(.*)", l)
            if m: strs.append(m.group(1))
            m = re.findall(r"\|([^|]*)\|", l); strs += m
            if '"' not in l:
                strs += re.findall(r"[\w]+[\[\(\{]+([^\]\)\}]+)[\]\)\}]+", l)
        missing = []
        for s in dict.fromkeys(strs):
            parts = re.split(r"<br\s*/?>|\\n", s)
            for q in parts:
                q = re.sub(r"<[^>]+>", "", html.unescape(q))
                q = re.sub(r"\s+", "", q)
                if q and q not in txt: missing.append(q)
        print(f"{p.name}: syntaxerr={len(bad)} checked={len(set(strs))} missing={len(missing)} {missing}")
