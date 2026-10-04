"""Stage 1, script 30: Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx -> data/.

Run from the project root:   python prep/30_higher_ed.py

This is the only source with DOMESTIC students alongside overseas ones, so
it's what makes "more than one in three" possible. Higher education only.

About "perturbed"
-----------------
The Department adds small random noise to protect privacy, which is why a
few cells are -1 or 1. Totals are reliable; tiny counts are not. Captions
using these numbers should say the figures are perturbed.

Outputs
-------
  he_summary_2024.csv            overseas vs domestic totals, two scopes    -> chart 1
  he_institution_2024.csv        one row per provider: share, size, group  -> chart 12
  he_field_citizenship_2024.csv  field shares, domestic vs overseas        -> chart 8
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pivotcache import read_pivot_cache  # noqa: E402
from labels import (GO8, HE_BUCKETS, HE_FIELD_LABEL, HOME_STATE_OVERRIDE,  # noqa: E402
                    PRIVATE_UNIS, STATE_ABBR, short_uni)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx"
OUT = ROOT / "data"
YEAR = 2024
COUNT = "Enrolment Count"


def save(df: pd.DataFrame, name: str) -> None:
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  wrote {name:<30} {len(df):>4,} rows  {path.stat().st_size / 1024:>6.1f} KB")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    print("Reading pivot cache")
    df = read_pivot_cache(RAW)
    he = df[df["Year"] == YEAR].copy()
    for col in ("Institution", "State", "Citizenship"):
        he[col] = he[col].astype(str)

    print("\nWriting CSVs")

    # ---- chart 1: the hook number, in two scopes ----------------------------
    # "All providers" is the honest headline. "Universities" leaves out the
    # bucket rows of private colleges, which are 58% overseas and push the
    # all-provider share up. Showing both lets the caption be exact.
    def split(frame: pd.DataFrame, scope: str) -> dict:
        c = frame.groupby("Citizenship")[COUNT].sum()
        o, d = int(c.get("Overseas", 0)), int(c.get("Domestic", 0))
        return {"scope": scope, "overseas": o, "domestic": d, "total": o + d,
                "overseas_share": round(o / (o + d), 5)}

    summary = pd.DataFrame([
        split(he, "All higher-education providers"),
        split(he[~he["Institution"].isin(HE_BUCKETS)], "Universities only"),
    ])
    save(summary, "he_summary_2024.csv")

    # ---- chart 12: one row per provider -------------------------------------
    inst = (he.pivot_table(index="Institution", columns="Citizenship", values=COUNT,
                           aggfunc="sum", fill_value=0)
              .reset_index().rename(columns={"Institution": "institution",
                                             "Domestic": "domestic", "Overseas": "overseas"}))
    inst = inst[~inst["institution"].isin(HE_BUCKETS)].copy()
    inst[["domestic", "overseas"]] = inst[["domestic", "overseas"]].clip(lower=0).astype(int)
    inst["total"] = inst["domestic"] + inst["overseas"]
    inst["overseas_share"] = (inst["overseas"] / inst["total"]).round(4)

    # Home state = where most of the provider's enrolments are. Needed so
    # clicking a state on Map 4 can filter this chart.
    by_state = (he[he["State"] != "Multi-State"]
                  .groupby(["Institution", "State"])[COUNT].sum().reset_index()
                  .sort_values(COUNT, ascending=False)
                  .drop_duplicates("Institution"))
    home = dict(zip(by_state["Institution"], by_state["State"].map(STATE_ABBR)))
    home.update(HOME_STATE_OVERRIDE)
    inst["state"] = inst["institution"].map(home)

    inst["group"] = inst["institution"].map(
        lambda n: "Group of Eight" if n in GO8 else ("Private" if n in PRIVATE_UNIS else "Other public"))
    inst["short_name"] = inst["institution"].map(short_uni)
    inst = inst.sort_values("overseas_share", ascending=False)
    save(inst[["institution", "short_name", "state", "group",
               "domestic", "overseas", "total", "overseas_share"]], "he_institution_2024.csv")

    # ---- chart 8: field shares, domestic vs overseas ------------------------
    # Uses the per-field count columns. A combined degree (e.g. Law/Commerce)
    # counts once in each of its fields; this is how the Department reports
    # fields, and the caption should say so. Shares are of the field-count
    # total, so each cohort's shares sum to 100%.
    field_cols = {f"{name} Count": label for name, label in HE_FIELD_LABEL.items()}
    fc = (he.groupby("Citizenship")[list(field_cols)].sum().T
            .rename(index=field_cols)
            .rename(columns={"Domestic": "domestic", "Overseas": "overseas"}))
    all_field_cols = [c for c in he.columns if c.endswith(" Count") and c != COUNT]
    denom = he.groupby("Citizenship")[all_field_cols].sum().sum(axis=1)
    fc["domestic_share"] = (fc["domestic"] / denom["Domestic"]).round(5)
    fc["overseas_share"] = (fc["overseas"] / denom["Overseas"]).round(5)
    fc["gap_pp"] = ((fc["overseas_share"] - fc["domestic_share"]) * 100).round(2)
    fc[["domestic", "overseas"]] = fc[["domestic", "overseas"]].astype(int)
    fc = (fc.reset_index().rename(columns={"index": "field"})
            .sort_values("gap_pp", ascending=False))
    save(fc[["field", "domestic", "overseas", "domestic_share", "overseas_share", "gap_pp"]],
         "he_field_citizenship_2024.csv")

    validate(summary, inst, fc)


def validate(summary, inst, fc) -> None:
    print("\nValidation")
    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        failures += not ok
        print(f"  [{' OK ' if ok else 'FAIL'}] {label}{(': ' + detail) if detail else ''}")

    allp = summary.iloc[0]
    check("2024 overseas", allp["overseas"] == 589_355, f"{allp['overseas']:,}")
    check("2024 total", allp["total"] == 1_676_077, f"{allp['total']:,}")
    for _, r in summary.iterrows():
        print(f"  [info] {r['scope']}: {r['overseas_share']:.1%} overseas "
              f"(about 1 in {1 / r['overseas_share']:.1f})")
    check("every provider has a home state", inst["state"].notna().all(),
          ", ".join(inst.loc[inst["state"].isna(), "institution"]))
    check("bucket rows excluded", not inst["institution"].isin(HE_BUCKETS).any())
    go8 = (inst["group"] == "Group of Eight").sum()
    check("all 8 Go8 universities found", go8 == 8, f"{go8}")
    check("providers", True, f"{len(inst)}")
    top = fc.iloc[0]
    print(f"  [info] widest gap: {top['field']} "
          f"({top['overseas_share']:.1%} overseas vs {top['domestic_share']:.1%} domestic)")

    print()
    print("All checks passed." if failures == 0 else f"{failures} check(s) failed.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
