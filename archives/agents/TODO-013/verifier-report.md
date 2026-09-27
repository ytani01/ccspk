# TODO-013 verifier report

作業ディレクトリ: `/home/ytani/.claude`。VOICEVOX エンジンは `http://127.0.0.1:50021`
で稼働中（`version` = `"0.25.2"`）。

## 1. `python3 hooks/speak-response.py --test`

```
$ timeout 30 python3 hooks/speak-response.py --test
ok
EXIT:0
```

通った。

## 2. readings.md の「後」の再現

`archives/agents/TODO-013/check-readings.py` を新しく作った（既存の
`kana.py` は「語」をそのまま投げるだけなので、これは `to_speech` を通してから
`audio_query` の `kana` を取って `readings.md` の「後」列と突き合わせる）。

```
$ python3 archives/agents/TODO-013/check-readings.py
一致: 59 件
```

59 行（表の全データ行）すべて一致。食い違いは 0 件。

`MELPA` の読み（表に無い語）も確かめた。

```
to_speech: MELPA
kana: メ'ルパ
```

「メルパ」になった。

## 3. `curl .../user_dict` と `voicevox/user_dict.json` の一致

```
$ curl -s http://127.0.0.1:50021/user_dict | jq -S . > /tmp/.../user_dict_live.json
$ jq -S . voicevox/user_dict.json > /tmp/.../user_dict_repo.json
$ diff /tmp/.../user_dict_live.json /tmp/.../user_dict_repo.json && echo IDENTICAL
IDENTICAL
```

完全に一致した。

## 4. UsersGuide の「読み上げの辞書」節のコマンドを実際に実行

すべて `docs/UsersGuide.md` に書かれたコマンドどおりに実行した。

- **読みを確かめる**: `TODO.md を直す` → `トゥ'ウドゥウ、エ'ム/ディ'イ、オ'/ナオ'ス`
- **登録する**（`surface=ZZTEST`、未使用の語）: 登録前は
  `ZZTEST` → `ズィ'イズィイティイイイエスティイ`（1 字ずつ）、登録後は
  `ザ'ッテ_スト` に変わった。読みが変わることを確認した
  （手順は 登録→delete で未登録の読みを確認→再登録、の順で行った。
  最終的な ID は `3128ad73-d92b-456a-a597-8bb8a2f7f377`）
- **一覧を見る**: `curl .../user_dict | jq -r ...` で 7 件（登録済み 6 語 +
  ZZTEST）を確認
- **消す**: `curl -X DELETE .../user_dict_word/3128ad73-...` → `HTTP:204`。
  一覧を取り直すと ZZTEST が消え、元の 6 語に戻った
- **戻す**（`import_user_dict?override=true`）: `HTTP:204`。実行後、
  `curl .../user_dict | jq -S .` と `voicevox/user_dict.json` を再度 diff し、
  `IDENTICAL_TO_REPO` を確認した。辞書は 3 と同じ状態に戻っている

README の手順以外で辞書を変える操作はしていない。

`/docs` は `curl -s -o /dev/null -w "HTTP:%{http_code}\n" http://127.0.0.1:50021/docs`
で `HTTP:200`。ブラウザでの実際の Try it out 操作は行っていない（依頼どおり
200 だけ見た）。

## 5. .gitignore と README のリンク

```
$ git check-ignore voicevox/user_dict.json; echo $?
1
$ git check-ignore docs/UsersGuide.md; echo $?
1
```

両方とも exit 1（無視されていない = 許可されている）。`git status --porcelain`
でも両方 `??`（追跡対象候補）として出ている。

README.md の 2 か所のリンク（38 行目、76 行目）はいずれも
`docs/UsersGuide.md#読み上げの辞書` を指し、`docs/UsersGuide.md` の 3 行目に
`## 読み上げの辞書` の見出しがある。一致している。

## 変更ファイルと指示の範囲

`git status` / `git diff` で見えたのは次のとおりで、TODO-013 の範囲と合っている。

- 変更: `.gitignore`（voicevox/ の除外規則）、`README.md`（辞書とリンクの説明）、
  `TODO.md`（チェックと決定事項）、`hooks/speak-response.py`（記号の置き換えと
  数字直後スペースの処理、テストの追加）
- 未追跡（新規）: `voicevox/user_dict.json`、`docs/UsersGuide.md`、
  `archives/agents/TODO-013/`（`readings.md`、`kana.py`、今回追加した
  `check-readings.py`、この報告）

指示に無いファイルの変更は見当たらなかった。

## 確かめられなかったこと・判断できなかったこと

- 音を実際に鳴らして耳で聞く確認はしていない（依頼どおり、聞くことは対象外）
- `readings.md` に載っている読み（カタカナ）が「正しい日本語の読みとして
  自然か」は判断していない（利用者が決めた事柄で、verifier の対象外）
- ブラウザから `/docs` の Try it out を実際にクリックして動かす確認はして
  いない。API を `curl` で直接叩いて同じエンドポイントの挙動は確認したので、
  ページが返る（200）以外の実害は未確認
- `to_speech` の正規表現の設計そのものの良し悪し（reviewer 済みとのことなので
  対象外とした）は見ていない
