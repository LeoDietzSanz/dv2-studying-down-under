# Studying Down Under

FIT3179 Data Visualisation 2: international students in Australia.

- **Plan:** `docs/implementation_plan.md` says what each chart is.
- **Architecture:** `docs/code_structure.md` says where the code lives and why.

## Layout

| Folder | What's in it | In git? |
|---|---|---|
| `raw/` | Source workbooks, as downloaded | No (too large) |
| `prep/` | Python that turns `raw/` into `data/` | Yes |
| `data/` | Slim CSVs the page reads | Yes (the site needs them) |
| `geo/` | TopoJSON and coordinate lookups | Yes |
| `charts/` | One Vega-Lite spec per chart | Yes |
| `css/`, `js/`, `index.html` | The page | Yes |

## Raw data sources

Download these into `raw/` under these exact names:

| File | Source |
|---|---|
| `Pivot_Basic_All_web.xlsx` | Department of Education, International student monthly summary and data tables: "All data" pivot |
| `Pivot_Detailed_Latest_web2025.xlsx` | Same page: "Latest data" detailed pivot |
| `Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx` | Department of Education, Higher Education Statistics, Student Data 2024 |
| `31010do001_202512.xlsx` | ABS, National, state and territory population, Dec 2025 |
| `worldbank_population.csv` | World Bank, SP.POP.TOTL (renamed from `API_SP.POP.TOTL_DS2_en_csv_v2_*.csv`) |
| `worldbank_country_metadata.csv` | Same download (renamed from `Metadata_Country_API_SP.POP.TOTL_*.csv`) |
| `dfat_top25_exports_2024-25.pdf` | DFAT, Australia's top 25 exports, goods & services 2024–25 (reference only; transcribed to `data/exports_by_commodity.csv`) |

## Working

```bash
# activate the environment (macOS/Linux)
source .venv/bin/activate
# activate the environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

python prep/check_setup.py     # confirm everything is in place
```

To view the page: right-click `index.html` in VSCode and choose **Open with Live Server**.
