#!/usr/bin/env python3
"""Render the three enclosure variants with coloured module blocks."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / "renders"

# name, color, center (x,y,z), size (x,y,z)
# Coordinates match enclosure.scad standoffs. Origin is the floor centre.
# Shared floor matches the Open Air: SPS30 over the bottom ports, SCD30 beside
# it, SGP41 on the USB wall, SHT45 on the intake side. Only the pack and the
# controller move between variants.
FLOOR = [
    ("SPS30", "#3d8bfd", (6, 4, 12.6), (41, 41, 12)),
    ("SCD30", "#e07a3d", (-28, 6, 10.0), (35, 23, 7)),
    ("SGP41", "#f2c14e", (-34, -2, 28.5), (18, 25.4, 5)),
    ("SHT45", "#2fbf71", (29, 29, 20.4), (25.3, 17.8, 4.8)),
    ("BQ25185", "#d64550", (-34, 18, 34.0), (16, 29.2, 6)),
]
LAYOUTS = {
    1: FLOOR + [
        ("ESP32", "#6b4c9a", (28, -30, 52), (12, 26, 58)),
        ("TPS63020", "#4aa3a2", (-2, -32, 34), (26, 18, 5)),
        ("Battery", "#8d99ae", (0, 6, 90), (68, 36, 18)),
        ("PCM", "#6b8f71", (36, -18, 22), (16, 12, 4)),
    ],
    2: FLOOR + [
        ("Battery", "#8d99ae", (0, -30, 16), (68, 26, 22)),
        ("ESP32", "#6b4c9a", (26, -30, 58), (12, 26, 50)),
        ("TPS63020", "#4aa3a2", (4, -32, 36), (26, 18, 5)),
        ("PCM", "#6b8f71", (34, -18, 20), (16, 12, 4)),
    ],
    3: FLOOR + [
        ("Battery", "#8d99ae", (0, -26, 88), (68, 28, 22)),
        ("ESP32", "#6b4c9a", (0, 18, 96), (58, 26, 10)),
        ("TPS63020", "#4aa3a2", (28, 18, 78), (26, 18, 5)),
        ("PCM", "#6b8f71", (34, -26, 72), (16, 12, 4)),
    ],
}

# M8x1 female receptacle: thread through the floor, nut and cups inside.
M8_POS = {1: (28, -30), 2: (34, 32), 3: (28, -30)}

VIEWS = {
    "front": (0, 0),
    "back": (0, 180),
    "side": (0, -90),
    "top": (90, 0),
    "bottom": (-90, 0),
    "isometric": (28, -58),
}


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
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces)[:, [0, 1, 2]].tolist() + np.array(faces)[:, [0, 2, 3]].tolist())


def add_mesh(ax, mesh, color, alpha=1.0):
    if mesh.is_empty:
        return
    tri = mesh.triangles
    # Keep the plot readable.
    if len(tri) > 6000:
        idx = np.linspace(0, len(tri) - 1, 6000).astype(int)
        tri = tri[idx]
    pc = Poly3DCollection(tri, alpha=alpha, linewidths=0)
    pc.set_facecolor(color)
    pc.set_edgecolor((0, 0, 0, 0.05))
    ax.add_collection3d(pc)


def scene_bounds(meshes):
    lo = np.min([m.bounds[0] for m in meshes], axis=0)
    hi = np.max([m.bounds[1] for m in meshes], axis=0)
    return lo, hi


def render(variant, view_name, elev, azim, exploded=False, transparent=False, path=None):
    folder = ROOT / f"variant-{variant}"
    shell = trimesh.load(folder / "shell.stl", force="mesh")
    lid = trimesh.load(folder / "lid.stl", force="mesh")
    grill = trimesh.load(folder / "grill.stl", force="mesh")
    divider = trimesh.load(folder / "divider.stl", force="mesh")
    # Park the grill over the floor ports and the divider on the thermal wall.
    grill.apply_translation([6, 4, -1.2])
    if variant == 1:
        divider.apply_translation([-18, 6, 24])
    elif variant == 2:
        divider.apply_translation([-18, 8, 52])
    else:
        divider.apply_translation([-18, 4, 18])
    lid_z = float(shell.bounds[1, 2]) - 1
    lid.apply_translation([0, 0, lid_z])

    if exploded:
        lid.apply_translation([0, 0, 28])
        grill.apply_translation([0, 46, 0])
        divider.apply_translation([28, 0, 0])

    fig = plt.figure(figsize=(8.2, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, shell, "#d9dde3", 0.28 if transparent or exploded else 0.55)
    add_mesh(ax, lid, "#bfc6d0", 0.35 if exploded else 0.7)
    add_mesh(ax, grill, "#9aa3ad", 0.9)
    add_mesh(ax, divider, "#f4f1ea", 0.95)
    add_mesh(ax, m8_mesh(variant), "#2c3338", 0.95)

    meshes = [shell, lid]
    for name, color, center, size in LAYOUTS[variant]:
        block = box_mesh(center, size)
        if exploded:
            block.apply_translation([0, 0, 10])
        add_mesh(ax, block, color, 0.95)
        meshes.append(block)
        c = np.asarray(center)
        ax.text(c[0], c[1], c[2] + size[2] / 2 + 1.5, name, fontsize=7, color="#1b1b1b")

    lo, hi = scene_bounds(meshes)
    center = (lo + hi) / 2
    span = (hi - lo).max() / 2
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    title = f"Variant {variant}"
    if exploded:
        title += " — exploded"
    elif transparent:
        title += " — modules inside"
    else:
        title += f" — {view_name}"
    ax.set_title(title, fontsize=12, pad=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def m8_mesh(variant):
    x, y = M8_POS[variant]
    thread = trimesh.creation.cylinder(radius=4.0, height=8, sections=20)
    thread.apply_translation([x, y, 2.0])
    nut = trimesh.creation.cylinder(radius=6.2, height=3.2, sections=6)
    nut.apply_translation([x, y, 6.0])
    cups = trimesh.creation.cylinder(radius=2.4, height=8, sections=16)
    cups.apply_translation([x, y, 11.5])
    return trimesh.util.concatenate([thread, nut, cups])


def legend(variant):
    fig = plt.figure(figsize=(9.2, 6.4))
    ax = fig.add_subplot(121, projection="3d")
    blocks = []
    for name, color, center, size in LAYOUTS[variant]:
        block = box_mesh(center, size)
        add_mesh(ax, block, color, 1.0)
        blocks.append(block)
        c = np.asarray(center, float)
        ax.text(c[0], c[1], c[2] + size[2] / 2 + 2, name, fontsize=8)
    add_mesh(ax, m8_mesh(variant), "#2c3338", 1.0)
    lo, hi = scene_bounds(blocks)
    span = max((hi - lo).max() / 2, 40)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=22, azim=-58)
    ax.set_axis_off()
    ax.set_title(f"Variant {variant} modules", fontsize=12)
    ax2 = fig.add_subplot(122)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, len(LAYOUTS[variant]) + 2)
    ax2.axis("off")
    rows = list(LAYOUTS[variant]) + [("M8", "#2c3338", None, None)]
    for i, (name, color, _c, _s) in enumerate(rows):
        y = len(rows) - i
        ax2.add_patch(plt.Rectangle((0.05, y - 0.35), 0.18, 0.7, color=color))
        ax2.text(0.3, y, name, va="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(RENDERS / f"variant-{variant}-legend.png", dpi=130)
    plt.close(fig)


def section(variant):
    shell = trimesh.load(ROOT / f"variant-{variant}" / "shell.stl", force="mesh")
    centers = shell.triangles_center
    keep = centers[:, 0] > -2
    cut = trimesh.Trimesh(vertices=shell.vertices, faces=shell.faces[keep], process=False)
    fig = plt.figure(figsize=(8.2, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, cut, "#c5ccd4", 0.9)
    for name, color, center, size in LAYOUTS[variant]:
        block = box_mesh(center, size)
        # Keep the half the cut opens, plus a little past the plane so labels remain.
        if center[0] < -8:
            continue
        add_mesh(ax, block, color, 1.0)
        c = np.asarray(center, float)
        ax.text(c[0], c[1], c[2] + size[2] / 2 + 1.5, name, fontsize=7)
    add_mesh(ax, m8_mesh(variant), "#2c3338", 1.0)
    lo, hi = shell.bounds
    span = (hi - lo).max() / 2
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=18, azim=-70)
    ax.set_axis_off()
    ax.set_title(f"Variant {variant} — section", fontsize=12)
    fig.tight_layout()
    fig.savefig(RENDERS / f"variant-{variant}-section.png", dpi=130)
    plt.close(fig)


def comparison():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.2), subplot_kw={"projection": "3d"})
    notes = {
        1: "Rear battery\nshortest",
        2: "Battery plinth\nside inlet",
        3: "Sensor pod\nbest isolation",
    }
    for ax, variant in zip(axes, (1, 2, 3)):
        shell = trimesh.load(ROOT / f"variant-{variant}" / "shell.stl", force="mesh")
        add_mesh(ax, shell, "#d9dde3", 0.35)
        for name, color, center, size in LAYOUTS[variant]:
            add_mesh(ax, box_mesh(center, size), color, 0.95)
        lo, hi = shell.bounds
        span = (hi - lo).max() / 2
        c = (lo + hi) / 2
        ax.set_xlim(c[0] - span, c[0] + span)
        ax.set_ylim(c[1] - span, c[1] + span)
        ax.set_zlim(0, hi[2] + 8)
        ax.view_init(elev=24, azim=-60)
        ax.set_axis_off()
        ax.set_title(f"Variant {variant}\n{notes[variant]}", fontsize=11)
    fig.suptitle("Modular enclosure variants — soldered wiring, same shell family", fontsize=13, y=0.98)
    fig.subplots_adjust(top=0.78, wspace=0.08)
    png = RENDERS / "comparison.png"
    fig.savefig(png, dpi=130)
    plt.close(fig)
    # One-page PDF of the same sheet.
    import matplotlib.backends.backend_pdf as pdf

    fig = plt.figure(figsize=(14, 5.2))
    img = plt.imread(png)
    plt.imshow(img)
    plt.axis("off")
    out = RENDERS / "comparison.pdf"
    with pdf.PdfPages(out) as pages:
        pages.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def paint(mesh, hexcolor, alpha=255):
    rgb = matplotlib.colors.to_rgb(hexcolor)
    mesh.visual.face_colors = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), alpha]
    return mesh


def export_glb():
    out = ROOT / "assembly"
    out.mkdir(exist_ok=True)
    for variant in (1, 2, 3):
        folder = ROOT / f"variant-{variant}"
        scene = trimesh.Scene()
        shell = trimesh.load(folder / "shell.stl", force="mesh")
        lid = trimesh.load(folder / "lid.stl", force="mesh")
        grill = trimesh.load(folder / "grill.stl", force="mesh")
        divider = trimesh.load(folder / "divider.stl", force="mesh")
        grill.apply_translation([6, 4, -1.2])
        if variant == 1:
            divider.apply_translation([-18, 6, 24])
        elif variant == 2:
            divider.apply_translation([-18, 8, 52])
        else:
            divider.apply_translation([-18, 4, 18])
        lid.apply_translation([0, 0, float(shell.bounds[1, 2]) - 1])
        named = {
            "Shell": paint(shell, "#d9dde3", 90),
            "Lid": paint(lid, "#bfc6d0", 140),
            "Grill": paint(grill, "#9aa3ad"),
            "Divider": paint(divider, "#f4f1ea"),
            "M8": paint(m8_mesh(variant), "#2c3338"),
        }
        labels = {
            "ESP32": "ESP32 LOLIN32",
            "Battery": "1S3P battery",
            "SCD30": "SCD30",
            "PCM": "PCM",
        }
        for name, color, center, size in LAYOUTS[variant]:
            named[labels.get(name, name)] = paint(box_mesh(center, size), color)
        named["M8 connector"] = named.pop("M8")
        for name, mesh in named.items():
            scene.add_geometry(mesh, node_name=name, geom_name=name)
        path = out / f"variant-{variant}.glb"
        scene.export(path)
        print("glb", path, path.stat().st_size)


def original_diagram():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    ax = axes[0]
    ax.set_title("Open Air, looking down into the bottom")
    ax.set_xlim(-50, 50)
    ax.set_ylim(-48, 48)
    ax.set_aspect("equal")
    ax.add_patch(plt.Rectangle((-46, -44), 92, 88, fill=False, lw=2, color="#333"))
    ax.add_patch(plt.Rectangle((-8, -16), 41, 41, color="#3d8bfd", alpha=0.85))
    ax.text(12, 4, "PMS5003T\ninlet down", ha="center", va="center", fontsize=8, color="white")
    ax.add_patch(plt.Rectangle((-42, -8), 30, 20, color="#e07a3d", alpha=0.9))
    ax.text(-27, 2, "S8 CO2", ha="center", va="center", fontsize=8)
    ax.add_patch(plt.Rectangle((-46, -28), 14, 22, color="#f2c14e", alpha=0.95))
    ax.text(-39, -17, "SGP41\nout", ha="center", va="center", fontsize=7)
    ax.add_patch(plt.Rectangle((18, -40), 12, 50, color="#6b4c9a", alpha=0.9))
    ax.text(24, -15, "PCB\nvertical", ha="center", va="center", fontsize=8, color="white")
    ax.annotate("USB-C", xy=(-46, 8), xytext=(-20, 36), fontsize=8,
                arrowprops=dict(arrowstyle="->", color="#d64550"))
    ax.plot([-46], [8], "o", color="#d64550")
    ax.set_xlabel("side wall with USB  →")
    ax.set_yticks([])
    ax.set_xticks([])
    ax = axes[1]
    ax.set_title("Open Air, side: air falls in, does not loop")
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 90)
    ax.add_patch(plt.Rectangle((8, 8), 70, 70, fill=False, lw=2))
    ax.annotate("", xy=(43, 18), xytext=(43, 70),
                arrowprops=dict(arrowstyle="->", color="#3d8bfd", lw=2))
    ax.text(48, 50, "inlet\ndown", color="#3d8bfd", fontsize=8)
    ax.annotate("", xy=(78, 40), xytext=(55, 22),
                arrowprops=dict(arrowstyle="->", color="#c47b2b", lw=2))
    ax.text(60, 36, "exhaust\nout the side", color="#c47b2b", fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(RENDERS / "original-reference.png", dpi=130)
    plt.close(fig)


def main():
    RENDERS.mkdir(exist_ok=True)
    for variant in (1, 2, 3):
        for name, (elev, azim) in VIEWS.items():
            render(variant, name, elev, azim, path=RENDERS / f"variant-{variant}-{name}.png")
        render(
            variant,
            "inside",
            28,
            -58,
            transparent=True,
            path=RENDERS / f"variant-{variant}-inside.png",
        )
        render(
            variant,
            "exploded",
            22,
            -50,
            exploded=True,
            path=RENDERS / f"variant-{variant}-exploded.png",
        )
        legend(variant)
        section(variant)
        print("rendered", variant)
    comparison()
    original_diagram()
    export_glb()
    print("comparison", RENDERS / "comparison.png")


if __name__ == "__main__":
    main()
