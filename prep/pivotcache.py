"""Read the hidden data inside an Excel pivot-table workbook.

Why this exists
---------------
The Department of Education workbooks are pivot tables. The sheet you see in
Excel is only a 16-row summary; pandas.read_excel returns that summary and
nothing else. The real records live in a hidden XML file inside the .xlsx
(an .xlsx is a ZIP archive):

    xl/pivotCache/pivotCacheDefinition1.xml   field names + lookup dictionaries
    xl/pivotCache/pivotCacheRecords1.xml      one <r> element per record

For Pivot_Basic_All_web.xlsx the records file is 383 MB of XML holding
3.5 million records, too big to load in one go. So we stream it: read one
record, keep the values we need, throw the XML away, move on. Memory stays
flat no matter how large the file is.

How a record is encoded
-----------------------
Each <r> has one child per field, in field order:
    <x v="12"/>   index 12 into that field's dictionary (categorical fields)
    <n v="3"/>    a literal number
    <s v="abc"/>  a literal string
    <m/>          missing

Usage
-----
    from pivotcache import read_pivot_cache
    df = read_pivot_cache("raw/Pivot_Basic_All_web.xlsx")

The first call streams the XML (about 45 seconds for the basic workbook) and
saves a parquet copy in raw/_cache/. Later calls load that copy in about a
second. If the source workbook changes, the cache is rebuilt automatically.
"""
from __future__ import annotations

import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from lxml import etree

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DEFINITION = "xl/pivotCache/pivotCacheDefinition1.xml"
RECORDS = "xl/pivotCache/pivotCacheRecords1.xml"


# --------------------------------------------------------------------------
# Step 1: the definition: field names and their lookup dictionaries
# --------------------------------------------------------------------------
def _read_fields(zf: zipfile.ZipFile) -> list[tuple[str, list | None]]:
    """Return [(field_name, dictionary_or_None), ...] in record order.

    Categorical fields have a dictionary of shared items; records refer to
    them by index. Purely numeric fields (the DATA_ columns) have no
    dictionary; their values are written directly into each record.
    """
    root = etree.fromstring(zf.read(DEFINITION))
    fields = []
    for fld in root.iter(f"{NS}cacheField"):
        shared = fld.find(f"{NS}sharedItems")
        items = None
        if shared is not None and len(shared):
            items = []
            for item in shared:
                tag = etree.QName(item).localname
                if tag == "m":
                    items.append(None)
                elif tag == "n":
                    v = float(item.get("v"))
                    items.append(int(v) if v.is_integer() else v)
                else:
                    items.append(item.get("v"))
        fields.append((fld.get("name"), items))
    return fields


# --------------------------------------------------------------------------
# Step 2: stream the records
# --------------------------------------------------------------------------
def _stream_records(path: Path, verbose: bool) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        if RECORDS not in zf.namelist():
            raise ValueError(
                f"{path.name} has no pivot cache. If you opened and re-saved it "
                "in Excel, download a fresh copy."
            )
        fields = _read_fields(zf)
        n_fields = len(fields)

        # One growing Python list per field. Categorical fields store the
        # small integer index (cheap); numeric fields store floats.
        columns: list[list] = [[] for _ in range(n_fields)]
        is_cat = [items is not None for _, items in fields]

        t0 = time.time()
        context = etree.iterparse(zf.open(RECORDS), events=("end",), tag=f"{NS}r")
        for count, (_, rec) in enumerate(context, start=1):
            for i, cell in enumerate(rec):
                tag = cell.tag[len(NS):]
                if tag == "x":
                    columns[i].append(int(cell.get("v")))
                elif tag == "n":
                    columns[i].append(float(cell.get("v")))
                elif tag == "m":
                    columns[i].append(-1 if is_cat[i] else np.nan)
                else:  # "s", "b", "d": rare inline literals
                    columns[i].append(cell.get("v"))

            # Free the XML we just used. Without these two lines lxml keeps
            # every processed record in memory and you're back to 383 MB.
            rec.clear()
            while rec.getprevious() is not None:
                del rec.getparent()[0]

            if verbose and count % 500_000 == 0:
                print(f"    {count:>9,} records  ({time.time() - t0:.0f}s)")

    # Turn the lists into proper pandas columns.
    data = {}
    for (name, items), values in zip(fields, columns):
        if items is not None:
            codes = np.asarray(values, dtype=np.int32)
            labels = pd.Index(items)
            if labels.has_duplicates or labels.hasnans:
                # Fall back to plain values if the dictionary is unusual.
                lookup = np.array(items + [None], dtype=object)
                data[name] = lookup[codes]
            elif all(isinstance(v, (int, float)) for v in items):
                # Numeric dictionaries (e.g. Year) become plain numbers, so
                # the column type is the same whether or not the cache is used.
                data[name] = np.asarray(items)[codes]
            else:
                data[name] = pd.Categorical.from_codes(codes, categories=labels)
        else:
            data[name] = pd.to_numeric(pd.Series(values), errors="coerce")
    df = pd.DataFrame(data)

    if verbose:
        print(f"    {len(df):,} records read in {time.time() - t0:.0f}s")
    return df


# --------------------------------------------------------------------------
# Public entry point, with a parquet cache
# --------------------------------------------------------------------------
def read_pivot_cache(xlsx_path: str | Path, use_cache: bool = True,
                     verbose: bool = True) -> pd.DataFrame:
    """Return every record in a pivot-table workbook as a flat DataFrame.

    Categorical fields come back as pandas Categoricals and numeric fields
    as floats. Field names are exactly as Excel stores them, e.g.
    'Nationality', 'DATA_YTD_Enrolments'.
    """
    path = Path(xlsx_path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run prep/check_setup.py")

    cache_dir = path.parent / "_cache"
    stat = path.stat()
    # The cache name includes the source's size and modification time, so a
    # replaced workbook never silently reuses an old cache.
    cache = cache_dir / f"{path.stem}.{stat.st_size}.{int(stat.st_mtime)}.parquet"

    if use_cache and cache.exists():
        if verbose:
            print(f"  {path.name}: loading cached copy")
        return pd.read_parquet(cache)

    if verbose:
        print(f"  {path.name}: streaming pivot cache (first run only; about a minute)")
    df = _stream_records(path, verbose)

    if use_cache:
        cache_dir.mkdir(exist_ok=True)
        for old in cache_dir.glob(f"{path.stem}.*.parquet"):
            old.unlink()
        df.to_parquet(cache, index=False)
    return df


if __name__ == "__main__":
    # Quick look:  python prep/pivotcache.py raw/Pivot_Basic_All_web.xlsx
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "raw/Pivot_Basic_All_web.xlsx"
    frame = read_pivot_cache(target)
    print()
    print(frame.dtypes)
    print()
    print(frame.head())
