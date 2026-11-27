# Modular outdoor enclosure

The enclosure keeps the original AirGradient Open Air cover and base ring and replaces the grill with one printed carrier. There is no battery in the box. The dev board is powered from its USB socket, or from the M8 plug when USB is unplugged. Its 5 V pin feeds the SPS30. Its 3.3 V pin feeds the I2C boards.

## Carrier

| Part | File | Change from the original STL |
| --- | --- | --- |
| Cover | [`reference-outdoor/`](reference-outdoor/README.md) Top Part C, 91.5 × 85.0 × 81.9 mm | None. Cap up, sleeve down over the ring. |
| Base ring | Bottom Part B, 83.0 × 82.9 × 26.7 mm | None. The lip that held the grill now holds the carrier. |
| Carrier | [`carrier/carrier.stl`](carrier/carrier.stl), from [`carrier.scad`](carrier.scad) | New. Same 71 mm seat as the grill, vents, clips, and the M8 hole. |

Assembly model: [`assembly/modular.glb`](assembly/modular.glb). Viewer: [`assembly/index.html`](assembly/index.html). Renders: [`renders/modular-exploded.png`](renders/modular-exploded.png), [`renders/modular-section.png`](renders/modular-section.png), [`renders/modular-front.png`](renders/modular-front.png), [`renders/modular-side.png`](renders/modular-side.png), and [`renders/modular-top.png`](renders/modular-top.png).

How the parts sit, looking down, z up:

- SHT45, SGP41, and SCD30 lie flat. The sensor face is the bottom face, over a field of 3.2 mm vents. SHT45 is on the left, away from the ESP32 and the SPS30.
- SPS30 stands. The inlet is the bottom edge, over a 34 × 8 mm slot. The outlet is the top edge, open into the cover, not ducted back to the inlet.
- The dev-board bay is 28 × 13 × 58 mm, the larger of a LOLIN32 (58 × 25.4) and an ESP32-S3 board (57.15 × 27.94). A D1 mini fits the same channel. USB is the bottom edge, over an 18 × 10 mm slot so a cable can come up from below.
- M8 A-coded 4-pin panel connector, thread M8×0.5. The hole is Ø8.2 mm and faces down, so the plug hangs and water runs off. The nut pocket is Ø16 × 6 mm on the inside of the plate. Pin 1 brown is 5 V in, pin 2 white is VBAT sense, pin 3 blue is GND, pin 4 black is VSOL sense.

Minimum gap between the part boxes is **0.9 mm**, SPS30 to SCD30. The next tight pairs are ESP32 to M8 at 1.0 mm and SPS30 to SHT45 at 1.2 mm. No part box intersects another. No sample point of a part box falls inside the cover plastic or the base ring. A few sample points of the SCD30 and the M8 nut land on the carrier seats they are meant to touch (the standoff tops and the nut pocket).

### Print

Print the carrier in PETG or ASA, 0.2 mm layers, four perimeters, 20% infill. Flange down. The clips and posts are vertical, so it does not need support. The original cover and base print as AirGradient published them, cap and lip oriented as in the STL after the cover is turned cap-up.

### Assembly order

1. Drop the carrier onto the base lip, flange down, M8 nose pointing out the bottom.
2. Fit the M8 receptacle through the Ø8.2 mm hole from below and tighten the nut in the Ø16 mm pocket. Solder the four leads before the boards go in.
3. Clip the SPS30 in, inlet down over the slot. Seat the SHT45, SCD30, and SGP41 on their posts, sensor faces down. Slide the dev board into the channel, USB over the cable slot.
4. Run the I2C and 5 V leads in the gutters and through the three tie bars. Keep the SHT45 leads on the left of the thermal wall.
5. Slide the original cover on from above and close it with the original four screws.
