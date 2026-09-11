# -*- coding: utf-8 -*-
"""全ジャンル共通の定義。

各ジャンルのモジュール（genres/<name>.py）は VOCAB・ALWAYS・ROLL_CHANCE などを持つ。
カメラの動き・品質タグ・ネガティブはジャンルに依らないので、ここに置いて注入する。
"""

# カメラワークはジャンルを問わない。動画モードのときだけ VOCAB に足される。
CAMERA = [
    ("動かさない", None, "static camera, locked-off shot"),
    ("ゆっくり右へ振る", None, "the camera slowly pans right"),
    ("ゆっくり左へ振る", None, "the camera slowly pans left"),
    ("ゆっくり寄る", None, "the camera slowly pushes in"),
    ("ゆっくり引く", None, "the camera slowly pulls back"),
    ("ゆっくり上へ振る", None, "the camera tilts up"),
    ("ゆっくり下へ振る", None, "the camera tilts down"),
    ("被写体を追う", None, "the camera tracks the subject"),
    ("回り込む", None, "the camera slowly orbits around the subject"),
    ("手持ちで揺れる", None, "handheld camera with a slight natural shake"),
]
CAMERA_CAT = "カメラの動き"
MOTION_CAT = "主役の動き"
VIDEO_ONLY = (MOTION_CAT, CAMERA_CAT)
CAMERA_CHANCE = 0.9

QUALITY = {
    "illust": "masterpiece, high score, great score, absurdres",
    "photo": "photorealistic, highly detailed, natural lighting, 8k uhd",
    "video": "cinematic, smooth natural motion, highly detailed",
}

NEGATIVE = {
    "illust": ("nsfw, nude, nipples, cleavage, revealing clothes, underwear, "
               "lowres, bad anatomy, bad hands, text, error, missing finger, "
               "extra digits, fewer digits, cropped, worst quality, low quality, "
               "low score, bad score, average score, signature, watermark, username, blurry"),
    "photo": ("cartoon, anime, illustration, painting, drawing, cgi, 3d render, "
              "worst quality, low quality, blurry, jpeg artifacts, watermark, text, "
              "deformed, bad anatomy, extra limbs"),
    "video": ("worst quality, blurry, jittery, distorted, flickering, warping, "
              "morphing, watermark, text, static image, frozen"),
}


def fragment(entry, model):
    """(日本語, イラスト用, 写実用) から、モデルに応じた英語断片を返す。"""
    jp, illust, photo = entry
    if model in ("photo", "video"):
        return photo if photo else illust
    return illust


def load(name):
    """ジャンルモジュールを読み込み、共通のカメラ語彙を差し込んで返す。"""
    import importlib
    g = importlib.import_module(name)
    if CAMERA_CAT not in g.VOCAB:
        g.VOCAB[CAMERA_CAT] = list(CAMERA)
        g.ROLL_CHANCE[CAMERA_CAT] = CAMERA_CHANCE
    missing = set(g.VOCAB) - set(g.ROLL_CHANCE)
    extra = set(g.ROLL_CHANCE) - set(g.VOCAB)
    if missing or extra:
        raise ValueError(f"{name}: ROLL_CHANCE と VOCAB のキーが不一致 "
                         f"（不足={sorted(missing)} 余分={sorted(extra)}）")
    return g
