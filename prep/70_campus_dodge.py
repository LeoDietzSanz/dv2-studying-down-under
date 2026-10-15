"""Map 4 circles: keep campus circles from piling on top of each other, for
the whole of Australia and for each state the reader can zoom to.

Reads   data/he_institution_geo_2024.csv
Writes  data/campus_dodge_2024.csv   one row per provider:
        dlon_all/dlat_all/mv_all   position (and px moved) in the national view
        dlon_st/dlat_st/mv_st      the same when zoomed to its own state

Priorities, in order: easy to read, no overlapping circles, then positional
accuracy. Every circle that would overlap another is moved just far enough
to clear it, the smaller circle doing most of the moving, and is pulled
back towards its campus as far as it can go. The same rule applies in every
view, so Sydney, Melbourne and Perth all behave alike. Where a circle has
moved more than a few pixels the chart draws a hairline back to its campus.

Positions are worked out in the chart's own projection and framing, for a
map 640 px wide (aspect 0.86). Circle sizes
in the chart scale with the map's width, and so does the map, so the nudges
stay right at other widths too.

The view frames (VIEWS) must match BOXES in js/boards.js and the initial
"box" value in charts/11-australia.vl.json.

Run:  python prep/70_campus_dodge.py      (also run by prep/build.py)
"""
from pathlib import Path
import math
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
W, H = 640, 550.4               # map size the chart's sizes are scaled to, px (aspect 0.86)
SIZE_MAX, DOMAIN_MAX = 560, 45000   # circle area range, px^2, and its domain (see the spec)
ZOOM_SIZE = 1.8                 # in a state view circles are drawn 1.8x the area (the legend follows)

PAD = 1.0                       # px between circles

# lon_min, lat_max, lon_max, lat_min  (same numbers as the spec's fit expression)
VIEWS = {
    "ALL": (112.5, -9.5, 155.0, -44.0),
    "NSW": (140.8, -28.0, 155.0, -37.6),
    "VIC": (140.8, -33.9, 150.2, -39.3),
    "QLD": (137.8, -10.5, 153.8, -29.3),
    "WA":  (112.8, -13.5, 129.2, -35.3),
    "SA":  (128.8, -25.8, 141.2, -38.2),
    "TAS": (143.6, -39.4, 148.6, -43.8),
    "NT":  (128.8, -10.8, 138.2, -26.2),
    "ACT": (148.70, -35.05, 149.45, -36.00),
}


# ---- the chart's projection: d3 conicEqualArea, parallels 18S/36S, rotate -134
_SY0 = math.sin(math.radians(-18))
_N = (_SY0 + math.sin(math.radians(-36))) / 2
_C = 1 + _SY0 * (2 * _N - _SY0)
_R0 = math.sqrt(_C) / _N


def proj(lon, lat):
    lam, phi = math.radians(lon - 134), math.radians(lat)
    r = math.sqrt(_C - 2 * _N * math.sin(phi)) / _N
    return r * math.sin(lam * _N), -(_R0 - r * math.cos(lam * _N))      # y down, like the screen


def unproj(x, y):
    y = -y
    r0y = _R0 - y
    l = math.atan2(x, abs(r0y)) * math.copysign(1, r0y)
    if r0y * _N <= 0:
        l -= math.pi * math.copysign(1, x) * math.copysign(1, r0y)
    phi = math.asin(max(-1, min(1, (_C - (x * x + r0y * r0y) * _N * _N) / (2 * _N))))
    return math.degrees(l / _N) + 134, math.degrees(phi)


def frame(view):
    """Pixel scale and offset the chart's 'fit' gives this view (8 points of its box)."""
    lon0, lat1, lon1, lat0 = VIEWS[view]
    mx, my = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    pts = [proj(a, b) for a, b in [(lon0, lat1), (mx, lat1), (lon1, lat1), (lon1, my),
                                   (lon1, lat0), (mx, lat0), (lon0, lat0), (lon0, my)]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    k = min(W / (max(xs) - min(xs)), H / (max(ys) - min(ys)))
    return k, min(xs), min(ys)


def dodge(df, view, pad):
    k, x0, y0 = frame(view)
    xy = [proj(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]
    x = [(a - x0) * k for a, _ in xy]
    y = [(b - y0) * k for _, b in xy]
    ax, ay = x[:], y[:]
    size_max = SIZE_MAX * (1 if view == "ALL" else ZOOM_SIZE)
    r = [math.sqrt(size_max * o / DOMAIN_MAX / math.pi) for o in df["overseas"]]
    n = len(x)
    for it in range(900):
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
                    # the smaller circle does most of the moving, so big
                    # providers stay closest to their campus
                    wi = r[j] ** 2 / (r[i] ** 2 + r[j] ** 2 + 1e-9)
                    wj = 1 - wi
                    x[i] -= ux * push * 2 * wi
                    y[i] -= uy * push * 2 * wi
                    x[j] += ux * push * 2 * wj
                    y[j] += uy * push * 2 * wj
                    moved = True
        if it < 600:                                  # pull home, then a final settle with no pull
            for i in range(n):
                x[i] += (ax[i] - x[i]) * 0.03
                y[i] += (ay[i] - y[i]) * 0.03
        elif not moved:
            break
    out = df.copy()
    back = [unproj(xi / k + x0, yi / k + y0) for xi, yi in zip(x, y)]
    out["dlon"] = [round(a, 4) for a, _ in back]
    out["dlat"] = [round(b, 4) for _, b in back]
    out["moved"] = [round(math.hypot(x[i] - ax[i], y[i] - ay[i]), 1) for i in range(n)]
    out["gap"] = min((math.hypot(x[i] - x[j], y[i] - y[j]) - r[i] - r[j]
                      for i in range(n) for j in range(i + 1, n) if r[i] > 0 and r[j] > 0), default=0)
    return out


def main() -> None:
    inst = pd.read_csv(DATA / "he_institution_geo_2024.csv").dropna(subset=["lat", "lon"])
    out = inst.copy()
    allv = dodge(inst, "ALL", PAD)
    out["dlon_all"], out["dlat_all"], out["mv_all"] = allv["dlon"].values, allv["dlat"].values, allv["moved"].values
    out["dlon_st"], out["dlat_st"], out["mv_st"] = out["lon"], out["lat"], 0.0
    worst = {"ALL": allv["gap"].iloc[0]}
    for view in VIEWS:
        if view == "ALL":
            continue
        mask = out["state"] == view
        if mask.any():
            res = dodge(inst[mask], view, PAD)
            out.loc[mask, "dlon_st"] = res["dlon"].values
            out.loc[mask, "dlat_st"] = res["dlat"].values
            out.loc[mask, "mv_st"] = res["moved"].values
            worst[view] = res["gap"].iloc[0]
    ok = all(g >= -0.5 for g in worst.values())
    for v, g in worst.items():
        print(f"  [{' OK ' if g >= -0.5 else 'FAIL'}] {v:<3} closest gap between circles {g:.1f}px")
    out.to_csv(DATA / "campus_dodge_2024.csv", index=False)
    print(f"  [ OK ] wrote data/campus_dodge_2024.csv; largest nudge {out['mv_all'].max():.0f}px nationally, "
          f"{out['mv_st'].max():.0f}px in a state view")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
