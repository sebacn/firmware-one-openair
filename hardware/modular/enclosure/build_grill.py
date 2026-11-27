#!/usr/bin/env python3
"""Build grill-modular.stl from the original Open Air Part A mesh.

The outer shell is kept: outline, outer wall, the lip that seats on Part B,
the corner mounting holes, and the vent pattern except where a new opening
is required. Interior PCB bosses are cut away. Mounts, the M8 hole, the
SPS30 inlet, and the USB slot are added on the inside of that same mesh.
"""

from pathlib import Path

import numpy as np
import trimesh
import manifold3d as mf

ROOT = Path(__file__).resolve().parent
REF = ROOT / "reference-outdoor"
SRC = REF / "AirGradient Outdoor DIY Bottom Part A.stl"
DST = ROOT / "grill-modular.stl"

# Assembly frame: same translation that seats Part B with its lip down.
# Part A is already in that CAD frame; assembly = raw + T.
# Component centers are in the assembly frame (z up, plate top at 5.2).


def base_translation():
    base = trimesh.load(REF / "AirGradient Outdoor DIY Bottom Part B.stl", force="mesh")
    return np.array([
        -(base.bounds[0, 0] + base.bounds[1, 0]) / 2,
        -(base.bounds[0, 1] + base.bounds[1, 1]) / 2,
        -base.bounds[0, 2],
    ])


def to_raw(xy, origin):
    return (float(xy[0] - origin[0]), float(xy[1] - origin[1]))


def cube(size, center):
    return mf.Manifold.cube(list(size), True).translate(list(center))


def cylinder(height, radius, center):
    # Manifold cylinders sit on z = 0. The third constructor argument is a
    # radius, not a segment count, so circular detail is set globally.
    return mf.Manifold.cylinder(height, radius).translate(
        [center[0], center[1], center[2] - height / 2]
    )


def main():
    mf.set_circular_segments(48)
    original = trimesh.load(SRC, force="mesh")
    origin = base_translation()
    grill_center = (original.bounds[0] + original.bounds[1]) / 2
    print("original bbox", np.round(original.bounds, 3).tolist())
    print("original extents", np.round(original.extents, 3).tolist())

    # Plate spans roughly z = -1.9 .. 0.5 in the original frame. The skirt
    # and the original PCB bosses hang below the plate, toward z = -11.
    plate_top = 0.50
    plate_bottom = -1.85

    cutters = []

    # Original interior bosses that are not the four corner shell screws.
    # Coordinates were measured in the grill's own centered frame.
    own = np.array([
        (original.bounds[0, 0] + original.bounds[1, 0]) / 2,
        (original.bounds[0, 1] + original.bounds[1, 1]) / 2,
        original.bounds[0, 2],
    ])
    # centered = raw + [-own.x, -own.y, -own.z]; raw = centered + own
    for cx, cy in ((-14.3, 28.7), (19.2, 28.7), (-22.3, -27.1), (21.7, -27.1)):
        raw = np.array([cx, cy, 0.0]) + own
        cutters.append(cylinder(8.4, 3.1, (raw[0], raw[1], -6.5)))

    def slot(asm_xy, size_xy):
        x, y = to_raw(asm_xy, origin)
        # Through the plate, from below the underside to above the top face.
        cutters.append(cube((size_xy[0], size_xy[1], 3.6), (x, y, -0.7)))

    def pocket(asm_xy, size_xy, depth=0.6):
        x, y = to_raw(asm_xy, origin)
        cutters.append(cube(
            (size_xy[0], size_xy[1], depth + 0.4),
            (x, y, plate_top - depth / 2 + 0.2),
        ))

    # SPS30 inlet, USB cable, and three extra slots under the SGP41
    # (the original pattern is solid there). All of these are floor cuts.
    slot((0.0, 26.5), (30.0, 6.0))
    slot((0.0, 2.0), (12.0, 8.0))
    for dy in (-3.2, 0.0, 3.2):
        slot((-10.0, -23.0 + dy), (12.0, 2.4))

    # Shallow registration pockets, smaller than the part so a lip remains.
    pocket((0.0, 26.5), (38.6, 10.2), 0.7)   # SPS30
    pocket((0.0, 2.0), (11.0, 26.0), 0.7)    # ESP32
    pocket((20.0, 1.5), (21.0, 33.0), 0.55)  # SCD30
    pocket((-24.0, 3.0), (15.8, 23.3), 0.55)  # SHT45
    pocket((-10.0, -23.0), (23.4, 15.8), 0.55)  # SGP41

    # M8 panel hole and the nut counterbore from the interior face.
    mx, my = to_raw((12.0, -25.5), origin)
    cutters.append(cylinder(3.6, 4.1, (mx, my, -0.7)))          # Ø8.2 through
    cutters.append(cylinder(1.7, 8.0, (mx, my, plate_top - 0.55)))  # Ø16 x 1.5 pocket

    # M2 clearance holes so the flat boards and the dev board screw to the plate.
    screw_xy = []
    for asm, dx, dy in (
        ((20.0, 1.5), 8.0, 14.0),
        ((-24.0, 3.0), 6.0, 9.5),
        ((-10.0, -23.0), 9.0, 6.0),
        ((0.0, 2.0), 0.0, 10.0),
    ):
        for sx in (-1, 1):
            for sy in (-1, 1):
                if dx == 0.0 and sx == 1:
                    continue
                screw_xy.append((asm[0] + sx * dx, asm[1] + sy * dy))
    for asm in screw_xy:
        x, y = to_raw(asm, origin)
        cutters.append(cylinder(3.6, 1.1, (x, y, -0.7)))

    block = cutters[0]
    for extra in cutters[1:]:
        block = block + extra

    mesh_in = mf.Mesh(
        vert_properties=np.asarray(original.vertices, np.float32),
        tri_verts=np.asarray(original.faces, np.uint32),
    )
    result = mf.Manifold(mesh_in) - block

    # Underside bosses around the screw holes, inside the skirt, so the
    # M2 threads have more than the plate thickness to hold.
    bosses = None
    for asm in screw_xy:
        x, y = to_raw(asm, origin)
        boss = cylinder(4.6, 2.3, (x, y, plate_bottom - 1.5))
        hole = cylinder(5.4, 1.1, (x, y, plate_bottom - 1.5))
        boss = boss - hole
        bosses = boss if bosses is None else bosses + boss
    result = result + bosses
    print("boolean", result.status(), "tri", result.num_tri(), "vol", round(result.volume(), 1))

    out_mesh = result.to_mesh()
    baked = trimesh.Trimesh(
        vertices=np.asarray(out_mesh.vert_properties[:, :3], np.float64),
        faces=np.asarray(out_mesh.tri_verts, np.int64),
        process=False,
    )
    baked.merge_vertices()
    baked.update_faces(baked.unique_faces())
    baked.remove_unreferenced_vertices()
    baked.export(DST)
    print("wrote", DST, "extents", np.round(baked.extents, 3).tolist())

    report(original, baked, grill_center)


def report(original, baked, center):
    print("--- outer match ---")
    ob, bb = original.bounds, baked.bounds
    print("bbox original", np.round(ob, 4).tolist())
    print("bbox modified", np.round(bb, 4).tolist())
    print("bbox delta", np.round(bb - ob, 4).tolist())
    print("extents", np.round(original.extents, 3).tolist(), np.round(baked.extents, 3).tolist())

    own = np.array([
        (original.bounds[0, 0] + original.bounds[1, 0]) / 2,
        (original.bounds[0, 1] + original.bounds[1, 1]) / 2,
    ])
    bosses = []
    for cx, cy in ((-14.3, 28.7), (19.2, 28.7), (-22.3, -27.1), (21.7, -27.1)):
        bosses.append(np.array([cx, cy]) + own)
    bosses = np.array(bosses)

    def away_from_bosses(pts):
        d = np.min(np.linalg.norm(pts[:, None, :2] - bosses[None, :, :], axis=2), axis=1)
        return d > 6.0

    def hausdorff(src_pts, dst, label):
        if len(src_pts) == 0:
            print(label, "empty")
            return
        dist = trimesh.proximity.closest_point(dst, src_pts)[1]
        print(
            f"{label}: n={len(src_pts)} hausdorff {dist.max():.4f} mm  "
            f"median {np.median(dist):.4f}  vertices moved >0.05 mm {(dist > 0.05).sum()}"
        )

    v = original.vertices
    r = np.hypot(v[:, 0] - center[0], v[:, 1] - center[1])
    keep = away_from_bosses(v)
    # The flange seat is the ring at z = -2 outside the cavity. The outer wall
    # is the material past the skirt. Boss bottoms sit on z = -10 and are not
    # part of either; those are the posts this grill removes.
    hausdorff(v[(np.abs(v[:, 2] + 2) < 0.05) & (r > 34.2) & keep], baked, "mating lip")
    axial = np.maximum(np.abs(v[:, 0] - center[0]), np.abs(v[:, 1] - center[1]))
    hausdorff(v[(axial > 34.6) & (v[:, 2] > -9) & keep], baked, "outer wall")
    hausdorff(v[(v[:, 2] < -9.3) & (r > 32) & keep], baked, "skirt bottom")

    bv = baked.vertices
    br = np.hypot(bv[:, 0] - center[0], bv[:, 1] - center[1])
    baxial = np.maximum(np.abs(bv[:, 0] - center[0]), np.abs(bv[:, 1] - center[1]))
    bkeep = away_from_bosses(bv)
    hausdorff(bv[(np.abs(bv[:, 2] + 2) < 0.05) & (br > 34.2) & bkeep], original, "mating lip reverse")
    hausdorff(bv[(baxial > 34.6) & (bv[:, 2] > -9) & bkeep], original, "outer wall reverse")
    print("watertight", baked.is_watertight, "volume", round(float(baked.volume), 1),
          "original volume", round(float(original.volume), 1))


if __name__ == "__main__":
    main()
