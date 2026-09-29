# TODO-043 レビュー報告（reviewer）

対象: `archives/agents/TODO-043/impl.diff`（`git diff` とは `TODO.md` のチェックだけが違う。それ以外は一致を確認）

実測は一時ディレクトリの `XDG_CONFIG_HOME`・`XDG_STATE_HOME`・`XDG_RUNTIME_DIR` で、手元のエンジン（0.25.2）に対して行った。Stop としては動かしていない。

## 要修正

### 1. `docs/Developer.md:445`（4.1 自己テスト）の dict の `demo()` の説明が古い

- 何が問題か: 「dict の `demo()` は、アクセントの位置の決め方（`accent_of`）と、全角から半角へ戻す `halfwidth` を確かめている」のままで、今回足した `pick()` と `speaker()`（一時ディレクトリで）が載っていない
- なぜ問題か: 同じ段落の hook・check の説明は、`demo()` が確かめる関数を漏れなく並べる書き方になっている。TODO-043 の完了条件「`demo()` に例を足し、`docs/Developer.md` に書く」にも当たる。`demo()` と文書は対で保守するもの

## 検討

### 2. エンジンに無い番号がファイルに残ると、読み上げ以外も止まる。文書はそこまで書いていない（境界線上。実害は未確認）

- 該当: `src/ccspk/user_dict.py:69`（`query()` が `speaker()` を使う）、`docs/UsersGuide.md:569`、`docs/Developer.md:332`
- 実測: `speaker` に `99999` を書くと
  - `ccspk speaker` → `99999  （エンジンの話者に無い）`、終了ステータス 0
  - `ccspk dict kana テスト` → `エンジンが断った（500）: {"detail":"Internal Server Error"}`、終了ステータス 1
  - `ccspk say あ` → 鳴らず、`Exception in thread Thread-1 (produce)` のトレースバック、終了ステータス 0（従来の合成失敗と同じ扱い）
  - エンジンは存在しない話者に 422 ではなく 500 を返す（`curl` で `speaker=99999` と `speaker=-3` を確認）
- なぜ問題か: `query()` は `dict kana`・`dict add`（`--speak` なしでもアクセントを決めるのに使う）・読み間違いの点検が使うので、これらもまとめて 500 で失敗する。UsersGuide 3.9 は「読み上げは鳴らない」、Developer.md 332 行は「`dict add --speak` と読み間違いの点検は呼ぶたびに読む」としか書いておらず、`dict kana`・`dict add` が止まることと、500 の表示から話者が原因だと分からないことが抜けている
- 起こりうる経路: エンジンを入れ替えて話者が減った、ファイルを手で書き換えた。`ccspk speaker` 自体は無い番号を書かない
- 直し方の判断（文書に足すだけにするか、`speaker()` を `/speakers` と突き合わせるか）は管理者に任せる

### 3. `src/ccspk/user_dict.py:329` 書き込みが上書きで、読む側と重なると一瞬 119 に戻る（実害は未確認）

- `SPEAKER_FILE.write_text()` はファイルを切り詰めてから書く。その間にフックの子プロセスが `speaker()` を呼ぶと、空の文字列で `ValueError` になり、その 1 回の読み上げだけ 119 で鳴る
- 窓は非常に短く、`ccspk speaker` を打つのと読み上げの開始が重なったときだけ。既存の `summary`・`queue` などは有無だけを見るので同じ問題は無い。一時ファイルに書いて `os.replace` すれば閉じるが、要るかは判断が要る

## 好みの範囲

### 4. `docs/UsersGuide.md:564`（3.9 終了ステータス）の `2` の説明

- `ccspk speaker -3` は click がオプションと見なして 2 で終わる（実測）。書いてある「3 つ以上、または `--list` と一緒に渡した」以外でも 2 になる。3.1 の共通の説明（「引数やオプションの誤り」）で足りるなら、3.9 の `2` の行は「引数の誤り」だけでよい

## 問題なかった観点

- `pick()` の分岐: 番号（全角数字も `isdecimal` と `int` で揃う）、名前だけで最初のスタイル、名前＋スタイル、部分一致は断る、いずれも正しい。`3 ノーマル` のように数字＋スタイルは名前として探して 1 で終わる（実測）
- `speaker()` の既定値への戻り: 無い・ディレクトリ・数でない・非 UTF-8 のバイト列（`UnicodeDecodeError` は `ValueError` の子）で 119 に戻ることを実測
- `speaker_` の引数チェックと終了ステータス: 引数なし 0、`--list x`・3 引数で 2、無い番号・名前で 1、書き込めないディレクトリでは `PermissionError` のトレースバック（`export` と同じく書き込みの失敗はそのまま上げる方針に沿う）
- `SPEAKER` の一本化: `rg -n "speaker|SPEAKER" src` で、`hook.synthesize`（`play()` で 1 回だけ読む）・`say`（`play()` 経由）・`dict add --speak`・`query()`（check.py が使う）の全部が `speaker()` を通る。`hook.py` の `SPEAKER` は消え、`synthesize()` の呼び元は `play()` だけ
- フックの子プロセス: `speaker()` は `OSError`・`ValueError` を全部受けて例外を出さない。合成の失敗は従来どおり produce のスレッドで起き、子プロセスの stderr は DEVNULL。フックの本体（親）は `speaker()` を呼ばない
- 文書のアンカー: UsersGuide 内のリンク 25 種はすべて見出しと一致。他のファイルから UsersGuide の 3.x を指すリンクは無い（Developer.md の `#32-ccspk-hook` などは番号が変わっていない）
- 文書とコードの一致: 3.9 の書式・引数・ファイル・例、1.9、README、Developer.md のファイル表・定数表からの `SPEAKER` 削除は、上の 2 以外は挙動と合う
- `demo()` の強さ: 4 か所を壊して `uv run ccspk test` がすべて落ちることを確認（スタイル省略を `style == s` に、`except` から `ValueError` を外す、番号を文字列で比べる、ファイルを無視して常に `SPEAKER`）。戻した後 `git diff` が impl.diff と一致し、`ok` に戻ることも確認
- 設計・範囲: 一時ディレクトリで定数を差し替える `demo()` の書き方は hook・check と同じ。指示に無い変更は無い
- コメント: `play()` の「読んでいる途中で変えても声は変えない」など、理由を書いている

## 作り込みすぎ

作り込みすぎ: なし（`styles()` は 1 行、`pick()` はテストのために分けてあり、どちらも要る）
