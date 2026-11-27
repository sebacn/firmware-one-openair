#!/usr/bin/env python3
"""Assembly of the modular monitor on the original outdoor shells.

Part B and Part C are the AirGradient STLs. The grill is the original Part A
with its interior reworked. Component boxes are the rev D parts.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parent
REF = ROOT / "reference-outdoor"
RENDERS = ROOT / "renders"

# xy centre, xy size, height above the grill's top face. Sensor faces point down.
PARTS = [
    ("SPS30", "#1f6feb", (0.0, 26.5), (40.6, 12.2), 40.6),
    ("ESP32", "#6b4c9a", (0.0, 2.0), (13.0, 28.0), 58.0),
    ("SCD30", "#e07a3d", (20.0, 1.5), (23.0, 35.0), 7.0),
    ("SHT45", "#1f9d55", (-24.0, 3.0), (17.8, 25.3), 4.8),
    ("SGP41", "#d4a017", (-10.0, -23.0), (25.4, 17.8), 4.8),
    ("M8", "#1a1a1a", (12.0, -25.5), (16.0, 16.0), 8.0),
]


def box_mesh(center, size):
    c = np.asarray(center, float)
    s = np.asarray(size, float) / 2
    corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    verts = c + corners * s
    faces = [
        [0, 1, 3, 2],
        [4, 6, 7, 5],
        [0, 4, 5, 1],
        [2, 3, 7, 6],
        [0, 2, 6, 4],
        [1, 5, 7, 3],
    ]
    tri = np.array(faces)
    return trimesh.Trimesh(
        vertices=verts,
        faces=tri[:, [0, 1, 2]].tolist() + tri[:, [0, 2, 3]].tolist(),
    )


def add_mesh(ax, mesh, color, alpha=1.0, limit=14000):
    if mesh.is_empty:
        return
    tri = mesh.triangles
    if len(tri) > limit:
        idx = np.linspace(0, len(tri) - 1, limit).astype(int)
        tri = tri[idx]
    pc = Poly3DCollection(tri, alpha=alpha, linewidths=0)
    pc.set_facecolor(color)
    pc.set_edgecolor((0, 0, 0, 0))
    ax.add_collection3d(pc)


def scene_bounds(meshes):
    lo = np.min([m.bounds[0] for m in meshes], axis=0)
    hi = np.max([m.bounds[1] for m in meshes], axis=0)
    return lo, hi


def paint(mesh, hexcolor, alpha=255):
    rgb = matplotlib.colors.to_rgb(hexcolor)
    mesh.visual.face_colors = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), alpha]
    return mesh


def _flip_roof_up(mesh):
    mesh = mesh.copy()
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    transform = np.eye(4)
    transform[1, 1] = -1.0
    transform[2, 2] = -1.0
    transform[1, 3] = 2 * center[1]
    transform[2, 3] = 2 * center[2]
    mesh.apply_transform(transform)
    return mesh


def load_shells():
    base = trimesh.load(REF / "AirGradient Outdoor DIY Bottom Part B.stl", force="mesh")
    origin = np.array([
        -(base.bounds[0, 0] + base.bounds[1, 0]) / 2,
        -(base.bounds[0, 1] + base.bounds[1, 1]) / 2,
        -base.bounds[0, 2],
    ])
    base.apply_translation(origin)
    grill = trimesh.load(ROOT / "grill-modular.stl", force="mesh")
    grill.apply_translation(origin)
    cover = trimesh.load(REF / "AirGradient Outdoor DIY Top Part C.stl", force="mesh")
    cb = cover.bounds.copy()
    cover.apply_translation([1.15, 0.0, 3.06 - cb[0, 2]])
    cover = _flip_roof_up(cover)
    return base, grill, cover


def part_records(plate_top):
    out = []
    for name, color, xy, size, height in PARTS:
        center = (xy[0], xy[1], plate_top + height / 2)
        full = (size[0], size[1], height)
        out.append((name, color, center, full, box_mesh(center, full)))
    return out


def _gap(a, sa, b, sb):
    dx = abs(a[0] - b[0]) - (sa[0] + sb[0]) / 2
    dy = abs(a[1] - b[1]) - (sa[1] + sb[1]) / 2
    if dx < 0 and dy < 0:
        return max(dx, dy)
    if dx < 0:
        return dy
    if dy < 0:
        return dx
    return min(dx, dy)


def clearances(base, grill, cover, plate_top):
    print("part gaps mm")
    for i in range(len(PARTS)):
        for j in range(i + 1, len(PARTS)):
            n1, _, a, s1, _ = PARTS[i]
            n2, _, b, s2, _ = PARTS[j]
            g = _gap(a, s1, b, s2)
            if g < 8:
                print(f"  {n1:6} {n2:6} {g:6.2f}")
    print("clearance to original shells mm (sampled)")
    for name, _, xy, size, height in PARTS:
        xs = np.linspace(xy[0] - size[0] / 2 + 0.3, xy[0] + size[0] / 2 - 0.3, 6)
        ys = np.linspace(xy[1] - size[1] / 2 + 0.3, xy[1] + size[1] / 2 - 0.3, 6)
        zs = np.linspace(plate_top + 0.5, plate_top + height - 0.3, 8)
        pts = np.array([(x, y, z) for z in zs for y in ys for x in xs])
        ib = int(base.contains(pts).sum())
        ic = int(cover.contains(pts).sum())
        ig = int(grill.contains(pts).sum())
        db = float(trimesh.proximity.closest_point(base, pts)[1].min())
        dc = float(trimesh.proximity.closest_point(cover, pts)[1].min())
        print(f"  {name:6} base {db:5.2f} (inside {ib})  cover {dc:5.2f} (inside {ic})  grill inside {ig}")


def scene(base, grill, cover, records, exploded=False):
    if exploded:
        grill = grill.copy()
        cover = cover.copy()
        grill.apply_translation([0, 0, -34])
        cover.apply_translation([0, 0, 52])
    out = trimesh.Scene()
    paint(base, "#d5dde4", 230)
    paint(grill, "#243447", 255)
    paint(cover, "#9bb0c2", 70)
    out.add_geometry(base, node_name="Base", geom_name="Base")
    out.add_geometry(grill, node_name="Grill", geom_name="Grill")
    out.add_geometry(cover, node_name="Cover", geom_name="Cover")
    for name, color, center, full, mesh in records:
        paint(mesh, color, 255)
        out.add_geometry(mesh, node_name=name, geom_name=name)
    return out


def frame(path, base, grill, cover, records, view, elev, azim, exploded=False, section=False):
    if exploded:
        grill = grill.copy()
        cover = cover.copy()
        grill.apply_translation([0, 0, -34])
        cover.apply_translation([0, 0, 52])
    if section:
        keep = cover.triangles_center[:, 0] > -6
        cover = trimesh.Trimesh(vertices=cover.vertices, faces=cover.faces[keep], process=False)
        keep = base.triangles_center[:, 0] > -6
        base = trimesh.Trimesh(vertices=base.vertices, faces=base.faces[keep], process=False)
    fig = plt.figure(figsize=(13.2, 10.2), facecolor="#eef1f4")
    ax = fig.add_subplot(111, projection="3d", facecolor="#eef1f4")
    add_mesh(ax, base, "#c5d0da", 0.55 if section else 0.9, limit=8000)
    add_mesh(ax, grill, "#1e2a38", 1.0, limit=22000)
    add_mesh(ax, cover, "#7f97ab", 0.18 if not section else 0.30, limit=9000)
    for name, color, center, full, mesh in records:
        add_mesh(ax, mesh, color, 1.0, limit=2000)
        ax.text(
            center[0], center[1], center[2] + full[2] / 2 + 1.6, name,
            fontsize=11, color="#102030",
        )
    lo, hi = scene_bounds([base, cover, grill])
    pad = 18 if exploded else 2
    span = (hi - lo).max() / 2 + pad
    mid = (lo + hi) / 2
    ax.set_xlim(mid[0] - span, mid[0] + span)
    ax.set_ylim(mid[1] - span, mid[1] + span)
    ax.set_zlim(mid[2] - span * 0.45, mid[2] + span * 0.7)
    ax.set_box_aspect((1.15, 1.15, 0.95))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("render", path.name)


def main():
    base, grill, cover = load_shells()
    plate_top = float(grill.bounds[1, 2])
    print("plate top", round(plate_top, 3))
    records = part_records(plate_top)
    clearances(base, grill, cover, plate_top)
    built = scene(base, grill, cover, records, exploded=False)
    path = ROOT / "assembly" / "modular.glb"
    built.export(path)
    print("glb", path.stat().st_size)
    frame(RENDERS / "modular-front.png", base, grill, cover, records, "front", 0, 0)
    frame(RENDERS / "modular-side.png", base, grill, cover, records, "side", 0, -90)
    frame(RENDERS / "modular-top.png", base, grill, cover, records, "top", 90, -90)
    frame(RENDERS / "modular-section.png", base, grill, cover, records, "section", 16, -62, section=True)
    frame(RENDERS / "modular-exploded.png", base, grill, cover, records, "exploded", 20, -58, exploded=True)


if __name__ == "__main__":
    main()
