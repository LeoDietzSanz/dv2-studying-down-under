"""Map 3 geometry: draw each source country's students as one ribbon that
splits into branches, one per state capital.

Reads   data/nationality_state_2025.csv   enrolments by citizenship x state
        data/country_lookup.csv           citizenship -> ISO3, region, lon/lat
        geo/au_state_capitals.csv         state -> capital city and lon/lat
Writes  data/flow_ribbons_2025.json       GeoJSON polygons, one per trunk/branch
        data/flow_origins_2025.csv        one row per origin (map tile + board)

Why ribbons (filled polygons) and not lines:
  A line's stroke width is in screen pixels, but where it sits is in degrees,
  so a trunk drawn as a 25 px line never exactly meets five branches drawn as
  thinner lines: the branches either overlap (and the trunk looks too wide) or
  gap. Here everything, width included, is geometry. Each trunk is a polygon
  as wide as all of its students; at the split its end edge is cut into
  slices, one per capital, and each branch starts on exactly its slice and
  leaves in the trunk's direction. Branch widths therefore add up to the
  trunk at every zoom level, and branches of one origin never cross.

Geometry is built in the map's own projection (azimuthal equidistant centred
on 110 E, 2 S, as in charts/10-flow-map.vl.json), so widths are even on
screen, then converted back to longitude/latitude for Vega-Lite.

Run:  python prep/60_flow_paths.py      (also run by prep/build.py)
"""
from pathlib import Path
import json
import math
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, GEO = ROOT / "data", ROOT / "geo"

N_ORIGINS = 20             # the 20 largest source countries
FLOW_MIN = 1000            # routes smaller than this are left out (caption says so)
RAD_PER_STUDENT = 0.075 / 230000    # ribbon width: 230,000 students = 0.075 rad (~4.3 deg)
MIN_WIDTH = 0.0022         # thinnest branch, so small routes stay visible (~1 px on a laptop)
SPLIT_BEFORE = 0.36        # rad (~21 deg) before the destinations' centre, trunks split
N_TRUNK, N_BRANCH = 16, 40

LON0, LAT0 = math.radians(110), math.radians(-2)    # projection centre

# Countries outside the map frame enter at its edge, labelled with the route.
ENTRY = {
    "COL": ((166.0, -9.0), "via the Pacific"),
    "BRA": ((166.0, -19.0), "via the Pacific"),
    "USA": ((166.0, 1.0), "via the Pacific"),
    "KEN": ((72.0, -8.0), "via the Indian Ocean"),
}
# Tiles that would sit on top of each other get nudged (lon, lat).
NUDGE = {"BTN": (2.5, 2.5), "HKG": (2.5, -1.5), "SGP": (-3.0, -2.0), "TWN": (2.0, 0.0)}

CAP_CODE = {"NSW": "SYD", "VIC": "MEL", "QLD": "BNE", "WA": "PER",
            "SA": "ADL", "ACT": "CBR", "TAS": "HBA", "NT": "DRW"}
SHORT = {"Korea, Republic of (South)": "South Korea", "United States of America": "United States",
         "Hong Kong SAR": "Hong Kong"}


# ---------------------------------------------------- azimuthal equidistant
def fwd(lon, lat):
    lam, phi = math.radians(lon) - LON0, math.radians(lat)
    c = math.acos(max(-1, min(1, math.sin(LAT0) * math.sin(phi)
                              + math.cos(LAT0) * math.cos(phi) * math.cos(lam))))
    k = 1 if c == 0 else c / math.sin(c)
    return (k * math.cos(phi) * math.sin(lam),
            k * (math.cos(LAT0) * math.sin(phi) - math.sin(LAT0) * math.cos(phi) * math.cos(lam)))


def inv(x, y):
    c = math.hypot(x, y)
    if c == 0:
        return math.degrees(LON0), math.degrees(LAT0)
    phi = math.asin(math.cos(c) * math.sin(LAT0) + y * math.sin(c) * math.cos(LAT0) / c)
    lam = LON0 + math.atan2(x * math.sin(c), c * math.cos(LAT0) * math.cos(c) - y * math.sin(LAT0) * math.sin(c))
    return round(math.degrees(lam), 4), round(math.degrees(phi), 4)


# --------------------------------------------------------------- geometry
def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def ribbon(centre, width):
    """Polygon around a centre line, `width` wide, in projected units."""
    left, right = [], []
    for i, p in enumerate(centre):
        a = centre[max(i - 1, 0)]
        b = centre[min(i + 1, len(centre) - 1)]
        tx, ty = unit((b[0] - a[0], b[1] - a[1]))
        nx, ny = -ty, tx
        left.append((p[0] + nx * width / 2, p[1] + ny * width / 2))
        right.append((p[0] - nx * width / 2, p[1] - ny * width / 2))
    ring = [inv(*p) for p in left + right[::-1]]
    ring.append(ring[0])
    # d3-geo wants exterior rings clockwise (north up); shoelace > 0 = anticlockwise
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:]))
    return ring[::-1] if area > 0 else ring


def bezier(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def group_of(raw) -> str:
    t = str(raw).lower()
    if "central" in t or "south asia" in t:
        return "South & Central Asia"
    if "east" in t:
        return "East & South-East Asia"
    if "america" in t:
        return "Americas"
    return "Rest of world"


def main() -> None:
    ns = pd.read_csv(DATA / "nationality_state_2025.csv")
    lk = pd.read_csv(DATA / "country_lookup.csv").drop_duplicates("nationality")
    caps = pd.read_csv(GEO / "au_state_capitals.csv").set_index("state")

    totals = ns.groupby("nationality")["enrolments"].sum().sort_values(ascending=False)
    top = totals.head(N_ORIGINS)
    features, origins = [], []

    for rank, (nat, all_students) in enumerate(top.items(), start=1):
        info = lk.loc[lk["nationality"] == nat].iloc[0]
        iso3 = info["iso3"]
        g = ns[(ns["nationality"] == nat) & (ns["enrolments"] >= FLOW_MIN)].copy()
        g = g[g["state"].isin(caps.index)]
        if g.empty:
            continue
        g["w"] = (g["enrolments"] * RAD_PER_STUDENT).clip(lower=MIN_WIDTH)
        g["dx"], g["dy"] = zip(*[fwd(caps.loc[s, "lon"], caps.loc[s, "lat"]) for s in g["state"]])

        (olon, olat), via = ENTRY.get(iso3, ((info["lon"], info["lat"]), ""))
        nlon, nlat = NUDGE.get(iso3, (0, 0))
        tile = (olon + nlon, olat + nlat)
        o = fwd(*tile)

        wsum = g["enrolments"].sum()
        centre = ((g["dx"] * g["enrolments"]).sum() / wsum, (g["dy"] * g["enrolments"]).sum() / wsum)
        dist = math.hypot(o[0] - centre[0], o[1] - centre[1])
        head = unit((centre[0] - o[0], centre[1] - o[1]))
        back = min(SPLIT_BEFORE, dist * 0.5)
        split = (centre[0] - head[0] * back, centre[1] - head[1] * back)
        perp = (-head[1], head[0])                      # left of travel
        trunk_w = g["w"].sum()
        shown = int(g["enrolments"].sum())
        grp = group_of(info["region_group"])
        name = SHORT.get(nat, nat)
        base = dict(iso3=iso3, country=name, grp=grp)

        trunk_line = [(o[0] + (split[0] - o[0]) * i / N_TRUNK, o[1] + (split[1] - o[1]) * i / N_TRUNK)
                      for i in range(N_TRUNK + 1)]
        features.append({"type": "Feature",
                         "properties": dict(base, part="trunk", code="", city="all capitals shown",
                                            enrolments=shown, share=round(shown / all_students, 4)),
                         "geometry": {"type": "Polygon", "coordinates": [ribbon(trunk_line, trunk_w)]}})

        # Slices of the trunk's end, left to right in the direction of travel:
        # destinations furthest to the left take the left-most slice.
        g["side"] = [head[0] * (dy - split[1]) - head[1] * (dx - split[0]) for dx, dy in zip(g["dx"], g["dy"])]
        g = g.sort_values("side", ascending=False)
        used = 0.0
        for _, r in g.iterrows():
            off = trunk_w / 2 - used - r["w"] / 2
            used += r["w"]
            start = (split[0] + perp[0] * off, split[1] + perp[1] * off)
            dest = (r["dx"], r["dy"])
            reach = math.hypot(dest[0] - start[0], dest[1] - start[1])
            ctrl = (start[0] + head[0] * reach * 0.5, start[1] + head[1] * reach * 0.5)
            line = [bezier(start, ctrl, dest, i / N_BRANCH) for i in range(N_BRANCH + 1)]
            features.append({"type": "Feature",
                             "properties": dict(base, part="branch", code=CAP_CODE[r["state"]],
                                                city=caps.loc[r["state"], "city"],
                                                enrolments=int(r["enrolments"]),
                                                share=round(r["enrolments"] / all_students, 4)),
                             "geometry": {"type": "Polygon", "coordinates": [ribbon(line, r["w"])]}})

        topr = g.sort_values("enrolments", ascending=False).iloc[0]
        origins.append(dict(rank=rank, iso3=iso3, country=name, grp=grp, lon=round(tile[0], 3),
                            lat=round(tile[1], 3), students=int(all_students),
                            top_code=CAP_CODE[topr["state"]], top_city=caps.loc[topr["state"], "city"],
                            top_share=round(topr["enrolments"] / all_students, 4),
                            top_lon=caps.loc[topr["state"], "lon"], top_lat=caps.loc[topr["state"], "lat"],
                            via=via))

    (DATA / "flow_ribbons_2025.json").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")))
    pd.DataFrame(origins).to_csv(DATA / "flow_origins_2025.csv", index=False)

    # ---- validation ----------------------------------------------------------
    ok = len(origins) == N_ORIGINS
    print(f"  [{' OK ' if ok else 'FAIL'}] {len(origins)} origins, {len(features)} ribbons")
    o = pd.DataFrame(origins).set_index("iso3")
    for iso3, share, code in [("CHN", 0.4664, "SYD"), ("IND", 0.4297, "MEL"), ("NPL", 0.6174, "SYD")]:
        good = abs(o.loc[iso3, "top_share"] - share) < 0.001 and o.loc[iso3, "top_code"] == code
        ok &= good
        print(f"  [{' OK ' if good else 'FAIL'}] {iso3}: {o.loc[iso3, 'top_share']:.1%} to {o.loc[iso3, 'top_code']}")
    print("  [ OK ] wrote data/flow_ribbons_2025.json and data/flow_origins_2025.csv")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
