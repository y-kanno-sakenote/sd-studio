#!/usr/bin/env python3
# 担当: ✅ 検証係（マンガー×ファインマン）
# 静的版(JS)とStreamlit版(Python)で、同じ入力から同じ照合結果・同じプロンプトが出るかを実測する。
# JS は web/build.py の HTML から関数部分をそのまま切り出して node で実行、Python は prompt_studio.py の
# compose/dedupe の関数本文をそのまま exec して使う（再実装しない）。
import json, pathlib, random, re, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
S = pathlib.Path(tempfile.mkdtemp(prefix="sdstudio_pyjs_"))
sys.path.insert(0, str(ROOT / "web")); sys.path.insert(0, str(ROOT / "genres")); sys.path.insert(0, str(ROOT))
import build, _common
from matcher import match, unmatched
DATA = build.collect()
import copy, types
BASE = {"illust": "masterpiece, sake brewery art, absurdres", "photo": "photorealistic, sake brewery photo, 8k uhd", "video": "cinematic, sake brewery footage"}
_qb = copy.deepcopy(next(gd for gd in DATA["genres"] if gd["id"] == "brewing")); _qb["id"] = "qabase"; _qb["base"] = BASE
DATA["genres"].append(_qb)

# --- JS 切り出し ---
html = build.HTML
js = html[html.index("<script>") + len("<script>"): html.index("function block(")]
js = js.replace("const DATA = __DATA__;", "const DATA = JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));")
js = js.replace('const $=id=>document.getElementById(id);', 'var QUALITY_ON=true; var $=id=>({checked:QUALITY_ON});')
assert "QUALITY_ON" in js and "JSON.parse" in js
js += r"""
const cases = JSON.parse(require('fs').readFileSync(process.argv[3],'utf8'));
const res = [];
for (const c of cases) {
  G = DATA.genres.find(g => g.id === c.genre);
  if (c.kind === "match") {
    const found = matchWords(c.text, G.vocab, G.aliases);
    const ties = found.__ties || {}; delete found.__ties;
    const chosen = Object.values(found).flat();
    res.push({found, ties, un: unmatched(c.text, G.vocab, G.aliases, chosen)});
  } else {
    MODEL = c.model; SEL = c.sel; QUALITY_ON = c.quality;
    res.push({p: compose(c.model, c.cats)});
  }
}
process.stdout.write(JSON.stringify(res));
"""
(S / "harness.js").write_text(js, encoding="utf-8")
(S / "data.json").write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")

# --- Python compose/dedupe を prompt_studio.py の本文から exec ---
src = (ROOT / "prompt_studio.py").read_text(encoding="utf-8")
m = re.search(r"\ndef dedupe\(.*?\n(?=\ndef show\()", src, re.S)
assert m, "compose/dedupe を切り出せない"
PYCODE = m.group(0)

def py_compose(g, model, sel, cats, quality):
    class SS(dict):
        pass
    ss = {f"keep_{c}": v for c, v in sel.items()}
    class St:  # st.session_state だけ使う
        session_state = ss
    ns = {"st": St, "VOCAB": g.VOCAB, "g": g, "CH": None, "free": "", "add_quality": quality,
          "QUALITY": _common.QUALITY, "fragment": _common.fragment}
    exec(PYCODE, ns)
    return ns["compose"](model, cats)

random.seed(20260913)
cases = []
genres = {gd["id"]: _common.load(gd["id"]) for gd in DATA["genres"] if gd["id"] != "qabase"}
_b = _common.load("brewing"); genres["qabase"] = types.SimpleNamespace(**{k: v for k, v in vars(_b).items() if not k.startswith("__")}); genres["qabase"].BASE = BASE
texts_by_genre = {}
for gid, g in genres.items():
    labels = [e[0] for v in g.VOCAB.values() for e in v]
    aliases = [a for v in g.ALIASES.values() for a in v]
    texts = [g.EXAMPLE, "女性", "男性", "若い女性が酒を飲む", "夜の雪、湯気、蔵人"] + labels + aliases
    for _ in range(150):
        k = random.randint(2, 4)
        texts.append("".join(random.choice(("", "の", "で", "と", "、")) + random.choice(labels + aliases) for _ in range(k)))
    texts_by_genre[gid] = texts
    for t in texts:
        cases.append({"kind": "match", "genre": gid, "text": t})
    cats_all = list(g.VOCAB)
    for _ in range(120):
        model = random.choice(["illust", "photo", "video"])
        cats = [c for c in cats_all if model == "video" or c not in _common.VIDEO_ONLY]
        sel = {}
        for c in cats:
            if random.random() < 0.5:
                sel[c] = random.sample([e[0] for e in g.VOCAB[c]], k=random.randint(1, min(2, len(g.VOCAB[c]))))
        cases.append({"kind": "compose", "genre": gid, "model": model, "sel": sel, "cats": cats,
                      "quality": random.random() < 0.7})
(S / "cases.json").write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")
out = subprocess.run(["node", str(S / "harness.js"), str(S / "data.json"), str(S / "cases.json")],
                     capture_output=True, text=True)
if out.returncode:
    print("node failed:", out.stderr[:800]); sys.exit(1)
res = json.loads(out.stdout)
n_match = n_comp = bad_match = bad_comp = n_ties = n_base = 0
multi = {}
for c, r in zip(cases, res):
    g = genres[c["genre"]]
    if c["kind"] == "match":
        n_match += 1
        found, ties = match(c["text"], g.VOCAB, g.ALIASES)
        chosen = [x for v in found.values() for x in v]
        un = list(unmatched(c["text"], g.VOCAB, g.ALIASES, chosen))
        n_ties += bool(ties)
        if found != r["found"] or un != r["un"] or ties != r["ties"]:
            bad_match += 1
            if bad_match <= 5:
                print("MATCH DIFF", c["genre"], repr(c["text"][:40]), "py=", found, ties, "js=", r["found"], r["ties"], "| un py=", un, "js=", r["un"])
        for cat, v in found.items():
            if len(v) > 1 and c["text"] in ("女性", "男性", g.EXAMPLE, "若い女性が酒を飲む"):
                multi[(c["genre"], c["text"][:30], cat)] = v
    else:
        n_comp += 1
        p = py_compose(g, c["model"], c["sel"], c["cats"], c["quality"])
        if c["genre"] == "qabase" and p: n_base += 1
        if p != r["p"]:
            bad_comp += 1
            if bad_comp <= 5:
                print("COMPOSE DIFF", c["genre"], c["model"], "\n py=", p, "\n js=", r["p"])
print(f"match cases={n_match} diff={bad_match} (ties有り={n_ties}) | compose cases={n_comp} diff={bad_comp} (BASE付き非空={n_base})")
print("同一カテゴリ複数採用（短文/例文）:", multi)
