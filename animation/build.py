"""Blockout Blender : bus jamaicain, plongee du ciel -> travelling -> rasta -> 180 vers le ciel.

Formes grossieres, une couleur par chose, un seul mouvement de camera continu.
Sert de "Video 1" (camera, timing, placement) pour Higgsfield Genjutsu.

Lancer :
    blender -b -P build.py -- --out out
ou, avec le module Python de Blender :
    python build.py --out out
Options : --stills 1,75,135   (images de controle seulement)
          --res 720x1280      --step 1
Les images sortent dans <out>/frames ; assembler avec ffmpeg (voir README).
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
DURATION = 12.0
N_FRAMES = int(FPS * DURATION)  # 360
BUS_SPEED = 20.0  # m/s, le long de +X

# ---------------------------------------------------------------- couleurs
# Une couleur = une chose. A decoder mot pour mot dans le prompt Genjutsu.
COL = {
    "bus": (1.0, 1.0, 1.0),  # BLANC   = le bus (sujet principal)
    "bus_front": (0.02, 0.02, 0.02),  # noir = pare-brise (donne le sens de marche)
    "wheel": (0.1, 0.1, 0.1),  # noir    = roues
    "road": (0.25, 0.25, 0.27),  # gris    = route goudronnee
    "dash": (0.8, 0.8, 0.8),  # gris clair = ligne centrale
    "sand": (0.93, 0.85, 0.55),  # jaune pale = plage
    "sea": (0.05, 0.35, 0.8),  # bleu    = mer
    "land": (0.25, 0.5, 0.2),  # vert    = vegetation au sol
    "hill": (0.1, 0.3, 0.12),  # vert fonce = collines
    "trunk": (0.45, 0.28, 0.12),  # brun    = troncs de palmiers
    "palm": (0.1, 0.7, 0.25),  # vert vif = feuillage des palmiers
    "stand": (1.0, 0.45, 0.0),  # ORANGE  = stands de fruits
    "stand_roof": (0.9, 0.1, 0.6),  # MAGENTA = toits des stands
    "rasta": (0.5, 0.1, 0.8),  # VIOLET  = le rasta
    "cloud": (0.75, 0.72, 0.9),  # lavande = nuages
}
SKY = (0.45, 0.7, 0.95)


def frame_of(t):
    return 1 + t * FPS


def bus_x(frame):
    return BUS_SPEED * (frame - 1) / FPS


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
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius)
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


# ---------------------------------------------------------------- scene
def build_world():
    rnd = random.Random(7)
    x0, x1 = -150.0, 450.0
    length = x1 - x0
    cx = (x0 + x1) / 2

    # Sol : mer (y < -34), plage (-34..-4), route (-4..4), terre (y > 4)
    box("sea", (length + 800, 900, 0.1), (cx, -484, -0.3), COL["sea"])
    box("sand", (length, 30, 0.1), (cx, -19, -0.12), COL["sand"])
    box("road", (length, 8, 0.1), (cx, 0, -0.05), COL["road"])
    box("land", (length + 800, 500, 0.1), (cx, 254, -0.1), COL["land"])
    x = x0
    while x < x1:
        box("dash", (3.0, 0.2, 0.02), (x, 0, 0.05), COL["dash"])
        x += 8.0

    # Collines au fond, cote terre
    for i in range(14):
        hx = x0 + i * (length / 13) + rnd.uniform(-15, 15)
        blob(
            "hill",
            1.0,
            (rnd.uniform(40, 70), rnd.uniform(30, 50), rnd.uniform(14, 30)),
            (hx, rnd.uniform(90, 140), 0),
            COL["hill"],
        )

    # Palmiers : denses cote terre, clairsemes sur la plage (hors trajet camera)
    def palm(px, py):
        h = rnd.uniform(6, 11)
        cone("trunk", 0.28, 0.18, h, (px, py, 0), COL["trunk"], segments=5)
        cone("palm", 3.2, 0.3, 1.6, (px, py, h - 0.4), COL["palm"], segments=7)

    x = x0
    while x < x1:
        palm(x + rnd.uniform(-2, 2), rnd.uniform(13, 20))
        palm(x + rnd.uniform(-4, 4), rnd.uniform(24, 45))
        x += rnd.uniform(5, 9)
    x = x0
    while x < x1:
        palm(x + rnd.uniform(-4, 4), rnd.uniform(-26, -14))
        x += rnd.uniform(22, 38)

    # Stands de fruits : bord de route cote terre, serres pendant le travelling
    x = 78.0
    while x < 172.0:
        sy = 7.6 + rnd.uniform(-0.4, 0.4)
        box("stand", (3.0, 1.6, 1.1), (x, sy, 0), COL["stand"])
        box("stand_roof", (3.6, 2.4, 0.15), (x, sy, 2.3), COL["stand_roof"])
        for dx in (-1.6, 1.6):
            box("stand_post", (0.1, 0.1, 2.3), (x + dx, sy - 1.0, 0), COL["stand"])
        x += rnd.uniform(6.5, 9.5)

    # Nuages : traverses pendant la plongee, et fond du plan final
    clouds = [
        (-25, -30, 95, 22), (20, 25, 80, 18), (-5, -55, 60, 16), (60, 30, 70, 20),
        (120, -90, 75, 26), (60, -140, 90, 30), (190, -120, 110, 34),
        (0, -200, 120, 40), (110, -230, 150, 45), (230, -60, 85, 24),
    ]
    for cxx, cyy, czz, r in clouds:
        blob("cloud", 1.0, (r, r * 0.7, r * 0.28), (cxx, cyy, czz), COL["cloud"])


def build_bus():
    root = empty("bus_root")
    y = 1.0  # roule a gauche (Jamaique), cote terre
    box("bus_body", (7.0, 2.3, 2.3), (0, 0, 0.45), COL["bus"], parent=root)
    box("bus_front", (0.08, 1.9, 0.9), (3.52, 0, 1.6), COL["bus_front"], parent=root)
    for wx in (-2.3, 2.3):
        for wy in (-1.1, 1.1):
            box("wheel", (0.9, 0.3, 0.9), (wx, wy, 0.0), COL["wheel"], parent=root)
    for f in range(1, N_FRAMES + 1):  # une cle par image : vitesse strictement constante
        root.location = (bus_x(f), y, 0)
        root.keyframe_insert("location", frame=f)
    return root


RASTA_POS = Vector((176.0, -5.0, 0.0))


def build_rasta():
    root = empty("rasta_root", RASTA_POS)
    box("rasta_body", (0.5, 0.35, 1.5), (0, 0, 0), COL["rasta"], parent=root)
    box("rasta_head", (0.3, 0.3, 0.3), (0.08, 0, 1.5), COL["rasta"], parent=root)
    box("rasta_hat", (0.45, 0.45, 0.25), (0, 0, 1.8), COL["rasta"], parent=root)
    arms = []
    for side in (-1, 1):
        arm = box("rasta_arm", (0.14, 0.14, 0.7), (0, side * 0.3, 0), COL["rasta"], parent=root)
        arm.location = (0, side * 0.3, 1.35)
        arm.rotation_euler = (math.pi, 0, 0)  # bras le long du corps
        arms.append((arm, side))

    # Il regarde le bus arriver (face a -X), sursaute, puis le suit du regard (+X).
    t_pass = (RASTA_POS.x - 0) / BUS_SPEED  # instant ou le bus le croise
    keys = [
        (0.0, math.pi),
        (t_pass - 0.5, math.pi),
        (t_pass + 0.5, math.pi / 2),
        (t_pass + 1.3, 0.25),
        (DURATION, 0.1),
    ]
    for t, rz in keys:
        root.rotation_euler = (0, 0, rz)
        root.keyframe_insert("rotation_euler", frame=frame_of(t))
    # Sursaut : petit recul + bras en l'air
    for t, dy, raised in (
        (t_pass - 0.6, 0.0, 0.0),
        (t_pass - 0.2, -0.5, 1.0),
        (t_pass + 1.6, -0.6, 1.0),
        (DURATION, -0.6, 0.6),
    ):
        root.location = RASTA_POS + Vector((0, dy, 0))
        root.keyframe_insert("location", frame=frame_of(t))
        for arm, side in arms:
            arm.rotation_euler = (math.pi - raised * side * 2.3, 0, 0)
            arm.keyframe_insert("rotation_euler", frame=frame_of(t))
    return root


# ---------------------------------------------------------------- camera
def bus_at(t):
    return Vector((BUS_SPEED * t, 1.0, 0.0))


def camera_keys():
    """(temps s, position camera, point vise) en coordonnees monde.

    0.0-2.5  plongee du ciel vers le bus
    2.5-4.0  rase le toit, dans l'axe de la route
    4.0-5.0  glisse sur le cote (cote mer), a hauteur de fenetre
    5.0-7.8  travelling lateral : les stands defilent derriere le bus
    7.8-9.6  la camera lache le bus et cadre le rasta, le bus file au fond
    9.6-12.0 demi-tour (180) vers la mer et montee dans le ciel
    """
    r = RASTA_POS
    k = []

    def rel(t, cam_off, tgt_off):
        b = bus_at(t)
        k.append((t, b + Vector(cam_off), b + Vector(tgt_off)))

    def world(t, cam, tgt):
        k.append((t, Vector(cam), Vector(tgt)))

    rel(0.0, (-30, -22, 150), (4, 0, 1))
    rel(1.2, (-22, -12, 78), (5, 0, 1))
    rel(2.5, (-9, -1.5, 9.5), (4, 0, 2.2))
    rel(3.3, (-3.5, -1.0, 4.4), (9, 0, 1.5))
    rel(4.0, (1.0, -3.0, 3.6), (8, 0.5, 1.5))
    rel(5.0, (6.5, -7.5, 1.6), (0.5, 0, 1.5))
    rel(6.4, (5.5, -7.8, 1.5), (0.0, 0, 1.5))
    rel(7.6, (3.0, -8.0, 1.5), (0.5, 0, 1.5))
    world(8.6, (r.x - 5.2, r.y - 2.6, 1.55), (r.x, r.y, 1.55))
    world(9.5, (r.x - 3.6, r.y - 2.9, 1.6), (r.x + 0.5, r.y, 1.6))
    world(10.2, (r.x - 4.5, r.y - 6.0, 4.0), (r.x - 2, r.y - 40, 6))
    world(11.0, (r.x - 6.5, r.y - 10.0, 16.0), (r.x - 60, r.y - 70, 50))
    world(12.0, (r.x - 9.0, r.y - 14.0, 42.0), (r.x - 90, r.y - 110, 190))
    return k


def hermite(keys, t, idx):
    """Interpolation Catmull-Rom (temps non uniformes) de la composante idx."""
    n = len(keys)
    i = 0
    while i < n - 2 and t > keys[i + 1][0]:
        i += 1
    t0, t1 = keys[i][0], keys[i + 1][0]
    p0, p1 = keys[i][idx], keys[i + 1][idx]

    def tangent(j):
        a = max(j - 1, 0)
        b = min(j + 1, n - 1)
        return (keys[b][idx] - keys[a][idx]) / (keys[b][0] - keys[a][0])

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
    cam_data.clip_start = 0.1
    cam_data.clip_end = 3000
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
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    scene = bpy.context.scene
    res = tuple(int(v) for v in args.res.split("x"))
    setup_render(scene, res)
    build_world()
    build_bus()
    build_rasta()
    build_camera()

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
