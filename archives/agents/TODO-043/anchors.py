import re,unicodedata
t=open("docs/UsersGuide.md",encoding="utf-8").read()
seen={};anc=set();incode=False
for l in t.splitlines():
    if l.startswith("```"): incode=not incode
    m=None if incode else re.match(r"#{1,6}\s+(.*)",l)
    if m:
        h=re.sub(r"[`*]","",m.group(1)).strip().lower()
        a="".join(c for c in h if c.isalnum() or c in "-_ ").replace(" ","-")
        n=seen.get(a,0);seen[a]=n+1;anc.add(a if n==0 else f"{a}-{n}")
links=re.findall(r"\]\(#([^)]+)\)",t)
bad=[x for x in links if x not in anc]
print(len(links),"links; bad:",bad)
