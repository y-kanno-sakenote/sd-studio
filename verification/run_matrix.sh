#!/bin/bash
# 担当: 検証係 — gen.py 実測マトリクス（順次実行・各runの壁時計を記録）
cd /Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio
run () { # $1=label 残りはgen.py引数
  local label="$1"; shift
  echo "===== $label : $(date +%T)"
  /usr/bin/time -p python3 gen.py "$@" 2>&1
  echo "===== $label end : $(date +%T)"
}
P="1girl, sake brewery, kimono"
run A_repro1  "$P" --seed 12345 -s 1024x1024 --tag rep
run B_bust    "$P" --seed 999   -s 1024x1024 --tag bust
run C_repro2  "$P" --seed 12345 -s 1024x1024 --tag rep
run D_batch4  "$P" --seed 4444  -s 1024x1024 -n 4 --tag b4
run E_832     "$P" --seed 777   -s 832x1216  --tag r832
run F_1536    "$P" --seed 777   -s 1536x1536 --tag r1536
echo "ALL DONE $(date +%T)"
