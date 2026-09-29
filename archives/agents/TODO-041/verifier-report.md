# TODO-041 verifier 報告

## 結果
4 枚とも mmdc で SVG・PNG に変換できた。エラー・警告なし、SVG に "Syntax error" / "Parse error" なし。

## 実行したコマンド
- `python3 archives/agents/TODO-041/extract_check.py extract $W`
  - 抜き出し: dev1（flowchart TD）、dev2・dev3（sequenceDiagram）、ug1（flowchart LR）。`$W` は scratchpad/todo041
- `npx -y -p @mermaid-js/mermaid-cli mmdc -p pp.json -i X.mmd -o X.svg`（と `.png`）を 4 枚とも実行。pp.json は `{"args":["--no-sandbox"]}`。出力は "Generating single mermaid chart" だけ
- `python3 archives/agents/TODO-041/extract_check.py check $W`（.mmd の文字列と SVG のテキストを空白除去で突き合わせ）

## 図ごと
| 図 | 描けた | 突き合わせで出なかった文字列 | 読めない所 |
|---|---|---|---|
| Developer.md 1 枚目（hook の流れ） | 描けた | 0 件（22 件を照合） | 無し。縦に長く（原寸 784x3725）文字は小さいが読める |
| Developer.md 2 枚目（speak の子プロセス） | 描けた | 0 件（14 件） | 無し。Note「to_speech() で整えて切る。…」が opt 枠の縦線をはみ出すが、文字は読める（実害は未確認） |
| Developer.md 3 枚目（check） | 描けた | 0 件（24 件） | 無し |
| UsersGuide.md 冒頭 | 描けた | 0 件（18 件） | 無し。全体が小さく、矢印ラベルは PNG では小さい字だが欠けや重なりは無い |

## 補足
- 最初の照合は 30 件ほど「出ない」と出たが、引用符付きラベルの引用符ごと突き合わせた、照合スクリプトの不具合。スクリプトを直して再実行し、上表の 0 件になった。抜けではない
- 照合はテキストの有無だけ。接続（矢印の向き）の正否は見ていない（依頼の範囲外）
- 「(--after=)」等の表記が SVG 上で「(--after=)」のまま出ていることは照合で確認済み

## 変更ファイル
verifier が追加したのは `archives/agents/TODO-041/extract_check.py` と本ファイルだけ。docs は触っていない。
