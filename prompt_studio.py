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
from vocab import VOCAB, QUALITY, NEGATIVE, ROLL_CHANCE, fragment  # noqa: E402

st.set_page_config(page_title="プロンプト工房", page_icon="🍶", layout="wide")

MODELS = {"イラスト（animagine）": "illust", "写実（juggernautXL）": "photo"}

st.title("🍶 プロンプト工房")
st.caption("日本語で選ぶと英語のプロンプトができる。ComfyUI のプロンプト欄に貼って使う。")

label = st.radio("モデル", list(MODELS), horizontal=True)
model = MODELS[label]

c1, c2, _ = st.columns([1, 1, 4])
if c1.button("🎲 おまかせ", use_container_width=True):
    for cat, entries in VOCAB.items():
        hit = random.random() < ROLL_CHANCE.get(cat, 0.5)
        st.session_state[f"sel_{cat}"] = [random.choice(entries)[0]] if hit else []
if c2.button("消す"):
    for cat in VOCAB:
        st.session_state[f"sel_{cat}"] = []

st.divider()

cats = list(VOCAB)
MAIN = [c for c in ("主役", "場所") if c in cats]  # 語彙側が変わっても壊れないように
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

# --- 組み立て ---
parts = []
for cat in cats:
    for jp in picked[cat]:
        entry = next(e for e in VOCAB[cat] if e[0] == jp)
        parts.append(fragment(entry, model))

st.divider()
free = st.text_input("自由に足す", "", help="英語で。カンマ区切り")
add_quality = st.checkbox("画質の指定を足す", value=True)

if free.strip():
    parts.append(free.strip())
if add_quality:
    parts.append(QUALITY[model])

prompt = ", ".join(p for p in parts if p)

st.subheader("プロンプト")
if prompt:
    st.code(prompt, language=None)
else:
    st.info("上から選ぶか「おまかせ」を押す")

# ネガティブは選んだ内容で変わらない。要るときだけ開く
with st.expander("ネガティブ（毎回同じ。一度貼れば済む）"):
    st.code(NEGATIVE[model], language=None)
