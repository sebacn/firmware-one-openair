// Two shells based on the AirGradient DIY outdoor enclosure.
// Original top is 91.5 x 85.0 x 81.9 mm. The published product is
// 91.5 x 86.7 x 85 mm. These keep that footprint and only add height.
//
//   openscad -o outdoor-flat/shell.stl -D 'mode="flat"' -D 'part="shell"' outdoor.scad
//
// mode: "flat" or "vertical"
// part: shell, lid, grill

mode = "flat";
part = "shell";

W = 91.5;
D = 86.7;
wall = 2.6;
floor_t = 2.4;
rad = 9;

function body_h() = mode == "flat" ? 112 : 94;

module rr(w, d, h, r) {
    hull() {
        for (x = [-1, 1], y = [-1, 1])
            translate([x * (w / 2 - r), y * (d / 2 - r), 0])
                cylinder(h = h, r = r, $fn = 24);
    }
}

module boss(h = 4.8, r = 3.0) {
    difference() {
        cylinder(h = h, r = r, $fn = 16);
        translate([0, 0, -0.2]) cylinder(h = h + 0.4, r = 1.15, $fn = 12);
    }
}

module tie(length = 8) {
    difference() {
        cube([length, 3.2, 2.2]);
        translate([1.4, 0.8, -0.2]) cube([length - 2.8, 1.6, 3]);
    }
}

module shell() {
    H = body_h();
    difference() {
        rr(W, D, H, rad);
        translate([0, 0, floor_t])
            rr(W - 2 * wall, D - 2 * wall, H, rad - 1.4);
        // USB-C, low on the -X wall, same side as the original.
        translate([-W / 2 - 2, 4, 28]) cube([8, 12, 7]);
        // M8x1 female receptacle. Hole 8.2 mm, keep-out for nut and cups.
        translate([30, 28, -2]) {
            cylinder(h = 8, d = 8.2, $fn = 28);
            translate([0, 0, 4]) cylinder(h = 14, d = 14, $fn = 28);
        }
        // Two PM ports in the floor, under the SPS30. Inlet is +Y.
        for (y = [-6, 16])
            translate([2, y, -2]) cylinder(h = 8, d = 16, $fn = 24);
        // Exhaust louvers on +X, opposite the USB wall.
        for (i = [0 : 3])
            translate([W / 2 - 4, -4 + i * 6, 8]) rotate([0, 90, 0])
                cylinder(h = 10, d = 4, $fn = 14);
        // Intake vents for the SHT45, front face.
        for (i = [0 : 3])
            translate([-8 + i * 7, D / 2 - 4, 16]) rotate([-90, 0, 0])
                cylinder(h = 10, d = 4, $fn = 14);
    }
    // Sensor floor, same in both modes.
    for (x = [-12, 16], y = [-8, 18])
        translate([x, y, floor_t]) boss();
    for (x = [-38, -16], y = [-2, 14])
        translate([x, y, floor_t]) boss();
    for (x = [-40, -26], y = [-6, 6])
        translate([x, y, 20]) boss();
    for (x = [12, 34], y = [18, 32])
        translate([x, y, 12]) boss();
    if (mode == "flat") {
        // Attic floor for the pack, above the electronics.
        for (x = [-24, 24], y = [-16, 16])
            translate([x, y, 78]) boss(3.2, 2.4);
        translate([-20, 30, 24]) tie(12);
        translate([8, -36, 24]) tie(10);
    } else {
        // Side bay bosses are the pack rails.
        translate([28, -36, 8]) cube([2.2, 28, 3]);
        translate([28, -36, 62]) cube([2.2, 28, 3]);
        translate([-20, 28, 24]) tie(12);
    }
}

module lid() {
    difference() {
        rr(W, D, 6, rad);
        translate([0, 0, 2.2])
            rr(W - 2 * wall - 0.6, D - 2 * wall - 0.6, 5, rad - 1.8);
    }
}

module grill() {
    difference() {
        hull() {
            for (x = [-1, 1], y = [-1, 1])
                translate([x * 12, y * 10, 0]) cylinder(h = 2, r = 5, $fn = 18);
        }
        for (x = [-8, 0, 8], y = [-6, 4, 12])
            translate([x, y, -0.2]) cylinder(h = 3, d = 3, $fn = 10);
    }
}

if (part == "shell") shell();
else if (part == "lid") lid();
else if (part == "grill") grill();
