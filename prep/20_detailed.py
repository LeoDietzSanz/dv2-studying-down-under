"""Stage 1, script 20: Pivot_Detailed_Latest_web2025.xlsx -> data/.

Run from the project root:   python prep/20_detailed.py

This workbook adds field of study and world region, which the basic one
doesn't have. It only covers 2019-2025 and only Oct/Nov/Dec, so we use the
December 2025 snapshot throughout.

Outputs
-------
  field_by_sector_2025.csv   field x sector, with Marimekko rectangle edges  -> chart 7
  country_field_2025.csv     top-10 countries x field, share within country  -> chart 9
  nationality_region.csv     nationality -> region and 6-colour region group -> charts 4, 10
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivotcache import read_pivot_cache  # noqa: E402
from labels import (ELICOS_GROUP, FIELD_GROUP, FIELD_ORDER, REGION_GROUP,  # noqa: E402
                    SCHOOL_GROUP, SECTOR_ORDER)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "Pivot_Detailed_Latest_web2025.xlsx"
OUT = ROOT / "data"
YEAR = 2025
TOP_N_COUNTRIES = 10
ENROL = "DATA_YTD_Enrolments"


def save(df: pd.DataFrame, name: str) -> None:
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  wrote {name:<26} {len(df):>5,} rows  {path.stat().st_size / 1024:>6.1f} KB")


def field_group(row) -> str:
    """Display field for one record. Sector overrides the official field
    for English-language and school enrolments (see labels.py)."""
    if row["Sector"] == "ELICOS":
        return ELICOS_GROUP
    if row["Sector"] == "Schools":
        return SCHOOL_GROUP
    return FIELD_GROUP[row["Broad_Field_Of_Education"]]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    print("Reading pivot cache")
    df = read_pivot_cache(RAW)

    dec = df[(df["Year"] == YEAR) & (df["Month"] == "Dec")].copy()
    for col in ("Sector", "Broad_Field_Of_Education", "Nationality", "Region"):
        dec[col] = dec[col].astype(str)

    # Map fields once per distinct (sector, field) pair rather than per row.
    pairs = dec[["Sector", "Broad_Field_Of_Education"]].drop_duplicates()
    pairs["field"] = pairs.apply(field_group, axis=1)
    dec = dec.merge(pairs, on=["Sector", "Broad_Field_Of_Education"], how="left")

    unmapped = dec["field"].isna().sum()
    if unmapped:
        raise SystemExit(f"{unmapped} records have a field not listed in labels.FIELD_GROUP")

    print("\nWriting CSVs")

    # ---- chart 7: Marimekko -------------------------------------------------
    # Column width = the field's share of all enrolments; within a column,
    # height = each sector's share of that field. Vega-Lite can compute
    # this, but the transforms are hard to read, so the rectangle edges
    # (x0, x1, y0, y1, all between 0 and 1) are calculated here instead.
    fs = (dec.groupby(["field", "Sector"])[ENROL].sum().reset_index()
             .rename(columns={"Sector": "sector", ENROL: "enrolments"}))
    fs = fs[fs["enrolments"] > 0]
    fs["enrolments"] = fs["enrolments"].astype(int)

    field_tot = fs.groupby("field")["enrolments"].sum().reindex(FIELD_ORDER).dropna()
    grand = field_tot.sum()
    x1 = (field_tot / grand).cumsum()
    x0 = x1 - field_tot / grand
    fs["field_total"] = fs["field"].map(field_tot).astype(int)
    fs["field_share"] = fs["field_total"] / grand
    fs["x0"], fs["x1"] = fs["field"].map(x0), fs["field"].map(x1)

    fs["sector_order"] = fs["sector"].map({s: i for i, s in enumerate(SECTOR_ORDER)})
    fs["field_order"] = fs["field"].map({f: i for i, f in enumerate(FIELD_ORDER)})
    fs = fs.sort_values(["field_order", "sector_order"]).reset_index(drop=True)
    fs["sector_share"] = fs["enrolments"] / fs["field_total"]
    fs["y1"] = fs.groupby("field")["sector_share"].cumsum()
    fs["y0"] = fs["y1"] - fs["sector_share"]
    cols = ["field", "field_order", "sector", "sector_order", "enrolments", "field_total",
            "field_share", "sector_share", "x0", "x1", "y0", "y1"]
    save(fs[cols].round(5), "field_by_sector_2025.csv")

    # ---- chart 9: country x field, share within country --------------------
    by_country = dec.groupby("Nationality")[ENROL].sum().sort_values(ascending=False)
    top = by_country.head(TOP_N_COUNTRIES).index.tolist()
    cf = (dec[dec["Nationality"].isin(top)]
             .groupby(["Nationality", "field"])[ENROL].sum()
             .unstack(fill_value=0).reindex(columns=FIELD_ORDER, fill_value=0)
             .stack().reset_index(name="enrolments")
             .rename(columns={"Nationality": "nationality"}))
    cf["enrolments"] = cf["enrolments"].astype(int)
    cf["country_total"] = cf["nationality"].map(by_country).astype(int)
    # Normalise within each country. Without this the heatmap would just show
    # that China and India are big; with it, rows are comparable.
    cf["share"] = (cf["enrolments"] / cf["country_total"]).round(5)
    cf["country_rank"] = cf["nationality"].map({c: i + 1 for i, c in enumerate(top)})
    cf["field_order"] = cf["field"].map({f: i for i, f in enumerate(FIELD_ORDER)})
    save(cf.sort_values(["country_rank", "field_order"]), "country_field_2025.csv")

    # ---- charts 4 and 10: nationality -> region -----------------------------
    # Built from all years in this workbook, so countries absent in 2025 still
    # get a region.
    allrec = df[["Nationality", "Region"]].astype(str).drop_duplicates()
    allrec = allrec[allrec["Region"] != "nan"]
    reg = (allrec.groupby("Nationality")["Region"].agg(lambda s: s.mode().iat[0])
                 .reset_index().rename(columns={"Nationality": "nationality", "Region": "region"}))
    reg["region_group"] = reg["region"].map(REGION_GROUP)
    if reg["region_group"].isna().any():
        missing = reg.loc[reg["region_group"].isna(), "region"].unique()
        raise SystemExit(f"Regions not in labels.REGION_GROUP: {missing}")
    save(reg.sort_values("nationality"), "nationality_region.csv")

    validate(dec, fs, cf, top)


def validate(dec, fs, cf, top) -> None:
    print("\nValidation")
    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        failures += not ok
        print(f"  [{' OK ' if ok else 'FAIL'}] {label}{(': ' + detail) if detail else ''}")

    total = int(dec[ENROL].sum())
    # Must equal the basic workbook's Dec 2025 total, or the two sources disagree.
    check("Dec 2025 total matches basic workbook", total == 1_058_040, f"{total:,}")
    check("Marimekko columns cover 0 to 1", abs(fs["x1"].max() - 1) < 1e-6)
    col_tops = fs.groupby("field")["y1"].max()
    check("every Marimekko column stacks to 1", bool(((col_tops - 1).abs() < 1e-6).all()))
    shares = cf.groupby("nationality")["share"].sum()
    check("each country's field shares sum to 1", bool(((shares - 1).abs() < 1e-3).all()))
    check("top countries", True, ", ".join(top))

    print()
    print("All checks passed." if failures == 0 else f"{failures} check(s) failed.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
