#!/usr/bin/env python3
"""Assembly of the USB-only modular monitor in the original outdoor shells.

The cover and the base ring are the AirGradient STLs. The carrier replaces
the grill. Component boxes are the rev D parts: no battery, no charger.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

from render_variants import add_mesh, box_mesh, paint, scene_bounds

ROOT = Path(__file__).resolve().parent
REF = ROOT / "reference-outdoor"
RENDERS = ROOT / "renders"

# xy centre, xy size, (z0, z1). Plate top is z = 5.2.
PARTS = [
    ("SPS30", "#3d8bfd", (0.0, 28.0), (40.6, 12.2), (6.7, 47.3)),
    ("ESP32", "#6b4c9a", (0.0, -10.0), (28.0, 13.0), (6.5, 64.5)),
    ("SCD30", "#e07a3d", (3.0, 9.5), (35.0, 23.0), (12.2, 19.2)),
    ("SHT45", "#2fbf71", (-25.0, 8.0), (17.8, 25.3), (12.2, 17.0)),
    ("SGP41", "#f2c14e", (0.0, -27.0), (25.3, 17.8), (12.2, 17.0)),
    ("M8", "#2b2b2b", (22.0, -4.0), (14.0, 14.0), (5.2, 11.0)),
]


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
    cover = trimesh.load(REF / "AirGradient Outdoor DIY Top Part C.stl", force="mesh")
    bounds = base.bounds
    base.apply_translation([
        -(bounds[0, 0] + bounds[1, 0]) / 2,
        -(bounds[0, 1] + bounds[1, 1]) / 2,
        -bounds[0, 2],
    ])
    cb = cover.bounds
    cover.apply_translation([1.15, 0.0, 3.06 - cb[0, 2]])
    # The published cover mesh has its cap at the low end. Turn that cap up.
    cover = _flip_roof_up(cover)
    carrier = trimesh.load(ROOT / "carrier" / "carrier.stl", force="mesh")
    return base, carrier, cover


def part_boxes():
    out = []
    for name, color, xy, size, z in PARTS:
        center = (xy[0], xy[1], (z[0] + z[1]) / 2)
        full = (size[0], size[1], z[1] - z[0])
        out.append((name, color, center, full, box_mesh(center, full)))
    return out


def _aabb(center, size):
    c = np.asarray(center, float)
    h = np.asarray(size, float) / 2
    return c - h, c + h


def clearances():
    rows = []
    boxes = []
    for name, color, xy, size, z in PARTS:
        center = (xy[0], xy[1], (z[0] + z[1]) / 2)
        full = (size[0], size[1], z[1] - z[0])
        boxes.append((name, _aabb(center, full)))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            n1, (a, b) = boxes[i]
            n2, (c, d) = boxes[j]
            pen = np.minimum(b, d) - np.maximum(a, c)
            if np.all(pen > 0):
                rows.append((n1, n2, -float(pen.min())))
            else:
                gaps = []
                for k in range(3):
                    if b[k] < c[k]:
                        gaps.append(c[k] - b[k])
                    elif d[k] < a[k]:
                        gaps.append(a[k] - d[k])
                    else:
                        gaps.append(0.0)
                positive = [g for g in gaps if g > 0]
                rows.append((n1, n2, min(positive) if len(positive) == 1 else min(g for g in gaps if g > 0) if positive else 0))
    return rows


def shell_hits(base, carrier, cover):
    hits = []
    for name, color, xy, size, z in PARTS:
        center = (xy[0], xy[1], (z[0] + z[1]) / 2)
        full = (size[0], size[1], z[1] - z[0])
        lo, hi = _aabb(center, full)
        pts = []
        for x in np.linspace(lo[0], hi[0], 4):
            for y in np.linspace(lo[1], hi[1], 4):
                for zz in np.linspace(lo[2], hi[2], 4):
                    pts.append((x, y, zz))
        pts = np.array(pts)
        for label, mesh in (("base", base), ("carrier", carrier), ("cover", cover)):
            n = int(mesh.contains(pts).sum())
            if n:
                hits.append((name, label, n, len(pts)))
    return hits


def scene(exploded=False):
    base, carrier, cover = load_shells()
    if exploded:
        carrier.apply_translation([0, 0, -30])
        cover.apply_translation([0, 0, 55])
    out = trimesh.Scene()
    paint(base, "#c5ccd3", 220)
    paint(carrier, "#9aa3ad", 235)
    paint(cover, "#d9dde3", 100)
    out.add_geometry(base, node_name="Base", geom_name="Base")
    out.add_geometry(carrier, node_name="Carrier", geom_name="Carrier")
    out.add_geometry(cover, node_name="Cover", geom_name="Cover")
    for name, color, center, full, mesh in part_boxes():
        paint(mesh, color, 255)
        out.add_geometry(mesh, node_name=name, geom_name=name)
    return out


def frame(path, view, elev, azim, exploded=False, section=False):
    base, carrier, cover = load_shells()
    if exploded:
        carrier.apply_translation([0, 0, -30])
        cover.apply_translation([0, 0, 55])
    if section:
        keep = cover.triangles_center[:, 0] > -8
        cover = trimesh.Trimesh(vertices=cover.vertices, faces=cover.faces[keep], process=False)
        keep = base.triangles_center[:, 0] > -8
        base = trimesh.Trimesh(vertices=base.vertices, faces=base.faces[keep], process=False)
    fig = plt.figure(figsize=(8.2, 6.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, base, "#c5ccd3", 0.85)
    add_mesh(ax, carrier, "#8e99a4", 0.95)
    add_mesh(ax, cover, "#d9dde3", 0.2 if not section else 0.55)
    for name, color, center, full, mesh in part_boxes():
        add_mesh(ax, mesh, color, 1)
        ax.text(center[0], center[1], center[2] + full[2] / 2 + 1.5, name, fontsize=7)
    lo, hi = scene_bounds([base, cover, carrier])
    span = (hi - lo).max() / 2 + (26 if exploded else 8)
    mid = (lo + hi) / 2
    ax.set_xlim(mid[0] - span, mid[0] + span)
    ax.set_ylim(mid[1] - span, mid[1] + span)
    ax.set_zlim(mid[2] - span, mid[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(f"Modular carrier — {view}", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    base, carrier, cover = load_shells()
    print("clearances mm (negative is an overlap)")
    for a, b, gap in clearances():
        print(f"  {a:8} {b:8} {gap:6.1f}")
    print("samples inside shell plastic")
    for name, label, n, total in shell_hits(base, carrier, cover):
        print(f"  {name:8} in {label:8} {n}/{total}")
    built = scene(False)
    path = ROOT / "assembly" / "modular.glb"
    built.export(path)
    print("glb", path.stat().st_size)
    frame(RENDERS / "modular-front.png", "front", 0, 0)
    frame(RENDERS / "modular-side.png", "side", 0, -90)
    frame(RENDERS / "modular-top.png", "top", 90, 0)
    frame(RENDERS / "modular-section.png", "section", 18, -70, section=True)
    frame(RENDERS / "modular-exploded.png", "exploded", 22, -58, exploded=True)


if __name__ == "__main__":
    main()
