"""Stage 1, script 40: the "study or business?" thread (Act 6) -> data/.

Run from the project root:   python prep/40_business.py

Two questions the other scripts don't ask:

1. Who teaches international students: public institutions or private
   (non-government) providers?  From Pivot_Basic_All_web.xlsx, whose
   ProviderType field splits every enrolment into Government and
   Non Government, December year-to-date, 2005-2025.

2. Which university degrees have become export products?  From the
   perturbed higher-education pivot (2020-2024): overseas students' share of
   enrolments at each course level. Postgraduate coursework (mostly
   master's degrees) is the one to watch.

Outputs
-------
  provider_type_by_year.csv   year x sector (+ "All sectors"): private share   -> chart 16
  he_course_level.csv         year x course level: overseas share            -> chart 17
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivotcache import read_pivot_cache  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW_BASIC = ROOT / "raw" / "Pivot_Basic_All_web.xlsx"
RAW_HE = ROOT / "raw" / "Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx"
OUT = ROOT / "data"

LEVELS = {                                  # HE pivot label -> reader label
    "Postgraduate other": "Postgraduate coursework",
    "Postgraduate research": "Postgraduate research",
    "Bachelor": "Bachelor degree",
    "Undergraduate other": "Diplomas and associate degrees",
}


def save(df: pd.DataFrame, name: str) -> None:
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  wrote {name:<26} {len(df):>5,} rows  {path.stat().st_size / 1024:>6.1f} KB")


def main() -> None:
    # ---- 1. private providers' share ------------------------------------------
    b = read_pivot_cache(RAW_BASIC)
    b = b[b["Month"] == "Dec"]
    b = b.assign(Sector=b["Sector"].astype(str), ProviderType=b["ProviderType"].astype(str))
    t = (b.groupby(["Year", "Sector", "ProviderType"], observed=True)["DATA_YTD_Enrolments"].sum()
           .unstack(fill_value=0))
    a = b.groupby(["Year", "ProviderType"], observed=True)["DATA_YTD_Enrolments"].sum().unstack(fill_value=0)
    a.index = pd.MultiIndex.from_product([a.index, ["All sectors"]], names=["Year", "Sector"])
    t = pd.concat([t, a])
    t["total"] = t["Government"] + t["Non Government"]
    t["private_share"] = (t["Non Government"] / t["total"]).round(4)
    prov = (t.reset_index()
              .rename(columns={"Year": "year", "Sector": "sector", "Non Government": "private",
                               "Government": "public"})
              [["year", "sector", "public", "private", "total", "private_share"]]
              .sort_values(["sector", "year"]))
    prov["year"] = prov["year"].astype(int)
    for c in ["public", "private", "total"]:
        prov[c] = prov[c].astype(int)

    # ---- 2. overseas share by course level --------------------------------------
    h = read_pivot_cache(RAW_HE)
    h = h.assign(level=h["Detailed_Course_Level"].astype(str).map(LEVELS),
                 who=h["Citizenship"].astype(str))
    h = h.dropna(subset=["level"])
    lv = (h.groupby(["Year", "level", "who"], observed=True)["Enrolment Count"].sum()
            .unstack(fill_value=0).reset_index())
    lv["total"] = lv["Domestic"] + lv["Overseas"]
    lv["overseas_share"] = (lv["Overseas"] / lv["total"]).round(4)
    lv = lv.rename(columns={"Year": "year", "Domestic": "domestic", "Overseas": "overseas"})
    lv["year"] = lv["year"].astype(int)
    for c in ["domestic", "overseas", "total"]:
        lv[c] = lv[c].astype(int)

    print("\nWriting CSVs")
    save(prov, "provider_type_by_year.csv")
    save(lv, "he_course_level.csv")

    # ---- validation ------------------------------------------------------------
    print("\nValidation")
    ok = True
    tot25 = int(prov.query("year == 2025 and sector == 'All sectors'")["total"].iloc[0])
    good = tot25 == 1058040
    ok &= good
    print(f"  [{' OK ' if good else 'FAIL'}] 2025 total matches the page: {tot25:,}")
    p05 = prov.query("year == 2005 and sector == 'All sectors'")["private_share"].iloc[0]
    p24 = prov.query("year == 2024 and sector == 'All sectors'")["private_share"].iloc[0]
    print(f"  [ OK ] private providers' share, all sectors: {p05:.1%} (2005) -> {p24:.1%} (2024)")
    pg = lv.query("year == 2024 and level == 'Postgraduate coursework'")["overseas_share"].iloc[0]
    print(f"  [ OK ] overseas share of postgraduate coursework, 2024: {pg:.1%}")
    if not ok:
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
