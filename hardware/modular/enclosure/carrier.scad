// Carrier that replaces the original Open Air grill.
// The lower 5 mm match the grill seat: a 64 mm plug through the lip,
// then a 71 mm flange that rests on it. Towers stay inside the cover.
// Units are millimetres. Origin is the enclosure centre, z = 0 is the
// outside bottom face.

$fn = 36;

module plate() {
    difference() {
        union() {
            cylinder(d = 64, h = 3);
            translate([0, 0, 3]) cylinder(d = 71, h = 2.2);
        }
        // SPS30 inlet, under the standing sensor.
        translate([0, 28, -0.2]) cube([34, 8, 6], center = true);
        // Vents under the three boards that face down.
        vent_field(-25, 8, 12, 16);
        vent_field(3, 8, 22, 14);
        vent_field(0, -27, 16, 12);
        // USB cable from below, under the dev board.
        translate([0, -10, -0.2]) cube([18, 10, 6], center = true);
        // M8 x 0.5 thread. 8.2 mm passes the major diameter.
        translate([22, -4, -0.2]) cylinder(d = 8.2, h = 12);
        // Nut pocket, 16 mm across, above the flange.
        translate([22, -4, 5.0]) cylinder(d = 16, h = 6);
    }
}

module vent_field(x, y, w, d) {
    for (ix = [-1, 0, 1])
        for (iy = [-1, 0, 1])
            translate([x + ix * w / 3, y + iy * d / 3, -0.2])
                cylinder(d = 3.2, h = 8);
}

module post(x, y) {
    difference() {
        translate([x, y, 5.2]) cylinder(d = 5.2, h = 6);
        translate([x, y, 6.5]) cylinder(d = 1.8, h = 6);
    }
}

module rail(x, y, w, d, h) {
    translate([x, y, 5.2]) cube([w, d, h], center = false);
}

module tie(x, y) {
    difference() {
        translate([x, y, 5.2]) cube([8, 3, 4], center = true);
        translate([x, y, 6.4]) cube([5, 4, 2], center = true);
    }
}

module carrier() {
    plate();
    // Thermal wall between the SHT45 and the SCD30.
    translate([-19.5, -8, 5.2]) cube([1.6, 20, 14]);
    // Standoffs under the three boards that face down. Two each, inset from the corners.
    for (p = [[-32, -2], [-20, 16], [-10, 0], [16, 16], [-8, -33], [8, -21]])
        post(p[0], p[1]);
    // SPS30 clips. The 12.2 mm body drops between the rails, inlet down.
    translate([-16, 19.6, 5.2]) cube([32, 1.4, 16]);
    translate([-16, 34.8, 5.2]) cube([32, 1.4, 16]);
    // ESP32 channel. The 28 mm width runs across X. USB end opens over the slot.
    translate([-16, -3.0, 5.2]) cube([32, 1.4, 12]);
    // Wire ties in the gutters and beside the M8 solder cups.
    tie(-8, 16);
    tie(6, -12);
    tie(14, -18);
}

carrier();
