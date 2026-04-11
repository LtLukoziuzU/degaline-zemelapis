#!/usr/bin/env python3
"""
check_pins.py — Detect likely misplaced gas station pins.

Method: each station declares a municipality (savivaldybė). We compare
its lat/lng against that municipality's known centroid. Stations further
than the threshold distance are flagged as suspicious.

Output: check_pins_report.txt  (human-readable, sorted worst-first)

DO NOT edit any data based on this output without manual review.
"""

import json
import math
import unicodedata

# ---------------------------------------------------------------------------
# Municipality centroids (lat, lng) and max-allowed radius in km.
# Centroids are approximate geographic centres, not administrative ones.
# Radii are generous to minimise false positives; only obvious outliers flag.
# ---------------------------------------------------------------------------

MUNI_DATA = {
    # key: normalised name (lowercase, no accents, collapse whitespace)
    # value: (lat, lng, radius_km)

    # --- city municipalities (tight) ---
    "alytaus m. sav.":       (54.403,  24.049, 12),
    "kauno m. sav.":         (54.899,  23.903, 14),
    "klaipedos m. sav.":     (55.703,  21.132, 12),
    "panevezio m. sav.":     (55.733,  24.365, 12),
    "siauliu m. sav.":       (55.934,  23.314, 12),
    "siauliu m.":            (55.934,  23.314, 12),   # alt label in data
    "vilniaus m. sav.":      (54.689,  25.279, 16),

    # --- small / special municipalities ---
    "birstono sav.":         (54.618,  24.014, 22),
    "druskininku sav.":      (54.018,  23.966, 25),   # elongated NS
    "elektrenu sav.":        (54.780,  24.662, 22),
    "kalvarijos sav.":       (54.383,  23.226, 22),
    "kazlu rudos sav.":      (54.764,  23.492, 28),
    "neringos sav.":         (55.300,  21.063, 55),   # Curonian Spit, very long NS
    "pagegiu sav.":          (55.175,  22.025, 28),
    "palangos sav.":         (55.920,  21.055, 15),
    "rietavo sav.":          (55.726,  21.928, 22),
    "visagino sav.":         (55.601,  26.420, 18),

    # --- district municipalities ---
    "akmenes r. sav.":       (56.248,  22.748, 35),
    "alytaus r. sav.":       (54.270,  24.130, 38),
    "anyksciu r. sav.":      (55.527,  25.102, 40),
    "birzu r. sav.":         (56.200,  24.750, 38),
    "ignalinos r. sav.":     (55.350,  26.175, 38),
    "jonavos r. sav.":       (55.068,  24.282, 32),
    "joniskio r. sav.":      (56.240,  23.610, 35),
    "jurbarko r. sav.":      (55.075,  22.768, 42),
    "kaisiadoiru r. sav.":   (54.868,  24.428, 30),   # typo-safe fallback below
    "kaisiadoriu r. sav.":   (54.868,  24.428, 30),
    "kauno r. sav.":         (54.870,  23.830, 40),
    "kelmes r. sav.":        (55.628,  22.928, 38),
    "klaipedos r. sav.":     (55.605,  21.380, 38),
    "kretingos r. sav.":     (55.882,  21.248, 30),
    "kupiskio r. sav.":      (55.830,  24.972, 38),
    "kedainiu r. sav.":      (55.283,  23.968, 40),
    "lazdiju r. sav.":        (54.233,  23.516, 40),   # elongated
    "marijampoles sav.":     (54.569,  23.354, 32),
    "mazeikiu r. sav.":      (56.298,  22.328, 35),
    "moletu r. sav.":        (55.227,  25.416, 40),
    "pakruojo r. sav.":      (56.073,  23.868, 35),
    "panevezio r. sav.":     (55.730,  24.370, 45),
    "pasvalio r. sav.":      (56.073,  24.400, 35),
    "plunges r. sav.":       (55.920,  21.850, 35),
    "prienu r. sav.":        (54.630,  23.948, 35),
    "radviliskio r. sav.":   (55.798,  23.547, 38),
    "raseiniu r. sav.":      (55.370,  23.118, 40),
    "rokiskio r. sav.":      (55.970,  25.583, 42),
    "skuodo r. sav.":        (56.270,  21.532, 35),
    "taurages r. sav.":      (55.250,  22.282, 42),
    "telsiu r. sav.":        (55.983,  22.232, 38),
    "traku r. sav.":         (54.648,  24.935, 38),
    "ukmerges r. sav.":      (55.248,  24.770, 38),
    "utenos r. sav.":        (55.498,  25.597, 42),
    "varenos r. sav.":       (54.222,  24.568, 42),
    "vilkaviskio r. sav.":   (54.651,  23.035, 32),
    "vilniaus r. sav.":      (54.803,  25.465, 45),
    "zarasu r. sav.":        (55.732,  26.248, 40),
    "sakiu r. sav.":         (54.953,  23.082, 38),
    "salcininku r. sav.":    (54.302,  25.097, 38),
    "siauliu r. sav.":       (55.934,  23.314, 45),
    "silales r. sav.":       (55.483,  22.183, 35),
    "silutes r. sav.":       (55.352,  21.482, 40),
    "sirvintu r. sav.":      (55.047,  24.953, 35),
    "svencioniu r. sav.":    (55.130,  25.997, 42),
}


def strip_accents(s: str) -> str:
    """Normalise accented Lithuanian characters to ASCII approximations."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalise_muni(raw: str) -> str:
    lower = raw.lower().strip()
    # collapse non-breaking spaces and other whitespace variants
    lower = " ".join(lower.split())
    return strip_accents(lower)


def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def main():
    with open("data/stations.json") as f:
        data = json.load(f)
    stations = data["stations"]

    flags = []
    unknown_munis = set()

    for s in stations:
        key = normalise_muni(s["municipality"])
        if key not in MUNI_DATA:
            unknown_munis.add(s["municipality"])
            continue

        clat, clng, radius = MUNI_DATA[key]
        dist = haversine_km(s["lat"], s["lng"], clat, clng)

        if dist > radius:
            flags.append({
                "dist_km": dist,
                "radius_km": radius,
                "excess_km": dist - radius,
                "company": s["company"],
                "municipality": s["municipality"],
                "address": s["address"],
                "lat": s["lat"],
                "lng": s["lng"],
                "centroid": (clat, clng),
            })

    flags.sort(key=lambda x: x["excess_km"], reverse=True)

    report_lines = []
    report_lines.append("=" * 72)
    report_lines.append("SUSPICIOUS PIN REPORT — check_pins.py")
    report_lines.append(f"Data date: {data.get('date', 'unknown')}")
    report_lines.append(f"Total stations checked: {len(stations)}")
    report_lines.append(f"Flagged: {len(flags)}")
    report_lines.append("Sorted by how far past the allowed radius (worst first).")
    report_lines.append("DO NOT edit data without manual map verification.")
    report_lines.append("=" * 72)

    if unknown_munis:
        report_lines.append("")
        report_lines.append("UNKNOWN MUNICIPALITIES (not in centroid table — skipped):")
        for m in sorted(unknown_munis):
            report_lines.append(f"  {repr(m)}")

    report_lines.append("")

    for i, f in enumerate(flags, 1):
        clat, clng = f["centroid"]
        report_lines.append(
            f"[{i:03d}] {f['excess_km']:6.1f} km over limit  "
            f"(dist {f['dist_km']:.1f} km, limit {f['radius_km']} km)"
        )
        report_lines.append(f"       Company:      {f['company']}")
        report_lines.append(f"       Municipality: {f['municipality']}")
        report_lines.append(f"       Address:      {f['address']}")
        report_lines.append(f"       Pin:          {f['lat']:.6f}, {f['lng']:.6f}")
        report_lines.append(f"       Muni centroid:{clat:.6f}, {clng:.6f}")
        report_lines.append(
            f"       Maps link:    https://www.google.com/maps?q={f['lat']},{f['lng']}"
        )
        report_lines.append("")

    report = "\n".join(report_lines)

    with open("check_pins_report.txt", "w") as f:
        f.write(report)

    print(report)
    print(f"\nReport written to check_pins_report.txt")


if __name__ == "__main__":
    main()
