# TODO-007 verifier-report

対象: `docs/Developer.md`「テストと動作の確かめ方」節のコマンドを、書いたとおりに
bash で実行し、書かれた結果になるかを確かめた。文書・コードは変更していない。

前提の確認:
- 実行前: `/run/user/649/claude-tts.unusable` は無し。`/run/user/649/claude-tts.pid` の中身は `11145`
- 実行後: `/run/user/649/claude-tts.unusable` は作られていない。`/run/user/649/claude-tts.pid` の中身は `11145` のまま（変化なし）
- VOICEVOX エンジン (`/home/ytani/.local/share/voicevox-engine/0.25.2/run`) は実行中のまま、止めていない

## 1. `python3 hooks/speak-response.py --test`

```
$ python3 hooks/speak-response.py --test
ok
EXIT:0
```

一致。

## 2. Stop を手で再現する（1 つ目のブロック）

文書の中身をそのまま heredoc に切り出し、bash で実行した。

```
$ bash block2.sh
/tmp/tmp.vKb177Zji5/claude-tts.pid
EXIT:0
```

`find $tmp -type f` の出力は `claude-tts.pid` のみで、期待どおり一致。

備考（実害は未確認）: このブロックは `PIPEWIRE_RUNTIME_DIR` に本物の実行時ディレクトリを
指すため、本物の VOICEVOX エンジンで合成・再生まで走った可能性がある（`PIDFILE` 自体は
一時ディレクトリ内にあり、本物の `claude-tts.pid`／`claude-tts.unusable` は前後で
変化していないことは確認済み）。実際に音が鳴ったかどうかは確認していない。

## 3. Stop を手で再現する（2 つ目のブロック、PATH を空にする）

```
$ bash block3.sh
pw-play が無い
EXIT:0
```

一致。

## 4. `--play` を直接起動するブロック

```
python3 hooks/speak-response.py --play '合成と再生だけを試す。' &
（実行中に pgrep -x pw-play で確認）
pw-play seen during run: 1
EXIT:0
```

終了コード 0、実行中に `pw-play` のプロセスが `pgrep` で確認できた。一致。
音そのものは指示どおり聞いていない。

## 5. 「最初の音までの時間」の python ブロック

文書の中身をそのまま heredoc に切り出し、bash 経由で 1 回実行した。

```
0.74 秒
EXIT:0
```

`N.NN 秒` の形で出力され、期待どおり一致。値は `0.74 秒`（1 回のみ計測、
このときエンジンは他の合成をしていない状態だった）。

## 6. コピーして貼ったまま動くか（heredoc・バックスラッシュ継続を含む）

上記 1〜5 すべて、文書のコード ブロックの中身をリポジトリ直下から改変せずに
そのまま bash（zsh ではなく）に流して実行した。バックスラッシュ継続を含む
ブロック 2・3、heredoc を含むブロック 5 のいずれも、貼ったままでエラーなく
動作した。

## 判断できないこと・確かめられなかったこと

- ブロック 2 の実行で実際に音が鳴ったかどうかは確認していない（指示の範囲外、
  および音は聞けない環境のため）。実害は未確認。
- `unusable()` の 3 条件（PATH・エンジン接続・PipeWire ソケット）のうち、
  ここで確認したのは PATH が無い場合（条件 1）のみ。エンジン接続やソケットの
  条件を個別に再現する指示は無かったため試していない。
- 文書の「フックの仕組み」節の記述の正しさはレビュー対象外として見ていない。
