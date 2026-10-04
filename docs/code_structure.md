# Code Structure & Environment
### Studying Down Under · FIT3179 Data Visualisation 2 · v1, 13 September 2026

Companion to `implementation_plan.md`. That file says *what* to build; this one says *where the code lives, why it's arranged that way, and how to run it*.

---

## Part A — The two-stage architecture

Everything splits into two halves that never mix.

**Stage 1 — Preparation (Python, runs on your laptop, never deployed).**
The four source workbooks total 66 MB, and one of them expands to a 383 MB XML file internally. None of that goes near the browser. Python reads the raw workbooks and writes a handful of slim CSVs — most under 100 KB, the largest around 400 KB.

**Stage 2 — Presentation (static files, deployed to GitHub Pages).**
Plain HTML, CSS and JavaScript. Vega-Lite from a CDN. No bundler, no npm, no build step. You edit a file, refresh the browser, and see it.

The reason for the hard split is that the two stages fail differently. A wrangling bug is a data bug — you fix it in pandas and re-run. An encoding bug is a design bug — you fix it in a JSON spec. Keeping them in separate folders with a CSV boundary between them means you always know which kind of bug you have. It also means the deployed site has no dependency on Python at all: if the prep scripts break in week 11, the site still works.

---

## Part B — Repository layout

```
dv2-studying-down-under/
│
├── index.html                  ← the entire page: markup + narrative text
│
├── css/
│   ├── tokens.css              ← colour + type + spacing variables. Single source of truth.
│   ├── type.css                ← the typographic scale
│   └── layout.css              ← grid, bands, responsive rules
│
├── js/
│   ├── manifest.js             ← array: which spec renders into which div
│   └── embed.js                ← loads theme, iterates manifest, calls vegaEmbed
│
├── charts/
│   ├── theme.json              ← shared Vega-Lite config: fonts, colours, axis style
│   ├── 01-waffle.vl.json
│   ├── 02-total-line.vl.json
│   ├── 03-sector-area.vl.json
│   ├── 04-05-origin-maps.vl.json      ← hconcat: Map 1 + Map 2, linked
│   ├── 06-bump.vl.json
│   ├── 07-marimekko.vl.json
│   ├── 08-dumbbell.vl.json
│   ├── 09-country-field-heat.vl.json
│   ├── 10-flow-map.vl.json
│   ├── 11-12-landing.vl.json          ← hconcat: Map 4 + beeswarm, linked
│   ├── 13-calendar-heat.vl.json
│   └── 14-export-bar.vl.json
│
├── data/                       ← COMMITTED. The output of Stage 1. (chart numbers →)
│   ├── totals_by_year.csv            2
│   ├── sector_by_year.csv            3
│   ├── nationality_by_year.csv       6   (also feeds 50_lookups)
│   ├── state_by_year.csv             (feeds 50_lookups)
│   ├── nationality_state_2025.csv    (feeds 50_lookups)
│   ├── monthly_commencements.csv     13
│   ├── field_by_sector_2025.csv      7
│   ├── country_field_2025.csv        9
│   ├── nationality_region.csv        (feeds 50_lookups)
│   ├── he_summary_2024.csv           1
│   ├── he_institution_2024.csv       (feeds 50_lookups)
│   ├── he_field_citizenship_2024.csv 8
│   ├── country_lookup.csv            (reference: every name → ISO3)
│   ├── country_2025.csv              4, 5
│   ├── flows_2025.csv                10
│   ├── state_2025.csv                11
│   ├── he_institution_geo_2024.csv   11, 12
│   └── exports_by_commodity.csv      14  (transcribed from DFAT PDF)
│
├── geo/                        ← COMMITTED. Geometry + hand-entered coordinates.
│   ├── README.md               ← provenance and the exact mapshaper commands
│   ├── world_countries.topo.json   (Natural Earth 1:50m, simplified, 119 KB)
│   ├── au_states.topo.json         (28 KB)
│   ├── country_points.csv
│   ├── au_state_capitals.csv
│   └── au_university_locations.csv
│
├── prep/                       ← Stage 1. Python.
│   ├── check_setup.py          ← confirms environment + raw files
│   ├── pivotcache.py           ← shared: streaming reader for Excel pivot caches
│   ├── labels.py               ← shared: field / region / university-group names
│   ├── 10_basic.py             ← Pivot_Basic_All_web.xlsx      → 6 CSVs
│   ├── 20_detailed.py          ← Pivot_Detailed_Latest_web2025 → 3 CSVs
│   ├── 30_higher_ed.py         ← Perturbed_Student_Enrolments  → 3 CSVs
│   ├── 50_lookups.py           ← World Bank + ABS joins, coordinates → 5 CSVs
│   └── build.py                ← runs 10 → 20 → 30 → 50 in order, stops on the first failure
│
├── raw/                        ← GIT-IGNORED. Drop the seven .xlsx files here.
│   └── .gitkeep
│
├── docs/
│   ├── implementation_plan.md  ← the living plan
│   ├── code_structure.md       ← this file
│   └── sketch.jpg              ← photo of the hand-drawn sketch
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Why each decision

**Specs are `.json` files, not JavaScript objects inlined in `index.html`.**
Three reasons, and the third is the one that matters for your mark. First, a 400-line spec inside a `<script>` tag makes `index.html` unreadable. Second, git diffs on JSON are legible; diffs on a single enormous HTML file are not. Third — and this is the point — you can paste any `.json` file straight into the [Vega Editor](https://vega.github.io/editor) to debug it in isolation, and you can show a single spec on screen during the Week-12 interview without scrolling through unrelated markup.

**One numbered file per chart, numbers matching the plan.**
`07-marimekko.vl.json` is chart 7 in `implementation_plan.md` and panel 7 on your sketch. When a tutor asks "where's the Marimekko," there is one obvious answer. The two linked pairs get hyphenated names (`04-05`, `11-12`) because a shared `param` only works inside a single spec — the filename records that structural fact.

**`theme.json` is separate and applied at embed time.**
Vega-Lite's `config` block controls fonts, label colours, axis strokes, grid opacity and the default categorical range. If you copy that block into fourteen files, then decide the axis grey is too dark, you edit fourteen files and miss one. Instead `embed.js` fetches `theme.json` once and passes it as the `config` option to every `vegaEmbed` call. Consistency across charts is explicitly marked under the layout and typography criteria, so this is not just tidiness.

**`tokens.css` holds every colour and size as a CSS custom property.**
The same hex values appear in `theme.json`. They must match — the ochre in a chart and the ochre in a heading are the same ochre. Keep the two files open side by side when you change anything. (A CSS file cannot import from JSON without a build step, and adding a build step to avoid one duplicated list is a bad trade.)

**`data/` and `geo/` are committed to git.**
GitHub Pages serves whatever is in the repo. If the CSVs aren't committed, the deployed site renders nothing. They're small and they're derived artefacts, which normally argues for ignoring them — but here they *are* the deployment, so they go in.

**`raw/` is git-ignored.**
`Pivot_Basic_All_web.xlsx` alone is 44 MB. GitHub warns above 50 MB per file and Pages has a 1 GB site limit; more practically, a repo full of 40 MB binaries is slow to clone and impossible to diff. The prep scripts read from `raw/`, and `README.md` records where to re-download each file.

**`prep/` scripts are numbered and idempotent.**
Each one reads from `raw/`, writes to `data/`, and can be re-run safely at any time. `build.py` runs them in order. Numbering by tens leaves room to insert `15_something.py` later without renaming anything.

---

## Part C — The pivot-cache problem, and how `pivotcache.py` solves it

This is the one genuinely non-obvious piece of engineering in the project, so it gets its own module and its own explanation.

Three of your four main workbooks are **Excel pivot tables, not flat tables**. The visible sheet is just a rendered view with dropdown filters. The actual data lives in a hidden part of the `.xlsx` (which is a ZIP archive) at `xl/pivotCache/pivotCacheRecords1.xml`.

For `Pivot_Basic_All_web.xlsx` that file is **383 MB of XML holding 3,512,371 records**. `pandas.read_excel` will not give you this data — it reads the rendered sheet, which is a 16-row summary. Loading the XML with a normal parser will exhaust memory.

The solution is streaming. `prep/pivotcache.py` exposes one function:

```python
def read_pivot_cache(xlsx_path: str) -> pandas.DataFrame:
    """Stream an Excel pivot cache into a flat DataFrame.

    Reads xl/pivotCache/pivotCacheDefinition1.xml for the field names and
    their shared-item dictionaries, then iterparses pivotCacheRecords1.xml
    one <r> element at a time, clearing each element and its previous
    siblings so peak memory stays flat regardless of file size.
    """
```

The mechanics, in brief:

- `pivotCacheDefinition1.xml` lists the fields in order. Categorical fields carry a `<sharedItems>` dictionary — the records store integer indices into it, which is why the file compresses from 383 MB to 44 MB.
- Each record `<r>` has one child per field, in field order. `<x v="12"/>` means *index 12 of this field's dictionary*; `<n v="3.0"/>` is a literal number.
- `lxml.etree.iterparse(..., tag='...}r')` yields records one at a time. After each, call `r.clear()` and delete previous siblings from the parent, or lxml keeps the whole processed tree alive and you're back to 383 MB.

Measured on this container: **44 seconds for a full pass** over the basic cache. That's why `10_basic.py` makes a *single* pass and accumulates every aggregate it needs in one go, rather than re-reading per chart. Six CSVs come out of one traversal.

**Cache it.** The first thing `10_basic.py` should do is check for `raw/_cache/basic.parquet`; if it's absent, stream the XML and write it; if present, load it in about a second. You will re-run this script fifteen times while tuning aggregations, and 44 seconds each time adds up to nothing useful.

---

## Part D — How the page assembles itself

`index.html` contains the narrative — headings, standfirsts, body paragraphs, captions, footer — and an empty `<div>` where each chart goes:

```html
<figure class="chart chart--full">
  <div id="vis-02"></div>
  <figcaption>
    <b>2 · Annotated line chart</b> — Total international enrolments,
    December snapshot, 2005–2025. Source: Department of Education, PRISMS.
  </figcaption>
</figure>
```

`js/manifest.js` is a flat list:

```js
export const CHARTS = [
  { el: "#vis-01", spec: "charts/01-waffle.vl.json" },
  { el: "#vis-02", spec: "charts/02-total-line.vl.json" },
  // …
];
```

`js/embed.js` does four things:

1. Fetches `charts/theme.json` once.
2. For each manifest entry, registers an `IntersectionObserver` on the target div.
3. When a div comes within ~400 px of the viewport, calls `vegaEmbed(el, specUrl, { config: theme, actions: false, renderer: "svg" })`.
4. Logs any failure to the console with the chart id, so a broken spec doesn't silently blank.

Lazy loading matters here. Fourteen specs, four of them maps with TopoJSON, all parsed at page load is a visibly janky first paint. Deferring until near-viewport makes the page feel instant, and the scroll-triggered appearance suits a narrative page. `renderer: "svg"` gives crisp text at any zoom and makes it easy to screenshot panels for your report; switch a specific map to `"canvas"` only if it stutters.

`actions: false` hides the "…" export menu in the deployed version. Keep it `true` while developing — the "Open in Vega Editor" link is the fastest debugging path you have.

---

## Part E — Environment setup on your laptop (VSCode)

### 1. Install the three things you need

- **VSCode** — you have it.
- **Python 3.11 or newer** — [python.org/downloads](https://www.python.org/downloads/). On Windows, tick *Add Python to PATH* during install.
- **Git** — [git-scm.com](https://git-scm.com/downloads).

Verify in the VSCode terminal (`Ctrl+` ` / `Cmd+` `):

```bash
python --version    # or python3 --version on macOS/Linux
git --version
```

### 2. VSCode extensions

Open the Extensions panel (`Ctrl+Shift+X`) and install:

| Extension | Publisher | What it's for |
|---|---|---|
| **Python** | Microsoft | Interpreter selection, debugging |
| **Live Server** | Ritwick Dey | Serves the site over `http://` — **essential**, see below |
| **Vega Viewer** | Randy Zwitch | Preview a `.vl.json` spec inside VSCode |
| **Rainbow CSV** | mechatroner | Makes the prep output readable |
| **Even Better TOML** / **Prettier** | — | Optional formatting |

**Why Live Server is not optional:** opening `index.html` by double-clicking gives you a `file://` URL. Browsers block `fetch()` on `file://` for security, so every CSV and every spec load fails with an opaque CORS error and the page renders blank. You must serve over HTTP. Right-click `index.html` → *Open with Live Server*. It also auto-reloads on save.

If you'd rather not use the extension, in the project root run `python -m http.server 8000` and open `http://localhost:8000`.

### 3. Create the project

```bash
mkdir dv2-studying-down-under && cd dv2-studying-down-under
code .
```

Then in the VSCode terminal:

```bash
# folder skeleton
mkdir -p css js charts data geo prep raw docs

# virtual environment
python -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

If PowerShell refuses with an execution-policy error, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Then:

```bash
pip install --upgrade pip
pip install pandas openpyxl lxml requests pyarrow
pip freeze > requirements.txt
```

`lxml` does the streaming XML. `pyarrow` gives you the parquet cache. `requests` fetches the World Bank data. `openpyxl` reads the ABS and DFAT sheets.

Press `Ctrl+Shift+P` → *Python: Select Interpreter* → pick the one inside `.venv`. Without this, VSCode's terminal and its linter disagree about what's installed.

### 4. `.gitignore`

```gitignore
raw/*
!raw/.gitkeep
.venv/
__pycache__/
*.pyc
.DS_Store
.vscode/settings.json
```

### 5. Drop the data in and build

Copy all seven `.xlsx` files into `raw/`, then:

```bash
python prep/build.py
```

It should print a validation report and populate `data/`. Spot-check one file with Rainbow CSV before you write a single spec.

### 6. Git and GitHub Pages

```bash
git init
git add .
git commit -m "Project skeleton, prep pipeline, first specs"
```

Create an empty repo on GitHub (no README, no .gitignore — you have both), then:

```bash
git remote add origin https://github.com/<you>/dv2-studying-down-under.git
git branch -M main
git push -u origin main
```

On GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save.**
Live at `https://<you>.github.io/dv2-studying-down-under/` within a minute or two.

Deploy early — in week 9, with one chart on the page. A deployment problem found in week 9 costs an hour; the same problem found the night before submission costs the assignment. Push after every working session.

---

## Part F — Working order

Build in this sequence. Each step is checkable before the next begins.

1. **`prep/pivotcache.py` + `prep/10_basic.py`.** Nothing else can start until CSVs exist. Verify `totals_by_year.csv` against the numbers in the plan's Appendix — if 2024 reads 1,088,612, your extraction is correct.
2. **`index.html` skeleton + `tokens.css` + `type.css` + `layout.css`.** Headings, standfirsts, empty figure divs, footer. No charts. Get the page looking right as a typographic object first; it's much harder to fix layout once fourteen charts are fighting you.
3. **`theme.json` + `embed.js` + chart 2** (the annotated line — simplest spec that exercises the whole pipeline). When chart 2 renders with the right fonts and colours, the machinery is proven.
4. **Charts 3, 13, 6** — everything else from the basic cache.
5. **`30_higher_ed.py` → charts 1, 8, 12.**
6. **`20_detailed.py` → charts 7, 9.**
7. **`50_lookups.py` + geometry → the linked map pair (4–5), then the flow map (10), then 11–12.** Maps last: they're the highest-risk specs and they depend on lookups that don't exist yet.
8. **Chart 14** once you've downloaded the DFAT commodity table.
9. **Annotations, captions, footer, alt text, final colour pass.**

Commit at every numbered step. If step 7 goes badly at 2 a.m., you want a clean `git checkout` back to a page that worked.
