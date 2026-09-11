# -*- coding: utf-8 -*-
"""ファンタジー（異世界・魔法）ジャンルの語彙モジュール。日本語ラベル → 英語プロンプト断片。"""

TITLE = "ファンタジー"
ICON = "🗡"
PORT = 8512

# 各項目は (日本語, イラスト用タグ, 写実用の語) の3つ組。3つめが None ならイラスト用を流用。
VOCAB = {
"主役": [
    ("女剣士", "1girl, knight, armor, sword", "a woman knight holding a sword"),
    ("男の騎士", "1boy, knight, full armor, sword", "a knight in full plate armor"),
    ("魔法使いの少女", "1girl, witch, witch hat, staff", "a young sorceress holding a staff"),
    ("年老いた魔法使い", "1boy, old man, wizard, long beard, robe", "an elderly wizard with a long white beard"),
    ("エルフの射手", "1girl, elf, pointy ears, bow (weapon)", "an elf archer with a longbow"),
    ("フードの旅人", "1girl, hood, cloak, backpack", "a hooded traveler with a worn cloak"),
    ("身軽な盗賊", "1boy, hood, dagger, dark clothes", "a nimble rogue holding a dagger"),
    ("獣耳の戦士", "1girl, animal ears, tail, armor", "a warrior with beast ears and a tail"),
    ("王女", "1girl, princess, tiara, dress", "a princess in a formal gown"),
    ("小さな妖精", "fairy, fairy wings, minigirl, glowing", "a tiny winged fairy, glowing faintly"),
    ("竜と少女", "1girl, dragon", "a girl standing beside a large dragon"),
    ("竜だけ", "dragon, no humans", "a large dragon, no people"),
    ("人物なし（遺跡）", "no humans, ruins, scenery", "ancient ruins, no people"),
    ("人物なし（城）", "no humans, castle, scenery", "a distant castle, no people"),
],
"服装・装備": [
    ("板金の鎧", "plate armor, pauldrons", "polished plate armor"),
    ("鎖帷子", "chainmail", "a chainmail shirt"),
    ("革の軽装", "leather armor, belt", "light leather armor"),
    ("長いローブ", "long robe, wide sleeves", "a long flowing robe"),
    ("とんがり帽子", "witch hat", "a tall pointed hat"),
    ("兜", "helmet", "a steel helmet"),
    ("赤いマント", "red cape", "a red cape"),
    ("フードを目深に", "hood, hood up, shadowed face", "a deep hood shadowing the face"),
    ("大きな剣を背負う", "greatsword, sword on back", "a greatsword strapped across the back"),
    ("弓と矢筒", "bow (weapon), quiver, arrow", "a longbow and a quiver of arrows"),
    ("杖を持つ", "holding staff", "holding a tall wooden staff"),
    ("護符の首飾り", "amulet, pendant, jewelry", "an amulet hanging on a cord"),
],
"しぐさ": [
    ("静かに微笑む", "smile, gentle expression", "smiling quietly"),
    ("鋭い目つき", "serious, sharp eyes", "a sharp, determined gaze"),
    ("剣を構える", "holding sword, fighting stance", "holding a sword in a ready stance"),
    ("呪文を唱える", "casting spell, magic, glowing hand", "casting a spell, one hand glowing"),
    ("本を読む", "reading, open book", "reading from an open book"),
    ("祈る", "praying, own hands clasped", "praying with hands clasped"),
    ("こちらを見る", "looking at viewer", "looking directly at the camera"),
    ("振り返る", "looking back, looking over shoulder", "looking back over one shoulder"),
    ("膝をついて息をつく", "kneeling, injured, exhausted", "kneeling, wounded and out of breath"),
    ("手を差し出す", "outstretched hand, reaching out", "reaching out an open hand"),
    ("笑い合う", "laughing", "laughing together"),
    ("遠くを見る", "looking afar", "gazing into the distance"),
],
"場所": [
    ("古城の広間", "castle interior, stone pillars, banner", "the great hall of an old castle"),
    ("石造りの砦", "stone fortress, battlements", "a stone fortress with high battlements"),
    ("深い森", "forest, tree, moss", "a deep mossy forest"),
    ("苔むした遺跡", "ruins, moss, vines, overgrown", "ruins overgrown with moss and vines"),
    ("古い図書館", "library, bookshelf, candle", "a vast library of towering bookshelves"),
    ("地下の洞窟", "cave, underground, rock", "an underground cavern"),
    ("宿場の酒場", "tavern, wooden table, fireplace", "the common room of a roadside tavern"),
    ("石畳の市場", "market, cobblestone, stall, crowd", "a cobblestone market square"),
    ("雪の山道", "snow, mountain, path", "a snowbound mountain path"),
    ("大きな滝", "waterfall, river, cliff", "a tall waterfall over a cliff"),
    ("竜の棲む岩場", "dragon, rocks, treasure, gold coins", "a rocky lair scattered with treasure"),
    ("浮かぶ島", "floating island, sky, cloud", "an island floating in the sky"),
    ("玉座の間", "throne room, throne, banner", "a throne room lined with banners"),
    ("荒野の街道", "wasteland, road, distant mountain", "a dirt road across an empty wasteland"),
],
"魔法・小道具": [
    ("魔法陣", "magic circle, glowing runes", "a glowing circle of runes on the ground"),
    ("光る杖", "glowing staff, magic", "a staff with a glowing tip"),
    ("舞う光の粒", "floating light particles, glowing", "motes of light floating in the air"),
    ("炎の魔法", "fire, flame, magic", "a burst of conjured flame"),
    ("氷の魔法", "ice, ice crystal, magic", "shards of conjured ice"),
    ("雷の魔法", "lightning, electricity, magic", "arcs of crackling lightning"),
    ("回復の光", "healing, warm glow, magic", "a warm healing light"),
    ("古い巻物", "scroll, parchment", "an old parchment scroll"),
    ("分厚い魔導書", "book, open book, magic", "a thick spellbook lying open"),
    ("水晶玉", "crystal ball", "a clouded crystal ball"),
    ("光る剣", "glowing sword, magic sword", "a sword glowing along the blade"),
    ("宝箱と金貨", "treasure chest, gold coins", "an open chest spilling gold coins"),
    ("吊り下げた灯り", "lantern, hanging lantern", "a lantern hanging from a hook"),
],
"光": [
    ("木漏れ日", "sunbeam, dappled sunlight", "dappled sunlight through leaves"),
    ("窓からの光", "light rays, window, god rays", "shafts of light from a high window"),
    ("松明の灯り", "torch, warm orange light", "the orange glow of torches"),
    ("蝋燭", "candlelight", "candlelight"),
    ("月明かり", "moonlight, blue theme", "cold moonlight"),
    ("逆光", "backlighting, rim light", "backlit with a bright rim of light"),
    ("青白い魔法の光", "blue glow, magical light", "a pale blue magical glow"),
    ("焚き火", "campfire, firelight", "the light of a campfire"),
    ("埃が舞う光", "dust particles, light rays", "dust drifting through a beam of light"),
    ("深い影", "dark, dim lighting, shadow", "a dim space with deep shadows"),
    ("金色の夕陽", "golden hour, sunset light", "low golden sunlight"),
],
"構図": [
    ("顔のアップ", "close-up, face focus", "a close-up of the face"),
    ("上半身", "upper body", "an upper body shot"),
    ("全身", "full body", "a full body shot"),
    ("見上げる構図", "from below, low angle", "shot from a low angle"),
    ("見下ろす構図", "from above, high angle", "shot from above"),
    ("引きの風景", "wide shot, scenery", "a wide establishing shot"),
    ("手元のアップ", "close-up of hands", "a close-up of the hands"),
    ("横顔", "profile", "a profile view"),
    ("背中越し", "from behind", "seen from behind"),
    ("背景をぼかす", "depth of field, blurry background", "shallow depth of field, blurred background"),
    ("左右対称", "symmetrical composition", "a symmetrical composition"),
],
"画風": [
    ("アニメ調", "anime style, cel shaded", None),
    ("水彩", "watercolor, soft edges", "a watercolor painting"),
    ("厚塗りの油彩", "oil painting, thick brushwork", "an oil painting with thick brushwork"),
    ("ペン画", "line art, ink drawing, monochrome", "a pen and ink drawing"),
    ("設定画風", "concept art, detailed", "concept art for a fantasy film"),
    ("カード絵風", "trading card art, dramatic lighting", "dramatic fantasy card art"),
    ("絵本風", "storybook illustration, soft colors", "a storybook illustration"),
    ("シネマティック", "cinematic lighting, movie still", "a cinematic film still"),
    ("写実的な絵画", "realistic, highly detailed painting", "a photorealistic painting"),
    ("モノクロ", "monochrome, greyscale", "in black and white"),
    ("淡い色", "pastel colors, soft palette", "a soft pastel color palette"),
],
"時間・天候": [
    ("朝もや", "morning, mist", "in the morning mist"),
    ("昼下がり", "day, afternoon", "in the early afternoon"),
    ("夕暮れ", "sunset, orange sky", "at sunset"),
    ("夜", "night, star (sky)", "at night under the stars"),
    ("満月の夜", "night, full moon", "on a night with a full moon"),
    ("雨", "rain, wet", "in the rain, everything wet"),
    ("雪", "snow, snowing", "with snow falling"),
    ("霧", "fog, mist", "in thick fog"),
    ("嵐", "storm, dark clouds, lightning", "in a storm, dark clouds and lightning"),
    ("晴天", "clear sky, sunny", "under a clear blue sky"),
],
"主役の動き": [
    ("ほとんど動かない", None, "almost still, only subtle movement"),
    ("ゆっくり歩く", None, "walking slowly forward"),
    ("振り返る", None, "turning to look back"),
    ("剣を抜く", None, "drawing a sword from its sheath"),
    ("剣を振る", None, "swinging a sword in a wide arc"),
    ("呪文を唱える", None, "chanting a spell, light gathering in the hand"),
    ("杖を掲げる", None, "raising a staff overhead"),
    ("マントがはためく", None, "a cloak billowing in the wind"),
    ("髪が風に揺れる", None, "hair moving in the breeze"),
    ("光の粒が舞い上がる", None, "motes of light drifting upward"),
    ("炎が揺らめく", None, "flames flickering and curling"),
    ("魔法陣が回る", None, "a glowing magic circle slowly rotating"),
    ("雪が降る", None, "snow falling gently"),
    ("木の葉が舞う", None, "leaves drifting through the air"),
    ("水面が揺れる", None, "water rippling across the surface"),
    ("竜が翼を広げる", None, "a dragon spreading its wings"),
],
}


# 主役に人物がいないとき、服装や表情を足すと矛盾する
NO_HUMAN = ("竜だけ", "人物なし（遺跡）", "人物なし（城）")
HUMAN_ONLY_CATS = ("服装・装備", "しぐさ")
NO_HUMAN_MOTION = ("ほとんど動かない", "光の粒が舞い上がる", "炎が揺らめく", "魔法陣が回る",
                   "雪が降る", "木の葉が舞う", "水面が揺れる", "竜が翼を広げる")


# 常時表示するカテゴリ（残りは「もっと選ぶ」に畳む）
ALWAYS = {
    "illust": ("主役", "場所"),
    "photo": ("主役", "場所"),
    "video": ("主役", "場所", "主役の動き"),
}

# 「おまかせ」で振るときの、カテゴリごとの採用確率
ROLL_CHANCE = {
    "主役": 1.0,
    "場所": 1.0,
    "光": 0.9,
    "画風": 0.8,
    "しぐさ": 0.7,
    "服装・装備": 0.7,
    "構図": 0.6,
    "魔法・小道具": 0.5,
    "時間・天候": 0.4,
    "主役の動き": 1.0,
}


