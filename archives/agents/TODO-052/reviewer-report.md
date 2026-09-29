# TODO-052 reviewer の報告

対象: `git diff`（未コミット）の `src/ccspk/hook.py`（`NAMES`・`rewrite()`・`play_rewritten()`・`demo()`）、
`docs/UsersGuide.md`、`docs/Developer.md`。

## 要修正

### 1. `src/ccspk/hook.py:803-810`（demo）: 「結果を待たずに告げる」ことが確かめられていない

- 何が問題か: 項目の中心の要件（`claude -p` の結果を待たずに、まず「要約します」と言う）を、`demo()` が
  確かめていない。`play_rewritten()` の `play(f"{name}します。")` と `worker.join()` を入れ替え、
  結果を待ってから告げる形に壊しても、`uv run ccspk test` は通る
- 根拠（実測）: 一時的に 2 行を入れ替えて `uv run ccspk test` を走らせたら rc=0（ほかの壊し方は下の表のとおり
  全部落ちた）。偽の `rewrite` がすぐ返すので、告げるのが `join()` の前か後かが `played` や `events` の
  順番に出ない
- 例えば偽の `rewrite` を、`play` が呼ばれるまで返らないようにする（`threading.Event` を待つなど）か、
  返るときにも `events` へ印を足して順番を比べれば、入れ替えで落ちるようになる（直し方は管理者の判断）

## 検討

### 2. `src/ccspk/hook.py:331-339`: 記録するのが、前の子プロセスを待った後に変わった（実害は未確認）

- 変更前は、順番に読むモードでも `check.record()` が `wait_for(after)` より前だった。今は待って、告げて、
  結果を待ってから記録する。待っている間に `stop_playing()` で止められた返答は、記録されなくなる
- 読んでいない文を記録しない分、読み間違いの点検には都合がよいとも読める。要件には書かれていない挙動の
  変化なので報告だけ。`docs/Developer.md` の 3.2 の手順（5 番）は新しい順番どおりに書いてあり、文書との食い違いは無い

### 3. `docs/Developer.md:190`（sequenceDiagram の Note）: 告げる文を付けてから記録するように読める

- Note が「失敗なら元の文を整えて切り、告げる文を前に付ける）。LOCK を取って check.record()」の順で、
  前置きを付けた文を記録するように読める。実装（`hook.py:338` で本文だけを記録し、`:342` で鳴らすときに付ける）と、
  同じ文書の手順 5・6（告げる文は記録しない）とは、書く順番が逆
- 本文の手順は正しく、図だけの読み違えやすさ

## 好みの範囲

なし。

## 作り込みすぎ

作り込みすぎ: なし（`done` のリストとスレッドは、例外でも元の文を読むための最小の形。`concurrent.futures` にしても短くならない）。

## 問題なしと確かめたもの

- 順番に読むモード: `claude -p` は `wait_for()` の前に裏で走り、告げるのは前の子プロセスが終わってから。demo の例で確かめられている（下の M2・M4 が落ちる）
- `stop_playing()`: スレッドから起こした子プロセスも同じプロセスグループに入り、`killpg(SIGTERM)` で親と一緒に止まる（実測。`start_new_session=True` の python がスレッドで `sleep 60` を `subprocess.run`、`killpg` の後に `pgrep -g` が空、親の rc=-15）。hook.py に SIGTERM のハンドラは無い
- `rewrite()` の例外: `done` が空になり、元の文を `to_speech()` して、告げる文を付けて読む（M7 が落ちる）
- `SUMMARY_TIMEOUT`: スレッドを起こした時から数える。前の読み上げを待つ時間は `claude -p` が終わっていれば関係しない。変更前と同じ
- `check.record()` に渡すのは本文だけ（M5 が落ちる）
- `rewrite()` が失敗で `""` を返す変更: 呼び出し元は `play_rewritten()` の 1 か所だけ（`rg -n "rewrite\(" src`）で、ほかは demo のみ
- `rewrite()` の docstring、`NAMES` のコメント、`docs/Developer.md` の定数表・3.2 の手順・demo の説明、`docs/UsersGuide.md` の説明は実装と合っている。「知らせず」「失敗は知らせない」の古い記述は残っていない（`rg`）
- ruff: 差分で増えた警告は無い（HEAD と比べて同じ種類）

## demo の強さ（壊して `uv run ccspk test` を走らせた結果）

| 壊し方 | 結果 |
|---|---|
| M1 告げるのを `worker.join()` の後にする | **通る（指摘 1）** |
| M2 `rewrite` を `wait_for` の後に同期で走らせる | 落ちる |
| M3 失敗のときの告げる文を外す | 落ちる |
| M4 告げるのを `wait_for` の前にする | 落ちる |
| M5 告げる文ごと記録する | 落ちる |
| M6 失敗のときの元の文を `to_speech()` しない | 落ちる |
| M7 `done` が空のときの備えを外す | 落ちる（IndexError） |
| M8 `rewrite()` を元の失敗時の戻り値に戻す | 落ちる |
| M9 「要約します」を言わない | 落ちる |

壊した後は `hook.py` を控えから戻し、`sha256sum` と `git diff | sha256sum` が始める前と同じことを確かめた。

---

# 2 回目（指摘を受けて直した分）

対象: `play_rewritten()` の裏のスレッド（`work()`）での LOCK と `check.record()`、例外の捕まえ方、demo の追加分、
`docs/Developer.md` の図と 3.2 の手順。

## 要修正

なし。1 回目の指摘 1（告げるのと `join()` の入れ替え）は、下の N1 で落ちることを確かめた。

## 検討

### 1. `src/ccspk/hook.py:323`（docstring）・`docs/Developer.md:219-220`（手順 2）: 「待つ前に記録する」は言い過ぎ

- 何が問題か: docstring は「記録も待つ前に済ませる」、手順 2 は「前の子プロセスを待つ前に記録するので、
  待つ間に止められても記録は残る」と書いている。実装では、記録するのは `claude -p` が終わった時点で、
  `wait_for()` と並んで進む。`claude -p` が前の読み上げより長くかかれば、記録は待ち終わった後、告げた後になる。
  その前に `stop_playing()` で止められれば記録は残らない
- 根拠（コードを読んで）: `work()` は `rewrite()` の戻りを待ってから `record()` する（`hook.py:327-341`）。
  demo の 2 つ目の例のコメント「待っている間に書き直しが済めば、告げる前に記録する」は条件付きで正しい
- 挙動は元の作り（`rewrite()` の途中で止められたら記録しない）と同じで、直すなら文書と docstring の言い方だけ。
  図（`Developer.md:181-192`）も CL の返事と記録が `wait_for()` の opt より前に描かれていて、同じ読み違いを招く

## 好みの範囲

### 2. `src/ccspk/hook.py:349`: スレッドが `record()` で止まると、書き直せていても「要約できなかった」と言う（実害は未確認）

- `done` が空になるのは、`work()` の中で `to_speech(text)` か `check.record()` が例外を投げたとき。
  `record()` が投げると、`rewrite()` が成功していても `("", to_speech(text))` になり、失敗と告げて元の文を読む
- `check.record()` は `OSError` を握りつぶす（`check.py:50`）ので、ここへ来るのは `OSError` 以外（書き込みの
  `UnicodeEncodeError` など）だけ。成功時の本文は `claude -p` の出力を厳密に復号した文なので、実際に起きる道筋は
  見つけていない

## 作り込みすぎ

作り込みすぎ: なし。

## 問題なしと確かめたもの

- スレッドの中の LOCK: `open`→`flock`→`record`→`close` の形は元と同じで、`finally` で必ず放す。メインのスレッドは LOCK に触らないのでぶつからない
- 例外: `rewrite()` の例外は `except Exception` で `""` にし、元の文を `to_speech()` して記録・再生する（N5 で落ちる）
- 最初の 2 つのテストを、記録と再生の別のリストにした形: 順番が決まらない所を比べておらず、`join()` の後に比べるので揺れない
- 順番に読むモードの 2 つの例は、偽の子プロセスが 0.5 秒で終わる前にスレッドが動く前提。3 回続けて `uv run ccspk test` が通った（遅い機械で揺れるかは未確認）

## demo の強さ（2 回目。壊して `uv run ccspk test`）

| 壊し方 | 結果 |
|---|---|
| N1 告げるのを `worker.join()` の後にする | 落ちる |
| N2 スレッドを `wait_for` の後に起こす | 落ちる |
| N3 告げるのを `wait_for` の前にする | 落ちる |
| N4 記録をスレッドから出し、`join()` の後にする | 落ちる |
| N5 スレッドの `try/except` を外す | 落ちる |
| N6 告げる文ごと記録する | 落ちる |
| N7 失敗のときの告げる文を外す | 落ちる |
| N8 失敗のときの元の文を `to_speech()` しない | 落ちる |

壊した後は控えから戻し、`hook.py` と `git diff` の `sha256sum` が始める前と同じことを確かめた。
