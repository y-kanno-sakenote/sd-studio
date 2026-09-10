#!/bin/bash
# 担当: 検証係 — gen.py 修正版の再検証（実サーバ・順次実行）
cd /Users/ymacmini/Documents/claudecode@macmini/dev/sd-studio
run () {
  local label="$1"; shift
  echo "===== $label : $(date +%T)"
  /usr/bin/time -p python3 gen.py "$@" 2>&1
  echo "----- $label exit=$? end=$(date +%T)"
}
P="1girl, sake brewery, kimono"
run A_repro1  "$P" --seed 12345 -s 1024x1024 --tag rp1
run B_break   "$P" --seed 999   -s 1024x1024 --tag cb
run C_repro2  "$P" --seed 12345 -s 1024x1024 --tag rp2
run D_n2      "$P" --seed 4444  -s 1024x1024 -n 2 --tag n2
run E_832     "$P" --seed 777   -s 832x1216  --tag r832
run F_ns20a   "$P" --seed 101   -s 1024x1024 -n 4 --tag ns20a
run G_ns20b   "$P" --seed 202   -s 1024x1024 -n 4 --tag ns20b
run H_s28     "$P" --seed 101   -s 1024x1024 -n 2 --steps 28 --tag s28
echo "ALL DONE $(date +%T)"
