# -*- coding: utf-8 -*-
"""genres/*.py から静的版（docs/index.html）を組み立てる。

語彙の正本は Python 側のまま。ここはそれを JSON にして HTML に埋め込むだけ。
  python3 web/build.py
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "genres"))
import _common  # noqa: E402

OUT = ROOT / "docs" / "index.html"


def collect():
    data = []
    for f in sorted((ROOT / "genres").glob("*.py")):
        if f.stem.startswith("_"):
            continue
        g = _common.load(f.stem)
        data.append({
            "id": f.stem, "title": g.TITLE, "icon": g.ICON, "port": g.PORT,
            "example": getattr(g, "EXAMPLE", ""),
            "vocab": {c: [[e[0], e[1], e[2]] for e in v] for c, v in g.VOCAB.items()},
            "always": {k: list(v) for k, v in g.ALWAYS.items()},
            "roll": g.ROLL_CHANCE,
            "videoOnly": list(_common.VIDEO_ONLY),
            "noHuman": list(g.NO_HUMAN),
            "humanOnlyCats": list(g.HUMAN_ONLY_CATS),
            "noHumanMotion": list(g.NO_HUMAN_MOTION),
            "aliases": {k: list(v) for k, v in getattr(g, "ALIASES", {}).items()},
        })
    return {"genres": data, "quality": _common.QUALITY, "negative": _common.NEGATIVE}


HTML = """<!doctype html><html lang="ja"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>プロンプト工房</title>
<style>
:root{--bg:#14110f;--card:#1c1815;--line:#332c26;--ink:#f2ece4;--dim:#9c9187;--accent:#c8a678}
*{box-sizing:border-box}
body{margin:0;padding:24px 16px 64px;background:var(--bg);color:var(--ink);
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;line-height:1.7}
.wrap{max-width:860px;margin:0 auto}
h1{font-size:19px;margin:0 0 2px;letter-spacing:.04em}
.sub{color:var(--dim);font-size:13px;margin:0 0 20px}
.row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.chip{padding:7px 13px;border:1px solid var(--line);border-radius:999px;background:var(--card);
 color:var(--ink);font-size:13px;cursor:pointer;font-family:inherit}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#1b1408;font-weight:600}
.chip.small{padding:5px 11px;font-size:12px}
input[type=text]{flex:1;min-width:200px;padding:11px 13px;border:1px solid var(--line);border-radius:9px;
 background:var(--card);color:var(--ink);font-size:15px;font-family:inherit}
button.go{padding:11px 16px;border:1px solid var(--accent);border-radius:9px;background:transparent;
 color:var(--accent);font-size:14px;cursor:pointer;font-family:inherit}
.note{font-size:12.5px;color:var(--dim);margin:-4px 0 14px}
.warn{font-size:13px;background:#3a2f14;border:1px solid #6b5620;color:#f0e2bd;
 padding:9px 12px;border-radius:8px;margin:-4px 0 14px}
details{border:1px solid var(--line);border-radius:10px;background:var(--card);padding:10px 14px;margin-bottom:16px}
summary{cursor:pointer;font-size:13.5px;color:var(--dim)}
.cat{margin:14px 0 4px;font-size:12px;color:var(--dim);letter-spacing:.05em}
hr{border:0;border-top:1px solid var(--line);margin:22px 0}
h2{font-size:14px;margin:0 0 2px;letter-spacing:.04em}
.outwrap{position:relative;margin-bottom:18px}
pre{white-space:pre-wrap;word-break:break-word;background:var(--card);border:1px solid var(--line);
 border-radius:9px;padding:14px 14px;font-size:13px;margin:6px 0 0;font-family:ui-monospace,monospace}
.copy{position:absolute;top:30px;right:8px;padding:4px 10px;font-size:11.5px;border:1px solid var(--line);
 border-radius:6px;background:var(--bg);color:var(--dim);cursor:pointer;font-family:inherit}
.empty{color:var(--dim);font-size:13px;padding:12px 0}
label.ck{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--dim);margin-bottom:14px}
footer{margin-top:34px;font-size:12px;color:#6d645d}
</style>
<div class="wrap">
<h1>🍶 プロンプト工房</h1>
<p class="sub">日本語で選ぶと英語のプロンプトができる。画像生成AIの入力欄に貼って使う。</p>

<div class="row" id="genres"></div>
<div class="row" id="models"></div>

<div class="row">
  <input type="text" id="sentence" placeholder="">
  <button class="go" id="pick">言葉を拾う</button>
</div>
<div id="msg"></div>

<div class="row">
  <button class="chip" id="roll">🎲 おまかせ</button>
  <button class="chip" id="clear">消す</button>
</div>

<div id="main"></div>
<details id="more"><summary>もっと選ぶ</summary><div id="rest"></div></details>

<label class="ck"><input type="checkbox" id="quality" checked> 画質の指定を足す</label>
<hr>
<div id="out"></div>
<details id="local"><summary>手元で使う（このMacでのみ通じる）</summary>
  <div class="row" id="localLinks"></div>
  <div class="note">ComfyUI と Streamlit 版は公開していない。上のリンクはこのMacで起動しているときだけ開く。<br>
  起動は <code>bin/studios.sh</code>（工房5つ）/ <code>bin/start.sh</code>（ComfyUI）。</div>
</details>
<footer>文章も選択も、この端末の外には出ない（すべてブラウザ内で処理）。<br>
語彙 __COUNT__ 語 / __GENRES__ ジャンル</footer>
</div>
<script>
const DATA = __DATA__;
const STOP_KANJI = new Set("中上下前後内外間手目口人物事時日方所元本体分気力生大小");
const norm = s => s.normalize("NFKC").toLowerCase();
const isKanji = c => c >= "\\u4e00" && c <= "\\u9fff";
const isKana = c => (c >= "\\u30a0" && c <= "\\u30ff") || (c >= "\\uff66" && c <= "\\uff9f");
const isLatin = c => /[a-z0-9]/i.test(c);
function runs(t){
  const out=[]; let cur="", kind=null;
  for(const ch of t){
    const k = isKanji(ch)?"k":isKana(ch)?"n":isLatin(ch)?"l":null;
    if(k && k===kind){cur+=ch;} else {if(cur)out.push(cur); cur = k?ch:""; kind=k;}
  }
  if(cur)out.push(cur);
  return out;
}
function parts(label){
  let b=label; for(const c of "（）()") b=b.split(c).join("・");
  return b.split("・").map(s=>s.trim()).filter(Boolean);
}
function keysOf(label){
  const ks=new Set([norm(label)]);
  for(const part of parts(label)){
    const head = norm(part[0]||"");
    for(const run of runs(part)){
      const n=norm(run);
      if(n.length===1){ if(isKanji(n)&&!STOP_KANJI.has(n)&&(n===head||part.length===1)) ks.add(n); continue; }
      const lo = isKana(n[0]) ? 3 : 2;
      for(let i=0;i<n.length;i++) for(let j=i+lo;j<=n.length;j++) ks.add(n.slice(i,j));
      ks.add(n);
    }
  }
  return ks;
}
const keyCache=new Map();
function K(label){ if(!keyCache.has(label)) keyCache.set(label, keysOf(label)); return keyCache.get(label); }
function allKeys(label, aliases){
  const s=new Set(K(label));
  for(const alt of (aliases[label]||[])) for(const k of K(alt)) s.add(k);
  return s;
}
function matchWords(text, vocab, aliases, perCat=2){
  const t=norm(text); const out={};
  if(!t.trim()) return out;
  for(const [cat, entries] of Object.entries(vocab)){
    const scored=[];
    for(const e of entries){
      let best=0;
      for(const k of allKeys(e[0], aliases)) if(k.length>=1 && t.includes(k)) best=Math.max(best,k.length);
      if(best) scored.push([best, best/Math.max(norm(e[0]).length,1), e[0]]);
    }
    if(scored.length){
      scored.sort((a,b)=> b[0]-a[0] || b[1]-a[1]);
      const top=scored[0][0];
      out[cat]=scored.slice(0,perCat).filter(x=>x[0]===top).map(x=>x[2]);
    }
  }
  return out;
}
function unmatched(text, vocab, aliases, selected){
  const known=new Set(), used=new Set();
  for(const entries of Object.values(vocab)) for(const e of entries)
    for(const k of allKeys(e[0],aliases)) known.add(k);
  for(const lab of selected) for(const k of allKeys(lab,aliases)) used.add(k);
  const missing=[], over=[];
  for(const run of runs(norm(text))){
    if(run.length<2) continue;
    const subs=[]; for(let i=0;i<run.length;i++) for(let j=i+2;j<=run.length;j++) subs.push(run.slice(i,j));
    if(subs.some(x=>used.has(x))) continue;
    if(subs.some(x=>known.has(x))){ if(!over.includes(run)) over.push(run); }
    else if(!missing.includes(run)) missing.push(run);
  }
  return [missing, over];
}
function dedupe(ps, tokenLevel){
  const seen=new Set(), out=[];
  for(const p of ps) for(const piece of (tokenLevel? p.split(",") : [p])){
    const s=piece.trim(), k=s.toLowerCase();
    if(s && !seen.has(k)){ seen.add(k); out.push(s); }
  }
  return out;
}
const frag=(e,m)=> (m==="photo"||m==="video") ? (e[2]||e[1]) : e[1];

let G=DATA.genres[0], MODEL="illust", SEL={}, MSG=null;
const $=id=>document.getElementById(id);

function catsFor(){ return Object.keys(G.vocab).filter(c=> MODEL==="video" || !G.videoOnly.includes(c)); }
function chip(label,on,fn,small){
  const b=document.createElement("button");
  b.className="chip"+(small?" small":""); b.textContent=label;
  b.setAttribute("aria-pressed", on?"true":"false"); b.onclick=fn; return b;
}
function renderTop(){
  const gs=$("genres"); gs.innerHTML="";
  for(const g of DATA.genres) gs.appendChild(chip(g.icon+" "+g.title, g.id===G.id, ()=>{G=g;SEL={};MSG=null;render();}));
  const ms=$("models"); ms.innerHTML="";
  for(const [k,v] of [["イラスト","illust"],["写実","photo"],["動画","video"]])
    ms.appendChild(chip(k, MODEL===v, ()=>{MODEL=v;render();}, true));
  $("sentence").placeholder = G.example || "作りたい絵を文章で書く";
}
function renderCats(){
  const main=$("main"), rest=$("rest"); main.innerHTML=""; rest.innerHTML="";
  const always=(G.always[MODEL]||[]).filter(c=>catsFor().includes(c));
  const chosen=[];
  for(const cat of catsFor()){
    const box=document.createElement("div");
    const h=document.createElement("div"); h.className="cat"; h.textContent=cat; box.appendChild(h);
    const row=document.createElement("div"); row.className="row";
    for(const e of G.vocab[cat]){
      const on=(SEL[cat]||[]).includes(e[0]);
      if(on) chosen.push(e[0]);
      row.appendChild(chip(e[0], on, ()=>{
        SEL[cat]=SEL[cat]||[];
        SEL[cat]= on ? SEL[cat].filter(x=>x!==e[0]) : SEL[cat].concat([e[0]]);
        render();
      }, true));
    }
    box.appendChild(row);
    (always.includes(cat)? main : rest).appendChild(box);
  }
  const picked=catsFor().flatMap(c=>(SEL[c]||[])).filter(x=>!main.textContent.includes(x));
  $("more").querySelector("summary").textContent =
    "もっと選ぶ" + (picked.length? "　"+picked.join("、") : "");
}
function compose(m, cats){
  const ps=[];
  for(const c of cats) for(const jp of (SEL[c]||[])){
    const e=G.vocab[c].find(x=>x[0]===jp); if(e) ps.push(frag(e,m));
  }
  if(!ps.length) return "";
  if($("quality").checked) ps.push(DATA.quality[m]);
  return dedupe(ps.filter(Boolean), m==="illust").join(", ");
}
function block(title,body,note){
  const w=document.createElement("div"); w.className="outwrap";
  const h=document.createElement("h2"); h.textContent=title; w.appendChild(h);
  if(note){const n=document.createElement("div");n.className="note";n.textContent=note;w.appendChild(n);}
  if(body){
    const pre=document.createElement("pre"); pre.textContent=body; w.appendChild(pre);
    const b=document.createElement("button"); b.className="copy"; b.textContent="コピー";
    b.onclick=()=>{navigator.clipboard.writeText(body); b.textContent="コピーした"; setTimeout(()=>b.textContent="コピー",1200);};
    w.appendChild(b);
  } else {
    const e=document.createElement("div"); e.className="empty"; e.textContent="上から選ぶか「おまかせ」を押す"; w.appendChild(e);
  }
  return w;
}
function renderOut(){
  const out=$("out"); out.innerHTML="";
  const cats=catsFor();
  if(MODEL==="video"){
    out.appendChild(block("動画用", compose("video",cats), "動画生成の入力欄に貼る"));
    const still=compose("illust", cats.filter(c=>!G.videoOnly.includes(c)));
    if(still) out.appendChild(block("元になる静止画用", still, "先にこれで1枚描き、その絵を動かす"));
    out.appendChild(block("ネガティブ（動画）", DATA.negative.video));
  } else {
    out.appendChild(block("プロンプト", compose(MODEL,cats)));
    out.appendChild(block("ネガティブ", DATA.negative[MODEL]));
  }
}
function renderMsg(){
  const m=$("msg"); m.innerHTML="";
  if(!MSG) return;
  if(MSG.over && MSG.over.length){
    const d=document.createElement("div"); d.className="warn";
    d.textContent = MSG.over.join("、")+" は語彙にあるが選ばれなかった（同じ枠で別の候補が勝った）。下で直せる";
    m.appendChild(d);
  }
  if(MSG.missing && MSG.missing.length){
    const d=document.createElement("div"); d.className="note";
    d.textContent = "語彙に無い言葉：" + MSG.missing.join("、");
    m.appendChild(d);
  }
  if(MSG.none){
    const d=document.createElement("div"); d.className="note";
    d.textContent="拾える言葉が無かった。下から直接選ぶか、別の言い方で書いてみる";
    m.appendChild(d);
  }
}
function render(){ renderTop(); renderCats(); renderMsg(); renderOut(); }

$("pick").onclick=()=>{
  const t=$("sentence").value.trim();
  if(!t){ MSG=null; render(); return; }
  const found=matchWords(t, G.vocab, G.aliases);
  SEL={}; for(const [c,v] of Object.entries(found)) if(catsFor().includes(c)) SEL[c]=v;
  const chosen=Object.values(SEL).flat();
  const [missing, over]=unmatched(t, G.vocab, G.aliases, chosen);
  MSG={missing, over, none: !chosen.length};
  render();
};
$("sentence").addEventListener("keydown", e=>{ if(e.key==="Enter") $("pick").click(); });
$("roll").onclick=()=>{
  const subs=G.vocab["主役"]; const subject=subs[Math.floor(Math.random()*subs.length)][0];
  const noHuman=G.noHuman.includes(subject);
  SEL={"主役":[subject]};
  for(const cat of catsFor()){
    if(cat==="主役") continue;
    if(noHuman && G.humanOnlyCats.includes(cat)) continue;
    let pool=G.vocab[cat];
    if(noHuman && cat==="主役の動き") pool=pool.filter(e=>G.noHumanMotion.includes(e[0]));
    if(!pool.length) continue;
    if(Math.random() < (G.roll[cat]??0.5)) SEL[cat]=[pool[Math.floor(Math.random()*pool.length)][0]];
  }
  MSG=null; render();
};
$("clear").onclick=()=>{ SEL={}; MSG=null; $("sentence").value=""; render(); };
$("quality").onchange=renderOut;

// 手元のStreamlit版とComfyUIへのリンク（localhost。他の端末では開かない）
(function(){
  const box=$("localLinks");
  for(const g of DATA.genres){
    const a=document.createElement("a");
    a.className="chip small"; a.href="http://localhost:"+g.port; a.target="_blank";
    a.textContent=g.icon+" "+g.title; a.style.textDecoration="none";
    box.appendChild(a);
  }
  const c=document.createElement("a");
  c.className="chip small"; c.href="http://127.0.0.1:8188"; c.target="_blank";
  c.textContent="🖼 ComfyUI"; c.style.textDecoration="none";
  box.appendChild(c);
})();

render();
</script>
</html>
"""

if __name__ == "__main__":
    data = collect()
    n = sum(len(v) for g in data["genres"] for v in g["vocab"].values())
    html = (HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False))
                .replace("__COUNT__", str(n))
                .replace("__GENRES__", str(len(data["genres"]))))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT}  {len(html)/1024:.0f}KB / {len(data['genres'])}ジャンル {n}語")
