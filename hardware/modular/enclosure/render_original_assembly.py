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
# Pose from the O-1PST assembly photos, not from a guessed side-wall mount.
# The board stands in the middle of the ring. Its short edge (USB, LED, button,
# SGP41) is the bottom edge. High KiCad X is down. KiCad Y runs along world X,
# with the USB end toward -X. The sheet is thin in Y: the PMS5003T is behind
# it (+Y) and the SenseAir carrier is on the floor to its right (+X).
# KiCad: USB1 (168, 67.37), D2 (166.57, 76.91), SW1 (167.80, 81.06),
# I2C1 (165.74, 101.53), U2 (124, 83.4). Edge x 113.31..170.34, y 61.41..105.37.
def _x(pcb_y):
    return -22.0 + (pcb_y - 61.41)

def _z(pcb_x):
    return 16.0 + (170.34 - pcb_x)

PARTS = [
    ("PCB", "#2f6b4f", (0.0, -18.0, 44.5), (44.0, 1.6, 57.0)),
    ("ESP32-C3", "#6b4c9a", (_x(83.40), -20.2, _z(124.00)), (13.2, 2.4, 16.6)),
    ("USB-C", "#222222", (_x(67.37), -21.0, 14.2), (9.0, 3.2, 7.5)),
    ("LED", "#f4f1ea", (_x(76.91), -20.4, _z(166.57)), (3.0, 2.4, 4.0)),
    ("Button", "#d0d0d0", (_x(81.06), -20.6, _z(167.80)), (4.5, 3.0, 3.5)),
    ("SGP41", "#f2c14e", (_x(101.53), -26.0, _z(165.74)), (10.0, 12.0, 4.5)),
    ("PMS5003T", "#3d8bfd", (-16.0, 14.0, 22.0), (38.0, 50.0, 21.0)),
    ("CO2 carrier", "#1f7a4d", (20.0, 12.0, 12.3), (32.0, 54.0, 1.6)),
    ("SenseAir S8", "#e07a3d", (20.0, 12.0, 17.4), (20.0, 33.5, 8.5)),
    ("S8 screw A", "#555555", (33.0, -8.0, 14.2), (4.0, 4.0, 3.0)),
    ("S8 screw B", "#555555", (33.0, 32.0, 14.2), (4.0, 4.0, 3.0)),
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
        if exploded and name in ("PCB", "ESP32-C3", "USB-C", "LED", "Button", "SGP41"):
            mesh = mesh.copy()
            mesh.apply_translation([0, 0, 28])
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
        if exploded and name in ("PCB", "ESP32-C3", "USB-C", "LED", "Button", "SGP41"):
            mesh.apply_translation([0, 0, 28])
            center = (center[0], center[1], center[2] + 28)
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
