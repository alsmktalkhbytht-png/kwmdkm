#!/usr/bin/env python3
"""preview.py <file.pdf> <outdir> [dpi] — render pages to PNG + contact sheets (8 per sheet)."""
import glob
import os
import subprocess
import sys

from PIL import Image

pdf, out = sys.argv[1], sys.argv[2]
dpi = sys.argv[3] if len(sys.argv) > 3 else "45"
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.png")):
    os.remove(f)
subprocess.run(["pdftoppm", "-r", dpi, "-png", pdf, os.path.join(out, "p")], check=True)
pages = sorted(glob.glob(os.path.join(out, "p-*.png")))
ims = [Image.open(p) for p in pages]
w, h = ims[0].size
per = 8
for k in range(0, len(ims), per):
    sheet = Image.new("RGB", (w * 4 + 30, h * 2 + 10), "#777")
    for j, im in enumerate(ims[k:k + per]):
        sheet.paste(im, ((j % 4) * (w + 10), (j // 4) * (h + 10)))
    sheet.save(os.path.join(out, f"sheet{k // per:02d}.png"))
print(len(ims), "pages")
