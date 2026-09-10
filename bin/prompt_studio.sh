#!/bin/bash
# プロンプト工房を起動（http://localhost:8511）
# Streamlitは jbsj の venv を間借りしている（蔵元司令室と同じ方式）
exec /Users/ymacmini/Documents/claudecode@macmini/dev/jbsj/.venv/bin/python -m streamlit run \
  /Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio/prompt_studio.py \
  --server.port 8511 "$@"
