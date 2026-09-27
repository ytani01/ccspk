# TODO-006 reviewer 報告

対象: 未コミットの `git diff`（`hooks/speak-response.py`、`README.md`、`TODO.md`）。
プロジェクトに `CLAUDE.md` は無いので、根拠はコードと実測（2026-09-28、
libpipewire 1.6.9、voicevox-engine 0.25.2、`Linger=no`）。

要修正: 0 件 / 検討: 2 件 / 好みの範囲: 2 件

## 要修正

なし。

## 検討

### 1. hooks/speak-response.py:49 コメントの理由が実測と合わない

- 何が: 「HTTP で問い合わせると、前の返答を合成している間は待たされる」。
- 根拠（実測）: 21 秒かかる `/synthesis` を走らせている最中に `GET /version` を
  投げると 1 ms で返った（空いているときは 5 ms）。TCP 接続は 0.2〜0.8 ms。
  待たされるのは合成どうし（TODO-002 / TODO-004 で確かめた現象）で、
  `/version` は待たされなかった。
- TCP 接続で見る判断そのものは妥当（速い、エンドポイントに依らない、
  接続だけ張って閉じてもエンジンのログに何も出ないことも確かめた）。直すなら
  コメントの理由だけ。CPU が詰まったときに `/version` が遅れるかは未確認。

### 2. hooks/speak-response.py:56-58 PipeWire のソケットの決め方が libpipewire とずれる所がある

- 何が: `PIPEWIRE_REMOTE` を 1 つのファイル名として `Path` に連結している。
- 根拠（実測、`pw-cli info 0` と `unusable()` の比較）:

  | 環境変数 | pw-cli | unusable() |
  |---|---|---|
  | なし（普段） | つながる | None |
  | `PIPEWIRE_REMOTE=/run/user/649/pipewire-0`（絶対パス） | ― | None（`Path` の `/` で絶対パスが勝つので正しい。`XDG_RUNTIME_DIR` を消しても None） |
  | `PIPEWIRE_REMOTE='[pipewire-0-manager,pipewire-0]'` | つながる | **使えないと判定**（`/run/user/649/[pipewire-0-manager,pipewire-0]` を探す） |
  | `PIPEWIRE_RUNTIME_DIR=`（空文字） | つながらない | None（`or` で `XDG_RUNTIME_DIR` へ落ちる） |
  | `XDG_RUNTIME_DIR` なし | つながらない | 使えないと判定（`/nonexistent/pipewire-0`）。一致 |

- 誤って「使えない」と覚えるのは 3 行目。`PIPEWIRE_REMOTE` を配列の形で
  環境変数に置く人がいるかは分からず、実害は未確認。4 行目は逆向き
  （使えないのに子プロセスを起こす）で、これも実害は未確認。

## 好みの範囲

### 3. README.md:43 「ログアウトで消える」

`$XDG_RUNTIME_DIR` が消えるのは、その利用者のセッションが全部終わったとき。
SSH や別の端末のセッションが残っていれば消えず、`loginctl enable-linger` を
入れていれば再起動まで残る（このマシンは `Linger=no` なので書いたとおり）。
決めた内容は変えず、書き方の精度だけの話。

### 4. テスト

`unusable()` と `main()` の新しい分岐は `demo()` で押さえていない。環境に依存する
ので、verifier の実測で代えるなら要らない。自動で残すなら、`PATH` を空にして
`"pw-play が無い"` が返ること程度。

## 誤って「使えない」と覚える場面（一時的な失敗を除く）

- 上の 2 の `PIPEWIRE_REMOTE` が配列の形のとき（実測）。
- `/tmp` に置く場合、同じマシンの別の利用者が `/tmp/claude-tts-<uid>.unusable` を
  先に作れば鳴らなくなる。`fs.protected_symlinks = 1` なのでシンボリックリンク
  経由の上書きは起きない。既存の `PIDFILE` と同じ置き方で、実害は未確認。
- ほかに、`PATH` / ソケット / エンジンは hook と子プロセスで同じ環境を見るので、
  hook だけが食い違う場面は見つからなかった。

## 分岐と条件式（食い違い無し）

- `main` の順序: `--test` → `--play` → `CLAUDE_TTS_SPEAK` と `UNUSABLE.exists()` →
  `unusable()` → stdin。ファイルがあるときは確かめずに返る。子プロセス
  （`--play`）は `UNUSABLE` を見ないので、鳴っている最中に覚えても止まらない
  だけで問題ない。stdin を読まずに返るのは以前の `CLAUDE_TTS_SPEAK` と同じ。
- 書き込みに失敗したら黙って返り、次の Stop でまた確かめる（子プロセスは
  起こさない）。仕様の範囲内。
- 使えるときの `unusable()` の所要時間は 0.13〜1.06 ms（3 回）。最初の音への
  影響は無視できる。
- 確かめている間、`/run/user/649/claude-tts.unusable` は作られていない。

## 範囲

指示に無い変更は無い。`PIDFILE` の書き方を 1 行にまとめたのは `RUNTIME` を
共有するためで、値は変わらない。

## 作り込みすぎ

- hooks/speak-response.py:40-42: shrink: 同じ条件式が 2 回。
  `BASE = Path(RUNTIME, "claude-tts") if RUNTIME else Path(f"/tmp/claude-tts-{os.getuid()}")`
  から `BASE.with_suffix(".pid")` / `BASE.with_suffix(".unusable")`（値が同じことは
  確かめた）。行数はほぼ変わらないので好みの範囲。
- ほかは無し。net: -0〜1 lines possible.
