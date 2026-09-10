#!/bin/bash
# ComfyUI 起動（Apple Silicon / MPS）
set -e
COMFY="$HOME/ComfyUI"
export PYTORCH_ENABLE_MPS_FALLBACK=1
cd "$COMFY"
exec ./venv/bin/python main.py --port 8188 "$@"
