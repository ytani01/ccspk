# 使い方

## 読み上げの辞書

返答の読み上げ（`hooks/speak-response.py`）で読み間違える語は、VOICEVOX の
エンジンのユーザー辞書で読みを直す。辞書はエンジンの中にあり、その元を
`voicevox/user_dict.json` に置いている。

GUI の VOICEVOX エディタは入れていないので、登録はエンジンの API で行う。
ブラウザから操作するなら `http://127.0.0.1:50021/docs`、コマンドなら `curl`。

### 読みを確かめる

登録する前後に、エンジンがどう読むかを見る。

```sh
curl -s -X POST -G http://127.0.0.1:50021/audio_query \
  --data-urlencode speaker=119 --data-urlencode 'text=TODO.md を直す' | jq -r .kana
```

`'` の直前の音の後で、音が下がる。

### 登録する

```sh
curl -s -X POST -G http://127.0.0.1:50021/user_dict_word \
  --data-urlencode surface=README \
  --data-urlencode pronunciation=リードミー \
  --data-urlencode accent_type=1 \
  --data-urlencode word_type=PROPER_NOUN
```

- `pronunciation` はカタカナ。`--data-urlencode` を使わないと、日本語が
  そのまま URL に入って `Invalid HTTP request received.` で失敗する
- `accent_type` は、音が下がる直前の音が頭から何番目か。1 なら最初の音の後で
  下がる（頭高）、0 なら下がらない（平板）
- 英字は大文字と小文字を別の語として扱う。両方直すなら両方登録する
  （`JSON` と `json`）
- 返ってくる文字列（UUID）が、その語の ID

ブラウザでは、`/docs` の `POST /user_dict_word` を開き、「Try it out」で
同じ値を入れて「Execute」。

### 一覧を見る・消す

```sh
curl -s http://127.0.0.1:50021/user_dict \
  | jq -r 'to_entries[] | "\(.key)  \(.value.surface)  \(.value.pronunciation)"'
curl -s -X DELETE http://127.0.0.1:50021/user_dict_word/<ID>
```

読みを変えるときは、消して登録し直す（`PUT /user_dict_word/<ID>` でもよい）。

### リポジトリに残す

登録や削除をしたら、辞書の元を書き直してコミットする。

```sh
curl -s http://127.0.0.1:50021/user_dict | jq -S . > ~/work/claudecodespeak/voicevox/user_dict.json
```

### 戻す

エンジンを入れ直したときや、別のマシンでは、辞書の元を読み込む。

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  -d @$HOME/work/claudecodespeak/voicevox/user_dict.json \
  'http://127.0.0.1:50021/import_user_dict?override=true'
```

`override=true` は、同じ ID の語があれば上書きする。辞書にあってファイルに
無い語は消えずに残る。

### 記号と数字

辞書で直せないものは、`hooks/speak-response.py` の `to_speech` で置き換えている。

- 「〜」「～」「→」は「から」にする。前後のスペースも消す（`1 〜 4` → `1から4`）
- 半角の「~」は、数字に挟まれたときだけ「から」にする（`1~4` → `1から4`）
- 数字の直後のスペースは、同じ行で日本語の文字が続くときだけ消す
  （`180 字` → `180字`）。全角数字も同じ
