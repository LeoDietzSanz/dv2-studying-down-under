"""Map 4 circles: move overlapping campus circles apart, once for the whole of
Australia and once for every state the reader can zoom to.

Reads   data/he_institution_geo_2024.csv
Writes  data/campus_dodge_2024.csv   one row per (view, provider)

In Sydney and Melbourne five to seven large circles share a few kilometres,
so on the map they sit on top of one another and can't be told apart or
clicked. For each view (ALL, NSW, VIC, ...) this script works out where each
circle would land on screen, then nudges overlapping circles apart (a simple
collision relaxation that also pulls each circle back towards its true
position). The chart draws each circle at its nudged position with a thin
leader line to a dot on the true campus location.

Screen size is estimated for a map 640 px wide and 550 px tall. Circle sizes
in the chart scale with the map's width, and so does the map, so the nudges
stay right at other widths too.

The view frames (VIEWS) must match the "fit" expression in
charts/11-australia.vl.json.

Run:  python prep/70_campus_dodge.py      (also run by prep/build.py)
"""
from pathlib import Path
import math
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
W, H = 640, 550                 # assumed map size, px
SIZE_MAX, DOMAIN_MAX = 900, 45000   # circle area range, px^2, and its domain (see the spec)
ZOOM_SIZE = 2.2                 # in a state view circles are drawn 2.2x the area (the legend follows)
PAD = 1.5                       # px between circles

# lon_min, lat_max, lon_max, lat_min  (same numbers as the spec's fit expression)
VIEWS = {
    "ALL": (112.5, -9.5, 157.5, -44.0),
    "NSW": (140.8, -28.0, 155.0, -37.6),
    "VIC": (140.8, -33.9, 150.2, -39.3),
    "QLD": (137.8, -10.5, 153.8, -29.3),
    "WA":  (112.8, -13.5, 129.2, -35.3),
    "SA":  (128.8, -25.8, 141.2, -38.2),
    "TAS": (143.6, -39.4, 148.6, -43.8),
    "NT":  (128.8, -10.8, 138.2, -26.2),
    "ACT": (148.70, -35.05, 149.45, -36.00),
}


def dodge(df, view, pad):
    lon0, lat1, lon1, lat0 = VIEWS[view]
    k = math.cos(math.radians((lat0 + lat1) / 2))
    s = min(W / ((lon1 - lon0) * k), H / (lat1 - lat0))      # px per degree
    x = [(lon - lon0) * k * s for lon in df["lon"]]
    y = [(lat1 - lat) * s for lat in df["lat"]]
    ax, ay = x[:], y[:]
    size_max = SIZE_MAX * (1 if view == "ALL" else ZOOM_SIZE)
    r = [math.sqrt(size_max * o / DOMAIN_MAX / math.pi) for o in df["overseas"]]
    n = len(x)
    for _ in range(400):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = x[j] - x[i], y[j] - y[i]
                d = math.hypot(dx, dy)
                need = r[i] + r[j] + pad
                if d < need:
                    if d < 1e-6:                      # identical points: split sideways
                        dx, dy, d = 1.0, 0.3, math.hypot(1.0, 0.3)
                    push = (need - d) / 2
                    ux, uy = dx / d, dy / d
                    # the bigger circle moves less, so the big ones stay near their campus
                    wi, wj = r[j] / (r[i] + r[j] + 1e-9), r[i] / (r[i] + r[j] + 1e-9)
                    x[i] -= ux * push * 2 * wi
                    y[i] -= uy * push * 2 * wi
                    x[j] += ux * push * 2 * wj
                    y[j] += uy * push * 2 * wj
                    moved = True
        for i in range(n):                            # gentle pull home
            x[i] += (ax[i] - x[i]) * 0.02
            y[i] += (ay[i] - y[i]) * 0.02
        if not moved:
            break
    # ---- labels (state views only) -------------------------------------
    # A provider with no close neighbour is named right beside its circle.
    # A city cluster (three or more circles within 70 px of each other) gets
    # its names stacked in a column just beside the cluster, in the order the
    # circles run from top to bottom, each joined to its circle by a leader.
    lx, ly, lalign, lead = [None] * n, [None] * n, ["left"] * n, [False] * n
    if view != "ALL":
        parent = list(range(n))
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(n):
            for j in range(i + 1, n):
                if math.hypot(x[i] - x[j], y[i] - y[j]) < 70:
                    parent[find(i)] = find(j)
        clusters = {}
        for i in range(n):
            clusters.setdefault(find(i), []).append(i)
        for members in clusters.values():
            if len(members) < 3:
                for i in members:
                    lx[i], ly[i] = x[i] + r[i] + 4, y[i]
                continue
            members.sort(key=lambda i: y[i])
            right = max(x[i] + r[i] for i in members) + 26
            left = min(x[i] - r[i] for i in members) - 26
            side_right = right + 90 < W or left - 90 < 0
            col = right if side_right else left
            step = 14
            cy = sum(y[i] for i in members) / len(members)
            top = max(8, min(H - 8 - step * (len(members) - 1), cy - step * (len(members) - 1) / 2))
            for k_, i in enumerate(members):
                lx[i], ly[i] = col, top + k_ * step
                lalign[i] = "left" if side_right else "right"
                lead[i] = True

    out = df.copy()
    out["view"] = view
    out["lab_lon"] = [None if v is None else round(lon0 + v / (k * s), 4) for v in lx]
    out["lab_lat"] = [None if v is None else round(lat1 - v / s, 4) for v in ly]
    out["lab_align"] = lalign
    out["lab_lead"] = lead
    out["dlon"] = [round(lon0 + xi / (k * s), 4) for xi in x]
    out["dlat"] = [round(lat1 - yi / s, 4) for yi in y]
    out["moved_px"] = [round(math.hypot(x[i] - ax[i], y[i] - ay[i]), 1) for i in range(n)]
    worst = min((math.hypot(x[i] - x[j], y[i] - y[j]) - r[i] - r[j]
                 for i in range(n) for j in range(i + 1, n) if r[i] > 0 and r[j] > 0), default=0)
    return out, worst


def main() -> None:
    inst = pd.read_csv(DATA / "he_institution_geo_2024.csv").dropna(subset=["lat", "lon"])
    frames, ok = [], True
    for view in VIEWS:
        sub = inst if view == "ALL" else inst[inst["state"] == view]
        res, worst = dodge(sub, view, PAD if view == "ALL" else 4.0)
        frames.append(res)
        good = worst >= -0.5
        ok &= good
        print(f"  [{' OK ' if good else 'FAIL'}] {view:<3} {len(sub):>2} providers, "
              f"closest gap {worst:.1f}px, largest nudge {res['moved_px'].max():.0f}px")
    pd.concat(frames).to_csv(DATA / "campus_dodge_2024.csv", index=False)
    print("  [ OK ] wrote data/campus_dodge_2024.csv")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
