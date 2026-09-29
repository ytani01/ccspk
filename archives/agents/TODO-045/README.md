# TODO-045 の分担

- main: 実装（`hook.py`・`cli.py`・`pyproject.toml`・文書）。1 ファイルの中の子プロセスの扱いと、それに合わせた文書なので分けない
- reviewer（Opus 5.5 / high）: 分岐（止めるか・待たせるか）と子プロセスの扱いが変わるので入れた。
  報告は [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: 一時ディレクトリの `XDG_*` と本物のエンジン・PipeWire で、来た順に鳴るか・全部止まるかを測る。
  報告は [verifier-report.md](verifier-report.md)、計測は [verify.sh](verify.sh) と [monitor.py](monitor.py)
- reviewer を先、verifier を後に回した。reviewer の指摘（`speak()` のテスト・4.2 の手順）を直してから verifier を起こした
