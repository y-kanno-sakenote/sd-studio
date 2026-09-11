# -*- coding: utf-8 -*-
"""自由記述の日本語から、語彙カタログの項目を拾う。

辞書照合だけで動く（外部モデルを使わない＝即座・確実・説明可能）。
ラベルの部分文字列が入力に現れるかを見て、長く一致したものを優先する。
"""
import unicodedata


def _norm(s):
    return unicodedata.normalize("NFKC", s).lower()


# 単独では意味を絞れない漢字。1文字キーとして使うと誤爆する（「車の中」が「霧の中」に当たる等）
STOP_KANJI = set("中上下前後内外間手目口人物事時日方所元本体分気力生大小")


def _is_kanji(ch):
    return "\u4e00" <= ch <= "\u9fff"


def _is_kana(ch):
    return "\u30a0" <= ch <= "\u30ff" or "\uff66" <= ch <= "\uff9f"


def _is_latin(ch):
    return ch.isascii() and ch.isalnum()


def _runs(text):
    """漢字・カタカナ・英数の連続した塊だけを取り出す。ひらがなは接続部分なので捨てる。

    ひらがなを含めると「ている」「の中」「込む」のような機能語で誤って一致する。
    """
    out, cur, kind = [], "", None
    for ch in text:
        k = "kanji" if _is_kanji(ch) else "kana" if _is_kana(ch) else "latin" if _is_latin(ch) else None
        if k and k == kind:
            cur += ch
        else:
            if len(cur) >= 1:
                out.append(cur)
            cur, kind = (ch, k) if k else ("", None)
    if cur:
        out.append(cur)
    return out


def _parts(label):
    base = label
    for ch in "（）()":
        base = base.replace(ch, "・")
    return [p.strip() for p in base.split("・") if p.strip()]


def _keys(label):
    """ラベルから照合キーを作る。漢字・カタカナの塊と、その2文字以上の部分。

    1文字の漢字は誤爆しやすい（「差し込む」が「回り込む」に当たる等）。
    語の先頭にあるか、その区切りのほぼ全体を占めるときだけ採る。
    """
    keys = {_norm(label)}
    for part in _parts(label):
        head = part[0] if part else ""
        for run in _runs(part):
            n = _norm(run)
            if len(n) == 1:
                if _is_kanji(n) and n not in STOP_KANJI and (n == _norm(head) or len(part) == 1):
                    keys.add(n)
                continue
            # カタカナは2文字だと汎用すぎる（「カウンター」が「ポスター」に当たる）
            lo = 3 if _is_kana(n[0]) else 2
            for i in range(len(n)):
                for j in range(i + lo, len(n) + 1):
                    keys.add(n[i:j])
            keys.add(n)
    return keys


def match(text, vocab, aliases=None, per_category=2, min_len=1):
    """{カテゴリ: [選ばれた日本語ラベル]} を返す。拾えなければそのカテゴリは空。

    aliases は {正式ラベル: (言い換え, ...)}。言い換えは照合にだけ使い、
    出来上がるプロンプトには一切出ない（＝出力を変えずに拾える率だけ上げられる）。
    同じカテゴリで同点の候補が並んだら per_category 件まで採る。
    """
    t = _norm(text)
    if not t.strip():
        return {}
    aliases = aliases or {}
    out = {}
    for cat, entries in vocab.items():
        scored = []
        for entry in entries:
            label = entry[0]
            keys = set(_keys(label))
            for alt in aliases.get(label, ()):
                keys |= _keys(alt)
            best = 0
            for k in keys:
                if len(k) >= min_len and k in t:
                    best = max(best, len(k))
            if best:
                # 一致した長さが第一。同点ならラベル全体に占める割合が高い方（=より的確）
                scored.append((best, best / max(len(_norm(label)), 1), label))
        if scored:
            scored.sort(reverse=True)
            top = scored[0][0]
            # 最高点に並んだものだけ複数採る（弱い候補で水増ししない）
            out[cat] = [lab for sc, _, lab in scored[:per_category] if sc == top]
    return out


def _label_keys(labels, aliases):
    keys = set()
    for lab in labels:
        keys |= _keys(lab)
        for alt in aliases.get(lab, ()):
            keys |= _keys(alt)
    return keys


def unmatched(text, vocab, aliases=None, selected=None):
    """入力のうち反映されなかった語を2種類に分けて返す。

      missing    … 語彙のどこにも無い（＝足す候補）
      overridden … 語彙にはあるが、同じカテゴリで別の候補に負けて選ばれなかった

    後者が曲者で、「男性」と書いたのに女性が出る、のような黙った取り違えになる。
    記録も保存もしない（画面に出すだけ）。
    """
    aliases = aliases or {}
    all_labels = [e[0] for entries in vocab.values() for e in entries]
    known = _label_keys(all_labels, aliases)
    used = _label_keys(selected or [], aliases)

    t = _norm(text)
    missing, overridden = [], []
    for run in _runs(t):
        if len(run) < 2:
            continue
        subs = [run[i:j] for i in range(len(run)) for j in range(i + 2, len(run) + 1)]
        if any(x in used for x in subs):
            continue
        if any(x in known for x in subs):
            if run not in overridden:
                overridden.append(run)
        elif run not in missing:
            missing.append(run)
    return missing, overridden
