"""Montage final : rendu Genjutsu + bande-son + carton d'infos de la soiree.

Usage : python assemble.py rendu_genjutsu.mp4 sortie.mp4 [--voice audio/voice_b.mp3]

Timeline (secondes) :
  0.0-2.5   plongee : vent
  2.5-7.8   bus : moteur, klaxon ; riddim
  7.7-10.2  break musical : passage du bus + voix du rasta
  10.2      drop + impact : le texte apparait sur le ciel
  12.0-14.5 derniere image figee, le texte reste lisible
"""

import argparse
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "audio")
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

VIDEO_LEN = 12.0
HOLD = 2.5
TOTAL = VIDEO_LEN + HOLD
DROP = 10.2  # drop musical + apparition du texte

# (texte, taille relative a la hauteur, position verticale relative, police, couleur, delai)
LINES = [
    ("BUBBLE", 0.115, 0.24, FONT_BLACK, "0xFFD400", 0.0),
    ("SAT 28 NOVEMBER", 0.050, 0.40, FONT_BLACK, "white", 0.35),
    ("KULTURE BAR · GENÈVE", 0.038, 0.47, FONT_BOLD, "white", 0.6),
    ("DJ BLITZ & GOLD UP", 0.046, 0.57, FONT_BLACK, "0x2BD957", 0.85),
    ("22H – 04H", 0.038, 0.64, FONT_BOLD, "white", 1.1),
]


def text_filters(tmpdir, height):
    parts = []
    px = max(1, round(height * 0.004))
    for i, (text, size, ypos, font, color, delay) in enumerate(LINES):
        path = os.path.join(tmpdir, f"line{i}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        t0 = DROP + delay
        alpha = f"if(lt(t,{t0}),0,min(1,(t-{t0})/0.25))"
        parts.append(
            f"drawtext=fontfile={font}:textfile={path}:fontsize=h*{size}:fontcolor={color}"
            f":x=(w-text_w)/2:y=h*{ypos}-text_h/2:alpha='{alpha}'"
            f":borderw={px}:bordercolor=black@0.55:shadowcolor=black@0.45:shadowx=0:shadowy={px}"
        )
    return ",".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--voice", default=os.path.join(AUDIO, "voice_b.mp3"))
    ap.add_argument("--voice-cuts", default="1.0:2.1,2.45:3.45",
                    help="debut:fin des deux phrases dans le fichier voix")
    args = ap.parse_args()
    (a0, a1), (b0, b1) = [tuple(float(v) for v in c.split(":")) for c in args.voice_cuts.split(",")]

    inputs = [
        args.video,
        os.path.join(AUDIO, "music.mp3"),
        os.path.join(AUDIO, "sfx_dive.mp3"),
        os.path.join(AUDIO, "sfx_bus.mp3"),
        os.path.join(AUDIO, "sfx_riser.mp3"),
        args.voice,
    ]

    def ms(t):
        return int(round(t * 1000))

    height = int(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height",
         "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip())

    with tempfile.TemporaryDirectory() as tmp:
        vf = (
            f"[0:v]trim=0:{VIDEO_LEN},setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={HOLD},{text_filters(tmp, height)},format=yuv420p[v]"
        )
        af = ";".join([
            # musique : son break (7.0-9.5 s dans le morceau) tombe sur le rasta, son drop sur le texte
            f"[1:a]adelay={ms(DROP - 9.5)}:all=1,volume=0.5[mus]",
            # plongee : bruitage + souffle de vent synthetique qui accelere
            f"[2:a]atrim=0:2.6,volume=4,afade=t=out:st=2.2:d=0.4[dive]",
            f"anoisesrc=color=pink:duration=2.7:amplitude=0.6,highpass=f=400,lowpass=f=5000,"
            f"volume='0.02+0.5*pow(t/2.5,3)':eval=frame,afade=t=out:st=2.45:d=0.25[wind]",
            # bus : moteur pendant le travelling, puis passage devant le rasta (a 8,8 s)
            f"[3:a]asplit=2[busa][busb]",
            f"[busa]atrim=0:3.2,asetpts=PTS-STARTPTS,volume=2.2,afade=t=in:d=0.4,afade=t=out:st=2.7:d=0.5,"
            f"adelay={ms(2.3)}:all=1[bus1]",
            f"[busb]atrim=0:5.0,asetpts=PTS-STARTPTS,volume=1.8,afade=t=in:d=0.4,afade=t=out:st=4.4:d=0.6,"
            f"adelay={ms(5.2)}:all=1[bus2]",
            # montee vers l'impact, cale sur le drop
            f"[4:a]volume=0.55,adelay={ms(DROP - 1.3)}:all=1[riser]",
            # voix du rasta, en deux phrases
            f"[5:a]asplit=2[va][vb]",
            f"[va]atrim={a0}:{a1},asetpts=PTS-STARTPTS,volume=1.6,adelay={ms(8.2)}:all=1[v1]",
            f"[vb]atrim={b0}:{b1},asetpts=PTS-STARTPTS,volume=1.6,adelay={ms(9.3)}:all=1[v2]",
            f"[mus][dive][wind][bus1][bus2][riser][v1][v2]amix=inputs=8:normalize=0:duration=longest,"
            f"atrim=0:{TOTAL},afade=t=out:st={TOTAL - 0.7}:d=0.7,alimiter=limit=0.95,"
            f"loudnorm=I=-14:TP=-1.0:LRA=11[a]",
        ])
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for p in inputs:
            cmd += ["-i", p]
        cmd += [
            "-filter_complex", vf + ";" + af,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", str(TOTAL), "-movflags", "+faststart", args.out,
        ]
        subprocess.run(cmd, check=True)
    print("OK ->", args.out)


if __name__ == "__main__":
    main()
