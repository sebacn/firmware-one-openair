# Modular outdoor monitor

A DIY outdoor air-quality monitor wired from off-the-shelf modules, instead of the AirGradient Open Air main PCB in [`../open-air/`](../README.md). Two variants, one per MCU board. Both put every sensor on one I2C bus.

This schematic is new work in this fork. It is not a redraw of an AirGradient board. The firmware it targets is the AirGradient One Open Air sketch, which remains under CC BY-SA 4.0. These hardware notes are under the same license.

Revision **C**, 2026-11-26. The dev board is powered from its own USB connector. Its 5 V pin feeds the SPS30. Its 3.3 V pin feeds every 3.3 V module.

| Variant | Project | MCU |
| --- | --- | --- |
| A | [`variant-a-esp32-d1mini/modular-a.kicad_pro`](variant-a-esp32-d1mini/modular-a.kicad_pro) | WEMOS LOLIN32 V1.0.0 (micro-USB) or an ESP32 D1 mini. Same I2C pins. USB power only; leave the LOLIN32 battery socket empty. |
| B | [`variant-b-esp32s3-n16r8/modular-b.kicad_pro`](variant-b-esp32s3-n16r8/modular-b.kicad_pro) | ESP32-S3-WROOM-1 N16R8 on an AI-S3 / DevKitC-1 clone (16 MB quad flash, 8 MB octal PSRAM). USB power only. |

Printable schematic, both sheets, landscape A4: [`schematic-modular-A4.pdf`](schematic-modular-A4.pdf).

Symbols are embedded in each `.kicad_sch`. There is no PCB. `hardware/modular/tools/gen_schematics.py` regenerates the sheets; the checked-in schematics are what KiCad ERC was run on.

## What the firmware in this change does

`pio run -e modular-lolin32` (same flags as `modular-esp32-d1mini` and `modular-lolin32-lite`) and `pio run -e modular-esp32s3-n16r8` select the pins below. The existing `esp32-c3` environment is unchanged.

Selecting an environment does two things in `examples/OneOpenAir/OneOpenAir.ino`:

- `Wire.begin` uses that variant's SDA/SCL, then `Wire.setClock(100000)` and a 200 ms clock-stretch timeout (SCD30 can stretch for up to 150 ms).
- `SPS30_ALWAYS_ON=1` keeps the SPS30 measurement running. VDD is wired to the dev-board 5 V pin, so the sensor is powered whenever USB is plugged in. The modular envs do not define `SPS30_5V_EN_PIN` or `VBAT_ADC_PIN`. Those two hooks stay in the sketch behind `#ifdef`, for a board that actually has a 5 V switch or a pack divider. Sensor intervals are unchanged: SCD30 at 2 s, SCD41 on the library's periodic measurement.

On these environments the sketch probes I2C for a CO2 sensor and reads the SPS30 at 0x69. The ESP32-C3 build does not. Details are in the startup log: SCD30 at 0x61 (continuous, 2 s, ASC on), SCD41 at 0x62 (periodic, ASC on), or neither. If both answer, SCD41 is used and SCD30 is left idle. SHT stays the temperature source; CO2-sensor T/RH is used only when no SHT answers. The inherited UART probe still exists for the C3 board. On these MCUs that probe is `Serial2` and nothing on the harness should be wired to it.

| Board | `Serial2` default pins (Arduino-ESP32 2.0.17) | Leave unconnected |
| --- | --- | --- |
| Variant A, LOLIN32 V1.0.0 | RX GPIO16, TX GPIO17 | GPIO16, GPIO17 |
| Variant B, ESP32-S3 | RX GPIO19, TX GPIO20 | GPIO19, GPIO20 (these are also the native USB pins) |

The sketch still drives GPIO3, GPIO4 and GPIO5 while it looks for a cellular card. Do not wire those pins on either variant.

## Modules

AliExpress listing pages did not return usable HTML to this environment (they block non-browser clients). Pinouts and voltages below are from the manufacturer's datasheet or the board pinout cited in the row. Confirm the silkscreen on the board you actually received before soldering.

Rev C does not fit a BQ25185 charger, a TPS63020 buck-boost, a 1S3P LG MH1 pack, a solar/DC input, a battery NTC, or a VBAT divider. Earlier sheets had those parts. This bill of materials does not.

| Name | Function | Interface | I2C address | Voltage | Source used |
| --- | --- | --- | --- | --- | --- |
| WEMOS LOLIN32 V1.0.0 | Variant A controller. ESP32-WROOM-32. 58 × 25.4 mm (earlier photo print 57.9 × 25.6 mm). Powered from its micro-USB. | GPIO, I2C | — | USB in. Header **5V** is VBUS out. Header **3V3** is the ME6211 output. | Archived Wemos LOLIN32 page, [espboards.dev LOLIN32](https://www.espboards.dev/esp32/lolin32/), and `images/wemos-lolin32.png`. |
| ESP32 D1 mini | Same firmware image as the LOLIN32 (`modular-esp32-d1mini`). GPIO21 SDA, GPIO22 SCL. | GPIO, I2C | — | USB in. Silkscreen **5V** (some boards print **5V0**) is VBUS. Silkscreen **3V3** (some print **3.3V**) is the regulator output. | [espboards.dev D1 mini ESP32](https://www.espboards.dev/esp32/d1-mini32/). |
| ESP32-S3 N16R8 (AI-S3) | Variant B controller. 16 MB quad SPI flash, 8 MB octal PSRAM. Board 57.15 × 27.94 mm. Powered from its USB connector. | GPIO, I2C | — | USB in. Silkscreen **5V** is VBUS (about 4.6 V after the DevKitC-1 Schottky). Silkscreen **3V3** is the onboard LDO. | [YD-ESP32-S3 size](https://www.espboards.dev/esp32/yd-esp32-s3/), Espressif DevKitC-1 v1.1 schematic, and `images/esp32s3-n16r8.png`. |
| SGP41 module | VOC / NOx. Header VIN, 3.3V, GND, SCL, SDA. Adafruit 6455 outline 25.4 × 17.78 mm. | I2C | 0x59 | 3.3 V into VIN (breakout accepts 3–5 V) | Photo `images/sgp41.png`, Sensirion SGP41 datasheet, and Adafruit 6455 Eagle. Listing [1005009523201465](https://pl.aliexpress.com/item/1005009523201465.html). |
| SCD30 module | CO2, plus its own T/RH. Fit this **or** the SCD41. 35 × 23 × 7 mm. Header VDD, GND, TX/SCL, RX/SDA, RDY, PWM, SEL. | I2C. `SEL` open or to GND. | 0x61 | 3.3 V (datasheet range 3.3–5.5 V; do not use 5 V here) | Photo `images/scd30.png` and Sensirion SCD30 datasheet. Listing [1005012719322072](https://pl.aliexpress.com/item/1005012719322072.html). |
| SCD41 module | CO2. Fit this **or** the SCD30. Header, label side, left to right: GND, VCC, SCL, SDA. Board 13.4 × 21.6 mm. | I2C | 0x62 | 3.3 V (sensor 2.4–5.5 V, peak about 205 mA at 3.3 V) | Photo `images/scd41.png` and Sensirion SCD4x datasheet. Listing [1005009897956849](https://pl.aliexpress.com/item/1005009897956849.html). |
| SHT45 module | Temperature / humidity. 25.3 × 17.8 × 4.8 mm. Header VIN, 3Vo, GND, SCL, SDA. Feed VIN from 3.3 V. 3Vo open. | I2C | 0x44 fixed | 3.3 V into VIN (seller allows 3.3–5 V; keep I2C at 3.3 V) | Seller card on `images/sht45.png` (marking MRS199A) and Sensirion SHT4x datasheet. Listing [1005012546290193](https://pl.aliexpress.com/item/1005012546290193.html). |
| SPS30 | Particulate matter. I2C mode. 41 × 41 × 12 mm (L × W × H). Header: VDD (5 V), SDA, SCL, SEL to GND, GND. | I2C, `SEL` to GND before power-up | 0x69 | 5 V ±10% on VDD, taken from the dev-board 5 V pin. Logic is 3.3 V (VIH min 2.31 V). Max 100 kHz. | Photo `images/sps30.png` and Sensirion SPS30 datasheet v2.0 (June 2023). Listing [1005009874188645](https://pl.aliexpress.com/item/1005009874188645.html). |
| R1, R2 | I2C pull-ups, 4.7 kΩ, from SDA and SCL to +3V3. | — | — | 3.3 V | Fitted on the sheet. See Wiring. |

## Photos and product pages

Every product-page URL and every photo URL below returned HTTP 200 when checked on 2026-11-25. Manufacturer and retailer images are hotlinked and are not copied into the repo. Photos of the modules in hand are stored under `images/`. Adafruit Learning System text is CC BY-SA; the shop JPEGs are only linked.

The AliExpress links are the purchase links from the original module list. The photos are of the official part or the closest official board, not of that exact AliExpress listing. Wemos does not sell a classic-ESP32 "D1 Mini"; the official ESP32-WROOM board in that family is the LOLIN D32, and the only image `wemos.cc` serves for it is a 16×16 thumbnail.

### SGP41

- This breakout: [`images/sgp41.png`](images/sgp41.png). Adafruit-style STEMMA QT clone. Header, with VIN at the bottom of the right-hand row in that photo and at the top of the schematic symbol: **VIN, 3.3V, GND, SCL, SDA**. Two 4-pin JST-SH connectors. Green LED marked `on`. A part marked 103 (10 kΩ) is the likely I2C pull-up pair.
- Adafruit's SGP41 board is product [6455](https://www.adafruit.com/product/6455), not 5839 (5839 is the OV5640 camera). The Eagle outline of [Adafruit SGP41 Gas Sensor Breakout rev A.brd](https://github.com/adafruit/Adafruit-SGP41-Gas-Sensor-Breakout-PCB/blob/main/Adafruit%20SGP41%20Gas%20Sensor%20Breakout%20rev%20A.brd), dimension layer, is **25.4 × 17.78 mm** (1.00 × 0.70 in). That is the reference size for this clone. The learn guide [pinouts](https://learn.adafruit.com/adafruit-sgp41-multi-pixel-gas-sensor-breakout/pinouts) page matches the header: VIN is the supply (same voltage as the logic, so 3.3 V here; the regulator also accepts 5 V), **3.3V is the regulator output and is left open**, SDA/SCL are level-shifted with 10 kΩ pull-ups, I2C address **0x59**.
- The chip does not compute an index. Sensirion's [SGP41 datasheet](https://sensirion.com/media/documents/5FE8673C/61E96F50/Sensirion_Gas_Sensors_Datasheet_SGP41.pdf) section 3.1 says to run `sgp41_execute_conditioning` for **10 s, and not longer than 10 s**, then feed the raw VOC and NOx ticks through the Gas Index Algorithm.
- Feed **VIN from 3.3 V** so the bus stays at 3.3 V. Do not tie the module's 3.3V pin to the rail.
- Sensor: [Sensirion SGP41](https://sensirion.com/products/catalog/SGP41). Photo: [webp](https://sensirion.com/media/portfolio/product/image/67113b8f-5ff8-4c9c-86bf-836bbd5cf902.webp).
- Purchase: [AliExpress 1005009523201465](https://pl.aliexpress.com/item/1005009523201465.html).

![SGP41 breakout, VIN 3.3V GND SCL SDA](images/sgp41.png)

### SCD30

- This module: [`images/scd30.png`](images/scd30.png), photographed on a centimetre grid. Sensirion's SCD30 datasheet gives the module size as **35 × 23 × 7 mm**. The 7-pin header, in datasheet order, is **VDD, GND, TX/SCL, RX/SDA, RDY, PWM, SEL**. The schematic symbol lists that order top to bottom.
- Leave **SEL unconnected or tie it to GND** for I2C. Either one selects I2C at address **0x61**. The sheet ties SEL to GND so the mode cannot float. RDY and PWM are no-connect. Supply range is 3.3–5.5 V; this monitor feeds VDD from 3.3 V. Keep I2C at **100 kHz or below**. 100 kHz is already the default on both modular environments. The SCD30 clock-stretches, which is why the Wire timeout is 200 ms.
- Sensor: [Sensirion SCD30](https://sensirion.com/products/catalog/SCD30). Photo: [webp](https://sensirion.com/media/portfolio/product/image/4b4053f1-f7ef-43d2-bfe0-b2f00cfe34ba.webp).
- Breakout of a different carrier: [Adafruit 4867](https://www.adafruit.com/product/4867). Photo: [JPEG](https://cdn-shop.adafruit.com/970x728/4867-07.jpg).
- Purchase: [AliExpress 1005012719322072](https://pl.aliexpress.com/item/1005012719322072.html).

![SCD30 module on a cm grid](images/scd30.png)

### SCD41

- Sensor: [Sensirion SCD41](https://sensirion.com/products/catalog/SCD41). Photo: [webp](https://sensirion.com/media/portfolio/product/image/0dbb13dc-abee-4dbf-a0d0-68cc881b5486.webp).
- Breakout: [Adafruit 5190](https://www.adafruit.com/product/5190). Photo: [JPEG](https://cdn-shop.adafruit.com/970x728/5190-06.jpg).
- Purchase: [AliExpress 1005009897956849](https://pl.aliexpress.com/item/1005009897956849.html).
- This module, measured from the photo below: PCB 13.4 × 21.6 mm. Header, left to right on the label side: **GND, VCC, SCL, SDA**. R1 and R2 are marked 103 (10 kΩ) and are the likely I2C pull-ups. C1 is the local bypass. U1 is the SCD41. The schematic symbol lists those four pins in that order, top to bottom.

![SCD41 module, header GND VCC SCL SDA](images/scd41.png)

![SCD41 on sensirion.com](https://sensirion.com/media/portfolio/product/image/0dbb13dc-abee-4dbf-a0d0-68cc881b5486.webp)

### SHT45

- This breakout (marking MRS199A): [`images/sht45.png`](images/sht45.png). Seller card on that image: 25.3 × 17.8 × 4.8 mm; supply 3.3–5 V with an onboard regulator; VLogic/Vcc 3–5 V; I2C address fixed at 0x44; accuracy ±1.0 %RH and ±0.1 °C; range −40 to +125 °C and 0–100 %RH; idle 80 nA excluding the regulator (the card also lists 0.4 µA average). Pins, in header order: **VIN, 3Vo, GND, SCL, SDA**, plus two 4-pin JST-SH (STEMMA QT / Qwiic) connectors.
- Feed **VIN from 3.3 V**. The I2C pull-ups follow that logic supply. 5 V on VIN can put 5 V on SDA/SCL. Leave **3Vo** open. It is the regulator output; do not tie it to the 3.3 V rail.
- Sensor: [Sensirion SHT45](https://sensirion.com/products/catalog/SHT45). Photo: [webp](https://sensirion.com/media/portfolio/series/image/07fb657d-331a-4652-b79f-0240926500f1.webp).
- Same sensor on an Adafruit carrier: [Adafruit 5665](https://www.adafruit.com/product/5665). Photo: [JPEG](https://cdn-shop.adafruit.com/970x728/5665-01.jpg).
- Purchase: [AliExpress 1005012546290193](https://pl.aliexpress.com/item/1005012546290193.html).

![SHT45 breakout, VIN 3Vo GND SCL SDA](images/sht45.png)

### SPS30

- This module: [`images/sps30.png`](images/sps30.png). 41 × 41 × 12 mm (L × W × H). Five-pin header: **VDD (5 V), SDA, SCL, SEL (tie to GND for I2C), GND**.
- Sensor: [Sensirion SPS30](https://sensirion.com/products/catalog/SPS30).
- Purchase: [AliExpress 1005009874188645](https://pl.aliexpress.com/item/1005009874188645.html).

![SPS30 module](images/sps30.png)

### WEMOS LOLIN32 V1.0.0

This is the variant A board the photo shows. Silkscreen reads LOLIN32 V1.0.0. ESP32-WROOM-32, micro-USB, a PH-2 battery socket, an onboard charger, a CHG LED, and a RESET button. The archived [Wemos LOLIN32 page](https://web.archive.org/web/20181114100348/wiki.wemos.cc/products:lolin32:lolin32) lists **58 × 25.4 mm** and a 500 mA charge current. An earlier marked photo of this board printed 57.9 × 25.6 mm, which is the same outline within about a millimetre. The photo below has no scale.

This monitor does not use the PH-2 socket or the onboard charger. Leave the socket empty. Power the board only from its micro-USB connector.

- Pinout drawing: [espboards.dev LOLIN32](https://www.espboards.dev/esp32/lolin32/).
- Purchase class: [AliExpress 1005008273255710](https://pl.aliexpress.com/item/1005008273255710.html).

![WEMOS LOLIN32 V1.0.0](images/wemos-lolin32.png)

### ESP32 D1 mini

`modular-esp32-d1mini` builds the same image as `modular-lolin32` (PlatformIO board `lolin32`, SDA GPIO21, SCL GPIO22). A physical ESP32 D1 mini brings those two GPIOs out as well, and its power pins are silkscreen **5V** (some prints **5V0**) and **3V3** (some prints **3.3V**). [espboards.dev](https://www.espboards.dev/esp32/d1-mini32/) draws pin 39 as `5V` / `5V0` ("5V from the USB connector") and pin 33 as `3V3` / `3.3V` ("3.3V power output from the on-board regulator"). Wemos-style boards use an ME6211-class regulator. Many clones fit an AMS1117-3.3 instead. Read the package on the board you have before trusting the current budget below.

### ESP32-S3-DevKitC-1 N16R8

- This board: [`images/esp32s3-n16r8.png`](images/esp32s3-n16r8.png). Purple AI-S3, two USB-C ports labelled COM and USB, RGB LED on GPIO48.
- Espressif board: [ESP32-S3-DevKitC-1](https://www.espressif.com/en/products/devkits/esp32-s3-devkitc-1). Guide: [v1.1 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html). Photo: [isometric PNG](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/_images/esp32-s3-devkitc-1-v1.1-isometric.png).
- Clone size: [YD-ESP32-S3, 57.15 × 27.94 mm](https://www.espboards.dev/esp32/yd-esp32-s3/).
- Purchase: [AliExpress 1005004617322170](https://pl.aliexpress.com/item/1005004617322170.html).

![ESP32-S3 N16R8 AI-S3 clone](images/esp32s3-n16r8.png)


## Wiring

Shared nets on both sheets: `SDA`, `SCL`, `+3V3`, `+5V_SPS`, `GND`.

```
USB connector on the dev board
        │
        ├── header 5V (VBUS) ── +5V_SPS ── SPS30 VDD
        │
        └── onboard 3.3 V LDO ── header 3V3 ── +3V3 ── SCD30 or SCD41, SGP41, SHT45, R1, R2
```

The USB jack on the ESP32 module is the only supply. Do not feed the 3V3 pin from another regulator while USB is plugged in. Do not put a cell in the LOLIN32 PH-2 socket.

I2C pull-ups are **R1 and R2, 4.7 kΩ, to +3V3, and they are fitted.**

- The SPS30 datasheet requires external pull-ups (their example is 10 kΩ) and the sensor has none.
- The SCD30's only pull-ups are internal 45 kΩ to its own 3 V rail. That is too weak to be the only pull-up on a cabled bus, and it is not a 5 V pull-up. Powering the SCD30 from 3.3 V keeps the bus at 3.3 V. Do not power it from 5 V.
- SGP41, SCD41 and SHT45 bare sensors also require external pull-ups. The breakout you receive may already have 4.7–10 kΩ. A 4.7 kΩ pair in parallel with one extra 10 kΩ pair is still about 3.2 kΩ, above the roughly 1 kΩ floor for a 3 mA sink at 3.3 V. The SCD41 carrier in `images/scd41.png` has two resistors marked 103 (10 kΩ), and the SGP41 photo shows a 103 as well. Adafruit's SGP41 guide also fits 10 kΩ. Those sit in parallel with R1 and R2. That is fine. If you measure the idle bus and the equivalent is under about 2 kΩ, remove either the schematic pair or the module pair.
- Never pull SDA or SCL up to 5 V.

Bus speed is 100 kHz. That is the SPS30 maximum and the SCD30 maximum. Sensirion recommends 50 kHz or less for the SCD30; this revision follows the 100 kHz spec and relies on clock stretching. Keep cables short. Sensirion suggests well under 10 cm for SPS30 on I2C.

### Power pins

SPS30 VDD goes to the dev board's 5 V header pin. Every 3.3 V module and R1/R2 go to the 3.3 V header pin. GND is common.

| Board | 5 V pin, to SPS30 VDD | 3.3 V pin, to the I2C modules and R1/R2 |
| --- | --- | --- |
| WEMOS LOLIN32 V1.0.0 | Silkscreen **5V**. [espboards.dev](https://www.espboards.dev/esp32/lolin32/) calls this pin `5V` / `VUSB`: USB VBUS through the CJ2301 ideal-diode switch, so the pin stays near 5 V while USB is plugged in. | Silkscreen **3V3** (the header repeats it). Output of the onboard ME6211. |
| ESP32 D1 mini | Silkscreen **5V**, or **5V0** on the espboards drawing. USB VBUS. | Silkscreen **3V3**, or **3.3V**. Output of the onboard regulator. |
| ESP32-S3 N16R8 (DevKitC-1 / AI-S3) | Silkscreen **5V**. On the official DevKitC-1 v1.1 schematic this net is `VCC_5V` after a 1N5819, about 4.6 V. The SPS30 allows 4.5–5.5 V, so measure a clone and keep the USB cable short. | Silkscreen **3V3**. Output of the onboard LDO. |

### Variant A — `modular-lolin32` (also `modular-esp32-d1mini` and `modular-lolin32-lite`)

The board in [`images/wemos-lolin32.png`](images/wemos-lolin32.png) is a **WEMOS LOLIN32 V1.0.0**. PlatformIO board is `lolin32`. The two older environment names build the same flags, which also match an ESP32 D1 mini's GPIO21/GPIO22 and its 5V/3V3 pins.

Arduino-ESP32 2.0.17 [`variants/lolin32/pins_arduino.h`](https://github.com/espressif/arduino-esp32/blob/2.0.17/variants/lolin32/pins_arduino.h) sets `SDA = 21`, `SCL = 22`, `LED_BUILTIN = 5`, `A0 = 36`. The [LOLIN32 pinout](https://www.espboards.dev/esp32/lolin32/) shows GPIO21 and GPIO22 on the header, and the user LED on GPIO5, active low (on when the pin is low). GPIO5 is also a strapping pin and must be high at boot, which is the LED-off state. It is not used for I2C.

| Signal | GPIO | Silkscreen | Notes |
| --- | --- | --- | --- |
| I2C SDA | 21 | 21 | Arduino `SDA` for `lolin32`. Same pin on the ESP32 D1 mini. |
| I2C SCL | 22 | 22 | Arduino `SCL`. Same pin on the ESP32 D1 mini. |
| 5 V to SPS30 | — | 5V | VBUS from the board's USB connector. Always on. |
| 3.3 V to I2C modules | — | 3V3 | Onboard LDO output. Do not back-feed this pin. |
| GND | — | GND | Common ground. |
| User LED | 5 | 5 | Active low. The cellular probe also drives GPIO5, so this LED can blink during that probe. |

Leave open: GPIO0, GPIO2, GPIO12 and GPIO15 (strapping), GPIO1/TX, GPIO3/RX, GPIO4, GPIO26, GPIO36/VP, and the flash pins GPIO6–11. GPIO34, GPIO35 and GPIO39 stay open. The LOLIN32 PH-2 battery socket stays empty. The CHG LED is the unused onboard charger's indicator, not the GPIO5 user LED.

Build flags: `-D I2C_SDA_PIN=21 -D I2C_SCL_PIN=22 -D I2C_CLOCK_HZ=100000 -D WIRE_TIMEOUT_MS=200 -D SPS30_ALWAYS_ON=1`.

### Variant B — `modular-esp32s3-n16r8`

PlatformIO board `esp32-s3-devkitc-1` with `board_build.arduino.memory_type = qio_opi`, quad flash mode, `board_build.psram_type = opi`, 16 MB flash size, and `-DBOARD_HAS_PSRAM`. The linked SDK in a successful build is the `qio_opi` package, which matches Espressif's N16R8 description: 16 MB **quad** SPI flash and 8 MB **octal** SPI PSRAM (not octal flash). GPIO8 and GPIO9 are this variant's default Wire pins.

The partition table is the existing 4 MB `partitions.csv`, so the OTA layout stays the same and the upper 12 MB of flash is unused. The stock board json is still titled "DevKitC-1-N8 (No PSRAM)"; the memory settings above override that.

| Signal | GPIO | DevKitC-1 silkscreen | Notes |
| --- | --- | --- | --- |
| I2C SDA | 8 | IO8 | Default `SDA` |
| I2C SCL | 9 | IO9 | Default `SCL` |
| 5 V to SPS30 | — | 5V | VBUS from the board's USB connector. Always on. |
| 3.3 V to I2C modules | — | 3V3 | Onboard LDO output. Do not back-feed this pin. |
| GND | — | GND | Common ground. |

Do not use, on an N16R8:

- GPIO33, GPIO34, GPIO35, GPIO36, GPIO37. Espressif's DevKitC-1 v1.1 guide says GPIO35–37 are taken by octal SPI flash/PSRAM. The octal PSRAM data lines also use GPIO33–34, so those are left unused too.
- GPIO0, GPIO3, GPIO45, GPIO46 (strapping). GPIO45 must stay low at boot on a 3.3 V flash part.
- GPIO6 and GPIO7. They are free on this module and are left open.
- GPIO43 / GPIO44 (UART0, the COM port) and GPIO19 / GPIO20 (native USB, and also this firmware's `Serial2` probe).
- GPIO48, the RGB LED.

The board in [`images/esp32s3-n16r8.png`](images/esp32s3-n16r8.png) is a purple AI-S3 DevKitC-1 clone with an ESP32-S3-WROOM-1 marked N16R8, two USB-C sockets, RST and BOOT, and an RGB LED. The silkscreen labels include **8 and 9**, which are SDA and SCL. GPIO6 and GPIO7 are labelled and stay unconnected. GPIO35, GPIO36 and GPIO37 are also labelled, and they stay unconnected: on N16R8 they belong to the octal PSRAM. Strapping pins GPIO0, GPIO3, GPIO45 and GPIO46 are not used. GPIO48 is the onboard RGB LED (WS2812). Some clones only connect that LED after an `RGB` solder bridge is closed; either way, do not use GPIO48 for a sensor.

Published size for this YD-ESP32-S3 / DevKitC-style clone is **57.15 × 27.94 mm** ([espboards.dev YD-ESP32-S3](https://www.espboards.dev/esp32/yd-esp32-s3/)). A shop listing of the same shape says about 57 × 28 mm. The photo has no scale, so that cited figure is the one to use. It is a bit shorter and wider than a 63 × 25.5 mm guess.

Flash and the serial log use the **COM** USB-C port (the UART bridge). The port marked **USB** is native USB-OTG. Either port can feed VBUS. USB CDC on boot is left off, so a cable in the USB socket will not show `Serial`. A board with only the native USB connector needs `-D ARDUINO_USB_CDC_ON_BOOT=1`.

Build flags: `-D I2C_SDA_PIN=8 -D I2C_SCL_PIN=9 -D I2C_CLOCK_HZ=100000 -D WIRE_TIMEOUT_MS=200 -D SPS30_ALWAYS_ON=1`.

## Power

The dev board's USB connector is the only input. A linear regulator on the board makes 3.3 V from that 5 V, and the header pins are the two rails:

- **5 V pin.** USB VBUS, or VBUS after the board's diode. This pin powers the SPS30 only. It does not go through the 3.3 V regulator.
- **3.3 V pin.** The regulator output. It already feeds the ESP32 module. The I2C sensors and the pull-ups share whatever current is left.

### 3.3 V pin, shared with the ESP32

Sensirion currents, at the intervals this firmware already uses (SCD30 at 2 s, SCD41 on the library's default periodic measurement, which is 5 s):

| Load on the 3.3 V rail | Current |
| --- | --- |
| SCD30, if fitted | about 19 mA average at a 2 s interval, **75 mA peak** |
| SCD41, if fitted instead of the SCD30 | about 15 mA average at a 5 s interval, **205 mA peak** |
| SGP41 heater | a few milliamps, about 3 mA typical and under 5 mA |
| SHT45 | tiny: well under 1 mA during a conversion, nanoamps when idle |
| R1 / R2, 4.7 kΩ | about 0.7 mA on a line while it is driven low |

ESP32 Wi-Fi is the large term, and it is on the same regulator as the sensors:

- ESP32-WROOM-32 (LOLIN32 and the D1 mini): Wi-Fi transmit is about **240 mA** typical at 19.5 dBm, 802.11b, 1 Mbps (Espressif ESP32 datasheet). Espressif's hardware design guidelines ask the 3.3 V supply to be able to deliver **500 mA**, because peaks during transmit and RF calibration are higher than that typical.
- ESP32-S3 (variant B): Wi-Fi transmit is about **340 mA** typical.

Regulator ratings are for the whole rail, including the module:

- **LOLIN32.** The 3V3 pin is the ME6211 output. That regulator's maximum output current is **500 mA**. A Wi-Fi typical of 240 mA plus an SCD30 peak of 75 mA plus the SGP41 (under 5 mA) is about 320 mA if those peaks overlap, inside 500 mA, with little spare if the chip's own spike reaches the 500 mA guideline at the same moment. An SCD41 peak of 205 mA plus a 240 mA transmit is about 445 mA before that extra spike, so an SCD41 on this board sits on the regulator's limit. Average current is comfortable: receive is well below the transmit figure, and the SCD30 average is about 19 mA.
- **ESP32 D1 mini.** Wemos-style boards use the same ME6211 class (500 mA datasheet, less in practice on a small board with little copper). Many clones fit an AMS1117-3.3, rated about 1 A, with about 1.1 V of dropout, so a diode-dropped USB rail near 4.6 V leaves the regulator little headroom and it runs hot. Treat 500 mA as the budget unless you have identified the fitted part.
- **ESP32-S3-DevKitC-1 v1.1.** The schematic fits an SGM2212-3.3, **800 mA**. 340 mA of transmit plus a 75 mA SCD30 peak fits. 340 mA plus a 205 mA SCD41 peak is about 545 mA, still inside 800 mA. The AI-S3 clone may use a different regulator; read the package marking if the 3V3 rail sags.

### 5 V pin, SPS30 only

The SPS30 datasheet (v2.0) allows VDD of 4.5–5.5 V. Supply current is 45–65 mA while measuring, and at most **80 mA** for about the first 200 ms while the fan starts. That current comes from the 5 V pin, not from the 3.3 V regulator.

USB current is approximately the 3.3 V rail current (a linear regulator passes the load current through) plus the SPS30. An SCD30 build at the overlap above is about 320 mA on 3.3 V plus 80 mA, about 400 mA from USB, inside a 500 mA port. An SCD41 peak plus Wi-Fi transmit plus the fan start can pass 500 mA (about 445 mA on a LOLIN32's 3.3 V rail, plus 80 mA). Use a port that can supply that, or expect a brown-out. The LOLIN32's 5V pin stays near 5 V (ideal-diode switch). The official DevKitC-1 5V pin is about 4.6 V after its Schottky, which is inside the SPS30's 4.5 V minimum only if the cable drop is small.

## Connectors

Wire the SCD30 in datasheet order: VDD, GND, TX/SCL, RX/SDA, RDY, PWM, SEL. The symbol lists that order top to bottom and ties SEL to GND. Leaving SEL open also selects I2C. RDY and PWM are no-connect. Keep the bus at 100 kHz or slower.

The SGP41 block follows the STEMMA QT header: VIN (from 3.3 V), 3.3V (open), GND, SCL, SDA. The SHT45 block is VIN (from 3.3 V), 3Vo (open), GND, SCL, SDA. The SCD41 block follows the photographed carrier: GND, VCC, SCL, SDA. Do not feed 5 V into an SGP41 pin that goes straight to the sensor. The SHT45 sensor itself is also limited to 3.6 V; its carrier has a regulator, and VIN is still held at 3.3 V so the I2C lines stay at 3.3 V.

SPS30 mating plug is a JST ZHR-5. Pin order from the datasheet, looking at the connector with pin 1 at the end Sensirion marks: 1 VDD (5 V), 2 SDA, 3 SCL, 4 SEL (to GND), 5 GND. SEL must be low at the moment power is applied. The metal shell is connected to pin 5 inside the sensor; don't let the shell sit at a different potential than GND.

## ERC

KiCad 9.0.9 `kicad-cli sch erc` on both projects, re-run 2026-11-26 for rev C: 0 errors, 0 warnings. The project file sets `lib_symbol_issues` to ignore, because every symbol is embedded in the sheet and the `Modular` / `Device` / `power` nicknames are not in the global library table. Re-run with:

```
kicad-cli sch erc --severity-error --severity-warning hardware/modular/variant-a-esp32-d1mini/modular-a.kicad_sch
kicad-cli sch erc --severity-error --severity-warning hardware/modular/variant-b-esp32s3-n16r8/modular-b.kicad_sch
```

## Build

From the repository root, with PlatformIO and `espressif32@6.13.0` (Arduino-ESP32 2.0.17, same pin as the ESP32-C3 environment):

```
pio run -e modular-lolin32
pio run -e modular-esp32-d1mini
pio run -e modular-lolin32-lite
pio run -e modular-esp32s3-n16r8
pio run -e esp32-c3
```

A build on 2026-11-26, rev C. Variant A is the LOLIN32 image (`lolin32`). `modular-esp32-d1mini` and `modular-lolin32-lite` use the same flags. `modular-lolin32-lite` was not rebuilt separately.

| Environment | Result | RAM | Flash |
| --- | --- | --- | --- |
| `modular-lolin32` | success | 78364 / 327680 bytes (23.9%) | 1785645 / 1966080 bytes (90.8%) |
| `modular-esp32-d1mini` | success | 78364 / 327680 bytes (23.9%) | 1785709 / 1966080 bytes (90.8%) |
| `modular-esp32s3-n16r8` | success | 73600 / 327680 bytes (22.5% of internal SRAM; the 8 MB PSRAM is not in this number) | 1674273 / 1966080 bytes (85.2%) |

Those numbers are with `AG_MODULAR_I2C` (SCD30/SCD41 auto-detect and SPS30 over I2C) and without `SPS30_5V_EN_PIN` or `VBAT_ADC_PIN`. The two variant A rows use the same flags on board `lolin32`. Their flash totals differ because the environment name is compiled into file paths. The `esp32-c3` environment was not changed and was not rebuilt.

The S3 image was linked against the `qio_opi` SDK libraries and `esptool` was invoked with `--flash_size 16MB`. The app partition is still the 4 MB Open Air slot (`0x1E0000` bytes), which is why the flash percentage is against 1.9 MB rather than 16 MB.
