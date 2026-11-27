#!/usr/bin/env python3
"""Generate the two modular outdoor-monitor KiCad schematics (rev D).

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

# Horizontal PTC. Pin 1 is the left terminal, pin 2 the right.
PTC_BODY = """        (rectangle (start -2.54 -1.27) (end 2.54 1.27)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline (pts (xy -2.54 1.27) (xy 2.54 -1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

# Horizontal Schottky. Pin 1 is the anode (left), pin 2 the cathode (right).
DIODE_H_BODY = """        (polyline (pts (xy -1.778 -1.27) (xy -1.778 1.27) (xy 1.27 0) (xy -1.778 -1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline (pts (xy 1.778 -1.524) (xy 1.778 1.524))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

# Vertical TVS. Pin 1 is the cathode (top, the bar), pin 2 the anode (bottom).
DIODE_V_BODY = """        (polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 1.27) (xy -1.27 -1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline (pts (xy -1.524 1.778) (xy 1.524 1.778))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

# Vertical capacitor. Pin 1 is the top terminal, pin 2 the bottom.
CAP_BODY = """        (polyline (pts (xy -1.778 0.762) (xy 1.778 0.762))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline (pts (xy -1.778 -0.762) (xy 1.778 -0.762))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )"""

class Sch:
    def __init__(self, project: str, title: str, comments: list[str], rev: str = "D", date: str = "2026-11-27"):
        self.project = project
        self.root = uid()
        self.title = title
        self.comments = comments
        self.rev = rev
        self.date = date
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
    (date "{self.date}")
    (rev "{self.rev}")
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
    add(two_pin("Device:PTC", True, PTC_BODY))
    add(two_pin("Device:D", True, DIODE_H_BODY))
    add(two_pin("Device:TVS", False, DIODE_V_BODY))
    add(two_pin("Device:C", False, CAP_BODY))

    if variant == "A":
        # LOLIN32 V1.0.0 and the ESP32 D1 mini share these header pins.
        # GPIO21/GPIO22 are Arduino SDA/SCL. GPIO34/35/32 are ADC1.
        mcu_right = [
            ("IO21", "bidirectional"),
            ("IO22", "bidirectional"),
            ("IO34", "bidirectional"),
            ("IO35", "bidirectional"),
            ("IO32", "bidirectional"),
        ]
        mcu_id = "Modular:MCU_A"
    else:
        # ESP32-S3 ADC1 is GPIO1-10. GPIO8/9 are I2C. GPIO6/7/10 stay free of
        # the N16R8 octal PSRAM pins and of the strapping pins.
        mcu_right = [
            ("IO8", "bidirectional"),
            ("IO9", "bidirectional"),
            ("IO6", "bidirectional"),
            ("IO7", "bidirectional"),
            ("IO10", "bidirectional"),
        ]
        mcu_id = "Modular:MCU_B"
    add(
        box_symbol(
            mcu_id,
            [("3V3", "power_out"), ("GND", "power_in"), ("5V", "power_out")],
            mcu_right,
            half_w=22.86,
        )
    )
    # Adafruit 6455 / STEMMA QT header, top to bottom with VIN at the top
    # of the row: VIN, 3.3V (regulator output, leave open), GND, SCL, SDA.
    add(
        box_symbol(
            "Modular:SGP41",
            [],
            [
                ("VIN", "power_in"),
                ("3.3V", "passive"),
                ("GND", "power_in"),
                ("SCL", "bidirectional"),
                ("SDA", "bidirectional"),
            ],
            half_w=15.24,
        )
    )
    # Seller header order: VIN, 3Vo, GND, SCL, SDA. 3Vo is the regulator
    # output and is left open. VIN is fed from 3.3 V.
    add(
        box_symbol(
            "Modular:SHT45",
            [],
            [
                ("VIN", "power_in"),
                ("3Vo", "passive"),
                ("GND", "power_in"),
                ("SCL", "bidirectional"),
                ("SDA", "bidirectional"),
            ],
            half_w=15.24,
        )
    )
    # Header on the measured 13.4 x 21.6 mm carrier, left to right on the label
    # side: GND, VCC, SCL, SDA. The symbol lists that order top to bottom.
    scd41_pins = [
        ("GND", "power_in"),
        ("VCC", "power_in"),
        ("SCL", "bidirectional"),
        ("SDA", "bidirectional"),
    ]
    add(box_symbol("Modular:SCD41", [], scd41_pins, half_w=15.24))
    # Sensirion SCD30 7-pin header, datasheet order, top to bottom.
    # SEL open or tied to GND selects I2C. The sheet ties it to GND.
    # Pins are on the left so the symbol can sit in the lower-left margin,
    # clear of U8 and of the title block.
    scd30_pins = [
        ("VDD", "power_in"),
        ("GND", "power_in"),
        ("TX/SCL", "bidirectional"),
        ("RX/SDA", "bidirectional"),
        ("RDY", "passive"),
        ("PWM", "passive"),
        ("SEL", "passive"),
    ]
    add(box_symbol("Modular:SCD30", scd30_pins, [], half_w=17.78))
    add(
        box_symbol(
            "Modular:SPS30",
            [("VDD", "power_in"), ("SDA", "bidirectional"), ("SCL", "bidirectional"), ("GND", "power_in")],
            [("SEL", "passive")],
            half_w=16.51,
        )
    )
    # IEC 61076-2-101 M8 A-coded 4-pin. Pin numbers match the standard insert.
    # 1 brown +5V, 2 white VBAT, 3 blue GND, 4 black VSOL.
    add(
        box_symbol(
            "Modular:M8",
            [
                ("+5V", "passive"),
                ("VBAT", "passive"),
                ("GND", "passive"),
                ("VSOL", "passive"),
            ],
            [],
            half_w=12.7,
        )
    )
    # Pin on the right so a part in the right margin stubs toward the sheet edge.
    add(box_symbol("Modular:VBUS", [], [("VBUS", "passive")], half_w=8.89))
    return libs


def wire_pins(sch: Sch, pins: dict, mapping: list[tuple]) -> None:
    """mapping items: (pin_name, kind, net_or_None, direction).

    Direction is recomputed from the symbol center so the stub leaves the body.
    KiCad mirrors symbol Y, so a hand-written up/down would often point inward.
    """
    center = pins.get("_center")
    for name, kind, net, direction in mapping:
        sch.stub(pins[name], direction, kind, net, center=center)


def gu(n: int) -> float:
    """Schematic connection grid is 1.27 mm. Every placed pin has to land on it."""
    return round(n * 1.27, 2)


def add_m8(sch: Sch, variant: str) -> None:
    """M8 front end. Nets are local labels. Vertical parts on one column are 18
    grid steps apart so a down-stub and the next up-stub do not touch."""
    # Clear of the I2C pull-up labels (y = 58.42) and above the 5 V row.
    j1 = sch.place("Modular:M8", "J1", "M8 A-code", gu(118), gu(64))
    wire_pins(
        sch,
        j1,
        [
            ("+5V", "lbl", "M8_RAW", "left"),
            ("VBAT", "lbl", "VBAT", "left"),
            ("GND", "pwr", "GND", "left"),
            ("VSOL", "lbl", "VSOL", "left"),
        ],
    )

    # M8 pin 1 -> PTC -> TVS to GND -> Schottky into the dev-board 5V pin.
    # D1 anode is the M8 side, so the 5V header cannot feed back out J1.
    f1 = sch.place("Device:PTC", "F1", "MF-R110", gu(86), gu(84))
    wire_pins(sch, f1, [("1", "lbl", "M8_RAW", "left"), ("2", "lbl", "M8_5V", "right")])
    d1 = sch.place("Device:D", "D1", "1N5822", gu(108), gu(84))
    wire_pins(sch, d1, [("1", "lbl", "M8_5V", "left"), ("2", "pwr", "+5V_SPS", "right")])
    d2 = sch.place("Device:TVS", "D2", "P6KE6.8A", gu(124), gu(84))
    wire_pins(sch, d2, [("1", "lbl", "M8_5V", "up"), ("2", "pwr", "GND", "down")])

    # VBAT: TVS at the pin, then 1.00M series/top and 1.00M to GND. ADC = VBAT/2.
    d3 = sch.place("Device:TVS", "D3", "P6KE6.8A", gu(100), gu(96))
    wire_pins(sch, d3, [("1", "lbl", "VBAT", "up"), ("2", "pwr", "GND", "down")])
    r10 = sch.place("Device:R", "R10", "1.00M", gu(116), gu(96))
    wire_pins(sch, r10, [("1", "lbl", "VBAT", "up"), ("2", "lbl", "A_VBAT", "down")])
    c10 = sch.place("Device:C", "C10", "100n", gu(100), gu(114))
    wire_pins(sch, c10, [("1", "lbl", "A_VBAT", "up"), ("2", "pwr", "GND", "down")])
    r11 = sch.place("Device:R", "R11", "1.00M", gu(116), gu(114))
    wire_pins(sch, r11, [("1", "lbl", "A_VBAT", "up"), ("2", "pwr", "GND", "down")])

    # VSOL: TVS at the pin, then 1.80M / 200k. ADC = VSOL/10.
    d4 = sch.place("Device:TVS", "D4", "P6KE30A", gu(132), gu(96))
    wire_pins(sch, d4, [("1", "lbl", "VSOL", "up"), ("2", "pwr", "GND", "down")])
    r12 = sch.place("Device:R", "R12", "1.80M", gu(148), gu(96))
    wire_pins(sch, r12, [("1", "lbl", "VSOL", "up"), ("2", "lbl", "A_VSOL", "down")])
    c11 = sch.place("Device:C", "C11", "100n", gu(132), gu(114))
    wire_pins(sch, c11, [("1", "lbl", "A_VSOL", "up"), ("2", "pwr", "GND", "down")])
    r13 = sch.place("Device:R", "R13", "200k", gu(148), gu(114))
    wire_pins(sch, r13, [("1", "lbl", "A_VSOL", "up"), ("2", "pwr", "GND", "down")])

    # USB-present divider, in the right margin past the sensor pin stubs (x ~ 236).
    # Rows are 20 grid steps apart so a GND stub cannot meet the USBDET stub.
    # The tap is the USB jack VBUS, before the dev board's diode, not the 5V pin.
    if variant == "A":
        c12 = sch.place("Device:C", "C12", "100n", gu(192), gu(40))
        wire_pins(sch, c12, [("1", "lbl", "USBDET", "up"), ("2", "pwr", "GND", "down")])
        j2 = sch.place("Modular:VBUS", "J2", "VBUS tap", gu(210), gu(40))
        wire_pins(sch, j2, [("VBUS", "lbl", "VBUS", "right")])
        r15 = sch.place("Device:R", "R15", "150k", gu(192), gu(60))
        wire_pins(sch, r15, [("1", "lbl", "USBDET", "up"), ("2", "pwr", "GND", "down")])
        r14 = sch.place("Device:R", "R14", "100k", gu(210), gu(60))
        wire_pins(sch, r14, [("1", "lbl", "VBUS", "up"), ("2", "lbl", "USBDET", "down")])
    else:
        r14 = sch.place("Device:R", "R14", "200k", gu(192), gu(34))
        wire_pins(sch, r14, [("1", "lbl", "COMVBUS", "up"), ("2", "lbl", "USBDET", "down")])
        j2 = sch.place("Modular:VBUS", "J2", "COM VBUS", gu(210), gu(34))
        wire_pins(sch, j2, [("VBUS", "lbl", "COMVBUS", "right")])
        r16 = sch.place("Device:R", "R16", "200k", gu(192), gu(54))
        wire_pins(sch, r16, [("1", "lbl", "OTGVBUS", "up"), ("2", "lbl", "USBDET", "down")])
        j3 = sch.place("Modular:VBUS", "J3", "USB VBUS", gu(210), gu(54))
        wire_pins(sch, j3, [("VBUS", "lbl", "OTGVBUS", "right")])
        c12 = sch.place("Device:C", "C12", "100n", gu(192), gu(74))
        wire_pins(sch, c12, [("1", "lbl", "USBDET", "up"), ("2", "pwr", "GND", "down")])
        r15 = sch.place("Device:R", "R15", "100k", gu(210), gu(74))
        wire_pins(sch, r15, [("1", "lbl", "USBDET", "up"), ("2", "pwr", "GND", "down")])


def build(variant: str) -> Sch:
    if variant == "A":
        project = "modular-a"
        title = "Modular outdoor monitor A (USB + M8)"
        comments = [
            "Not the AirGradient V1.3 PCB. Modules plus an M8 A-coded 4-pin panel plug.",
            "USB jack, or M8 pins 1 and 3, feed the dev-board 5V pin. 3V3 pin feeds the I2C modules.",
            "M8: 1 brown +5V, 2 white VBAT, 3 blue GND, 4 black VSOL. Sense only on pins 2 and 4.",
            "D1 1N5822 ORs M8 5V onto the 5V pin. F1 PTC and D2 TVS protect that input.",
            "A4 landscape 297 x 210 mm. Rev D, 2026-11-27.",
        ]
        mcu_id = "Modular:MCU_A"
        mcu_value = "LOLIN32 / D1 mini"
        pin_line = "LOLIN32 and D1 mini: 5V pin after D1, 3V3 pin is the onboard LDO. Do not back-feed 3V3."
        gpio_line = "SDA GPIO21, SCL GPIO22. VBAT GPIO34, VSOL GPIO35, USB detect GPIO32. PH-2 socket stays empty."
        avoid_line = (
            "Leave open: GPIO0/2/12/15 (strap), GPIO5 (LED), GPIO1/3/4, GPIO16/17 (Serial2), GPIO6-11 (flash)."
        )
        usb_line = (
            "J2 is the micro-USB VBUS pad, before the LOLIN32 CJ2301 or the D1 mini Schottky. Not the 5V header."
        )
    else:
        project = "modular-b"
        title = "Modular outdoor monitor B (USB + M8)"
        comments = [
            "Not the AirGradient V1.3 PCB. Modules plus an M8 A-coded 4-pin panel plug.",
            "USB jack, or M8 pins 1 and 3, feed the dev-board 5V pin. 3V3 pin feeds the I2C modules.",
            "M8: 1 brown +5V, 2 white VBAT, 3 blue GND, 4 black VSOL. Sense only on pins 2 and 4.",
            "D1 1N5822 ORs M8 5V onto the 5V pin. F1 PTC and D2 TVS protect that input.",
            "A4 landscape 297 x 210 mm. Rev D, 2026-11-27.",
        ]
        mcu_id = "Modular:MCU_B"
        mcu_value = "ESP32-S3 N16R8"
        pin_line = "DevKitC-1 / AI-S3: 5V pin is after the onboard Schottky. 3V3 pin is the onboard LDO."
        gpio_line = "SDA GPIO8, SCL GPIO9. VBAT GPIO6, VSOL GPIO7, USB detect GPIO10. N16R8 quad flash, octal PSRAM."
        avoid_line = (
            "Leave open: GPIO0/3/45/46 (strap), GPIO19/20 (USB), GPIO43/44 (UART), GPIO33-37 (octal PSRAM), GPIO48 (RGB)."
        )
        usb_line = (
            "J2 and J3 are the two USB-jack VBUS pads, before the DevKitC-1 1N5819s. Not the 5V header."
        )

    sch = Sch(project, title, comments)
    for sym in build_libraries(variant).values():
        sch.add_def(sym)
    for net, graphic in (
        ("GND", GND_GRAPHIC),
        ("+3V3", ARROW_GRAPHIC),
        ("+5V_SPS", ARROW_GRAPHIC),
    ):
        sch.add_power_lib(net, graphic)

    # The dev board's USB connector is the only supply. Its 5V header pin is
    # VBUS (power_out onto +5V_SPS). Its 3V3 header pin is the onboard LDO
    # (power_out onto +3V3). GND is power_in everywhere, so one PWR_FLAG drives it.
    sch.wire(16.51, 132.08, 16.51, 124.46)
    sch.place_power("GND", 16.51, 124.46)
    sch.place_flag(16.51, 132.08)

    mcu = sch.place(mcu_id, "U1", mcu_value, 62.23, 86.36)
    if variant == "A":
        sig = [
            ("IO21", "SDA"),
            ("IO22", "SCL"),
            ("IO34", "A_VBAT"),
            ("IO35", "A_VSOL"),
            ("IO32", "USBDET"),
        ]
    else:
        sig = [
            ("IO8", "SDA"),
            ("IO9", "SCL"),
            ("IO6", "A_VBAT"),
            ("IO7", "A_VSOL"),
            ("IO10", "USBDET"),
        ]
    wire_pins(
        sch,
        mcu,
        [
            ("3V3", "pwr", "+3V3", "left"),
            ("GND", "pwr", "GND", "left"),
            ("5V", "pwr", "+5V_SPS", "left"),
        ]
        + [(name, "lbl", net, "right") for name, net in sig],
    )

    rpu_sda = sch.place("Device:R", "R1", "4.7k", 119.38, 48.26)
    wire_pins(
        sch,
        rpu_sda,
        [
            ("1", "pwr", "+3V3", "up"),
            ("2", "lbl", "SDA", "down"),
        ],
    )
    rpu_scl = sch.place("Device:R", "R2", "4.7k", 137.16, 48.26)
    wire_pins(
        sch,
        rpu_scl,
        [
            ("1", "pwr", "+3V3", "up"),
            ("2", "lbl", "SCL", "down"),
        ],
    )

    sgp = sch.place("Modular:SGP41", "U2", "SGP41 VOC/NOx 0x59", 210.82, 55.88)
    wire_pins(
        sch,
        sgp,
        [
            ("VIN", "pwr", "+3V3", "right"),
            ("3.3V", "nc", None, "right"),
            ("GND", "pwr", "GND", "right"),
            ("SCL", "lbl", "SCL", "right"),
            ("SDA", "lbl", "SDA", "right"),
        ],
    )
    sht = sch.place("Modular:SHT45", "U3", "SHT45 0x44 VIN=3.3V", 210.82, 101.6)
    wire_pins(
        sch,
        sht,
        [
            ("VIN", "pwr", "+3V3", "right"),
            ("3Vo", "nc", None, "right"),
            ("GND", "pwr", "GND", "right"),
            ("SCL", "lbl", "SCL", "right"),
            ("SDA", "lbl", "SDA", "right"),
        ],
    )
    scd41 = sch.place("Modular:SCD41", "U5", "SCD41 0x62  FIT ONE", 210.82, 147.32)
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
    # Lower left, pins facing the margin, clear of U6 and the title block.
    scd30 = sch.place("Modular:SCD30", "U4", "SCD30 0x61  FIT ONE", 48.26, 162.56)
    wire_pins(
        sch,
        scd30,
        [
            ("VDD", "pwr", "+3V3", "left"),
            ("GND", "pwr", "GND", "left"),
            ("TX/SCL", "lbl", "SCL", "left"),
            ("RX/SDA", "lbl", "SDA", "left"),
            ("RDY", "nc", None, "left"),
            ("PWM", "nc", None, "left"),
            ("SEL", "pwr", "GND", "left"),
        ],
    )
    sps = sch.place("Modular:SPS30", "U6", "SPS30 I2C 0x69", 137.16, 162.56)
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

    add_m8(sch, variant)

    # One text object per line. KiCad does not treat \n inside a text string as a break.
    note_lines = [
        "Power: dev-board USB, or J1 M8 pins 1 and 3 when USB is unplugged. Never feed the 3V3 pin.",
        "M8 pin 1: F1 MF-R110, D2 P6KE6.8A, D1 1N5822 (anode at M8) into the dev-board 5V pin = +5V_SPS = SPS30 VDD.",
        "M8 pin 2 VBAT 2.7-4.6 V: D3 P6KE6.8A, R10/R11 1.00M/1.00M, C10 100n. ADC = VBAT/2 (4.6 V -> 2.30 V, 6.2 V -> 3.10 V).",
        "M8 pin 4 VSOL up to 22 V: D4 P6KE30A, R12/R13 1.80M/200k, C11 100n. ADC = VSOL/10 (22 V -> 2.20 V, 25 V -> 2.50 V, 31 V -> 3.10 V).",
        usb_line,
        "Firmware reads A_VBAT and A_VSOL, and reports both as 0 while USBDET is above 1.2 V.",
        pin_line,
        gpio_line,
        "I2C is 100 kHz at 3.3 V. R1 and R2 are 4.7k to +3V3. Fit U4 or U5, not both. U6 SEL to GND before power-up.",
        avoid_line,
    ]
    note_y = 6.35
    for line in note_lines:
        sch.text(line, 8.89, note_y, 1.016, "left top")
        note_y += 2.54
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
