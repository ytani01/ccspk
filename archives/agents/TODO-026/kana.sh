#!/bin/sh
# TODO-026: 品詞を直した単語を含む文を、フックと同じ整形（to_speech）に通してから読みを出す
cd "$(dirname "$0")/../../.." || exit 1
while IFS= read -r s; do
  t=$(.venv/bin/python -c "import sys; from ccspk.hook import to_speech; print(to_speech(sys.argv[1]))" "$s")
  printf '%s\t%s\n' "$s" "$(.venv/bin/ccspk dict kana "$t")"
done <<'SENTENCES'
テストが全部通って、コミットした。
通ってから直す。
LOCK ファイルを消す。
LOCKを取る。
2 文目も短く切る。
3文目まで読む。
辞書の語を直す。
語の品詞を決める。
一時ディレクトリに向ける。
一時ディレクトリを消す。
SENTENCES
