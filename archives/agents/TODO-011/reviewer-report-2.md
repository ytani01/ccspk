# TODO-011 reviewer の報告（2 回目）

対象: `hook.py` の `speak()`（`-P` を足した）と、`docs/Developer.md` の 47・53-58・80・102 行付近。
条件は 1 回目と同じ（`.venv/bin/claudecodespeak`、`XDG_RUNTIME_DIR` は `mktemp -d`、
`PIPEWIRE_REMOTE=x`、偽の `pw-play` を `PATH` の先頭に置いた）。1 回目の (1)(2) の判断事項は見ていない。

## 要修正

なし。

## 検討

### 1. `docs/Developer.md:81` と `src/claudecodespeak/hook.py:40` の「click を通さないので速い」は、測ると 2 ms ほどの差しかない

- 実測（10 回の中央値、cwd は `/`）:
  - `python -P -c pass` 9.7 ms
  - `python -P -m claudecodespeak.hook`（子と同じ import。引数が無いので何もしない）62.6 ms
  - `python -P -m claudecodespeak.cli hook --help`（click を通る）65.0 ms
- なぜ: `hook.py` は先頭で `click` と `.mylog`（loguru）を import するので、子プロセスも
  その分（50 ms ほど）を払う。click で引数を解くのをやめても、得をするのは cli・add_word の import と解析の分だけ
- 実害: 最初の音までの目安（1.2〜2.5 秒）に比べて小さく、動きには影響しない。書いてある理由が
  測った値と合わないだけ。文言を直すか、子を本当に速くするか（click・loguru を import しない）は管理者が決める。
  境界線上なので報告だけ

## 問題なかったもの

- 作業ディレクトリの同名モジュール: `click.py`・`queue.py`・`json.py`・`claudecodespeak.py`（読み込まれたら印のファイルを書く）を
  置いたディレクトリを cwd にして Stop の JSON を渡した。rc=0、印のファイルは 1 つもできず、子のグループ
  （`python -P -m claudecodespeak.hook --play …`・`pw-play`・`sleep`）が 1.5 秒後も動いていた。1 回目で見た問題はもう起きない
- `stop_playing()` の見分け（`-P` あり）: cmdline は `…/python -P -m claudecodespeak.hook --play 確認です。二つ目の文です。`。
  2 回目のフックで前のグループが消え、新しい子に替わった
- 見分けの反対側: `PIDFILE` に `sleep 60` の PID を書いてからフックを走らせても、`sleep` は止まらなかった（`SN` のまま）
- `docs/Developer.md:47`: `claudecodespeak hook` を起動する、でコードと合う
- `docs/Developer.md:53-58`: 表の `--play` の行「合成と再生だけをする。子プロセスと同じ動き」は、`main()` の `--play`
  と `if __name__ == "__main__"` の子が同じ `play()` に入るので合う
- `docs/Developer.md:80-82`: 子の起こし方（`python -P -m claudecodespeak.hook --play <本文>`）と `-P` の理由は、`hook.py:247-249` と合う（速さの記述は上の 1.）
- `docs/Developer.md:102`: 重複を消して「子プロセス」の節を指す形になり、食い違いは無くなった

## 作り込みすぎ

なし（今回の差分は `-P` 1 語とコメント 1 行、文書の書き換えだけ）。
