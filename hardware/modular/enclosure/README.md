# Modular outdoor enclosure

Three ways to put the modular monitor inside a shell that keeps the AirGradient outdoor look: a rounded rectangular body, a bottom particulate screen, and a USB opening on the side. The models are parametric OpenSCAD, not a boolean edit of the original meshes. The original STLs were measured and the new shell follows that size and those openings.

Source: [`enclosure.scad`](enclosure.scad). Renders: [`renders/`](renders/).

All wiring is soldered. There are no sockets or plug-in headers on the boards. The only panel connector is the solar inlet.

## What the original enclosure is

Measured with trimesh from `hardware/open-air/enclosure/` (units millimetres):

| STL | Outer size (X × Y × Z) | What it is |
| --- | --- | --- |
| Top Part C | 91.5 × 85.0 × 81.9 | Main rounded shell. A column of features on one side wall is the USB / control side. The end view shows two round openings, the particulate inlet and outlet. |
| Bottom Part B | 83.0 × 82.9 × 26.7 | Open rounded ring. The middle is empty, so air can pass through the base. |
| Bottom Part A | 71.5 × 71.2 × 11.5 | Thin round grill plate with a ring of mounting holes. This sits in the airflow path. |

The new shell is 98 × 94 mm in plan, a few millimetres outside the original top, so a 70 mm battery and a wire gutter both fit. Height is the only large change, and only where the battery needs it.

## Modules the shell must hold

Sizes are the ones in [`../README.md`](../README.md). The controller bay is the larger of the two boards (LOLIN32 58 × 25.4 mm, ESP32-S3 57.15 × 27.94 mm), so one body fits either. The CO2 bay fits the SCD30 (35 × 23 × 7 mm); an SCD41 (13.4 × 21.6 mm) uses the same standoffs. The battery cradle uses the upper end of the measured pack, 70 × 57 × 22 mm.

| Module | Footprint used |
| --- | --- |
| Controller | 58 × 28 mm |
| SPS30 | 41 × 41 × 12 mm |
| SCD30 (or SCD41) | 35 × 23 × 7 mm |
| SGP41 | 25.4 × 17.8 mm |
| SHT45 | 25.3 × 17.8 × 4.8 mm |
| BQ25185 | 29.2 × 19.1 mm, USB-C toward the side wall |
| TPS63020 | 26 × 18 mm |
| 1S3P pack | 70 × 57 × 22 mm envelope |

## Soldered wiring

Boards sit on 4.8 mm standoffs. That clears a solder fillet on the underside and lets a wire leave the pad without rubbing the floor. There is no header stack, so the bay stays at the part height.

Each bay has a gutter about 8 mm wide beside the solder edge. That is the bend room for 24 AWG (a bend radius of about 2 mm, with extra length so the joint is not the bend). Along the gutter are cable-tie bridges (a bar with a slot) and a strain-relief bar (wires pass under a 2 mm bridge) at the exit of the bay. Tie the harness at those bars, at the solar connector solder cups, and again before the USB cutout so a tug on the panel connector does not pull a sensor pad.

Keep the SPS30 inlet and outlet leads out of the cool bay. Run them in the exhaust-side gutter.

## Solar connector

**M8 female panel receptacle, front mount, solder cups, IP67.** The part used for the hole is an IEC 61076-2-104 A-coded **2-pin** socket with an **M8×1** thread, the same class as the Westsam “M8 A-code 2-pin female front mount socket, solder, M8×1.0” ([product page](https://en.westsaim.com.cn/Products_1/118.html)). Two pins are enough for VIN and GND and this exact part is sold. A 3-pin or 4-pin M8 is more common in catalogues, but it is not required.

The shell hole is **Ø8.2 mm**, which lets the M8×1 thread through a 2.4 mm floor. Above the hole, inside the box, a **Ø14 mm × 12 mm** keep-out clears the nut (about 11 mm across the flats) and the solder cups. Tie the two soldered leads before they leave that pocket. The hole is on the bottom, offset from the particulate ports (front corner on variant 2, so it misses the battery).

## The three variants

### Variant 1 — rear battery

Height 106 mm. The pack stands in a rear pocket (70 mm tall) with two strap bars. The SPS30 sits on the floor over two 16 mm ports; its exhaust leaves through side louvers. SHT45 and SGP41 share a front bay behind a separate divider wall, with their own side vents. SCD30 is mid-height on the opposite wall from the exhaust. ESP32, BQ25185, and TPS63020 are on the top shelf. The USB-C slot is on the lower side wall.

- Airflow: inlet faces down, exhaust leaves sideways. Short ducts.
- Heat: divider helps, but the battery and the electronics share one volume with the sensors.
- Service: one cavity, lid off, everything visible. The standing battery is the awkward piece.
- Print: shortest shell. Floor ports need no support if the grill is a separate part.
- Size: closest to the original 82 mm height.

### Variant 2 — battery plinth

Height 122 mm. The pack lies on the floor. Particulate air does **not** pass through that floor: inlet and outlet are 12 mm side holes so the pack does not block them. Sensors sit on a deck above the pack. Electronics are on top. USB-C is high on the side wall. The M8 hole is in the front bottom corner, clear of the pack.

- Airflow: sideways inlet, good for rain, longer path than variant 1.
- Heat: the pack is low and away from the ESP32, but it is still under the sensor deck.
- Service: battery is easy to strap down. Reaching the deck means unplugging nothing (wires are soldered), so leave service loops in the gutter.
- Print: taller. Side holes are simple.
- Size: 16 mm taller than variant 1.

### Variant 3 — sensor pod

Height 130 mm. The lower half is only sensors: SPS30 on the floor ports, SHT45 and SGP41 behind the divider, SCD30 on the vented wall. A bulkhead separates that pod from the upper bay, which holds the pack and the electronics. USB-C is just above the joint. Solar stays on the bottom, offset from the ports.

- Airflow: same down-inlet as variant 1, and the exhaust path stops at the bulkhead.
- Heat: best of the three. The cool bay is low, walled off from the SPS30 exhaust side, and the ESP32, charger, and TPS63020 are above the bulkhead.
- Service: two zones. The lid opens the electronics. The sensor pod is deeper.
- Print: tallest. Same floor-down shell as variant 1.
- Size: 130 mm plus the 6 mm lid.

**Use variant 3** if this box will sit in the sun. Use variant 1 if the smaller print matters more than the thermal wall. Variant 2 is the one to pick when the pack must come out without disturbing the SPS30.

## Print

Outdoor, so not PLA. **ASA** if the printer can hold about 90–100 °C on the bed and the part will see full sun. **PETG** if ASA is not available; it is tougher to print cleanly but handles weather. Natural or light grey, 0.2 mm layers, 4 perimeters, 20% gyroid, no supports on the shell if it is printed floor-down. Print the grill and the divider flat. The lid prints rim-down.

The shell is the body. The grill covers the floor ports (variants 1 and 3). The divider is the thermal wall; it is a separate part so it can be glued or screwed to the bosses after the wires are in.

## Renders

| View | Variant 1 | Variant 2 | Variant 3 |
| --- | --- | --- | --- |
| Isometric | [variant-1-isometric.png](renders/variant-1-isometric.png) | [variant-2-isometric.png](renders/variant-2-isometric.png) | [variant-3-isometric.png](renders/variant-3-isometric.png) |
| Inside | [variant-1-inside.png](renders/variant-1-inside.png) | [variant-2-inside.png](renders/variant-2-inside.png) | [variant-3-inside.png](renders/variant-3-inside.png) |
| Exploded | [variant-1-exploded.png](renders/variant-1-exploded.png) | [variant-2-exploded.png](renders/variant-2-exploded.png) | [variant-3-exploded.png](renders/variant-3-exploded.png) |

Front, back, side, top, and bottom PNGs use the same name pattern. Comparison sheet: [renders/comparison.png](renders/comparison.png) and [renders/comparison.pdf](renders/comparison.pdf).

Colours in the renders: blue SPS30, green SHT45, yellow SGP41, orange SCD30, purple ESP32, red BQ25185, teal TPS63020, grey battery, dark nut for the M8 receptacle, olive for a 1S PCM placeholder.

Browser assemblies, one mesh per part, are in [`assembly/`](assembly/index.html). Open `assembly/index.html` (GitHub raw via raw.githack works; a local `file://` page will not load the GLB). The shell can be faded or hidden. Extra PNGs per variant: `variant-N-legend.png` (modules only, with a colour key), `variant-N-section.png` (shell cut away), and labelled `variant-N-front.png`, `variant-N-side.png`, `variant-N-top.png`.

## Open points

- The shell is a new body in the original style. It is not a cut of the AirGradient STL, so screw bosses from the original kit do not transfer.
- The solar part is a 2-pin M8×1 front-mount receptacle, hole Ø8.2 mm. If the part in hand is a 3-pin or 4-pin M8 of the same thread, the hole does not change; use two pins and leave the others open.
- The CO2 standoffs fit an SCD30. An SCD41 sits in the same bay with a shorter footprint.
- The pack still needs a 1S PCM in series. The cradle does not include a PCM clip.
