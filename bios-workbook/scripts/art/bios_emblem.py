"""Generates the BIOS emblem (cover) and compact mark (page header).

Non-circular identity: a burgundy 'page tile' whose lower edge opens like a book, a folded
gold corner, the A / 文 translation bubbles, and the BIOS word with the I drawn as a pen nib.
Colours keep the original identity: burgundy + cream + gold.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

BURG, BURG_DK, BURG_LT = "#8a2233", "#4f0f1c", "#a8364a"
CREAM, GOLD, GOLD_LT, GOLD_DK = "#f8eedc", "#d4a54e", "#f0cf86", "#a87a2c"

TILE = "M34 8 H270 L304 42 V156 Q233 144 162 172 Q91 144 20 156 V22 Q20 8 34 8 Z"


def svg(with_tagline=True, uid="e"):
    tag = ""
    if with_tagline:
        tag = f'''
  <g font-family="Mada" font-weight="800" text-anchor="middle">
    <line x1="48" y1="133.5" x2="72" y2="133.5" stroke="{GOLD}" stroke-width="1.2"/>
    <line x1="252" y1="133.5" x2="276" y2="133.5" stroke="{GOLD}" stroke-width="1.2"/>
    <rect x="72.5" y="131" width="5" height="5" transform="rotate(45 75 133.5)" fill="{GOLD}"/>
    <rect x="246.5" y="131" width="5" height="5" transform="rotate(45 249 133.5)" fill="{GOLD}"/>
    <text x="162" y="137.6" font-size="10" letter-spacing="2.1" fill="{GOLD_LT}">LECTURE TRANSLATION</text>
  </g>'''
    word_y = 118 if with_tagline else 128
    dy = word_y - 118
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 324 196" role="img" aria-label="BIOS">
  <defs>
    <linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BURG_LT}"/><stop offset=".45" stop-color="{BURG}"/><stop offset="1" stop-color="{BURG_DK}"/>
    </linearGradient>
    <linearGradient id="{uid}au" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GOLD_LT}"/><stop offset=".55" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_DK}"/>
    </linearGradient>
    <linearGradient id="{uid}fold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{GOLD_DK}"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_LT}"/>
    </linearGradient>
    <clipPath id="{uid}c"><path d="{TILE}"/></clipPath>
    <pattern id="{uid}dots" width="9" height="9" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r=".9" fill="#fff" opacity=".10"/>
    </pattern>
  </defs>
  <!-- page block under the tile (book thickness) -->
  <path d="M20 156 Q91 144 162 172 Q233 144 304 156 V163 Q233 151 162 179 Q91 151 20 163 Z" fill="{CREAM}"/>
  <path d="M20 163 Q91 151 162 179 Q233 151 304 163 V168 Q233 156 162 185 Q91 156 20 168 Z" fill="url(#{uid}au)"/>
  <!-- tile -->
  <path d="{TILE}" fill="url(#{uid}g)"/>
  <g clip-path="url(#{uid}c)">
    <rect x="0" y="0" width="324" height="196" fill="url(#{uid}dots)"/>
    <path d="M150 -10 L222 -10 L110 200 L38 200 Z" fill="#fff" opacity=".055"/>
    <path d="M236 -10 L256 -10 L144 200 L124 200 Z" fill="#fff" opacity=".04"/>
    <path d="M162 40 V172" stroke="{BURG_DK}" stroke-width="1" opacity=".0"/>
  </g>
  <path d="M40 16 H266 L295 45 V148 Q232 137 162 162 Q92 137 29 148 V28 Q29 16 40 16 Z" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".5"/>
  <!-- folded corner -->
  <path d="M270 8 L304 42 H281 Q270 42 270 31 Z" fill="url(#{uid}fold)"/>
  <path d="M270 8 L304 42" stroke="{GOLD_DK}" stroke-width=".8" opacity=".6"/>
  <!-- translation bubbles -->
  <g transform="translate(-6 {min(dy, 6) - 5})">
    <path d="M38 22 h34 a7 7 0 0 1 7 7 v18 a7 7 0 0 1 -7 7 h-18 l-9 8 v-8 h-7 a7 7 0 0 1 -7 -7 v-18 a7 7 0 0 1 7 -7 z" fill="{CREAM}"/>
    <text x="51" y="45.5" font-family="Mada" font-weight="900" font-size="21" fill="{BURG}" text-anchor="middle">A</text>
    <path d="M70 34 h28 a7 7 0 0 1 7 7 v16 a7 7 0 0 1 -7 7 h-5 v8 l-9 -8 h-14 a7 7 0 0 1 -7 -7 v-16 a7 7 0 0 1 7 -7 z"
      fill="url(#{uid}au)" stroke="{BURG}" stroke-width="2.2"/>
    <text x="84" y="56" font-family="WenQuanYi Zen Hei, Noto Sans CJK SC, sans-serif" font-weight="700" font-size="16" fill="{BURG_DK}" text-anchor="middle">文</text>
  </g>
  <!-- wordmark: B · nib · O S -->
  <g transform="translate(0 {dy})">
    <text x="121" y="118" font-family="Mada" font-weight="900" font-size="72" fill="{CREAM}" text-anchor="end" letter-spacing="0">B</text>
    <g transform="translate(136 0)">
      <path d="M-8 64 H8 V73 Q15 86 11 99 L0 122 L-11 99 Q-15 86 -8 73 Z" fill="url(#{uid}au)"/>
      <path d="M-8 73 H8" stroke="{BURG_DK}" stroke-width="1.6" opacity=".7"/>
      <circle cx="0" cy="95" r="3.4" fill="{BURG}"/>
      <path d="M0 98 V119" stroke="{BURG}" stroke-width="1.8" stroke-linecap="round"/>
    </g>
    <text x="153" y="118" font-family="Mada" font-weight="900" font-size="72" fill="{CREAM}" letter-spacing="1">OS</text>
  </g>{tag}
</svg>'''


if __name__ == "__main__":
    with open(os.path.join(OUT, "bios-emblem.svg"), "w") as f:
        f.write(svg(True, "e"))
    with open(os.path.join(OUT, "bios-mark.svg"), "w") as f:
        f.write(svg(False, "m"))
    print("ok")
