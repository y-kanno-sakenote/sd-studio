#!/usr/bin/env python3
# 担当: ✅ 検証係（マンガー×ファインマン）
# 2026-09-13 再検証: 直した6点（同点/おまかせ×人物なし/_gone/BASE/壊れたJSON）と回帰を Streamlit AppTest で実測。
# genres/test.py と saved/ は複製しない。BASE は複製した brewing に BASE を足した合成ジャンル qabase で測る。
#   dev/jbsj/.venv/bin/python verification/qa_recheck_apptest.py
import os, sys, json, pathlib, shutil, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
S = pathlib.Path(tempfile.mkdtemp(prefix="sdstudio_qa2_"))
(S / "app" / "genres").mkdir(parents=True)
for f in ("prompt_studio.py", "matcher.py"):
    shutil.copy(ROOT / f, S / "app" / f)
for f in (ROOT / "genres").glob("*.py"):
    if f.name != "test.py":
        shutil.copy(f, S / "app" / "genres" / f.name)
BASE = {"illust": "masterpiece, sake brewery art, absurdres",
        "photo": "photorealistic, sake brewery photo, 8k uhd",
        "video": "cinematic, sake brewery footage"}
(S / "app" / "genres" / "qabase.py").write_text(
    (ROOT / "genres" / "brewing.py").read_text(encoding="utf-8") + f"\nBASE = {BASE!r}\nPORT = 8599\n", encoding="utf-8")
APP = S / "app" / "prompt_studio.py"
sys.path.insert(0, str(S / "app" / "genres")); sys.path.insert(0, str(S / "app"))
from streamlit.testing.v1 import AppTest
import _common
from _common import QUALITY

def new(genre):
    os.environ["SD_STUDIO_GENRE"] = genre
    return AppTest.from_file(str(APP), default_timeout=60).run()
def btn(at, label): return [b for b in at.button if b.label == label][0]
def prompt(at): return at.code[0].value if at.code else ""
def ss(at, k): return at.session_state[k] if k in at.session_state else "<absent>"
def warns(at): return [w.value for w in at.warning]
def errs(at): return [e.value for e in at.error]
def excs(at): return [str(e.value)[:160] for e in at.exception]
def pick_words(at, text):
    [t for t in at.text_input if t.label == "文章で書く"][0].input(text); at = at.run()
    return btn(at, "言葉を拾う").click().run()
def frag(G, cat, jp, m="illust"): return _common.fragment(next(e for e in G.VOCAB[cat] if e[0] == jp), m)
R = {}
def judge(name, ok, detail=""):
    R[name] = ok; print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

# ---------------- 1. 同点の両取り廃止 ----------------
print("=== 1. 同点（portrait）")
GP = _common.load("portrait")
at = new("portrait")
at = pick_words(at, GP.EXAMPLE)
print("  EXAMPLE →", {c: ss(at, f"sel_{c}") for c in GP.VOCAB if ss(at, f"sel_{c}")}, "\n  warn=", warns(at), "exc=", excs(at))
judge("1a EXAMPLEで各欄1件", all(len(ss(at, f"sel_{c}")) <= 1 for c in GP.VOCAB if ss(at, f"sel_{c}") != "<absent>"))
at = new("portrait"); at = pick_words(at, "女性")
sel = ss(at, "sel_主役"); w = warns(at)
print("  女性 → 主役=", sel, "warn=", w)
judge("1b 女性→主役1件＋同点は警告に出る", len(sel) == 1 and any("年配の女性" in x for x in w) and "年配の女性" not in sel)
judge("1c 同点警告は既存の overridden 文言に合流", any("選ばれなかった" in x for x in w))

# ---------------- 2. おまかせ×人物なし（畳んだまま） ----------------
print("=== 2. おまかせ×人物なし（brewing）")
GB = _common.load("brewing"); CLOTH = GB.VOCAB["服装"][0][0]; GEST = GB.VOCAB["しぐさ"][0][0]
at = new("brewing")
at.session_state["panel_more"] = True; at = at.run()
at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
at.multiselect(key="sel_しぐさ").set_value([GEST]); at = at.run()
at.session_state["panel_more"] = False; at = at.run()
hit = None
for i in range(120):
    at = btn(at, "🎲 おまかせ").click().run()
    if at.session_state["keep_主役"][0] in GB.NO_HUMAN:
        hit = i; break
    at.session_state["keep_服装"] = [CLOTH]; at.session_state["keep_しぐさ"] = [GEST]
print(f"  try#{hit} 主役={ss(at,'keep_主役')} keep_服装={ss(at,'keep_服装')} keep_しぐさ={ss(at,'keep_しぐさ')} 見出し={at.button(key='btn_panel_more').label!r}")
p = prompt(at)
judge("2a 人物なし主役で服装/しぐさの控えが空", hit is not None and ss(at, "keep_服装") == [] and ss(at, "keep_しぐさ") == [])
judge("2b プロンプトに服装/しぐさ断片が無い", frag(GB, "服装", CLOTH) not in p and frag(GB, "しぐさ", GEST) not in p)
at = at.run(); judge("2c 再描画後も空のまま", ss(at, "keep_服装") == [] and frag(GB, "服装", CLOTH) not in prompt(at))

# ---------------- 3. 語彙から消えたラベル（_gone） ----------------
print("=== 3. _gone（brewing: 畳んだ服装と表示中の場所を改名）")
PLACE = GB.VOCAB["場所"][0][0]; CF = frag(GB, "服装", CLOTH); PF = frag(GB, "場所", PLACE)  # reloadでVOCABが差し替わる前に断片を固定
gfile = S / "app" / "genres" / "brewing.py"; orig = gfile.read_text(encoding="utf-8")
try:
    at = new("brewing")
    at.session_state["panel_more"] = True; at = at.run()
    at.multiselect(key="sel_場所").set_value([PLACE]); at = at.run()
    at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
    at.session_state["panel_more"] = False; at = at.run()
    p0 = prompt(at); print("  改名前 prompt has 服装/場所:", CF in p0, PF in p0)
    gfile.write_text(orig.replace(f'("{PLACE}",', f'("{PLACE}改",', 1).replace(f'("{CLOTH}",', f'("{CLOTH}改",', 1), encoding="utf-8")
    at = at.run()
    print("  改名後 1回目: exc=", excs(at), "\n    warn=", warns(at), "\n    keep_服装=", ss(at,"keep_服装"), "keep_場所=", ss(at,"keep_場所"), "sel_場所=", ss(at,"sel_場所"),
          "\n    見出し=", at.button(key="btn_panel_more").label if at.button(key="btn_panel_more") else None, "\n    prompt=", prompt(at)[:120], "_gone=", ss(at, "_gone"))
    w1 = warns(at)
    at = at.run()
    print("  改名後 2回目(次の操作相当): warn=", warns(at), "keep_服装=", ss(at,"keep_服装"), "prompt=", prompt(at)[:80], "_gone=", ss(at,"_gone"))
    w2 = warns(at)
    at = at.run(); print("  改名後 3回目: warn=", warns(at), "_gone=", ss(at,"_gone"))
    judge("3a 改名直後の描画で『語彙に無くなった』警告が出る", any("語彙に無くなった" in x and CLOTH in x for x in w1), f"(1回目warn={w1})")
    judge("3b 次の操作で警告が出る", any("語彙に無くなった" in x and CLOTH in x for x in w2), f"(2回目warn={w2})")
    judge("3c 表示中の欄(場所)の消えたラベルも警告に出る", any(PLACE in x and "語彙に無くなった" in x for x in w1 + w2), "(pickが控えを先に掃除すると黙って消える)")
    judge("3d 例外なし", not excs(at))
finally:
    gfile.write_text(orig, encoding="utf-8")

# ---------------- 4. BASE ----------------
print("=== 4. BASE（合成ジャンル qabase）")
GQ = _common.load("qabase"); SUBJ = next(e[0] for e in GQ.VOCAB["主役"] if e[0] not in GQ.NO_HUMAN)
at = new("qabase")
judge("4a 選択なし・キャラなし・自由欄なし → 空（画質だけは出さない）", len(at.code) == 1 and any("上から選ぶか" in i.value for i in at.info), f"code数={len(at.code)} info={[i.value for i in at.info]}")
at.text_input(key="chara").input("さくら"); at = at.run(); p = prompt(at)
print("  キャラのみ:", p)
judge("4b キャラ名だけで BASE が先頭に入る", p.startswith(BASE["illust"]) and _common.character("さくら")["text"] in p)
at = new("qabase"); at.text_input(key="free").input("red umbrella"); at = at.run(); p = prompt(at)
print("  自由欄のみ:", p)
judge("4c 自由欄だけで BASE が先頭に入る", p.startswith(BASE["illust"]) and "red umbrella" in p)
for m, radio in (("photo", "写実（juggernautXL）"), ("illust", "イラスト（animagine）")):
    at = new("qabase"); at.radio(key="model_radio").set_value(radio); at = at.run()
    at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run(); p = prompt(at)
    toks = [t.strip().lower() for t in p.split(",")]
    dup = {t for t in toks if toks.count(t) > 1}
    basetoks = [t.strip().lower() for t in BASE[m].split(",")]
    qtoks = [t.strip().lower() for t in QUALITY[m].split(",")]
    print(f"  {m}: {p}")
    judge(f"4d {m}: BASE先頭・共通語({set(basetoks)&set(qtoks)})が1回だけ・画質の残りは入る",
          p.startswith(BASE[m]) and not dup and all(t in toks for t in qtoks), f"dup={dup}")
at.checkbox(key="quality_ck").set_value(False); at = at.run(); p = prompt(at)
judge("4e 画質OFFでも BASE は入り画質の残りは入らない", p.startswith(BASE["illust"]) and "high score" not in p, p)
at = new("qabase"); at.radio(key="model_radio").set_value("動画（LTXV）"); at = at.run()
at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run()
codes = [c.value for c in at.code]; print("  video codes:", [c[:70] for c in codes])
judge("4f 動画: 動画用はvideo BASE、静止画用はillust BASE", codes[0].startswith(BASE["video"]) and codes[1].startswith(BASE["illust"]))

# ---------------- 5. 壊れた保存ファイル ----------------
print("=== 5. 壊れた saved（brewing）")
SAVED = S / "app" / "saved" / "brewing.json"; SAVED.parent.mkdir(exist_ok=True)
for content in ("{ broken", "null", '{"a":1}', ""):
    SAVED.write_text(content, encoding="utf-8")
    at = new("brewing")
    b = btn(at, "保存"); e = errs(at)
    at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run()
    at.text_input(key="save_name").input("qa-x"); at = at.run()
    try:
        at = btn(at, "保存").click().run(); clicked = True
    except Exception as ex:
        clicked = f"click raised {type(ex).__name__}"
    after = SAVED.read_text(encoding="utf-8")
    print(f"  content={content!r}: error={[x[:60] for x in e]} disabled={b.disabled} click={clicked} file_unchanged={after == content} exc={excs(at)}")
    # AppTest の click() は disabled を無視して押せる（ブラウザでは押せない）ので、合否は「赤エラー＋disabledがフロントに届く」で見る
    judge(f"5 {content!r}: 赤エラー＋保存ボタン disabled", bool(e) and b.disabled and not excs(at))
for content in ("[1]", '[{"x":1}]'):
    SAVED.write_text(content, encoding="utf-8"); at = new("brewing")
    print(f"  content={content!r}: error={errs(at)} disabled={btn(at,'保存').disabled} exc={excs(at)}")
    at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run(); at.text_input(key="save_name").input("qa-y"); at = at.run()
    try: at = btn(at, "保存").click().run()
    except Exception as ex: print("   click raised", ex)
    print(f"     保存後 exc={excs(at)} file={SAVED.read_text()[:60]!r}")
SAVED.unlink()

# ---------------- 6. 回帰：選択保持・保存→呼び出し（モデル往復）・同名上書き ----------------
print("=== 6. 回帰（brewing）")
at = new("brewing"); at.session_state["panel_more"] = True; at = at.run()
at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
at.session_state["panel_more"] = False; at = at.run(); at = at.run()
judge("6a 畳んでも服装が残る", ss(at, "keep_服装") == [CLOTH] and frag(GB, "服装", CLOTH) in prompt(at))
at = new("brewing"); at.radio(key="model_radio").set_value("写実（juggernautXL）"); at = at.run()
at.session_state["panel_more"] = True; at = at.run()
at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run()
at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
at.session_state["use_服装"] = False; at = at.run()
at.text_input(key="chara").input("さくら"); at = at.run()
p_saved = prompt(at)
at.text_input(key="save_name").input("qa-1"); at = at.run(); at = btn(at, "保存").click().run()
at.text_input(key="save_name").input("qa-1"); at = at.run(); at = btn(at, "保存").click().run()
n = len(json.loads(SAVED.read_text()))
at2 = new("brewing"); at2.session_state["panel_saved"] = True; at2 = at2.run(); at2 = at2.button(key="ld0").click().run()
print("  保存時=", p_saved, "\n  呼出後=", prompt(at2), "\n  model=", at2.radio(key="model_radio").value, "件数=", n)
judge("6b 呼び出しでプロンプト・モデル一致", p_saved == prompt(at2) and at2.radio(key="model_radio").value == "写実（juggernautXL）")
judge("6c 同名上書きで1件", n == 1)
SAVED.unlink(missing_ok=True)

# ---------------- 7. match() のAPI（空文字） ----------------
print("=== 7. match() 戻り値")
import matcher
for t in ("", "　", " 　 "):
    r = matcher.match(t, GB.VOCAB, GB.ALIASES)
    print(f"  match({t!r}) -> {type(r).__name__} {r}")
r = matcher.match("", GB.VOCAB); judge("7 空文字でも (out, ties) の2要素で返る", isinstance(r, tuple) and len(r) == 2, f"実際={r!r}")

print("\n==== 集計:", sum(R.values()), "/", len(R), "PASS;  FAIL:", [k for k, v in R.items() if not v])
print("temp:", S)
