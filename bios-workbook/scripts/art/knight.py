"""Knight theme art: cover illustration + small note stickers (original vector drawings).

Palette taken from the user's knight references: dark steel, antique gold, crimson.
  python3 bios-workbook/scripts/art/knight.py
writes assets/art/knight.svg (ECG chest), knight-parasitology.svg (flagellate chest) and assets/stickers/{alert,compare,tip,remember}.svg
"""
import math
import os
import random

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
STEEL_DK, STEEL, STEEL_LT, STEEL_HI = "#1c2126", "#3a424b", "#7d8893", "#c9d0d6"
GOLD_DK, GOLD, GOLD_LT = "#8a6424", "#c39a4a", "#ecd08c"
CRIM_DK, CRIM, CRIM_LT = "#5e0f17", "#9b1c26", "#c8323c"
PARCH = "#f6efe2"


def defs(u):
    return f'''<defs>
  <linearGradient id="{u}st" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{STEEL_LT}"/><stop offset=".35" stop-color="{STEEL_HI}"/>
    <stop offset=".55" stop-color="{STEEL_LT}"/><stop offset="1" stop-color="{STEEL}"/></linearGradient>
  <linearGradient id="{u}sd" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{STEEL}"/><stop offset="1" stop-color="{STEEL_DK}"/></linearGradient>
  <linearGradient id="{u}au" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{GOLD_LT}"/><stop offset=".55" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_DK}"/></linearGradient>
  <linearGradient id="{u}auh" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD_DK}"/><stop offset=".5" stop-color="{GOLD_LT}"/><stop offset="1" stop-color="{GOLD_DK}"/></linearGradient>
  <linearGradient id="{u}cr" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CRIM_LT}"/><stop offset=".6" stop-color="{CRIM}"/><stop offset="1" stop-color="{CRIM_DK}"/></linearGradient>
  <linearGradient id="{u}bl" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#9aa4ad"/><stop offset=".48" stop-color="#eef2f5"/>
    <stop offset=".52" stop-color="#b7c0c8"/><stop offset="1" stop-color="#6f7a85"/></linearGradient>
</defs>'''


def crown(cx, y, w, h, u, sw=1.2):
    """gold crown: band from y to y+h*.32, five points up to y-h*.68"""
    bw = w / 2
    band_t, band_b = y, y + h * .32
    tops = [(-1, .55), (-.5, .8), (0, 1.0), (.5, .8), (1, .55)]
    pts = []
    for i, (fx, fh) in enumerate(tops):
        x = cx + fx * bw * .92
        pts.append(f"{x:.1f} {band_t - h * .68 * fh:.1f}")
        if i < 4:
            xm = cx + (fx + .25) * bw * .92
            pts.append(f"{xm:.1f} {band_t - h * .12:.1f}")
    body = (f'<path d="M{cx - bw:.1f} {band_b:.1f} L{cx - bw:.1f} {band_t:.1f} L{" L".join(pts)} '
            f'L{cx + bw:.1f} {band_t:.1f} L{cx + bw:.1f} {band_b:.1f} Z" fill="url(#{u}au)" stroke="{GOLD_DK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    jewels = "".join(
        f'<circle cx="{cx + fx * bw * .92:.1f}" cy="{band_t - h * .68 * fh:.1f}" r="{w * .028:.1f}" fill="{GOLD_LT}" stroke="{GOLD_DK}" stroke-width="{sw * .6}"/>'
        for fx, fh in tops if fx != 0)
    cross = (f'<path d="M{cx:.1f} {band_t - h * .68 - h * .26:.1f} V{band_t - h * .55:.1f} M{cx - w * .05:.1f} {band_t - h * .68 - h * .15:.1f} H{cx + w * .05:.1f}" '
             f'stroke="{GOLD_DK}" stroke-width="{w * .035:.1f}" stroke-linecap="round"/>')
    band = (f'<rect x="{cx - bw:.1f}" y="{band_t + h * .08:.1f}" width="{w:.1f}" height="{h * .14:.1f}" fill="{GOLD_DK}" opacity=".35"/>'
            + "".join(f'<circle cx="{cx + k * w * .22:.1f}" cy="{band_t + h * .15:.1f}" r="{w * .03:.1f}" fill="{CRIM if k == 0 else GOLD_LT}"/>'
                      for k in (-2, -1, 0, 1, 2)))
    return cross + body + band + jewels


def great_helm(cx, top, w, h, u, cross=True, sw=1.4):
    """front-facing great helm (flat-topped dome, visor slit, breaths)"""
    l, r, b = cx - w / 2, cx + w / 2, top + h
    shell = (f'<path d="M{l:.1f} {b:.1f} L{l:.1f} {top + h * .3:.1f} Q{l:.1f} {top:.1f} {cx:.1f} {top - h * .02:.1f} '
             f'Q{r:.1f} {top:.1f} {r:.1f} {top + h * .3:.1f} L{r:.1f} {b:.1f} Q{cx:.1f} {b + h * .1:.1f} {l:.1f} {b:.1f} Z" '
             f'fill="url(#{u}st)" stroke="{STEEL_DK}" stroke-width="{sw}"/>')
    # shading on right half
    shade = (f'<path d="M{cx:.1f} {top - h * .02:.1f} Q{r:.1f} {top:.1f} {r:.1f} {top + h * .3:.1f} L{r:.1f} {b:.1f} '
             f'Q{cx + w * .25:.1f} {b + h * .07:.1f} {cx:.1f} {b + h * .05:.1f} Z" fill="{STEEL_DK}" opacity=".28"/>')
    sy = top + h * .40
    slit = (f'<path d="M{l + w * .06:.1f} {sy:.1f} Q{cx:.1f} {sy - h * .05:.1f} {r - w * .06:.1f} {sy:.1f} '
            f'L{r - w * .06:.1f} {sy + h * .085:.1f} Q{cx:.1f} {sy + h * .035:.1f} {l + w * .06:.1f} {sy + h * .085:.1f} Z" fill="{STEEL_DK}"/>')
    trim = (f'<path d="M{l:.1f} {top + h * .27:.1f} Q{cx:.1f} {top + h * .19:.1f} {r:.1f} {top + h * .27:.1f}" fill="none" stroke="url(#{u}auh)" stroke-width="{h * .05:.1f}"/>'
            f'<path d="M{l + w * .04:.1f} {sy + h * .15:.1f} Q{cx:.1f} {sy + h * .1:.1f} {r - w * .04:.1f} {sy + h * .15:.1f}" fill="none" stroke="url(#{u}auh)" stroke-width="{h * .035:.1f}"/>'
            f'<rect x="{cx - w * .045:.1f}" y="{top + h * .02:.1f}" width="{w * .09:.1f}" height="{h * .92:.1f}" rx="{w * .02:.1f}" fill="url(#{u}au)" opacity=".95"/>')
    holes = ""
    for side in (-1, 1):
        for i in range(3):
            for j in range(2):
                x = cx + side * (w * .2 + j * w * .1)
                y = top + h * (.66 + i * .08)
                holes += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{w * .022:.1f}" fill="{STEEL_DK}"/>'
    crs = ""
    if cross:
        x0, y0, s = cx - w * .3, top + h * .78, w * .085
        crs = (f'<path d="M{x0:.1f} {y0 - s:.1f} V{y0 + s * 1.3:.1f} M{x0 - s * .8:.1f} {y0 - s * .1:.1f} H{x0 + s * .8:.1f}" '
               f'stroke="{CRIM}" stroke-width="{s * .55:.1f}" stroke-linecap="round"/>')
    return shell + shade + slit + trim + holes + crs


def sword(cx, tip, guard, pommel, bw, u, gw=None):
    gw = gw or bw * 7
    blade = (f'<path d="M{cx:.1f} {tip:.1f} L{cx + bw / 2:.1f} {tip + bw * 1.6:.1f} L{cx + bw / 2:.1f} {guard:.1f} '
             f'L{cx - bw / 2:.1f} {guard:.1f} L{cx - bw / 2:.1f} {tip + bw * 1.6:.1f} Z" fill="url(#{u}bl)" stroke="{STEEL_DK}" stroke-width="{bw * .07:.1f}"/>'
             f'<path d="M{cx:.1f} {tip + bw * 1.2:.1f} V{guard - bw * .3:.1f}" stroke="{STEEL}" stroke-width="{bw * .1:.1f}" opacity=".6"/>')
    g = guard
    cg = (f'<path d="M{cx - gw / 2:.1f} {g + bw * .25:.1f} Q{cx:.1f} {g - bw * .45:.1f} {cx + gw / 2:.1f} {g + bw * .25:.1f} '
          f'L{cx + gw / 2:.1f} {g + bw * .75:.1f} Q{cx:.1f} {g + bw * .2:.1f} {cx - gw / 2:.1f} {g + bw * .75:.1f} Z" fill="url(#{u}au)" stroke="{GOLD_DK}" stroke-width="{bw * .08:.1f}"/>'
          f'<circle cx="{cx - gw / 2:.1f}" cy="{g + bw * .5:.1f}" r="{bw * .48:.1f}" fill="url(#{u}au)" stroke="{GOLD_DK}" stroke-width="{bw * .08:.1f}"/>'
          f'<circle cx="{cx + gw / 2:.1f}" cy="{g + bw * .5:.1f}" r="{bw * .48:.1f}" fill="url(#{u}au)" stroke="{GOLD_DK}" stroke-width="{bw * .08:.1f}"/>'
          f'<path d="M{cx:.1f} {g - bw * .55:.1f} L{cx + bw * .45:.1f} {g + bw * .35:.1f} L{cx:.1f} {g + bw * 1.1:.1f} L{cx - bw * .45:.1f} {g + bw * .35:.1f} Z" fill="{CRIM}" stroke="{GOLD_DK}" stroke-width="{bw * .08:.1f}"/>')
    grip_t, grip_b = g + bw * .9, pommel - bw * .5
    grip = (f'<rect x="{cx - bw * .32:.1f}" y="{grip_t:.1f}" width="{bw * .64:.1f}" height="{grip_b - grip_t:.1f}" rx="{bw * .2:.1f}" fill="{CRIM_DK}"/>'
            + "".join(f'<path d="M{cx - bw * .32:.1f} {grip_t + k * bw * .45:.1f} l{bw * .64:.1f} {bw * .25:.1f}" stroke="{GOLD}" stroke-width="{bw * .08:.1f}"/>'
                      for k in range(1, int((grip_b - grip_t) / (bw * .45)))))
    pm = f'<circle cx="{cx:.1f}" cy="{pommel:.1f}" r="{bw * .62:.1f}" fill="url(#{u}au)" stroke="{GOLD_DK}" stroke-width="{bw * .08:.1f}"/>'
    return blade + grip + pm + cg


# ───────────────────────── cover ─────────────────────────
def chest_parasite():
    """gold flagellate (trypanosome-like) engraved across the chest — parasitology"""
    top, bot = [], []
    for i in range(41):
        t = i / 40
        x = 252 + t * 128
        w = 9 * math.sin(math.pi * t) ** .8
        y = 300 + 7 * math.sin(t * math.pi * 2)
        top.append(f"{x:.1f} {y - w:.1f}")
        bot.append(f"{x:.1f} {y + w:.1f}")
    body = f'<path d="M{top[0]} L{" L".join(top[1:])} L{" L".join(reversed(bot))} Z" fill="{GOLD}" stroke="{GOLD_LT}" stroke-width="1.4" opacity=".95"/>'
    fin = "M256 300 " + " ".join(f"L{256 + k * 3.1:.1f} {300 + 7 * math.sin((k * 3.1 + 4) / 128 * math.pi * 2) - 9 * math.sin(math.pi * (k * 3.1 + 4) / 128) ** .8 - 3 - 2.4 * (k % 2):.1f}" for k in range(1, 40))
    flag = "M380 300 q12 -10 22 0 t22 0 t18 -2"
    return (body + f'<path d="{fin}" fill="none" stroke="{GOLD_LT}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="{flag}" fill="none" stroke="{GOLD_LT}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<circle cx="296" cy="303" r="4.6" fill="{STEEL_DK}" stroke="{GOLD_LT}" stroke-width="1.2"/>'
            f'<circle cx="262" cy="301" r="2" fill="{STEEL_DK}"/>')


def cover(chest="ecg"):
    u = "kc"
    W, H = 640, 360
    cx = 320
    rnd = random.Random(7)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">', defs(u)]
    s.append(f'''<defs>
  <linearGradient id="{u}arch" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e9e4d8"/><stop offset="1" stop-color="#d9d3c4"/></linearGradient>
  <clipPath id="{u}ac"><path d="M178 360 V170 Q178 40 320 8 Q462 40 462 170 V360 Z"/></clipPath>
</defs>''')
    # gothic arch window behind the knight
    s.append(f'<path d="M178 360 V170 Q178 40 320 8 Q462 40 462 170 V360 Z" fill="url(#{u}arch)"/>')
    rays = "".join(
        f'<path d="M320 150 L{320 + 420 * math.cos(a):.1f} {150 + 420 * math.sin(a):.1f} L{320 + 420 * math.cos(a + .06):.1f} {150 + 420 * math.sin(a + .06):.1f} Z" fill="{GOLD}" opacity=".10"/>'
        for a in [i * math.pi / 14 - math.pi for i in range(29)])
    s.append(f'<g clip-path="url(#{u}ac)">{rays}</g>')
    s.append(f'<path d="M178 360 V170 Q178 40 320 8 Q462 40 462 170 V360" fill="none" stroke="{GOLD}" stroke-width="2.2"/>')
    s.append(f'<path d="M190 360 V172 Q190 52 320 22 Q450 52 450 172 V360" fill="none" stroke="{GOLD}" stroke-width=".8" opacity=".7"/>')
    # banners left / right (heraldic pennants)
    for side in (-1, 1):
        x = cx + side * 222
        s.append(f'<path d="M{x - 3:.0f} 40 V330" stroke="{GOLD_DK}" stroke-width="3" stroke-linecap="round"/>'
                 f'<circle cx="{x - 3:.0f}" cy="36" r="5" fill="url(#{u}au)"/>'
                 f'<path d="M{x - 3:.0f} 50 h{side * 48} v86 l{-side * 24} -18 l{-side * 24} 18 Z" fill="url(#{u}cr)"/>'
                 f'<path d="M{x - 3 + side * 6:.0f} 56 h{side * 36} v68 l{-side * 18} -13 l{-side * 18} 13 Z" fill="none" stroke="{GOLD}" stroke-width="1.2"/>')
        # a small fleur on each banner
        fx = x - 3 + side * 24
        s.append(f'<path d="M{fx} 72 q-6 10 0 22 q6 -12 0 -22 Z M{fx - 9} 86 q6 -6 9 4 q-7 2 -9 -4 Z M{fx + 9} 86 q-6 -6 -9 4 q7 2 9 -4 Z" fill="{GOLD_LT}"/>'
                 f'<rect x="{fx - 7}" y="94" width="14" height="3" rx="1.5" fill="{GOLD_LT}"/>')
    # cape
    s.append(f'<path d="M262 196 Q200 250 150 360 H490 Q440 250 378 196 Z" fill="url(#{u}cr)"/>')
    s.append(f'<path d="M262 196 Q222 260 196 360 M378 196 Q418 260 444 360" fill="none" stroke="{CRIM_DK}" stroke-width="3" opacity=".6"/>')
    # torso plate
    s.append(f'<path d="M252 214 Q320 196 388 214 L404 360 H236 Z" fill="url(#{u}sd)"/>')
    s.append(f'<path d="M262 236 Q320 220 378 236" fill="none" stroke="url(#{u}auh)" stroke-width="3"/>')
    if chest == "parasite":
        s.append(chest_parasite())
    else:   # ECG pulse engraved on the chest (physiology)
        s.append(f'<path d="M248 300 H292 l7 -16 l8 32 l9 -46 l9 50 l7 -20 H392" fill="none" stroke="{GOLD_LT}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" opacity=".95"/>')
    # chainmail neck
    mail = "".join(f'<circle cx="{x}" cy="{y}" r="2.1" fill="none" stroke="{STEEL_LT}" stroke-width=".9" opacity=".75"/>'
                   for y in range(186, 222, 4) for x in range(272 + (y // 4 % 2) * 2, 370, 4))
    s.append(f'<path d="M270 182 H370 L382 214 Q320 204 258 214 Z" fill="{STEEL_DK}"/>{mail}')
    # pauldrons: three overlapping curved lames per shoulder, gold-rimmed
    for side in (-1, 1):
        def X(dx):
            return cx + side * dx
        lames = [(44, 196, 152, 218, 30), (58, 214, 150, 240, 26), (74, 234, 144, 262, 22)]
        for k, (x_in, y_top, x_out, y_bot, th) in reversed(list(enumerate(lames))):
            d = (f"M{X(x_in):.0f} {y_top + th:.0f} Q{X(x_in + 10):.0f} {y_top - 8:.0f} {X((x_in + x_out) / 2 + 14):.0f} {y_top - 4:.0f} "
                 f"Q{X(x_out + 4):.0f} {y_top + 4:.0f} {X(x_out):.0f} {y_bot:.0f} "
                 f"Q{X(x_out - 18):.0f} {y_bot + 6:.0f} {X(x_out - 30):.0f} {y_bot - 4:.0f} "
                 f"Q{X((x_in + x_out) / 2 + 6):.0f} {y_top + th * .55:.0f} {X(x_in):.0f} {y_top + th + 14:.0f} Z")
            s.append(f'<path d="{d}" fill="url(#{u}st)" stroke="{STEEL_DK}" stroke-width="1.5"/>')
            s.append(f'<path d="M{X(x_out):.0f} {y_bot:.0f} Q{X(x_out - 18):.0f} {y_bot + 6:.0f} {X(x_out - 30):.0f} {y_bot - 4:.0f} '
                     f'Q{X((x_in + x_out) / 2 + 6):.0f} {y_top + th * .55:.0f} {X(x_in):.0f} {y_top + th + 14:.0f}" fill="none" stroke="url(#{u}auh)" stroke-width="2.6"/>')
        # filigree swirl on the top lame
        s.append(f'<path d="M{X(86):.0f} 214 q{side * 10} -12 {side * 22} -3 q{side * 7} 7 {side * -3} 12 q{side * -8} 3 {side * -9} -5" fill="none" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"/>')
    # helm + crown
    s.append(great_helm(cx, 72, 116, 128, u, cross=False, sw=1.8))
    s.append(crown(cx, 66, 112, 46, u, sw=1.4))
    # sword in front, point up (like the reference composition)
    s.append(sword(cx, 92, 262, 330, 16, u, gw=150))
    # embers
    for _ in range(46):
        x, y = rnd.uniform(60, 580), rnd.uniform(10, 350)
        if 170 < x < 470 and y > 40:
            continue
        r = rnd.uniform(.8, 2.4)
        col = rnd.choice([GOLD_LT, GOLD, CRIM_LT])
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" opacity="{rnd.uniform(.35, .85):.2f}"/>')
    # ground line + laurel ticks
    s.append(f'<path d="M120 359 H520" stroke="{GOLD}" stroke-width="1.5"/>')
    s.append('</svg>')
    return "\n".join(s)


# ───────────────────────── stickers (100×100) ─────────────────────────
def badge(u, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{defs(u)}'
            f'<path d="M50 3 L91 18 V52 Q91 80 50 97 Q9 80 9 52 V18 Z" fill="url(#{u}au)"/>'
            f'<path d="M50 9 L85 22 V52 Q85 75 50 90 Q15 75 15 52 V22 Z" fill="url(#{u}sd)"/>'
            f'{inner}</svg>')


def st_alert():          # crowned great helm (exam alert)
    u = "sa"
    return badge(u, great_helm(50, 40, 40, 42, u, cross=True, sw=1) + crown(50, 37, 38, 20, u, sw=.8))


def st_compare():        # two crossed swords + small shield (compare)
    u = "sc"
    sw1 = sword(50, 14, 64, 82, 10, u, gw=34)
    return badge(u, f'<g transform="rotate(-35 50 52)">{sw1}</g><g transform="rotate(35 50 52)">{sw1}</g>'
                 f'<path d="M50 40 L62 45 V55 Q62 64 50 70 Q38 64 38 55 V45 Z" fill="url(#{u}cr)" stroke="{GOLD}" stroke-width="1.6"/>'
                 f'<path d="M50 46 V63 M43 52 H57" stroke="{GOLD_LT}" stroke-width="2.2" stroke-linecap="round"/>')


def st_tip():            # winged helm (memory tip)
    u = "st"
    wing = "".join(f'<path d="M62 {48 - k * 6} q{14 + k * 3} {-10 - k * 3} {22 + k * 2} {-16 - k * 2} q-4 {12 + k} {-20 - k * 2} {22 + k * 2} Z" '
                   f'fill="{GOLD_LT if k % 2 else GOLD}" stroke="{GOLD_DK}" stroke-width=".8"/>' for k in range(4))
    return badge(u, wing + great_helm(46, 34, 40, 46, u, cross=False, sw=1)
                 + f'<path d="M30 40 Q46 30 62 40" fill="none" stroke="url(#{u}auh)" stroke-width="2.6"/>')


def st_remember():       # crested (spartan) helm in profile (remember / key points)
    u = "sr"
    crest = "".join(f'<path d="M{24 + k * 4} {30 - math.sin(k / 12 * math.pi) * 6:.1f} l{-6 + k * .3:.1f} {-12 - math.sin(k / 12 * math.pi) * 6:.1f}" '
                    f'stroke="{CRIM_LT if k % 2 else CRIM}" stroke-width="4" stroke-linecap="round"/>' for k in range(13))
    helm = (f'<path d="M24 34 Q50 22 74 38 Q80 50 74 62 L62 62 L62 80 L44 84 Q30 76 26 58 Q22 46 24 34 Z" fill="url(#{u}st)" stroke="{STEEL_DK}" stroke-width="1.2"/>'
            f'<path d="M46 50 Q60 46 74 52 L74 58 Q60 54 48 58 Z" fill="{STEEL_DK}"/>'
            f'<path d="M56 58 L56 80" stroke="{STEEL_DK}" stroke-width="3"/>'
            f'<path d="M24 34 Q50 22 74 38" fill="none" stroke="url(#{u}auh)" stroke-width="3"/>'
            f'<path d="M28 44 Q44 40 50 48" fill="none" stroke="{GOLD}" stroke-width="1.6"/>')
    return badge(u, f'<path d="M22 30 Q48 14 76 30" fill="{CRIM_DK}"/>{crest}{helm}')


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "assets", "stickers"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "art", "knight.svg"), "w") as f:
        f.write(cover())
    with open(os.path.join(ROOT, "assets", "art", "knight-parasitology.svg"), "w") as f:
        f.write(cover("parasite"))
    for name, fn in [("alert", st_alert), ("compare", st_compare), ("tip", st_tip), ("remember", st_remember)]:
        with open(os.path.join(ROOT, "assets", "stickers", name + ".svg"), "w") as f:
            f.write(fn())
    print("ok")
