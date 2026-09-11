# -*- coding: utf-8 -*-
"""プロンプト工房 — 日本語で選ぶと英語プロンプトが組み上がる。

  dev/sd-studio/bin/prompt_studio.sh   （http://localhost:8511）

出てきた文字列をComfyUIのプロンプト欄に貼る。生成はしない。
"""
import random
import sys
import pathlib

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "prompts"))
from vocab import (VOCAB, QUALITY, NEGATIVE, ROLL_CHANCE, VIDEO_ONLY,  # noqa: E402
                   ALWAYS, fragment)

st.set_page_config(page_title="プロンプト工房", page_icon="🍶", layout="wide")

MODELS = {"イラスト（animagine）": "illust",
          "写実（juggernautXL）": "photo",
          "動画（LTXV）": "video"}

st.title("🍶 プロンプト工房")
st.caption("日本語で選ぶと英語のプロンプトができる。ComfyUI のプロンプト欄に貼って使う。")

label = st.radio("モデル", list(MODELS), horizontal=True)
model = MODELS[label]

c1, c2, _ = st.columns([1, 1, 4])
if c1.button("🎲 おまかせ", use_container_width=True):
    for cat, entries in VOCAB.items():
        if cat in VIDEO_ONLY and model != "video":
            st.session_state[f"sel_{cat}"] = []
            continue
        hit = random.random() < ROLL_CHANCE.get(cat, 0.5)
        st.session_state[f"sel_{cat}"] = [random.choice(entries)[0]] if hit else []
if c2.button("消す"):
    for cat in VOCAB:
        st.session_state[f"sel_{cat}"] = []

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


def compose(m, target_cats):
    parts = [fragment(next(e for e in VOCAB[c] if e[0] == jp), m)
             for c in target_cats for jp in picked.get(c, [])]
    if free.strip():
        parts.append(free.strip())
    if add_quality:
        parts.append(QUALITY[m])
    return ", ".join(p for p in parts if p)


def show(title, body, note=None):
    st.subheader(title)
    if note:
        st.caption(note)
    if body:
        st.code(body, language=None)
    else:
        st.info("上から選ぶか「おまかせ」を押す")


if model == "video":
    # 動画は「情景＋動き」で書くのが最良（実測）。その情景と揃った静止画用も同時に出す。
    show("動画用", compose("video", cats), "`3_動画` か `4_静止画から動画` のプロンプト欄に貼る")
    still_cats = [c for c in cats if c not in VIDEO_ONLY]
    show("元になる静止画用", compose("illust", still_cats),
         "`4_静止画から動画` を使うときだけ。まず `1_イラスト` でこれを貼って1枚描き、"
         "その絵を4に渡す。情景が揃うので動画側が絵を保ちやすい")
    with st.expander("ネガティブ（毎回同じ。一度貼れば済む）"):
        st.caption("動画用")
        st.code(NEGATIVE["video"], language=None)
        st.caption("静止画用")
        st.code(NEGATIVE["illust"], language=None)
else:
    show("プロンプト", compose(model, cats))
    with st.expander("ネガティブ（毎回同じ。一度貼れば済む）"):
        st.code(NEGATIVE[model], language=None)
