# verifier 報告 TODO-025

1. `uv run ccspk test`: `ok`、終了コード 0
2. chunks(to_speech(t)) の実測
   - 3 文: ['実装が終わったので、', '確かめてください。', 'reviewer の指摘は二つあり、', 'どちらも直しました。', '三つ目の文ですが、ここは切りません。']
   - 1 文: ['実装が終わったので、', '確かめてください。']
   - 2 文目が短い: ['実装が終わったので、', '確かめてください。', 'はい、どうぞ。']（切れていない。期待どおり）
3. エンジン応答あり（/version = "0.25.2"）。XDG_RUNTIME_DIR は使い捨ての一時ディレクトリに替えて実行
   - `ccspk say` 3 文: 終了コード 0、10.55 秒
   - `ccspk say` 2 文目が短い例: 終了コード 0、3.03 秒
   （所要時間は合成と再生の合計。音の良し悪しは見ていない）
4. docs/Developer.md: 「動き方」の段落、関数表（split_first・chunks）、定数表（CUT）は実際の動きと一致。
   README.md:27 と Developer.md:20 の「1 文目ができたらすぐ鳴らす」は、前半が先に鳴る点で今も正しい。食い違いなし。

## 変更ファイル
TODO.md, docs/Developer.md, src/ccspk/hook.py（未追跡: archives/agents/TODO-025/）。指示の範囲内。差分は hook.py の chunks・コメント・demo() と Developer.md のみで余計な変更なし。

## 確かめなかったこと
テストを壊して落ちるかは依頼に無いので未実施。
