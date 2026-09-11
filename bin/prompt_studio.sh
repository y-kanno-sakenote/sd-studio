#!/bin/bash
# プロンプト工房を起動する。ジャンルごとに別ポート・別プロセス。
#   bin/prompt_studio.sh            → 醸造・日本酒（既定）
#   bin/prompt_studio.sh fantasy    → ファンタジー
#   bin/prompt_studio.sh --list     → 使えるジャンル一覧
# Streamlitは jbsj の venv を間借りしている（蔵元司令室と同じ方式）
set -e
ROOT="/Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio"
PY="/Users/ymacmini/Documents/claudecode@macmini/dev/jbsj/.venv/bin/python"
GENRE="${1:-brewing}"; shift 2>/dev/null || true

if [ "$GENRE" = "--list" ] || [ "$GENRE" = "-l" ]; then
  "$PY" - "$ROOT" <<'PYEOF'
import sys, pathlib, importlib
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "genres"))
import _common
print("ジャンル        ポート  名前")
for f in sorted((root / "genres").glob("*.py")):
    if f.stem.startswith("_"): continue
    try:
        g = _common.load(f.stem)
        print(f"{f.stem:14s} {g.PORT}  {g.TITLE}")
    except Exception as e:
        print(f"{f.stem:14s}   --   読み込み失敗: {e}")
PYEOF
  exit 0
fi

PORT=$("$PY" -c "
import sys; sys.path.insert(0,'$ROOT/genres')
import _common
try: print(_common.load('$GENRE').PORT)
except Exception as e: print('ERR:'+str(e))
")
case "$PORT" in
  ERR:*) echo "起動できない: ${PORT#ERR:}"; echo "使えるジャンルは bin/prompt_studio.sh --list"; exit 1;;
esac

echo "プロンプト工房（$GENRE） → http://localhost:$PORT"
SD_STUDIO_GENRE="$GENRE" exec "$PY" -m streamlit run "$ROOT/prompt_studio.py" --server.port "$PORT" "$@"
