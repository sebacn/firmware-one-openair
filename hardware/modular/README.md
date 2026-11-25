# Modular outdoor monitor

A DIY outdoor air-quality monitor wired from off-the-shelf modules, instead of the AirGradient Open Air main PCB in [`../open-air/`](../README.md). Two variants, one per MCU board. Both put every sensor on one I2C bus.

This schematic is new work in this fork. It is not a redraw of an AirGradient board. The firmware it targets is the AirGradient One Open Air sketch, which remains under CC BY-SA 4.0. These hardware notes are under the same license.

Revision **A**, 2026-11-25.

| Variant | Project | MCU |
| --- | --- | --- |
| A | [`variant-a-esp32-d1mini/modular-a.kicad_pro`](variant-a-esp32-d1mini/modular-a.kicad_pro) | ESP32-WROOM-32 on a WeMos D1 Mini ESP32 / LOLIN32-mini class board |
| B | [`variant-b-esp32s3-n16r8/modular-b.kicad_pro`](variant-b-esp32s3-n16r8/modular-b.kicad_pro) | ESP32-S3-DevKitC-1 class, module N16R8 (16 MB quad flash, 8 MB octal PSRAM) |

Printable schematic, both sheets, landscape A4: [`schematic-modular-A4.pdf`](schematic-modular-A4.pdf).

Symbols are embedded in each `.kicad_sch`. There is no PCB. `hardware/modular/tools/gen_schematics.py` regenerates the sheets; the checked-in schematics are what KiCad ERC was run on.

## What the firmware in this change does

`pio run -e modular-esp32-d1mini` and `pio run -e modular-esp32s3-n16r8` select the pins below. The existing `esp32-c3` environment is unchanged.

Selecting an environment does three things in `examples/OneOpenAir/OneOpenAir.ino`:

- `Wire.begin` uses that variant's SDA/SCL, then `Wire.setClock(100000)` and a 200 ms clock-stretch timeout (SCD30 can stretch for up to 150 ms).
- `SPS30_5V_EN_PIN` is driven high at startup so the 5 V boost stays on. Drive it low later to remove power from the SPS30.
- `VBAT_ADC_PIN` is read with 11 dB attenuation. The log line multiplies the pin voltage by 2 for the 100 kΩ / 100 kΩ divider.

It does **not** switch the SPS30 driver to I2C, and it does **not** auto-detect SCD30 versus SCD41. Those stay future firmware work. The sheet is drawn for I2C anyway: SPS30 `SEL` is tied to GND, and either CO2 module can be fitted. Until that firmware exists, the sketch still probes SPS30 and the SenseAir S8 on a UART (`Serial0` on the ESP32-C3, `Serial2` on these two boards). Leave the `Serial2` pins unconnected.

| Board | `Serial2` default pins (Arduino-ESP32 2.0.17) | Leave unconnected |
| --- | --- | --- |
| Variant A, ESP32 | RX GPIO16 (D4), TX GPIO17 (D3) | D3, D4 |
| Variant B, ESP32-S3 | RX GPIO19, TX GPIO20 | GPIO19, GPIO20 (these are also the native USB pins) |

The sketch still drives GPIO3, GPIO4 and GPIO5 while it looks for a cellular card. Do not wire those pins on either variant.

## Modules

AliExpress listing pages did not return usable HTML to this environment (they block non-browser clients). Pinouts and voltages below are from the manufacturer's datasheet or, for the charger, from the Adafruit 6106 Eagle schematic. Confirm the silkscreen on the board you actually received before soldering.

| Name | Function | Interface | I2C address | Voltage | Source used |
| --- | --- | --- | --- | --- | --- |
| ESP32 D1 Mini / LOLIN32-mini class | Variant A controller. ESP32-WROOM-32. | GPIO, I2C, ADC1 | — | 3.3 V on the 3V3 pin | Arduino-ESP32 2.0.17 `variants/d1_mini32/pins_arduino.h` and `variants/d32/d32_core.h` |
| ESP32-S3-DevKitC-1 N16R8 | Variant B controller. 16 MB quad SPI flash, 8 MB octal PSRAM. | GPIO, I2C, ADC1 | — | 3.3 V on the 3V3 pin | Espressif ESP32-S3-WROOM-1 datasheet v1.8; DevKitC-1 v1.1 user guide; Arduino-ESP32 `variants/esp32s3/pins_arduino.h` |
| SGP41 module | VOC / NOx | I2C | 0x59 | 3.3 V (sensor abs. max 3.6 V) | Sensirion SGP41 datasheet. Listing [1005009523201465](https://pl.aliexpress.com/item/1005009523201465.html) was not fetched. |
| SCD30 module | CO2, plus its own T/RH. Fit this **or** the SCD41. | I2C. `SEL` to GND. | 0x61 | 3.3 V (datasheet range 3.3–5.5 V; do not use 5 V here) | Sensirion SCD30 datasheet and interface description. Listing [1005012719322072](https://pl.aliexpress.com/item/1005012719322072.html). |
| SCD41 module | CO2. Fit this **or** the SCD30. | I2C | 0x62 | 3.3 V (sensor 2.4–5.5 V, peak about 205 mA at 3.3 V) | Sensirion SCD4x datasheet. Listing [1005009897956849](https://pl.aliexpress.com/item/1005009897956849.html). |
| SHT45 module | Temperature / humidity for compensation | I2C | 0x44 for SHT45-AD1B | 3.3 V (sensor abs. max 3.6 V) | Sensirion SHT4x datasheet. Listing [1005012546290193](https://pl.aliexpress.com/item/1005012546290193.html). |
| SPS30 | Particulate matter. I2C mode. | I2C, `SEL` to GND before power-up | 0x69 | 5 V ±10% on VDD. Logic is 3.3 V (VIH min 2.31 V). Max 100 kHz. | Sensirion SPS30 datasheet v2.0 (June 2023). Listing [1005009874188645](https://pl.aliexpress.com/item/1005009874188645.html). |
| BQ25185 + 5 V boost | USB-C / solar charger, 1S Li-ion, TPS61023 5 V boost for the SPS30 | Power. `EN` is active high. | — | Solar/DC operating range 3.6–18 V (abs. max 25 V, OVP about 18.5 V). Pack is 1S. Boost output 5 V. | TI BQ25185 datasheet Rev. B; Adafruit 6106 Eagle schematic and learn guide. Listing [1005008650602873](https://pl.aliexpress.com/item/1005008650602873.html) treated as a 6106 clone. |
| TPS63020 module | 3.3 V buck-boost for the ESP32 3V3 pin and every 3.3 V sensor | Power. `EN` tied to VIN. | — | Input from VBAT (about 3.0–4.2 V). Output set to 3.3 V. TI input range 1.8–5.5 V. | Listing [1005001949409346](https://pl.aliexpress.com/item/1005001949409346.html) was not fetched. Treat it as a TPS63020 module with a potentiometer. |
| 1S pack | 2 or 3 18650 cells in parallel, one 1S protection circuit | Battery | — | 3.0–4.2 V | — |
| 10 kΩ NTC, β(25/85) = 3435 K | Cold/hot charge cutoff, body on the cells | Analog, charger `TS` to GND | — | — | BQ25185 TS bias is specified for this NTC |

Product photos were not stored. The AliExpress pages blocked the fetch, and the Sensirion, Adafruit and Espressif product photos found from here are not clearly licensed for redistribution. No `images/` directory was added.

## Wiring

Shared nets on both sheets: `SDA`, `SCL`, `+3V3`, `ESP_3V3` (the ESP32 side of JP1), `GND`, `VBAT`, `+5V_SPS`, `VIN_SOLAR`, `BOOST_EN`, `SPS_EN`, `VBAT_SENSE`, `TS`.

I2C pull-ups are **R4 and R5, 4.7 kΩ, to +3V3, and they are fitted.** Decision:

- The SPS30 datasheet requires external pull-ups (their example is 10 kΩ) and the sensor has none.
- The SCD30's only pull-ups are internal 45 kΩ to its own 3 V rail. That is too weak to be the only pull-up on a cabled bus, and it is not a 5 V pull-up. Powering the SCD30 from 3.3 V keeps the bus at 3.3 V. Do not power it from 5 V.
- SGP41, SCD41 and SHT45 bare sensors also require external pull-ups. The breakout you receive may already have 4.7–10 kΩ. A 4.7 kΩ pair in parallel with one extra 10 kΩ pair is still about 3.2 kΩ, above the roughly 1 kΩ floor for a 3 mA sink at 3.3 V. If you measure the idle bus and the equivalent is under about 2 kΩ, remove either the schematic pair or the module pair.
- Never pull SDA or SCL up to 5 V.

Bus speed is 100 kHz. That is the SPS30 maximum and the SCD30 maximum. Sensirion recommends 50 kHz or less for the SCD30; this revision follows the 100 kHz spec and relies on clock stretching. Keep cables short. Sensirion suggests well under 10 cm for SPS30 on I2C.

`JP1` is in series with the 3.3 V feed to the ESP32 `3V3` pin.

- Fit JP1 for battery operation.
- Remove JP1 before plugging a USB cable into the ESP32 board.
- Do not power the board from USB and from the 3V3 pin at the same time. The onboard regulator and the TPS63020 will fight.
- Do not connect `+5V_SPS` to the ESP32 `5V` / VBUS pin. That 5 V rail is only for the SPS30.

### Variant A — `modular-esp32-d1mini`

PlatformIO board `wemos_d1_mini32` (classic ESP32-WROOM-32, 4 MB flash). A LOLIN D32 (`lolin_d32`) is the same chip; its silkscreen prints IO numbers instead of D0/D1/D2/A0, and the GPIO numbers in this table still apply. Do not also connect a battery to a D32's own charger pad.

| Signal | GPIO | Silkscreen on a D1 Mini ESP32 | Notes |
| --- | --- | --- | --- |
| I2C SDA | 21 | D2 | Arduino `SDA` in `d32_core.h` |
| I2C SCL | 22 | D1 | Arduino `SCL` |
| SPS30 5 V enable | 26 | D0 | Active high. Series 1 kΩ (R3) to the boost `EN`. |
| VBAT ADC | 36 | A0 | ADC1 channel 0, input only. 11 dB attenuation. |
| ESP32 3V3 | — | 3V3 | From JP1 / TPS63020. Not from USB at the same time. |
| ESP32 5V | — | 5V | No connect. |
| GND | — | G | Common ground. |

`A0` in this Arduino variant is GPIO36 with no extra onboard divider (`d32_core.h` sets `A0 = 36`). The 100 kΩ / 100 kΩ divider on the sheet is the only divider. If your clone's A0 already has a divider, do not stack a second one; measure it first.

Build flags: `-D I2C_SDA_PIN=21 -D I2C_SCL_PIN=22 -D SPS30_5V_EN_PIN=26 -D VBAT_ADC_PIN=36 -D I2C_CLOCK_HZ=100000 -D WIRE_TIMEOUT_MS=200 -D VBAT_DIVIDER_NUM=2 -D VBAT_DIVIDER_DEN=1`.

### Variant B — `modular-esp32s3-n16r8`

PlatformIO board `esp32-s3-devkitc-1` with `board_build.arduino.memory_type = qio_opi`, quad flash mode, `board_build.psram_type = opi`, 16 MB flash size, and `-DBOARD_HAS_PSRAM`. The linked SDK in a successful build is the `qio_opi` package, which matches Espressif's N16R8 description: 16 MB **quad** SPI flash and 8 MB **octal** SPI PSRAM (not octal flash). GPIO8 and GPIO9 are this variant's default Wire pins.

The partition table is the existing 4 MB `partitions.csv`, so the OTA layout stays the same and the upper 12 MB of flash is unused. The stock board json is still titled "DevKitC-1-N8 (No PSRAM)"; the memory settings above override that.

| Signal | GPIO | DevKitC-1 silkscreen | Notes |
| --- | --- | --- | --- |
| I2C SDA | 8 | IO8 | Default `SDA` |
| I2C SCL | 9 | IO9 | Default `SCL` |
| SPS30 5 V enable | 7 | IO7 | Active high. GPIO10 is this variant's default SPI SS, so the enable is not on GPIO10. |
| VBAT ADC | 6 | IO6 | ADC1 channel 5. Usable while Wi-Fi is on. |
| ESP32 3V3 | — | 3V3 | From JP1 / TPS63020. |
| ESP32 5V | — | 5V | No connect. |
| GND | — | GND | Common ground. |

Do not use, on an N16R8:

- GPIO33, GPIO34, GPIO35, GPIO36, GPIO37. Espressif's DevKitC-1 v1.1 guide says GPIO35–37 are taken by octal SPI flash/PSRAM. The octal PSRAM data lines also use GPIO33–34, so those are left unused too.
- GPIO0, GPIO3, GPIO45, GPIO46 (strapping). GPIO45 must stay low at boot on a 3.3 V flash part.
- GPIO43 / GPIO44 (UART0, the USB-UART port) and GPIO19 / GPIO20 (native USB, and also this firmware's `Serial2` probe).

Build flags: `-D I2C_SDA_PIN=8 -D I2C_SCL_PIN=9 -D SPS30_5V_EN_PIN=7 -D VBAT_ADC_PIN=6` plus the same clock, timeout and divider macros as variant A. USB CDC on boot is left off, matching a DevKitC-1 whose programming port is the USB-UART bridge. A clone with only the native USB connector needs `-D ARDUINO_USB_CDC_ON_BOOT=1` added before it will print on that connector.

## Power

```
USB-C on the charger module ──┐
                               ├── BQ25185 ── BAT ── 1S pack (2–3× 18650 parallel, protected)
Solar / DC on VIN ────────────┘     │
                                    ├── VBAT ── TPS63020 EN+VIN ── 3.3 V ── JP1 ── ESP32 3V3 and all 3.3 V sensors
                                    └── internal SYS ── TPS61023 ── +5V_SPS ── SPS30 VDD
                                              EN ← GPIO, active high, 1 kΩ series
```

Adafruit's 6106 schematic (the file `Adafruit bq25185 with 5V Boost Breakout.sch` in their GitHub repo) was used as the clone's pinout:

- The 8-pin header brings out VIN, VBUS, D−, D+, GND, VBAT, +5V and EN. **SYS is not on the header.** The TPS61023 input is SYS, inside the module. The TPS63020 is therefore fed from **VBAT**, the pin that is actually available. A missing or protection-open cell means the 3.3 V rail does not run, even if USB is plugged into the charger. The 5 V boost can still run, because it is powered from SYS internally.
- `EN` has a 100 kΩ pull-up to SYS (about 3.0 V on battery, about 4.5 V when an input is present). TPS61023 enables above 1.2 V and shuts off below about 0.4 V. R3 (1 kΩ) lets a 3.3 V GPIO override that pull-up. While the GPIO is high-Z at reset, the 100 kΩ pulls EN up and the SPS30 powers on; the injected current into the ESP32 pin is under about 20 µA. Do not replace R3 with a short.
- `TS/MR` is tied to GND through a fitted 10 kΩ (R16 on the Adafruit board) and is **not** on the header. That fixed resistor holds the pin at the nominal point and disables the temperature cutoff. For a cold-charge cutoff, remove that 10 kΩ and wire RT1 from the TS pad to GND, with the thermistor body on the cells. A clone that copies this board has the same limitation unless its silkscreen shows a TS/TH pin.
- Charge current on the Adafruit board defaults to 1 A, which is fine for two or three parallel 18650s. Adafruit documents a 6 hour safety timer that is not removable. A deeply discharged 3-cell parallel pack at 1 A may not finish in one session.
- `/CE` is tied so charging is enabled. Leave it that way.

TI's electrical table does not publish the cutoff in °C. With the 38 µA TS bias (`ITSMR`), VCOLD ≈ 1.01 V and VHOT ≈ 0.115 V, a 10 kΩ β=3435 NTC is roughly 2 °C at the cold entry and roughly 60 °C at the hot entry. That is a calculation from those three numbers, not a line in the datasheet. A fixed 10 kΩ from TS to GND disables both cutoffs.

Solar open-circuit voltage should stay under 18 V. The charger's operating range goes to 18 V and it trips input OVP around 18.5 V (absolute maximum on IN is 25 V). A "6 V" panel (Voc typically under 12 V) fits. A "12 V" panel must be checked for Voc.

SPS30 supply current from the same datasheet: measurement 45–65 mA, fan start at most 80 mA for the first 200 ms. That is under the TPS61023's roughly 200 mA hard-start limit that Adafruit warns about. Enable the boost with the sensor idle, then start a measurement.

The battery divider is R1 = R2 = 100 kΩ from VBAT to GND, with C1 = 100 nF from the midpoint to GND. Pin voltage is half the pack voltage, so 4.2 V becomes 2.1 V, inside the ESP32 ADC range at 11 dB. The reading is approximate; the ESP32 ADC is not linear.

Set the TPS63020 module's output to 3.3 V and measure it **before** it touches the ESP32. If the module already ties EN to VIN, do not also drive that pad from a GPIO; the sheet shows EN tied to VBAT, which is the same node.

## Connectors

Wire the SCD30 by the names printed on its PCB: VDD, GND, TX/SCL, RX/SDA, RDY, PWM, SEL. The sheet uses that order and ties SEL to GND (I2C). RDY and PWM are no-connect. The datasheet figure is the reference; do not assume a photo's left-to-right order if the silkscreen disagrees.

SGP41, SHT45 and SCD41 are drawn as 4-pin modules: VCC, GND, SCL, SDA, all at 3.3 V. That matches the usual carrier. If your SCD41 board's VIN pin only feeds a 3.3 V LDO, 3.3 V on VIN can be below the dropout; use that board's 3V3 pin instead, or confirm the regulator. Do not feed 5 V into an SGP41 or SHT45 carrier that has no regulator. Both sensors are destroyed above 3.6 V.

SPS30 mating plug is a JST ZHR-5. Pin order from the datasheet, looking at the connector with pin 1 at the end Sensirion marks: 1 VDD (5 V), 2 SDA, 3 SCL, 4 SEL (to GND), 5 GND. SEL must be low at the moment power is applied. The metal shell is connected to pin 5 inside the sensor; don't let the shell sit at a different potential than GND.

## ERC

KiCad 9.0.9 `kicad-cli sch erc` on both projects: 0 errors, 0 warnings. The project file sets `lib_symbol_issues` to ignore, because every symbol is embedded in the sheet and the `Modular` / `Device` / `power` nicknames are not in the global library table. Re-run with:

```
kicad-cli sch erc --severity-error --severity-warning hardware/modular/variant-a-esp32-d1mini/modular-a.kicad_sch
kicad-cli sch erc --severity-error --severity-warning hardware/modular/variant-b-esp32s3-n16r8/modular-b.kicad_sch
```

## Build

From the repository root, with PlatformIO and `espressif32@6.13.0` (Arduino-ESP32 2.0.17, same pin as the ESP32-C3 environment):

```
pio run -e modular-esp32-d1mini
pio run -e modular-esp32s3-n16r8
```

A build on 2026-11-25, after `git submodule update --init --recursive`:

| Environment | Result | RAM | Flash |
| --- | --- | --- | --- |
| `modular-esp32-d1mini` | success | 79516 / 327680 bytes (24.3%) | 1809929 / 1966080 bytes (92.1%) |
| `modular-esp32s3-n16r8` | success | 74920 / 327680 bytes (22.9% of internal SRAM; the 8 MB PSRAM is not in this number) | 1700597 / 1966080 bytes (86.5%) |
| `esp32-c3` (unchanged environment, rebuilt as a check) | success | 68844 / 327680 bytes (21.0%) | 1781418 / 1966080 bytes (90.6%) |

The S3 image was linked against the `qio_opi` SDK libraries and `esptool` was invoked with `--flash_size 16MB`. The app partition is still the 4 MB Open Air slot (`0x1E0000` bytes), which is why the flash percentage is against 1.9 MB rather than 16 MB.
