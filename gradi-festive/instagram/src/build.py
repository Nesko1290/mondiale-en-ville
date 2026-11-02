"""Generate the GRADI "Big Opening" Instagram visuals as HTML, then render them to PNG.

Usage: python3 build.py   (from any directory; writes HTML here and PNGs in ../)
Rendering needs Node + Playwright (see render.cjs).
"""
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
IMG = (HERE.parent.parent / "img").as_uri()

FONTS = ("https://fonts.googleapis.com/css2?family=Caveat:wght@500"
         "&family=Gloock&family=Outfit:wght@300;400;600;800&display=swap")

BASE_CSS = """
:root { --bordeaux:#631c21; --profond:#3e1014; --forest:#1f3627; --cream:#efe2cc; --ink:#1a1414;
        --logo:'Outfit',sans-serif; --serif:'Gloock',serif; --script:'Caveat',cursive; }
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:var(--w); height:var(--h); overflow:hidden; }
body { background:var(--bg, var(--bordeaux)); color:var(--cream); font-family:var(--logo); position:relative; }
/* soft vignette + paper grain, like the printed moodboard tiles */
body::before { content:""; position:absolute; inset:0; z-index:5; pointer-events:none;
  background: radial-gradient(ellipse 80% 70% at 50% 45%, rgba(255,255,255,.05), rgba(0,0,0,.32) 100%); }
body::after { content:""; position:absolute; inset:0; z-index:6; pointer-events:none; opacity:.22; mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); }
.stage { position:absolute; inset:0; z-index:2; display:flex; flex-direction:column; align-items:center; text-align:center; }
.emblem { border-radius:50%; -webkit-mask-image:radial-gradient(circle, #000 58%, transparent 71%); mask-image:radial-gradient(circle, #000 58%, transparent 71%); }
.mark b { display:block; font-weight:800; letter-spacing:.02em; line-height:1; font-size:var(--s); }
.mark span { display:block; font-weight:400; font-size:calc(var(--s)*.118); letter-spacing:.42em; padding-left:.42em; text-transform:uppercase; margin-top:calc(var(--s)*.15); }
.label { font-weight:600; letter-spacing:.32em; text-transform:uppercase; padding-left:.32em; }
.rule { width:120px; height:1px; background:rgba(239,226,204,.5); }
.frame { position:absolute; inset:var(--fi, 36px); border:1.5px solid rgba(239,226,204,.35); z-index:3; pointer-events:none; }
.photo { object-fit:cover; display:block; filter:contrast(1.05) saturate(.95); }
"""


def page(w, h, bg, body, extra_css=""):
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<link rel="stylesheet" href="{FONTS}">
<style>:root{{--w:{w}px;--h:{h}px;--bg:var(--{bg});}}{BASE_CSS}{extra_css}</style></head>
<body>{body}</body></html>"""


def img(name):
    return f"{IMG}/{name}.webp"


# ---------- FEED 4:5 (1080 x 1350) ----------

def post_announce():
    css = """
    .stage { padding:96px 80px 88px; justify-content:space-between; }
    .big { font-weight:800; font-size:178px; line-height:.86; letter-spacing:-.005em; }
    .script { font-family:var(--script); font-size:118px; line-height:1; transform:rotate(-6deg); margin:-14px 0 -6px 220px; }
    .dates { font-family:var(--serif); font-size:150px; line-height:1; letter-spacing:.02em; }
    .dates i { font-style:normal; font-size:.5em; vertical-align:.32em; padding:0 .28em; opacity:.7; }
    """
    body = f"""<div class="frame"></div><div class="stage">
      <div style="display:flex;flex-direction:column;align-items:center;gap:22px">
        <img class="emblem" src="{img('moon-emblem')}" width="132" height="132">
        <div class="mark" style="--s:62px"><b>GRADI</b><span>Festif Expérience</span></div>
      </div>
      <div>
        <div class="big">BIG<br>OPENING</div>
        <div class="script">this week</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:20px">
        <div class="dates">5<i>✦</i>6<i>✦</i>7</div>
        <div class="label" style="font-size:24px">November · Genève</div>
        <div class="rule"></div>
        <div style="font-size:24px;font-weight:300;letter-spacing:.06em">Jeudi · Vendredi · Samedi</div>
      </div>
    </div>"""
    return page(1080, 1350, "bordeaux", body, css)


def post_photo():
    css = """
    .stage { padding:80px 72px 76px; justify-content:space-between; }
    .arch { width:560px; height:700px; border-radius:280px 280px 0 0; overflow:hidden; border:1.5px solid rgba(239,226,204,.45); padding:12px; }
    .arch img { width:100%; height:100%; border-radius:268px 268px 0 0; }
    .head { font-weight:800; font-size:92px; line-height:.92; }
    .dates { font-family:var(--serif); font-size:60px; line-height:1; }
    """
    body = f"""<div class="stage">
      <div class="label" style="font-size:22px">GRADI · Festif Expérience</div>
      <div class="arch"><img class="photo" src="{img('curtain')}"></div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:16px">
        <div class="head">BIG OPENING<br>THIS WEEK</div>
        <div class="dates">5 · 6 · 7 November</div>
      </div>
    </div>"""
    return page(1080, 1350, "forest", body, css)


NIGHTS = [
    ("Jeudi", "5", "Opening Night", "Le rideau s'ouvre.", "menu", "bordeaux"),
    ("Vendredi", "6", "Friday Night", "Le dîner, puis la piste.", "legs", "forest"),
    ("Samedi", "7", "Saturday Night", "Eat late, stay later.", "pasta", "profond"),
]


def carousel_cover():
    css = """
    .stage { padding:110px 80px; justify-content:center; gap:46px; }
    .big { font-weight:800; font-size:150px; line-height:.88; }
    .script { font-family:var(--script); font-size:96px; transform:rotate(-5deg); }
    .swipe { position:absolute; bottom:70px; right:80px; z-index:3; font-size:22px; letter-spacing:.3em; font-weight:600; }
    """
    body = f"""<div class="frame"></div><div class="stage">
      <img class="emblem" src="{img('moon-emblem')}" width="150" height="150">
      <div class="big">BIG<br>OPENING</div>
      <div class="script">three nights</div>
      <div class="label" style="font-size:26px">5 · 6 · 7 November · Genève</div>
    </div><div class="swipe">→</div>"""
    return page(1080, 1350, "bordeaux", body, css)


def carousel_night(day, num, title, line, photo, bg):
    css = """
    .stage { padding:84px 76px 80px; justify-content:space-between; align-items:stretch; text-align:left; }
    .top { display:flex; justify-content:space-between; align-items:flex-start; }
    .num { font-family:var(--serif); font-size:400px; line-height:.78; }
    .pic { width:400px; height:500px; border:1.5px solid rgba(239,226,204,.45); padding:10px; }
    .pic img { width:100%; height:100%; }
    .day { font-family:var(--serif); font-size:96px; line-height:1; }
    .title { font-weight:800; font-size:64px; letter-spacing:.01em; margin-top:10px; }
    .line { font-family:var(--serif); font-size:44px; margin-top:26px; opacity:.92; }
    .foot { display:flex; justify-content:space-between; font-size:20px; letter-spacing:.3em; font-weight:600; opacity:.75; }
    """
    body = f"""<div class="stage">
      <div class="top">
        <div><div class="label" style="font-size:22px;padding-left:0">November</div><div class="num">{num}</div></div>
        <div class="pic"><img class="photo" src="{img(photo)}"></div>
      </div>
      <div>
        <div class="day">{day} {num}</div>
        <div class="title">{title.upper()}</div>
        <div class="line">{line}</div>
      </div>
      <div class="foot"><span>GRADI</span><span>BIG OPENING · GENÈVE</span></div>
    </div>"""
    return page(1080, 1350, bg, body, css)


def carousel_cta():
    css = """
    .stage { padding:110px 90px; justify-content:center; gap:40px; }
    .h { font-family:var(--serif); font-size:96px; line-height:1.02; }
    .perk { font-size:30px; font-weight:300; line-height:1.5; }
    .btn { background:var(--cream); color:var(--bordeaux); font-weight:800; font-size:28px; letter-spacing:.18em; padding:26px 44px; }
    .dm { font-size:26px; letter-spacing:.06em; }
    .dm b { font-weight:800; }
    """
    body = f"""<div class="frame"></div><div class="stage">
      <img class="emblem" src="{img('moon-emblem')}" width="120" height="120">
      <div class="h">Une table<br>vous attend.</div>
      <div class="perk">Liste Privée : cocktail de bienvenue offert<br>et réservation prioritaire.</div>
      <div class="btn">RÉSERVER · LIEN EN BIO</div>
      <div class="dm">ou écrivez <b>FÊTE</b> en DM</div>
    </div>"""
    return page(1080, 1350, "forest", body, css)


# ---------- STORIES 9:16 (1080 x 1920) ----------
# Safe zone: keep text between y=250 and y=1580 (top bar, bottom reply/link sticker).

def story_announce():
    css = """
    .stage { padding:250px 80px 340px; justify-content:space-between; }
    .big { font-weight:800; font-size:190px; line-height:.86; }
    .script { font-family:var(--script); font-size:120px; transform:rotate(-6deg); margin:-10px 0 0 240px; }
    .strip { display:flex; gap:14px; }
    .strip img { width:290px; height:362px; }
    .dates { font-family:var(--serif); font-size:120px; line-height:1; }
    .sticker { position:absolute; left:50%; bottom:200px; transform:translateX(-50%); z-index:3; font-size:20px; letter-spacing:.3em; opacity:.6; font-weight:600; }
    """
    body = f"""<div class="stage">
      <div class="mark" style="--s:72px"><b>GRADI</b><span>Festif Expérience</span></div>
      <div><div class="big">BIG<br>OPENING</div><div class="script">this week</div></div>
      <div class="strip">
        <img class="photo" src="{img('menu')}"><img class="photo" src="{img('velvet')}"><img class="photo" src="{img('curtain')}">
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:18px">
        <div class="dates">5 · 6 · 7</div>
        <div class="label" style="font-size:26px">November · Genève</div>
      </div>
    </div><div class="sticker">↓ RÉSERVER ↓</div>"""
    return page(1080, 1920, "bordeaux", body, css)


def story_countdown(n, word, sub, bg):
    css = """
    .stage { padding:260px 80px 340px; justify-content:space-between; }
    .n { font-family:var(--serif); font-size:720px; line-height:.8; }
    .word { font-family:var(--script); font-size:130px; line-height:1; margin-top:-30px; }
    .head { font-weight:800; font-size:84px; line-height:.95; }
    """
    body = f"""<div class="frame" style="--fi:44px"></div><div class="stage">
      <img class="emblem" src="{img('moon-emblem')}" width="150" height="150">
      <div><div class="n">{n}</div><div class="word">{word}</div></div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:22px">
        <div class="head">BIG OPENING</div>
        <div class="label" style="font-size:26px">{sub}</div>
      </div>
    </div>"""
    return page(1080, 1920, bg, body, css)


def story_tonight(day, num, title, line, photo, bg):
    css = """
    .stage { padding:250px 80px 340px; justify-content:space-between; }
    .tonight { font-weight:800; font-size:170px; line-height:.86; }
    .pic { width:640px; height:760px; border:1.5px solid rgba(239,226,204,.45); padding:12px; }
    .pic img { width:100%; height:100%; }
    .day { font-family:var(--serif); font-size:86px; line-height:1; }
    .line { font-family:var(--serif); font-size:46px; opacity:.9; }
    """
    body = f"""<div class="stage">
      <div style="display:flex;flex-direction:column;align-items:center;gap:20px">
        <div class="label" style="font-size:26px">{title}</div>
        <div class="tonight">CE SOIR</div>
      </div>
      <div class="pic"><img class="photo" src="{img(photo)}"></div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:18px">
        <div class="day">{day} {num} novembre</div>
        <div class="line">{line}</div>
        <div class="label" style="font-size:22px;opacity:.75">GRADI · Genève</div>
      </div>
    </div>"""
    return page(1080, 1920, bg, body, css)


def main():
    jobs = {
        "01-post-big-opening": post_announce(),
        "02-post-big-opening-photo": post_photo(),
        "03-carrousel-1-couverture": carousel_cover(),
        "04-carrousel-2-jeudi": carousel_night(*NIGHTS[0]),
        "05-carrousel-3-vendredi": carousel_night(*NIGHTS[1]),
        "06-carrousel-4-samedi": carousel_night(*NIGHTS[2]),
        "07-carrousel-5-reserver": carousel_cta(),
        "08-story-annonce": story_announce(),
        "09-story-lundi-J-3": story_countdown("3", "jours", "Jeudi 5 · Vendredi 6 · Samedi 7", "bordeaux"),
        "10-story-mardi-J-2": story_countdown("2", "jours", "Jeudi 5 · Vendredi 6 · Samedi 7", "forest"),
        "11-story-mercredi-demain": story_countdown("1", "demain soir", "Jeudi 5 novembre · Genève", "profond"),
        "12-story-jeudi-ce-soir": story_tonight(*NIGHTS[0]),
        "13-story-vendredi-ce-soir": story_tonight(*NIGHTS[1]),
        "14-story-samedi-ce-soir": story_tonight(*NIGHTS[2]),
    }
    for name, html in jobs.items():
        (HERE / f"{name}.html").write_text(html, encoding="utf-8")
    subprocess.run(["node", str(HERE / "render.cjs"), str(HERE), str(HERE.parent)], check=True)


if __name__ == "__main__":
    main()
