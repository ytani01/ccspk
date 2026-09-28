# TODO-009 verifier-report

対象: `voicevox/add-word.py`（未コミット）。VOICEVOX エンジン
（http://127.0.0.1:50021、version 0.25.2）に対して実機で確認した。
試した語は `zzverify` / `zzverify2` / `ZZVERIFY` のみ（大文字小文字違いの
確認に指示どおり ZZVERIFY を使用）。エラー系の確認では
`zzverify3` / `zzverify4` という表記を渡したが、どちらもエンジンに
登録される前に失敗しており、user_dict には残っていないことを確認済み。

## 1. `--test`

一致。`ok` を標準出力し、終了コード 0。

## 2. 新規登録

一致。`python3 voicevox/add-word.py zzverify ズズベリファイ` →
`登録した: zzverify → ズズベリファイ（accent_type 2、ID 17f849cc-...）`、
終了コード 0。`/user_dict` の実体（ID 17f849cc-f8a6-4869-b5d5-83085112cffa）:
`part_of_speech_detail_1: "固有名詞"`、`accent_type: 2`（表示の
「ズズ'ベリファイ」＝2 モーラ目の後で下がる、と一致）。

## 3. 書き換え

一致。`--type COMMON_NOUN` で書き換え → 同じ ID
（17f849cc-f8a6-4869-b5d5-83085112cffa）のまま
`part_of_speech_detail_1` が `"一般"` に変化、終了コードは
`書き換えた: ...` を出して 0。続けて `--type` を省いて読みだけ
`ズズベリファイア` に変更 → `part_of_speech_detail_1` は `"一般"` の
まま、`priority` も 5 のまま変わらず。

## 4. 大文字と小文字

一致。`ZZVERIFY ズズベリファイ` は `zzverify` の ID
（17f849cc-...）とは別の新規 ID（bb51cc3e-c0b6-413a-8cea-e3ad7395e512）で
登録され、「登録した」の表示。

## 5. `--accent 0`

一致。`zzverify2 ズズ --accent 0` → `/user_dict` 実体の
`accent_type` が 0。

## 6. エラー

- ひらがなの読み `ずず` → `エンジンが断った（422）: ...発音は有効な
  カタカナでなくてはいけません...` を出して終了コード 1、traceback なし。
- 読み `ー` → `読みから音が取れない。カタカナで渡す` を出して終了コード 1、
  traceback なし。
- どちらの場合も `zzverify3` / `zzverify4` は `/user_dict` に登録されて
  いないことを確認済み（フィルタで 0 件）。

一致。

## 7. `--speak`

- 通常: `zzverify ズズベリファイ --speak` は終了コード 0（音が出たかは
  未確認・判定対象外）。
- `PATH=/nonexistent` にした状態で、`python3 -c 'import sys;print(sys.executable)'`
  で得た実体パス（`/usr/bin/python3`）から直接
  `add-word.py ... --speak` を呼ぶと、登録・書き換えメッセージの後に
  `pw-play が無いので鳴らせない（登録は済んだ）` を出して終了コード 1、
  traceback なし。

一致。

## 8. エンジンに繋がらないとき

`/tmp/add-word-badengine.py` という一時コピーを作り、`ENGINE` の行だけ
`http://127.0.0.1:1` に書き換えて実行（`diff` で他の行が変わっていない
ことを確認済み。リポジトリの `voicevox/add-word.py` は未変更）。
出力は `エンジン（http://127.0.0.1:1）とやり取りできない: [Errno 111]
Connection refused`、終了コード 1、traceback なし。一致。

## 9. 片付け

`zzverify`（ID 17f849cc-f8a6-4869-b5d5-83085112cffa）、`zzverify2`
（ID 7c35f08d-cff2-4a36-9e9f-aa7d37b98241）、`ZZVERIFY`
（ID bb51cc3e-c0b6-413a-8cea-e3ad7395e512）を DELETE し、いずれも
204。`diff <(curl -s http://127.0.0.1:50021/user_dict | jq -S .)
voicevox/user_dict.json` は差分なし（終了コード 0）。一致。

## git の変更範囲

`git status --porcelain` は次のとおりで、TODO-009 の範囲と合っている
（コードや文書を直していない）。

```
 M README.md
 M TODO.md
 M docs/Developer.md
 M docs/UsersGuide.md
?? archives/agents/TODO-009/
?? voicevox/add-word.py
```

## 確かめられなかったこと・判断が要る点

- 7 の `--speak` で実際に音が出たかどうかは、依頼どおり判定していない
  （「音が出たかは判定しない」の指示に沿った）。
- 6 の `ー` のケースは、`accent_of` に到達する前に `/audio_query` への
  POST 自体はエンジンに通っている（読みの妥当性チェックはエンジン側で
  弾かれず、`accent_phrases` が空で返ってきて `add-word.py` 側の
  `sys.exit` が発火した、という理解）。この経路の解釈が正しいかは
  ソースを読んでの推定であり、エンジン内部の挙動までは確認していない。
  実害は未確認。
- コードの設計・文体（reviewer 済み）は見ていない。
