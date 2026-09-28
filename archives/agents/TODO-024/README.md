# TODO-024 の分担

- main: 実装（`stop_playing()` の戻り値、`stop` サブコマンド、文書 4 か所）。変更が小さいので実装担当は分けない
- reviewer: 戻り値を足して分岐が変わるので、フックの動きが変わっていないか、文書との一致と直し漏れを見る → [reviewer-report.md](reviewer-report.md)
- verifier: 一時の `$XDG_RUNTIME_DIR` で実際に再生を起こし、`ccspk stop` で止まるか、メッセージが分かれるかを確かめる → [verifier-report.md](verifier-report.md)

振り返りは `archives/todo/TODO-024. 読み上げを止める ccspk stop を足す.md`。
