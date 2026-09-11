# -*- coding: utf-8 -*-
"""表（スプレッドシートからコピーしたCSV/TSV）を工房の語彙に取り込む。

  python3 web/import_table.py 表.tsv --name mygenre --title "私の工房" --port 8521

想定する形（カテゴリ名の行 → 見出し行 → 中身、の繰り返し）:

    特徴
    No.	English Keyword	日本語訳
    1	freckles	そばかす
    2	heterochromia	オッドアイ

    ポーズ・体勢
    No.	English Keyword	日本語訳
    1	arms crossed	腕を組む

空の行・番号だけの行は飛ばす。英語か日本語が空の行も飛ばす。
日本語訳が語彙のラベルになり、English Keyword がイラスト用タグになる。
**写実用の語（3列目）は埋まらない**ので、必要なら生成後に手で足す。
"""
import argparse, csv, io, pathlib, re, sys

HEADER_RE = re.compile(r"^\s*no\.?\s*$", re.I)


def clean(s):
    return (s or "").replace("　", " ").strip().strip('"').strip()


def parse(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8-sig")
    delim = "\t" if raw.count("\t") >= raw.count(",") else ","
    rows = list(csv.reader(io.StringIO(raw), delimiter=delim))

    vocab, current, skipped = {}, None, 0
    for row in rows:
        cells = [clean(c) for c in row]
        if not any(cells):
            continue
        filled = [c for c in cells if c]
        # 見出し行（No. / English Keyword / 日本語訳）
        if HEADER_RE.match(cells[0] if cells else ""):
            continue
        # 単独のセル＝カテゴリ名。ただし数字だけの行は「中身が空の番号行」なので除く
        if len(filled) == 1 and (len(cells) < 2 or not cells[1]):
            name = filled[0].replace("\n", "").strip()
            if name.isdigit():
                skipped += 1
                continue
            current = name
            vocab.setdefault(current, [])
            continue
        if current is None:
            continue
        en = cells[1] if len(cells) > 1 else ""
        ja = cells[2] if len(cells) > 2 else ""
        if not en or not ja:
            skipped += 1
            continue
        if any(e[0] == ja for e in vocab[current]):   # 同じラベルは1回だけ
            continue
        vocab[current].append((ja, en, None))
    vocab = {k: v for k, v in vocab.items() if v}
    return vocab, skipped


TPL = '''# -*- coding: utf-8 -*-
"""{title}。表から取り込んで作った語彙。

取り込み元: {src}
写実用の語（3つ組の3番目）は表に無いため None。必要なら手で足す。
"""

TITLE = {title!r}
ICON = {icon!r}
PORT = {port}
PUBLISH = {publish}

VOCAB = {{
{body}}}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--name", required=True, help="ファイル名になる英字の識別子")
    ap.add_argument("--title", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--icon", default="🎨")
    ap.add_argument("--publish", action="store_true", help="公開版にも載せる")
    a = ap.parse_args()

    vocab, skipped = parse(a.table)
    if not vocab:
        sys.exit("カテゴリも語彙も読み取れなかった。カテゴリ名の行と No. の見出し行があるか確認する")

    body = ""
    for cat, entries in vocab.items():
        body += f'    {cat!r}: [\n'
        for ja, en, _ in entries:
            body += f'        ({ja!r}, {en!r}, None),\n'
        body += "    ],\n"

    out = pathlib.Path(__file__).resolve().parent.parent / "genres" / f"{a.name}.py"
    out.write_text(TPL.format(title=a.title, icon=a.icon, port=a.port,
                              publish=a.publish, src=pathlib.Path(a.table).name,
                              body=body), encoding="utf-8")
    n = sum(len(v) for v in vocab.values())
    print(f"{out}")
    print(f"  {len(vocab)}カテゴリ / {n}語" + (f"（空欄などで飛ばした行 {skipped}）" if skipped else ""))
    for cat, entries in vocab.items():
        print(f"    {cat}: {len(entries)}")


if __name__ == "__main__":
    main()
