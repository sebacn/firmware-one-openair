#!/usr/bin/env python3
"""Renders, dimension sheets, and GLBs for the two three-part outdoor variants."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.backends.backend_pdf import PdfPages

from render_variants import add_mesh, box_mesh, paint, scene_bounds

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / "renders"

# Cover sits 12 mm up: the 28 mm ring and the 16 mm slide overlap.
COVER_Z = 12.0
FLOOR = [
    ("SPS30", "#3d8bfd", (2, 5, 40), (41, 41, 12)),
    ("SCD30", "#e07a3d", (-26, 6, 38), (35, 23, 7)),
    ("SGP41", "#f2c14e", (-32, -6, 50), (16, 25.4, 5)),
    ("SHT45", "#2fbf71", (22, 26, 46), (25.3, 17.8, 4.8)),
    ("BQ25185", "#d64550", (-24, -22, 11), (19.1, 29.2, 6)),
]
LAYOUTS = {
    "flat": FLOOR + [
        ("ESP32", "#6b4c9a", (4, -22, 72), (12, 26, 52)),
        ("TPS63020", "#4aa3a2", (-6, -24, 36), (26, 18, 5)),
        ("Battery", "#8d99ae", (0, 2, 108), (70, 50, 18)),
        ("PCM", "#6b8f71", (26, -6, 96), (16, 12, 4)),
    ],
    "vertical": FLOOR + [
        ("Battery", "#8d99ae", (28, -4, 62), (22, 50, 70)),
        ("ESP32", "#6b4c9a", (-6, -22, 66), (12, 26, 52)),
        ("TPS63020", "#4aa3a2", (2, -24, 36), (26, 18, 5)),
        ("PCM", "#6b8f71", (10, -26, 28), (16, 12, 4)),
    ],
}
# Assembled size. Plan is the cover. Height is cover plus the 12 mm of ring below it.
SIZE = {
    "flat": (91.5, 86.7, 124),
    "vertical": (91.5, 86.7, 106),
}
PART_H = {"flat": (3.2, 28.0, 112.0), "vertical": (3.2, 28.0, 94.0)}
VIEWS = {"front": (0, 0), "side": (0, -90), "top": (90, 0)}


def load_parts(mode):
    folder = ROOT / f"outdoor-{mode}"
    base = trimesh.load(folder / "base.stl", force="mesh")
    grill = trimesh.load(folder / "grill.stl", force="mesh")
    cover = trimesh.load(folder / "cover.stl", force="mesh")
    grill.apply_translation([0, 0, 3.2])
    cover.apply_translation([0, 0, COVER_Z])
    return base, grill, cover


def modules(mode):
    out = []
    for name, color, center, size in LAYOUTS[mode]:
        out.append((name, color, box_mesh(center, size)))
    return out


def frame(mode, view, elev, azim, path, exploded=False, section=False):
    base, grill, cover = load_parts(mode)
    if exploded:
        grill.apply_translation([0, 0, 36])
        cover.apply_translation([0, 0, 70])
    if section:
        keep = cover.triangles_center[:, 0] > -4
        cover = trimesh.Trimesh(vertices=cover.vertices, faces=cover.faces[keep], process=False)
    fig = plt.figure(figsize=(8, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, base, "#c5ccd3", 0.9)
    add_mesh(ax, grill, "#9aa3ad", 0.95)
    add_mesh(ax, cover, "#d9dde3", 0.28 if not section else 0.75)
    for name, color, mesh in modules(mode):
        add_mesh(ax, mesh, color, 1)
        c = mesh.centroid
        ax.text(c[0], c[1], c[2] + 4, name, fontsize=7)
    lo, hi = scene_bounds([base, cover])
    span = (hi - lo).max() / 2 + (20 if exploded else 0)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(f"Outdoor {mode} — {view}", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def legend(mode):
    fig = plt.figure(figsize=(9.2, 6.2))
    ax = fig.add_subplot(121, projection="3d")
    blocks = []
    for name, color, mesh in modules(mode):
        add_mesh(ax, mesh, color, 1)
        blocks.append(mesh)
    lo, hi = scene_bounds(blocks)
    span = max((hi - lo).max() / 2, 40)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(max(0, c[2] - span), c[2] + span)
    ax.view_init(elev=22, azim=-58)
    ax.set_axis_off()
    w, d, h = SIZE[mode]
    ax.set_title(f"Outdoor {mode}\n{w:.1f} × {d:.1f} × {h:.0f} mm", fontsize=11)
    ax2 = fig.add_subplot(122)
    ax2.axis("off")
    ax2.set_xlim(0, 1)
    rows = [(n, col) for n, col, _m in modules(mode)]
    ax2.set_ylim(0, len(rows) + 1)
    for i, (name, color) in enumerate(rows):
        y = len(rows) - i
        ax2.add_patch(plt.Rectangle((0.05, y - 0.35), 0.16, 0.7, color=color))
        ax2.text(0.28, y, name, va="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(RENDERS / f"outdoor-{mode}-legend.png", dpi=130)
    plt.close(fig)


def dimensions(mode):
    w, d, h = SIZE[mode]
    grill_h, base_h, cover_h = PART_H[mode]
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.8))
    titles = ("Front", "Side", "Top")
    # Simple orthographic boxes with dimension text. Not a hidden-line drawing
    # of the mesh; the numbers are the designed sizes.
    boxes = [
        ((0, 0), (w, h), f"W {w:.1f}\nH {h:.0f}"),
        ((0, 0), (d, h), f"D {d:.1f}\nH {h:.0f}"),
        ((0, 0), (w, d), f"W {w:.1f} × D {d:.1f}"),
    ]
    notes = [
        f"cover {cover_h:.0f}  base {base_h:.0f}  grill {grill_h:.1f}",
        "USB-C recess on the base bottom, -X / -Y",
        "PM ports near centre, M8 at (+30, +26)",
    ]
    for ax, title, ((x, y), (bw, bh), label), note in zip(axes, titles, boxes, notes):
        ax.set_title(title)
        ax.add_patch(plt.Rectangle((x, y), bw, bh, fill=False, lw=1.6))
        ax.text(bw / 2, bh + 4, label, ha="center", fontsize=8)
        ax.text(bw / 2, -8, note, ha="center", fontsize=7)
        ax.set_xlim(-12, bw + 12)
        ax.set_ylim(-16, bh + 16)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle(
        f"Outdoor {mode}: {w:.1f} × {d:.1f} × {h:.0f} mm   "
        f"(original 91.5 × 86.7 × 85)",
        fontsize=11,
    )
    fig.tight_layout()
    png = RENDERS / f"outdoor-{mode}-dimensions.png"
    pdf = RENDERS / f"outdoor-{mode}-dimensions.pdf"
    fig.savefig(png, dpi=140)
    with PdfPages(pdf) as pages:
        pages.savefig(fig)
    plt.close(fig)


def glb(mode):
    base, grill, cover = load_parts(mode)
    scene = trimesh.Scene()
    named = {
        "Base": paint(base, "#c5ccd3"),
        "Grill": paint(grill, "#9aa3ad"),
        "Cover": paint(cover, "#d9dde3", 100),
    }
    labels = {"ESP32": "ESP32 LOLIN32", "Battery": "1S3P battery", "PCM": "PCM"}
    for name, color, center, size in LAYOUTS_FULL(mode):
        named[labels.get(name, name)] = paint(box_mesh(center, size), color)
    for name, mesh in named.items():
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    path = ROOT / "assembly" / f"outdoor-{mode}.glb"
    scene.export(path)
    print(path.name, path.stat().st_size)


def LAYOUTS_FULL(mode):
    return LAYOUTS[mode]


def main():
    RENDERS.mkdir(exist_ok=True)
    for mode in ("flat", "vertical"):
        for view, (elev, azim) in VIEWS.items():
            frame(mode, view, elev, azim, RENDERS / f"outdoor-{mode}-{view}.png")
        frame(mode, "section", 18, -70, RENDERS / f"outdoor-{mode}-section.png", section=True)
        frame(mode, "exploded", 22, -50, RENDERS / f"outdoor-{mode}-exploded.png", exploded=True)
        legend(mode)
        dimensions(mode)
        glb(mode)
    original_drawings()
    original_glb()
    size_comparison()


# local copies so this file does not depend on the old outdoor dicts
LAYOUTS = LAYOUTS
VIEWS = VIEWS


def frame(mode, view, elev, azim, path, exploded=False, section=False):
    base, grill, cover = load_parts(mode)
    if exploded:
        grill.apply_translation([0, 0, 40])
        cover.apply_translation([0, 0, 78])
    if section:
        keep = cover.triangles_center[:, 0] > -4
        cover = trimesh.Trimesh(vertices=cover.vertices, faces=cover.faces[keep], process=False)
    fig = plt.figure(figsize=(8, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, base, "#c5ccd3", 0.95)
    add_mesh(ax, grill, "#8e99a4", 0.95)
    add_mesh(ax, cover, "#d9dde3", 0.22 if not section else 0.72)
    for name, color, center, size in LAYOUTS[mode]:
        mesh = box_mesh(center, size)
        add_mesh(ax, mesh, color, 1)
        ax.text(center[0], center[1], center[2] + size[2] / 2 + 1.5, name, fontsize=7)
    lo, hi = scene_bounds([base, cover])
    span = (hi - lo).max() / 2 + (24 if exploded else 6)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(-4, hi[2] + (30 if exploded else 8))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    w, d, h = SIZE[mode]
    ax.set_title(f"Outdoor {mode} — {view}   {w:.1f} × {d:.1f} × {h:.0f} mm", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def original_drawings():
    parts = [
        ("Grill A", (71.5, 71.2, 11.5), "round screen, Ø about 71.5"),
        ("Base ring B", (83.0, 82.9, 26.7), "open centre, sleeve for the cover"),
        ("Cover C", (91.5, 85.0, 81.9), "slides over the 83 mm ring"),
        ("Assembled", (91.5, 86.7, 85.0), "published O-1PST size"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, (title, (w, d, h), note) in zip(axes.ravel(), parts):
        ax.set_title(f"{title}\n{w:.1f} × {d:.1f} × {h:.1f} mm")
        ax.add_patch(plt.Rectangle((0, 0), w, h, fill=False, lw=1.6))
        ax.text(w / 2, h + 3, f"W {w:.1f}   H {h:.1f}", ha="center", fontsize=8)
        ax.text(w / 2, -6, note, ha="center", fontsize=7)
        ax.set_xlim(-8, max(w, 100))
        ax.set_ylim(-12, h + 12)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Original DIY outdoor STLs — bounding sizes. Cover wall steps in; the lower sleeve opening is about 82–84 mm.", fontsize=10)
    fig.tight_layout()
    png = RENDERS / "original-dimensions.png"
    fig.savefig(png, dpi=140)
    with PdfPages(RENDERS / "original-dimensions.pdf") as pages:
        pages.savefig(fig)
    plt.close(fig)


def size_comparison():
    rows = [
        ("Original", 91.5, 86.7, 85),
        ("Flat battery", 91.5, 86.7, 124),
        ("Vertical battery", 91.5, 86.7, 106),
    ]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Same scale — front view")
    x = 0
    for name, w, d, h in rows:
        ax.add_patch(plt.Rectangle((x, 0), w, h, fill=False, lw=1.5))
        ax.text(x + w / 2, h + 3, f"{name}\n{w:.1f} × {d:.1f} × {h:.0f}", ha="center", fontsize=8)
        x += w + 18
    ax.set_xlim(-10, x)
    ax.set_ylim(-10, 150)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    png = RENDERS / "size-comparison.png"
    fig.savefig(png, dpi=140)
    with PdfPages(RENDERS / "size-comparison.pdf") as pages:
        pages.savefig(fig)
    plt.close(fig)


def original_glb():
    ref = ROOT / "reference-outdoor"
    names = [
        "AirGradient Outdoor DIY Bottom Part B.stl",
        "AirGradient Outdoor DIY Bottom Part A.stl",
        "AirGradient Outdoor DIY Top Part C.stl",
    ]
    colors = ["#c5ccd3", "#9aa3ad", "#d9dde3"]
    labels = ["Base", "Grill", "Cover"]
    scene = trimesh.Scene()
    z = 0
    for fname, color, label in zip(names, colors, labels):
        mesh = trimesh.load(ref / fname, force="mesh")
        mesh.apply_translation(-mesh.bounds.mean(axis=0))
        mesh.apply_translation([0, 0, z - mesh.bounds[0, 2]])
        # Overlap the cover onto the ring by about 24 mm so the stack is ~85 mm.
        if label == "Cover":
            mesh.apply_translation([0, 0, -24])
        paint(mesh, color, 255 if label != "Cover" else 110)
        scene.add_geometry(mesh, node_name=label, geom_name=label)
        z = mesh.bounds[1, 2]
    path = ROOT / "assembly" / "original.glb"
    scene.export(path)
    print("original", path.stat().st_size)


if __name__ == "__main__":
    main()
