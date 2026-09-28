# verifier 報告 TODO-024（ccspk stop）

環境: エンジン 127.0.0.1:50021 は動作中（version 0.25.2）。`XDG_RUNTIME_DIR` は mktemp -d、`PIPEWIRE_RUNTIME_DIR=/run/user/$(id -u)`。テスト後に \rm -r で削除。

1. 合う。10 文で hook（rc=0）、1.5 秒後 `ccspk.pid`=63739。
   `ps -g 63739`: 63739 (python -m ccspk.hook --play …) と 63742 (pw-play -)。
   `ccspk stop` → 「止めた」rc=0。直後 `ps -g 63739` は見出しのみ（プロセスなし）、`ccspk.pid` 無し（ls: No such file）。tmp に残ったのは ccspk.last と ccspk.lock。
2. 合う。続けて stop → 「鳴っていない」rc=0。
3. 合う。pid ファイル無し → 「鳴っていない」。`ccspk.pid` に無関係な `sleep 30`（PID 63761）を書く → 「鳴っていない」、`ps` で `63761 SN sleep 30` が生存。pid ファイルは消えた（既存の stop_playing() の動作。先に unlink する）。
4. 合う。`chmod 000 ccspk.lock`（uid 649、root ではない）で stop → traceback なし、「鳴っていない」、rc=0。
   参考: そのあと同じ文で hook（rc=0）→ 1 秒後 stop は「鳴っていない」。ただしこれは 5 秒以内の同じ文の重複防止（LAST）か、lock 不可で再生を起こさなかったのか、切り分けていない（実害は未確認。stop の項目の範囲外の可能性が高い）。
5. 合う。`uv run ccspk test` rc=0。`ccspk --help` に「stop    鳴っている読み上げを止める（エンジンの合成は止めない）。」が出る。
6. 合う。UsersGuide のコマンド `ccspk stop`、表示「止めた」「鳴っていない」は実際と一致。
   未確認: 「最初の音を待っているあいだも含む」（合成待ちの間に止まるか）は実測していない。1 の測定は pw-play が起動済みの状態だった。

## 変更ファイル
CLAUDE.md, docs/Developer.md, docs/UsersGuide.md, src/ccspk/cli.py, src/ccspk/hook.py（と未追跡の archives/agents/TODO-024/）。TODO の指示範囲と一致。指示外のファイルなし。テストコード（demo()）への追加は差分に無い（指示にも無い）。
