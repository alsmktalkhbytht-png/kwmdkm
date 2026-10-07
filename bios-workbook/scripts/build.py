#!/usr/bin/env python3
"""BIOS workbook v3 — content (.bw or .json) -> HTML -> PDF (A4, Chromium).

usage: build.py <content.bw|json> <out-base> [--html-only]
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import themes  # noqa: E402

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
AR_LETTERS = {"a": "أ", "b": "ب", "c": "ج", "d": "د", "e": "هـ", "f": "و", "g": "ز", "h": "ح"}
STAGES_AR = {1: "الأولى", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة", 6: "السادسة"}
STAGES_EN = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th"}
TERMS_AR = {1: "الفصل الأول", 2: "الفصل الثاني"}


# ───────────────────────── parsing (.bw text format) ─────────────────────────
def split2(s):
    en, _, ar = s.partition("||")
    return en.strip(), ar.strip()


def parse_bw(text):
    meta, blocks = {}, []
    cur = None          # current block being filled
    pending_en = None   # (kind, payload) waiting for its "> ar" line

    def flush():
        nonlocal cur
        if cur is not None:
            blocks.append(cur)
        cur = None

    for raw in text.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
            continue
        if s.startswith("@"):
            k, _, v = s[1:].partition(":")
            v = v.strip()
            meta[k.strip()] = int(v) if v.isdigit() else v
            continue
        if s.startswith("> "):
            ar = s[2:].strip()
            kind, payload = pending_en
            payload["ar"] = ar
            pending_en = None
            continue
        if s.startswith("=+ "):
            blocks[-1]["en2"], blocks[-1]["ar2"] = split2(s[3:])
            continue
        if s.startswith("= "):
            flush()
            en, ar = split2(s[2:])
            blocks.append({"t": "title", "en": en, "ar": ar})
            continue
        m = re.match(r"^(#{1,3}) (.*)$", s)
        if m:
            flush()
            en, ar = split2(m.group(2))
            blocks.append({"t": {1: "section", 2: "sub", 3: "sub2"}[len(m.group(1))], "en": en, "ar": ar})
            continue
        if s == "pagebreak":
            flush()
            blocks.append({"t": "pagebreak"})
            continue
        if s in ("p", "ol", "ul", "summary", "keypoints", "keyterms"):
            flush()
            cur = {"t": s, "items": []}
            continue
        if s.startswith("fig "):
            flush()
            parts = [x.strip() for x in s[4:].split("|")]
            fig = {"t": "figure", "src": parts[0]}
            if len(parts) >= 3:
                fig["caption"] = [parts[1], parts[2]]
            blocks.append(fig)
            continue
        if s.startswith("lab "):
            labels = []
            for chunk in s[4:].split(" ; "):
                a, _, b = chunk.partition(" = ")
                labels.append([a.strip(), b.strip()])
            blocks[-1]["labels"] = labels
            continue
        # content lines inside a block
        if cur is None:
            raise SystemExit(f"line outside block: {s[:60]}")
        if cur["t"] == "keyterms":
            a, _, b = s.partition(" = ")
            cur["items"].append({"en": a.strip(), "ar": b.strip()})
            continue
        if cur["t"] in ("ol", "ul"):
            if s.startswith("** "):
                item = {"lvl": 2, "en": s[3:].strip(), "more": []}
                cur["items"].append(item)
                pending_en = ("item", item)
            elif s.startswith("* "):
                item = {"lvl": 1, "en": s[2:].strip(), "more": []}
                cur["items"].append(item)
                pending_en = ("item", item)
            elif s.startswith("+ "):
                pair = {"en": s[2:].strip()}
                cur["items"][-1]["more"].append(pair)
                pending_en = ("more", pair)
            else:
                raise SystemExit(f"bad list line: {s[:60]}")
            continue
        pair = {"en": s}
        cur["items"].append(pair)
        pending_en = ("pair", pair)
    flush()
    return {"meta": meta, "blocks": blocks}


# ───────────────────────── inline markup + bidi ─────────────────────────
LAT = r"A-Za-z0-9°˚μµ⁺⁻₀-₉Å"
RUN = re.compile(
    rf"\([^()؀-ۿ]*[A-Za-z0-9][^()؀-ۿ]*\)"            # (English …)
    rf"|[{LAT}~^*=][{LAT}\s\-\+,./%~^*'’:=–]*[{LAT}+\-%~^*=]"           # bare latin / numbers
    rf"|[{LAT}]"
)


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"(\d) (%|nm|A˚|μm|°C|ml)", "\\1\u00a0\\2", s)
    s = re.sub(r"==(.+?)==", r'<b class="term">\1</b>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"~(.+?)~", r"<sub>\1</sub>", s)
    s = re.sub(r"\^(.+?)\^", r"<sup>\1</sup>", s)
    return s


def md(s, ar=False):
    if not ar:
        return inline(s)
    out, last = [], 0
    for m in RUN.finditer(s):
        tok = m.group(0)
        # don't isolate pure markup tokens like "**" or "=="
        if not re.search(rf"[{LAT}]", tok):
            continue
        out.append(inline_open(s[last:m.start()]))
        out.append(("ISO", tok))
        last = m.end()
    out.append(inline_open(s[last:]))
    # rebuild string with placeholders, then run inline markup on whole thing so ** spanning works
    buf, isos = "", []
    for o in out:
        if isinstance(o, tuple):
            isos.append(o[1])
            buf += f"{len(isos) - 1}"
        else:
            buf += o
    buf = inline(buf)
    return re.sub(r"(\d+)", lambda m: f'<bdi class="lt" dir="ltr">{inline(isos[int(m.group(1))])}</bdi>', buf)


def inline_open(s):
    return s


# ───────────────────────── HTML rendering ─────────────────────────
def badge(kind):
    return f'<span class="badge b-{kind}">{"EN" if kind == "en" else "AR"}</span>'


def pair_html(en, ar, cls=""):
    return (f'<div class="pair {cls}"><div class="en" dir="ltr">{badge("en")}<div class="tx">{md(en)}</div></div>'
            f'<div class="ar" dir="rtl">{badge("ar")}<div class="tx">{md(ar, True)}</div></div></div>')


MARK = re.compile(r"^(-\s*)?((?:[0-9]{1,2}|[a-hA-H]|I{1,3}|IV|V))[.)]\s+")


def list_marker(text, ordered):
    m = MARK.match(text) if ordered else None
    if m:
        tok = m.group(2)
        rest = text[m.end():]
        if tok.isdigit():
            ar = tok.translate(AR_DIGITS)
        elif tok.lower() in AR_LETTERS and len(tok) == 1:
            ar = AR_LETTERS[tok.lower()]
        else:
            ar = tok
        return tok, ar, rest
    return None, None, re.sub(r"^-\s*", "", text)


def render_list(b):
    ordered = b["t"] == "ol"
    out = []
    for it in b["items"]:
        tok, artok, rest = list_marker(it["en"], ordered or it["lvl"] == 2)
        lvl = it["lvl"]
        if tok:
            en_mk = f'<span class="num">{tok}</span>'
            ar_mk = f'<span class="num num-ar">{artok}</span>'
        else:
            en_mk = ar_mk = '<span class="dia"></span>'
        ar = re.sub(r"^-\s*", "", it.get("ar", ""))
        out.append(
            f'<div class="li lvl{lvl}"><div class="pair">'
            f'<div class="en" dir="ltr">{en_mk}<div class="tx">{md(rest)}</div></div>'
            f'<div class="ar" dir="rtl">{ar_mk}<div class="tx">{md(ar, True)}</div></div></div></div>')
        for mo in it["more"]:
            out.append(f'<div class="li lvl{lvl} cont">{pair_html(mo["en"], mo["ar"])}</div>')
    return f'<div class="blk card list split" data-k="list">{"".join(out)}</div>'


def render_block(b, ctx):
    t = b["t"]
    if t == "title":
        meta = ctx["meta"]
        unit = meta.get("unit", "lecture")
        n = meta.get("lecture", 1)
        lab_en = ("WEEK" if unit == "week" else "LEC")
        kind_en = "THEORY" if meta.get("type") == "theory" else "PRACTICAL"
        sub = ""
        if b.get("en2"):
            sub = f'<div class="t-en2">{md(b["en2"])}</div><div class="t-ar2" dir="rtl">{md(b["ar2"], True)}</div>'
        return (f'<div class="blk lec-title" data-k="title"><div class="lt-num"><small>{lab_en}</small><b>{n}</b></div>'
                f'<div class="lt-body"><div class="kicker">{kind_en} · {lab_en if unit=="week" else "LECTURE"} {n}</div>'
                f'<div class="t-en">{md(b["en"])}</div><div class="t-ar" dir="rtl">{md(b["ar"], True)}</div>{sub}</div></div>'
                f'<div class="blk key" data-k="key"><span class="k k-en">EN · Lecture text</span>'
                f'<span class="k k-ar" dir="rtl">AR · الترجمة العربية</span>'
                f'<span class="k k-nt" dir="rtl">✍︎ ملاحظات الطالب أسفل كل صفحة</span></div>')
    if t == "section":
        ctx["sec"] += 1
        n = ctx["sec"]
        return (f'<div class="blk sec head" data-k="head"><div class="sec-num">{n}</div><div class="sec-bar">'
                f'<span class="s-en">{md(b["en"])}</span><span class="s-ar" dir="rtl">{md(b["ar"], True)}</span></div></div>')
    if t in ("sub", "sub2"):
        return (f'<div class="blk {t} head" data-k="head"><span class="chk"></span>'
                f'<span class="s-en">{md(b["en"])}</span><span class="s-ar" dir="rtl">{md(b["ar"], True)}</span>'
                f'<span class="dots"></span></div>')
    if t == "p":
        return f'<div class="blk card para split" data-k="p">{"".join(pair_html(i["en"], i["ar"]) for i in b["items"])}</div>'
    if t in ("ol", "ul"):
        return render_list(b)
    if t == "figure":
        ctx["fig"] += 1
        cap = ""
        if b.get("caption"):
            cap = (f'<div class="cap"><span class="c-en">{md(b["caption"][0])}</span>'
                   f'<span class="c-ar" dir="rtl">{md(b["caption"][1], True)}</span></div>')
        labs = ""
        if b.get("labels"):
            chips = "".join(f'<span class="chip"><i dir="ltr">{md(a)}</i><em dir="rtl">{md(c, True)}</em></span>'
                            for a, c in b["labels"])
            labs = f'<div class="labels"><div class="lab-h">LABELS · <span dir="rtl">ترجمة التسميات</span></div>{chips}</div>'
        src = os.path.join(ctx["imgdir"], b["src"])
        return (f'<div class="blk card figure" data-k="fig"><div class="img"><img src="file://{src}"></div>'
                f'{cap}{labs}</div>')
    if t == "summary":
        rows = "".join(
            f'<div class="srow"><span class="sn">{i + 1}</span>{pair_html(x["en"], x["ar"])}</div>'
            for i, x in enumerate(b["items"]))
        return (f'<div class="blk card summary split" data-k="sum" data-head="1"><div class="box-h sum-h">'
                f'<span>∑ LECTURE SUMMARY</span><span dir="rtl">ملخص المحاضرة</span></div>{rows}</div>')
    if t == "keypoints":
        rows = "".join(
            f'<div class="kp"><div class="en" dir="ltr"><span class="star">★</span><div class="tx">{md(x["en"])}</div></div>'
            f'<div class="ar" dir="rtl"><div class="tx">{md(x["ar"], True)}</div></div></div>'
            for x in b["items"])
        return (f'<div class="blk card keypoints split" data-k="kp" data-head="1"><div class="box-h kp-h">'
                f'<span>★ KEY POINTS</span><span dir="rtl">النقاط الأساسية</span></div>{rows}</div>')
    if t == "keyterms":
        chips = "".join(f'<span class="kt"><i dir="ltr">{md(x["en"])}</i><em dir="rtl">{md(x["ar"], True)}</em></span>'
                        for x in b["items"])
        return (f'<div class="blk card keyterms split" data-k="kt" data-head="1"><div class="box-h kt-h">'
                f'<span>Aa KEY TERMS</span><span dir="rtl">المصطلحات الأساسية</span></div>{chips}</div>')
    if t == "pagebreak":
        return '<div class="blk pagebreak" data-k="br"></div>'
    raise SystemExit(f"unknown block {t}")


def cover_html(meta, theme_key, art_svg, logo_svg):
    unit = meta.get("unit", "lecture")
    n = meta.get("lecture", 1)
    st = int(meta.get("stage", 0) or 0)
    term = int(meta.get("term", 0) or 0)
    theory = meta.get("type") == "theory"
    title = meta["_title"]

    def val(x):
        return x if x else '<span class="blank"></span>'

    unit_en = "Week" if unit == "week" else "Lecture"
    unit_ar = "الأسبوع" if unit == "week" else "المحاضرة"
    sub = ""
    if title.get("en2"):
        sub = (f'<div class="c-en2">{md(title["en2"])}</div>'
               f'<div class="c-ar2" dir="rtl">{md(title["ar2"], True)}</div>')
    return f'''
<section class="page cover">
  <div class="c-frame"></div>
  <div class="c-logo">{logo_svg}</div>
  <div class="c-subj-ar" dir="rtl">{html.escape(meta.get("subject_ar", ""))}</div>
  <div class="c-subj-en">{html.escape(meta.get("subject", "").upper())}</div>
  <div class="c-art">{art_svg}</div>
  <div class="c-card">
    <div class="c-kick">{"THEORY" if theory else "PRACTICAL"} · {unit_en.upper()} {n}</div>
    <div class="c-en">{md(title["en"])}</div>
    <div class="c-ar" dir="rtl">{md(title["ar"], True)}</div>
    {sub}
    <div class="c-type"><span dir="rtl">{"نظري" if theory else "عملي"}</span> · {"Theory" if theory else "Practical"}</div>
  </div>
  <div class="c-info">
    <div class="c-row full"><span class="lab">Instructor <em dir="rtl">التدريسي</em></span>
      <span class="v"><b>{val(html.escape(meta.get("doctor", "")))}</b>{(' <em dir="rtl">' + html.escape(meta["doctor_ar"]) + '</em>') if meta.get("doctor_ar") else ''}</span></div>
    <div class="c-row"><span class="lab">Stage <em dir="rtl">المرحلة</em></span>
      <span class="v"><b>{STAGES_EN.get(st, "")} Stage</b> <em dir="rtl">{STAGES_AR.get(st, "")}</em></span></div>
    <div class="c-row"><span class="lab">Term <em dir="rtl">الفصل</em></span>
      <span class="v"><b>{STAGES_EN.get(term, "")} Term</b> <em dir="rtl">{TERMS_AR.get(term, "")}</em></span></div>
    <div class="c-row"><span class="lab">{unit_en} <em dir="rtl">{unit_ar}</em></span>
      <span class="v"><b>{n}</b> <em dir="rtl">{unit_ar} {str(n).translate(AR_DIGITS)}</em></span></div>
  </div>
</section>'''


def build(src, out_base, html_only=False):
    with open(src, encoding="utf-8") as f:
        txt = f.read()
    data = json.loads(txt) if src.endswith(".json") else parse_bw(txt)
    if not src.endswith(".json"):
        with open(os.path.splitext(src)[0] + ".json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    meta = data["meta"]
    tk = themes.pick(meta)
    th = themes.THEMES[tk]
    ctx = {"meta": meta, "sec": 0, "fig": 0, "imgdir": os.path.join(os.path.dirname(os.path.abspath(src)), "img")}
    meta["_title"] = next(b for b in data["blocks"] if b["t"] == "title")
    body = "\n".join(render_block(b, ctx) for b in data["blocks"])

    art = ""
    if th.get("art"):
        with open(os.path.join(ROOT, "assets", "art", th["art"]), encoding="utf-8") as f:
            art = f.read()
    with open(os.path.join(ROOT, "assets", "bios-emblem.svg"), encoding="utf-8") as f:
        logo = f.read()
    with open(os.path.join(ROOT, "assets", "bios-mark.svg"), encoding="utf-8") as f:
        mark = f.read()
    with open(os.path.join(ROOT, "assets", "workbook.css"), encoding="utf-8") as f:
        css = f.read().replace("FONTDIR", "file://" + os.path.join(ROOT, "assets", "fonts"))
    with open(os.path.join(HERE, "paginate.js"), encoding="utf-8") as f:
        js = f.read()

    unit = meta.get("unit", "lecture")
    st = int(meta.get("stage", 0) or 0)
    n = meta.get("lecture", 1)
    kind_ar = "نظري" if meta.get("type") == "theory" else "عملي"
    unit_ar = "الأسبوع" if unit == "week" else "المحاضرة"
    hdr = {
        "doctor": meta.get("doctor", ""),
        "line2": f"المرحلة {STAGES_AR.get(st, '')} · {kind_ar} · {unit_ar} {n}",
        "foot_en": meta["_title"]["en"],
        "foot_ar": meta["_title"]["ar"],
        "notes": int(meta.get("notes_lines", 3)),
        "mark": mark,
    }
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{html.escape(meta.get("subject", ""))} – {unit} {n}</title>
<style>:root{{{themes.css_vars(tk)}}}{css}</style></head>
<body>
{cover_html(meta, tk, art, logo)}
<div id="flow">{body}</div>
<script>window.HDR={json.dumps(hdr, ensure_ascii=False)};</script>
<script>{js}</script>
</body></html>'''
    os.makedirs(os.path.dirname(os.path.abspath(out_base)), exist_ok=True)
    html_path = out_base + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)
    print("html:", html_path)
    if html_only:
        return
    pdf_path = out_base + ".pdf"
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", os.path.join(HERE, "render.js"), html_path, pdf_path], check=True, env=env)
    print("pdf:", pdf_path)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    build(a[0], a[1], "--html-only" in sys.argv)
