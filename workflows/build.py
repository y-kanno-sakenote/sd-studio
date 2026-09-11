# -*- coding: utf-8 -*-
"""ComfyUI 用ワークフローJSONを生成する。

  python3 workflows/build.py

ネガティブは prompts/vocab.py から引く（プロンプト工房と同じ定義を使い、二重管理しない）。
出力先は ~/ComfyUI/user/default/workflows/ と このフォルダの両方。
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "prompts"))
from vocab import NEGATIVE  # noqa: E402

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
    still("1_イラスト", "animagine-xl-4.0.safetensors", "illust",
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
