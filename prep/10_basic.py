"""Stage 1, script 10: Pivot_Basic_All_web.xlsx -> six CSVs in data/.

Run from the project root:   python prep/10_basic.py

Reads the basic pivot cache once and writes every aggregate the page needs
from it. Ends by checking a few totals against the published figures, so you
know straight away if the extraction is wrong.

Two things about this data that every chart depends on
------------------------------------------------------
1. The values are YEAR-TO-DATE. 'DATA_YTD_Enrolments' in, say, March is the
   number of enrolments from January to March. So a full-year figure is the
   December value, never a sum across months. Summing months would count
   most students eleven or twelve times.

2. Enrolments are not students. A student enrolled in two courses (an
   English course then a degree, say) counts twice. Every caption that uses
   these numbers should say "enrolments".

Outputs
-------
  totals_by_year.csv          year, enrolments, commencements          -> chart 2
  sector_by_year.csv          year, sector, enrolments                 -> chart 3
  nationality_by_year.csv     year, nationality, enrolments, rank      -> charts 4, 5, 6
  state_by_year.csv           year, state, enrolments                  -> chart 11
  nationality_state_2025.csv  nationality, state, enrolments           -> chart 10
  monthly_commencements.csv   year, month, month_num, ytd, monthly     -> chart 13
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivotcache import read_pivot_cache  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "Pivot_Basic_All_web.xlsx"
OUT = ROOT / "data"

LATEST_YEAR = 2025
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
REAL_STATES = ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]
# 'NAT' in the State field is providers that operate nationally rather than in
# one state. It's well under 1% of enrolments. It stays in national totals
# but can't be placed on a map, so the state-level files leave it out.

ENROL, COMM = "DATA_YTD_Enrolments", "DATA_YTD_Commencements"


def save(df: pd.DataFrame, name: str) -> None:
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  wrote {name:<28} {len(df):>6,} rows  {path.stat().st_size / 1024:>7.1f} KB")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    print("Reading pivot cache")
    df = read_pivot_cache(RAW)

    # Columns arrive as Categoricals. observed=True stops groupby producing
    # empty rows for every unused category combination.
    df["State"] = df["State"].astype(str)
    dec = df[df["Month"] == "Dec"]

    print("\nWriting CSVs")

    # ---- chart 2: total enrolments per year ---------------------------------
    totals = (dec.groupby("Year", observed=True)[[ENROL, COMM]].sum()
                 .reset_index()
                 .rename(columns={"Year": "year", ENROL: "enrolments", COMM: "commencements"}))
    totals[["enrolments", "commencements"]] = totals[["enrolments", "commencements"]].astype(int)
    save(totals, "totals_by_year.csv")

    # ---- chart 3: enrolments by sector per year ------------------------------
    sector = (dec.groupby(["Year", "Sector"], observed=True)[ENROL].sum()
                 .reset_index()
                 .rename(columns={"Year": "year", "Sector": "sector", ENROL: "enrolments"}))
    sector["enrolments"] = sector["enrolments"].astype(int)
    save(sector, "sector_by_year.csv")

    # ---- charts 4, 5, 6: enrolments by nationality per year, with rank -----
    nat = (dec.groupby(["Year", "Nationality"], observed=True)[ENROL].sum()
              .reset_index()
              .rename(columns={"Year": "year", "Nationality": "nationality", ENROL: "enrolments"}))
    nat["enrolments"] = nat["enrolments"].astype(int)
    nat = nat[nat["enrolments"] > 0]
    # Rank 1 = most enrolments that year. 'min' gives tied countries the same rank.
    nat["rank"] = (nat.groupby("year")["enrolments"]
                      .rank(method="min", ascending=False).astype(int))
    nat = nat.sort_values(["year", "rank"])
    save(nat, "nationality_by_year.csv")

    # ---- chart 11: enrolments by state per year ------------------------------
    state = (dec[dec["State"].isin(REAL_STATES)]
                .groupby(["Year", "State"], observed=True)[ENROL].sum()
                .reset_index()
                .rename(columns={"Year": "year", "State": "state", ENROL: "enrolments"}))
    state["enrolments"] = state["enrolments"].astype(int)
    save(state, "state_by_year.csv")

    # ---- chart 10: origin -> state flows, latest year -------------------------
    flows = (dec[(dec["Year"] == LATEST_YEAR) & dec["State"].isin(REAL_STATES)]
                .groupby(["Nationality", "State"], observed=True)[ENROL].sum()
                .reset_index()
                .rename(columns={"Nationality": "nationality", "State": "state", ENROL: "enrolments"}))
    flows["enrolments"] = flows["enrolments"].astype(int)
    flows = flows[flows["enrolments"] > 0].sort_values("enrolments", ascending=False)
    save(flows, "nationality_state_2025.csv")

    # ---- chart 13: monthly commencements -------------------------------------
    # Commencements are cumulative within each year, so the number that
    # started in a given month is this month's YTD minus last month's YTD.
    # January has no previous month in the same year, so it's taken as-is.
    monthly = (df.groupby(["Year", "Month"], observed=True)[COMM].sum()
                 .reset_index()
                 .rename(columns={"Year": "year", "Month": "month", COMM: "ytd"}))
    monthly["month"] = monthly["month"].astype(str)
    monthly["month_num"] = monthly["month"].map({m: i + 1 for i, m in enumerate(MONTHS)})
    monthly = monthly.sort_values(["year", "month_num"]).reset_index(drop=True)
    monthly["ytd"] = monthly["ytd"].astype(int)
    monthly["monthly"] = monthly.groupby("year")["ytd"].diff().fillna(monthly["ytd"]).astype(int)
    save(monthly[["year", "month", "month_num", "ytd", "monthly"]], "monthly_commencements.csv")

    validate(totals, nat, state, monthly)


# ------------------------------------------------------------------ checks
def validate(totals, nat, state, monthly) -> None:
    """Compare against figures verified independently on 13 Sep 2026."""
    print("\nValidation")
    failures = 0

    def check(label, got, expected):
        nonlocal failures
        ok = got == expected
        failures += not ok
        print(f"  [{' OK ' if ok else 'FAIL'}] {label}: {got:,}" + ("" if ok else f" (expected {expected:,})"))

    t = totals.set_index("year")["enrolments"]
    check("2005 total enrolments", int(t[2005]), 346_419)
    check("2019 total enrolments", int(t[2019]), 952_392)
    check("2024 total enrolments", int(t[2024]), 1_088_612)
    check("2025 total enrolments", int(t[2025]), 1_058_040)

    n24 = nat[nat["year"] == 2024].set_index("nationality")["enrolments"]
    check("2024 China", int(n24["China"]), 221_102)
    check("2024 Nepal", int(n24["Nepal"]), 86_858)

    # Monthly values should never be negative. A negative would mean the YTD
    # series fell, i.e. the differencing assumption is wrong for that month.
    neg = monthly[monthly["monthly"] < 0]
    if len(neg):
        failures += 1
        print(f"  [FAIL] {len(neg)} negative monthly commencement values:")
        print(neg.head(10).to_string(index=False))
    else:
        print("  [ OK ] monthly commencements are all non-negative")

    # Dec monthly sums back to the Dec YTD figure for each year
    roll = monthly.groupby("year")["monthly"].sum()
    dec_ytd = monthly[monthly["month"] == "Dec"].set_index("year")["ytd"]
    same = bool((roll == dec_ytd).all())
    failures += not same
    print(f"  [{' OK ' if same else 'FAIL'}] monthly values add back up to each year's December total")

    nat_share = 1 - state[state["year"] == LATEST_YEAR]["enrolments"].sum() / t[LATEST_YEAR]
    print(f"  [info] 'NAT' (national providers) excluded from state files: {nat_share:.2%} of {LATEST_YEAR} enrolments")

    print()
    print("All checks passed." if failures == 0 else f"{failures} check(s) failed. Don't build charts on these files yet.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
