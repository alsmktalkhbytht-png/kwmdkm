"""Cover art for physiology: heart + ECG trace, a cell with organelles, a membrane bilayer
with a channel protein (transport), molecules and bubbles. Flat vector, coloured by theme classes."""
import math
import os
import random

random.seed(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "art", "physiology.svg")

S = []
a = S.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 380">')
a('''<style>
.a-p{fill:var(--p)}.a-pdk{fill:var(--pdk)}.a-p2{fill:var(--p2)}.a-acc{fill:var(--acc)}.a-accdk{fill:var(--accdk)}
.a-tint{fill:var(--tint)}.a-white{fill:#fff}.a-warm{fill:var(--warm)}.a-shade{fill:#000;opacity:.10}
.s-p{stroke:var(--p);fill:none}.s-p2{stroke:var(--p2);fill:none}.s-pdk{stroke:var(--pdk);fill:none}.s-acc{stroke:var(--acc);fill:none}
.s-white{stroke:#fff;fill:none}
</style>''')

# organic background blob
a('<path class="a-tint" d="M70 210 C40 120 120 40 240 52 C330 60 360 20 470 30 C590 42 660 120 640 210 '
  'C622 300 540 352 420 344 C330 338 290 368 190 352 C100 338 92 286 70 210 Z"/>')
# soft dots
for _ in range(70):
    x, y = random.uniform(30, 660), random.uniform(20, 360)
    a(f'<circle class="a-p2" cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(1, 2.4):.1f}" opacity="{random.uniform(.15, .4):.2f}"/>')
# bubbles
for _ in range(14):
    x, y, r = random.uniform(40, 650), random.uniform(30, 350), random.uniform(5, 13)
    a(f'<circle class="s-p2" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" stroke-width="1.6" opacity=".55"/>')

# ── membrane bilayer strip (bottom) with channel protein ──
y0 = 300
a('<g>')
a(f'<rect x="60" y="{y0 - 22}" width="560" height="44" rx="22" class="a-warm"/>')
for i in range(26):
    x = 80 + i * 21
    if 300 <= x <= 360:
        continue
    for side in (-1, 1):
        hy = y0 + side * 15
        a(f'<path class="s-p2" stroke-width="2.2" d="M{x - 3} {hy - side * 4} L{x - 3} {y0 + side * 2} M{x + 3} {hy - side * 4} L{x + 3} {y0 + side * 2}"/>')
        a(f'<circle class="a-p" cx="{x}" cy="{hy}" r="6"/>')
# channel protein
a(f'<rect x="298" y="{y0 - 36}" width="26" height="72" rx="12" class="a-acc"/>')
a(f'<rect x="336" y="{y0 - 36}" width="26" height="72" rx="12" class="a-acc"/>')
a(f'<rect x="304" y="{y0 - 30}" width="6" height="60" rx="3" class="a-white" opacity=".35"/>')
# molecules moving through channel
for i, yy in enumerate((y0 - 62, y0 - 2, y0 + 50)):
    a(f'<circle class="a-pdk" cx="330" cy="{yy}" r="7"/>')
a(f'<path class="s-pdk" stroke-width="3" stroke-linecap="round" d="M330 {y0 - 80} V{y0 + 70}" opacity=".25"/>')
a(f'<path class="a-pdk" d="M322 {y0 + 64} L338 {y0 + 64} L330 {y0 + 76} Z"/>')
# glucose hexagons near membrane
for cx, cy, s in ((150, 238, 13), (190, 252, 10), (520, 244, 12)):
    pts = " ".join(f"{cx + s * math.cos(math.radians(60 * k + 30)):.1f},{cy + s * math.sin(math.radians(60 * k + 30)):.1f}" for k in range(6))
    a(f'<polygon points="{pts}" class="a-white" stroke="var(--p)" stroke-width="2.4"/>')
a('</g>')

# ── ECG trace across ──
ecg = "M40 150 H170 L182 150 L190 138 L198 150 L214 150 L222 170 L236 70 L250 196 L260 150 L292 150 L304 130 L322 150 H420 " \
      "L430 150 L438 140 L446 150 L460 150 L468 168 L480 92 L492 186 L500 150 L528 150 L540 134 L556 150 H650"
a(f'<path d="{ecg}" class="s-white" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>')
a(f'<path d="{ecg}" class="s-acc" stroke-width="3.6" stroke-linejoin="round" stroke-linecap="round"/>')

# ── heart (left) ──
a('<g transform="translate(150 118)">')
a('<path class="a-accdk" d="M8 -62 C8 -86 30 -92 34 -74 L34 -40 L20 -40 Z"/>')                  # aorta
a('<path class="a-p" d="M-14 -58 C-16 -80 0 -84 4 -70 L2 -40 L-10 -40 Z"/>')                     # pulmonary
a('<path class="a-acc" d="M0 70 C-46 40 -78 6 -74 -26 C-70 -58 -34 -66 -10 -46 C2 -36 6 -36 14 -44 '
  'C40 -66 78 -54 76 -20 C74 14 44 44 0 70 Z"/>')
a('<path class="a-accdk" d="M0 70 C20 56 40 38 56 18 C30 30 12 40 0 70 Z" opacity=".55"/>')
a('<path class="a-white" d="M-50 -30 C-46 -46 -30 -50 -20 -44 C-34 -40 -42 -32 -46 -20 Z" opacity=".55"/>')
a('<path class="s-accdk" d="M6 -36 C2 -6 -12 20 -6 46" stroke="var(--accdk)" stroke-width="3" fill="none" opacity=".6"/>')
a('</g>')

# ── cell (right) ──
a('<g transform="translate(520 120)">')
a('<ellipse rx="96" ry="78" class="a-p2"/>')
a('<ellipse rx="88" ry="70" class="a-white"/>')
a('<ellipse rx="84" ry="66" class="a-tint"/>')
# ER
for k in range(4):
    a(f'<path class="s-p2" stroke-width="3" stroke-linecap="round" d="M{-6 + k * 7} {-50 - k * 2} C{30 + k * 6} {-56 - k * 3} {52 + k * 4} {-34 - k * 2} {58 + k * 3} {-8 - k * 2}"/>')
# nucleus
a('<circle cx="-12" cy="-4" r="30" class="a-pdk"/>')
a('<circle cx="-12" cy="-4" r="30" class="s-p2" stroke-width="3" stroke-dasharray="5 4"/>')
a('<circle cx="-4" cy="-10" r="9" class="a-p2"/>')
# mitochondria
for (mx, my, rot) in ((40, 34, -20), (-52, 40, 25), (54, -2, 70)):
    a(f'<g transform="translate({mx} {my}) rotate({rot})"><ellipse rx="17" ry="9" class="a-acc"/>'
      f'<path class="s-white" stroke-width="2" d="M-11 0 Q-8 -6 -5 0 T1 0 T7 0 T12 0"/></g>')
# golgi
for k in range(3):
    a(f'<path class="s-p" stroke-width="3.2" stroke-linecap="round" d="M{-70 + k * 5} {-26 + k * 7} q 14 -10 28 0"/>')
# vesicles
for (vx, vy) in ((-36, -46), (20, 52), (-70, 6), (66, 30)):
    a(f'<circle cx="{vx}" cy="{vy}" r="4.5" class="a-p"/>')
a('</g>')

# ── neuron hint (top-centre) ──
a('<g transform="translate(360 64)" opacity=".9">')
a('<path class="s-p" stroke-width="4" stroke-linecap="round" d="M0 0 L-34 -22 M0 0 L-30 18 M0 0 L-6 -32 M0 0 L70 6 M70 6 L86 -6 M70 6 L88 16"/>')
a('<circle r="12" class="a-p"/><circle r="5" class="a-white"/>')
a('</g>')

a('</svg>')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write("\n".join(S))
print("ok", OUT)
