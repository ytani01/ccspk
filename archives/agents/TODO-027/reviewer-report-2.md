# TODO-027 reviewer の報告（2 回目）

対象: `git diff HEAD -- docs/UsersGuide.md docs/Developer.md` のうち、前回の指摘を受けて直した箇所。
根拠は `src/ccspk/hook.py`・`user_dict.py` を読んだもの。コマンドは動かしていない。行番号は作業ツリーの `docs/UsersGuide.md`。

## 要修正

なし。

## 検討

なし。

## 好みの範囲

- `docs/UsersGuide.md:129-130`: 大文字・小文字の文を消した跡で、コードブロックの後ろに空行が 2 つ続いている（ほかの箇所はどこも 1 つ）
- `docs/UsersGuide.md:168-172` と `ccspk say`・`ccspk hook` の終了ステータス: 共通の節は「サブコマンドに共通」として「`1` — 失敗」と書いているが、`say` は合成や `pw-play` の失敗でも `0`、`hook` は常に `0` になる。各節で言い切っているので読み違えは起きにくい。共通の節に「各サブコマンドの節に書いたものを除く」のような断りを入れるかは管理者の判断（実害は未確認）
- `ccspk dict list` の例（`README  リードミー  1  5`）: 手順の節の例（`ccspk dict add README リードミー --speak`）で新しく登録すると優先度は `7`（`user_dict.py` の `priority=7 if priority is None`）なので、手順どおりにやった人の表示と 1 列食い違う。実際の出力の抜粋なので、そのままでもよい

## 合っていたもの

- 1. `docs/Developer.md:132` → `UsersGuide.md#ccspk-hook`: 張り先の 199-200 行に `PIPEWIRE_REMOTE` の理由がある。ほかのリンク（Developer.md:30・54・160・205）の張り先も残っている
- 2. `say` の終了ステータス: `hook.py` の `play()` と一致（`pw-play` の `returncode` を見ない、合成の例外は別スレッドのトレースバック、`pw-play` の `FileNotFoundError` は 1 つ目の wav が来たときだけ）
- 3. 重複の削除: stop の「再生だけ止める」は `ccspk stop` の節だけ、大文字・小文字は `SURFACE` だけ、`status --clear` の「次の返答から」は手順の節だけ、`export` の繰り返しの文は消えている。消したことで落ちた説明は無い
- 4. 終了ステータスを足した分: `kana`・`list` の `1`（`call` の `sys.exit`）、`export` の `1`（書き込み先を開くのが遅れて開くので click の `FileError`、main の実測とも合う）、`import` の `1`（`HTTPError`・`OSError`）と `2`（`click.File("rb")` は開けないと `BadParameter`、前回 `rc=2` を実測）: コードと一致。`import` の「JSON の形が違う」で `1` になるのは未確認（エンジンが 422 を返す前提）
- 5. 例: `add`・`list`・`remove` の ID（`7dbd9f32-…`）、`accent_type 4`、優先度 `7`（新しい単語の既定）が 3 つの例でつながっている。表示の形は `user_dict.py` の `print` と一致
- 6. `hook` の条件: `agent_id` を見るのは MessageDisplay・PreToolUse だけ（`hook.py` の `(display or ask) and payload.get("agent_id")`）、5 秒は `SAME_WITHIN`、「同じ文」は Developer.md:91・178 と hook.py:60 の言い方と揃っている。見出しを「読み上げずに終わる」にしたので、「理由をファイルに記録する」とも食い違わない
- `test` の説明（「`demo()` の `assert`」）: CLAUDE.md の書き方と揃っている
- 新しい重複や食い違い: 上の好みの範囲のほかには見当たらない

## 作り込みすぎ

作り込みすぎ: なし（今回の差分は削る方向で、新たに増えたのは足りなかった終了ステータスだけ）。

Lean already. Ship.
