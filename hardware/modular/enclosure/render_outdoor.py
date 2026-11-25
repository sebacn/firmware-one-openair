#!/usr/bin/env python3
"""Renders and GLBs for the two outdoor-DIY variants."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

from render_variants import add_mesh, box_mesh, paint, scene_bounds

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / "renders"

FLOOR = [
    ("SPS30", "#3d8bfd", (2, 5, 12.4), (41, 41, 12)),
    ("SCD30", "#e07a3d", (-28, 6, 9.6), (35, 23, 7)),
    ("SGP41", "#f2c14e", (-32, -4, 26.5), (16, 25.4, 5)),
    ("SHT45", "#2fbf71", (24, 28, 18.4), (25.3, 17.8, 4.8)),
    ("BQ25185", "#d64550", (-32, 16, 32.5), (16, 29.2, 6)),
]
LAYOUTS = {
    "flat": FLOOR + [
        ("ESP32", "#6b4c9a", (8, -26, 48), (12, 26, 52)),
        ("TPS63020", "#4aa3a2", (-8, -26, 32), (26, 18, 5)),
        ("Battery", "#8d99ae", (0, 0, 98), (70, 50, 18)),
        ("PCM", "#6b8f71", (28, -8, 86), (16, 12, 4)),
    ],
    "vertical": FLOOR + [
        ("Battery", "#8d99ae", (30, -6, 42), (20, 52, 70)),
        ("ESP32", "#6b4c9a", (-4, -26, 46), (12, 26, 52)),
        ("TPS63020", "#4aa3a2", (6, -28, 30), (26, 18, 5)),
        ("PCM", "#6b8f71", (16, -24, 18), (16, 12, 4)),
    ],
}
M8 = {"flat": (30, 28), "vertical": (30, 28)}
VIEWS = {"front": (0, 0), "side": (0, -90), "top": (90, 0)}


def m8(mode):
    x, y = M8[mode]
    thread = trimesh.creation.cylinder(radius=4.0, height=8, sections=18)
    thread.apply_translation([x, y, 2])
    nut = trimesh.creation.cylinder(radius=6.0, height=3, sections=6)
    nut.apply_translation([x, y, 6])
    cups = trimesh.creation.cylinder(radius=2.2, height=7, sections=14)
    cups.apply_translation([x, y, 11])
    return trimesh.util.concatenate([thread, nut, cups])


def frame(mode, view, elev, azim, path, shell_alpha=0.35, modules_only=False, section=False):
    shell = trimesh.load(ROOT / f"outdoor-{mode}" / "shell.stl", force="mesh")
    if section:
        keep = shell.triangles_center[:, 0] > -2
        shell = trimesh.Trimesh(vertices=shell.vertices, faces=shell.faces[keep], process=False)
    fig = plt.figure(figsize=(8, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    if not modules_only:
        add_mesh(ax, shell, "#d9dde3", 0.85 if section else shell_alpha)
    blocks = []
    for name, color, center, size in LAYOUTS[mode]:
        block = box_mesh(center, size)
        add_mesh(ax, block, color, 1)
        blocks.append(block)
        c = np.asarray(center, float)
        ax.text(c[0], c[1], c[2] + size[2] / 2 + 1.2, name, fontsize=7)
    add_mesh(ax, m8(mode), "#2c3338", 1)
    lo, hi = scene_bounds(blocks + [shell])
    span = (hi - lo).max() / 2
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
    fig = plt.figure(figsize=(9, 6.2))
    ax = fig.add_subplot(121, projection="3d")
    blocks = []
    for name, color, center, size in LAYOUTS[mode]:
        block = box_mesh(center, size)
        add_mesh(ax, block, color, 1)
        blocks.append(block)
    lo, hi = scene_bounds(blocks)
    span = max((hi - lo).max() / 2, 36)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=22, azim=-58)
    ax.set_axis_off()
    ax.set_title(f"Outdoor {mode}", fontsize=12)
    ax2 = fig.add_subplot(122)
    ax2.axis("off")
    ax2.set_xlim(0, 1)
    rows = list(LAYOUTS[mode]) + [("M8", "#2c3338", None, None)]
    ax2.set_ylim(0, len(rows) + 1)
    for i, (name, color, _c, _s) in enumerate(rows):
        y = len(rows) - i
        ax2.add_patch(plt.Rectangle((0.05, y - 0.35), 0.16, 0.7, color=color))
        ax2.text(0.28, y, name, va="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(RENDERS / f"outdoor-{mode}-legend.png", dpi=130)
    plt.close(fig)


def glb(mode):
    folder = ROOT / f"outdoor-{mode}"
    shell = trimesh.load(folder / "shell.stl", force="mesh")
    lid = trimesh.load(folder / "lid.stl", force="mesh")
    grill = trimesh.load(folder / "grill.stl", force="mesh")
    grill.apply_translation([2, 4, -1])
    lid.apply_translation([0, 0, float(shell.bounds[1, 2]) - 1])
    scene = trimesh.Scene()
    named = {
        "Shell": paint(shell, "#d9dde3", 90),
        "Lid": paint(lid, "#bfc6d0", 140),
        "Grill": paint(grill, "#9aa3ad"),
        "M8 connector": paint(_m8(mode), "#2c3338"),
    }
    labels = {"ESP32": "ESP32 LOLIN32", "Battery": "1S3P battery", "PCM": "PCM"}
    for name, color, center, size in LAYOUTS[mode]:
        named[labels.get(name, name)] = paint(box_mesh(center, size), color)
    for name, mesh in named.items():
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    path = ROOT / "assembly" / f"outdoor-{mode}.glb"
    scene.export(path)
    print(path, path.stat().st_size)


M8_XY = {"flat": (30, 28), "vertical": (30, 28)}


def _m8(mode):
    x, y = M8_XY[mode]
    parts = []
    for r, h, z, n in ((4.0, 8, 2, 18), (6.0, 3, 6, 6), (2.2, 7, 11, 14)):
        cyl = trimesh.creation.cylinder(radius=r, height=h, sections=n)
        cyl.apply_translation([x, y, z])
        parts.append(cyl)
    return trimesh.util.concatenate(parts)


def main():
    RENDERS.mkdir(exist_ok=True)
    for mode in ("flat", "vertical"):
        for view, (elev, azim) in VIEWS.items():
            frame_ok(mode, view, elev, azim, RENDERS / f"outdoor-{mode}-{view}.png")
        frame_ok(mode, "section", 18, -70, RENDERS / f"outdoor-{mode}-section.png", section=True)
        legend(mode)
        glb(mode)
        print("done", mode)


def frame_ok(mode, view, elev, azim, path, section=False):
    frame(mode, view, elev, azim, path, section=section)


if __name__ == "__main__":
    main()
