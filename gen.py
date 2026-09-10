#!/usr/bin/env python3
"""ComfyUI の HTTP API を叩いて画像を一括生成する CLI。

  python3 gen.py "1girl, sake brewery, kimono" -n 4
  python3 gen.py "a bottle of japanese sake on wooden table" -m photo -s 1024x1024

サーバは bin/start.sh で先に起動しておくこと。
"""
import argparse, json, pathlib, random, re, sys, time, urllib.request, urllib.error

SERVER = "http://127.0.0.1:8188"
ROOT = pathlib.Path(__file__).resolve().parent

# モデル別プリセット: (ckpt ファイル名, 品質タグ, ネガティブ, 既定steps, 既定cfg)
PRESETS = {
    "illust": dict(
        ckpt="animagine-xl-4.0.safetensors",
        quality="masterpiece, high score, great score, absurdres",
        negative="nsfw, nude, nipples, cleavage, revealing clothes, underwear, "
                 "lowres, bad anatomy, bad hands, text, error, missing finger, "
                 "extra digits, fewer digits, cropped, worst quality, low quality, "
                 "low score, bad score, average score, signature, watermark, username, blurry",
        steps=20, cfg=5.0,
    ),
    "photo": dict(
        ckpt="juggernautXL-v9.safetensors",
        quality="photorealistic, highly detailed, natural lighting, 8k uhd",
        negative="cartoon, anime, illustration, painting, drawing, cgi, 3d render, "
                 "worst quality, low quality, blurry, jpeg artifacts, watermark, text, "
                 "deformed, bad anatomy, extra limbs",
        steps=30, cfg=4.5,
    ),
}


def _open(req_or_url):
    try:
        return json.loads(urllib.request.urlopen(req_or_url).read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:2000]
        sys.exit(f"ComfyUI がエラーを返した (HTTP {e.code}):\n{body}")


def post(path, payload):
    req = urllib.request.Request(SERVER + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return _open(req)


def get(path):
    return _open(SERVER + path)


def build_graph(a, p):
    pos = f"{a.prompt}, {p['quality']}" if not a.raw else a.prompt
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": p["ckpt"]}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": a.negative or p["negative"], "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": a.width, "height": a.height, "batch_size": a.n}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg,
                         "sampler_name": a.sampler, "scheduler": a.scheduler,
                         "denoise": 1.0, "model": ["1", 0],
                         "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAELoader",
              "inputs": {"vae_name": "sdxl_vae.safetensors"}},
        "7": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["6", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": a.tag}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("-m", "--model", default="illust", choices=list(PRESETS), help="illust=アニメ/イラスト photo=写実")
    ap.add_argument("-n", type=int, default=1, help="生成枚数")
    ap.add_argument("-s", "--size", default="1024x1024")
    ap.add_argument("--negative", default="")
    ap.add_argument("--steps", type=int)
    ap.add_argument("--cfg", type=float)
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--sampler", default="dpmpp_2m")
    ap.add_argument("--scheduler", default="karras")
    ap.add_argument("--tag", default="sd", help="出力ファイル名の接頭辞")
    ap.add_argument("--raw", action="store_true", help="品質タグを足さず prompt をそのまま使う")
    ap.add_argument("--timeout", type=int, default=900, help="完了待ちの上限秒")
    ap.add_argument("-o", "--out", default=str(ROOT / "out"))
    a = ap.parse_args()

    p = PRESETS[a.model]
    a.steps = a.steps or p["steps"]
    a.cfg = a.cfg if a.cfg is not None else p["cfg"]
    m = re.fullmatch(r"(\d+)x(\d+)", a.size.lower().strip())
    if not m:
        sys.exit(f"--size の書式が不正: {a.size!r}  例) 1024x1024 / 832x1216")
    a.width, a.height = int(m.group(1)), int(m.group(2))
    if a.width % 8 or a.height % 8 or a.width < 256 or a.height < 256:
        sys.exit(f"--size は256以上・8の倍数であること: {a.width}x{a.height}")
    if a.seed < 0:
        a.seed = random.randint(0, 2**32 - 1)

    try:
        get("/system_stats")
    except urllib.error.URLError:
        sys.exit("ComfyUI が起動していない。先に bin/start.sh を実行すること。")

    t0 = time.time()
    pid = post("/prompt", {"prompt": build_graph(a, p)})["prompt_id"]
    print(f"model={p['ckpt']} seed={a.seed} steps={a.steps} cfg={a.cfg} {a.width}x{a.height} x{a.n}")

    deadline = time.time() + a.timeout
    while True:
        h = get(f"/history/{pid}")
        st = h.get(pid, {}).get("status", {})
        if st.get("completed") or st.get("status_str") in ("success", "error"):
            break
        if time.time() > deadline:
            sys.exit(f"タイムアウト（{a.timeout}秒）。ComfyUI 側のログを確認すること。")
        time.sleep(1.0)

    outdir = pathlib.Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for node in h[pid]["outputs"].values():
        for img in node.get("images", []):
            q = f"/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
            data = urllib.request.urlopen(SERVER + q).read()
            dst = outdir / img["filename"]
            dst.write_bytes(data)
            saved.append(dst)
    if len(saved) != a.n:
        for m in st.get("messages", []):
            print(m, file=sys.stderr)
        sys.exit(f"生成失敗: {a.n}枚要求に対し {len(saved)}枚しか出力されなかった "
                 f"(status={st.get('status_str')})。中断されたか、サーバ側でエラーが出ている。")
    print(f"{time.time()-t0:.1f}s  →  " + "\n           ".join(str(s) for s in saved))


if __name__ == "__main__":
    main()
