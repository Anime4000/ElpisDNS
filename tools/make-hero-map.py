#!/usr/bin/env python3
"""
Generates img/hero-map.svg - the animated night map behind the hero banner.

Run it only when you want to change the map, the arcs or the ASN list:

    python tools/make-hero-map.py

The site itself needs no build step. This exists because the landmass is a
few hundred dots sampled from coastline polygons, and nobody should have to
type those by hand.

Two files come out:

    img/hero-map.svg         animated, used by .hero-banner::after
    img/hero-map-static.svg  no animation, served to prefers-reduced-motion

Projection is plain equirectangular, rolled so the Asia-Pacific sits in the
middle of the frame: Europe on the left where the hero text covers it, the
Malacca Strait dead centre, the US west coast on the right edge.
"""

import math
import os

# ---------------------------------------------------------------- geometry

W, H = 900, 420

LON0, LON1 = -20.0, 258.0      # 278 degrees of longitude, left to right
LAT_TOP = 60.0                 # top edge of the map band
SCALE = W / (LON1 - LON0)      # px per degree, identical on both axes
MAP_TOP = 32.0                 # empty band above the map, for HUD labels
MAP_H = H - MAP_TOP - 32.0     # and one below it, for the status line
LAT_BOTTOM = LAT_TOP - MAP_H / SCALE


def pxn(lon, lat):
    """Canvas coordinates for a longitude already rolled into frame space."""
    return ((lon - LON0) * SCALE, (LAT_TOP - lat) * SCALE + MAP_TOP)


def px(lon, lat):
    """Longitude/latitude to canvas coordinates, rolling the far side east."""
    if lon < LON0:
        lon += 360.0
    return pxn(lon, lat)


def fmt(value):
    return f"{value:.1f}".rstrip("0").rstrip(".")


def point(lon, lat):
    x, y = px(lon, lat)
    return fmt(x), fmt(y)


# ------------------------------------------------------------- coastlines
#
# Deliberately rough. At 3 degree dot spacing anything finer is invisible,
# and a hand-typed coastline that pretends to be survey grade would be a
# lie told in 400 coordinate pairs.

LAND = [
    # Europe
    [(-10, 36), (-9, 43), (-2, 43), (-2, 48), (2, 51), (4, 52), (8, 54),
     (9, 57), (11, 58), (14, 55), (19, 55), (21, 56), (24, 59), (28, 60),
     (30, 60), (31, 62), (29, 66), (24, 66), (21, 70), (28, 71), (35, 68),
     (40, 66), (45, 66), (50, 68), (58, 70), (60, 68), (60, 60), (57, 56),
     (52, 52), (48, 48), (40, 45), (37, 44), (30, 45), (28, 41), (23, 40),
     (19, 40), (16, 41), (12, 38), (15, 37), (18, 40), (13, 45), (9, 44),
     (4, 43), (3, 42), (-2, 36), (-6, 36), (-10, 36)],

    # Scandinavia lobe, so the Baltic does not swallow Norway
    [(5, 58), (8, 63), (12, 65), (16, 69), (22, 70), (25, 69), (20, 65),
     (15, 62), (11, 59), (5, 58)],

    # Britain and Ireland
    [(-6, 50), (-3, 53), (-2, 56), (-4, 58), (-6, 57), (-7, 54), (-6, 50)],

    # Africa
    [(-17, 15), (-16, 20), (-13, 25), (-9, 30), (-6, 35), (0, 36), (10, 37),
     (11, 33), (20, 32), (25, 31), (32, 31), (35, 28), (37, 22), (39, 15),
     (43, 12), (51, 12), (51, 8), (45, 5), (42, 0), (41, -5), (40, -10),
     (36, -18), (35, -24), (32, -28), (28, -32), (22, -34), (18, -34),
     (15, -28), (13, -22), (12, -16), (9, -5), (6, 0), (9, 4), (3, 6),
     (-4, 5), (-8, 4), (-13, 8), (-16, 12), (-17, 15)],

    # Madagascar
    [(44, -12), (49, -14), (50, -18), (47, -25), (45, -22), (43, -17), (44, -12)],

    # Arabia and the Middle East
    [(34, 28), (38, 32), (44, 33), (48, 30), (52, 25), (56, 26), (59, 23),
     (57, 19), (52, 15), (45, 13), (43, 16), (39, 21), (35, 25), (34, 28)],

    # Asia, the big one
    [(35, 45), (40, 45), (45, 42), (50, 40), (55, 37), (58, 30), (60, 25),
     (63, 25), (67, 24), (70, 21), (73, 16), (77, 8), (80, 10), (81, 16),
     (85, 20), (88, 22), (92, 21), (95, 17), (97, 10), (100, 6), (103, 1),
     (104, 8), (107, 11), (109, 15), (108, 21), (112, 22), (118, 24),
     (122, 30), (122, 37), (126, 40), (128, 43), (131, 43), (135, 48),
     (140, 53), (143, 55), (150, 59), (155, 60), (160, 62), (165, 62),
     (170, 65), (178, 68), (180, 70), (170, 72), (160, 72), (150, 73),
     (140, 74), (130, 74), (120, 75), (110, 76), (100, 77), (90, 76),
     (80, 74), (70, 73), (66, 70), (62, 68), (60, 64), (60, 55), (58, 52),
     (52, 50), (48, 48), (42, 47), (35, 45)],

    # Japan
    [(129, 32), (133, 34), (136, 35), (139, 35), (141, 38), (141, 41),
     (143, 43), (145, 44), (144, 45), (141, 42), (138, 37), (134, 34),
     (131, 31), (129, 32)],

    # Sumatra
    [(95, 5), (98, 3), (101, -2), (105, -6), (106, -5), (102, -1), (99, 4),
     (95, 5)],

    # Borneo
    [(109, 2), (112, 4), (117, 5), (119, 1), (117, -3), (114, -4), (111, -3),
     (109, -1), (109, 2)],

    # Java and the lesser Sundas
    [(105, -6), (110, -7), (114, -8), (118, -9), (123, -9), (120, -10),
     (114, -9), (108, -8), (105, -6)],

    # Sulawesi
    [(119, 1), (122, 1), (124, 1), (125, -2), (122, -5), (120, -3), (119, 1)],

    # Philippines
    [(120, 18), (122, 16), (124, 12), (126, 8), (123, 7), (121, 12), (120, 18)],

    # New Guinea
    [(131, -1), (136, -2), (141, -3), (147, -6), (150, -9), (146, -9),
     (140, -7), (134, -4), (131, -1)],

    # Australia
    [(114, -22), (113, -26), (115, -32), (118, -35), (125, -33), (130, -32),
     (135, -35), (138, -35), (141, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (148, -20), (143, -13), (136, -12), (130, -12), (126, -14),
     (122, -17), (114, -22)],

    # New Zealand
    [(172, -41), (174, -37), (178, -38), (176, -41), (170, -45), (167, -46),
     (172, -41)],

    # Alaska and the Canadian west, at the right edge of the frame
    [(-168, 66), (-166, 60), (-158, 57), (-152, 58), (-145, 60), (-140, 59),
     (-135, 57), (-130, 52), (-125, 48), (-124, 42), (-121, 35), (-117, 32),
     (-114, 30), (-112, 26), (-116, 30), (-120, 34), (-124, 40), (-128, 50),
     (-133, 54), (-140, 60), (-148, 60), (-156, 58), (-162, 63), (-168, 66)],
]


def normalize(poly):
    """
    Roll a polygon into the frame's longitude space, all points together.

    Without this, a shape straddling the left seam - Africa starts at 17W,
    the frame starts at 20W - ends up with half its points at x=1200 and
    half at x=60, and the fill paints a band clean across the map.
    """
    rolled = [(lon + 360.0 if lon < LON0 else lon, lat) for lon, lat in poly]
    lons = [lon for lon, _ in rolled]
    if max(lons) - min(lons) > 180.0:
        rolled = [(lon - 360.0 if lon >= LON0 + 180.0 else lon, lat)
                  for lon, lat in rolled]
    return rolled


LAND = [normalize(poly) for poly in LAND]


def inside(lon, lat, poly):
    """Ray casting, the usual."""
    hit = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            cut = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < cut:
                hit = not hit
    return hit


def land_path(poly):
    """Coastline outline, so the dot field reads as land and not as noise."""
    parts = []
    for i, (lon, lat) in enumerate(poly):
        x, y = pxn(lon, lat)
        parts.append(f"{'M' if i == 0 else 'L'}{fmt(x)} {fmt(y)}")
    return " ".join(parts) + " Z"


def land_dots(step=2.4):
    dots = []
    lat = LAT_TOP
    row = 0
    while lat > LAT_BOTTOM:
        lon = LON0
        col = 0
        while lon < LON1:
            if any(inside(lon, lat, poly) for poly in LAND):
                # Deterministic jitter, so the grid does not read as graph paper
                seed = (row * 73 + col * 151) % 97
                bucket = 0 if seed % 7 == 0 else (1 if seed % 3 else 2)
                x, y = pxn(lon, lat)
                dots.append((x, y, bucket))
            lon += step
            col += 1
        lat -= step
        row += 1
    return dots


# ------------------------------------------------------------------- data

HUB = (102.5, 2.2)          # the Malacca Strait, where ΕΛΠΙΣ lives

CITIES = {
    "kul": (101.7, 3.15), "sin": (103.8, 1.29), "jkt": (106.8, -6.2),
    "hkg": (114.2, 22.3), "tyo": (139.7, 35.7), "syd": (151.2, -33.9),
    "bom": (72.9, 19.1), "dxb": (55.3, 25.2), "fra": (8.7, 50.1),
    "lon": (-0.1, 51.5), "sea": (-122.3, 47.6), "lax": (-118.2, 34.05),
    "mnl": (121.0, 14.6), "icn": (127.0, 37.5), "per": (115.9, -32.0),
    "jnb": (28.0, -26.2), "bkk": (100.5, 13.75), "tpe": (121.5, 25.0),
    "pek": (116.4, 39.9), "kch": (110.3, 1.55),
}

# Arcs out of the hub. (destination, phase one duration, start delay)
ARCS = [
    ("tyo", 3.6, 0.20), ("hkg", 3.0, 0.55), ("syd", 4.0, 0.90),
    ("bom", 3.4, 1.25), ("lax", 4.4, 1.60), ("sea", 4.6, 0.35),
    ("fra", 4.2, 1.95), ("mnl", 2.8, 2.30), ("icn", 3.2, 0.75),
    ("jkt", 2.4, 1.10), ("per", 3.0, 2.60), ("dxb", 3.8, 1.45),
]

# Long hauls that ignore the hub, for depth across the Pacific.
CROSS = [
    ("tyo", "lax", 4.8, 1.0), ("fra", "bom", 4.4, 2.2),
    ("syd", "sea", 5.2, 0.6), ("icn", "lax", 5.0, 2.8),
    ("tpe", "syd", 4.0, 1.7),
]

# The HUD walks this list, one target at a time.
TARGETS = [
    ("AS4788", "TM NET", "MY", "kul"),
    ("AS15169", "GOOGLE", "US", "lax"),
    ("AS154516", "PERFECT NETWORK", "MY", "kch"),
    ("AS13335", "CLOUDFLARE", "US", "sea"),
    ("AS9930", "TIME DOTCOM", "MY", "sin"),
    ("AS2914", "NTT", "JP", "tyo"),
    ("AS7713", "TELKOM INDONESIA", "ID", "jkt"),
    ("AS4657", "STARHUB", "SG", "sin"),
    ("AS4837", "CHINA UNICOM", "CN", "pek"),
    ("AS6939", "HURRICANE ELECTRIC", "US", "sea"),
    ("AS153334", "ORIGIN TECHLAB", "MY", "bkk"),
    ("AS135134", "SHANA NETWORK", "SG", "tpe"),
]

# Things that do not get through. (source city, verdict, cycle offset)
THREATS = [
    ("pek", "TRACKER", 1.4),
    ("bom", "MALWARE", 4.2),
    ("tyo", "PHISHING", 6.9),
    ("syd", "AD BEACON", 9.6),
    ("lax", "SPYWARE", 12.1),
]

CYCLE = 2.15            # seconds each ASN holds the reticle
THREAT_CYCLE = 14.0     # seconds between repeats of one threat


# ------------------------------------------------------------------ paths

def arc(a, b, bend=0.24, lift=1.0):
    """Quadratic bezier between two canvas points, bowed away from the equator."""
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    span = math.hypot(dx, dy)
    # Perpendicular, always pointing up the canvas so arcs look like great circles
    nx, ny = -dy / span, dx / span
    if ny > 0:
        nx, ny = -nx, -ny
    cx, cy = mx + nx * span * bend * lift, my + ny * span * bend * lift
    return (cx, cy)


def arc_path(p1, p2, bend=0.24):
    cx, cy = arc(p1, p2, bend)
    return (f"M{fmt(p1[0])} {fmt(p1[1])} Q{fmt(cx)} {fmt(cy)} "
            f"{fmt(p2[0])} {fmt(p2[1])}")


def arc_length(p1, p2, bend=0.24):
    cx, cy = arc(p1, p2, bend)
    total, prev = 0.0, p1
    for i in range(1, 41):
        t = i / 40
        u = 1 - t
        x = u * u * p1[0] + 2 * u * t * cx + t * t * p2[0]
        y = u * u * p1[1] + 2 * u * t * cy + t * t * p2[1]
        total += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
    return total


def trim(p1, p2, bend, keep):
    """Point a given distance short of the end of an arc, and the arc up to it."""
    cx, cy = arc(p1, p2, bend)
    length = arc_length(p1, p2, bend)
    want = max(0.0, length - keep)
    total, prev, cut = 0.0, p1, 1.0
    for i in range(1, 121):
        t = i / 120
        u = 1 - t
        x = u * u * p1[0] + 2 * u * t * cx + t * t * p2[0]
        y = u * u * p1[1] + 2 * u * t * cy + t * t * p2[1]
        total += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
        if total >= want:
            cut = t
            break
    # de Casteljau split at cut
    ax = p1[0] + (cx - p1[0]) * cut
    ay = p1[1] + (cy - p1[1]) * cut
    bx = cx + (p2[0] - cx) * cut
    by = cy + (p2[1] - cy) * cut
    ex = ax + (bx - ax) * cut
    ey = ay + (by - ay) * cut
    path = f"M{fmt(p1[0])} {fmt(p1[1])} Q{fmt(ax)} {fmt(ay)} {fmt(ex)} {fmt(ey)}"
    return path, (ex, ey), arc_length(p1, (ex, ey), bend) * cut + 1


# ------------------------------------------------------------------ output

def build(animated=True):
    out = []
    add = out.append

    add('<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-labelledby="hero-map-title">')
    add('\t<title id="hero-map-title">Night map of encrypted DNS traffic '
        'crossing the Asia-Pacific, with blocked queries dropped at the '
        'resolver</title>')

    # ---- defs
    add('\t<defs>')
    add('\t\t<linearGradient id="fade" x1="0" y1="0" x2="900" y2="0" '
        'gradientUnits="userSpaceOnUse">')
    add('\t\t\t<stop offset="0" stop-color="#000" stop-opacity="0"/>')
    add('\t\t\t<stop offset="0.30" stop-color="#fff" stop-opacity="0.85"/>')
    add('\t\t\t<stop offset="0.55" stop-color="#fff" stop-opacity="1"/>')
    add('\t\t\t<stop offset="0.97" stop-color="#fff" stop-opacity="1"/>')
    add('\t\t\t<stop offset="1" stop-color="#000" stop-opacity="0"/>')
    add('\t\t</linearGradient>')
    add('\t\t<mask id="edge">')
    add(f'\t\t\t<rect width="{W}" height="{H}" fill="url(#fade)"/>')
    add('\t\t</mask>')

    hx, hy = px(*HUB)
    add(f'\t\t<radialGradient id="atmos" cx="{fmt(hx)}" cy="{fmt(hy)}" '
        'r="420" gradientUnits="userSpaceOnUse">')
    add('\t\t\t<stop offset="0" stop-color="#ff7a2f" stop-opacity="0.16"/>')
    add('\t\t\t<stop offset="0.45" stop-color="#1d4a6b" stop-opacity="0.12"/>')
    add('\t\t\t<stop offset="1" stop-color="#0b0e13" stop-opacity="0"/>')
    add('\t\t</radialGradient>')

    add('\t\t<style>')
    add('\t\t\t.grid{stroke:#2a3a4a;stroke-width:.6;fill:none;opacity:.35}')
    add('\t\t\t.land{fill:#152532;fill-opacity:.85;stroke:#2f4d64;'
        'stroke-width:.7;stroke-opacity:.55}')
    add('\t\t\t.d0{fill:#82a6bf;opacity:.95}')
    add('\t\t\t.d1{fill:#5b7a92;opacity:.85}')
    add('\t\t\t.d2{fill:#42607a;opacity:.75}')
    add('\t\t\t.base{fill:none;stroke:#3b6a8c;stroke-width:.9;opacity:.30}')
    add('\t\t\t.halo{fill:none;stroke:#ff7a2f;stroke-width:5;opacity:.16;'
        'stroke-linecap:round}')
    add('\t\t\t.beam{fill:none;stroke:#ffb672;stroke-width:1.7;opacity:.95;'
        'stroke-linecap:round}')
    add('\t\t\t.bad{fill:none;stroke:#ff3b30;stroke-width:1.6;'
        'stroke-linecap:round;stroke-dasharray:5 4}')
    add('\t\t\t.badhalo{fill:none;stroke:#ff3b30;stroke-width:5;opacity:.14;'
        'stroke-linecap:round}')
    add('\t\t\t.hud{stroke:#ff9552;fill:none;stroke-width:1.2}')
    add('\t\t\t.hudline{stroke:#ff9552;stroke-width:.8;opacity:.7;'
        'stroke-dasharray:3 3}')
    add('\t\t\ttext{font-family:"JetBrains Mono",Consolas,"DejaVu Sans Mono",'
        'monospace}')
    add('\t\t\t.asn{fill:#ffb672;font-size:15px;letter-spacing:1.5px}')
    add('\t\t\t.org{fill:#8fa4b6;font-size:9.5px;letter-spacing:2px}')
    add('\t\t\t.tag{fill:#ff3b30;font-size:9.5px;letter-spacing:2px}')
    add('\t\t</style>')
    add('\t</defs>')

    add('\t<g mask="url(#edge)">')

    # ---- atmosphere
    add(f'\t\t<rect width="{W}" height="{H}" fill="url(#atmos)"/>')

    # ---- graticule
    add('\t\t<g class="grid">')
    lon = -10.0
    while lon <= LON1:
        x, _ = px(lon if lon <= 180 else lon - 360, 0)
        add(f'\t\t\t<path d="M{fmt(x)} {fmt(MAP_TOP)} V{fmt(MAP_TOP + MAP_H)}"/>')
        lon += 30.0
    for lat in (60, 40, 20, 0, -20, -40):
        _, y = px(0, lat)
        add(f'\t\t\t<path d="M0 {fmt(y)} H{W}"/>')
    add('\t\t</g>')

    # ---- landmass, outline first then the dot field on top
    add('\t\t<g class="land">')
    for poly in LAND:
        add(f'\t\t\t<path d="{land_path(poly)}"/>')
    add('\t\t</g>')

    dots = land_dots()
    for bucket in (0, 1, 2):
        chunk = [d for d in dots if d[2] == bucket]
        if not chunk:
            continue
        add(f'\t\t<g class="d{bucket}">')
        r = 1.35 if bucket == 0 else (1.2 if bucket == 1 else 1.05)
        line = []
        for x, y, _ in chunk:
            line.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{r}"/>')
            if len(line) == 8:
                add("\t\t\t" + "".join(line))
                line = []
        if line:
            add("\t\t\t" + "".join(line))
        add('\t\t</g>')
    print(f"  {len(dots)} land dots")

    # ---- quiet base arcs
    hub = px(*HUB)
    add('\t\t<g class="base">')
    for name, _, _ in ARCS:
        add(f'\t\t\t<path d="{arc_path(hub, px(*CITIES[name]))}"/>')
    for a, b, _, _ in CROSS:
        add(f'\t\t\t<path d="{arc_path(px(*CITIES[a]), px(*CITIES[b]), 0.30)}"/>')
    add('\t\t</g>')

    # ---- traffic
    add('\t\t<!-- Orange traffic. One slow pass, then it settles into a '
        'much faster loop. -->')
    runs = [(hub, px(*CITIES[n]), 0.24, d, s) for n, d, s in ARCS]
    runs += [(px(*CITIES[a]), px(*CITIES[b]), 0.30, d, s) for a, b, d, s in CROSS]

    for i, (p1, p2, bend, slow, delay) in enumerate(runs):
        d = arc_path(p1, p2, bend)
        length = arc_length(p1, p2, bend)
        dash = 30
        fast = round(slow * 0.34, 2)
        add(f'\t\t<g>')
        for cls in ("halo", "beam"):
            add(f'\t\t\t<path class="{cls}" d="{d}" '
                f'stroke-dasharray="{dash} {fmt(length)}" '
                f'stroke-dashoffset="{fmt(length + dash)}">')
            if animated:
                tag = f'{cls[0]}{i}'
                add(f'\t\t\t\t<animate id="{tag}" '
                    f'attributeName="stroke-dashoffset" '
                    f'from="{fmt(length + dash)}" to="0" dur="{slow}s" '
                    f'begin="{delay}s" fill="freeze"/>')
                add(f'\t\t\t\t<animate attributeName="stroke-dashoffset" '
                    f'from="{fmt(length + dash)}" to="0" dur="{fast}s" '
                    f'begin="{tag}.end" repeatCount="indefinite"/>')
            add('\t\t\t</path>')
        add('\t\t</g>')

    # ---- the resolver itself
    add('\t\t<g>')
    add(f'\t\t\t<circle cx="{fmt(hub[0])}" cy="{fmt(hub[1])}" r="4.5" '
        'fill="#ffb672"/>')
    for i, delay in enumerate((0, 1.6, 3.2)):
        add(f'\t\t\t<circle cx="{fmt(hub[0])}" cy="{fmt(hub[1])}" r="8" '
            'fill="none" stroke="#ff7a2f" stroke-width="1.2" opacity="0">')
        if animated:
            add(f'\t\t\t\t<animate attributeName="r" values="8;46" dur="4.8s" '
                f'begin="{delay}s" repeatCount="indefinite"/>')
            add(f'\t\t\t\t<animate attributeName="opacity" '
                f'values="0;.55;0" dur="4.8s" '
                f'begin="{delay}s" repeatCount="indefinite"/>')
        add('\t\t\t</circle>')
    add('\t\t</g>')

    # ---- threats
    add('\t\t<!-- Red traffic never reaches the resolver. It dies on the '
        'shield ring. -->')
    for i, (src, verdict, offset) in enumerate(THREATS):
        p1 = px(*CITIES[src])
        d, end, length = trim(p1, hub, 0.26, 40)
        ex, ey = end
        show = 3.4 / THREAT_CYCLE          # how much of the cycle it is on screen
        k = [0, 0.012, show * 0.55, show * 0.62, show * 0.72, 1]
        keys = ";".join(f"{v:.4f}" for v in k)

        add('\t\t<g opacity="0">')
        if animated:
            add(f'\t\t\t<animate attributeName="opacity" '
                f'values="0;1;1;1;0;0" keyTimes="{keys}" '
                f'dur="{THREAT_CYCLE}s" begin="{offset}s" '
                'repeatCount="indefinite"/>')
        else:
            add('\t\t\t<set attributeName="opacity" to="1"/>')

        for cls in ("badhalo", "bad"):
            add(f'\t\t\t<path class="{cls}" d="{d}" '
                f'stroke-dasharray="{fmt(length)}" '
                f'stroke-dashoffset="{fmt(length)}">')
            if animated:
                add(f'\t\t\t\t<animate attributeName="stroke-dashoffset" '
                    f'values="{fmt(length)};0;0;0;0;{fmt(length)}" '
                    f'keyTimes="{keys}" dur="{THREAT_CYCLE}s" '
                    f'begin="{offset}s" repeatCount="indefinite"/>')
            else:
                add('\t\t\t\t<set attributeName="stroke-dashoffset" to="0"/>')
            add('\t\t\t</path>')

        # kill marker
        add(f'\t\t\t<g transform="translate({fmt(ex)} {fmt(ey)})">')
        add('\t\t\t\t<g opacity="0">')
        if animated:
            kk = [0, show * 0.54, show * 0.58, show * 0.70, show * 0.78, 1]
            kkeys = ";".join(f"{v:.4f}" for v in kk)
            add(f'\t\t\t\t\t<animate attributeName="opacity" '
                f'values="0;0;1;1;0;0" keyTimes="{kkeys}" '
                f'dur="{THREAT_CYCLE}s" begin="{offset}s" '
                'repeatCount="indefinite"/>')
        else:
            add('\t\t\t\t\t<set attributeName="opacity" to="1"/>')
        add('\t\t\t\t\t<path d="M-6 -6 L6 6 M6 -6 L-6 6" stroke="#ff3b30" '
            'stroke-width="2.2" stroke-linecap="round"/>')
        add('\t\t\t\t\t<circle r="11" fill="none" stroke="#ff3b30" '
            'stroke-width="1" opacity=".7"/>')
        anchor = "end" if ex > W * 0.62 else "start"
        tx = -16 if anchor == "end" else 16
        add(f'\t\t\t\t\t<text class="tag" x="{tx}" y="4" '
            f'text-anchor="{anchor}">{verdict} DROPPED</text>')
        add('\t\t\t\t</g>')
        add('\t\t\t</g>')
        add('\t\t</g>')

    # ---- HUD
    add('\t\t<!-- Sci-fi HUD. One autonomous system at a time, on a loop. -->')
    total = round(CYCLE * len(TARGETS), 2)
    for i, (asn, org, cc, city) in enumerate(TARGETS):
        tx, ty = px(*CITIES[city])
        begin = round(i * CYCLE, 2)
        right = tx < W * 0.60
        lx = tx + (34 if right else -34)
        anchor = "start" if right else "end"
        # keyTimes across the whole loop: visible for one slot only
        slot = CYCLE / total
        k = [0, slot * 0.10, slot * 0.22, slot * 0.86, slot * 0.97, 1]
        keys = ";".join(f"{v:.4f}" for v in k)

        add('\t\t<g opacity="0">')
        if animated:
            add(f'\t\t\t<animate attributeName="opacity" '
                f'values="0;.35;1;1;0;0" keyTimes="{keys}" dur="{total}s" '
                f'begin="{begin}s" repeatCount="indefinite"/>')
        elif i == 0:
            add('\t\t\t<set attributeName="opacity" to="1"/>')

        # brackets
        add(f'\t\t\t<g class="hud" transform="translate({fmt(tx)} {fmt(ty)})">')
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            add(f'\t\t\t\t<path d="M{13 * sx} {19 * sy} L{19 * sx} {19 * sy} '
                f'L{19 * sx} {13 * sy}"/>')
        add('\t\t\t\t<circle r="3.2" fill="#ff9552" stroke="none"/>')
        add('\t\t\t\t<circle r="9" opacity=".45"/>')
        if animated:
            add('\t\t\t\t<animateTransform attributeName="transform" '
                'type="scale" additive="sum" values="1.6;1" dur=".45s" '
                f'begin="{begin}s" repeatCount="indefinite" '
                f'fill="freeze"/>')
        add('\t\t\t</g>')

        # leader and label
        add(f'\t\t\t<path class="hudline" d="M{fmt(tx + (20 if right else -20))} '
            f'{fmt(ty)} H{fmt(lx)}"/>')
        add(f'\t\t\t<text class="asn" x="{fmt(lx + (6 if right else -6))}" '
            f'y="{fmt(ty - 2)}" text-anchor="{anchor}">{asn}</text>')
        add(f'\t\t\t<text class="org" x="{fmt(lx + (6 if right else -6))}" '
            f'y="{fmt(ty + 12)}" text-anchor="{anchor}">{org} &#183; {cc}</text>')
        add('\t\t</g>')

    # ---- frame chrome, which also stops the Pacific looking like a hole
    top, bottom = MAP_TOP - 14, MAP_TOP + MAP_H + 14
    add('\t\t<g stroke="#3f5d75" stroke-width="1" fill="none" opacity=".5">')
    for cx_, cy_, sx, sy in ((330, top, 1, 1), (884, top, -1, 1),
                             (330, bottom, 1, -1), (884, bottom, -1, -1)):
        add(f'\t\t\t<path d="M{cx_} {fmt(cy_ + 16 * sy)} V{fmt(cy_)} '
            f'H{cx_ + 22 * sx}"/>')
    add('\t\t</g>')

    add('\t\t<g stroke="#3f5d75" stroke-width="1" opacity=".35">')
    for i in range(14):
        x = 360 + i * 38
        h = 7 if i % 4 else 12
        add(f'\t\t\t<path d="M{x} {fmt(top)} V{fmt(top + h)}"/>')
    add('\t\t</g>')

    add('\t\t<g opacity=".7">')
    add('\t\t\t<text class="org" x="884" y="{}" fill="#6d8296" '
        'text-anchor="end">ELPIS &#47;&#47; GLOBAL TRACE</text>'
        .format(fmt(top - 6)))
    add('\t\t\t<text class="org" x="601" y="{}" fill="#6d8296">'
        'TRACE ACTIVE &#183; ASN LOCK &#183; ENCRYPTED</text>'
        .format(fmt(bottom + 16)))
    add(f'\t\t\t<circle cx="591" cy="{fmt(bottom + 12)}" r="3" fill="#ff3b30">')
    if animated:
        add('\t\t\t\t<animate attributeName="opacity" values="1;.15;1" '
            'dur="1.4s" repeatCount="indefinite"/>')
    add('\t\t\t</circle>')
    add('\t\t</g>')

    # ---- scan sweep
    if animated:
        add('\t\t<g opacity=".5">')
        add('\t\t\t<path d="M0 {} V{}" stroke="#7fd4ff" stroke-width="1.4" '
            'opacity=".22">'.format(fmt(top), fmt(bottom)))
        add('\t\t\t\t<animateTransform attributeName="transform" '
            'type="translate" values="300,0;900,0" dur="7s" '
            'repeatCount="indefinite"/>')
        add('\t\t\t\t<animate attributeName="opacity" '
            'values="0;.22;.22;0" keyTimes="0;.08;.9;1" dur="7s" '
            'repeatCount="indefinite"/>')
        add('\t\t\t</path>')
        add('\t\t</g>')

    add('\t</g>')
    add('</svg>')
    return "\n".join(out) + "\n"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, animated in (("hero-map.svg", True), ("hero-map-static.svg", False)):
        path = os.path.join(root, "img", name)
        svg = build(animated)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(svg)
        print(f"  wrote img/{name}  ({len(svg) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
