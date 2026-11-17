"""Remplace l'inscription du bandeau du bus par "BUBBLE" sur la photo de reference.

Usage : python make_bus_reference.py photo_source.jpg bus_reference_bubble.jpg
"""

import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
X0, X1 = 250, 716  # etendue horizontale de l'ancienne inscription
Y_TOP = 481  # ligne de vert propre au-dessus du texte
TEXT = "BUBBLE"
COLOR = (22, 84, 30)


def main(src, dst):
    im = Image.open(src).convert("RGB")
    px = im.load()
    # Efface l'ancien texte : degrade vertical entre le vert au-dessus et en dessous.
    for x in range(X0, X1):
        y_bot = int(round(509 + (x - X0) / (X1 - X0) * 2))
        top, bot = px[x, Y_TOP], px[x, y_bot]
        for y in range(Y_TOP, y_bot + 1):
            t = (y - Y_TOP) / (y_bot - Y_TOP)
            px[x, y] = tuple(int(round(top[c] * (1 - t) + bot[c] * t)) for c in range(3))
    band = im.crop((X0, Y_TOP, X1, 512)).filter(ImageFilter.GaussianBlur(1.2))
    im.paste(band, (X0, Y_TOP))

    # Ecrit BUBBLE en capitales espacees, legerement incline comme le bandeau.
    font = ImageFont.truetype(FONT, 24)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    spacing = 14
    widths = [d.textlength(ch, font=font) for ch in TEXT]
    total = sum(widths) + spacing * (len(TEXT) - 1)
    x = (X0 + X1) / 2 - total / 2 + 20
    for ch, w in zip(TEXT, widths):
        d.text((x, 496), ch, font=font, fill=COLOR + (235,), anchor="lm")
        x += w + spacing
    layer = layer.rotate(-0.5, center=((X0 + X1) / 2, 496), resample=Image.BICUBIC)
    layer = layer.filter(ImageFilter.GaussianBlur(0.4))
    im.paste(layer, (0, 0), layer)
    im.save(dst, quality=95)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
