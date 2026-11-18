"""Repeint la photo de reference du bus en blanc et orange (couleurs TPG).

Usage : python make_bus_tpg.py bus_reference_caribbean.jpg bus_reference_tpg.jpg
Vert -> orange vif, jaune -> blanc, bas de caisse rouge-orange conserve.
"""

import sys

import numpy as np
from PIL import Image


def main(src, dst):
    hsv = np.array(Image.open(src).convert("RGB").convert("HSV")).astype(np.float32)
    h, s, v = hsv[..., 0] / 255 * 360, hsv[..., 1] / 255, hsv[..., 2] / 255
    rows = np.arange(h.shape[0])[:, None] * np.ones((1, h.shape[1]))
    bus = rows > 452  # la carrosserie commence sous les arbres
    green = bus & (h > 75) & (h < 160) & (s > 0.45) & (v > 0.25)
    yellow = bus & (h > 33) & (h <= 75) & (s > 0.3) & (v > 0.3)
    out = hsv.copy()
    out[..., 0][green] = 22 / 360 * 255
    out[..., 1][green] = np.clip(s[green] * 1.05, 0, 1) * 255
    out[..., 2][green] = np.clip(v[green] * 1.25, 0, 1) * 255
    out[..., 1][yellow] = s[yellow] * 0.06 * 255
    out[..., 2][yellow] = np.clip(v[yellow] * 1.15, 0, 1) * 255
    Image.fromarray(out.astype(np.uint8), "HSV").convert("RGB").save(dst, quality=95)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
