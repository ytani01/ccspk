# TODO-026 verifier 報告

最後に import で now.json へ戻し、export と cmp した結果は一致（cmp 終了コード 0）。辞書は作業前の状態に戻っている。

- 手順 2: 5 単語（LOCK・一時ディレクトリ・文目・語・通って）の品詞・優先度・読み・accent_type は README の表どおり。
  VERB=動詞/自立(通って, 優先度 10)、COMMON_NOUN=名詞/一般(LOCK 5・語 7・一時ディレクトリ 8)、SUFFIX=名詞/接尾(文目 7)。読みと accent_type は変更前と同じ。
  ID ごとの突き合わせ: user_dict.before.json と now.json は 47 件で ID 集合が同じ。差があるのはこの 5 件だけ。
- 手順 3: 変更前へ import → kana.sh の出力と kana-before.tsv は diff 空（終了コード 0）。
- 手順 4: now.json へ import → kana.sh の出力と kana-after.tsv は diff 空（終了コード 0）。cmp now.json check.json は一致（0）。
- 手順 5: kana.sh は to_speech を通している。to_speech('2 文目も短く切る。') = '2文目も短く切る。'（空白が消える）。
  変更前は ニア'ヤメモ、変更後は ニ'ブンメモ で、整形後の文が読まれている。
- git status: M TODO.md、?? archives/agents/TODO-026/。コードの変更なし。

食い違い: なし。判断が要る点: なし（TODO.md の差分は範囲外なので見ていない）。
