# -*- coding: utf-8 -*-
"""日本語ラベル → 英語プロンプト断片の対応表。

各項目は (日本語, イラスト用タグ, 写実用の語) の3つ組。
3つめが None ならイラスト用をそのまま使う。
イラスト用は Danbooru 系タグ（animagine）、写実用は自然な描写語（juggernaut）。
"""

VOCAB = {
"主役": [
    ("巫女", "1girl, miko, shrine maiden", "a shrine maiden"),
    ("女性の蔵人", "1girl, brewery worker", "a woman working at a sake brewery"),
    ("男性の蔵人", "1boy, brewery worker", "a man working at a sake brewery"),
    ("杜氏（年配の職人）", "1boy, old man, master brewer, wrinkles", "an elderly master brewer"),
    ("若い女性", "1girl, young woman", "a young woman"),
    ("着物の女性", "1girl, kimono", "a woman in a kimono"),
    ("女将", "1girl, mature female, elegant", "the proprietress of a traditional inn"),
    ("店主", "1boy, shopkeeper", "a shopkeeper"),
    ("客ふたり", "2people, drinking together", "two people drinking together"),
    ("猫", "cat, no humans", "a cat"),
    ("人物なし（風景）", "no humans, scenery", "an empty scene, no people"),
    ("狐の面をつけた人物", "1girl, fox mask", "a person wearing a fox mask"),
    ("酒器だけ", "no humans, still life", "a still life of sake vessels"),
],
"服装": [
    ("藍の作務衣", "indigo samue, work clothes", "indigo work clothes"),
    ("白い前掛け", "white apron", "a white apron"),
    ("長靴と手ぬぐい", "rubber boots, tenugui headband", "rubber boots and a cloth headband"),
    ("和帽子", "white headscarf", "a white head covering"),
    ("紺の法被", "navy happi coat", "a navy happi coat"),
    ("振袖", "furisode, long sleeves", "an elaborate long-sleeved kimono"),
    ("浴衣", "yukata", "a summer yukata"),
    ("袴", "hakama", "hakama trousers"),
    ("割烹着", "kappogi, white smock", "a white cooking smock"),
    ("眼鏡", "glasses", "eyeglasses"),
    ("髪をまとめた", "hair up, bun", "hair tied up in a bun"),
    ("手袋と長い前掛け", "gloves, long apron", "gloves and a long apron"),
],
"しぐさ": [
    ("穏やかに微笑む", "smile, gentle expression", "smiling gently"),
    ("真剣な顔", "serious, focused expression", "a serious, focused expression"),
    ("疲れた顔で一息", "tired, wiping sweat", "pausing to wipe away sweat"),
    ("盃を掲げる", "holding a sake cup, raising it", "raising a sake cup"),
    ("櫂で撹拌する", "stirring with a long paddle", "stirring with a long wooden paddle"),
    ("麹を手でほぐす", "crumbling rice with hands", "crumbling rice koji by hand"),
    ("香りを利く", "smelling, eyes closed", "inhaling the aroma with eyes closed"),
    ("帳簿をつける", "writing in a ledger", "writing in a ledger"),
    ("こちらを見る", "looking at viewer", "looking directly at the camera"),
    ("横を向く", "looking to the side, profile", "seen in profile"),
    ("俯く", "looking down", "looking downward"),
    ("笑い合う", "laughing together", "laughing together"),
],
"場所": [
    ("酒蔵の仕込み場", "sake brewery interior, wooden beams", "the fermentation room of a sake brewery"),
    ("麹室", "koji room, warm humid air, cedar walls", "a warm cedar-walled koji room"),
    ("タンクの並ぶ蔵", "rows of large steel tanks", "rows of large steel fermentation tanks"),
    ("古い木造の蔵", "old wooden warehouse, dim", "an old wooden storehouse"),
    ("蔵の暖簾の前", "in front of a shop curtain, noren", "in front of a shop curtain"),
    ("試飲カウンター", "tasting counter, bottles lined up", "a tasting counter lined with bottles"),
    ("居酒屋のカウンター", "izakaya counter, lanterns", "the counter of a small izakaya"),
    ("田んぼ", "rice paddy, rural landscape", "a rice paddy"),
    ("雪の里山", "snowy village, mountains", "a snow-covered rural village"),
    ("縁側", "engawa, wooden veranda, garden", "a wooden veranda facing a garden"),
    ("石畳の路地", "stone paved alley", "a stone-paved alley"),
    ("神社の境内", "shrine grounds, torii gate", "the grounds of a shinto shrine"),
    ("港町", "harbor town", "a harbor town"),
    ("木桶の並ぶ倉", "rows of wooden barrels", "rows of wooden barrels"),
],
"小道具": [
    ("木桶", "wooden barrel", "a wooden barrel"),
    ("蒸米から立つ湯気", "steam rising from steamed rice", "steam rising from freshly steamed rice"),
    ("麹蓋", "shallow wooden koji trays", "shallow wooden trays of rice koji"),
    ("櫂棒", "long wooden paddle", "a long wooden paddle"),
    ("四合瓶", "sake bottle", "a bottle of sake"),
    ("徳利と猪口", "tokkuri and ochoko, sake set", "a sake flask and small cup"),
    ("枡", "wooden masu cup", "a square wooden cup"),
    ("蛇の目の利き猪口", "tasting cup with blue circles", "a tasting cup with blue concentric circles"),
    ("杉玉", "cedar ball hanging, sugidama", "a cedar ball hanging under the eaves"),
    ("酒林と看板", "wooden signboard", "a wooden signboard"),
    ("醪の泡", "bubbling fermenting mash", "the bubbling surface of fermenting mash"),
    ("搾りの布", "pressing cloth", "cloth used for pressing"),
    ("ラベル貼りの作業台", "workbench with labels", "a workbench covered with labels"),
],
"光": [
    ("朝の斜光", "morning light, warm sunbeam", "warm morning light slanting in"),
    ("窓からの柔らかい光", "soft window light", "soft light from a window"),
    ("裸電球の灯り", "bare light bulb, warm glow", "the glow of a bare light bulb"),
    ("提灯の灯り", "paper lantern light", "the light of paper lanterns"),
    ("夕暮れ", "sunset, orange sky", "at sunset"),
    ("夜", "night, dark", "at night"),
    ("薄暗い蔵の中", "dim interior, shadows", "a dim interior with deep shadows"),
    ("湯気ごしの光", "light through steam", "light filtering through steam"),
    ("雪明かり", "snow light, pale blue", "pale light reflected off snow"),
    ("蝋燭", "candlelight", "candlelight"),
    ("逆光", "backlit, rim light", "backlit with a rim of light"),
],
"構図": [
    ("顔のアップ", "close-up, face focus", "a close-up of the face"),
    ("上半身", "upper body", "an upper body shot"),
    ("全身", "full body", "a full body shot"),
    ("見上げる構図", "from below, low angle", "shot from a low angle"),
    ("見下ろす構図", "from above, high angle", "shot from above"),
    ("引きの風景", "wide shot, scenery", "a wide establishing shot"),
    ("手元のアップ", "close-up of hands", "a close-up of the hands"),
    ("横顔", "profile view", "a profile view"),
    ("背中越し", "from behind", "seen from behind"),
    ("被写界深度が浅い", "depth of field, blurry background", "shallow depth of field, blurred background"),
    ("対称の構図", "symmetrical composition", "a symmetrical composition"),
],
"画風": [
    ("アニメ調", "anime style, cel shaded", None),
    ("水彩", "watercolor, soft edges", "a watercolor painting"),
    ("浮世絵風", "ukiyo-e style, woodblock print", "in the style of a woodblock print"),
    ("線画・墨絵", "ink painting, sumi-e, monochrome", "an ink wash painting"),
    ("厚塗り", "thick painterly brushwork", "thick painterly brushwork"),
    ("レトロなポスター", "retro poster style, flat colors", "a retro poster illustration"),
    ("フィルム写真", "film grain, analog photo", "shot on film, visible grain"),
    ("モノクロ写真", "monochrome, black and white", "a black and white photograph"),
    ("シネマティック", "cinematic lighting, movie still", "a cinematic film still"),
    ("ドキュメンタリー写真", "documentary photography", "documentary-style photography"),
    ("柔らかいパステル", "pastel colors, soft palette", "a soft pastel color palette"),
],
"季節・天気": [
    ("冬・雪", "winter, snowing", "in winter, snow falling"),
    ("春・桜", "spring, cherry blossoms", "in spring, cherry blossoms"),
    ("夏・青空", "summer, blue sky, cicada", "in summer under a blue sky"),
    ("秋・紅葉", "autumn, red leaves", "in autumn with red foliage"),
    ("雨", "rain, wet ground", "in the rain, wet ground"),
    ("霧", "fog, misty", "in thick fog"),
    ("晴天", "clear sky, sunny", "on a clear sunny day"),
],
"主役の動き": [
    ("ほとんど動かない", None, "almost still, only subtle movement"),
    ("ゆっくり歩く", None, "walking slowly forward"),
    ("振り返る", None, "turning to look back"),
    ("うなずく", None, "nodding slowly"),
    ("櫂で混ぜる", None, "stirring the mash with a long wooden paddle"),
    ("手元で作業する", None, "hands working carefully"),
    ("湯気が立ちのぼる", None, "steam rising and curling upward"),
    ("酒が注がれる", None, "sake being poured into a cup"),
    ("泡が弾ける", None, "bubbles rising and popping on the surface"),
    ("暖簾が風に揺れる", None, "a cloth curtain swaying in the breeze"),
    ("提灯が揺れる", None, "paper lanterns swaying gently"),
    ("火が揺らめく", None, "flames flickering"),
    ("髪が風に揺れる", None, "hair moving in the breeze"),
    ("雪が降る", None, "snow falling gently"),
    ("葉が舞う", None, "leaves drifting through the air"),
    ("盃を口へ運ぶ", None, "raising a cup to the lips"),
],
"カメラの動き": [
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
],
}

# 品質タグ（末尾に付ける）
QUALITY = {
    "illust": "masterpiece, high score, great score, absurdres",
    "photo": "photorealistic, highly detailed, natural lighting, 8k uhd",
    "video": "cinematic, smooth natural motion, highly detailed",
}

# ネガティブ（gen.py のプリセットと揃えてある）
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

# 動画のときだけ出すカテゴリ
VIDEO_ONLY = ("主役の動き", "カメラの動き")

# 常時表示するカテゴリ（残りは「もっと選ぶ」に畳む）
ALWAYS = {
    "illust": ("主役", "場所"),
    "photo": ("主役", "場所"),
    "video": ("主役", "場所", "主役の動き"),
}

# 「おまかせ」で振るときの、カテゴリごとの採用確率
ROLL_CHANCE = {
    "主役": 1.0, "場所": 1.0, "光": 0.9, "画風": 0.8,
    "しぐさ": 0.7, "服装": 0.6, "構図": 0.6,
    "小道具": 0.5, "季節・天気": 0.4,
    "主役の動き": 1.0, "カメラの動き": 0.9,
}


def fragment(entry, model):
    """(日本語, イラスト用, 写実用) から、モデルに応じた英語断片を返す。"""
    jp, illust, photo = entry
    if model in ("photo", "video"):
        return photo if photo else illust
    return illust
