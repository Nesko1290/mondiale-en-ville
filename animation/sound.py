"""Bande-son de la version Geneve : musique + sound design, calee sur le montage.

Usage : python sound.py video_avec_carton.mp4 sortie.mp4
(la video d'entree est celle produite par endcard.py : rendu Genjutsu + carton)

Timeline (secondes) :
  0.0-1.9   ciel : vent qui monte, puis souffle quand la camera traverse le nuage
  1.8       la musique demarre plein pot sur la traversee du nuage
  1.9-4.0   plongee : vent
  3.4-8.2   moteur du bus a fond
  4.4-8.4   carrefour : klaxons, pneus qui crissent (le bus grille le feu a 5,35 s)
  8.0-10.8  dans le bus : passagers qui crient et rient, moteur etouffe
  10.5-13.5 le bus passe devant la femme : souffle et feuilles mortes
  12.7-15.8 course vers le panneau : vent qui monte, puis impact sur le carton
  15.8-fin  carton : la musique va jusqu'a sa fin naturelle
"""

import argparse
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "audio")

MUSIC_START = 1.8
CARD_AT = 15.8


def ms(t):
    return int(round(t * 1000))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--music-volume", type=float, default=0.75)
    args = ap.parse_args()

    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video],
        capture_output=True, text=True, check=True).stdout.strip())

    inputs = [args.video] + [os.path.join(A, f) for f in (
        "music_geneve.mp3",  # 1
        "sfx_dive.mp3",  # 2
        "sfx_moteur.mp3",  # 3
        "sfx_trafic.mp3",  # 4
        "sfx_passagers.mp3",  # 5
        "sfx_bourrasque.mp3",  # 6
        "sfx_riser.mp3",  # 7
        "sfx_bus.mp3",  # 8
    )]

    def wind(label, start, dur, peak, rise=True):
        """Souffle synthetique : bruit rose filtre dont le volume monte (ou descend)."""
        env = f"pow(t/{dur},1.5)" if rise else f"pow(1-t/{dur},1.5)"
        return (f"anoisesrc=color=pink:duration={dur}:amplitude=0.6,highpass=f=350,lowpass=f=5500,"
                f"volume='0.12*{peak}+{peak}*{env}':eval=frame,afade=t=out:st={dur - 0.2}:d=0.2,"
                f"adelay={ms(start)}:all=1[{label}]")

    af = ";".join([
        f"[1:a]adelay={ms(MUSIC_START)}:all=1,volume={args.music_volume}[mus]",
        wind("w1", 0.0, 1.9, 2.4),  # monte jusqu'a la traversee du nuage
        f"[2:a]atrim=0:1.2,volume=5,adelay={ms(1.55)}:all=1[burst]",
        wind("w2", 1.9, 2.3, 0.35, rise=False),  # plongee
        # moteur du bus : dehors a fond, puis etouffe a l'interieur
        "[3:a]asplit=2[m1][m2]",
        f"[m1]volume=1.0,afade=t=in:d=0.6,afade=t=out:st=4.2:d=0.8,adelay={ms(3.4)}:all=1[mot1]",
        f"[m2]lowpass=f=500,volume=1.1,atrim=0:3.0,afade=t=in:d=0.3,afade=t=out:st=2.5:d=0.5,"
        f"adelay={ms(8.0)}:all=1[mot2]",
        f"[8:a]atrim=2.6:5.0,asetpts=PTS-STARTPTS,volume=1.6,afade=t=in:d=0.2,afade=t=out:st=1.9:d=0.5,"
        f"adelay={ms(5.6)}:all=1[pass]",
        # carrefour : klaxons et pneus au moment ou le bus grille le feu
        f"[4:a]volume=1.25,afade=t=in:d=0.3,afade=t=out:st=3.3:d=0.7,adelay={ms(4.4)}:all=1[trafic]",
        # dans le bus
        f"[5:a]volume=1.15,afade=t=in:d=0.15,afade=t=out:st=2.4:d=0.6,adelay={ms(8.1)}:all=1[gens]",
        # la femme : passage du bus + bourrasque de feuilles
        f"[6:a]volume=1.2,afade=t=out:st=2.4:d=0.6,adelay={ms(10.5)}:all=1[rafale]",
        # course vers le panneau, impact sur le carton
        wind("w3", 12.7, 3.1, 0.45),
        f"[7:a]volume=0.6,adelay={ms(CARD_AT - 1.3)}:all=1[impact]",
        f"[mus][w1][burst][w2][mot1][mot2][pass][trafic][gens][rafale][w3][impact]"
        f"amix=inputs=12:normalize=0:duration=longest,atrim=0:{total},"
        f"afade=t=out:st={total - 0.6}:d=0.6,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0:LRA=11[a]",
    ])
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p in inputs:
        cmd += ["-i", p]
    cmd += ["-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", str(total),
            "-movflags", "+faststart", args.out]
    subprocess.run(cmd, check=True)
    print("OK ->", args.out)


if __name__ == "__main__":
    main()
