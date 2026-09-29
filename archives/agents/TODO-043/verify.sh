#!/bin/zsh
cd /home/ytani/work/ccspk
S=/tmp/claude-649/-home-ytani-work-ccspk/02ea16d1-85da-4c91-b122-8492a0d5f5ad/scratchpad/v43
\rm -rf $S; mkdir -p $S/c $S/s $S/r
export XDG_CONFIG_HOME=$S/c XDG_STATE_HOME=$S/s XDG_RUNTIME_DIR=$S/r
C=.venv/bin/ccspk; F=$S/c/ccspk/speaker
run(){ echo "\$ ccspk $*"; $C "$@"; echo "[exit $?]"; }
echo "== 1"; uv run ccspk test; echo "[exit $?]"
echo "== 2"; run speaker; run speaker 3; cat $F; run speaker ずんだもん; cat $F; run speaker 夜語トバリ 呆れ; cat $F; find $S/c
echo "== 3"; for a in "99999" "存在しない名前" "夜語トバリ ツンツン" "a b c" "--list 3"; do run speaker ${(z)a}; cat $F; done
echo "== 4"; run speaker --list | rg -vc '^\$|^\[exit'; curl -s --max-time 5 127.0.0.1:50021/speakers | python3 -c 'import json,sys;print(sum(len(p["styles"]) for p in json.load(sys.stdin)))'
echo "== 5"; echo x > $F; run speaker
echo "== 6"; echo 3 > $F
cat > $S/six.py <<'PY'
import ccspk.hook as h, ccspk.user_dict as u
urls=[]
def fake(req,*a,**k):
    urls.append(req.full_url if hasattr(req,'full_url') else req); raise RuntimeError("stop")
h.urllib.request.urlopen=fake
try: h.play("テスト。")
except Exception as e: print("play exc",e)
import time; time.sleep(1)
print("play url:",urls[:1])
args=[]
u.call=lambda *a,**k:(args.append((a,k)),b"{}")[1]
u.query("テスト"); print("query:",args)
PY
.venv/bin/python $S/six.py
\rm $F; .venv/bin/python $S/six.py
