"""Blockout Blender v4 : bus aux couleurs TPG sur le quai du Mont-Blanc, Geneve.

Un seul plan continu de 15,5 s :
  0.0-1.9   dans le ciel : nuage "GENEVA ARE YOU READY?", la camera le traverse
  1.9-4.0   plongee vers le quai : lac, Jet d'Eau, immeubles haussmanniens
  4.0-5.6   au-dessus du toit (valises), feux rouges droit devant : le bus passe sous le portique
  5.6-8.0   travelling lateral cote lac, lettrage du bus, facades qui defilent
  8.0-9.0   la camera entre par une fenetre laterale
  9.0-10.6  traverse le bus dans l'allee, passagers avec valises, sort par l'arriere
  10.6-12.7 pivote sur la femme au telephone sur la promenade, qui se retourne
  12.7-15.5 fonce le long du quai jusqu'au panneau geant avec les infos

Formes grossieres, une couleur par chose. Sert de "Video 1" pour Higgsfield Genjutsu.

Lancer :
    blender -b -P build.py -- --out out
ou, avec le module Python de Blender :
    python build.py --out out
Options : --stills 1,75,135   (images de controle seulement)
          --res 720x1280      --step 1
Les images sortent dans <out>/frames ; le rendu saute les images deja presentes,
donc on peut relancer la commande si Blender plante en cours de route.
"""

import argparse
import math
import os
import random
import sys

import bpy  # doit etre importe avant bmesh / mathutils
import bmesh
from mathutils import Vector

FPS = 30
INTRO = 1.5  # secondes dans le ciel avant la plongee
DURATION = 14.0 + INTRO
N_FRAMES = int(FPS * DURATION)  # 465
BUS_SPEED = 20.0  # m/s, le long de +X
BUS_Y = -1.5  # roule a droite (Suisse), voie cote lac

BUS_TEXT = "FROM THE CARIBBEAN TO GENEVA"
CLOUD_LINES = [("GENEVA", 7.0, 9.5), ("ARE YOU", 5.5, 0.0), ("READY?", 7.0, -9.5)]  # texte, hauteur, decalage
SIGN_LINES = [  # (texte, hauteur des lettres en m, altitude du centre en m)
    ("Bubble", 1.9, 13.1),  # logo jaune
    ("SAT 28 NOV", 1.1, 11.3),
    ("KULTURE BAR", 0.95, 9.7),
    ("GENEVA", 0.95, 8.4),
    ("DJ BLITZ & GOLD UP", 0.62, 7.1),
    ("22H - 04H", 0.8, 6.0),
]
SIGN_X = 320.0

# ---------------------------------------------------------------- couleurs
# Une couleur = une chose. A decoder mot pour mot dans le prompt Genjutsu.
COL = {
    "bus": (1.0, 1.0, 1.0),  # BLANC   = le bus (sujet principal)
    "bus_front": (0.02, 0.02, 0.02),  # noir = pare-brise (donne le sens de marche)
    "bus_text": (0.05, 0.25, 0.08),  # vert fonce = lettrage du bus
    "wheel": (0.1, 0.1, 0.1),  # noir    = roues
    "seat": (0.0, 0.8, 0.8),  # CYAN    = sieges du bus
    "passenger": (1.0, 0.4, 0.7),  # ROSE = passagers
    "suitcase": (0.6, 0.33, 0.1),  # MARRON = valises (sur les genoux et sur le toit)
    "cloud_text": (0.75, 0.72, 0.9),  # lavande = lettres de nuage dans le ciel
    "logo": (1.0, 0.83, 0.0),  # JAUNE = logo Bubble sur le panneau
    "road": (0.25, 0.25, 0.27),  # gris fonce = chaussee du quai
    "dash": (0.8, 0.8, 0.8),  # gris clair = marquages et passages pietons
    "sidewalk": (0.6, 0.6, 0.62),  # gris moyen = trottoirs et promenade du lac
    "ground": (0.45, 0.45, 0.47),  # gris = sol de la ville
    "lake": (0.05, 0.35, 0.8),  # BLEU    = lac Leman
    "building": (0.85, 0.78, 0.62),  # BEIGE = immeubles haussmanniens
    "window": (0.15, 0.15, 0.2),  # anthracite = fenetres et balcons
    "roof": (0.3, 0.33, 0.42),  # ardoise = toits mansardes
    "trunk": (0.45, 0.28, 0.12),  # brun    = troncs des platanes
    "tree": (0.1, 0.7, 0.25),  # VERT     = feuillage des platanes
    "pole": (0.12, 0.12, 0.12),  # noir   = poteaux et boitiers des feux
    "red_light": (1.0, 0.0, 0.0),  # ROUGE VIF = feux rouges allumes
    "car": (0.7, 0.9, 0.1),  # VERT-JAUNE = voitures arretees au feu
    "jet": (0.85, 0.95, 1.0),  # blanc bleute = Jet d'Eau
    "mountain": (0.5, 0.55, 0.7),  # bleu-gris = montagnes au loin
    "rasta": (0.5, 0.1, 0.8),  # VIOLET  = la femme au telephone
    "sign": (0.03, 0.03, 0.03),  # NOIR    = panneau geant
    "sign_text": (1.0, 1.0, 1.0),  # blanc = texte et cadre du panneau
    "sign_post": (0.5, 0.5, 0.55),  # gris = poteaux du panneau
}
SKY = (0.45, 0.7, 0.95)


def frame_of(t):
    return 1 + t * FPS


def bus_x(frame):
    return BUS_SPEED * ((frame - 1) / FPS - INTRO)


# ---------------------------------------------------------------- geometrie
def new_obj(name, bm, color, loc=(0, 0, 0), parent=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.color = (*color, 1.0)
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def box(name, size, loc, color, parent=None):
    """Boite centree en XY, posee sur z = loc.z (base)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z = (v.co.z + 0.5) * sz
    return new_obj(name, bm, color, loc, parent)


def cone(name, r1, r2, depth, loc, color, segments=6, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2, depth=depth
    )
    for v in bm.verts:
        v.co.z += depth / 2
    return new_obj(name, bm, color, loc, parent)


def blob(name, radius, scale, loc, color):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=radius)  # lisse : sinon Genjutsu recopie les facettes
    for v in bm.verts:
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    return new_obj(name, bm, color, loc)


def empty(name, loc=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    return obj


def text(name, body, height, loc, rot, color, max_width=None, parent=None, puffy=False):
    """Texte 3D centre sur loc. height = hauteur approximative des capitales."""
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = height / 0.7
    curve.extrude = 0.01
    if puffy:  # lettres gonflees et arrondies, sans aretes : lues comme du nuage, pas de la pierre
        curve.extrude = 0.0
        curve.bevel_depth = height * 0.16
        curve.bevel_resolution = 4
        curve.offset = -height * 0.05
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = rot
    obj.color = (*color, 1.0)
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    if max_width:
        bpy.context.view_layer.update()
        width = obj.dimensions.x
        if width > max_width:
            s = max_width / width
            obj.scale = (s, s, s)
    return obj


# ---------------------------------------------------------------- decor
CROSS_X = 85.0  # carrefour ou le bus grille le feu rouge


def building(cx, w, h, front_y=9.0, depth=16.0, detailed=True):
    """Immeuble haussmannien : corps beige, toit mansarde, rangees de fenetres et balcons."""
    box("building", (w, depth, h), (cx, front_y + depth / 2, 0), COL["building"])
    box("roof", (w * 0.97, depth * 0.94, 3.2), (cx, front_y + depth / 2, h), COL["roof"])
    if not detailed:
        return
    bm = bmesh.new()

    def add(size, loc):
        geo = bmesh.ops.create_cube(bm, size=1.0)
        for v in geo["verts"]:
            v.co.x = v.co.x * size[0] + loc[0]
            v.co.y = v.co.y * size[1] + loc[1]
            v.co.z = v.co.z * size[2] + loc[2]

    cols = max(2, int(w / 2.6))
    step = w / cols
    floors = int((h - 5.0) / 3.3)
    for c in range(cols):
        x = cx - w / 2 + step * (c + 0.5)
        add((step * 0.7, 0.3, 3.0), (x, front_y, 2.1))  # vitrines du rez-de-chaussee
        for f in range(floors):
            add((1.1, 0.3, 2.0), (x, front_y, 6.4 + f * 3.3))
    for f in (0, floors - 1):  # balcons filants
        add((w, 0.7, 0.18), (cx, front_y - 0.3, 5.3 + f * 3.3))
    new_obj("window", bm, COL["window"])


def build_world():
    rnd = random.Random(7)
    x0, x1 = -150.0, 520.0
    length = x1 - x0
    cx = (x0 + x1) / 2

    # Lac cote -Y, promenade (-12..-4), chaussee (-4..4), trottoir (4..9), immeubles (y > 9)
    box("lake", (length + 2400, 1500, 0.1), (cx, -762, -0.8), COL["lake"])
    box("promenade", (length, 8, 0.15), (cx, -8, 0), COL["sidewalk"])
    box("railing", (length, 0.12, 1.0), (cx, -11.9, 0.15), COL["pole"])
    box("road", (length, 8, 0.1), (cx, 0, -0.05), COL["road"])
    box("sidewalk", (length, 5, 0.15), (cx, 6.5, 0), COL["sidewalk"])
    box("ground", (length + 800, 520, 0.1), (cx, 269, -0.1), COL["ground"])
    x = x0
    while x < x1:
        box("dash", (3.0, 0.2, 0.02), (x, 0, 0.05), COL["dash"])
        x += 8.0

    # Premiere rangee : facades haussmanniennes le long du quai, rue transversale au carrefour
    x = x0
    while x < x1:
        w = rnd.uniform(18, 28)
        if x < CROSS_X + 7 and x + w > CROSS_X - 7:  # laisse la rue transversale libre
            x = CROSS_X + 7.5
            continue
        if x < CROSS_X - 7 < x + w + 6:
            w = CROSS_X - 7.5 - x
        building(x + w / 2, w, rnd.uniform(19, 24))
        x += w + 0.5
    # Ilots de ville derriere, sans detail (vus seulement d'en haut)
    for row in range(1, 7):
        x = x0
        while x < x1:
            w = rnd.uniform(22, 40)
            if not (x < CROSS_X + 7 and x + w > CROSS_X - 7):
                building(x + w / 2, w, rnd.uniform(16, 24), front_y=9.0 + row * 34, depth=22, detailed=False)
            x += w + rnd.uniform(6, 12)
    box("cross_street", (14, 260, 0.1), (CROSS_X, 134, -0.03), COL["road"])

    # Platanes sur la promenade du lac
    x = x0
    while x < x1:
        if abs(x - CROSS_X) > 6 and abs(x - 186) > 9:  # degage le carrefour et la femme
            h = rnd.uniform(4.5, 6)
            cone("trunk", 0.3, 0.22, h, (x, -10.8, 0), COL["trunk"], segments=6)
            blob("tree", 1.0, (2.8, 2.8, 2.2), (x, -10.8, h + 1.3), COL["tree"])
        x += rnd.uniform(11, 15)

    # Carrefour : passages pietons, feux rouges face au bus, voitures a l'arret
    for zx in (CROSS_X - 10, CROSS_X + 10):
        for i in range(8):
            box("zebra", (3.0, 0.5, 0.02), (zx, -3.5 + i, 0.06), COL["dash"])
    # Portique de feux au-dessus de la chaussee : trois gros feux rouges bien visibles,
    # la camera passe dessous avec le bus. Aucun poteau sur la trajectoire de la camera.
    lx = CROSS_X - 8.0
    for py in (-5.2, 5.2):
        box("light_pole", (0.3, 0.3, 7.0), (lx, py, 0), COL["pole"])
        box("light_head", (0.45, 0.55, 1.4), (lx, py, 2.6), COL["pole"])
        box("red_light", (0.14, 0.42, 0.42), (lx - 0.28, py, 3.5), COL["red_light"])
    box("light_beam", (0.3, 10.7, 0.3), (lx, 0, 6.8), COL["pole"])
    for ly in (-2.6, 0.0, 2.6):
        box("light_head", (0.5, 0.8, 1.6), (lx, ly, 5.3), COL["pole"])
        box("red_light", (0.16, 0.62, 0.62), (lx - 0.32, ly, 6.15), COL["red_light"])
    for cy in (11.0, 17.5):  # dans la rue transversale, pretes a traverser
        box("car", (1.8, 4.3, 1.4), (CROSS_X - 2.0, cy, 0.1), COL["car"])

    # Au loin : Jet d'Eau dans la rade, rive opposee et montagnes
    cone("jet", 4.0, 0.6, 140.0, (330, -380, 0), COL["jet"], segments=8)
    box("far_shore", (length + 2400, 400, 6), (cx, -1700, 0), COL["tree"])
    for i in range(9):
        blob("mountain", 1.0, (rnd.uniform(260, 420), 200, rnd.uniform(140, 300)),
             (x0 - 700 + i * 280, -2000, 0), COL["mountain"])


def build_sign():
    """Panneau geant au-dessus de la route, face au trafic (tourne vers -X)."""
    w, z0, z1 = 7.4, 4.8, 14.8
    for py in (-4.6, 4.6):
        box("sign_post", (0.5, 0.5, z1), (SIGN_X + 0.3, py, 0), COL["sign_post"])
    box("sign_beam", (0.4, 9.7, 0.5), (SIGN_X + 0.3, 0, z0 - 0.5), COL["sign_post"])
    box("sign_board", (0.3, w, z1 - z0), (SIGN_X, 0, z0), COL["sign"])
    # cadre blanc
    fx = SIGN_X - 0.17
    for py in (-w / 2 + 0.15, w / 2 - 0.15):
        box("sign_frame", (0.04, 0.12, z1 - z0 - 0.3), (fx, py, z0 + 0.15), COL["sign_text"])
    for pz in (z0 + 0.15, z1 - 0.27):
        box("sign_frame", (0.04, w - 0.3, 0.12), (fx, 0, pz), COL["sign_text"])
    rot = (math.pi / 2, 0, -math.pi / 2)  # face a -X, se lit de gauche a droite
    for body, height, z in SIGN_LINES:
        color = COL["logo"] if body == "Bubble" else COL["sign_text"]
        text("sign_text", body, height, (SIGN_X - 0.2, 0, z), rot, color, max_width=6.3)


# ---------------------------------------------------------------- bus
BUS_L, BUS_W = 7.0, 2.3
FLOOR_Z, SILL_Z, HEAD_Z, ROOF_Z = 0.45, 1.35, 2.25, 2.75


def build_bus():
    """Bus creux : on peut entrer par les fenetres laterales et sortir par l'arriere."""
    root = empty("bus_root")
    c = COL["bus"]
    hl, hw = BUS_L / 2, BUS_W / 2
    box("bus_floor", (BUS_L, BUS_W, 0.12), (0, 0, FLOOR_Z - 0.12), c, parent=root)
    box("bus_roof", (BUS_L, BUS_W, 0.12), (0, 0, ROOF_Z - 0.12), c, parent=root)
    for side in (-1, 1):
        y = side * (hw - 0.04)
        box("bus_side_low", (BUS_L, 0.08, SILL_Z - FLOOR_Z), (0, y, FLOOR_Z), c, parent=root)
        box("bus_side_band", (BUS_L, 0.08, ROOF_Z - HEAD_Z), (0, y, HEAD_Z), c, parent=root)
        for px in (-3.44, -2.1, -0.7, 0.7, 2.1, 3.44):
            box("bus_pillar", (0.12, 0.08, HEAD_Z - SILL_Z), (px, y, SILL_Z), c, parent=root)
        # lettrage sur le bandeau, des deux cotes
        rot = (math.pi / 2, 0, 0) if side < 0 else (math.pi / 2, 0, math.pi)
        text(
            "bus_text", BUS_TEXT, 0.27, (0, side * (hw + 0.02), (HEAD_Z + ROOF_Z) / 2),
            rot, COL["bus_text"], max_width=BUS_L - 0.5, parent=root,
        )
    # avant plein avec pare-brise ; arriere ouvert a hauteur de fenetre
    box("bus_front_wall", (0.08, BUS_W, ROOF_Z - FLOOR_Z), (hl - 0.04, 0, FLOOR_Z), c, parent=root)
    box("bus_front", (0.08, 1.9, 0.9), (hl + 0.02, 0, 1.45), COL["bus_front"], parent=root)
    box("bus_rear_low", (0.08, BUS_W, SILL_Z - FLOOR_Z), (-hl + 0.04, 0, FLOOR_Z), c, parent=root)
    box("bus_rear_band", (0.08, BUS_W, ROOF_Z - HEAD_Z), (-hl + 0.04, 0, HEAD_Z), c, parent=root)
    for wx in (-2.3, 2.3):
        for wy in (-1.1, 1.1):
            box("wheel", (0.9, 0.3, 0.9), (wx, wy, 0.0), COL["wheel"], parent=root)

    # sieges et passagers de part et d'autre de l'allee centrale
    rnd = random.Random(3)
    sx = -2.9
    while sx < 2.0:
        for side in (-1, 1):
            y = side * 0.72
            box("seat", (0.45, 0.7, 0.42), (sx, y, FLOOR_Z), COL["seat"], parent=root)
            box("seat_back", (0.1, 0.7, 0.95), (sx - 0.22, y, FLOOR_Z), COL["seat"], parent=root)
            if rnd.random() < 0.8:
                box("passenger", (0.3, 0.42, 0.62), (sx, y, FLOOR_Z + 0.42), COL["passenger"], parent=root)
                box("passenger_head", (0.22, 0.22, 0.24), (sx + 0.02, y, FLOOR_Z + 1.04), COL["passenger"], parent=root)
                # valise sur les genoux
                box("suitcase", (0.16, 0.46, 0.32), (sx + 0.25, y, FLOOR_Z + 0.5), COL["suitcase"], parent=root)
                if rnd.random() < 0.4:  # bras leves : ils dansent
                    for ay in (-0.17, 0.17):
                        box("passenger_arm", (0.08, 0.08, 0.5), (sx + 0.05, y + ay, FLOOR_Z + 0.95), COL["passenger"], parent=root)
        sx += 0.95

    # galerie de toit chargee de valises et de malles
    lx = -2.9
    while lx < 2.6:
        lw, ld, lh = rnd.uniform(0.6, 1.0), rnd.uniform(0.5, 0.9), rnd.uniform(0.25, 0.5)
        box("suitcase", (lw, ld, lh), (lx, rnd.uniform(-0.45, 0.45), ROOF_Z), COL["suitcase"], parent=root)
        lx += lw + 0.15

    for f in range(1, N_FRAMES + 1):  # une cle par image : vitesse strictement constante
        root.location = (bus_x(f), BUS_Y, 0)
        root.keyframe_insert("location", frame=f)
    return root


# ---------------------------------------------------------------- rasta
RASTA_POS = Vector((186.5, -4.6, 0.0))
RASTA_CAM = Vector((185.4, -3.0, 1.65))  # ou se pose la camera pour le cadrer


def build_rasta():
    root = empty("rasta_root", RASTA_POS)
    box("rasta_body", (0.5, 0.35, 1.5), (0, 0, 0), COL["rasta"], parent=root)
    box("rasta_head", (0.3, 0.3, 0.3), (0.08, 0, 1.5), COL["rasta"], parent=root)
    box("rasta_hat", (0.45, 0.45, 0.25), (0, 0, 1.8), COL["rasta"], parent=root)
    arms = []
    for side in (-1, 1):
        arm = box("rasta_arm", (0.14, 0.14, 0.7), (0, 0, 0), COL["rasta"], parent=root)
        arm.location = (0, side * 0.3, 1.35)
        arm.rotation_euler = (math.pi, 0, 0)  # bras le long du corps
        arms.append((arm, side))

    # Il regarde le bus arriver (-X), le suit du regard (+X), puis se retourne vers la camera.
    t_pass = RASTA_POS.x / BUS_SPEED + INTRO
    to_cam = RASTA_CAM - RASTA_POS
    face_cam = math.atan2(to_cam.y, to_cam.x)
    for t, rz in [
        (0.0, math.pi),
        (t_pass - 0.5, math.pi),
        (t_pass + 0.1, math.pi / 2),
        (t_pass + 0.5, 0.2),
        (t_pass + 0.8, 0.2),
        (t_pass + 1.2, face_cam),
        (DURATION, face_cam),
    ]:
        root.rotation_euler = (0, 0, rz)
        root.keyframe_insert("rotation_euler", frame=frame_of(t))
    # Sursaut : petit recul + bras en l'air
    for t, dy, raised in (
        (t_pass - 0.6, 0.0, 0.0),
        (t_pass - 0.2, -0.4, 1.0),
        (t_pass + 2.0, -0.4, 1.0),
        (DURATION, -0.4, 0.7),
    ):
        root.location = RASTA_POS + Vector((0, dy, 0))
        root.keyframe_insert("location", frame=frame_of(t))
        for arm, side in arms:
            arm.rotation_euler = (math.pi - raised * side * 2.3, 0, 0)
            arm.keyframe_insert("rotation_euler", frame=frame_of(t))
    return root


# ---------------------------------------------------------------- camera
def bus_at(t):
    return Vector((BUS_SPEED * (t - INTRO), BUS_Y, 0.0))


def camera_keys():
    """(temps s, position camera, point vise) en coordonnees monde."""
    r = RASTA_POS
    head = (r.x, r.y - 0.4, 1.65)
    k = []

    def rel(t, cam_off, tgt_off):  # t = temps apres l'intro
        b = bus_at(t + INTRO)
        k.append((t + INTRO, b + Vector(cam_off), b + Vector(tgt_off)))

    def world(t, cam, tgt):
        k.append((t + INTRO, Vector(cam), Vector(tgt)))

    # intro : approche lente du nuage de lettres, tres haut dans le ciel
    b0 = bus_at(0.0)
    k.append((0.0, b0 + Vector((-36, -28, 192)), b0 + Vector((4, 0, 1))))
    # plongee, toit, flanc
    rel(0.0, (-30, -22, 150), (4, 0, 1))
    rel(1.2, (-22, -12, 78), (5, 0, 1))
    rel(2.5, (-9, -1.5, 9.5), (4, 0, 2.2))
    # reste au-dessus du toit, regard vers l'avant : feux rouges droit devant,
    # le bus passe sous le portique a 3,85 s sans freiner
    rel(3.3, (-5.0, -0.3, 4.7), (10, 0, 3.0))
    rel(4.0, (-3.5, -0.5, 4.4), (10, 0, 2.6))
    rel(4.4, (0.8, -3.2, 3.4), (7, 0.5, 1.6))
    # travelling lateral cote lac : lettrage + facades
    rel(5.0, (6.0, -6.6, 1.7), (0.3, 0, 1.7))
    rel(5.8, (5.0, -6.6, 1.7), (0.0, 0, 1.8))
    # approche et entree par la fenetre avant droite
    rel(6.5, (4.2, -4.0, 1.9), (0.5, 0, 1.8))
    rel(7.0, (3.15, -1.7, 1.93), (-2.0, 0.3, 1.8))
    rel(7.3, (2.75, -0.95, 1.93), (-6.0, 0.2, 1.7))
    # traversee de l'allee, regard vers l'arriere, sortie par la lunette arriere
    rel(7.7, (1.8, 0.0, 1.9), (-10, 0, 1.6))
    rel(8.3, (-0.6, 0.0, 1.9), (-10, 0, 1.6))
    rel(8.9, (-3.0, 0.0, 1.9), (-10, 0, 1.6))
    rel(9.15, (-4.0, 0.0, 1.9), (-10, -1.5, 1.6))
    # pivot par le cote mer vers le rasta, qui se retourne vers la camera
    world(9.5, (182.3, 0.2, 1.8), (180.5, -10, 1.5))
    world(9.9, (184.2, -1.2, 1.68), head)
    world(10.4, (RASTA_CAM.x, RASTA_CAM.y, RASTA_CAM.z), head)
    world(11.1, (RASTA_CAM.x + 0.3, RASTA_CAM.y - 0.1, RASTA_CAM.z), head)
    # repart vers l'avant, depasse le bus par au-dessus, fonce sur le panneau
    world(11.6, (189.5, 0.0, 2.4), (232, 1, 3))
    world(12.3, (236, 0.0, 5.5), (SIGN_X, 0, 9.5))
    world(13.1, (SIGN_X - 17, 0.0, 9.4), (SIGN_X, 0, 9.8))  # arrive tot : le panneau remplit deja le cadre
    world(14.0, (SIGN_X - 6.8, 0.0, 9.8), (SIGN_X, 0, 9.8))  # puis poussee lente
    return k


def hermite(keys, t, idx):
    """Interpolation cubique monotone (sans depassement) de la composante idx.

    Tangentes de Catmull-Rom, bridees composante par composante : nulles quand la
    valeur fait une pause ou change de sens, sinon limitees a 3x la pente voisine.
    Evite que la camera "prenne son elan" a l'envers avant une acceleration.
    """
    n = len(keys)
    i = 0
    while i < n - 2 and t > keys[i + 1][0]:
        i += 1
    t0, t1 = keys[i][0], keys[i + 1][0]
    p0, p1 = keys[i][idx], keys[i + 1][idx]

    def slope(a, b):
        return (keys[b][idx] - keys[a][idx]) / (keys[b][0] - keys[a][0])

    def tangent(j):
        if j == 0:
            return slope(0, 1)
        if j == n - 1:
            return slope(n - 2, n - 1)
        d0, d1, m = slope(j - 1, j), slope(j, j + 1), slope(j - 1, j + 1)
        out = Vector((0.0, 0.0, 0.0))
        for c in range(3):
            if d0[c] * d1[c] > 0:
                lim = 3 * min(abs(d0[c]), abs(d1[c]))
                out[c] = max(-lim, min(lim, m[c]))
        return out

    m0, m1 = tangent(i), tangent(i + 1)
    dt = t1 - t0
    s = min(max((t - t0) / dt, 0.0), 1.0)
    h00 = 2 * s**3 - 3 * s**2 + 1
    h10 = s**3 - 2 * s**2 + s
    h01 = -2 * s**3 + 3 * s**2
    h11 = s**3 - s**2
    return h00 * p0 + h10 * dt * m0 + h01 * p1 + h11 * dt * m1


def build_camera():
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 16
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 36
    cam_data.clip_start = 0.05
    cam_data.clip_end = 6000
    cam = bpy.data.objects.new("cam", cam_data)
    cam.rotation_mode = "QUATERNION"
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    keys = camera_keys()
    prev_q = None
    for f in range(1, N_FRAMES + 1):
        t = (f - 1) / FPS
        pos = hermite(keys, t, 1)
        tgt = hermite(keys, t, 2)
        pos.z = max(pos.z, 0.5)
        q = (tgt - pos).to_track_quat("-Z", "Y")
        if prev_q is not None and q.dot(prev_q) < 0:
            q.negate()
        prev_q = q.copy()
        cam.location = pos
        cam.rotation_quaternion = q
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
    return cam


def build_cloud_text():
    """Lettres de nuage "GENEVA ARE YOU READY?" placees sur la trajectoire de la camera."""
    keys = camera_keys()
    t_hit = INTRO + 0.4  # instant ou la camera traverse les lettres
    pos = hermite(keys, t_hit, 1)
    aim = hermite(keys, 0.8, 2) - hermite(keys, 0.8, 1)
    root = empty("cloud_text_root", pos)
    root.rotation_mode = "QUATERNION"
    root.rotation_quaternion = aim.to_track_quat("-Z", "Y")  # face a la camera
    for body, height, dy in CLOUD_LINES:
        obj = text("cloud_text", body, height, (0, dy, 0), (0, 0, 0), COL["cloud_text"], max_width=34, parent=root, puffy=True)
        # disparait une fois traverse, pour ne pas reapparaitre a l'envers dans le ciel
        for f, hidden in ((1, False), (int(frame_of(t_hit)) + 2, True)):
            obj.hide_render = hidden
            obj.keyframe_insert("hide_render", frame=f)
    return root


# ---------------------------------------------------------------- rendu
def setup_render(scene, res):
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = N_FRAMES
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
    except TypeError:
        print("Workbench indisponible, rendu avec", scene.render.engine)
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_shadows = False
    sh.show_cavity = True
    sh.show_object_outline = True
    sh.background_type = "WORLD"
    world = bpy.data.worlds.new("sky")
    world.color = SKY
    scene.world = world
    scene.view_settings.view_transform = "Standard"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False


def main():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    ap.add_argument("--stills", default="")
    ap.add_argument("--res", default="720x1280")
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=N_FRAMES)
    args = ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    res = tuple(int(v) for v in args.res.split("x"))
    setup_render(scene, res)
    build_world()
    build_sign()
    build_bus()
    build_rasta()
    build_camera()
    build_cloud_text()

    out = os.path.abspath(args.out)
    if args.stills:
        frames = [int(v) for v in args.stills.split(",")]
        sub = "stills"
    else:
        frames = range(args.start, args.end + 1, args.step)
        sub = "frames"
    os.makedirs(os.path.join(out, sub), exist_ok=True)
    for f in frames:
        path = os.path.join(out, sub, f"f{f:04d}.png")
        if os.path.exists(path):
            continue
        scene.frame_set(f)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
    print("TERMINE", len(list(frames)), "images ->", os.path.join(out, sub))


if __name__ == "__main__":
    main()
