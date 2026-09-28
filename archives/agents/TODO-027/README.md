# TODO-027 の分担

- main — UsersGuide.md の書き直し（文書だけで、実装の担当を分けるほどの規模ではない）
- reviewer（Opus 5.5 / high） — 手順の節からコマンドの節へ説明を移したので、移した説明が
  今のコード・`--help` と合っているか、同じ説明が 2 か所に残っていないか、落ちた説明が無いかを見る
- verifier（Sonnet 5.5 / medium） — コマンドの節の書式・例・終了ステータスを書いたとおりに試す。
  reviewer の指摘で文書が変わるので、reviewer の後に回す

着手前に main が例の出力を取るとき、登録済みだった `ccspk` を `dict add` で書き換えてから
`dict remove` で消してしまった。`~/.config/ccspk/user_dict.json`（一時ディレクトリに向けて
いたので無傷）を `dict import` して戻し、エンジンの辞書とファイルが一致することを確かめた。
verifier の依頼には、試す単語が未登録かを先に確かめること、終わったらエンジンの辞書が
元と一致するかを確かめることを入れる。

報告:

- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)
