# -*- coding: utf-8 -*-
"""風景・自然ジャンルの語彙モジュール（人物のいない自然物・地形・気象が主役）。"""

TITLE = "風景・自然"
ICON = "🏔"
EXAMPLE = "朝もやの立つ針葉樹の林、光が差し込む"
PORT = 8513

# (日本語, イラスト用タグ, 写実用の語)。3つめが None ならイラスト用をそのまま使う。
# イラスト用は Danbooru 系タグ（animagine）、写実用は自然な描写語（juggernaut）。
VOCAB = {
"主役": [
    ("険しい山並み", "mountain, mountainous horizon, scenery, no humans", "a range of jagged mountain peaks"),
    ("一本の大木", "tree, scenery, no humans", "a single great tree standing alone"),
    ("深い森", "forest, tree, scenery, no humans", "a deep forest"),
    ("竹林", "bamboo forest, scenery, no humans", "a bamboo grove"),
    ("滝", "waterfall, water, scenery, no humans", "a tall waterfall"),
    ("湖", "lake, reflection, scenery, no humans", "a still lake"),
    ("荒れた海", "ocean, waves, scenery, no humans", "a rough sea with breaking waves"),
    ("砂浜と波打ち際", "beach, ocean, sand, scenery, no humans", "a sandy shore where the waves run up"),
    ("花畑", "flower field, flower, scenery, no humans", "a field of wildflowers"),
    ("草原", "field, grass, scenery, no humans", "wide open grassland"),
    ("雪原", "snow, field, scenery, no humans", "an empty snowfield"),
    ("砂漠の砂丘", "desert, sand, scenery, no humans", "rolling desert dunes"),
    ("断崖", "cliff, ocean, scenery, no humans", "a sheer cliff above the sea"),
    ("空と雲", "cloud, sky, scenery, no humans", "towering clouds filling the sky"),
    ("棚田", "rice paddy, field, scenery, no humans", "terraced rice paddies on a hillside"),
    ("景色を眺める人", "1girl, from behind, scenery, wide shot", "a lone figure seen from behind, looking out over the landscape"),
],
"場所": [
    ("山の稜線", "mountain, sky, scenery", "high on a mountain ridge"),
    ("谷あいの渓流", "river, rock, forest, scenery", "a mountain stream running through a valley"),
    ("海辺の岬", "cliff, ocean, horizon, scenery", "a headland jutting out into the sea"),
    ("湖のほとり", "lake, shore, scenery", "on the shore of a lake"),
    ("針葉樹の林", "pine tree, forest, scenery", "a stand of tall pines"),
    ("苔むした沢", "moss, rock, water, forest", "a mossy ravine with water running over stones"),
    ("田んぼと畦道", "rice paddy, path, scenery", "rice fields with narrow paths between them"),
    ("山あいの集落", "village, mountain, scenery", "a small village at the foot of the mountains"),
    ("火山の山肌", "volcano, smoke, scenery", "the bare slope of a volcano"),
    ("氷の海", "ice, snow, ocean, scenery", "a glacier meeting an icy sea"),
    ("洞窟の中から", "cave, light, scenery", "from inside a cave, looking out"),
    ("砂丘の連なり", "desert, sand, scenery", "a chain of sand dunes"),
    ("湿原", "water, grass, field, scenery", "a wetland of shallow water and reeds"),
    ("岩だらけの海岸", "rock, ocean, waves, scenery", "a rocky coastline"),
    ("峠の一本道", "road, mountain, scenery", "a single road winding over a mountain pass"),
],
"時間帯・光": [
    ("夜明け前", "night, gradient sky, scenery", "the pale twilight before dawn"),
    ("日の出", "sunrise, sun, orange sky", "sunrise, the sun just clearing the horizon"),
    ("朝もや", "morning, fog, sunlight", "early morning haze"),
    ("真昼の強い日差し", "day, sunlight, blue sky", "harsh midday sun"),
    ("木漏れ日", "sunbeam, light rays, forest", "sunlight filtering down through leaves"),
    ("夕焼け", "sunset, orange sky, cloud", "a burning sunset sky"),
    ("日没直後の青い時間", "evening, gradient sky, dark blue", "the blue hour just after sunset"),
    ("星空", "starry sky, night, star (sky)", "a sky full of stars"),
    ("天の川", "milky way, starry sky, night", "the milky way arching overhead"),
    ("満月の夜", "full moon, night, moonlight", "a bright full moon at night"),
    ("逆光", "backlighting, silhouette", "backlit, the landscape reduced to silhouette"),
    ("雲間からの光", "light rays, cloud, sunlight", "shafts of light breaking through the clouds"),
    ("オーロラ", "aurora, night sky, star (sky)", "the aurora rippling across the night sky"),
],
"天候": [
    ("快晴", "clear sky, blue sky, sunny", "a perfectly clear sky"),
    ("うろこ雲", "cloudy sky, cloud, blue sky", "a sky patterned with small scattered clouds"),
    ("厚い曇り", "cloudy sky, grey sky", "a heavy overcast sky"),
    ("入道雲", "cloud, summer, blue sky", "towering thunderheads"),
    ("通り雨", "rain, wet, scenery", "a passing rain shower"),
    ("土砂降り", "rain, storm, wet", "pouring rain"),
    ("雷", "lightning, storm, cloud", "lightning splitting a dark sky"),
    ("濃霧", "fog, mist", "thick fog"),
    ("雪が降る", "snowing, snow", "falling snow"),
    ("吹雪", "snowing, snow, wind", "a blizzard of driving snow"),
    ("虹", "rainbow, sky, cloud", "a rainbow after the rain"),
    ("雨上がりの光", "wet, sunlight, puddle", "sunlight breaking out after rain, everything wet"),
],
"季節": [
    ("桜の季節", "cherry blossoms, spring, falling petals", "cherry trees in full bloom"),
    ("新緑", "spring, tree, leaf, green theme", "the fresh green of early spring"),
    ("夏草の盛り", "summer, grass, green theme", "summer grass at its thickest"),
    ("蝉の鳴く午後", "summer, cicada, tree", "a hot summer afternoon loud with cicadas"),
    ("紅葉", "autumn leaves, autumn, red theme", "autumn foliage turned red and gold"),
    ("枯れ野", "autumn, field, bare tree", "a withered, brown field"),
    ("初雪", "winter, snow, snowing", "the first snow of the year"),
    ("厳冬", "winter, snow, ice", "deep winter, everything frozen hard"),
    ("雪解け", "snow, water, spring", "snow melting into running water"),
    ("梅雨", "rain, wet, green theme", "the rainy season, everything damp and green"),
],
"水と空": [
    ("鏡のような水面", "reflection, reflective water, lake", "water as still as a mirror"),
    ("波が砕ける", "waves, ocean, water", "waves breaking into white spray"),
    ("川面のきらめき", "river, sparkle, sunlight", "sunlight glittering on the surface of the river"),
    ("水面に映る月", "moon, reflection, water", "the moon reflected on the water"),
    ("透き通った浅瀬", "water, rock, reflection", "clear shallow water running over stones"),
    ("渦を巻く流れ", "water, river, rock", "water swirling in a slow eddy"),
    ("立ちこめる水蒸気", "steam, water, hot spring", "steam rising off the water"),
    ("雲海", "cloud, mountain, scenery", "a sea of clouds lying below the peaks"),
    ("空いっぱいの雲", "cloud, cloudy sky, sky", "clouds filling the whole sky"),
    ("低い雲が流れる", "cloud, wind, sky", "low clouds streaming past"),
    ("氷の張った水面", "ice, water, winter", "a sheet of ice over the water"),
    ("水たまりに映る空", "puddle, reflection, sky", "the sky mirrored in a puddle"),
],
"構図・画角": [
    ("広大な引き", "wide shot, scenery", "an extremely wide establishing shot"),
    ("地平線を低く", "horizon, sky, wide shot", "a low horizon with a vast sky above"),
    ("空を広くとる", "sky, cloud, wide shot", "most of the frame given over to the sky"),
    ("見上げる", "from below, sky", "looking steeply upward"),
    ("見下ろす", "from above, scenery", "seen from high above"),
    ("手前に草や枝", "blurry foreground, leaf, grass", "grass and branches framing the foreground"),
    ("道が奥へ続く", "road, scenery, perspective", "a path leading away into the distance"),
    ("左右対称", "symmetry, reflection", "a symmetrical composition"),
    ("遠近が強い", "perspective, scenery", "strong perspective, great depth"),
    ("細部のアップ", "close-up, detail", "a close-up of surface texture"),
    ("霞む遠景", "fog, depth of field, scenery", "distant layers fading into haze"),
    ("縦に長い構図", "tall image, scenery", "a tall vertical composition"),
],
"画風": [
    ("アニメ背景美術", "anime style, scenery, detailed background", "a painted anime-style background"),
    ("水彩", "watercolor (medium), traditional media", "a watercolor painting"),
    ("墨絵", "monochrome, traditional media, ink wash painting", "an ink wash painting"),
    ("浮世絵", "ukiyo-e, traditional media", "in the style of a woodblock print"),
    ("油彩の厚塗り", "oil painting (medium), painterly", "a thickly painted oil landscape"),
    ("淡いパステル", "pastel colors, soft", "a soft pastel color palette"),
    ("レトロな旅行ポスター", "retro artstyle, flat color", "a retro travel poster"),
    ("ドット絵", "pixel art", None),
    ("風景写真", "realistic, photorealistic", "a landscape photograph"),
    ("フィルムの粒子", "film grain, realistic", "shot on film, visible grain"),
    ("白黒写真", "monochrome, greyscale", "a black and white photograph"),
    ("シネマ的な色", "cinematic lighting, scenery", "cinematic color grading, a film still"),
    ("長時間露光", "motion blur, scenery", "a long exposure, motion smeared into streaks"),
],
"主役の動き": [
    ("ほとんど動かない", None, "almost still, only the faintest movement"),
    ("雲がゆっくり流れる", None, "clouds drifting slowly across the sky"),
    ("霧が木立を抜ける", None, "mist drifting through the trees"),
    ("波が寄せては返す", None, "waves rolling in and washing back"),
    ("波が岩に砕ける", None, "waves crashing against the rocks"),
    ("川が流れ下る", None, "water tumbling downstream over the rocks"),
    ("滝が落ち続ける", None, "water pouring endlessly over the falls"),
    ("草が風に波打つ", None, "grass rippling in the wind"),
    ("花びらが舞う", None, "petals drifting through the air"),
    ("雨が降りしきる", None, "rain falling steadily, rings spreading on the water"),
    ("雪が静かに降る", None, "snow falling quietly"),
    ("光が移ろう", None, "the light slowly shifting across the landscape"),
    ("星がゆっくり回る", None, "the stars wheeling slowly overhead"),
    ("水面が揺れる", None, "the surface rippling, breaking up the reflection"),
    ("鳥の群れが横切る", None, "a flock of birds crossing the frame"),
    ("人影がゆっくり歩く", None, "a lone figure walking slowly through the scene"),
],
}

# 主役が人物なしのとき、人物前提のカテゴリ・動きを足すと矛盾する
NO_HUMAN = ("険しい山並み", "一本の大木", "深い森", "竹林", "滝", "湖", "荒れた海",
            "砂浜と波打ち際", "花畑", "草原", "雪原", "砂漠の砂丘", "断崖", "空と雲", "棚田")
HUMAN_ONLY_CATS = ()
NO_HUMAN_MOTION = ("ほとんど動かない", "雲がゆっくり流れる", "霧が木立を抜ける",
                   "波が寄せては返す", "波が岩に砕ける", "川が流れ下る", "滝が落ち続ける",
                   "草が風に波打つ", "花びらが舞う", "雨が降りしきる", "雪が静かに降る",
                   "光が移ろう", "星がゆっくり回る", "水面が揺れる", "鳥の群れが横切る")


# 常時表示するカテゴリ（残りは「もっと選ぶ」に畳む）
ALWAYS = {
    "illust": ("主役", "場所"),
    "photo": ("主役", "場所"),
    "video": ("主役", "場所", "主役の動き"),
}

# 「おまかせ」で振るときの、カテゴリごとの採用確率
ROLL_CHANCE = {
    "主役": 1.0, "場所": 1.0,
    "時間帯・光": 0.9, "天候": 0.8, "水と空": 0.7,
    "画風": 0.7, "構図・画角": 0.6, "季節": 0.5,
    "主役の動き": 1.0,
}

# 照合にだけ使う言い換え。プロンプトには出ない。
ALIASES = {
    "針葉樹の林": ("杉林", "松林", "杉", "林"),
    "深い森": ("森", "樹海"),
    "朝もや": ("朝靄", "もや", "靄"),
}
