# -*- coding: utf-8 -*-
"""ComfyUI 用ワークフローJSONを生成する。

  python3 workflows/build.py

ネガティブは genres/_common.py から引く（プロンプト工房と同じ定義を使い、二重管理しない）。
出力先は ~/ComfyUI/user/default/workflows/ と このフォルダの両方。
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "genres"))
from _common import NEGATIVE  # noqa: E402

OUT = [pathlib.Path.home() / "ComfyUI/user/default/workflows", ROOT / "workflows"]


def node(i, t, pos, size, outputs=(), inputs=(), widgets=()):
    return {"id": i, "type": t, "pos": list(pos), "size": list(size), "flags": {}, "order": i - 1,
            "mode": 0,
            "inputs": [{"name": n, "type": ty, "link": l} for n, ty, l in inputs],
            "outputs": [{"name": n, "type": ty, "links": l, "slot_index": s}
                        for s, (n, ty, l) in enumerate(outputs)],
            "properties": {"Node name for S&R": t}, "widgets_values": list(widgets)}


def dump(name, nodes, links, last_node, last_link):
    wf = {"last_node_id": last_node, "last_link_id": last_link, "nodes": nodes, "links": links,
          "groups": [], "config": {}, "extra": {}, "version": 0.4}
    for d in OUT:
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.json").write_text(json.dumps(wf, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  ", name)


def still(name, ckpt, mode, pos_text):
    """静止画（SDXL）。イラスト用と写実用で ckpt とネガティブだけが違う。"""
    nodes = [
        node(1, "CheckpointLoaderSimple", (40, 300), (340, 98),
             outputs=[("MODEL", "MODEL", [1]), ("CLIP", "CLIP", [2, 3]), ("VAE", "VAE", None)],
             widgets=[ckpt]),
        node(2, "CLIPTextEncode", (430, 100), (420, 200),
             inputs=[("clip", "CLIP", 2)], outputs=[("CONDITIONING", "CONDITIONING", [4])],
             widgets=[pos_text]),
        node(3, "CLIPTextEncode", (430, 340), (420, 200),
             inputs=[("clip", "CLIP", 3)], outputs=[("CONDITIONING", "CONDITIONING", [5])],
             widgets=[NEGATIVE[mode]]),
        node(4, "EmptyLatentImage", (430, 580), (330, 106),
             outputs=[("LATENT", "LATENT", [6])], widgets=[832, 1216, 1]),
        node(5, "KSampler", (900, 200), (330, 262),
             inputs=[("model", "MODEL", 1), ("positive", "CONDITIONING", 4),
                     ("negative", "CONDITIONING", 5), ("latent_image", "LATENT", 6)],
             outputs=[("LATENT", "LATENT", [7])],
             widgets=[42, "randomize", 20, 5.0 if mode == "illust" else 4.5,
                      "dpmpp_2m", "karras", 1.0]),
        node(6, "VAELoader", (40, 460), (340, 58),
             outputs=[("VAE", "VAE", [8])], widgets=["sdxl_vae.safetensors"]),
        node(7, "VAEDecode", (1280, 200), (250, 46),
             inputs=[("samples", "LATENT", 7), ("vae", "VAE", 8)],
             outputs=[("IMAGE", "IMAGE", [9])]),
        node(8, "SaveImage", (1280, 300), (420, 460),
             inputs=[("images", "IMAGE", 9)], widgets=[mode]),
    ]
    links = [[1, 1, 0, 5, 0, "MODEL"], [2, 1, 1, 2, 0, "CLIP"], [3, 1, 1, 3, 0, "CLIP"],
             [4, 2, 0, 5, 1, "CONDITIONING"], [5, 3, 0, 5, 2, "CONDITIONING"],
             [6, 4, 0, 5, 3, "LATENT"], [7, 5, 0, 7, 0, "LATENT"], [8, 6, 0, 7, 1, "VAE"],
             [9, 7, 0, 8, 0, "IMAGE"]]
    dump(name, nodes, links, 8, 9)


def still_ref(name, ckpt, mode, pos_text):
    """静止画＋手本の絵柄に寄せる（IP-Adapter plus SDXL）。gen.py --ref と同じつなぎ方。個人利用に限る"""
    note = ("【手本の絵柄に寄せる・個人利用に限る】\n"
            "① 左下の「画像を読み込む」で手本の画像を選ぶ（upload）\n"
            "② 上の文に、描きたいものを英語で書く（作家名は入れない）\n"
            "③ IPAdapter Advanced の weight＝効きの強さ（0.8から。寄せたいほど上げる）\n"
            "   weight_type：style transfer＝絵柄だけ（おすすめ）／strong style transfer＝強く（weight 0.5前後から。手本の中身が漏れやすい）／linear＝中身まで寄せる\n"
            "④ 実行。1枚90秒ほど\n"
            "※ 公開・販売・SNSに出さない。既存のキャラクターは再現しない。\n"
            "※ この画面で上げた手本は ~/ComfyUI/input に残る。気になったら消す")
    nodes = [
        node(1, "CheckpointLoaderSimple", (40, 300), (340, 98),
             outputs=[("MODEL", "MODEL", [1]), ("CLIP", "CLIP", [2, 3]), ("VAE", "VAE", None)],
             widgets=[ckpt]),
        node(2, "CLIPTextEncode", (430, 100), (420, 200),
             inputs=[("clip", "CLIP", 2)], outputs=[("CONDITIONING", "CONDITIONING", [4])],
             widgets=[pos_text]),
        node(3, "CLIPTextEncode", (430, 340), (420, 200),
             inputs=[("clip", "CLIP", 3)], outputs=[("CONDITIONING", "CONDITIONING", [5])],
             widgets=[NEGATIVE[mode]]),
        node(4, "EmptyLatentImage", (430, 580), (330, 106),
             outputs=[("LATENT", "LATENT", [6])], widgets=[832, 1216, 1]),
        node(5, "KSampler", (1300, 200), (330, 262),
             inputs=[("model", "MODEL", 10), ("positive", "CONDITIONING", 4),
                     ("negative", "CONDITIONING", 5), ("latent_image", "LATENT", 6)],
             outputs=[("LATENT", "LATENT", [7])],
             widgets=[42, "randomize", 20, 5.0 if mode == "illust" else 4.5, "dpmpp_2m", "karras", 1.0]),
        node(6, "VAELoader", (40, 460), (340, 58),
             outputs=[("VAE", "VAE", [8])], widgets=["sdxl_vae.safetensors"]),
        node(7, "VAEDecode", (1680, 200), (250, 46),
             inputs=[("samples", "LATENT", 7), ("vae", "VAE", 8)],
             outputs=[("IMAGE", "IMAGE", [9])]),
        node(8, "SaveImage", (1680, 300), (420, 460),
             inputs=[("images", "IMAGE", 9)], widgets=[mode + "_ref"]),
        node(9, "IPAdapterUnifiedLoader", (900, 600), (340, 78),
             inputs=[("model", "MODEL", 1)],
             outputs=[("model", "MODEL", [11]), ("ipadapter", "IPADAPTER", [12])],
             widgets=["PLUS (high strength)"]),
        node(10, "IPAdapterAdvanced", (900, 740), (340, 280),
             inputs=[("model", "MODEL", 11), ("ipadapter", "IPADAPTER", 12), ("image", "IMAGE", 13)],
             outputs=[("MODEL", "MODEL", [10])],
             widgets=[0.8, "style transfer", "concat", 0.0, 1.0, "V only"]),
        node(11, "LoadImage", (40, 600), (390, 380),
             outputs=[("IMAGE", "IMAGE", [13]), ("MASK", "MASK", None)],
             widgets=["sample_anime_still.png", "image"]),
        node(12, "Note", (40, 40), (380, 230), widgets=[note]),
    ]
    links = [[1, 1, 0, 9, 0, "MODEL"], [2, 1, 1, 2, 0, "CLIP"], [3, 1, 1, 3, 0, "CLIP"],
             [4, 2, 0, 5, 1, "CONDITIONING"], [5, 3, 0, 5, 2, "CONDITIONING"],
             [6, 4, 0, 5, 3, "LATENT"], [7, 5, 0, 7, 0, "LATENT"], [8, 6, 0, 7, 1, "VAE"],
             [9, 7, 0, 8, 0, "IMAGE"], [10, 10, 0, 5, 0, "MODEL"], [11, 9, 0, 10, 0, "MODEL"],
             [12, 9, 1, 10, 1, "IPADAPTER"], [13, 11, 0, 10, 2, "IMAGE"]]
    dump(name, nodes, links, 12, 13)


def person_pose(name, ckpt, mode, pos_text):
    """Aの人物（全身の手本・IP-Adapter）× Bのポーズ（DWPose→ControlNet）。顔の手本は既定で外してある（bypass）。
    gen.py --ref/--face/--pose と同じつなぎ方・同じ既定値（2026-10-19 実測）。個人利用に限る"""
    note = ("【Aの人物 × Bのポーズ・個人利用に限る】\n"
            "① 「A：人物の手本」に人物の画像（自分のキャラ等）を upload\n"
            "② 「B：ポーズの手本」に、そのポーズをしている画像を upload\n"
            "③ 上の文に、Aの特徴（髪・目・服）と、Bのポーズを英語で書く（作家名・既存キャラ名は入れない）\n"
            "④ 実行。1枚2分ほど（画像生成の前はローカルAIを使っていないこと）\n"
            "効き：IPAdapter Advanced（全身）weight 0.45／ControlNet strength 0.75\n"
            "顔も寄せたいとき：紫の3つ（顔の手本・顔用の読み込み・顔のIPAdapter）を右クリック→Bypass を外し、顔のあたりを切り抜いた画像を入れる。weight 0.3から。0.5以上だと画面が白っぽく荒れた\n"
            "※ 公開・販売・SNSに出さない。この画面で上げた手本は ~/ComfyUI/input に残る")
    nodes = [
        node(1, "CheckpointLoaderSimple", (40, 300), (340, 98),
             outputs=[("MODEL", "MODEL", [1]), ("CLIP", "CLIP", [2, 3]), ("VAE", "VAE", None)], widgets=[ckpt]),
        node(2, "CLIPTextEncode", (430, 60), (420, 200), inputs=[("clip", "CLIP", 2)],
             outputs=[("CONDITIONING", "CONDITIONING", [4])], widgets=[pos_text]),
        node(3, "CLIPTextEncode", (430, 300), (420, 180), inputs=[("clip", "CLIP", 3)],
             outputs=[("CONDITIONING", "CONDITIONING", [5])], widgets=[NEGATIVE[mode]]),
        node(4, "EmptyLatentImage", (430, 520), (330, 106),
             outputs=[("LATENT", "LATENT", [6])], widgets=[832, 1216, 1]),
        node(5, "KSampler", (1700, 200), (330, 262),
             inputs=[("model", "MODEL", 17), ("positive", "CONDITIONING", 18),
                     ("negative", "CONDITIONING", 19), ("latent_image", "LATENT", 6)],
             outputs=[("LATENT", "LATENT", [7])],
             widgets=[42, "randomize", 20, 5.0, "dpmpp_2m", "karras", 1.0]),
        node(6, "VAELoader", (40, 460), (340, 58), outputs=[("VAE", "VAE", [8, 20])],
             widgets=["sdxl_vae.safetensors"]),
        node(7, "VAEDecode", (2080, 200), (250, 46), inputs=[("samples", "LATENT", 7), ("vae", "VAE", 8)],
             outputs=[("IMAGE", "IMAGE", [9])]),
        node(8, "SaveImage", (2080, 300), (420, 560), inputs=[("images", "IMAGE", 9)], widgets=[mode + "_pose"]),
        node(9, "IPAdapterUnifiedLoader", (900, 60), (340, 78), inputs=[("model", "MODEL", 1)],
             outputs=[("model", "MODEL", [10]), ("ipadapter", "IPADAPTER", [11, 22])],
             widgets=["PLUS (high strength)"]),
        node(10, "IPAdapterAdvanced", (900, 180), (340, 280),
             inputs=[("model", "MODEL", 10), ("ipadapter", "IPADAPTER", 11), ("image", "IMAGE", 12)],
             outputs=[("MODEL", "MODEL", [13])], widgets=[0.45, "linear", "concat", 0.0, 1.0, "V only"]),
        node(11, "LoadImage", (40, 620), (390, 380), outputs=[("IMAGE", "IMAGE", [12]), ("MASK", "MASK", None)],
             widgets=["sample_anime_still.png", "image"]),
        node(12, "IPAdapterUnifiedLoader", (1300, 60), (340, 78),
             inputs=[("model", "MODEL", 13), ("ipadapter", "IPADAPTER", 22)],
             outputs=[("model", "MODEL", [14]), ("ipadapter", "IPADAPTER", [15])],
             widgets=["PLUS FACE (portraits)"]),
        node(13, "IPAdapterAdvanced", (1300, 180), (340, 280),
             inputs=[("model", "MODEL", 14), ("ipadapter", "IPADAPTER", 15), ("image", "IMAGE", 16)],
             outputs=[("MODEL", "MODEL", [17])], widgets=[0.3, "linear", "concat", 0.0, 1.0, "V only"]),
        node(14, "LoadImage", (900, 520), (360, 340), outputs=[("IMAGE", "IMAGE", [16]), ("MASK", "MASK", None)],
             widgets=["sample_anime_still.png", "image"]),
        node(15, "LoadImage", (40, 1040), (390, 380), outputs=[("IMAGE", "IMAGE", [23]), ("MASK", "MASK", None)],
             widgets=["sample_anime_still.png", "image"]),
        node(16, "DWPreprocessor", (480, 1040), (340, 220), inputs=[("image", "IMAGE", 23)],
             outputs=[("IMAGE", "IMAGE", [24])],
             widgets=["enable", "enable", "enable", 1024, "yolox_l.onnx", "dw-ll_ucoco_384.onnx", "enable"]),
        node(17, "ControlNetLoader", (900, 920), (380, 58), outputs=[("CONTROL_NET", "CONTROL_NET", [25])],
             widgets=["controlnet-openpose-sdxl-xinsir.safetensors"]),
        node(18, "ControlNetApplyAdvanced", (1300, 920), (340, 186),
             inputs=[("positive", "CONDITIONING", 4), ("negative", "CONDITIONING", 5),
                     ("control_net", "CONTROL_NET", 25), ("image", "IMAGE", 24), ("vae", "VAE", 20)],
             outputs=[("positive", "CONDITIONING", [18]), ("negative", "CONDITIONING", [19])],
             widgets=[0.75, 0.0, 1.0]),
        node(19, "Note", (40, 40), (380, 240), widgets=[note]),
    ]
    titles = {11: "A：人物の手本", 14: "Aの顔の手本（切り抜き）", 15: "B：ポーズの手本"}
    for n in nodes:
        if n["id"] in titles:
            n["title"] = titles[n["id"]]
        if n["id"] in (12, 13, 14):   # 顔の手本は既定で外す（bypass）。紫で目立たせる
            n["mode"] = 4
            n["color"], n["bgcolor"] = "#323", "#535"
    links = [[1, 1, 0, 9, 0, "MODEL"], [2, 1, 1, 2, 0, "CLIP"], [3, 1, 1, 3, 0, "CLIP"],
             [4, 2, 0, 18, 0, "CONDITIONING"], [5, 3, 0, 18, 1, "CONDITIONING"], [6, 4, 0, 5, 3, "LATENT"],
             [7, 5, 0, 7, 0, "LATENT"], [8, 6, 0, 7, 1, "VAE"], [9, 7, 0, 8, 0, "IMAGE"],
             [10, 9, 0, 10, 0, "MODEL"], [11, 9, 1, 10, 1, "IPADAPTER"], [12, 11, 0, 10, 2, "IMAGE"],
             [13, 10, 0, 12, 0, "MODEL"], [14, 12, 0, 13, 0, "MODEL"], [15, 12, 1, 13, 1, "IPADAPTER"],
             [16, 14, 0, 13, 2, "IMAGE"], [17, 13, 0, 5, 0, "MODEL"], [18, 18, 0, 5, 1, "CONDITIONING"],
             [19, 18, 1, 5, 2, "CONDITIONING"], [20, 6, 0, 18, 4, "VAE"], [22, 9, 1, 12, 1, "IPADAPTER"],
             [23, 15, 0, 16, 0, "IMAGE"], [24, 16, 0, 18, 3, "IMAGE"], [25, 17, 0, 18, 2, "CONTROL_NET"]]
    dump(name, nodes, links, 19, 25)


def video_t2v(name, pos_text):
    nodes = [
        node(1, "CheckpointLoaderSimple", (40, 240), (390, 98),
             outputs=[("MODEL", "MODEL", [1]), ("CLIP", "CLIP", None), ("VAE", "VAE", [2])],
             widgets=["ltxv-2b-0.9.8-distilled.safetensors"]),
        node(2, "CLIPLoader", (40, 400), (390, 82), outputs=[("CLIP", "CLIP", [3, 4])],
             widgets=["t5xxl_fp16.safetensors", "ltxv"]),
        node(3, "CLIPTextEncode", (480, 100), (430, 190), inputs=[("clip", "CLIP", 3)],
             outputs=[("CONDITIONING", "CONDITIONING", [5])], widgets=[pos_text]),
        node(4, "CLIPTextEncode", (480, 340), (430, 160), inputs=[("clip", "CLIP", 4)],
             outputs=[("CONDITIONING", "CONDITIONING", [6])], widgets=[NEGATIVE["video"]]),
        node(5, "LTXVConditioning", (480, 540), (330, 82),
             inputs=[("positive", "CONDITIONING", 5), ("negative", "CONDITIONING", 6)],
             outputs=[("positive", "CONDITIONING", [7]), ("negative", "CONDITIONING", [8])],
             widgets=[25.0]),
        node(6, "EmptyLTXVLatentVideo", (480, 670), (330, 130),
             outputs=[("LATENT", "LATENT", [9])], widgets=[768, 512, 49, 1]),
        node(7, "KSampler", (960, 240), (330, 262),
             inputs=[("model", "MODEL", 1), ("positive", "CONDITIONING", 7),
                     ("negative", "CONDITIONING", 8), ("latent_image", "LATENT", 9)],
             outputs=[("LATENT", "LATENT", [10])],
             widgets=[42, "randomize", 8, 1.0, "euler", "simple", 1.0]),
        node(8, "VAEDecode", (1340, 240), (250, 46),
             inputs=[("samples", "LATENT", 10), ("vae", "VAE", 2)],
             outputs=[("IMAGE", "IMAGE", [11])]),
        node(9, "SaveWEBM", (1340, 330), (420, 200), inputs=[("images", "IMAGE", 11)],
             widgets=["video", "vp9", 25.0, 32.0]),
    ]
    links = [[1, 1, 0, 7, 0, "MODEL"], [2, 1, 2, 8, 1, "VAE"],
             [3, 2, 0, 3, 0, "CLIP"], [4, 2, 0, 4, 0, "CLIP"],
             [5, 3, 0, 5, 0, "CONDITIONING"], [6, 4, 0, 5, 1, "CONDITIONING"],
             [7, 5, 0, 7, 1, "CONDITIONING"], [8, 5, 1, 7, 2, "CONDITIONING"],
             [9, 6, 0, 7, 3, "LATENT"], [10, 7, 0, 8, 0, "LATENT"], [11, 8, 0, 9, 0, "IMAGE"]]
    dump(name, nodes, links, 9, 11)


def video_i2v(name, pos_text):
    nodes = [
        node(1, "CheckpointLoaderSimple", (40, 240), (390, 98),
             outputs=[("MODEL", "MODEL", [1]), ("CLIP", "CLIP", None), ("VAE", "VAE", [2, 3])],
             widgets=["ltxv-2b-0.9.8-distilled.safetensors"]),
        node(2, "CLIPLoader", (40, 400), (390, 82), outputs=[("CLIP", "CLIP", [4, 5])],
             widgets=["t5xxl_fp16.safetensors", "ltxv"]),
        node(3, "CLIPTextEncode", (480, 60), (430, 170), inputs=[("clip", "CLIP", 4)],
             outputs=[("CONDITIONING", "CONDITIONING", [6])], widgets=[pos_text]),
        node(4, "CLIPTextEncode", (480, 270), (430, 140), inputs=[("clip", "CLIP", 5)],
             outputs=[("CONDITIONING", "CONDITIONING", [7])], widgets=[NEGATIVE["video"]]),
        node(5, "LoadImage", (40, 560), (390, 340),
             outputs=[("IMAGE", "IMAGE", [8]), ("MASK", "MASK", None)],
             widgets=["sample_anime_still.png", "image"]),
        node(6, "LTXVImgToVideo", (960, 460), (340, 180),
             inputs=[("positive", "CONDITIONING", 6), ("negative", "CONDITIONING", 7),
                     ("vae", "VAE", 2), ("image", "IMAGE", 8)],
             outputs=[("positive", "CONDITIONING", [9]), ("negative", "CONDITIONING", [10]),
                      ("latent", "LATENT", [11])],
             widgets=[768, 512, 17, 1, 1.0]),
        node(7, "LTXVConditioning", (960, 300), (330, 82),
             inputs=[("positive", "CONDITIONING", 9), ("negative", "CONDITIONING", 10)],
             outputs=[("positive", "CONDITIONING", [12]), ("negative", "CONDITIONING", [13])],
             widgets=[25.0]),
        node(8, "KSampler", (1360, 240), (330, 262),
             inputs=[("model", "MODEL", 1), ("positive", "CONDITIONING", 12),
                     ("negative", "CONDITIONING", 13), ("latent_image", "LATENT", 11)],
             outputs=[("LATENT", "LATENT", [14])],
             widgets=[42, "randomize", 8, 1.0, "euler", "simple", 1.0]),
        node(9, "VAEDecode", (1740, 240), (250, 46),
             inputs=[("samples", "LATENT", 14), ("vae", "VAE", 3)],
             outputs=[("IMAGE", "IMAGE", [15])]),
        node(10, "SaveWEBM", (1740, 330), (420, 200), inputs=[("images", "IMAGE", 15)],
             widgets=["video_anime", "vp9", 25.0, 32.0]),
    ]
    links = [[1, 1, 0, 8, 0, "MODEL"], [2, 1, 2, 6, 2, "VAE"], [3, 1, 2, 9, 1, "VAE"],
             [4, 2, 0, 3, 0, "CLIP"], [5, 2, 0, 4, 0, "CLIP"],
             [6, 3, 0, 6, 0, "CONDITIONING"], [7, 4, 0, 6, 1, "CONDITIONING"],
             [8, 5, 0, 6, 3, "IMAGE"],
             [9, 6, 0, 7, 0, "CONDITIONING"], [10, 6, 1, 7, 1, "CONDITIONING"],
             [11, 6, 2, 8, 3, "LATENT"],
             [12, 7, 0, 8, 1, "CONDITIONING"], [13, 7, 1, 8, 2, "CONDITIONING"],
             [14, 8, 0, 9, 0, "LATENT"], [15, 9, 0, 10, 0, "IMAGE"]]
    dump(name, nodes, links, 10, 15)


if __name__ == "__main__":
    print("生成:")
    still("1_イラスト", "animagine-xl-4.0-opt.safetensors", "illust",
          "1girl, sake brewery interior, kimono, holding a sake cup, warm lantern light, "
          "masterpiece, high score, great score, absurdres")
    still("2_写実", "juggernautXL-v9.safetensors", "photo",
          "a bottle of japanese sake and a ceramic cup on a wooden counter, soft window light, "
          "photorealistic, highly detailed, natural lighting, 8k uhd")
    video_t2v("3_動画", "a slow pan across a traditional japanese sake brewery, wooden barrels, "
                        "steam rising and curling upward, warm morning light, "
                        "cinematic, smooth natural motion, highly detailed")
    video_i2v("4_静止画から動画",
              # 絵の内容（情景）＋ 動き の順に書く。動きだけだと絵が離れていく（実測）
              "anime style, cel shaded, 1girl in kimono in a japanese sake brewery, "
              "warm lantern light, "
              "she walks slowly forward, her kimono sways gently, "
              "the camera slowly pushes in")
    still_ref("5_手本の絵柄に寄せる", "animagine-xl-4.0-opt.safetensors", "illust",
              "a bottle of japanese sake and a small cup on a wooden table, no humans, "
              "masterpiece, high score, great score, absurdres")
    person_pose("6_人物とポーズを組み合わせる", "animagine-xl-4.0-opt.safetensors", "illust",
                "1girl, solo, short red hair, green eyes, white haori jacket, navy hakama, "
                "waving with right hand raised high, left hand on hip, full body, simple white background, "
                "masterpiece, high score, great score, absurdres")
