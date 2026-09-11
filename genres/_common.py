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


# 書かなくてよいもの（書けば優先される）
DEFAULTS = {
    "ICON": "🎨", "EXAMPLE": "", "ALIASES": {},
    "NO_HUMAN": (), "HUMAN_ONLY_CATS": (), "NO_HUMAN_MOTION": (),
    "PUBLISH": True,   # False にすると公開版（docs/index.html）に載らない
}


def load(name):
    """ジャンルモジュールを読み込み、足りないものを補って返す。

    必ず書くのは TITLE / PORT / VOCAB の3つだけ。
    ALWAYS と ROLL_CHANCE は省略すれば VOCAB から自動で作る。
    """
    import importlib
    g = importlib.import_module(name)

    for key in ("TITLE", "PORT", "VOCAB"):
        if not hasattr(g, key):
            raise ValueError(f"{name}.py に {key} が無い（TITLE・PORT・VOCAB は必須）")
    for key, val in DEFAULTS.items():
        if not hasattr(g, key):
            setattr(g, key, val)

    for cat, entries in g.VOCAB.items():
        for e in entries:
            if not (isinstance(e, (list, tuple)) and len(e) == 3):
                raise ValueError(f"{name}.py の「{cat}」に3つ組でない項目がある: {e!r}"
                                 "（日本語, イラスト用タグ, 写実用の語 or None）")

    if CAMERA_CAT not in g.VOCAB:
        g.VOCAB[CAMERA_CAT] = list(CAMERA)

    cats = list(g.VOCAB)
    if not hasattr(g, "ALWAYS"):
        head = [c for c in cats if c not in VIDEO_ONLY][:2]
        g.ALWAYS = {"illust": tuple(head), "photo": tuple(head),
                    "video": tuple(head + ([MOTION_CAT] if MOTION_CAT in cats else []))}
    if not hasattr(g, "ROLL_CHANCE"):
        g.ROLL_CHANCE = {}
    for i, c in enumerate(cats):
        g.ROLL_CHANCE.setdefault(c, CAMERA_CHANCE if c == CAMERA_CAT
                                 else 1.0 if i < 2 else 0.6)

    extra = set(g.ROLL_CHANCE) - set(g.VOCAB)
    if extra:
        raise ValueError(f"{name}.py: ROLL_CHANCE に VOCAB に無いカテゴリがある: {sorted(extra)}")
    return g
