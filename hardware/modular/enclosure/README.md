# Modular outdoor enclosure

The cover and the base ring are the original AirGradient Open Air STLs, unchanged. The grill is the original Part A mesh. Its outer outline, outer wall, mating lip, corner mounting holes, and the vent pattern outside the new openings are that mesh. The original interior PCB bosses are cut away, and the mounts for this monitor are added on the inside. There is no battery in the box. The dev board is powered from its USB socket, or from the M8 plug when USB is unplugged. Its 5 V pin feeds the SPS30. Its 3.3 V pin feeds the I2C boards.

## Parts

| Part | File | What changed |
| --- | --- | --- |
| Cover | [`reference-outdoor/`](reference-outdoor/README.md) Top Part C, 91.5 × 85.0 × 81.9 mm | Nothing. Cap up, sleeve down over the ring. |
| Base ring | Bottom Part B, 83.0 × 82.9 × 26.7 mm | Nothing. The lip still holds the grill. |
| Grill | [`grill-modular.stl`](grill-modular.stl), from [`build_grill.py`](build_grill.py) | Interior only. Outer bounding box is the original 71.541 × 71.189 × 11.5 mm. |

Assembly model: [`assembly/modular.glb`](assembly/modular.glb). Viewer: [`assembly/index.html`](assembly/index.html). Renders: [`renders/modular-exploded.png`](renders/modular-exploded.png), [`renders/modular-section.png`](renders/modular-section.png), [`renders/modular-front.png`](renders/modular-front.png), [`renders/modular-side.png`](renders/modular-side.png), and [`renders/modular-top.png`](renders/modular-top.png).

## Outer geometry

`build_grill.py` imports `AirGradient Outdoor DIY Bottom Part A.stl` and booleans only the interior. Compared with that file:

| Check | Result |
| --- | --- |
| Bounding box | Identical. Both are `[-35.479, -35.633, -11.000]` to `[36.062, 35.556, 0.500]` mm. Delta is 0 on every corner. |
| Extents | Both 71.541 × 71.189 × 11.5 mm. |
| Mating lip | Hausdorff distance 0.000 mm, both directions. 207 original vertices on the seat (z = −2 mm, radius > 34.2 mm, clear of the removed bosses) and 220 on the modified mesh. None moved by more than 0.05 mm. |
| Outer wall | Hausdorff distance 0.000 mm, both directions (72 vertices past the skirt, above the boss bottoms). |
| Skirt bottom | Hausdorff distance 0.000 mm on the 157 vertices at z < −9.3 mm and radius > 32 mm that are not the removed bosses. |
| Corner mounting holes | Unchanged. Vertices within 4 mm of each of the four holes match the original exactly. |

The four interior PCB bosses are gone. That is the only change on the underside besides the new screw bosses. The vent pattern is the original one except for the openings listed below.

## How the parts sit

Looking down, z up. The grill's top face is at z = 5.2 mm in the assembly, which is the original CAD frame with the base lip at the bottom.

- SHT45, SGP41, and SCD30 lie flat. The sensor face is the bottom face, over the original vent openings. SHT45 is on the left. Its edge is 4.75 mm from the SPS30 and 8.60 mm from the ESP32.
- SPS30 stands. The inlet is the bottom edge, over a 30 × 6 mm slot cut through the floor. The outlet is the top edge, open into the cover.
- The dev board stands on its USB end. The footprint is 13 × 28 mm, the larger of a LOLIN32 (58 × 25.4, stood on the short end) and an ESP32-S3 board (57.15 × 27.94) once the board width is the 28 mm side and the component height is the 13 mm side. A D1 mini fits the same place. USB is at the bottom, over a 12 × 8 mm cable slot.
- M8 A-coded 4-pin panel connector, thread M8×0.5. The hole is Ø8.2 mm and faces down. The nut pocket is Ø16 × 1.5 mm from the inside face. Pin 1 brown is 5 V in, pin 2 white is VBAT sense, pin 3 blue is GND, pin 4 black is VSOL sense.
- The original pattern under the SGP41 is mostly solid, so three 12 × 2.4 mm slots are cut there. SCD30 sits on the dense original vents (about a third of its footprint is already open). SHT45 sits on the original openings along the left side.
- Each board drops into a pocket 0.55 to 0.7 mm deep and is screwed through Ø2.2 mm holes into bosses on the underside of the plate.

### Clearance to the original meshes

Gaps between the part boxes, in mm. The smallest is **1.30 mm**, SGP41 to the M8 nut.

| | ESP32 | SCD30 | SHT45 | SGP41 | M8 |
| --- | ---: | ---: | ---: | ---: | ---: |
| SPS30 | 4.40 | 1.40 | 4.75 | | |
| ESP32 | | 2.00 | 8.60 | 2.10 | 5.50 |
| SCD30 | | | | 5.80 | 1.50 |
| SHT45 | | | | 4.45 | 7.85 |
| SGP41 | | | | | 1.30 |

Distance from sample points on each part to the original shell meshes. No sample falls inside the base plastic, the cover plastic, or the grill plastic.

| Part | To the base | To the cover |
| --- | ---: | ---: |
| SPS30 | 2.38 mm | 4.70 mm |
| ESP32 | 18.33 mm | 3.26 mm |
| SCD30 | 4.18 mm | 9.15 mm |
| SHT45 | 3.03 mm | 5.87 mm |
| SGP41 | 2.52 mm | 5.99 mm |
| M8 | 1.61 mm | 5.68 mm |

The nearest approach to the cover is the top of the ESP32, 3.26 mm. The nearest approach to the base is the M8 nut, 1.61 mm.

### Print

Print the grill in PETG or ASA, 0.2 mm layers, four perimeters, 20% infill, flange up so the vent face is on the bed. The original cover and base print as AirGradient published them.

### Assembly order

1. Set the grill on the base lip the way the original Part A sits. The skirt hangs through the opening.
2. Fit the M8 receptacle through the Ø8.2 mm hole from below and tighten the nut in the Ø16 mm pocket. Solder the four leads before the boards go in.
3. Seat the SHT45, SCD30, and SGP41 in their pockets, sensor faces down, and screw them through the Ø2.2 mm holes. Stand the SPS30 in its pocket, inlet down over the slot. Stand the dev board in its pocket, USB over the cable slot.
4. Run the I2C and 5 V leads along the plate. Keep the SHT45 leads on the left, away from the SPS30 and the dev board.
5. Slide the original cover on from above and close it with the original four screws.
