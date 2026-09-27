# TODO-001 の分担

[TODO-001](../../todo/TODO-001.%20Claude%20の返答を%20VOICEVOX%20で読み上げる.md)

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装、エンジンの導入と切り替え、話者の聞き比べ | — |
| reviewer（1 回目） | 差分全体の分岐と設計 | [reviewer-report.md](reviewer-report.md) |
| reviewer（2 回目、同じ担当に続けて依頼） | 1 回目の指摘の直しと、エンジンの差し替え | [reviewer-report-2.md](reviewer-report-2.md) |
| verifier | 本物の `claude -p` での Stop hook を含む 9 項目の実測 | [verifier-report.md](verifier-report.md) |

## 分担にした理由

- 実装は 1 ファイルの小さいスクリプトなので main が持った
- hook の分岐（鳴らす／鳴らさない、前の再生を止める）と、プロセスグループへの
  kill があるので reviewer を入れた
- 音が出るかは利用者が耳で確かめたので、verifier には PID と cmdline で
  判定できるものだけを頼んだ（声の品質は見させない）
- reviewer を先、verifier を後に回した
