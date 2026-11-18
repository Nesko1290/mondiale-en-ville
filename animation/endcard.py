"""Carton final facon panneau, avec le vrai logo Bubble et le texte exact.

Le rendu Genjutsu finit en poussant sur le panneau ; on enchaine par un fondu
rapide sur ce carton plein cadre, qui continue le mouvement par un leger zoom.

Usage : python endcard.py rendu_genjutsu.mp4 sortie.mp4 [--hold 3.0]
"""

import argparse
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "logo_bubble.png")
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

# (texte, taille relative a la largeur, police, couleur, espace au-dessus relatif a la hauteur)
LINES = [
    ("SAT 28 NOV", 0.105, FONT_BLACK, (255, 255, 255), 0.05),
    ("KULTURE BAR", 0.118, FONT_BLACK, (255, 212, 0), 0.03),
    ("GENEVA", 0.075, FONT_BOLD, (255, 255, 255), 0.012),
    ("DJ BLITZ & GOLD UP", 0.074, FONT_BLACK, (255, 255, 255), 0.05),
    ("22H – 04H", 0.075, FONT_BOLD, (255, 212, 0), 0.015),
]


def make_card(width, height, path):
    w, h = width * 2, height * 2  # dessine en double resolution
    card = Image.new("RGB", (w, h), (12, 12, 16))
    d = ImageDraw.Draw(card)
    m = int(w * 0.055)
    d.rounded_rectangle((m, m, w - m, h - m), radius=int(w * 0.05), outline=(255, 255, 255), width=int(w * 0.012))

    logo = Image.open(LOGO).convert("RGBA")
    lw = int(w * 0.8)
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)

    fonts = [ImageFont.truetype(f, int(w * size)) for _, size, f, _, _ in LINES]
    heights = [d.textbbox((0, 0), t, font=fo)[3] - d.textbbox((0, 0), t, font=fo)[1]
               for (t, *_), fo in zip(LINES, fonts)]
    total = logo.height + sum(heights) + sum(int(h * gap) for *_, gap in LINES)
    y = (h - total) // 2
    card.paste(logo, ((w - lw) // 2, y), logo)
    y += logo.height
    for (text, _, _, color, gap), font, th in zip(LINES, fonts, heights):
        y += int(h * gap)
        box = d.textbbox((0, 0), text, font=font)
        d.text(((w - (box[2] - box[0])) // 2 - box[0], y - box[1]), text, font=font, fill=color)
        y += th
    card.save(path)


def probe(video, entry):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", entry, "-of", "csv=p=0", video],
        capture_output=True, text=True, check=True).stdout.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--hold", type=float, default=3.0, help="duree du carton en secondes")
    ap.add_argument("--fade", type=float, default=0.35)
    ap.add_argument("--card-only", help="ecrit seulement l'image du carton a ce chemin")
    args = ap.parse_args()

    width, height = (int(v) for v in probe(args.video, "stream=width,height").split(","))
    duration = float(probe(args.video, "format=duration"))
    if args.card_only:
        make_card(width, height, args.card_only)
        return

    with tempfile.TemporaryDirectory() as tmp:
        card = os.path.join(tmp, "card.png")
        make_card(width, height, card)
        n = int((args.hold + args.fade) * 30)
        # le carton avance lentement, pour prolonger la poussee de camera
        zoom = f"zoompan=z='1.0+0.05*min(1,on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={width}x{height}:fps=30"
        fc = (
            f"[0:v]fps=30,format=yuv420p,setsar=1[v0];"
            f"[1:v]{zoom},format=yuv420p,setsar=1[v1];"
            f"[v0][v1]xfade=transition=fade:duration={args.fade}:offset={duration - args.fade:.3f}[v]"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", args.video, "-i", card,
             "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
             "-movflags", "+faststart", args.out], check=True)
    print("OK ->", args.out)


if __name__ == "__main__":
    main()
