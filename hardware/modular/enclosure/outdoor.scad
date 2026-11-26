// Two outdoor variants that keep the AirGradient DIY three-part stack:
//   grill  — round bottom screen (original part A, ~72 mm)
//   base   — open ring the grill drops into (original part B, ~83 mm)
//   cover  — sleeve that slides over the ring (original part C, 91.5 x 86.7)
//
// The cover's lower opening is 84.2 mm so it slides over the 83 mm ring
// with about 0.6 mm per side, the same sleeve fit as the original.
//
//   openscad -o outdoor-flat/base.stl -D 'mode="flat"' -D 'part="base"' outdoor.scad
//
// mode: "flat" or "vertical"
// part: grill, base, cover

mode = "flat";
part = "base";

// Cover plan matches the published Open Air, 91.5 x 86.7 mm.
W = 91.5;
D = 86.7;
// Base ring, original part B is 83.0 x 82.9 x 26.7.
ring = 83.0;
ring_h = 28.0;
// Slide: cover inner opening over the ring.
slide_clear = 0.6;
slide_overlap = 16.0;
wall = 2.4;
rad = 8;

// Flat: +30 mm attic for a 22 mm pack under the lid.
// Vertical: +12 mm so a 70 mm pack plus a 4 mm PCM stands inside.
function cover_h() = mode == "flat" ? 112 : 94;

module rr(w, d, h, r) {
    hull() {
        for (x = [-1, 1], y = [-1, 1])
            translate([x * (w / 2 - r), y * (d / 2 - r), 0])
                cylinder(h = h, r = r, $fn = 24);
    }
}

module boss(h = 4.8) {
    difference() {
        cylinder(h = h, r = 3.0, $fn = 16);
        translate([0, 0, -0.2]) cylinder(h = h + 0.4, r = 1.15, $fn = 12);
    }
}

// Round grill, original part A. Sits on the ring lip.
module grill() {
    difference() {
        cylinder(h = 3.2, d = 70, $fn = 64);
        // Particle screen, clear of the USB pocket and the M8 hole.
        for (x = [-12, 0, 12], y = [-4, 8, 18])
            translate([x, y, -0.4]) cylinder(h = 4, d = 3.4, $fn = 12);
        // Three screws into the ring lip.
        for (a = [0, 120, 240])
            rotate([0, 0, a]) translate([30, 0, -0.4])
                cylinder(h = 4, d = 3.2, $fn = 12);
    }
}

module base() {
    difference() {
        rr(ring, ring, ring_h, rad);
        // Open centre. Lip at z=3.2 supports the grill.
        translate([0, 0, 3.2]) cylinder(h = ring_h, d = 68, $fn = 64);
        // PM ports through the ring floor, under the SPS30.
        for (y = [-6, 16])
            translate([2, y, -1]) cylinder(h = 6, d = 16, $fn = 24);
        // M8x1 female receptacle. 8.2 mm thread hole, 14 mm cup keep-out.
        translate([30, 26, -1]) {
            cylinder(h = 8, d = 8.2, $fn = 28);
            translate([0, 0, 3.2]) cylinder(h = 14, d = 14, $fn = 28);
        }
        // USB-C recess in the bottom face, opposite the M8 and clear of the
        // particle ports. The hole is smaller than the recess so the
        // connector sits up inside a drip lip.
        translate([-26, -28, -1]) cube([18, 14, 3.4], center = false);
        translate([-22, -24, -1]) cube([10, 6, 8], center = false);
    }
    // Optional cap boss beside the USB recess.
    translate([-30, -16, 0]) difference() {
        cylinder(h = 4, d = 6, $fn = 16);
        translate([0, 0, 1.6]) cylinder(h = 3, d = 2.4, $fn = 12);
    }
    // Grill screw bosses on the lip.
    for (a = [0, 120, 240])
        rotate([0, 0, a]) translate([30, 0, 3.2])
            difference() {
                cylinder(h = 3.2, d = 7, $fn = 16);
                translate([0, 0, -0.2]) cylinder(h = 4, d = 2.2, $fn = 12);
            }
}

module cover() {
    H = cover_h();
    difference() {
        rr(W, D, H, rad + 1);
        // Sleeve. The bottom opening is 84.2 mm across so it slides
        // over the 83 mm ring for slide_overlap millimetres.
        translate([0, 0, -0.2])
            rr(ring + 2 * slide_clear, ring + 2 * slide_clear, slide_overlap + 0.2, rad - 0.4);
        translate([0, 0, slide_overlap])
            rr(W - 2 * wall, D - 2 * wall, H, rad - 0.6);
        // Side exhaust, above the sleeve, opposite the USB wall.
        for (i = [0 : 3])
            translate([W / 2 - 3, -8 + i * 6, slide_overlap + 6])
                rotate([0, 90, 0]) cylinder(h = 8, d = 4, $fn = 12);
        // Intake louvers for the SHT45, front face.
        for (i = [0 : 3])
            translate([-10 + i * 7, D / 2 - 3, slide_overlap + 10])
                rotate([-90, 0, 0]) cylinder(h = 8, d = 4, $fn = 12);
    }
    // Standoffs for the sensor floor, measured from the top of the sleeve
    // once the cover is seated (the ring floor is below this).
    z0 = slide_overlap + 1;
    for (x = [-10, 14], y = [-8, 16])
        translate([x, y, z0]) boss();
    for (x = [-36, -16], y = [-2, 14])
        translate([x, y, z0]) boss();
    for (x = [-38, -24], y = [-8, 4])
        translate([x, y, z0 + 16]) boss();
    for (x = [8, 30], y = [16, 30])
        translate([x, y, z0 + 8]) boss();
    if (mode == "flat") {
        for (x = [-22, 22], y = [-14, 14])
            translate([x, y, H - 28]) boss(3.0);
        translate([-16, 28, z0 + 18]) cube([14, 2.4, 2]);
    } else {
        // Rails for the pack standing on the +X wall.
        translate([26, -30, z0 + 4]) cube([2.2, 24, 3]);
        translate([26, -30, z0 + 58]) cube([2.2, 24, 3]);
        translate([-16, 26, z0 + 18]) cube([14, 2.4, 2]);
    }
}

if (part == "grill") grill();
else if (part == "base") base();
else if (part == "cover") cover();
