#!/bin/bash
# ComfyUI 起動（Apple Silicon / MPS）
#   bin/start.sh          localhost のみ（既定）
#   bin/start.sh --remote localhost ＋ Tailscale の自分のIPだけに開く
#                         （同じWi-Fiの他人には見えない。公開もしない）
#   bin/start.sh stop     止める
set -e
COMFY="$HOME/ComfyUI"

# ポートで見つけて止める（プロセス名での pkill は取りこぼす＝古いのが生き残り、
# 新しい方がポートを取れずに黙って死ぬ）
if [ "$1" = "stop" ]; then
  PIDS=$(lsof -nP -tiTCP:8188 -sTCP:LISTEN 2>/dev/null || true)
  [ -n "$PIDS" ] && kill $PIDS && echo "ComfyUI 停止" || echo "動いていない"
  exit 0
fi
OLD=$(lsof -nP -tiTCP:8188 -sTCP:LISTEN 2>/dev/null || true)
if [ -n "$OLD" ]; then
  echo "8188 を使っている古いプロセスを止める ($OLD)"
  kill $OLD; sleep 3
fi
TS="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
export PYTORCH_ENABLE_MPS_FALLBACK=1

LISTEN=""
if [ "$1" = "--remote" ]; then
  shift
  TSIP=$("$TS" ip -4 2>/dev/null | head -1 || true)
  if [ -z "$TSIP" ]; then
    echo "Tailscale が動いていないので localhost のみで起動する"
  else
    LISTEN="--listen 127.0.0.1,$TSIP"
    echo "外部ブラウザから → http://$TSIP:8188  （Tailscale に繋いだ端末だけ）"
  fi
fi

cd "$COMFY"
exec ./venv/bin/python main.py --port 8188 $LISTEN "$@"
