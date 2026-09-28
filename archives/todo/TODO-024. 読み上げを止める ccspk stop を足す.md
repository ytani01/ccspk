# TODO-024. 読み上げを止める ccspk stop を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | medium | 8,761 | 57,274 | 68% |
| reviewer | Opus 5.5 | high | 1,604 | 43,223 | 27% |
| verifier | Sonnet 5.5 | medium | 211 | 27,581 | 5% |
| 合計 |  |  | 10,576 | 128,078 | 概算 $1.6 |

- 集計は決着のコミットの前（現在時刻まで）。サブエージェントの分は少なめに出る

## きっかけ

Claude Code で Esc を押して返答を中断しても、読み上げの再生は止まらない。
止める手段をコマンドとして用意する。止めるのは再生だけで、エンジンで進んでいる合成は止めず、
次の読み上げを黙らせることもしない（利用者が決めた。2026-09-29）。

## やったこと

- `src/ccspk/hook.py`: `stop_playing()` が止めたら `True`、それ以外は `False` を返すようにした。
  サブコマンド `stop` を足した。フックと同じ `LOCK` を取ってから `stop_playing()` を呼び、
  「止めた」か「鳴っていない」を表示する。`LOCK` を開けないときはフックと同じくロック無しで進む。
  `LOCK` のコメントに PIDFILE と `ccspk stop` の用途を足した
- `src/ccspk/cli.py`: `stop` を登録し、docstring のサブコマンドの列挙に足した
- `docs/UsersGuide.md`: 「鳴っている読み上げを止める」の節を足した
- `docs/Developer.md`: サブコマンドの表（3 つ → 4 つ）、「前の再生を止める」の戻り値、
  ファイルの表の `LOCK` の行を直した
- `CLAUDE.md`: サブコマンドの列挙に `stop` を足した

## 確かめたこと

詳細は [archives/agents/TODO-024/](../agents/TODO-024/README.md)。

- reviewer（1 回目）: フックの `main()` は戻り値を使わないので動きは変わらない。
  LOCK を取らないと、フックが子プロセスを起こした直後の PIDFILE を消して止め損なう競合がある
  （実害は未確認）、合成待ちのあいだも「止めた」と出て文書の「鳴っていれば」と合わない、の 2 点 →
  LOCK を取るようにし、文書を「最初の音を待っているあいだも含む」に直した
- reviewer（2 回目）: LOCK を開けないと traceback で落ちる → フックと同じくロック無しで進むようにした
- verifier: 一時の `$XDG_RUNTIME_DIR` で再生を起こし、`ccspk stop` で「止めた」、プロセスグループと
  `ccspk.pid` が消えること、2 回目は「鳴っていない」、PIDFILE が無関係な PID を指すときは
  そのプロセスに触れないこと、`ccspk.lock` を `chmod 000` にしても終了コード 0 で動くこと、
  `ccspk test` が通ることを実測した
- verifier が未実測とした「合成待ちのあいだも止まる」は、子プロセスが合成と再生の両方を受け持ち、
  起こした時点で PIDFILE が書かれるので、コードから決まる

## 分担の振り返り

- reviewer は LOCK の競合と LOCK を開けないときの traceback を見つけた。どちらも main の実装では
  見落としていた。verifier は食い違いを見つけなかった（reviewer の後に回したので、直したあとの差分を測れた）
- 見込みとの食い違いは reviewer が 2 回動いたことだけ。1 回目の指摘を直した方法（LOCK を取る）が
  新しい失敗の経路を生んだため
- 次に同じ規模なら同じ組み方でよい。ただし main がフックの既存の経路（`main()` の LOCK の取り方）に
  揃えて最初から書けば、reviewer の 2 回目は要らなかった。既存の関数と同じ資源を触るコマンドを足すときは、
  既存の側の取り方を写してから reviewer に回す
