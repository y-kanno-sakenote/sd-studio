# 担当: 検証係 — PNGのバイト列hashと「画素のみ」hashを両方出す（メタデータ差と画素差を切り分ける）
import hashlib, sys
from PIL import Image
for p in sys.argv[1:]:
    b = open(p, "rb").read()
    im = Image.open(p).convert("RGB")
    print(f"{p.split('/')[-1]:24s} bytes={hashlib.sha256(b).hexdigest()[:16]} "
          f"pixels={hashlib.sha256(im.tobytes()).hexdigest()[:16]} size={im.size}")
