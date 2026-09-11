#!/bin/bash
# 全ジャンルのプロンプト工房を立ち上げて、入口ページを開く。
#   bin/studios.sh          起動して入口を開く（動いているものはそのまま）
#   bin/studios.sh stop     全部止める
set -e
ROOT="/Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio"
PY="/Users/ymacmini/Documents/claudecode@macmini/dev/jbsj/.venv/bin/python"

if [ "$1" = "stop" ]; then
  # ポートで見つけて止める（プロセス名の pkill は取りこぼしがある）
  PIDS=$(lsof -nP -tiTCP:8511,8512,8513,8514,8515 -sTCP:LISTEN 2>/dev/null || true)
  [ -n "$PIDS" ] && kill $PIDS && echo "全ジャンル停止" || echo "動いているものは無かった"
  exit 0
fi

GENRES=$("$PY" -c "
import sys,pathlib; sys.path.insert(0,'$ROOT/genres')
import _common
for f in sorted(pathlib.Path('$ROOT/genres').glob('*.py')):
    if f.stem.startswith('_'): continue
    try:
        g=_common.load(f.stem); print(f'{f.stem}\t{g.PORT}\t{g.TITLE}\t{g.ICON}')
    except Exception: pass
")

printf "%-12s %-6s %s\n" ジャンル ポート 状態
while IFS=$'\t' read -r name port title icon; do
  if curl -s -o /dev/null --max-time 1 "http://localhost:$port"; then
    printf "%-12s %-6s 起動済み\n" "$name" "$port"
  else
    SD_STUDIO_GENRE="$name" nohup "$PY" -m streamlit run "$ROOT/prompt_studio.py" \
      --server.port "$port" --server.headless true > "/tmp/sd-studio_$name.log" 2>&1 &
    printf "%-12s %-6s 起動中…\n" "$name" "$port"
  fi
done <<< "$GENRES"

# Tailscale が動いていれば、入口のリンクをそのIPにする（このMacからも他端末からも同じURLで開ける）
TSIP=$(/Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4 2>/dev/null | head -1 || true)
HOSTNAME_FOR_LINKS="${TSIP:-localhost}"
[ -n "$TSIP" ] && echo "外部ブラウザから → http://$TSIP:8511 など（Tailscale に繋いだ端末だけ）"

# 入口ページを、いま存在するジャンルから組み立てる
"$PY" - "$ROOT" "$HOSTNAME_FOR_LINKS" <<'PYEOF'
import sys, pathlib, html
root = pathlib.Path(sys.argv[1]); host = sys.argv[2]
sys.path.insert(0, str(root / "genres"))
import _common
cards = []
for f in sorted((root / "genres").glob("*.py")):
    if f.stem.startswith("_"):
        continue
    try:
        g = _common.load(f.stem)
    except Exception:
        continue
    n = sum(len(v) for v in g.VOCAB.values())
    cards.append(f'''<a class="card" href="http://{host}:{g.PORT}" target="_blank">
      <div class="icon">{g.ICON}</div>
      <div class="name">{html.escape(g.TITLE)}</div>
      <div class="meta">:{g.PORT} ・ 語彙{n}</div></a>''')
(root / "studios.html").write_text(f'''<!doctype html><meta charset="utf-8">
<title>プロンプト工房</title>
<style>
 :root {{ color-scheme: light dark; }}
 body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 48px 32px;
        background: #14110f; color: #f2ece4; }}
 h1 {{ font-size: 20px; font-weight: 600; margin: 0 0 4px; letter-spacing: .04em; }}
 p.sub {{ color: #9c9187; font-size: 13px; margin: 0 0 32px; }}
 .grid {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
         max-width: 900px; }}
 .card {{ display: block; padding: 22px 18px; border: 1px solid #332c26; border-radius: 12px;
         background: #1c1815; text-decoration: none; color: inherit; transition: .15s; }}
 .card:hover {{ border-color: #7a6247; background: #241e19; transform: translateY(-2px); }}
 .icon {{ font-size: 30px; line-height: 1; }}
 .name {{ margin-top: 12px; font-size: 15px; font-weight: 600; }}
 .meta {{ margin-top: 3px; font-size: 11px; color: #8b8078; letter-spacing: .03em; }}
 .comfy {{ margin-top: 34px; font-size: 13px; }}
 .comfy a {{ color: #c8a678; }}
</style>
<h1>プロンプト工房</h1>
<p class="sub">日本語で選ぶと英語のプロンプトができる。ComfyUI のプロンプト欄に貼って使う。</p>
<div class="grid">{"".join(cards)}</div>
<p class="comfy">▸ <a href="http://{host}:8188" target="_blank">ComfyUI（生成する場所）</a><br><span style="color:#6d645d">ComfyUI を他端末から使うときは <code>bin/start.sh --remote</code> で起動する</span></p>
''', encoding="utf-8")
print(f"入口ページ: {root/'studios.html'}")
PYEOF

sleep 4
open "$ROOT/studios.html"
