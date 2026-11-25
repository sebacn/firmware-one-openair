#!/usr/bin/env python3
"""Generate the two modular outdoor-monitor KiCad schematics (rev A).

One sheet per variant, A4 landscape (297 x 210 mm). Symbols are embedded, so
the projects open without the KiCad system libraries. Run from anywhere:

    python3 hardware/modular/tools/gen_schematics.py
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRO_TEMPLATE = ROOT / "hardware/open-air/main-board/ag_outdoor.kicad_pro"
OUT_A = ROOT / "hardware/modular/variant-a-esp32-d1mini"
OUT_B = ROOT / "hardware/modular/variant-b-esp32s3-n16r8"

# 1.27 mm schematic grid.
G = 1.27


def g(n: float) -> float:
    return round(n * G, 2)


def uid() -> str:
    return str(uuid.uuid4())


def num(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class Pin:
    def __init__(self, name: str, number: str, x: float, y: float, angle: int, etype: str):
        self.name = name
        self.number = number
        self.x = x
        self.y = y
        self.angle = angle
        self.etype = etype


class SymbolDef:
    def __init__(self, lib_id: str, pins: list[Pin], graphics: str, ref_y: float, value_y: float):
        self.lib_id = lib_id
        self.pins = {p.number: p for p in pins}
        self.pin_list = pins
        self.graphics = graphics
        self.ref_y = ref_y
        self.value_y = value_y

    @property
    def short(self) -> str:
        return self.lib_id.split(":", 1)[1]

    def sexpr(self) -> str:
        pin_s = []
        for p in self.pin_list:
            pin_s.append(
                f"""        (pin {p.etype} line (at {num(p.x)} {num(p.y)} {p.angle}) (length 2.54)
          (name "{esc(p.name)}" (effects (font (size 1.016 1.016))))
          (number "{p.number}" (effects (font (size 1.016 1.016))))
        )"""
            )
        pins_block = "\n".join(pin_s)
        return f"""    (symbol "{self.lib_id}" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 {num(self.ref_y)} 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "{esc(self.short)}" (at 0 {num(self.value_y)} 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "~" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "{self.short}_0_1"
{self.graphics}
      )
      (symbol "{self.short}_1_1"
{pins_block}
      )
    )"""


def rect(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""        (rectangle (start {num(x1)} {num(y1)}) (end {num(x2)} {num(y2)})
          (stroke (width 0.254) (type default))
          (fill (type background))
        )"""


def box_symbol(lib_id: str, left: list[tuple[str, str]], right: list[tuple[str, str]], half_w: float = 17.78) -> SymbolDef:
    """left/right entries are (pin_name, electrical_type). Pins are numbered left-then-right."""
    pitch = 5.08

    def side_pins(entries, x, angle, start_num):
        n = len(entries)
        if n == 0:
            return []
        top = (n - 1) * pitch / 2
        pins = []
        for i, (name, etype) in enumerate(entries):
            pins.append(Pin(name, str(start_num + i), x, round(top - i * pitch, 2), angle, etype))
        return pins

    # Connection point is one pin-length outside the box.
    left_pins = side_pins(left, -(half_w + 2.54), 0, 1)
    right_pins = side_pins(right, half_w + 2.54, 180, 1 + len(left))
    pins = left_pins + right_pins
    n = max(len(left), len(right), 1)
    half_h = (n - 1) * pitch / 2 + 3.81
    graphics = rect(-half_w, -half_h, half_w, half_h)
    return SymbolDef(lib_id, pins, graphics, half_h + 2.54, -(half_h + 3.81))


def two_pin(lib_id: str, horizontal: bool, body: str) -> SymbolDef:
    if horizontal:
        pins = [
            Pin("~", "1", -5.08, 0, 0, "passive"),
            Pin("~", "2", 5.08, 0, 180, "passive"),
        ]
        ref_y, value_y = 3.81, -3.81
    else:
        pins = [
            Pin("~", "1", 0, 5.08, 270, "passive"),
            Pin("~", "2", 0, -5.08, 90, "passive"),
        ]
        ref_y, value_y = 7.62, -7.62
    return SymbolDef(lib_id, pins, body, ref_y, value_y)


def power_symbol(net: str, graphic: str) -> str:
    # Pin name and value are the net. Not built via SymbolDef because of the
    # (power) flag and the hidden zero-length pin.
    return f"""    (symbol "power:{net}" (power) (pin_names (offset 0) hide) (pin_numbers hide) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -6.35 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "{esc(net)}" (at 0 3.81 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "{net}_0_1"
{graphic}
      )
      (symbol "{net}_1_1"
        (pin power_in line (at 0 0 90) (length 0) hide
          (name "{esc(net)}" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )"""


PWR_FLAG = """    (symbol "power:PWR_FLAG" (pin_numbers hide) (pin_names (offset 0) hide) (in_bom no) (on_board yes)
      (property "Reference" "#FLG" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "PWR_FLAG" (at 2.54 0 0)
        (effects (font (size 1.27 1.27)) (justify left))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "~" (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "PWR_FLAG_0_1"
        (polyline (pts (xy 0 0) (xy 0 2.54) (xy 2.54 1.27) (xy 0 0))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
      )
      (symbol "PWR_FLAG_1_1"
        (pin power_out line (at 0 0 270) (length 0) hide
          (name "pwr" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )"""

GND_GRAPHIC = """        (polyline (pts (xy -1.524 0) (xy 1.524 0))
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.016 -0.762) (xy 1.016 -0.762))
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -0.508 -1.524) (xy 0.508 -1.524))
          (stroke (width 0.254) (type default)) (fill (type none)))"""

ARROW_GRAPHIC = """        (polyline (pts (xy 0 0) (xy 0 2.54))
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27))
          (stroke (width 0.254) (type default)) (fill (type none)))"""

R_BODY = """        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

RH_BODY = """        (rectangle (start -2.54 -1.016) (end 2.54 1.016)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

C_BODY = """        (polyline (pts (xy -1.524 0.762) (xy 1.524 0.762))
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.524 -0.762) (xy 1.524 -0.762))
          (stroke (width 0.254) (type default)) (fill (type none)))"""

JP_BODY = """        (rectangle (start -2.54 -1.27) (end 2.54 1.27)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline (pts (xy -1.27 0) (xy 1.27 0))
          (stroke (width 0.254) (type default)) (fill (type none)))"""


class Sch:
    def __init__(self, project: str, title: str, comments: list[str]):
        self.project = project
        self.root = uid()
        self.title = title
        self.comments = comments
        self.defs: dict[str, SymbolDef] = {}
        self.extra_lib: list[str] = []
        self.items: list[str] = []
        self._pwr = 0
        self._flg = 0

    def add_def(self, sym: SymbolDef) -> None:
        self.defs[sym.lib_id] = sym

    def add_power_lib(self, net: str, graphic: str) -> None:
        ident = f"power:{net}"
        if ident not in self.defs:
            self.extra_lib.append(power_symbol(net, graphic))
            # Placeholder so we don't emit it twice. Pin map is unused:
            # power symbols are placed by place_power().
            self.defs[ident] = SymbolDef(ident, [Pin(net, "1", 0, 0, 90, "power_in")], "", 0, 0)

    def place(self, lib_id: str, ref: str, value: str, x: float, y: float) -> dict[str, tuple[float, float]]:
        sym = self.defs[lib_id]
        pin_uuids = [(p.number, uid()) for p in sym.pin_list]
        pin_lines = "\n".join(f'    (pin "{n}" (uuid {u}))' for n, u in pin_uuids)
        # Reference above the body, value below. Shift by the placed origin.
        ref_y = y + sym.ref_y
        val_y = y + sym.value_y
        self.items.append(
            f"""  (symbol (lib_id "{lib_id}") (at {num(x)} {num(y)} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid {uid()})
    (property "Reference" "{esc(ref)}" (at {num(x)} {num(ref_y)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{esc(value)}" (at {num(x)} {num(val_y)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "~" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
{pin_lines}
    (instances
      (project "{self.project}"
        (path "/{self.root}"
          (reference "{esc(ref)}") (unit 1)
        )
      )
    )
  )"""
        )
        # KiCad's placed-symbol transform mirrors Y: sheet_y = origin_y - pin_y.
        world = {"_center": (x, y)}
        for p in sym.pin_list:
            world[p.number] = (round(x + p.x, 2), round(y - p.y, 2))
            world[p.name] = world[p.number]
        return world

    def place_power(self, net: str, x: float, y: float) -> None:
        self._pwr += 1
        ref = f"#PWR{self._pwr:03d}"
        self.items.append(
            f"""  (symbol (lib_id "power:{net}") (at {num(x)} {num(y)} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid {uid()})
    (property "Reference" "{ref}" (at {num(x)} {num(y - 5.08)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "{esc(net)}" (at {num(x)} {num(y + 3.81)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid {uid()}))
    (instances
      (project "{self.project}"
        (path "/{self.root}"
          (reference "{ref}") (unit 1)
        )
      )
    )
  )"""
        )

    def place_flag(self, x: float, y: float) -> None:
        self._flg += 1
        ref = f"#FLG{self._flg:02d}"
        self.items.append(
            f"""  (symbol (lib_id "power:PWR_FLAG") (at {num(x)} {num(y)} 0) (unit 1)
    (in_bom no) (on_board yes) (dnp no)
    (uuid {uid()})
    (property "Reference" "{ref}" (at {num(x)} {num(y + 3.81)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "PWR_FLAG" (at {num(x + 2.54)} {num(y)} 0)
      (effects (font (size 1.016 1.016)) (justify left))
    )
    (property "Footprint" "" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "~" (at {num(x)} {num(y)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid {uid()}))
    (instances
      (project "{self.project}"
        (path "/{self.root}"
          (reference "{ref}") (unit 1)
        )
      )
    )
  )"""
        )

    def wire(self, x1: float, y1: float, x2: float, y2: float) -> None:
        if (x1, y1) == (x2, y2):
            return
        # One corner when the segment is not orthogonal, so ERC sees a real wire.
        if x1 != x2 and y1 != y2:
            self.wire(x1, y1, x2, y1)
            self.wire(x2, y1, x2, y2)
            return
        self.items.append(
            f"""  (wire (pts (xy {num(x1)} {num(y1)}) (xy {num(x2)} {num(y2)}))
    (stroke (width 0) (type default))
    (uuid {uid()})
  )"""
        )

    def label(self, name: str, x: float, y: float, angle: int = 0) -> None:
        justify = "right" if angle == 180 else "left"
        self.items.append(
            f"""  (label "{esc(name)}" (at {num(x)} {num(y)} {angle})
    (effects (font (size 1.016 1.016)) (justify {justify}))
    (uuid {uid()})
  )"""
        )

    def text(self, body: str, x: float, y: float, size: float = 1.27, justify: str = "left top") -> None:
        self.items.append(
            f"""  (text "{esc(body)}" (at {num(x)} {num(y)} 0)
    (effects (font (size {num(size)} {num(size)})) (justify {justify}))
    (uuid {uid()})
  )"""
        )

    def nc(self, x: float, y: float) -> None:
        self.items.append(
            f"""  (no_connect (at {num(x)} {num(y)}) (uuid {uid()}))"""
        )

    def stub(self, pin_xy: tuple[float, float], direction: str, kind: str, net: str | None = None, center: tuple[float, float] | None = None) -> None:
        x, y = pin_xy
        if kind != "nc" and center is not None:
            cx, cy = center
            if abs(x - cx) >= abs(y - cy):
                direction = "right" if x >= cx else "left"
            else:
                direction = "up" if y >= cy else "down"
        step = {
            "left": (-7.62, 0, 180),
            "right": (7.62, 0, 0),
            "up": (0, 5.08, 0),
            "down": (0, -5.08, 0),
        }[direction]
        x2, y2 = round(x + step[0], 2), round(y + step[1], 2)
        if kind == "nc":
            self.nc(x, y)
            return
        self.wire(x, y, x2, y2)
        if kind == "pwr":
            assert net is not None
            self.place_power(net, x2, y2)
        elif kind == "lbl":
            assert net is not None
            # The label anchor is the wire end. Angle 0 draws the name to the
            # right; angle 180 draws it to the left, away from a leftward stub.
            angle = 0 if direction in ("up", "down", "right") else 180
            self.label(net, x2, y2, angle)
        elif kind == "flag":
            assert net is not None
            self.place_power(net, x2, y2)
            # Flag sits on the same point as the power symbol pin, joined by the wire end.
            self.place_flag(x2, y2)
        else:
            raise ValueError(kind)

    def dump(self) -> str:
        lib = []
        emitted = set()
        for ident, sym in self.defs.items():
            if ident.startswith("power:"):
                continue
            if ident not in emitted:
                lib.append(sym.sexpr())
                emitted.add(ident)
        lib.extend(self.extra_lib)
        if "power:PWR_FLAG" not in emitted:
            lib.append(PWR_FLAG)
        comments = "\n".join(
            f'    (comment {i} "{esc(c)}")' for i, c in enumerate(self.comments, start=1)
        )
        return f"""(kicad_sch (version 20230121) (generator eeschema)

  (uuid {self.root})

  (paper "User" 297 210)

  (title_block
    (title "{esc(self.title)}")
    (date "2026-11-25")
    (rev "A")
    (company "DIY modular outdoor monitor")
{comments}
  )

  (lib_symbols
{chr(10).join(lib)}
  )

{chr(10).join(self.items)}

  (sheet_instances
    (path "/" (page "1"))
  )
)
"""


def build_libraries(variant: str) -> dict[str, SymbolDef]:
    libs: dict[str, SymbolDef] = {}

    def add(sym: SymbolDef) -> None:
        libs[sym.lib_id] = sym

    add(two_pin("Device:R", False, R_BODY))
    add(two_pin("Device:R_H", True, RH_BODY))
    add(two_pin("Device:C", False, C_BODY))
    add(two_pin("Modular:JP", True, JP_BODY))

    add(
        box_symbol(
            "Modular:SOLAR",
            [],
            [("VIN", "power_out"), ("GND", "power_in")],
            half_w=12.7,
        )
    )
    add(
        box_symbol(
            "Modular:PACK",
            [],
            [("BAT", "power_out"), ("GND", "power_in")],
            half_w=15.24,
        )
    )
    add(
        box_symbol(
            "Modular:BQ25185",
            [("VIN", "power_in"), ("BAT", "power_in"), ("TS", "passive"), ("GND", "power_in")],
            [("5V", "power_out"), ("EN", "passive")],
            half_w=20.32,
        )
    )
    add(
        box_symbol(
            "Modular:TPS63020",
            [("VIN", "power_in"), ("EN", "passive")],
            [("VOUT", "power_out"), ("GND", "power_in")],
            half_w=17.78,
        )
    )
    if variant == "A":
        mcu_right = [
            ("IO21/D2", "bidirectional"),
            ("IO22/D1", "bidirectional"),
            ("IO26/D0", "output"),
            ("IO36/A0", "passive"),
        ]
        mcu_id = "Modular:MCU_A"
    else:
        mcu_right = [
            ("IO8", "bidirectional"),
            ("IO9", "bidirectional"),
            ("IO7", "output"),
            ("IO6", "passive"),
        ]
        mcu_id = "Modular:MCU_B"
    add(
        box_symbol(
            mcu_id,
            [("3V3", "power_in"), ("GND", "power_in"), ("5V", "passive")],
            mcu_right,
            half_w=20.32,
        )
    )
    i2c4 = [("VCC", "power_in"), ("GND", "power_in"), ("SCL", "bidirectional"), ("SDA", "bidirectional")]
    add(box_symbol("Modular:SGP41", [], i2c4, half_w=15.24))
    add(box_symbol("Modular:SHT45", [], i2c4, half_w=15.24))
    # Header on the measured 13.4 x 21.6 mm carrier, left to right on the label
    # side: GND, VCC, SCL, SDA. The symbol lists that order top to bottom.
    scd41_pins = [
        ("GND", "power_in"),
        ("VCC", "power_in"),
        ("SCL", "bidirectional"),
        ("SDA", "bidirectional"),
    ]
    add(box_symbol("Modular:SCD41", [], scd41_pins, half_w=15.24))
    add(
        box_symbol(
            "Modular:SCD30",
            [("VDD", "power_in"), ("GND", "power_in"), ("SCL", "bidirectional"), ("SDA", "bidirectional")],
            [("RDY", "passive"), ("PWM", "passive"), ("SEL", "passive")],
            half_w=17.78,
        )
    )
    add(
        box_symbol(
            "Modular:SPS30",
            [("VDD", "power_in"), ("SDA", "bidirectional"), ("SCL", "bidirectional"), ("GND", "power_in")],
            [("SEL", "passive")],
            half_w=16.51,
        )
    )
    return libs


def wire_pins(sch: Sch, pins: dict, mapping: list[tuple]) -> None:
    """mapping items: (pin_name, kind, net_or_None, direction).

    Direction is recomputed from the symbol center so the stub leaves the body.
    KiCad mirrors symbol Y, so a hand-written up/down would often point inward.
    """
    center = pins.get("_center")
    for name, kind, net, direction in mapping:
        sch.stub(pins[name], direction, kind, net, center=center)


def build(variant: str) -> Sch:
    if variant == "A":
        project = "modular-a"
        title = "Modular outdoor monitor — variant A (ESP32-WROOM-32 D1 Mini)"
        comments = [
            "Not the AirGradient V1.3 PCB. Off-the-shelf modules only.",
            "SDA GPIO21/D2, SCL GPIO22/D1, SPS30 EN GPIO26/D0, VBAT ADC GPIO36/A0",
            "I2C 100 kHz, 3.3 V logic. Fit SCD30 (0x61) or SCD41 (0x62), not both.",
            "A4 landscape 297 x 210 mm. Rev A, 2026-11-25.",
        ]
        mcu_id = "Modular:MCU_A"
        mcu_value = "ESP32 D1 Mini / LOLIN32-mini"
        gpio_line = (
            "Variant A: SDA GPIO21 (D2), SCL GPIO22 (D1), SPS30 EN GPIO26 (D0, active high), VBAT ADC GPIO36 (A0, ADC1)."
        )
        avoid_line = (
            "Also leave open: GPIO0/2/12/15 (strap), GPIO1/TX, GPIO3/RX, GPIO6-11 (flash), GPIO4 and GPIO5/D8."
        )
    else:
        project = "modular-b"
        title = "Modular outdoor monitor — variant B (ESP32-S3 N16R8 DevKitC)"
        comments = [
            "Not the AirGradient V1.3 PCB. Off-the-shelf modules only.",
            "SDA GPIO8, SCL GPIO9, SPS30 EN GPIO7, VBAT ADC GPIO6 (ADC1)",
            "N16R8: 16 MB quad flash, 8 MB octal PSRAM. Do not use GPIO33-37.",
            "A4 landscape 297 x 210 mm. Rev A, 2026-11-25.",
        ]
        mcu_id = "Modular:MCU_B"
        mcu_value = "ESP32-S3-DevKitC-1 N16R8"
        gpio_line = (
            "Variant B N16R8: SDA GPIO8, SCL GPIO9, SPS30 EN GPIO7 (active high), VBAT ADC GPIO6 (ADC1)."
        )
        avoid_line = (
            "Also leave open: GPIO0/3/45/46 (strap), GPIO19/20 (USB), GPIO43/44 (UART), GPIO33-37 (octal PSRAM)."
        )

    sch = Sch(project, title, comments)
    for sym in build_libraries(variant).values():
        sch.add_def(sym)
    for net, graphic in (
        ("GND", GND_GRAPHIC),
        ("+3V3", ARROW_GRAPHIC),
        ("+5V_SPS", ARROW_GRAPHIC),
        ("VBAT", ARROW_GRAPHIC),
        ("VIN_SOLAR", ARROW_GRAPHIC),
        ("ESP_3V3", ARROW_GRAPHIC),
    ):
        sch.add_power_lib(net, graphic)

    # --- power input ---
    solar = sch.place("Modular:SOLAR", "J1", "Solar / DC 5-18V", 33.02, 43.18)
    wire_pins(
        sch,
        solar,
        [
            ("VIN", "pwr", "VIN_SOLAR", "right"),
            ("GND", "pwr", "GND", "right"),
        ],
    )
    pack = sch.place("Modular:PACK", "J2", "1S 18650 2-3P protected", 33.02, 86.36)
    wire_pins(
        sch,
        pack,
        [
            ("BAT", "pwr", "VBAT", "right"),
            ("GND", "pwr", "GND", "right"),
        ],
    )
    ntc = sch.place("Device:R", "RT1", "10k NTC B3435", 76.2, 86.36)
    wire_pins(
        sch,
        ntc,
        [
            ("1", "lbl", "TS", "up"),
            ("2", "pwr", "GND", "down"),
        ],
    )

    chg = sch.place("Modular:BQ25185", "U1", "BQ25185 + 5V boost", 114.3, 48.26)
    wire_pins(
        sch,
        chg,
        [
            ("VIN", "pwr", "VIN_SOLAR", "left"),
            ("BAT", "pwr", "VBAT", "left"),
            ("TS", "lbl", "TS", "left"),
            ("GND", "pwr", "GND", "left"),
            ("5V", "pwr", "+5V_SPS", "right"),
            ("EN", "lbl", "BOOST_EN", "right"),
        ],
    )

    tps = sch.place("Modular:TPS63020", "U2", "TPS63020 set to 3.3V", 114.3, 99.06)
    wire_pins(
        sch,
        tps,
        [
            ("VIN", "pwr", "VBAT", "left"),
            ("EN", "pwr", "VBAT", "left"),
            ("VOUT", "pwr", "+3V3", "right"),
            ("GND", "pwr", "GND", "right"),
        ],
    )

    rtop = sch.place("Device:R", "R1", "100k", 33.02, 137.16)
    wire_pins(
        sch,
        rtop,
        [
            ("1", "pwr", "VBAT", "up"),
            ("2", "lbl", "VBAT_SENSE", "down"),
        ],
    )
    rbot = sch.place("Device:R", "R2", "100k", 53.34, 137.16)
    wire_pins(
        sch,
        rbot,
        [
            ("1", "lbl", "VBAT_SENSE", "up"),
            ("2", "pwr", "GND", "down"),
        ],
    )
    cap = sch.place("Device:C", "C1", "100n", 73.66, 137.16)
    wire_pins(
        sch,
        cap,
        [
            ("1", "lbl", "VBAT_SENSE", "up"),
            ("2", "pwr", "GND", "down"),
        ],
    )

    jp = sch.place("Modular:JP", "JP1", "FIT=battery OPEN=USB", 114.3, 137.16)
    wire_pins(
        sch,
        jp,
        [
            ("1", "pwr", "+3V3", "left"),
            ("2", "pwr", "ESP_3V3", "right"),
        ],
    )
    # ESP_3V3 is fed only through JP1, so ERC needs an explicit power-out on that net.
    # The stub on pin 2 already ends on the ESP_3V3 symbol; drop the flag just below it.
    jx, jy = jp["2"]
    flag_x = jx + (7.62 if jx >= jp["_center"][0] else -7.62)
    sch.wire(flag_x, jy, flag_x, jy - 5.08)
    sch.place_flag(flag_x, jy - 5.08)

    rser = sch.place("Device:R_H", "R3", "1k", 157.48, 137.16)
    wire_pins(
        sch,
        rser,
        [
            ("1", "lbl", "SPS_EN", "left"),
            ("2", "lbl", "BOOST_EN", "right"),
        ],
    )

    # Ground return is entirely power-in pins. One flag marks the net driven.
    sch.wire(15.24, 124.46, 15.24, 119.38)
    sch.place_power("GND", 15.24, 119.38)
    sch.place_flag(15.24, 124.46)

    # --- MCU and sensors ---
    mcu = sch.place(mcu_id, "U3", mcu_value, 175.26, 71.12)
    if variant == "A":
        sig = [("IO21/D2", "SDA"), ("IO22/D1", "SCL"), ("IO26/D0", "SPS_EN"), ("IO36/A0", "VBAT_SENSE")]
    else:
        sig = [("IO8", "SDA"), ("IO9", "SCL"), ("IO7", "SPS_EN"), ("IO6", "VBAT_SENSE")]
    wire_pins(
        sch,
        mcu,
        [
            ("3V3", "pwr", "ESP_3V3", "left"),
            ("GND", "pwr", "GND", "left"),
            ("5V", "nc", None, "left"),
        ]
        + [(name, "lbl", net, "right") for name, net in sig],
    )
    # Re-stub of the first pin happened inside wire_pins. Good.

    rpu_sda = sch.place("Device:R", "R4", "4.7k", 210.82, 38.1)
    wire_pins(
        sch,
        rpu_sda,
        [
            ("1", "pwr", "+3V3", "up"),
            ("2", "lbl", "SDA", "down"),
        ],
    )
    rpu_scl = sch.place("Device:R", "R5", "4.7k", 228.6, 38.1)
    wire_pins(
        sch,
        rpu_scl,
        [
            ("1", "pwr", "+3V3", "up"),
            ("2", "lbl", "SCL", "down"),
        ],
    )

    sgp = sch.place("Modular:SGP41", "U4", "SGP41 VOC/NOx 0x59", 248.92, 55.88)
    wire_pins(
        sch,
        sgp,
        [
            ("VCC", "pwr", "+3V3", "right"),
            ("GND", "pwr", "GND", "right"),
            ("SCL", "lbl", "SCL", "right"),
            ("SDA", "lbl", "SDA", "right"),
        ],
    )
    sht = sch.place("Modular:SHT45", "U5", "SHT45-AD1B 0x44", 248.92, 96.52)
    wire_pins(
        sch,
        sht,
        [
            ("VCC", "pwr", "+3V3", "right"),
            ("GND", "pwr", "GND", "right"),
            ("SCL", "lbl", "SCL", "right"),
            ("SDA", "lbl", "SDA", "right"),
        ],
    )
    scd30 = sch.place("Modular:SCD30", "U6", "SCD30 0x61  FIT ONE", 152.4, 114.3)
    # SCD30 center collides with R3. Move is handled by coordinates above... check later.
    wire_pins(
        sch,
        scd30,
        [
            ("VDD", "pwr", "+3V3", "left"),
            ("GND", "pwr", "GND", "left"),
            ("SCL", "lbl", "SCL", "left"),
            ("SDA", "lbl", "SDA", "left"),
            ("RDY", "nc", None, "right"),
            ("PWM", "nc", None, "right"),
            ("SEL", "pwr", "GND", "right"),
        ],
    )
    scd41 = sch.place("Modular:SCD41", "U7", "SCD41 0x62  FIT ONE", 248.92, 137.16)
    wire_pins(
        sch,
        scd41,
        [
            ("VCC", "pwr", "+3V3", "right"),
            ("GND", "pwr", "GND", "right"),
            ("SCL", "lbl", "SCL", "right"),
            ("SDA", "lbl", "SDA", "right"),
        ],
    )
    sps = sch.place("Modular:SPS30", "U8", "SPS30 I2C 0x69", 88.9, 175.26)
    wire_pins(
        sch,
        sps,
        [
            ("VDD", "pwr", "+5V_SPS", "left"),
            ("SDA", "lbl", "SDA", "left"),
            ("SCL", "lbl", "SCL", "left"),
            ("GND", "pwr", "GND", "left"),
            ("SEL", "pwr", "GND", "right"),
        ],
    )

    # One text object per line. KiCad 9 does not treat \n inside a text string as a break.
    note_lines = [
        gpio_line,
        "JP1 FIT = run from U2. OPEN JP1 before the ESP32 USB plug. Never USB and the 3V3 pin at once.",
        "Do not tie +5V_SPS to the ESP32 5V pin. I2C is 100 kHz at 3.3 V. R4/R5 = 4.7k to +3V3. Never pull SDA/SCL to 5 V.",
        "Fit U6 SCD30 (0x61, SEL=GND) OR U7 SCD41 (0x62), not both. U8 SEL=GND selects I2C 0x69 before power-up.",
        "EN is active high through R3. RT1 replaces the module's fixed 10k on TS. Set U2 to 3.3 V before connecting it.",
        "Leave GPIO3, GPIO4 and GPIO5 open. " + avoid_line,
    ]
    note_y = 10.16
    for line in note_lines:
        sch.text(line, 12.7, note_y, 1.016, "left top")
        note_y += 2.54
    # silence unused
    return sch


def write_project(directory: Path, project: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    text = PRO_TEMPLATE.read_text()
    text = text.replace('"filename": "ag_outdoor.kicad_pro"', f'"filename": "{project}.kicad_pro"')
    # Symbols are embedded in the sheet. This warning only means the nickname
    # is not in the global KiCad library table.
    text = text.replace('"lib_symbol_issues": "warning"', '"lib_symbol_issues": "ignore"')
    (directory / f"{project}.kicad_pro").write_text(text)


def main() -> None:
    for variant, directory, project in (
        ("A", OUT_A, "modular-a"),
        ("B", OUT_B, "modular-b"),
    ):
        sch = build(variant)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{project}.kicad_sch").write_text(sch.dump())
        write_project(directory, project)
        print(f"wrote {directory / (project + '.kicad_sch')}")


if __name__ == "__main__":
    main()
