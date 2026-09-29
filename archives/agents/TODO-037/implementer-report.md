# TODO-037 実装の報告（implementer）

## 変えたこと

### src/ccspk/hook.py

- 32: `from .user_dict import DICT_FILE, STATE`（check 経由で既に読み込まれているので、重い import は増えない）
- 69-78: 定数 `SUMMARY`（`DICT_FILE.parent / "summary"`）・`SUMMARIZE`（`--summarize`）・`SUMMARY_TIMEOUT`（30）・
  `SUMMARY_PROMPT`（`prompt.txt` を元に、字数を `LIMIT` から作る。「頼んでいることや決めることが返答に無ければ、
  無いとは書かず、そのことに触れないでください。」の 1 行を足した）
- 104-111: `to_speech()` を `clip(tidy(text))` にし、本体を `tidy()` に移した（`clip()` の前の文を取るため）
- 189-197: `summary_env()`（`1`→True、`0`→False、ほかは None）、`summary_on()`
- 200-205: `prepare(raw)` — `(子プロセスに渡す文, 要約させるか)`。`len(tidy) > LIMIT` かつ入のときだけ切らずに渡す
- 208-228: `summarize(text)` — 子プロセスの中で `claude -p --model sonnet …` を起こす。`cwd=STATE`（mkdir）、
  `CCSPK_SPEAK=0`、`timeout=SUMMARY_TIMEOUT`、`start_new_session` は付けない。
  `OSError`・`TimeoutExpired`・終了コードが 0 でない・`to_speech()` の結果が空 → `clip(text)`
- 231-245: `play_summary(text)` — 要約 → `LOCK` を取って `check.record()` → 放して `play()`
- 372-376: `speak(text, to_summarize=False)` — 要約のときは `--play --summarize <本文>`
- 646, 660-662: `main()` で `prepare()` を使う。`LAST` は子プロセスに渡す文で比べる。要約のときは `record()` を呼ばない
- 704-716: `summary` コマンド（`on`/`off`/引数なし。`click.Choice`。環境変数が決めていれば 1 行添える）
- 720-723: `__main__` で `--play --summarize` を見分ける（`len(sys.argv) == 4` も見る。本文が `--summarize` だけのときに取り違えないため）
- 545-606: `demo()` に足した分（切り替え 6 通り、`prepare` の分かれ目、偽の `claude` での `summarize` 6 通り＋`claude` が無いとき）。
  偽の `claude` は、標準入力・`-p`/`sonnet`・`CCSPK_SPEAK=0`・`cwd` を確かめてから返す。時間切れは上限を 0.5 秒に差し替え

### src/ccspk/cli.py

- 1, 10, 38: `summary` を足した（docstring の並びにも）

### 文書

- `docs/UsersGuide.md`: 「1.6 長い返答を要約して読む」を新設、「3.2 ccspk hook」に要約と失敗時の動き、
  「3.6 ccspk summary」を新設（遅れ 5〜6 秒・1〜1.5 セント）、2.3 の `spoken.txt` に「要約したときは要約」。
  旧 3.6〜3.14 を 3.7〜3.15 に繰り下げ、リンク（`#37-ccspk-test`・`#38-ccspk-dict`・`#310`・`#312`・`#313`）を直した
- `docs/Developer.md`: 依存の `claude`、1 の表の hook.py、2 の動き方、3.1 のサブコマンド表（4→5 つ）と手順 7・8・10、
  3.2 に要約の子プロセスの流れ、3.6 の表（`to_speech`/`tidy`/`prepare`）、3.7 の定数 4 つ、3.8 の `record()`、
  4.1 の demo の説明、4.2 に「要約が入っていると本物の `claude -p` を呼ぶ」注意
- `README.md`: 特徴と主な機能に `ccspk summary`、外に送るものに「要約させる返答の整えた文も」

`rg -n '#[0-9]+-' docs README.md` で拾ったリンクは、すべて実在する見出しを指している。

## 確かめたこと

- `uv run ccspk test` → `ok` 3 行、終了コード 0（最終版で実行）
- 子プロセスを直接（偽の `claude`・偽の `pw-play`、`XDG_RUNTIME_DIR`・`XDG_STATE_HOME`・`XDG_CONFIG_HOME` は一時ディレクトリ）:
  `python -P -m ccspk.hook --play --summarize <200 字>` → 終了コード 0、`spoken.txt` に要約が 1 行、`claude` の引数とプロンプト、標準入力 600 バイト（200 字）
- フックを MessageDisplay で（同じ一時環境、`CCSPK_SUMMARY=1`）: 子プロセスの cmdline に `--play --summarize`、
  直後は `spoken.txt` 無し・要約後に記録される。`CCSPK_SUMMARY=0` では切った文がフックで記録される
- `claude` が 20 秒眠る偽物で要約中に `ccspk stop` → 「止めた」、グループの python・sh・sleep が全部消え、記録もされない
- `ccspk summary`（引数なし→off、on→on、off→off）、`CCSPK_SUMMARY=1` で注記 1 行、`bad` → 終了コード 2
- 本物の `claude` は呼んでいない。本物の `$XDG_*` は使っていない
  （ただし手動の確かめで、本物の VOICEVOX エンジンには合成を頼んだ。`pw-play` は偽物なので鳴っていない）

## 判断が要る点・懸念

- **`CLAUDE.md` のサブコマンドの並びに `summary` を足していない。** brief の指示だが、担当の定義で `CLAUDE.md` は
  触らないことになっているため。main で足してほしい（冒頭の「`hook`・`say`・`stop`・`status`・`test`・`dict`」）
- `ccspk summary on` は、環境変数が優先しているときも切り替えた後の実際の状態（環境変数の値）を表示し、注記を添える
- 時間切れのとき、`subprocess.run` は `claude` 本体だけを kill する。`claude` が起こした孫プロセスが残るかは未確認
  （本物の `claude` を呼んでいないため）。次の返答が来れば `killpg` でまとめて止まる
- `summarize()` の `cwd` は brief どおり `STATE` だが、ここは `spoken.txt` などがあり空ではない（`--tools ""` なので読まれはしない）
- demo の切り替えは、`XDG_CONFIG_HOME` を向ける代わりに `SUMMARY` をモジュールの中で一時パスに差し替えて確かめた
  （`SUMMARY` は import 時に決まるため）。`XDG_CONFIG_HOME` に従うことは、上の手動の確かめで見た
