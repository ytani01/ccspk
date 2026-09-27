# TODO-001 verifier report

実行環境: /home/ytani/.claude、XDG_RUNTIME_DIR=/run/user/649、
scratch = /tmp/claude-649/-home-ytani--claude/0da861d3-0979-4634-b2d7-64eb848e132e/scratchpad/tt

## 1. `--test` が ok を返すか

```
$ python3 hooks/speak-response.py --test
ok
```
終了コード 0。OK。

## 2. テストが壊すと落ちるか（scratch にコピーして変異）

- `mut1.py`（`text = text.replace("_", " ")` の行を削除）
  → `python3 mut1.py --test` は `AssertionError`（`assert to_speech("CLAUDE_TTS_SPEAK を足す") == "CLAUDE TTS SPEAK を足す"` で失敗、終了コード 1）。
- `mut2.py`（コードフェンスの `re.sub` の行だけを削除。`assert` 行の
  「コード省略」は残したまま）
  → `python3 mut2.py --test` は `AssertionError`
  （`got == "見出し foo.py を 直した。 コード省略。 詳細 を見る"` に対し実際は
  `"見出し foo.py を 直した。 python print(1) 詳細 を見る"`、終了コード 1）。

両方とも狙った箇所の削除でテストが落ちることを確認。リポジトリ本体
（`hooks/speak-response.py`）は変更していない。

## 3. 本物の Stop hook（last_assistant_message が届くか）

`claude -p '「テストです」とだけ返してください'` を 1 回実行。PID ファイルの
ポーリングで子プロセスの `cmdline` を捕捉した。

- 出力: `テストです`
- PID ファイルは新しい番号（176991 → 実測時は環境により変動、再実測では
  176991 のケースで確認）
- `/proc/<pid>/cmdline` に以下が含まれることを確認（実測値）:
  ```
  sh -c f=$(mktemp --suffix=.wav) && ... curl ... 'http://127.0.0.1:50021/audio_query?speaker=119&text=%E3%83%86%E3%82%B9%E3%83%88%E3%81%A7%E3%81%99' | curl ... 'http://127.0.0.1:50021/synthesis?speaker=119' > "$f" && test -s "$f" && pw-play "$f"
  ```
  `audio_query` と `%E3%83%86%E3%82%B9%E3%83%88`（テスト）の両方が入っている。
  OK。

## 4. `CLAUDE_TTS_SPEAK` が 1 でないとき

- 未設定（`env -u CLAUDE_TTS_SPEAK`）: hook 実行後 PID ファイルは存在しない
  （`ls` がエラー = ファイル無し）。終了コード 0。
- `CLAUDE_TTS_SPEAK=0`: 同様に PID ファイルは存在しない。終了コード 0。

両方とも鳴らない側の挙動どおり。OK。

## 5. 再生中に次の入力

長文（180 文字超）を投げて PID1=177530（実測）を取得。0.5 秒後に
`ps` でプロセスグループ内に `sh`（curl パイプ）と `curl`（synthesis 側）の
2 プロセスが存在することを確認。1.5 秒後に短文を投げると:

- PID ファイルは新しい番号（PID2、実測 177604）に変わった
- PID1 のプロセスグループ（`pgid=177530`）に属すプロセスは 0 件（`ps` で該当なし）

1 回目のグループが消え、2 回目の番号になることを確認。OK。

## 6. 古い PID（無関係なプロセス）

`setsid sleep 60 &` で無関係なプロセスを作り、その PID を PID ファイルに
直接書いてから hook を 1 回実行（`CLAUDE_TTS_SPEAK=1`、普通の短文）。

- hook の終了コード 0
- 実行直後、`sleep` の PID は生きたまま（`/proc/<pid>` が存在）
- PID ファイルは新しい番号に更新されていた

`cmdline` にエンジンの URL が含まれないプロセスは kill しない、という
本体のガード（`stop_playing` の `if ENGINE.encode() not in ...: return`）が
効いていることを確認。確認後、その `sleep` プロセスは `kill` で自分で止めた
（確認は完了している）。OK。

## 7. エンジンが止まっているとき

`systemctl --user stop voicevox-engine` の後、hook を 1 回実行。

- hook の終了コード 0（即座に返る。Popen が非同期のため）
- 10 秒後、PID ファイルに書かれたプロセスグループ（sh/curl/pw-play）は
  `ps` に 1 件も残っていない（leader process も `/proc` から消滅）
- `/tmp` に `tmp.*.wav` は残っていない（`rg` で 0 件）

その後 `systemctl --user start voicevox-engine` で復旧し、`curl -s
127.0.0.1:50021/version` が `"0.25.2"` を返すまで確認した（2 回目のリトライで
復旧、`systemctl --user is-active` も `active`）。OK。

## 8. README の手順（ダウンロードはせず、周辺だけ確認）

- `gh release view 0.25.2 -R VOICEVOX/voicevox_engine --json assets` の
  asset 一覧に `voicevox_engine-linux-cpu-x64-0.25.2.vvpp` が存在する
  （手順どおりの名前と一致）
- unit ファイル `~/.claude/systemd/voicevox-engine.service` の
  `ExecStart=%h/.local/share/voicevox-engine/0.25.2/run --host 127.0.0.1
  --port 50021` について、`%h` を展開した実パス
  `/home/ytani/.local/share/voicevox-engine/0.25.2/run` は実在し、
  実行可能ビット（`-rwxr-xr-x`）が付いている
- `systemctl --user is-enabled voicevox-engine` → `enabled`
- `~/.config/systemd/user/voicevox-engine.service` は
  `/home/ytani/.claude/systemd/voicevox-engine.service` へのシンボリックリンク
  （`readlink -f` で一致）

すべて手順どおり。OK。

## 9. settings.json と git status

- `jq '.hooks.Stop'` で Stop hook の登録（`python3
  "$HOME/.claude/hooks/speak-response.py"`、timeout 5）が読めた
- `jq '.env.CLAUDE_TTS_SPEAK'` → `"1"`
- `git status --short -uall` の差分・新規ファイル:
  `.gitignore` `README.md` `TODO.md` `settings.json`（変更）、
  `hooks/speak-response.py` `systemd/voicevox-engine.service`
  `archives/agents/TODO-001/reviewer-report.md`
  `archives/agents/TODO-001/reviewer-report-2.md`（新規）。
  いずれも TODO-001 の作業に対応するもので、`__pycache__` や `.pyc` の
  ような余計なファイルは無い（`rg -i 'pycache|\.pyc'` で 0 件）。OK。

## まとめ

1〜9 すべて仕様どおりの挙動を実測で確認した。落ちたものは無い。

## 確かめられなかったこと・判断できないこと

- 実際の音（再生された音声の内容・声質）は聞いていない。依頼の範囲外
  （「読み上げの声の品質」は見なくてよいと指定されていたため）
- README に無い運用上の懸念（例えば `run` プロセス自体の異常終了時の
  自動復旧の可否など）は確認していない。依頼の範囲外と判断した
- 3 の PID・cmdline は環境依存の実行時刻でプロセス番号が変わるため、
  再現時は別の番号になる。挙動（audio_query とテキストの URL エンコードが
  含まれること）自体は安定して確認できた
