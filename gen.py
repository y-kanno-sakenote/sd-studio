#!/usr/bin/env python3
"""ComfyUI の HTTP API を叩いて画像を一括生成する CLI。

  python3 gen.py "1girl, sake brewery, kimono" -n 4
  python3 gen.py "a bottle of japanese sake on wooden table" -m photo -s 1024x1024

サーバは bin/start.sh で先に起動しておくこと。
"""
import argparse, atexit, json, os, pathlib, random, re, sys, tempfile, time, urllib.parse, urllib.request, urllib.error

SERVER = "http://127.0.0.1:8188"
ROOT = pathlib.Path(__file__).resolve().parent

# モデル別プリセット: (ckpt ファイル名, 品質タグ, ネガティブ, 既定steps, 既定cfg)
PRESETS = {
    "illust": dict(
        ckpt="animagine-xl-4.0-opt.safetensors",
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
    src = ["9", 0] if a.lora else ["1", 0]   # LoRA があれば model/clip は LoraLoader 経由
    clip = ["9", 1] if a.lora else ["1", 1]
    g = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": (a.ckpt or p["ckpt"])}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": pos, "clip": clip}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": a.negative or p["negative"], "clip": clip}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": a.width, "height": a.height, "batch_size": a.n}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg,
                         "sampler_name": a.sampler, "scheduler": a.scheduler,
                         "denoise": 1.0, "model": src,
                         "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAELoader",
              "inputs": {"vae_name": "sdxl_vae.safetensors"}},
        "7": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["6", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": a.tag}},
    }
    if a.lora:
        g["9"] = {"class_type": "LoraLoader",
                  "inputs": {"lora_name": a.lora, "strength_model": a.lora_w, "strength_clip": a.lora_w,
                             "model": ["1", 0], "clip": ["1", 1]}}
    if a.ref_name:
        # 手本の画像を IP-Adapter（ComfyUI_IPAdapter_plus）で読ませ、KSampler の model を差し替える。
        # 既定の「style transfer」は絵柄だけを寄せ、手本の構図や中身は写さない（個人利用・模写にしないため）
        g["10"] = {"class_type": "LoadImage", "inputs": {"image": a.ref_name}}
        g["11"] = {"class_type": "IPAdapterUnifiedLoader",
                   "inputs": {"model": src, "preset": "PLUS (high strength)"}}
        g["12"] = {"class_type": "IPAdapterAdvanced",
                   "inputs": {"model": ["11", 0], "ipadapter": ["11", 1], "image": ["10", 0],
                              "weight": a.ref_w, "weight_type": REF_MODES[a.ref_mode],
                              "combine_embeds": "concat", "start_at": 0.0, "end_at": 1.0,
                              "embeds_scaling": "V only"}}
        g["5"]["inputs"]["model"] = ["12", 0]
    if a.face_name:
        # 顔の手本（Aの顔のあたりを切り抜いた画像がよく効く）。全身の手本があればその後ろにつなぐ
        g["13"] = {"class_type": "LoadImage", "inputs": {"image": a.face_name}}
        g["14"] = {"class_type": "IPAdapterUnifiedLoader",
                   "inputs": {"model": g["5"]["inputs"]["model"], "preset": "PLUS FACE (portraits)"}}
        if a.ref_name:   # 全身の手本と画像の読み取り役（CLIP vision）を共有して、メモリに二重に載せない
            g["14"]["inputs"]["ipadapter"] = ["11", 1]
        g["15"] = {"class_type": "IPAdapterAdvanced",
                   "inputs": {"model": ["14", 0], "ipadapter": ["14", 1], "image": ["13", 0],
                              "weight": a.face_w, "weight_type": "linear",
                              "combine_embeds": "concat", "start_at": 0.0, "end_at": 1.0,
                              "embeds_scaling": "V only"}}
        g["5"]["inputs"]["model"] = ["15", 0]
    if a.pose_name and getattr(a, "pose_line", False):
        # 線画の手本（デッサン人形など）は輪郭をそのまま手本にする。反転はしない（黒線・白地のまま）。
        # 最後まで効かせると人形の質感まで描かれるので、7割で手を離す（2026-10-28 実測）
        g["16"] = {"class_type": "LoadImage", "inputs": {"image": a.pose_name}}
        g["18"] = {"class_type": "ControlNetLoader",
                   "inputs": {"control_net_name": "mistoLine_fp16.safetensors"}}
        g["19"] = {"class_type": "ControlNetApplyAdvanced",
                   "inputs": {"positive": ["2", 0], "negative": ["3", 0], "control_net": ["18", 0],
                              "image": ["16", 0], "strength": a.pose_w,
                              "start_percent": 0.0, "end_percent": 0.7, "vae": ["6", 0]}}
        g["5"]["inputs"]["positive"] = ["19", 0]
        g["5"]["inputs"]["negative"] = ["19", 1]
    elif a.pose_name:
        # ポーズの手本（B）から骨組みを取り出し（DWPose）、ControlNet で骨組みどおりに描かせる
        g["16"] = {"class_type": "LoadImage", "inputs": {"image": a.pose_name}}
        g["17"] = {"class_type": "DWPreprocessor",
                   "inputs": {"image": ["16", 0], **DWPOSE}}   # 設定は check_pose と共通
        g["18"] = {"class_type": "ControlNetLoader",
                   "inputs": {"control_net_name": "controlnet-openpose-sdxl-xinsir.safetensors"}}
        g["19"] = {"class_type": "ControlNetApplyAdvanced",
                   "inputs": {"positive": ["2", 0], "negative": ["3", 0], "control_net": ["18", 0],
                              "image": ["17", 0], "strength": a.pose_w,
                              "start_percent": 0.0, "end_percent": 1.0, "vae": ["6", 0]}}
        g["5"]["inputs"]["positive"] = ["19", 0]
        g["5"]["inputs"]["negative"] = ["19", 1]
    return g


def free_ollama():
    """生成の前に Ollama のモデルを下ろしてメモリを空ける（24GBで SDXL＋手本＋ControlNet を載せるため。2026-10-19）。
    Ollama が動いていない・何も載っていないときは何もしない"""
    try:
        ps = json.loads(urllib.request.urlopen("http://127.0.0.1:11434/api/ps", timeout=2).read())
    except Exception:
        return
    for m in ps.get("models", []):
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                         data=json.dumps({"model": m["name"], "keep_alive": 0}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=30).read()
            print(f"Ollama の {m['name']} を下ろした（メモリを空けるため）")
        except Exception:
            pass


# --ref-mode の日本語寄りの呼び名 → IPAdapterAdvanced の weight_type
REF_MODES = {"style": "style transfer",          # 絵柄だけ寄せる（既定）
             "strong": "strong style transfer",  # 絵柄をより強く。強さ0.8だと手本の中身まで漏れた（2026-10-17 qa実測）→0.5前後から
             "all": "linear"}                    # 絵柄も中身も寄せる（手本がほぼそのまま出る。使いどころ注意）


MAX_FETCH = 20 * 1024 * 1024     # URLから取る手本の上限（20MB）


def fetch_ref(src, opt):
    """URL なら一時ファイルに落としてそのパスを返す。ファイルのパスならそのまま返す。

    落とした一時ファイルは終了時に必ず消す（エラー・Ctrl-C でも）。見せてもらった絵を手元に溜めない。
    """
    if not re.match(r"^https?://", src or "", re.I):
        return src
    try:
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (sd-studio)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype = r.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if not ctype.startswith("image/"):
                sys.exit(f"{opt} のURLが画像ではない（{ctype or '種類が分からない'}）: {src}")
            data = r.read(MAX_FETCH + 1)
    except urllib.error.HTTPError as e:
        sys.exit(f"{opt} のURLを取れない（HTTP {e.code}）: {src}")
    except urllib.error.URLError as e:
        sys.exit(f"{opt} のURLにつながらない（{e.reason}）: {src}")
    if len(data) > MAX_FETCH:
        sys.exit(f"{opt} の画像が大きすぎる（20MBまで）: {src}")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(ctype) \
        or pathlib.Path(urllib.parse.urlparse(src).path).suffix.lower() or ".png"
    fd, tmp = tempfile.mkstemp(prefix="sdpose_", suffix=ext)
    os.write(fd, data)
    os.close(fd)
    atexit.register(lambda: pathlib.Path(tmp).unlink(missing_ok=True))
    return tmp


DWPOSE = {"detect_hand": "enable", "detect_body": "enable", "detect_face": "enable",
          "resolution": 1024, "bbox_detector": "yolox_l.onnx",
          "pose_estimator": "dw-ll_ucoco_384.onnx", "scale_stick_for_xinsr_cn": "enable"}


def check_pose(name):
    """ポーズの手本から骨格が読めたかを、本生成の前に確かめる。読めなければ止める。

    読めないまま進むと ControlNet に空の骨格が渡り、姿勢は一切効かないのに黙って生成してしまう
    （デッサン人形の線画などで起きる。2026-10-28 に実例）。
    """
    from PIL import Image
    import io as _io
    g = {"1": {"class_type": "LoadImage", "inputs": {"image": name}},
         "2": {"class_type": "DWPreprocessor", "inputs": {"image": ["1", 0], **DWPOSE}},
         "3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0], "filename_prefix": "sdposecheck"}}}
    pid = post("/prompt", {"prompt": g})["prompt_id"]
    t0 = time.time()
    while True:
        h = get(f"/history/{pid}")
        st = h.get(pid, {}).get("status", {})
        if st.get("completed") or st.get("status_str") in ("success", "error"):
            break
        if time.time() - t0 > 180:
            sys.exit("ポーズの読み取りが時間切れ。ComfyUI のログを確認すること")
        time.sleep(1)
    imgs = [i for v in h[pid]["outputs"].values() for i in v.get("images", [])]
    if not imgs:
        sys.exit("ポーズの読み取りに失敗した（ComfyUI 側のエラー）")
    i = imgs[0]
    q = f"/view?filename={i['filename']}&subfolder={i['subfolder']}&type={i['type']}"
    data = urllib.request.urlopen(SERVER + q).read()
    # 確かめ用の画像は残さない
    (pathlib.Path.home() / "ComfyUI" / "output" / i["subfolder"] / i["filename"]).unlink(missing_ok=True)
    im = Image.open(_io.BytesIO(data)).convert("L")
    lit = sum(im.histogram()[33:])                   # 明るさ33以上＝骨格の線
    return lit / (im.width * im.height) >= 0.001     # 骨格の線がほぼ無い＝人として読めていない


def looks_like_lineart(path):
    """白地に色の薄い線だけの絵か。骨格が読めない絵を何でも線画扱いにしないための見分け。

    カラーの絵を輪郭の手本にすると色の塊まで形として拾ってしまう（2026-10-28 qa指摘）。
    """
    from PIL import Image, ImageStat
    im = Image.open(path).convert("RGB").resize((128, 128))
    h = im.convert("L").histogram()
    white = sum(h[200:]) / (128 * 128)                       # ほぼ白の割合
    sat = ImageStat.Stat(im.convert("HSV").split()[1]).mean[0]  # 彩度の平均
    return white > 0.6 and sat < 30


def pad_to(path, w, h):
    """線画の手本を、生成の縦横比に白い余白で合わせる（引き伸ばすと人形が歪むため）。

    比率がほぼ同じなら元のまま。足した画像は一時ファイルで、終了時に必ず消す。
    """
    from PIL import Image
    im = Image.open(path).convert("RGB")
    ar_t, ar_i = w / h, im.width / im.height
    if abs(ar_i - ar_t) / ar_t < 0.03:
        return path
    if ar_i > ar_t:      # 手本の方が横長 → 上下に余白
        nh = round(im.width / ar_t)
        canvas = Image.new("RGB", (im.width, nh), "white")
        canvas.paste(im, (0, (nh - im.height) // 2))
    else:                # 手本の方が縦長 → 左右に余白
        nw = round(im.height * ar_t)
        canvas = Image.new("RGB", (nw, im.height), "white")
        canvas.paste(im, ((nw - im.width) // 2, 0))
    fd, tmp = tempfile.mkstemp(prefix="sdpose_", suffix=".png")
    os.close(fd)
    canvas.save(tmp)
    atexit.register(lambda: pathlib.Path(tmp).unlink(missing_ok=True))
    return tmp


def upload_ref(path, opt="--ref"):
    """手本の画像を ComfyUI の input に上げ、サーバ側の名前を返す（multipart を手組み）"""
    p = pathlib.Path(path).expanduser()
    if not p.is_file():
        sys.exit(f"{opt} の画像が見つからない: {p}")
    boundary = "----sdstudio" + str(random.randint(0, 10**12))
    # 毎回ちがう名前で上げる（同じ名前の画像を上書きしない）。生成後に cleanup_ref で消す
    up = f"sdref_{random.randint(0, 10**9):09d}{p.suffix.lower() or '.png'}"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{up}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + p.read_bytes() + \
           f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(SERVER + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    r = _open(req)
    return f"{r['subfolder']}/{r['name']}" if r.get("subfolder") else r["name"]


def cleanup_ref(name):
    """上げた手本の画像を ComfyUI の input から消す（見せてもらった絵を手元に溜めない。個人利用の約束）"""
    f = pathlib.Path.home() / "ComfyUI" / "input" / name
    if name and f.name.startswith("sdref_") and f.is_file():
        f.unlink()


def run(a, p):
    """グラフを投げて完了まで待つ。戻り値は (history, prompt_id, status, 開始時刻)"""
    t0 = time.time()
    pid = post("/prompt", {"prompt": build_graph(a, p)})["prompt_id"]
    ref = (f" 手本={a.ref_mode}/{a.ref_w}" if a.ref else "") + (f" 顔={a.face_w}" if a.face else "") + \
          (f" ポーズ={a.pose_w}（{'線画' if getattr(a, 'pose_line', False) else '骨格'}）" if a.pose else "") + (" 下書き" if a.draft else "")
    print(f"model={a.ckpt or p['ckpt']} seed={a.seed} steps={a.steps} cfg={a.cfg} {a.width}x{a.height} x{a.n}{ref}")

    deadline = time.time() + a.timeout
    while True:
        h = get(f"/history/{pid}")
        st = h.get(pid, {}).get("status", {})
        if st.get("completed") or st.get("status_str") in ("success", "error"):
            break
        if time.time() > deadline:
            sys.exit(f"タイムアウト（{a.timeout}秒）。ComfyUI 側のログを確認すること。")
        time.sleep(1.0)

    return h, pid, st, t0


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
    ap.add_argument("--ckpt", default="", help="モデルのファイル名を直接指定（プリセットより優先）。"
                    "過去の記録を再現するとき用。例 animagine-xl-4.0.safetensors")
    ap.add_argument("--lora", default="", help="~/ComfyUI/models/loras のファイル名（例 pixel-art-xl.safetensors）")
    ap.add_argument("--lora-w", type=float, default=1.0, dest="lora_w", help="LoRA の強さ")
    ap.add_argument("--raw", action="store_true", help="品質タグを足さず prompt をそのまま使う")
    ap.add_argument("--ref", default="", help="手本の画像（IP-Adapter で絵柄を寄せる）。個人利用に限る")
    ap.add_argument("--ref-w", type=float, default=0.8, dest="ref_w", help="手本の効きの強さ（0〜1.5くらい）")
    ap.add_argument("--ref-mode", default="style", choices=list(REF_MODES), dest="ref_mode",
                    help="style=絵柄だけ（既定）／strong=絵柄を強く（手本の中身が漏れやすい。--ref-w 0.5前後から）／all=中身も寄せる（ほぼ手本どおりになる）")
    ap.add_argument("--face", default="", help="顔の手本（顔のあたりを切り抜いた画像がよく効く）。個人利用に限る")
    ap.add_argument("--face-w", type=float, default=0.3, dest="face_w",
                    help="顔の手本の効きの強さ。イラストでは0.5〜0.6で画面が白っぽく荒れた（2026-10-19実測）→0.3前後から。荒れたら --face を外す")
    ap.add_argument("--pose", default="", help="ポーズの手本（この画像の姿勢で描く）。画像のパスかURL")
    ap.add_argument("--pose-w", type=float, default=None, dest="pose_w",
                    help="ポーズの効きの強さ（0〜1）。既定は骨格0.75・線画0.8（どちらも実測）")
    ap.add_argument("--pose-mode", default="auto", choices=["auto", "skeleton", "line"], dest="pose_mode",
                    help="auto=骨格を読み、読めなければ線画として輪郭を使う／skeleton=骨格だけ／line=線画だけ")
    ap.add_argument("--draft", action="store_true", help="下書き：大きさを約0.6倍にして速く回す（良いものだけ本番の大きさで描き直す）")
    ap.add_argument("--keep-ollama", action="store_true", dest="keep_ollama",
                    help="手本（--ref/--face/--pose）を使う生成でも、前に Ollama のモデルを下ろさない（既定では下ろしてメモリを空ける）")
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
    if a.draft:   # 約0.6倍・64の倍数に丸める
        a.width, a.height = (max(256, round(v * 0.625 / 64) * 64) for v in (a.width, a.height))
    if a.seed < 0:
        a.seed = random.randint(0, 2**32 - 1)

    try:
        get("/system_stats")
    except urllib.error.URLError:
        sys.exit("ComfyUI が起動していない。先に bin/start.sh を実行すること。")

    # ポーズはURLでも渡せる（一時ファイルに落としてから、以降はファイルとして扱う）
    # kill（SIGTERM）でも finally と atexit の後片付けが走るよう、通常の終了に変える
    import signal
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

    a.pose = fetch_ref(a.pose, "--pose")

    # 先に全部の画像があるか確かめてから上げる（途中で止まって上げた分が残らないように。2026-10-19 qa指摘）
    for opt, path in (("--ref", a.ref), ("--face", a.face), ("--pose", a.pose)):
        if path and not pathlib.Path(path).expanduser().is_file():
            sys.exit(f"{opt} の画像が見つからない: {pathlib.Path(path).expanduser()}")
    if not a.keep_ollama and (a.ref or a.face or a.pose):   # 手本を使う重い生成のときだけ（テイモン等の常駐利用とぶつけない）
        free_ollama()
    a.ref_name = a.face_name = a.pose_name = ""
    try:
        a.ref_name = upload_ref(a.ref) if a.ref else ""
        a.face_name = upload_ref(a.face, "--face") if a.face else ""
        a.pose_line = False
        if a.pose:
            # 手本の縦横比を生成に合わせてから上げる（骨格・線画とも、比率が違うと中央が切り取られて
            # 頭や足が切れる／人形が歪む。2026-10-28 qa指摘）
            a.pose_name = upload_ref(pad_to(a.pose, a.width, a.height), "--pose")
            if a.pose_mode == "line":
                a.pose_line = True
            elif not check_pose(a.pose_name):
                if a.pose_mode == "skeleton":
                    sys.exit("ポーズの手本から人の姿勢を読み取れなかった（骨格が空）。このまま描くと姿勢は効かない。"
                             "線画の手本なら --pose-mode line を使う")
                if not looks_like_lineart(a.pose):
                    sys.exit("ポーズの手本から骨格を読めず、線画にも見えない（色のある絵）。このまま描くと姿勢は効かない。"
                             "人がはっきり写った手本に替えるか、線画として使うなら --pose-mode line")
                print("骨格が読めなかったので、線画として輪郭を手本にする（MistoLine）")
                a.pose_line = True
        if a.pose_w is None:             # 強さの既定は方式ごとに違う（どちらも実測）
            a.pose_w = 0.8 if a.pose_line else 0.75
        h, pid, st, t0 = run(a, p)
    finally:   # エラー・時間切れ・Ctrl-C でも、上げた手本は必ず消す
        for u in (a.ref_name, a.face_name, a.pose_name):
            cleanup_ref(u)
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
