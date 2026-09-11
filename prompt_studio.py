# -*- coding: utf-8 -*-
"""プロンプト工房 — 日本語で選ぶと英語プロンプトが組み上がる。

  dev/sd-studio/bin/prompt_studio.sh <ジャンル>

ジャンルごとに別ポート・別プロセスで動く。語彙は genres/<ジャンル>.py。
出てきた文字列をComfyUIのプロンプト欄に貼る。生成はしない。
"""
import os
import random
import sys
import pathlib

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "genres"))
import _common  # noqa: E402
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from matcher import match as match_words, unmatched  # noqa: E402
from _common import QUALITY, NEGATIVE, VIDEO_ONLY, fragment  # noqa: E402

GENRE = os.environ.get("SD_STUDIO_GENRE", "brewing")
try:
    g = _common.load(GENRE)
except Exception as e:  # 語彙ファイルの不備は起動時にはっきり出す
    st.error(f"ジャンル『{GENRE}』を読み込めない: {e}")
    st.stop()

VOCAB, ALWAYS, ROLL_CHANCE = g.VOCAB, g.ALWAYS, g.ROLL_CHANCE
NO_HUMAN, HUMAN_ONLY_CATS = g.NO_HUMAN, g.HUMAN_ONLY_CATS
NO_HUMAN_MOTION = g.NO_HUMAN_MOTION

st.set_page_config(page_title=f"プロンプト工房 — {g.TITLE}", page_icon=g.ICON, layout="wide")

MODELS = {"イラスト（animagine）": "illust",
          "写実（juggernautXL）": "photo",
          "動画（LTXV）": "video"}

st.title(f"{g.ICON} プロンプト工房　{g.TITLE}")
st.caption("日本語で選ぶと英語のプロンプトができる。ComfyUI のプロンプト欄に貼って使う。")

label = st.radio("モデル", list(MODELS), horizontal=True)
model = MODELS[label]

# 文章で書いて、そこから語彙を拾う。拾った結果は下の選択欄に入るので、あとから直せる。
f1, f2 = st.columns([5, 1])
sentence = f1.text_input("文章で書く", "", label_visibility="collapsed",
                         placeholder=getattr(g, "EXAMPLE", "作りたい絵を文章で書く"))
picked_empty = False
if f2.button("言葉を拾う", use_container_width=True):
    if sentence.strip():
        found = match_words(sentence, VOCAB, getattr(g, "ALIASES", None))
        for cat in VOCAB:
            st.session_state[f"sel_{cat}"] = found.get(cat, [])
        picked_empty = not found
        chosen = [lab for labs in found.values() for lab in labs]
        st.session_state["_missed"] = unmatched(
            sentence, VOCAB, getattr(g, "ALIASES", None), chosen)
    else:
        # text_input は Enter を押すまで値が渡らない。黙って空振りさせない。
        st.warning("文章を入れて **Enter** を押してから「言葉を拾う」")

if picked_empty:
    st.info("拾える言葉が無かった。下から直接選ぶか、別の言い方で書いてみる")

missing, overridden = st.session_state.get("_missed") or ([], [])
if overridden:
    st.warning("**" + "、".join(overridden) + "** は語彙にあるが選ばれなかった"
               "（同じ枠で別の候補が勝った）。下の選択欄で直せる")
if missing:
    st.caption("語彙に無い言葉：" + "、".join(missing)
               + f"　— 要るなら genres/{GENRE}.py に足す")

c1, c2, _ = st.columns([1, 1, 4])
if c1.button("🎲 おまかせ", use_container_width=True):
    # 「主役」が無い工房（表から取り込んだものなど）もあるので先頭カテゴリで代用する
    subject_cat = "主役" if "主役" in VOCAB else next(
        (c for c in VOCAB if c not in VIDEO_ONLY), None)
    subject = random.choice(VOCAB[subject_cat])[0] if subject_cat else None
    no_human = subject in NO_HUMAN
    for cat, entries in VOCAB.items():
        if cat in VIDEO_ONLY and model != "video":
            st.session_state[f"sel_{cat}"] = []
            continue
        if cat == subject_cat:
            st.session_state[f"sel_{cat}"] = [subject]
            continue
        # 人物がいない絵に服装や表情を足さない
        if no_human and cat in HUMAN_ONLY_CATS:
            st.session_state[f"sel_{cat}"] = []
            continue
        pool = entries
        if no_human and cat == "主役の動き":
            pool = [e for e in entries if e[0] in NO_HUMAN_MOTION]
        hit = random.random() < ROLL_CHANCE.get(cat, 0.5)
        st.session_state[f"sel_{cat}"] = [random.choice(pool)[0]] if hit and pool else []
if c2.button("消す"):
    for cat in VOCAB:
        st.session_state[f"sel_{cat}"] = []
    st.session_state["_picked_from"] = None

st.divider()

cats = [c for c in VOCAB if model == "video" or c not in VIDEO_ONLY]
MAIN = [c for c in ALWAYS.get(model, ()) if c in cats]  # 語彙側が変わっても壊れないように
rest = [c for c in cats if c not in MAIN]
picked = {}


def pick(cat):
    labels = [e[0] for e in VOCAB[cat]]
    picked[cat] = st.multiselect(cat, labels, key=f"sel_{cat}")


cols = st.columns(len(MAIN)) if MAIN else []
for i, cat in enumerate(MAIN):
    with cols[i]:
        pick(cat)

# 畳んだ中身が効いていることは、見出しに選んだ名前を並べて伝える
chosen = [v for c in rest for v in st.session_state.get(f"sel_{c}", [])]
head = "もっと選ぶ" + ("　" + "、".join(chosen) if chosen else "")
with st.expander(head):
    cols = st.columns(3)
    for i, cat in enumerate(rest):
        with cols[i % 3]:
            pick(cat)

st.divider()
free = st.text_input("自由に足す", "", help="英語で。カンマ区切り")
add_quality = st.checkbox("画質の指定を足す", value=True)


def dedupe(parts, token_level):
    """重複を落とす。タグ列は語単位、英文は断片単位で見る。

    語彙どうしが同じ語を含むことは避けられない（風景の多くが scenery を持つ等）。
    重ねるとSDXLでその語の重みが不当に上がるので、組み立て時に1回だけにする。
    """
    seen, out = set(), []
    for p in parts:
        for piece in (p.split(",") if token_level else [p]):
            piece = piece.strip()
            key = piece.lower()
            if piece and key not in seen:
                seen.add(key)
                out.append(piece)
    return out


def compose(m, target_cats):
    """選択が何も無ければ空を返す（画質タグだけのプロンプトは出さない）。"""
    parts = [fragment(next(e for e in VOCAB[c] if e[0] == jp), m)
             for c in target_cats for jp in picked.get(c, [])]
    if free.strip():
        parts.append(free.strip())
    if not parts:
        return ""
    if add_quality:
        parts.append(QUALITY[m])
    return ", ".join(dedupe([p for p in parts if p], token_level=(m == "illust")))


def show(title, body, note=None, placeholder=True):
    st.subheader(title)
    if note:
        st.caption(note)
    if body:
        st.code(body, language=None)
    elif placeholder:
        st.info("上から選ぶか「おまかせ」を押す")


if model == "video":
    # 動画は「情景＋動き」で書くのが最良（実測）。その情景と揃った静止画用も同時に出す。
    show("動画用", compose("video", cats), "`3_動画` か `4_静止画から動画` に貼る")
    still_cats = [c for c in cats if c not in VIDEO_ONLY]
    still = compose("illust", still_cats)
    if still:
        show("元の静止画用（`4_静止画から動画` を使うときだけ）", still,
             "`1_イラスト` で1枚描いて、その絵を `4` に渡す", placeholder=False)
    with st.expander("ネガティブ（毎回同じ。一度貼れば済む）"):
        st.caption("動画用")
        st.code(NEGATIVE["video"], language=None)
        st.caption("静止画用")
        st.code(NEGATIVE["illust"], language=None)
else:
    show("プロンプト", compose(model, cats))
    with st.expander("ネガティブ（毎回同じ。一度貼れば済む）"):
        st.code(NEGATIVE[model], language=None)
