# TODO-041 の分担

- main: 言い回しの直しと図の書き足し。文書だけで、込み入ったロジックが無いので分けなかった
- reviewer（Opus 5.5 / high）: 図と文章をコードと突き合わせる。書き写しでなくコードとの照合が要り、判断を伴うので Opus。[報告](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 4 枚を `mmdc` で描き、文字列を SVG と突き合わせる。手順が決まっているので Sonnet。
  [報告](verifier-report.md)、スクリプトは `extract_check.py`
- reviewer を先に回し、指摘を直した後の図を verifier に描かせた
