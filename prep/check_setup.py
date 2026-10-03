"""Setup checker for the DV2 project.

Run from the project root:   python prep/check_setup.py

It checks that Python, the packages and the raw data files are all in place.
Every line should say OK before you start writing prep code. Nothing here
modifies your files; it only reads and reports.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"

OK, WARN, FAIL = "  OK  ", " WARN ", " FAIL "
problems = 0


def report(status: str, msg: str) -> None:
    global problems
    if status == FAIL:
        problems += 1
    print(f"[{status}] {msg}")


# ---------------------------------------------------------------- 1. Python
print("\n1. Python")
v = sys.version_info
if v >= (3, 11):
    report(OK, f"Python {v.major}.{v.minor}.{v.micro}")
else:
    report(FAIL, f"Python {v.major}.{v.minor} found; 3.11 or newer is needed")

in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
if in_venv:
    report(OK, f"Running inside a virtual environment ({Path(sys.prefix).name})")
else:
    report(WARN, "Not inside a virtual environment. Activate .venv first (see README step 4)")

# -------------------------------------------------------------- 2. Packages
print("\n2. Packages")
for pkg, why in [
    ("pandas", "tables and aggregation"),
    ("openpyxl", "reading the ABS sheet"),
    ("lxml", "streaming the Excel pivot caches"),
    ("pyarrow", "the parquet cache that makes re-runs fast"),
]:
    try:
        mod = importlib.import_module(pkg)
        report(OK, f"{pkg} {getattr(mod, '__version__', '')}  ({why})")
    except ImportError:
        report(FAIL, f"{pkg} missing  ->  pip install -r requirements.txt")

# ------------------------------------------------------------ 3. Raw files
print("\n3. Raw data files in raw/")

# (exact name you should use, a fragment that identifies a mis-named copy, required?, what it feeds)
EXPECTED = [
    ("Pivot_Basic_All_web.xlsx", "pivot_basic", True, "charts 2-6, 10, 11, 13"),
    ("Pivot_Detailed_Latest_web2025.xlsx", "pivot_detailed", True, "charts 7, 9"),
    ("Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx", "perturbed", True, "charts 1, 8, 12"),
    ("31010do001_202512.xlsx", "31010do001", True, "chart 11"),
    ("worldbank_population.csv", "api_sp.pop.totl", True, "chart 5"),
    ("worldbank_country_metadata.csv", "metadata_country", True, "chart 5 (drops aggregates)"),
    ("dfat_top25_exports_2024-25.pdf", "top-25-exports", False, "reference copy for chart 14"),
]


def norm(s: str) -> str:
    return s.lower().replace(" ", "_")


present = [p for p in RAW.iterdir() if p.is_file() and p.name != ".gitkeep"] if RAW.exists() else []

for exact, fragment, required, feeds in EXPECTED:
    target = RAW / exact
    if target.exists():
        mb = target.stat().st_size / 1_048_576
        report(OK, f"{exact}  ({mb:,.1f} MB)  -> {feeds}")
        continue
    # Look for the same file under a different name (spaces, browser suffixes, etc.)
    near = [p for p in present if fragment in norm(p.name) and "metadata_indicator" not in norm(p.name)]
    if near:
        report(FAIL if required else WARN,
               f"Found '{near[0].name}'. Rename it to '{exact}'")
    elif required:
        report(FAIL, f"{exact} missing  -> {feeds}")
    else:
        report(WARN, f"{exact} not found (optional)  -> {feeds}")

# ------------------------------------------------- 4. Quick integrity checks
print("\n4. Integrity")
basic = RAW / "Pivot_Basic_All_web.xlsx"
if basic.exists():
    import zipfile
    try:
        with zipfile.ZipFile(basic) as z:
            ok = "xl/pivotCache/pivotCacheRecords1.xml" in z.namelist()
        report(OK if ok else FAIL,
               "Pivot cache present inside Pivot_Basic_All_web.xlsx" if ok
               else "No pivot cache inside Pivot_Basic_All_web.xlsx. Re-download it; it may have been re-saved by Excel")
    except zipfile.BadZipFile:
        report(FAIL, "Pivot_Basic_All_web.xlsx is not a valid .xlsx. The download may be incomplete")

exports = ROOT / "data" / "exports_by_commodity.csv"
report(OK if exports.exists() else FAIL,
       "data/exports_by_commodity.csv present (used by the smoke-test page)" if exports.exists()
       else "data/exports_by_commodity.csv missing. Re-copy it from the starter folder")

# ----------------------------------------------------------------- Summary
print()
if problems == 0:
    print("All checks passed. You're ready to write prep/pivotcache.py.")
else:
    print(f"{problems} problem(s) to fix. Re-run this script after fixing them.")
sys.exit(1 if problems else 0)
