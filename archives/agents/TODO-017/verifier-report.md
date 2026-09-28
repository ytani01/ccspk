# TODO-017 verifier-report

## 検証コマンドと結果

- `uv run claudecodespeak test` → `ok` / `ok`、終了コード 0。通過。
- `.venv/bin/claudecodespeak dict --help` / `dict add --help` / `dict list --help` /
  `dict remove --help` / `dict import --help` → いずれも「単語」に置き換わっており、
  折り返しや文字化けなし。一致。

## 1. 拾い残しの確認

`rg -n -P '(?<![単用言敬国英])語(?!り)' src docs README.md CLAUDE.md` の残り 13 件を
すべて確認した。

- `README.md:21`、`docs/UsersGuide.md:18`、`hook.py:38`、`user_dict.py:32`、
  `docs/Developer.md:157` → 「夜語トバリ」（話者名の固有名詞）。辞書の 1 件ではない。一致。
- `docs/UsersGuide.md:209` → 「日本語の文字」。辞書と無関係。一致。
- `hook.py:43`「name() のように語の中にも出るので」、`hook.py:109`「1 語と読まれない
  よう残す」、`hook.py:188`「語と助詞の間で切れて」、`hook.py:342`（コメント）と
  `docs/Developer.md:26`「語の中の半角「:」「(」では切らない」→ いずれも読み上げ用の
  文の区切り・トークン分割の話（`split_first`・`CUT` 正規表現まわり）で、
  VOICEVOX のユーザー辞書のエントリを指すものではない。周辺コード
  （`hook.py` の `CUT`、`split_first` の docstring とテスト）を読んで確認した。
  main の判断（「文の区切り・トークンの話で辞書の 1 件ではない」）と食い違いは無い。

## 2. 巻き込みの確認

`git diff -- CLAUDE.md README.md docs/Developer.md docs/UsersGuide.md
src/claudecodespeak/user_dict.py` を全行読んだ（TODO.md のチェック 1 件を除き
6 ファイル、変更行は追加・削除ともに 23 行）。

- 変更箇所はすべて辞書の 1 件を指す「語」→「単語」の書き換えで、対象外の
  「日本語」「用語」などを誤って変えた箇所は無かった。
- 「日本単語」のような壊れた語や、不自然な空白の混入も無かった。
- TODO.md 以外に、指示にない意図しないファイルの変更は無かった
  （`git status` の変更ファイルは CLAUDE.md, README.md, TODO.md, docs/Developer.md,
  docs/UsersGuide.md, src/claudecodespeak/user_dict.py の 6 件のみで、TODO-017 の
  対象と一致）。

## 確かめられなかったこと・判断できないこと

- 特になし。境界線上と感じた箇所（hook.py の 4 か所、Developer.md:26）は
  main の判断どおりで、こちらでも食い違いを見つけられなかった。
