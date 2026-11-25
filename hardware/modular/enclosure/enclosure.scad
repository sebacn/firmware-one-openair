// Modular outdoor enclosure, three placement variants.
// Style follows the AirGradient outdoor DIY shell: rounded rectangular body,
// bottom PM screen, side USB. Wires are soldered, so there are no sockets.
//
//   openscad -o variant-1/shell.stl -D 'variant=1' -D 'part="shell"' enclosure.scad
//
// Parts: shell, lid, grill, divider
// Units: millimetres.

variant = 1;
part = "shell";

W = 98;
D = 94;
wall = 2.6;
floor_t = 2.4;
rad = 10;
eps = 0.4;

function body_h(v) = v == 1 ? 106 : (v == 2 ? 122 : 130);

module rr(w, d, h, r) {
    hull() {
        for (x = [-1, 1], y = [-1, 1])
            translate([x * (w / 2 - r), y * (d / 2 - r), 0])
                cylinder(h = h, r = r, $fn = 28);
    }
}

module boss(h = 5.2, r = 3.1) {
    difference() {
        cylinder(h = h, r = r, $fn = 18);
        translate([0, 0, -0.2]) cylinder(h = h + 0.4, r = 1.15, $fn = 12);
    }
}

// Cable-tie bridge: a 8 x 3 x 2.4 bar with a 4 x 1.6 slot.
module tie(length = 8) {
    difference() {
        cube([length, 3.2, 2.4]);
        translate([1.6, 0.8, -0.2]) cube([length - 3.2, 1.6, 3]);
    }
}

// Strain-relief bar: wires pass under a 2 mm bridge.
module strain(span = 14) {
    difference() {
        cube([span, 4, 4.2]);
        translate([1.2, -0.2, 1.4]) cube([span - 2.4, 4.6, 1.8]);
    }
}

module usb_slot() {
    // BQ25185 USB-C, reachable on the -X wall, drip lip left in the shell.
    h = variant == 2 ? 96 : (variant == 3 ? 70 : 34);
    translate([-W / 2 - 2, 8, h]) cube([8, 12, 7]);
}

module solar_hole() {
    // SP13 IP68 2-pin panel mount. Thread needs a 13 mm hole.
    // Variant 2 keeps the hole in the front corner so it misses the battery plinth.
    if (variant == 2)
        translate([34, 32, -2]) cylinder(h = 8, d = 13, $fn = 32);
    else
        translate([28, -30, -2]) cylinder(h = 8, d = 13, $fn = 32);
}

module pm_ports() {
    // Two 16 mm ports in the floor, under the SPS30. Inlet is the front one.
    // Variant 2 carries the battery on that floor, so the air enters from the side.
    if (variant == 2) {
        for (z = [8, 16])
            translate([W / 2 - 4, 6, z]) rotate([0, 90, 0])
                cylinder(h = 10, d = 12, $fn = 24);
    } else {
        for (y = [-8, 14])
            translate([6, y, -2]) cylinder(h = 8, d = 16, $fn = 28);
    }
}

module side_louvers(z0, n = 4) {
    for (i = [0 : n - 1])
        translate([W / 2 - 4, -6 + i * 7, z0]) rotate([0, 90, 0])
            cylinder(h = 10, d = 4.2, $fn = 16);
}

module cool_vents(z0) {
    for (i = [0 : 3])
        translate([-W / 2 - 2, 22 + i * 6, z0]) rotate([0, 90, 0])
            cylinder(h = 10, d = 4.2, $fn = 16);
}

module shell() {
    H = body_h(variant);
    difference() {
        rr(W, D, H, rad);
        translate([0, 0, floor_t])
            rr(W - 2 * wall, D - 2 * wall, H, rad - 1.6);
        usb_slot();
        solar_hole();
        pm_ports();
        // SPS30 exhaust leaves sideways, not into the cool bay.
        side_louvers(variant == 2 ? 40 : 8, 3);
        cool_vents(variant == 2 ? 58 : (variant == 3 ? 18 : 28));
        // CO2 bay vents, opposite the exhaust.
        if (variant != 2)
            for (i = [0 : 3])
                translate([-10 + i * 8, -D / 2 - 2, variant == 3 ? 36 : 52])
                    rotate([-90, 0, 0]) cylinder(h = 10, d = 4.2, $fn = 16);
        else
            for (i = [0 : 3])
                translate([-10 + i * 8, -D / 2 - 2, 78])
                    rotate([-90, 0, 0]) cylinder(h = 10, d = 4.2, $fn = 16);
    }
    standoffs();
    guides();
}

module standoffs() {
    // 4.5 mm so a solder fillet and a wire leaving the pad clear the floor.
    h = 4.8;
    if (variant == 1) {
        // SPS30, front, over the floor ports.
        for (x = [-16, 16], y = [-4, 22])
            translate([x, y, floor_t]) boss(h);
        // Cool bay: SHT45 and SGP41, front-left, above the SPS30.
        for (x = [-38, -22], y = [18, 32])
            translate([x, y, 24]) boss(h);
        // SCD30, mid, side vents behind it.
        for (x = [-20, 4], y = [-28, -12])
            translate([x, y, 50]) boss(h);
        // ESP32, BQ25185, TPS63020 on the upper shelf.
        for (x = [-30, 18], y = [6, 28])
            translate([x, y, 74]) boss(h);
        for (x = [22, 36], y = [-8, 6])
            translate([x, y, 74]) boss(3.6, 2.6);
    } else if (variant == 2) {
        // Battery plinth uses the floor. Sensors sit on a raised deck.
        for (x = [-16, 16], y = [-6, 20])
            translate([x, y, 32]) boss(h);
        for (x = [-38, -22], y = [16, 30])
            translate([x, y, 52]) boss(h);
        for (x = [-18, 6], y = [-30, -14])
            translate([x, y, 74]) boss(h);
        for (x = [-28, 16], y = [8, 28])
            translate([x, y, 96]) boss(h);
        for (x = [24, 38], y = [-6, 8])
            translate([x, y, 96]) boss(3.6, 2.6);
    } else {
        // Lower pod is only sensors. Electronics and the battery are above the bulkhead.
        for (x = [-16, 16], y = [-6, 20])
            translate([x, y, floor_t]) boss(h);
        for (x = [-38, -22], y = [14, 30])
            translate([x, y, 22]) boss(h);
        for (x = [-16, 8], y = [-32, -16])
            translate([x, y, 40]) boss(h);
        for (x = [-28, 16], y = [10, 30])
            translate([x, y, 86]) boss(h);
        for (x = [22, 36], y = [-4, 10])
            translate([x, y, 86]) boss(3.6, 2.6);
    }
}

module guides() {
    // Wire gutters: tie anchors and a strain bar at each zone exit.
    if (variant == 1) {
        translate([-46, 8, 29]) tie(10);
        translate([-46, 24, 29]) tie(10);
        translate([-44, 4, 29]) strain(16);
        translate([18, -36, 55]) tie(10);
        translate([30, -20, 55]) strain(12);
        translate([-20, 0, 79]) tie(12);
        translate([8, 34, 79]) strain(18);
        // Battery strap slots in the rear pocket.
        translate([-30, -40, 20]) cube([60, 2.2, 3]);
        translate([-30, -40, 64]) cube([60, 2.2, 3]);
    } else if (variant == 2) {
        translate([-36, -8, 8]) tie(12);
        translate([20, -8, 8]) tie(12);
        translate([-10, 20, 8]) strain(20);
        translate([-44, 10, 57]) tie(10);
        translate([16, -36, 79]) tie(10);
        translate([-16, 4, 101]) strain(16);
    } else {
        translate([-44, 8, 27]) tie(10);
        translate([-44, 22, 27]) strain(14);
        translate([8, -36, 45]) tie(10);
        translate([-20, -8, 64]) strain(22);
        translate([6, 34, 91]) tie(12);
        translate([-28, -36, 96]) tie(12);
    }
}

module lid() {
    difference() {
        rr(W, D, 6, rad);
        translate([0, 0, 2.2]) rr(W - 2 * wall - 0.6, D - 2 * wall - 0.6, 5, rad - 2);
        // Four corner screw holes into the shell rim.
        for (x = [-1, 1], y = [-1, 1])
            translate([x * (W / 2 - 8), y * (D / 2 - 8), -0.2])
                cylinder(h = 8, r = 1.6, $fn = 14);
    }
}

module grill() {
    // Round screen in the spirit of the original bottom plate, over the PM ports.
    difference() {
        hull() {
            for (x = [-1, 1], y = [-1, 1])
                translate([x * 14, y * 10, 0]) cylinder(h = 2, r = 6, $fn = 20);
        }
        for (x = [-10, 0, 10], y = [-6, 4, 12])
            translate([x, y, -0.2]) cylinder(h = 3, d = 3.2, $fn = 12);
    }
}

module divider() {
    // Thermal wall between the SPS30 exhaust side and the SHT/SGP bay.
    if (variant == 1)
        cube([2.2, 36, 28]);
    else if (variant == 2)
        cube([2.2, 34, 24]);
    else
        cube([2.2, 40, 32]);
}

if (part == "shell") shell();
else if (part == "lid") lid();
else if (part == "grill") grill();
else if (part == "divider") divider();
