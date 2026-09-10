#!/bin/bash
# 担当: 検証係 — キュー滞留・タイムアウト残留ジョブの実測
cd /Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio
P="1girl, sake brewery, kimono"
echo "== T1 同時2本（キュー滞留）: $(date +%T)"
( python3 gen.py "$P" --seed 555 --tag q1 > verification/q1.txt 2>&1; echo "q1 exit=$?" >> verification/q1.txt ) &
( python3 gen.py "$P" --seed 666 --tag q2 > verification/q2.txt 2>&1; echo "q2 exit=$?" >> verification/q2.txt ) &
wait
cat verification/q1.txt verification/q2.txt
echo "== T2 timeout残留: $(date +%T)"
python3 gen.py "$P" --seed 888 --tag tmo --timeout 5; echo "tmo exit=$?"
curl -s http://127.0.0.1:8188/queue | python3 -c "import json,sys;d=json.load(sys.stdin);print('running',len(d['queue_running']),'pending',len(d['queue_pending']))"
echo "== T3 -n 0: $(date +%T)"
python3 gen.py "$P" -n 0 --tag zero; echo "n0 exit=$?"
echo "QDONE $(date +%T)"
