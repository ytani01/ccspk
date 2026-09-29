# TODO-041. 文書の言い回しを直し、mermaid の図を入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（書き換えと書き足し）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（書き換えと書き足し）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 50 | 14,442 | 78,466 | 1,754,792 | 72% |
| reviewer | Opus 5.5 | high | 24 | 3,407 | 59,002 | 515,860 | 23% |
| verifier | Sonnet 5.5 | medium | 12 | 1,337 | 24,286 | 118,271 | 6% |
| 合計 |  |  | 86 | 19,186 | 161,754 | 2,388,923 | 計 2,569,949 |

- 立ててから着手までに TODO-049・050 を挟んだので、`--since '2026-09-29 22:06:00'`（着手したやり取りの時刻）で切った
- reviewer・verifier は `~/.claude/agents/` の定義どおり（opus / high、sonnet / medium）
- サブエージェントの分は少なめに出る（Claude Code の報告では reviewer 63,722、verifier 28,669 トークン）

## きっかけ

文書の説明に mermaid の図を入れる規則を `~/.claude/CLAUDE.md` の「日本語の書き方」に足したので、今ある文書に当てはめる。
あわせて、TODO-035 で見つけた言い回しの 4 か所を同じ 2 つの文書で直す（reviewer を 1 回にまとめるため）。

## やったこと

言い回し（先に直し、図はその後の文章に合わせた）:

- `docs/Developer.md`「2. 動き方」: 「1 文目ができたらすぐ鳴らす」と「1 文目の前半ができたらすぐ鳴らす」を、
  「最初の塊（1 文目の前半）ができたらすぐ鳴らす」にまとめた。1・2 文目を切る理由を並べ、
  「切った所は抑揚が下がる」「最初の音までの時間」を別の箇条に分けた
- 同じ節の「`Stop` が空のときは、今までどおり止める」を「空の `Stop` では、前の再生を止める」にした
- `docs/UsersGuide.md`「1.2」: 何もしないのがフックのコマンドだと分かるよう、コマンドを示して書いた
- `docs/UsersGuide.md`「3.3 ccspk say」: 「鳴らし終わってから終わる」を「鳴らし終えるまで戻らない」にした

図:

- `docs/Developer.md`「3.1 流れ」: `main()` の 10 段と途中で終わる分岐、最後の `check.after_stop()` を `flowchart` で。
  図の前に「`LOCK` を取った後で終わるときは、放してから Stop なら `check.after_stop()` を呼ぶ」を 1 文足した
- 「3.2 子プロセス」: フック → 子プロセス → `claude -p` → エンジン → `pw-play` を `sequenceDiagram` で（合成と再生は `par`）
- 「3.8 自動の点検」: Stop → `after_stop()` → 点検の起動 → 読みの取得 → `claude -p` → 登録と書き出しを `sequenceDiagram` で
- `docs/UsersGuide.md` の冒頭: Claude Code・`ccspk`・VOICEVOX エンジン・PipeWire・`claude -p`・辞書のファイルの構成図

## 確かめたこと

- reviewer（[報告](../agents/TODO-041/reviewer-report.md)）: 言い回しの 4 つは意味が変わっていないか、今のコードに合う側に直っている。
  図とコードの食い違いは要修正 0 件、検討 3 件、好み 1 件。4 件とも直した
  （3.8 の `save()` の矢印の向き、`CHECKED` の mtime を点検の始めに控えた値に揃えること、単語が残らないときに `claude -p` を呼ばない分岐、
  構成図の「点検していない読んだ文があれば」）
- verifier（[報告](../agents/TODO-041/verifier-report.md)）: 直した後の 4 枚とも `mmdc` で SVG・PNG に描け、エラー・警告は無い。
  図の中の文字列と SVG の突き合わせで、出なかったものは 0 件
- 3.2 の図で Note が `opt` の枠をはみ出すが、文字は読めるので直さない

## 分担の振り返り

- reviewer は、main が書き写しで済ませた 3.8 の図の細部（`save()` の向き、mtime を控える時点、単語が残らない分岐）を
  コードから拾った。verifier は描画の失敗を見つけなかった（4 枚とも描けた）が、はみ出しを 1 件報告した
- 見込みどおりの編成で、食い違いは無い
- 次に図を入れる項目では、verifier の突き合わせのスクリプト（`archives/agents/TODO-041/extract_check.py`）を使い回し、
  描画の確認は同じく Sonnet に任せる。図がコードの分岐を写すものなら reviewer は外さない。図が 1〜2 枚なら、
  main が `mmdc` を 1 回走らせるだけで verifier の起動分（全体の 6%）を省けるかを、立てるときに見る
