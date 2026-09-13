#!/usr/bin/env python3
# 担当: ✅ 検証係（マンガー×ファインマン）
# prompt_studio.py を一時ディレクトリに複製（genres/test.py と saved/ は複製しない）し、Streamlit AppTest で
# 「畳んだ要素」「おまかせ×人物なし」「語彙ホットリロード」「保存→呼び出し」「BASE×画質」を実測する。
#   dev/jbsj/.venv/bin/python verification/qa_state_apptest.py
# 注意: panel ボタンは AppTest ではラベルが変わる関係で2回目のクリックが効かないので session_state["panel_more"] を直接切り替える
import os, sys, json, pathlib, shutil, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
S = pathlib.Path(tempfile.mkdtemp(prefix="sdstudio_qa_"))
(S / "app" / "genres").mkdir(parents=True)
for f in ("prompt_studio.py", "matcher.py"):
    shutil.copy(ROOT / f, S / "app" / f)
for f in (ROOT / "genres").glob("*.py"):
    if f.name != "test.py":
        shutil.copy(f, S / "app" / "genres" / f.name)
APP = S / "app" / "prompt_studio.py"
SAVED = S / "app" / "saved" / "brewing.json"
os.environ["SD_STUDIO_GENRE"] = "brewing"
sys.path.insert(0, str(S / "app" / "genres"))
from streamlit.testing.v1 import AppTest
import _common
G = _common.load("brewing"); VOCAB = G.VOCAB
def new(): return AppTest.from_file(str(APP), default_timeout=60).run()
def btn(at, label): return [b for b in at.button if b.label == label][0]
def prompt(at): return at.code[0].value if at.code else ""
def frag(cat, jp, m="illust"): return _common.fragment(next(e for e in VOCAB[cat] if e[0] == jp), m)
def st_(at, k): return at.session_state[k] if k in at.session_state else "<absent>"
def dump(at, tag): print(f" {tag}: panel_more={st_(at,'panel_more')} sel_服装={st_(at,'sel_服装')} keep_服装={st_(at,'keep_服装')} 服装in_prompt={frag('服装',CLOTH) in prompt(at)} 主役={st_(at,'keep_主役')}")
CLOTH = VOCAB["服装"][0][0]; PLACE = VOCAB["場所"][0][0]

print("--- T1: 選んで畳む（panel_more を直接 False にして畳む）")
at = new()
at.session_state["panel_more"] = True; at = at.run()
at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run(); dump(at, "開いて選択")
at.session_state["panel_more"] = False; at = at.run(); dump(at, "畳んだ直後")
at = at.run(); dump(at, "もう1回再描画")

print("--- T2: 畳んだまま おまかせ → 人物なし主役")
for i in range(80):
    at = btn(at, "🎲 おまかせ").click().run()
    if at.session_state["keep_主役"][0] in G.NO_HUMAN: break
    at.session_state["keep_服装"] = [CLOTH]   # 人物ありの回では服装が入っている状態を保つ
dump(at, f"try#{i}"); print("   prompt=", prompt(at)); print("   見出し=", at.button(key="btn_panel_more").label)
at = at.run(); dump(at, "再描画後も")

print("--- T7: 畳んだ中(服装)と描画中(場所)のラベルを語彙側で改名")
gfile = S / "app" / "genres" / "brewing.py"; orig = gfile.read_text(encoding="utf-8")
try:
    at = new()
    at.session_state["panel_more"] = True; at = at.run()
    at.multiselect(key="sel_場所").set_value([PLACE]); at = at.run()
    at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
    at.session_state["panel_more"] = False; at = at.run(); dump(at, "改名前")
    print("   keep_場所=", st_(at,"keep_場所"), "prompt=", prompt(at))
    gfile.write_text(orig.replace(f'("{PLACE}",', f'("{PLACE}改",', 1).replace(f'("{CLOTH}",', f'("{CLOTH}改",', 1), encoding="utf-8")
    at = at.run()
    print(" 改名後 exception=", [str(e.value)[:200] for e in at.exception])
    print("   keep_場所=", st_(at,"keep_場所"), "sel_場所=", st_(at,"sel_場所"), "keep_服装=", st_(at,"keep_服装"), "sel_服装=", st_(at,"sel_服装"))
    print("   見出し=", at.button(key="btn_panel_more").label); print("   prompt=", prompt(at))
    print("   warnings/info=", [w.value for w in at.warning] + [i.value for i in at.info])
finally:
    gfile.write_text(orig, encoding="utf-8")

print("--- T5/T6: 保存→呼び出し（オフ要素の混入・モデル未復元）と壊れたJSON")
at = new()
at.session_state["panel_more"] = True; at = at.run()
SUBJ = next(e[0] for e in VOCAB["主役"] if e[0] not in G.NO_HUMAN)
at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run()
at.multiselect(key="sel_服装").set_value([CLOTH]); at = at.run()
at.session_state["use_服装"] = False; at = at.run()
p_saved = prompt(at)
at.text_input(key="save_name").input("qa-1"); at = at.run(); at = btn(at, "保存").click().run()
at2 = new(); at2.session_state["panel_saved"] = True; at2 = at2.run(); at2 = at2.button(key="ld0").click().run()
print(" 保存時prompt =", p_saved); print(" 呼び出しprompt=", prompt(at2)); print(" 一致=", p_saved == prompt(at2))
SAVED.write_text("{ broken", encoding="utf-8")
at = new(); print(" 壊れたJSONでの警告=", [w.value for w in at.warning] + [e.value for e in at.error])
at.multiselect(key="sel_主役").set_value([SUBJ]); at = at.run()
at.text_input(key="save_name").input("qa-2"); at = at.run(); at = btn(at, "保存").click().run()
print(" 保存後のファイル件数=", len(json.loads(SAVED.read_text())), "（壊れる前の分は戻らない）")
print("temp:", S)
