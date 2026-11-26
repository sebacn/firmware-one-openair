#!/usr/bin/env python3
"""Full O-1PST assembly inside the published DIY outdoor STLs.

Shell positions come from the three STL bounds. Component sizes come from
the Open Air KiCad boards and the Plantower / SenseAir / Espressif drawings.
Where the part sits in the shell is marked in the README: the KiCad files
give positions on the PCB, not in the enclosure.
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

# name, color, center (mm), size (mm)
# Board pose: USB edge toward the cover's -X bulge, 57 mm running inward,
# 44 mm vertical, sheet parallel to the XZ plane. See the README.
# USB edge of the 57.03 x 43.96 mm board is at world x = -28 (the cover bulge).
# pcb x 170.34 -> world x -28, and pcb x decreases as world x increases.
# pcb y 61.41 -> world z 18, so the USB end of that edge is the lower end.
PARTS = [
    ("PCB", "#2f6b4f", (0.5, 18.0, 40.0), (57.0, 1.6, 44.0)),
    ("ESP32-C3", "#6b4c9a", (18.3, 20.0, 40.0), (16.6, 2.4, 13.2)),
    ("USB-C", "#222222", (-27.3, 20.4, 24.0), (7.5, 3.2, 9.0)),
    ("SGP41", "#f2c14e", (-34.0, 18.0, 58.0), (12.0, 4.5, 10.0)),
    ("CO2 carrier", "#1f7a4d", (0.5, 16.4, 46.0), (54.0, 1.6, 32.0)),
    ("SenseAir S8", "#e07a3d", (0.5, 11.4, 48.0), (33.5, 8.5, 20.0)),
    ("PMS5003T", "#3d8bfd", (4.0, -10.0, 23.0), (50.0, 38.0, 21.0)),
]


def load_shells():
    base = trimesh.load(REF / "AirGradient Outdoor DIY Bottom Part B.stl", force="mesh")
    grill = trimesh.load(REF / "AirGradient Outdoor DIY Bottom Part A.stl", force="mesh")
    cover = trimesh.load(REF / "AirGradient Outdoor DIY Top Part C.stl", force="mesh")
    # Center the ring. Its own origin is already within 0.2 mm of the middle.
    b = base.bounds
    base.apply_translation([-(b[0, 0] + b[1, 0]) / 2, -(b[0, 1] + b[1, 1]) / 2, -b[0, 2]])
    g = grill.bounds
    grill.apply_translation([-(g[0, 0] + g[1, 0]) / 2, -(g[0, 1] + g[1, 1]) / 2, -g[0, 2]])
    # The bottom rim is about 1.2 mm left of the ring axis. Shift it onto the
    # ring, and sit that rim 3 mm up so the stack is the published 85 mm.
    # The extra length on -X is the USB side and stays on -X.
    c = cover.bounds
    cover.apply_translation([1.15, 0.0, 3.06 - c[0, 2]])
    return base, grill, cover


def component_meshes():
    return [(name, color, box_mesh(center, size)) for name, color, center, size in PARTS]


def build_scene(exploded=False):
    base, grill, cover = load_shells()
    if exploded:
        grill.apply_translation([0, 0, -28])
        cover.apply_translation([0, 0, 55])
    scene = trimesh.Scene()
    paint(base, "#c5ccd3", 210)
    paint(grill, "#9aa3ad", 230)
    paint(cover, "#d9dde3", 100)
    scene.add_geometry(base, node_name="Base", geom_name="Base")
    scene.add_geometry(grill, node_name="Grill", geom_name="Grill")
    scene.add_geometry(cover, node_name="Cover", geom_name="Cover")
    for name, color, mesh in component_meshes():
        if exploded and name != "PMS5003T":
            mesh = mesh.copy()
            mesh.apply_translation([0, 0, 18])
        paint(mesh, color, 255)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    return scene


def export_glb():
    scene = build_scene(False)
    path = ROOT / "assembly" / "original.glb"
    scene.export(path)
    print("original.glb", path.stat().st_size, "nodes", list(scene.graph.nodes))
    return path


def _frame(path, view, elev, azim, exploded=False, section=False):
    base, grill, cover = load_shells()
    if exploded:
        grill.apply_translation([0, 0, -28])
        cover.apply_translation([0, 0, 55])
    if section:
        keep = cover.triangles_center[:, 0] > -10
        cover = trimesh.Trimesh(vertices=cover.vertices, faces=cover.faces[keep], process=False)
        keep = base.triangles_center[:, 0] > -10
        base = trimesh.Trimesh(vertices=base.vertices, faces=base.faces[keep], process=False)
    fig = plt.figure(figsize=(8.2, 6.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, base, "#c5ccd3", 0.9)
    add_mesh(ax, grill, "#8e99a4", 0.95)
    add_mesh(ax, cover, "#d9dde3", 0.18 if not section else 0.55)
    for name, color, center, size in PARTS:
        mesh = box_mesh(center, size)
        if exploded and name != "PMS5003T":
            mesh.apply_translation([0, 0, 18])
            center = (center[0], center[1], center[2] + 18)
        add_mesh(ax, mesh, color, 1)
        ax.text(center[0], center[1], center[2] + size[2] / 2 + 1.2, name, fontsize=7)
    lo, hi = scene_bounds([base, cover, grill])
    span = (hi - lo).max() / 2 + (28 if exploded else 8)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(f"Original Open Air — {view}", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(path.name)


def legend():
    fig = plt.figure(figsize=(9.4, 6.4))
    ax = fig.add_subplot(121, projection="3d")
    blocks = []
    for name, color, center, size in PARTS:
        mesh = box_mesh(center, size)
        add_mesh(ax, mesh, color, 1)
        blocks.append(mesh)
    lo, hi = scene_bounds(blocks)
    span = max((hi - lo).max() / 2, 36)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=22, azim=-58)
    ax.set_axis_off()
    ax.set_title("Original O-1PST\ncomponents", fontsize=11)
    ax2 = fig.add_subplot(122)
    ax2.axis("off")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, len(PARTS) + 1)
    for i, (name, color, _c, size) in enumerate(PARTS):
        y = len(PARTS) - i
        ax2.add_patch(plt.Rectangle((0.04, y - 0.28), 0.12, 0.55, color=color))
        ax2.text(0.22, y, f"{name}   {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f}", va="center", fontsize=8)
    fig.tight_layout()
    path = RENDERS / "original-assembly-legend.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(path.name)


def main():
    export_glb()
    _frame(RENDERS / "original-assembly-front.png", "front", 0, 0)
    _frame(RENDERS / "original-assembly-side.png", "side", 0, -90)
    _frame(RENDERS / "original-assembly-top.png", "top", 90, 0)
    _frame(RENDERS / "original-assembly-section.png", "section", 18, -70, section=True)
    _frame(RENDERS / "original-exploded.png", "exploded", 22, -58, exploded=True)
    legend()


if __name__ == "__main__":
    main()
