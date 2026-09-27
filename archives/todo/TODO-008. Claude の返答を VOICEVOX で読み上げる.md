# TODO-008. Claude の返答を VOICEVOX で読み上げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5 → Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high、2 回）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 → Opus 5.5 | medium | 90,981 | 320,360 | 90% |
| reviewer | Opus 5.5 | high | 1,204 | 113,844 | 8% |
| verifier | Sonnet 5 | medium | 268 | 47,855 | 3% |
| 合計 |  |  | 92,453 | 482,059 | 概算 $12.8 |

- main は途中で Opus 5 から Opus 5.5 に切り替わった（利用者の設定）。
  範囲には、方針を決めた前のセッションの分も入っている
- reviewer は同じ担当に 2 回続けて頼んだ
- サブエージェントの output は少なめに出ている（`subagents/` のログの取りこぼし）

## きっかけ

hyprwhspr-utils の TODO-004 の途中で、Claude の返答を音声で聞きたいと
利用者が相談した。

当初は yt_slide と同じ Google Translate TTS を使う方針で、180 文字で
HTTP 200 と mp3 が返ることまで実測した。ところが auto mode の分類器が
**Data Exfiltration** として、スクリプトの作成・`permissions.allow` への追加・
README への追記をすべて拒否した。会話ログを外部へ送る形そのものが
検出対象だった。Claude からは解除も権限の追加もできない。

そこで、ローカルで合成する VOICEVOX に替えて、送信そのものをやめた。
ローカルに替えてからは一度も拒否されていない。

## やったこと

- `hooks/speak-response.py` — Stop hook。入力の `last_assistant_message` を
  整形し（コードブロック・表・Markdown の記号・URL を消す、`_` は空白、
  先頭 180 文字）、VOICEVOX の `/audio_query` → `/synthesis` で wav を作って
  `pw-play` で鳴らす。合成と再生は `start_new_session` の子プロセスに投げ、
  その PID を `$XDG_RUNTIME_DIR/claude-tts.pid` に残す。次の Stop では、
  その PID の cmdline にエンジンの URL があるときだけプロセスグループごと止める
- `systemd/voicevox-engine.service` — エンジンを常駐させる user unit。
  `systemctl --user link` でつなぐ
- `settings.json` — `Stop` hook の登録と `env` の `CLAUDE_TTS_SPEAK=1`
- `.gitignore`・`README.md` — 新しいファイルの追跡と、「返答の読み上げ」の節

エンジンは次の順で落ち着いた。

1. AUR の `voicevox-engine` 0.24.1。依存から `uvicorn` が漏れていた。
   さらに `python-pyworld` 0.3.5 が setuptools 84 で削除された
   `pkg_resources` を import して起動しなかったので、版番号を返すだけの
   代用を `PYTHONPATH` で読ませて動かした
2. 話者を聞き比べて一度は東北イタコに決めたが、利用者が夜語トバリを
   希望した。トバリは VOICEVOX 0.25.2 からなので、公式リリースの Linux 単体版
   0.25.2 に替えた。単体版は Python を同梱しているので、`uvicorn` も代用も
   要らなくなり、消した。AUR の `voicevox-engine` は利用者が外した

話者は夜語トバリ（明るい、id 119）。

## 確かめたこと

- reviewer（1 回目）: 要修正 0、検討 6。`last_assistant_message` が Stop hook の
  入力にあることを本体から見つけ、会話ログを読む処理を消せた。ほかに
  `_` を消すと識別子がつながる、閉じていないコードブロックと `~~~` を読む、
  古い PID への killpg、`claude -p` でも鳴る、を挙げた
- reviewer（2 回目）: 要修正 0、検討 3。古い PID への killpg がまだ 1 回残る、
  `XDG_RUNTIME_DIR` が無いときの置き場所が Claude Code の一時ディレクトリと
  同名、を受けて直した。行頭が ``` の地の文が以降すべて省略される件は見送った
- verifier: 9 項目すべて実測で合った。本物の `claude -p` で PID ファイルが
  更新され、cmdline に `audio_query` と「テスト」の URL エンコードが入る
  （`last_assistant_message` が届く）。`--test` はコピーを 2 か所壊すと
  AssertionError で落ちる。無関係なプロセスの PID を書いても kill しない。
  エンジンが止まっていても終了コード 0 で、子プロセスも wav も残らない
- 音が出ることと声は利用者が耳で確かめた
- 決めて残したもの: `claude -p` のような非対話の実行でも鳴るが、それでよい
  （困ったらその実行だけ `CLAUDE_TTS_SPEAK=0`）

## 残ること

- 合成が終わるまで鳴らないので、128 文字で最初の音まで約 11 秒かかる
  （`synthesis` 10.4 秒、音声 22.2 秒）。文ごとに合成して 1 文目から鳴らす
  高速化を TODO-009 として立てる

## 分担の振り返り

- **各担当が見つけたもの**: reviewer の 1 回目がいちばん効いた。
  `last_assistant_message` の発見で実装が縮み、ターンの最後に text が無いと
  古い返答を読む弱点も消えた。2 回目は、自分で入れた修正（`/tmp/claude-UID`）が
  Claude Code の一時ディレクトリと重なることを拾った。verifier は食い違いを
  見つけなかったが、本物の `claude -p` で入力のフィールドが届くことを実測で
  押さえたのは、reviewer の静的な確認では埋まらない部分だった
- **見込みとの食い違い**: 担当の編成は見込みどおり。食い違ったのは main の
  消費で、全体の 9 割。原因は分類器での足止め（Stop hook に何度も押し戻された）と、
  エンジンの依存漏れを 1 つずつ潰したこと、話者の聞き比べ、エンジンの差し替え
- **次に同じ規模なら**: 外部へデータを送る設計は、auto mode では着手前に
  分類器で止まる前提で考え、立てる時点でローカルの代案と並べて選んでもらう。
  外部のパッケージを入れる項目は、入れた直後に起動まで確かめる手順を
  依頼の最初に置く（依存漏れが 3 つ続いた）。話者のような好みの選択は、
  エンジンの版を決める前に済ませる（トバリの希望でエンジンを入れ直した）
