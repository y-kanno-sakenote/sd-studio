# -*- coding: utf-8 -*-
"""人物・ポートレートの語彙モジュール。ジャンルを問わず使い回す土台（人物が必ずいる前提）。"""

TITLE = "人物・ポートレート"
ICON = "🧑"
EXAMPLE = "逆光で笑っている短髪の女性、フィルム写真"
PORT = 8515

# 各項目は (日本語, イラスト用タグ, 写実用の語)。3つめが None ならイラスト用をそのまま使う。
VOCAB = {
"主役": [
    ("若い女性", "1girl, solo, young woman", "a young woman"),
    ("若い男性", "1boy, solo, young man", "a young man"),
    ("落ち着いた大人の女性", "1girl, solo, mature female", "a woman in her forties"),
    ("落ち着いた大人の男性", "1boy, solo, mature male", "a man in his forties"),
    ("年配の女性", "1girl, solo, old woman, wrinkles", "an elderly woman with a deeply lined face"),
    ("年配の男性", "1boy, solo, old man, wrinkles", "an elderly man with a deeply lined face"),
    ("中性的な人物", "1other, solo, androgynous", "an androgynous person"),
    ("褐色肌の女性", "1girl, solo, dark skin, dark-skinned female", "a woman with deep brown skin"),
    ("褐色肌の男性", "1boy, solo, dark skin, dark-skinned male", "a man with deep brown skin"),
    ("眼鏡の知的な女性", "1girl, solo, glasses", "a studious-looking person wearing glasses"),
    ("がっしりした体格の男性", "1boy, solo, muscular male", "a broad-shouldered, powerfully built person"),
    ("ふたり並んで", "2people, two people side by side", "two people standing side by side"),
    ("向かい合うふたり", "2people, facing each other", "two people facing each other"),
    ("小さな集団", "multiple people, group of people", "a small group of people"),
],
"髪": [
    ("長い黒髪", "long hair, black hair", "long black hair"),
    ("短い黒髪", "short hair, black hair", "closely cropped black hair"),
    ("肩までの茶髪", "medium hair, brown hair", "shoulder-length brown hair"),
    ("ボブ", "bob cut", "a blunt bob"),
    ("ポニーテール", "ponytail", "hair pulled back in a ponytail"),
    ("お団子にまとめた", "hair bun", "hair gathered into a bun"),
    ("三つ編み", "braid, braided hair", "a single braid"),
    ("くせのあるうねった髪", "wavy hair", "loose wavy hair"),
    ("細かいカールの髪", "curly hair", "tightly curled hair"),
    ("白髪まじり", "grey hair", "hair going grey at the temples"),
    ("真っ白な髪", "white hair", "fully white hair"),
    ("刈り上げた短髪", "very short hair, undercut", "a close-shaved undercut"),
    ("乱れた髪", "messy hair", "tousled, unbrushed hair"),
    ("片目にかかる前髪", "hair over one eye", "a fringe falling over one eye"),
],
"表情": [
    ("穏やかに微笑む", "smile, closed mouth", "a quiet, closed-lipped smile"),
    ("声を出して笑う", "laughing, open mouth, smile", "laughing openly"),
    ("真剣な顔", "serious", "a serious, concentrated expression"),
    ("無表情", "expressionless", "a neutral, unreadable expression"),
    ("目を閉じている", "closed eyes", "eyes closed"),
    ("こちらをじっと見る", "looking at viewer", "looking straight into the lens"),
    ("視線をそらす", "looking away", "looking away from the camera"),
    ("眠たげな目", "half-closed eyes", "heavy, sleepy eyelids"),
    ("驚いた顔", "surprised, wide eyed", "a startled expression, eyes wide"),
    ("困った顔", "troubled, frown", "a troubled frown"),
    ("物思いにふける", "thinking, pensive", "a thoughtful, faraway look"),
    ("頬を染める", "blush", "a faint flush across the cheeks"),
    ("涙ぐむ", "tears, crying", "eyes brimming with tears"),
    ("眉をひそめる", "furrowed brow", "a furrowed brow"),
],
"服装": [
    ("白いシャツ", "white shirt, collared shirt", "a crisp white shirt"),
    ("黒いタートルネック", "black turtleneck, sweater", "a black turtleneck"),
    ("ざっくりしたニット", "knit sweater", "a chunky knit sweater"),
    ("スーツ", "formal, suit, necktie", "a tailored suit"),
    ("デニムジャケット", "denim jacket", "a denim jacket"),
    ("革のジャケット", "leather jacket", "a worn leather jacket"),
    ("丈の長いコート", "trench coat, long coat", "a long trench coat"),
    ("無地のTシャツ", "t-shirt, simple clothes", "a plain cotton t-shirt"),
    ("薄手のワンピース", "dress, sundress", "a light summer dress"),
    ("パーカー", "hoodie", "a soft hooded sweatshirt"),
    ("和服", "japanese clothes, kimono", "a kimono"),
    ("巻いたマフラー", "scarf", "a scarf wound around the neck"),
    ("つば付きの帽子", "hat, cap", "a brimmed hat"),
    ("細い縁の眼鏡", "glasses, thin-framed eyewear", "thin wire-framed glasses"),
],
"ポーズ": [
    ("まっすぐ立つ", "standing", "standing squarely, facing forward"),
    ("腕を組む", "crossed arms", "arms folded across the chest"),
    ("手をポケットに入れる", "hands in pockets", "hands pushed into the pockets"),
    ("頬に手を当てる", "hand on own cheek", "one hand resting against the cheek"),
    ("腰に手を当てる", "hand on hip", "a hand planted on the hip"),
    ("椅子に座る", "sitting, on chair", "seated on a chair"),
    ("机に肘をつく", "head rest, leaning on table", "elbows on a table, chin resting on the hands"),
    ("壁にもたれる", "leaning against wall", "leaning back against a wall"),
    ("振り返る", "looking back, from behind", "glancing back over the shoulder"),
    ("少し首をかしげる", "head tilt", "head tilted slightly to one side"),
    ("前かがみになる", "leaning forward", "leaning forward toward the camera"),
    ("カップを両手で持つ", "holding cup, two hands", "cradling a cup in both hands"),
    ("眼鏡を直す", "adjusting eyewear", "pushing glasses up the nose"),
    ("髪をかき上げる", "hand in own hair", "pushing a hand back through the hair"),
],
"光": [
    ("窓からの柔らかい光", "soft lighting, indoor light", "soft window light falling across the face"),
    ("片側から斜めの光", "dramatic lighting, side lighting", "light raking in from one side, half the face in shadow"),
    ("逆光で輪郭が光る", "backlighting, rim lighting", "backlit, a bright rim along the hair and shoulders"),
    ("夕方の金色の光", "sunset, golden light", "low golden light late in the day"),
    ("曇りの日の均一な光", "overcast, soft light", "flat, even light on an overcast day"),
    ("木漏れ日", "dappled sunlight", "dappled sunlight through leaves"),
    ("強いコントラストの影", "high contrast, harsh shadows", "hard shadows and bright highlights"),
    ("暗い背景に浮かぶ顔", "dark background, chiaroscuro", "the face emerging from a dark background"),
    ("ネオンの色がかった光", "neon lights, colored lighting", "colored neon light washing over the skin"),
    ("蝋燭の灯り", "candlelight, warm glow", "warm flickering candlelight"),
    ("朝の白い光", "morning light, pale light", "pale early morning light"),
    ("水面の反射光", "reflected light, water reflection", "rippling light reflected off water"),
    ("霧の中の拡散光", "fog, diffused light", "diffused light in thin mist"),
],
"構図・レンズ": [
    ("顔のアップ", "close-up, portrait", "a tight close-up of the face"),
    ("胸から上", "portrait, upper body", "a head and shoulders shot"),
    ("腰から上", "cowboy shot", "framed from the waist up"),
    ("全身", "full body", "a full length shot"),
    ("横顔", "profile, from side", "a profile view"),
    ("背中越し", "from behind", "seen from behind"),
    ("見上げる構図", "from below", "shot from a low angle looking up"),
    ("見下ろす構図", "from above", "shot from above looking down"),
    ("背景がとろける", "depth of field, blurry background", "a very shallow depth of field, the background dissolved"),
    ("背景まで写る広い画", "wide shot, scenery", "a wide shot showing the surroundings"),
    ("手前に何かを入れて覗く", "foreground focus, framed", "something in the foreground partly framing the subject"),
    ("画面の端に寄せる", "off-center composition", "the subject pushed to one side of the frame"),
    ("斜めに傾いた画", "dutch angle", "the frame tilted off axis"),
    ("鏡ごしに写る", "mirror, reflection", "seen in a mirror"),
],
"画風": [
    ("アニメ調", "anime style, cel shading", "a clean cel-shaded illustration"),
    ("やわらかい塗り", "soft shading, pastel colors", "soft airbrushed shading in pale colors"),
    ("厚塗り", "painterly, thick brushwork", "thick visible brushwork"),
    ("水彩", "watercolor (medium)", "a watercolor painting with bleeding edges"),
    ("鉛筆の線画", "sketch, lineart, graphite", "a graphite pencil drawing"),
    ("墨の濃淡", "ink wash, monochrome", "an ink wash drawing in shades of black"),
    ("平たい色面", "flat color, minimal shading", "flat blocks of color with almost no shading"),
    ("レトロな印刷風", "retro artstyle, halftone", "a retro print look with visible halftone dots"),
    ("フィルム写真", "film grain", "shot on 35mm film, visible grain"),
    ("白黒写真", "monochrome, greyscale", "a black and white photograph"),
    ("スタジオの人物写真", "studio portrait, plain backdrop", "a studio portrait against a seamless backdrop"),
    ("スナップ写真", "candid, snapshot", "a candid, unposed snapshot"),
    ("映画のワンシーン", "cinematic lighting, movie still", "a still frame from a film"),
    ("色あせた古い写真", "faded colors, vintage photo", "a faded, slightly yellowed old photograph"),
],
"場所": [
    ("無地の背景", "simple background, grey background", "a plain seamless backdrop"),
    ("窓辺", "window, indoors", "beside a window"),
    ("散らかった部屋", "messy room, indoors", "a cluttered lived-in room"),
    ("台所", "kitchen, indoors", "a kitchen"),
    ("喫茶店の席", "cafe, indoors", "a seat in a small cafe"),
    ("仕事場の机", "office, desk", "a desk in a workplace"),
    ("夜の街路", "city street, night", "a city street at night"),
    ("雑踏", "crowd, city", "a crowded street"),
    ("駅のホーム", "train station, platform", "a railway platform"),
    ("公園の木立", "park, trees", "among the trees of a park"),
    ("草原", "grassland, field, outdoors", "an open grass field"),
    ("海辺", "beach, ocean, outdoors", "the edge of the sea"),
    ("階段の踊り場", "stairs, indoors", "a stairwell landing"),
    ("車の中", "car interior", "inside a parked car"),
    ("古びた建物の廊下", "hallway, old building", "the corridor of an old building"),
],
"主役の動き": [
    ("ほとんど動かない", None, "almost still, only breathing and small shifts"),
    ("ゆっくりまばたきする", None, "blinking slowly"),
    ("こちらを向く", None, "turning to face the camera"),
    ("振り返る", None, "turning to look back over the shoulder"),
    ("うなずく", None, "nodding slowly"),
    ("ゆっくり微笑む", None, "a smile spreading slowly across the face"),
    ("髪をかき上げる", None, "pushing a hand back through the hair"),
    ("ゆっくり歩いてくる", None, "walking slowly toward the camera"),
    ("カップを口へ運ぶ", None, "lifting a cup to the lips"),
    ("目を伏せる", None, "lowering the eyes"),
    ("何かを言いかける", None, "beginning to speak"),
    ("髪が風に揺れる", None, "hair stirring in the breeze"),
    ("手を差し出す", None, "reaching a hand out toward the camera"),
    ("笑い出す", None, "breaking into laughter"),
],
}


# 常時表示するカテゴリ（残りは「もっと選ぶ」に畳む）
ALWAYS = {
    "illust": ("主役", "場所"),
    "photo": ("主役", "場所"),
    "video": ("主役", "場所", "主役の動き"),
}

# 「おまかせ」で振るときの、カテゴリごとの採用確率
ROLL_CHANCE = {
    "主役": 1.0, "場所": 1.0,
    "光": 0.9, "表情": 0.8, "構図・レンズ": 0.8,
    "髪": 0.7, "服装": 0.7, "画風": 0.7,
    "ポーズ": 0.6,
    "主役の動き": 1.0,
}

# 人物が必ずいるジャンルなので、人物なしの分岐は使わない
NO_HUMAN = ()
HUMAN_ONLY_CATS = ()
NO_HUMAN_MOTION = ()

# 照合にだけ使う言い換え。プロンプトには出ない。
ALIASES = {
    "眼鏡の知的な女性": ("メガネ", "めがね"),
    "細い縁の眼鏡": ("メガネ", "めがね"),
}
