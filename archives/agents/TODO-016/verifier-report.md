# TODO-016 verifier 報告

VOICEVOX エンジン（http://127.0.0.1:50021, version 0.25.2）に対して
`.venv/bin/claudecodespeak dict` を実際に叩いて確認した。使った表記は
既存語と重ならない「ゾゾテスト」のみ。既存の語には触れていない。

## 実測結果（6 通り）

1. 新規・指定なし → `priority: 5`（一致）
2. 登録済み・指定なし（読みをゾゾテストニに変更して add）→ `priority: 5`（5 のまま、一致）
3. 登録済み・`--priority 8` → `priority: 8`（一致）
4. 登録済み・指定なし（読みをゾゾテストサンに変更して add）→ `priority: 8`（8 のまま、一致）
5. remove 後、新規・`--priority 3` で add → `priority: 3`（一致）
6. 範囲外 `--priority 11` → `Error: Invalid value for '--priority': 11 is not in the range 0<=x<=10.`、
   終了コード 2 で弾かれた（一致）

各コマンドは `SURFACE PRONUNCIATION [--priority N]` の形で実行し、都度
`curl -s --max-time 10 http://127.0.0.1:50021/user_dict | jq` で `priority` を
直接読んだ（表示メッセージだけで判断していない）。

## クリーンアップの確認

作業前に `dict export $SCRATCH/before.json`、5 の登録後に `dict remove ゾゾテスト`、
その後 `dict export $SCRATCH/after.json` を取り、`diff before.json after.json` は
差分なし（終了コード 0）。エンジンの辞書を元の状態に戻せていることを確認した。

## `uv run claudecodespeak test`

`ok` / `ok` の 2 行が出力され、終了コード 0。

## `docs/UsersGuide.md` の記述との突き合わせ

`git diff -- docs/UsersGuide.md` で追加された記述:

- 「同じ表記が登録済みなら、読みを書き換える（品詞と優先度は、指定しなければ今のまま）」
  → 実測 2, 4 と一致
- 「優先度は `--priority`（0〜10、大きいほど優先）。省くと、新しい語は 5、登録済みの語は
  今の優先度のまま」→ 実測 1, 2, 3, 4 と一致
- 「登録したのに表示した読みが変わらないときは、エンジン標準の読みに負けている。優先度を
  上げて登録し直す（「節」は 5 ではフシのままで、7 でセツになった）」という記述内容
  （「節」の実例）は、今回の検証対象（ゾゾテストでの priority 挙動）とは別の実例であり、
  再現の対象にしていない。真偽は確かめていない。

## 変更されたファイルと指示の範囲

`git status --porcelain`:

```
 M TODO.md
 M docs/UsersGuide.md
 M src/claudecodespeak/user_dict.py
?? archives/agents/TODO-016/
```

指示（`dict add` への `--priority` 追加とドキュメント更新）の範囲と一致している。
`archives/agents/TODO-016/` は reviewer-report.md と本ファイルのみで、範囲外のファイルは無い。

`src/claudecodespeak/user_dict.py` の差分は以下の通り（今回の実測で妥当性を確認した箇所）:

- PUT（登録済みの語の更新）: `priority=old["priority"] if priority is None else priority`
- POST（新規の語の登録）: `extra = {} if priority is None else {"priority": priority}` を
  `word_type` と一緒に渡す。省いた場合はエンジンの既定 5 になることを実測 1 で確認した。

## 確かめられなかったこと・判断できないこと

- 「節」をセツと読ませる実例（優先度 7）そのものの再現は指示の対象外なので行っていない。
- `--type` との組み合わせ（同時指定時の優先度と品詞の独立性）は指示の 6 通りに
  含まれていないため確認していない。挙動は未確認。
- コードのレビュー（分岐の妥当性など）は reviewer の担当であり、ここでは行っていない。
