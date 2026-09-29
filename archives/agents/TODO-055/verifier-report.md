# TODO-055 verifier report

## 1. 実測（CCSPK_SPEAK が子プロセスに届くか）
指示のコマンドはそのままでは失敗した。`--allowedTools` が可変長引数で、末尾のプロンプトまで取り込まれたため。

    Error: Input must be provided either through stdin or as a prompt argument when using --print
    (exit=1)

プロンプトを先頭に移して再実行した（オプションは同じ）。

    cd "$(mktemp -d)" && CCSPK_SPEAK=0 claude -p 'Run exactly: printenv CCSPK_SPEAK . Reply with only its output.' --model haiku --setting-sources "" --no-session-persistence --allowedTools 'Bash(printenv:*)'; echo "exit=$?"

出力:

    0
    exit=0

結果: `0` が返った。「`--setting-sources ""` の claude -p には 0 がそのまま届く」は実測で合った。
「settings.json を読む claude -p では env が上書きして 1 に戻る」の側は今回は測っていない（依頼外）。

## 2. git diff docs/Developer.md
- 変更ファイル: `docs/Developer.md`、`TODO.md`（開始時から変更済み。TODO.md は依頼の範囲外なので中身は見ていない）。
- 消した行: 手順 1 内の 4 行（読み上げが起きない理由 / CCSPK_SPEAK=0 は念のため / env が上書き / 点検の claude -p も同じ）。これ以外の行は消えていない。
- 足した行: 手順 5 の後ろ、空行を挟んだインデント無しの独立段落 5 行 + 空行。手順 1〜5 の文に欠けも重複も無い。
- 移した段落以外の変更: 無い（diff は 2 つのハンクのみ、上記の削除と追加だけ）。
- 手順の中に移した段落の文は残っていない。
- 番号付きリストの続き: 手順 1 の「…`stop_playing()` で一緒に止まる。」の次の行が、同じ 3 スペースのインデントの「終了コードが 0 なら…」で、手順 1 に繋がる。手順 2 は ` 2.` のまま。
- 内容の変化（意図どおり）: 「念のためで、これだけでは止まらない」は「settings.json を読まないので、足した CCSPK_SPEAK=0 もそのまま子プロセスに届く。効かないのは settings.json を読む claude -p の場合」に変わった。参照先（UsersGuide の 1.3）と check.py への言及は残っている。

## 判断できなかったこと
- 実測のコマンド自体が指示のままでは動かなかった点（上記）。文書側の問題ではない。
