"""Photo de reference du bus, version finale : blanc et orange, tournee vers la droite.

Part de la photo sans inscription, la repeint (make_bus_tpg), la retourne
horizontalement pour que l'avant du bus soit a droite (sens de marche dans le
travelling), puis ecrit le lettrage a l'endroit sur le bandeau.

Usage : python make_bus_reference_v2.py bus_reference_plain.jpg bus_reference_tpg.jpg
"""

import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import make_bus_tpg

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
TEXT = "FROM THE CARIBBEAN TO GENEVA"
COLOR = (40, 22, 10)
X0, X1, Y = 4, 470, 496  # bandeau apres retournement


def main(src, dst):
    with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
        make_bus_tpg.main(src, tmp.name)
        im = ImageOps.mirror(Image.open(tmp.name).convert("RGB"))
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = 24
    while True:
        font = ImageFont.truetype(FONT, size)
        spacing = size * 0.08
        widths = [d.textlength(ch, font=font) for ch in TEXT]
        total = sum(widths) + spacing * (len(TEXT) - 1)
        if total <= (X1 - X0) - 30 or size <= 8:
            break
        size -= 1
    x = (X0 + X1) / 2 - total / 2
    for ch, w in zip(TEXT, widths):
        d.text((x, Y), ch, font=font, fill=COLOR + (240,), anchor="lm")
        x += w + spacing
    layer = layer.rotate(0.5, center=((X0 + X1) / 2, Y), resample=Image.BICUBIC)
    layer = layer.filter(ImageFilter.GaussianBlur(0.4))
    im.paste(layer, (0, 0), layer)
    im.save(dst, quality=95)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
