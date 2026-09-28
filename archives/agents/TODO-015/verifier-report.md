# TODO-015 verifier-report

実際に `.venv/bin/claudecodespeak`（`uv sync` 済み）を動かして確かめた。
VOICEVOX エンジンは 127.0.0.1:50021 で稼働、辞書は本物（テスト用の
`ZZTESTWORD` は add → list 確認 → remove で後始末済み。最終状態は
`voicevox/user_dict.json` とバイト一致を確認済み）。

## 1. test
`.venv/bin/claudecodespeak test` → `ok` を 2 行出力、終了コード 0。一致。

## 2. --help / hook --help
`--help` に `dict`・`hook`・`say`・`status`・`test` が出る。`add-word` は無い。
`hook --help` に `-h, --help` のみで `--play`・`--test` は無い。一致。

## 3. dict kana / dict list（節）
`dict kana 節` → `セ'ツ`。
`dict list` に `973b220b-... 節 セツ 1` の行あり。一致。

## 4. dict add / list / remove（ダミー語）
一致するが、途中で気になった点が 1 つ（詳細下記）。
- `dict add ZZTESTWORD ズズテスト` → `登録した: ZZTESTWORD → ズズテスト（accent_type 2、ID …）`、exit 0
- 直後の `dict list | rg ZZTESTWORD`（半角のまま検索）が **ヒットしなかった**。
  調べると、エンジンが表記を全角に正規化して保存していた（`ＺＺＴＥＳＴＷＯＲＤ`）。
  `rg -i "ｚ|zz"` で見ると登録は確認できた。
  **これは `dict add` 自体の既存の挙動（エンジン側の正規化）であり、今回の
  TODO-015 の変更対象ではない。** `dict remove ZZTESTWORD`（半角指定）は
  正常に見つけて削除できており、`find()` 側は半角⇔全角を問題なく解決している。
  実害は未確認・境界線上の判断はしていない（報告のみ）。
- `dict remove ZZTESTWORD` → `消した: ZZTESTWORD（ID …）`、exit 0。`dict list`
  から消えた（grep exit 1）ことを確認。
- 2 回目の `dict remove ZZTESTWORD` → `登録されていない: ZZTESTWORD`、exit 1。一致。
- 後始末後、`dict export | cmp - voicevox/user_dict.json` は差分無し（exit 0）。
  テストの語は残っていない。

## 5. dict export（標準出力・ファイル）
`dict export | cmp - voicevox/user_dict.json` → 差分無し。
`dict export /tmp/....json && cmp` → 差分無し。両方一致。

## 6. dict import（ファイル・標準入力）
`dict import voicevox/user_dict.json` → `読み込んだ`、exit 0。その後の
export と cmp は差分無し。
`dict import < voicevox/user_dict.json` → 同上。両方一致。

## 7. エンジンに届かないとき
`ENGINE` を書き換える CLI オプションが無いため、`uv run python -c` で
`claudecodespeak.user_dict.ENGINE = 'http://127.0.0.1:1'` にしたうえで
click の `CliRunner` から `dict_group` の `list` を呼んだ。
結果: `exit_code=1`、出力
`エンジン（http://127.0.0.1:1）とやり取りできない: [Errno 111] Connection refused`。
一致（設計どおり、`call()` に例外処理が集約されている）。

## 8. export の書き込み失敗
`dict export /nonexistent/dir/x.json` →
`Error: Could not open file '/nonexistent/dir/x.json': No such file or directory`、
exit 1。**「エンジン」という語は出ない**（click の `File` オプションが開く時点で
落ちるため、`call()` の例外処理を通らない）。設計の意図（通信の失敗と取り違えない）
どおり。一致。

## 9. status
`XDG_RUNTIME_DIR` を一時ディレクトリに向けて確認（本物は使っていない）。
- ファイル無し: `止まっていない`、exit 0、ファイルは作られない。
- `claude-tts.unusable` に理由（`エンジンが起動していない`）を書いた状態:
  `/tmp/.../claude-tts.unusable: エンジンが起動していない`、exit 0。
- `status --clear`: 上と同じ表示に続けて `消した`、exit 0、ファイルは消える。
  その後の `status` は「止まっていない」に戻る。
すべて一致。

## 10. フックの子プロセス
docs/Developer.md の「フックを手で動かす」の最初の手順どおり、一時ディレクトリで
`hook` を動かした。`claude-tts.pid` の PID の `/proc/<PID>/cmdline` は
`/home/ytani/work/claudecodespeak/.venv/bin/python -P -m claudecodespeak.hook --play 確認です。二つ目の文です。`
で、`--play` と `claudecodespeak.hook` の両方が入っていることを確認（鳴り終わる前に読んだ）。一致。

## 11. 文書
`rg -n -e 'add-word' -e 'add_word' -e '--play' -e 'hook --test' -e 'curl' -e 'rm ' README.md CLAUDE.md docs/`
の結果:

```
docs/Developer.md:87:  speak() は、`python -P -m claudecodespeak.hook --play <本文>` で子プロセスを起こす。
docs/Developer.md:108: /proc/<pid>/cmdline に `--play` と…（stop_playing() の見分け方の説明）
docs/Developer.md:159: | `PLAY` | `--play` | 子プロセスの目印。… |
docs/Developer.md:203, 223: rm -r $tmp（手動検証用の一時ディレクトリの後始末）
docs/UsersGuide.md:27: rm voicevox_engine-linux-cpu-x64-0.25.2.vvpp（エンジンのインストール手順、辞書やunusableと無関係）
docs/UsersGuide.md:30: curl -s http://127.0.0.1:50021/version（設計で明示的に残すとされたエンジン起動確認）
```

`add-word`・`add_word`・`hook --test` の一致は無い。残っている `--play`・`curl`・`rm`
はいずれも設計で「残してよい」とされた文脈（`--play` は子プロセスの仕組みの説明、
`curl …/version` はエンジン起動確認、`rm -r $tmp`/`rm voicevox_engine...vvpp` は
辞書や unusable の操作ではない）で、旧い書き方の残存ではない。一致。

文書中の実際に打てるコマンド例を 1 つずつ実行して確認:
- `claudecodespeak dict kana 'TODO.md を直す'` 相当（`節` で代用、上記 3 参照）: 通る
- `claudecodespeak dict list`: 通る
- `claudecodespeak dict export voicevox/user_dict.json`: 通る（cmp で確認済み、上記 5）
- `claudecodespeak dict import voicevox/user_dict.json`: 通る（上記 6）
- `claudecodespeak status` / `status --clear`: 通る（上記 9）
- `claudecodespeak test`: 通る（上記 1）
- `claudecodespeak say '確認です。'`: exit 0 で通る（1 回のみ、音の確認はしていない）

`dict add README リードミー --speak` はダミー語では確かめていない（本物の辞書に
`README` という語を追加・書き換えたくないため、実行を控えた。`--speak` オプション
自体は `dict add --help` に載っていることのみ確認）。

## 変更ファイルと指示の一致
`git diff --stat` の対象は CLAUDE.md、README.md、TODO.md、docs/Developer.md、
docs/UsersGuide.md、src/claudecodespeak/cli.py、src/claudecodespeak/hook.py、
src/claudecodespeak/user_dict.py（add_word.py からの rename）で、設計の
「ファイル」の節と一致。指示に無いファイルの変更は無い。
`TODO.md` の TODO-015 のチェックボックスは全項目チェック済み。

## 確かめられなかったこと・判断できないこと
- `dict add ... --speak` は本物の辞書を汚さないため未実施（`--help` 表示のみ確認）。
  実害は未確認。
- `say` は音が実際に正しく聞こえるかまでは確認していない（指示どおり 1 回鳴らして
  exit 0 のみ確認）。
- 4 の全角正規化の挙動が既存仕様どおりかどうかは、今回のコードを読んでいないため
  判断できない（テストは半角→全角どちらでも add/remove とも動作することのみ確認）。
