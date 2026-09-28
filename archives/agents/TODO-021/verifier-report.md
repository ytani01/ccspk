# TODO-021 verifier 報告

コードは直していない。食い違いは無かった。

## 1. XDG_CONFIG_HOME を一時ディレクトリへ（umask 022）
- dict add ZZTEST: 一致。ファイルに `"surface": "ZZTEST"`（半角）、権限 644、`.tmp` 無し（ディレクトリは user_dict.json のみ）、41 単語
- dict remove ZZTEST: 一致。ファイルから消えた（`rg -c` が 1 件も無し）
- dict import <そのファイル>: 一致。「読み込んだ」「書き出した: <一時>/ccspk/user_dict.json」、`.tmp` 無し
- エンジンの `dict list` に ZZTEST（全角・半角とも）無し: 一致

## 2. DICT_FILE
- `XDG_CONFIG_HOME=`（空）・未設定とも `/home/ytani/.config/ccspk/user_dict.json`: 一致（.venv/bin/python で読んだ）

## 3. restart
- daemon-reload → restart 1 回: 1.35 秒で戻った、`is-active` は active
- journal に「読み込んだ」「書き出した: /home/ytani/.config/ccspk/user_dict.json」あり、`POST /import_user_dict 204`
- 本物の辞書は 40 単語のまま、md5 は作業の前後で同じ（b35a4567…）。エンジンの `dict list` も 40 行

## 4. UsersGuide の例
- `dict export backup.json`: 終了コード 0、40 単語、20096 バイト
- `dict import backup.json`: 終了コード 0。一時の `ccspk/user_dict.json` が backup.json と `cmp` で同一
- 本物の辞書は変わっていない

## 変更ファイル
CLAUDE.md, README.md, TODO.md, docs/UsersGuide.md, src/ccspk/user_dict.py, systemd/voicevox-engine.service、`voicevox/user_dict.json` の削除（staged）、未追跡 archives/agents/TODO-021/。TODO-021 の項目と合っている。中身の範囲の突き合わせ以上はしていない。

## 確かめていないこと
- `uv run ccspk test` は指示に無いので走らせていない
- restart は 1 回だけ（エンジン起動直後に応答待ちが働く経路は、journal で 1 回分見た）
