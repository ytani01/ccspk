# TODO-027 verifier 報告

手順: `archives/agents/TODO-027/verify.sh`、全出力: `verify.out`（同じ場所）。
XDG_CONFIG_HOME・XDG_RUNTIME_DIR は scratchpad/verify 下。エンジンは止めていない。
食い違い: なし（文書の記述と実測が全部一致）。

## 出力の形（例と同じ）
- dict kana 'Ponytail を使う' — `ポ'ニテイル、オ'/_ツカウ'`、rc=0
- dict add Ponytail ポニーテール — 「登録した: … （accent_type 4、ID …）」「書き出した: パス」「読み: ポニイテ'エル」の 3 行、rc=0
- dict list — `ID  表記  読み  accent  優先度` の 2 スペース区切り、表記順、Ponytail は `4  7`、rc=0
- dict remove Ponytail — 「消した: Ponytail（ID …）」「書き出した: パス」、rc=0
- dict import backup.json — 「読み込んだ」「書き出した: パス」、rc=0
- status — 無いとき「止まっていない」、あるとき `パス: 理由`、--clear で理由の後に「消した」、その後「止まっていない」、すべて rc=0
- stop — 「鳴っていない」、rc=0（「止めた」は再生を止める確認なので対象外）
- test — `ok` 2 行、rc=0

## 終了ステータス（記述と一致）
- dict remove 未登録 → 1（「登録されていない: …」）
- dict add 引数なし → 2
- dict import 無いファイル → 2
- dict import `[1]` → 1、`{"x":1}` → 1（どちらもエンジンが 422 で断った）
- dict export 無いディレクトリの中 → 1
- dict add 読み `ボ！` → 1（エンジンが 422 で断った）。dict list で Bad は未登録のまま
- test → 0
- hook（CCSPK_SPEAK なし、`{}`）→ 0
- hook（CCSPK_SPEAK=1、ccspk.unusable あり）→ 0。出力なし。音が出ないことは耳では確認していない（出力が空で 0 だけ確認）
- stop → 0、say 'テスト。' → 0
- -V（`ccspk 0.2.1.dev14+g33c7eaa6b`）・-h・dict add -h・hook -h → 0

## 確かめていないこと
- エンジン停止時の動き（止めないので未確認）
- 文書の `say` の終了 1（pw-play が無い）、`--speak`、stop の実再生停止
- 例の ID・パスは環境依存なので突き合わせていない

## 辞書の diff
backup.json と最後の export を `python3 -m json.tool --sort-keys` で揃えて diff: 差なし（`DICT SAME`）。
Ponytail は dict remove で消した。開始時の dict list は 48 行（Ponytail なし）。
