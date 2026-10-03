# Implementation Plan — v4
### Studying Down Under · FIT3179 Data Visualisation 2
**Living document.** v4, 13 September 2026. Supersedes `plan_v3_and_sketch_instructions.md`.

---

## Part A — What changed in v4, and why

v4 is the first version written with the actual data in hand. Five changes.

**1. The hook figure is wrong in v1–v3, and the truth is better.**
Every previous version said "1 in 4 university students is international." The 2024 higher-education data says **589,355 overseas students out of 1,676,077 — 35.2 per cent**. It is **more than one in three**. This is a stronger opening and it is defensible from the file. (Caveat to check in prep: that total includes the "Non-University Higher Education Providers" bucket, which runs 58% overseas. Compute the universities-only figure as well and use whichever you can caption honestly — likely "one in three" either way.)

**2. Chart 2's line starts in 2005, not 1994.** The basic pivot cache begins in 2005. No loss: 2005 is the start of the VET boom, so the series still opens on a rise and still contains all three shocks.

**3. Act 5 gets a real ending.** Full-year 2025 enrolments are **1,058,040**, down from **1,088,612** in 2024 — the first non-pandemic annual fall in the series. The caps are visible in the data, not just asserted in the narrative.

**4. Region colouring on Map 1 no longer needs a new source.** The detailed workbook carries a `Region` field mapped to `Nationality`. Extract that mapping once in `20_detailed.py` and reuse it to colour the basic-cache countries.

**5. Chart 14 is at risk.** The trade file sourced is *direction* of trade (exports by partner economy), not *composition* by commodity. It cannot produce "education vs iron ore." See Part E.

**Still outstanding:** confirm the current state of the 2025–26 caps and Ministerial Direction settings before writing Act 5's prose. Storytelling is marked partly on factual coherence and that policy has moved repeatedly.

---

## Part B — The design system

### Palette

One accent, one counterpoint, two sequential ramps, one categorical set. Nothing else. The accent is reserved — throughout the whole page, **ochre means "international"** and nothing else ever uses it.

| Role | Hex | Used for |
|---|---|---|
| Paper | `#FAF7F2` | Page background — warm off-white, not pure white |
| Panel | `#FFFFFF` | Chart plotting areas, to lift them off the paper |
| Ink | `#14212B` | Headings, chart titles, annotation text |
| Ink-muted | `#5C6670` | Body text, captions, axis labels |
| Rule | `#E2DCD3` | Hairlines, grid, figure borders |
| **Accent — international** | `#C2701C` | Every mark representing international students |
| **Counterpoint — domestic** | `#2A6B70` | Every mark representing domestic students |
| Highlight | `#8C2F1B` | Annotation leader lines, the 2025 decline marker. Sparingly |

**Sequential A — counts** (choropleths and heatmaps of raw volume):
`#EDF4F4 → #C5DEDE → #8FC0C2 → #4E9296 → #226568 → #0D4247`

**Sequential B — rates** (the per-capita map, so a reader can never confuse a rate with a count):
`#FBF1E3 → #F1D6AE → #E0B074 → #C2701C → #9A5411 → #6B390A`

**Categorical — sector** (five values, one page-wide assignment, never re-shuffled):

| Sector | Hex |
|---|---|
| Higher Education | `#1D4E5C` |
| VET | `#C2701C` |
| ELICOS | `#7FA8B8` |
| Schools | `#86A96E` |
| Non-award | `#A79B8E` |

**Categorical — region** (Map 1 symbol fill, six classes): `#1D4E5C` North-East Asia · `#C2701C` Southern & Central Asia · `#7FA8B8` South-East Asia · `#86A96E` Americas · `#B5794E` Sub-Saharan Africa · `#8C93A1` Europe / Middle East / Oceania.

**Why this survives scrutiny.** Teal–ochre is the standard colourblind-safe opposition: it separates cleanly under deuteranopia and protanopia, where red–green does not. Both sequential ramps are single-hue with monotonic lightness, so they read correctly in greyscale and satisfy the ordered-channel requirement from the marks-and-channels notes. Categorical hue is used only where the attribute is genuinely categorical. The accent is reserved for one meaning, which is the "one accent colour" principle from the data-ink material.

### Typography

| Role | Family | Size / line-height | Weight |
|---|---|---|---|
| Page title | Source Serif 4 | 56 / 1.05 | 700 |
| Standfirst | Inter | 21 / 1.5 | 400, `--ink-muted` |
| KPI numeral | Source Serif 4 | 68 / 1.0, tabular figures | 700, accent |
| Act heading | Source Serif 4 | 32 / 1.2 | 600 |
| Act standfirst | Inter | 19 / 1.5 | 500 |
| Body | Inter | 17 / 1.65 | 400 |
| Chart title | Inter | 16 / 1.3 | 600 |
| Chart subtitle | Inter | 13.5 / 1.4 | 400, muted |
| Axis / legend label | Inter | 11.5 | 400, muted |
| Annotation | Inter | 12.5 | 600, highlight |
| Caption | Inter | 12.5 / 1.45 | 400, muted |
| Footer | Inter | 12 / 1.5 | 400, muted |

Both are free on Google Fonts. One `<link>`, subset to the weights above.

**Why.** A serif display face against a sans text face gives you hierarchy through contrast in *form*, not just size — which is the point the typography notes make about weight, size and colour contrast guiding the eye. Inter is used for everything small because humanist sans faces with large x-heights outperform serifs at 11–12 px on screen, and every chart label sits in that range. Tabular figures on the KPI numerals stop digits jittering. Body measure is capped at **62 characters**, matching the seven-to-ten-words-per-line guidance; body text is left-aligned, never justified, never centred.

### Layout

- **Single scrolling page.** Content column **1120 px** max, centred, 12 columns, 24 px gutters.
- **The left sight-line is the spine.** Every act heading, every body paragraph, every chart's left edge and every caption starts on column 1. One vertical line down the whole page. This single decision carries most of the layout mark.
- **Three chart widths only:** full (12 col, ~1072 px), half (6 col, ~524 px), and wide (8 col) for the flow map's world outline. No other widths.
- **Vertical rhythm:** 96 px between acts, 48 px between charts inside an act, 12 px from chart to its caption. Body paragraphs sit in a 7-column block (~62ch) so text never runs the full width even though charts do — that asymmetry creates the white space the layout notes call for.
- **Act headings** get a 1 px `--rule` hairline above them, full content width. Cheap, and it makes the five-act structure legible at a glance while scrolling.
- **Responsive:** below 900 px, half-width charts stack to full width; the two `hconcat` pairs stack vertically. Below 640 px, reduce title to 38 px. Don't over-engineer this — it's marked on the desktop view.
- **Footer:** hairline, then author, date, all five sources with URLs, and the AI-use acknowledgement.

### Interaction — three things only

1. **Tooltips on every chart.** Formatted numbers (`,.0f`), full category names, never raw field codes.
2. **Hover a country in the Act 2 map pair** → highlights in both Map 1 and Map 2. One `hconcat` spec, one shared `param`.
3. **Click a state on Map 4** → filters the beeswarm to that state's institutions. One `hconcat` spec.

No year sliders. A slider is an exploration control; this is a presentation piece, and the rubric distinguishes them. Optional fourth if testers find the per-capita map confusing: a `bind: {input: "radio"}` raw/per-100k toggle on Map 2.

---

## Part C — The fourteen charts

Numbering matches `charts/NN-*.vl.json` and the sketch panels.

### Header band

Title **STUDYING DOWN UNDER**. Standfirst: one sentence establishing that this is Australia's largest services export and that the people behind the number are 1.06 million individuals from 200-plus countries.

Two KPI numerals, tabular, ochre:
- **1 in 3** — university students in Australia is from overseas
- **#3** — Australia's rank as a destination for internationally mobile students *(UNESCO, cite in footer)*

---

### Act 1 — "A world-class classroom"
*Standfirst: the scale of the thing, and the three times it broke.*

**Chart 1 · Waffle / isotype grid** — ADVANCED · load-bearing
- **Title:** More than one in three
- **Subtitle:** Share of all Australian higher-education students who are overseas students, 2024
- **Caption:** 1 · Isotype grid — each square is 1% of the 1,676,077 students enrolled in Australian higher education in 2024; 35 are overseas. Source: Department of Education, Higher Education Student Data (perturbed), 2024.
- **Data:** `he_institution_2024.csv`, aggregated to two numbers
- **How:** 10×10 grid of `square` marks. 35 filled accent, 65 filled `#E2DCD3`. Position on a derived row/column; colour is the only other channel. No legend — the subtitle carries it.

**Chart 2 · Annotated line chart** — basic
- **Title:** Twenty years, three shocks
- **Subtitle:** Total international student enrolments, December snapshot, 2005–2025
- **Caption:** 2 · Line chart with annotations — enrolments count courses, not people; a student in two courses counts twice. Source: Department of Education, PRISMS.
- **Data:** `totals_by_year.csv`
- **How:** `line` + `point`. x = year (ordinal→temporal), y = enrolments (quantitative, zero baseline). Three `rule`+`text` annotation layers in `--highlight`: *2009 — VET visa crackdown*, *2020 — borders close*, *2025 — first fall outside the pandemic*. End-of-line direct label instead of a legend.

**Chart 3 · Stacked area by sector** — basic
- **Title:** The boom was never only universities
- **Subtitle:** Enrolments by education sector, 2005–2025
- **Caption:** 3 · Stacked area chart — VET's 2009 peak was driven by cookery and hairdressing courses tied to permanent-residence pathways. Source: Department of Education, PRISMS.
- **Data:** `sector_by_year.csv`
- **How:** `area` with `stack: "zero"`, colour = the five-sector categorical scale. Ordered largest-at-bottom. One text annotation on the VET bulge.

---

### Act 2 — "Who's in the classroom?"
*Standfirst: the obvious answer is China and India. The interesting answer is Nepal.*

**Charts 4 + 5 build as one `hconcat` spec — they must stay side by side. The comparison is the insight.**

**Chart 4 · MAP 1 — Proportional-symbol map** — advanced (surplus)
- **Title:** Where they come from
- **Subtitle:** International student enrolments by country of citizenship, 2025
- **Caption:** 4 · Proportional-symbol map, Equal Earth projection — circle area encodes enrolments; colour encodes world region. Source: Department of Education, PRISMS.
- **Data:** `nationality_by_year.csv` (2025) + `geo/country_centroids.csv` + `geo/ne_110m_admin_0_countries.topo.json`
- **How:** `geoshape` basemap in `#F0EDE7` with `#E2DCD3` borders, `equalEarth` projection rotated so the Pacific isn't split. `circle` marks at centroids; **size scaled by `sqrt`** (area, not radius — the bubble-plot guidance is explicit), `opacity: 0.85`, thin white stroke. Colour = region categorical.

**Chart 5 · MAP 2 — Per-capita choropleth** — ADVANCED · load-bearing
- **Title:** …and where that's a big deal
- **Subtitle:** Students in Australia per 100,000 people of the sending country, 2025
- **Caption:** 5 · Choropleth, Equal Earth projection — Nepal sends more students to Australia per head than any large country on Earth. China's raw total is the largest; its rate is unremarkable. Sources: Department of Education, PRISMS; World Bank, total population (SP.POP.TOTL).
- **Data:** `nationality_by_year.csv` + `country_population.csv`, joined on ISO3
- **How:** `geoshape`, colour = Sequential B (ochre), **quantile or threshold bins, not linear** — the distribution is severely right-skewed and a linear ramp will show one dark country and 200 pale ones. Same projection and size as Map 4 so the pair reads as a genuine comparison.
- **This is the analytical core of the page.** It is the chart that makes the second data source do real work rather than sit there satisfying a rule.

**Chart 6 · Bump chart** — advanced (surplus)
- **Title:** The order keeps changing
- **Subtitle:** Rank of the top 10 source countries, 2010–2025
- **Caption:** 6 · Bump chart — encodes rank, not volume; a line that stays flat is a country holding position, not a country holding still. Source: Department of Education, PRISMS.
- **Data:** `nationality_by_year.csv`
- **How:** `line` + `point` per country. y = rank, **reversed scale, 1 at top**, integer ticks. Grey all lines except China, India and Nepal; direct-label those three at both ends. No legend.

---

### Act 3 — "What they come to study"
*Standfirst: your passport predicts your degree more than you'd expect.*

**Chart 7 · Marimekko / mosaic** — ADVANCED · load-bearing
- **Title:** Two fields carry the whole system
- **Subtitle:** Enrolments by broad field of education, split by sector, 2025
- **Caption:** 7 · Marimekko chart — column width encodes the size of each field; the vertical split shows sector composition within it. Management & Commerce and IT together account for a disproportionate share. Source: Department of Education, PRISMS (detailed).
- **Data:** `field_by_sector_2025.csv`
- **How:** `rect` marks on derived cumulative x-extents (`x`/`x2`) and stacked y-shares (`y`/`y2`). Colour = sector categorical. Both `transform` steps computed in Python, not in Vega-Lite — keep the spec readable.

**Chart 8 · Dumbbell plot** — ADVANCED · load-bearing
- **Title:** The two cohorts study different things
- **Subtitle:** Share of enrolments in each field: domestic vs overseas students, higher education, 2024
- **Caption:** 8 · Dumbbell plot — each row compares one field's share of domestic enrolments (teal) with its share of overseas enrolments (ochre). The gap is the point. Figures are perturbed for confidentiality. Source: Department of Education, Higher Education Student Data.
- **Data:** `he_field_citizenship_2024.csv`
- **How:** `rule` from domestic to overseas share, then two `circle` marks. Rows sorted by gap size, not alphabetically. Colour-coded words in the subtitle instead of a legend.

**Chart 9 · Country × field heatmap** — ADVANCED · load-bearing
- **Title:** Your passport predicts your degree
- **Subtitle:** Share of each country's enrolments by broad field, top 10 source countries, 2025
- **Caption:** 9 · Heatmap — colour encodes each field's share *within* a country, so rows are comparable despite very different totals. Source: Department of Education, PRISMS (detailed).
- **Data:** `country_field_2025.csv`
- **How:** `rect`, colour = Sequential A. **Normalise within row** — without it the map just re-shows that China and India are large. Countries sorted by total; fields in a fixed order shared with chart 7.

---

### Act 4 — "Where they land"
*Standfirst: different origins land in different states. The map that shows it is the hinge of this page.*

**Chart 10 · MAP 3 — Flow map** — ADVANCED · load-bearing
- **Title:** Different origins, different states
- **Subtitle:** Enrolments from the top 12 source countries to Australian states and territories, 2025
- **Caption:** 10 · Flow map — line thickness encodes enrolment volume; colour encodes origin region. Straight geodesic rules, Equal Earth projection. Source: Department of Education, PRISMS.
- **Data:** `nationality_state_2025.csv` + `geo/country_centroids.csv` + state centroids
- **How:** `rule` marks with `longitude`/`latitude` and `longitude2`/`latitude2`. `strokeWidth` scaled by `sqrt`, `opacity: 0.55`, `strokeCap: "round"`. Filter to the top 12 origins and drop flows below a threshold or it becomes a hairball. **The lines must visibly fan to different state endpoints** — that fanning is the chart's entire justification.

**Charts 11 + 12 build as one `hconcat` spec — clicking a state filters the beeswarm.**

**Chart 11 · MAP 4 — Australia hybrid** — ADVANCED · load-bearing
- **Title:** Two states take the lion's share
- **Subtitle:** State fill: international enrolments per 1,000 residents. Circles: enrolments by city.
- **Caption:** 11 · Choropleth with proportional symbols, Albers conic equal-area projection — an equal-area projection is required because the comparison is of areas and densities. Sources: Department of Education, PRISMS; ABS, National, state and territory population, Dec 2025.
- **Data:** `state_by_year.csv` + `state_population.csv` + `geo/au_university_cities.csv` + `geo/au_states.topo.json`
- **How:** `geoshape` with Sequential A fill, layered `circle` marks at city coordinates with `sqrt` size. `conicEqualArea`, parallels ≈ −18 and −36, rotate ≈ [−134, 0]. `params: [{name: "stateSel", select: {type: "point", fields: ["state"]}}]`.

**Chart 12 · Beeswarm** — advanced (surplus)
- **Title:** Some campuses are more international than others
- **Subtitle:** Each dot is one higher-education provider, 2024
- **Caption:** 12 · Beeswarm / unit chart — x encodes the overseas share of a provider's enrolments; dot area encodes total size. Murdoch (57%), Sydney (51%) and RMIT (50%) sit at one end; New England (6%) at the other. Figures are perturbed. Source: Department of Education, Higher Education Student Data.
- **Data:** `he_institution_2024.csv`
- **How:** `circle` with a force-free jitter (`yOffset` from a `random()` transform, or a computed dodge in Python). x = overseas share, size = total enrolments (`sqrt`), colour = Go8 / other public / private. Filter `stateSel`. Direct-label the four named extremes only.
- **Note:** exclude the aggregate "Non-University Higher Education Providers" row — it is a bucket, not a provider, and it would sit at 58% and mislead.

---

### Act 5 — "The shock, and what's at stake"
*Standfirst: the system has a rhythm, and policy has just interrupted it.*

**Chart 13 · Calendar heatmap** — ADVANCED · load-bearing
- **Title:** The rhythm, and the hole in it
- **Subtitle:** Monthly commencements, 2015–2025
- **Caption:** 13 · Calendar heatmap — colour encodes commencements in each month. The February and July intake peaks are visible every year except 2020–21. Monthly values derived by differencing year-to-date totals. Source: Department of Education, PRISMS.
- **Data:** `monthly_commencements.csv`
- **How:** `rect`, x = month (Jan–Dec, fixed order), y = year (descending), colour = Sequential A with `scale: {type: "sqrt"}`. Thin `--paper` stroke between cells.
- **Prep warning:** the source field is **YTD cumulative**. Monthly value = YTD(m) − YTD(m−1) within each year, with January taken as-is. Getting this wrong produces a heatmap that just gets darker left to right, which is a plausible-looking and completely wrong chart.

**Chart 14 · Horizontal export bar** — basic
- **Title:** Bigger than gold
- **Subtitle:** Australia's largest exports by value, 2024–25
- **Caption:** 14 · Bar chart, top 10 of Australia's 25 largest exports. Education-related travel services earned $53.6 billion in 2024–25, which put it fourth, behind iron ore, coal and natural gas and ahead of gold ($46.9 billion). Goods are on a recorded-trade basis and services on a balance-of-payments basis. Source: DFAT, *Australia's top 25 exports, goods & services 2024–25*, compiled from ABS data.
- **Data:** `exports_by_commodity.csv` (all 25 rows; filter to `rank <= 10` in the spec)
- **How:** horizontal `bar`, sorted descending, education bar in accent, all others `#B8B0A6`. Direct value labels at bar ends, no x-axis. Closes the loop with the standfirst.
- **Optional enrichment:** the CSV also has 2022–23 and 2023–24 values. Education grew from $36.3 billion to $53.6 billion over those two years while coal fell from $127.4 billion to $71.3 billion. That would make a good tooltip line or annotation, but don't build a second chart from it.

---

## Part D — The ledger

- **14 charts** (10 non-map + 4 maps) → requirement is ≥10 ✔
- **4 map idioms** at two scales, both with defensible equal-area projections → requirement is ≥3 ✔
- **Load-bearing advanced idioms (8):** waffle · per-capita choropleth · flow map · Australia hybrid map · Marimekko · dumbbell · country×field heatmap · calendar heatmap. **Do not cut any of these.**
- **Surplus advanced (3):** bump chart · proportional-symbol map · beeswarm. A marker reading the rubric literally could call the beeswarm a dot plot and the symbol map a bubble chart, so they are excluded from the count on purpose. Cut from here if weeks 9–11 run short.
- **Basic (3):** line, stacked area, bar. Each is the correct idiom for its task; none is counted as advanced.
- **Data sources combined (5):** DoE PRISMS · DoE Higher Education Statistics · World Bank population · ABS ERP · DFAT trade. Two of them (World Bank, ABS) are joined to do analytical work, not decoration.

---

## Part E — Data status

### Confirmed working

| File | Covers | Feeds |
|---|---|---|
| `Pivot_Basic_All_web.xlsx` | 3,512,371 records · 2005–2025 · all 12 months · Nationality × State × Sector × ProviderType · YTD enrolments + commencements | 2, 3, 4, 5, 6, 10, 11, 13 |
| `Pivot_Detailed_Latest_web2025.xlsx` | 755,700 records · 2019–2025 · Oct/Nov/Dec · adds Region, Broad/Narrow/Detailed field, Level of study | 7, 9, + the region lookup for 4 |
| `Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx` | 235,292 records · 2020–2024 · 46 institutions × citizenship × field × level | 1, 8, 12 |
| `31010do001_202512.xlsx` | ABS ERP by state, Table 3, 2005/2015/2024/2025 | 11 |
| `API_SP.POP.TOTL_DS2_en_csv_v2_446263.csv` + country metadata | World Bank population, 1960–2025, updated 13 July 2026. 217 countries once aggregates are dropped (keep rows where the metadata's `Region` is non-blank) | 5 |
| `data/exports_by_commodity.csv` (transcribed from DFAT PDF) | DFAT top 25 exports, goods & services, 2022–23 to 2024–25, A$ million | 14 |

`2024_Section2_All_Students.xlsx` and `2024_Section7_Overseas_Students.xlsx` are now **redundant**. The perturbed pivot gives the same information in flat form without subtracting one table from another. Keep them as a cross-check on the "1 in 3" figure; build nothing on them.

`australias-direction-of-goods-services-trade-calendar-years.xlsx` is also **unused**. It breaks exports down by partner country, not by product, so it can't feed chart 14. Leave it out of the footer's source list.

**World Bank resolved (v4.1).** The reveal holds up: Nepal sends roughly **290 students per 100,000 people**, against about 16 for China and 12 for India. Use the **2025** population column.

**Joining the names will need some manual work.** 172 of the 221 DoE nationality names match World Bank names exactly. 49 don't, and they fall into three groups:
- *Spelling differences*, which a hand-written dictionary in `50_lookups.py` fixes: Vietnam→Viet Nam, Iran→Iran, Islamic Rep., Korea, Republic of (South)→Korea, Rep., Hong Kong SAR→Hong Kong SAR, China, Macau→Macao SAR, China, United States of America→United States, Czech Republic→Czechia, Swaziland→Eswatini, Laos→Lao PDR, Kyrgyzstan→Kyrgyz Republic, Egypt, Gambia, Bahamas, Slovakia, Syria, Yemen, Venezuela, Somalia, East Timor, the two Congos, St Kitts/Lucia/Vincent, Micronesia, Gaza Strip and West Bank→West Bank and Gaza.
- *Historical or catch-all categories* to drop: Yugoslavia, Zaire, Netherlands Antilles, Other, United Kingdom (Other), United States (Territories).
- *Territories with no World Bank row* to drop from the per-capita map only: Anguilla, Cook Islands, Réunion, Falklands and similar. All of them have tiny student numbers.
- **Taiwan is the one that matters.** The World Bank doesn't publish it, but Taiwan sends real numbers of students. Hard-code its population (about 23.4 million, from Taiwan's national statistics office) and cite that source in the footer, or grey it out on Map 2 with a "no data" note. Don't silently drop it.

`2024_Section2`, `2024_Section7` and `31010do001` were uploaded a second time on 3 October. They're byte-identical to the first copies, so they don't change anything.

### One gap remaining (built in code, nothing to download)

**1. ~~World Bank population~~ Resolved 3 October 2026.** See above.

**2. ~~DFAT composition of trade~~ Resolved 3 October 2026.**
DFAT publishes this table only as a one-page PDF, which is why it was hard to find; there's no XLSX version. The table was transcribed into `data/exports_by_commodity.csv`: 25 rows, 2022–23 to 2024–25. Totals and shares were checked against the PDF.
- **Cite:** DFAT, *Australia's top 25 exports, goods & services 2024–25*. `https://www.dfat.gov.au/sites/default/files/australias-goods-services-by-top-25-exports-2024-25.pdf`
- Download the PDF into `raw/` too. If a tutor asks where the CSV came from, you can show them the original.
- Footnote (c) in the PDF says how student fees are classified in the services data changed from January 2020 because of COVID-19. Mention it in the caption only if you also use the 2022–23 values.

**3. Coordinate lookups — block charts 4, 10 and 11.** Nothing to download. These are built in `50_lookups.py`.
Three small CSVs you build once in `50_lookups.py`:
- `country_centroids.csv` — country name, ISO3, lat, lon. Derivable from the Natural Earth 110m TopoJSON, or from any public centroid list.
- `au_university_cities.csv` — city, lat, lon. Roughly 12 rows: Sydney, Melbourne, Brisbane, Perth, Adelaide, Canberra, Hobart, Darwin, Gold Coast, Newcastle, Wollongong, Geelong.
- An **ISO3 mapping from DoE nationality names to World Bank/Natural Earth names**. This is the fiddly one: "Hong Kong SAR", "Korea, Republic of (South)", "Taiwan", "China", "Macau" and the "not stated" categories all need manual handling. Build it once, print the unmatched rows, fix them by hand, and reuse the same file everywhere. Budget an hour and do it before you touch a map spec.

TopoJSON (`world-110m`, Australian states) loads from a CDN or is committed to `geo/` — no sourcing needed.

---

## Part F — Appendix: verified figures

Use these to check your prep pipeline. If `10_basic.py` reproduces them, the extraction is correct.

**Total international enrolments, December snapshot:**

| Year | Enrolments | | Year | Enrolments |
|---|---|---|---|---|
| 2005 | 346,419 | | 2016 | 708,863 |
| 2006 | 381,998 | | 2017 | 795,658 |
| 2007 | 452,889 | | 2018 | 872,600 |
| 2008 | 544,899 | | 2019 | 952,392 |
| 2009 | 632,969 | | 2020 | 879,874 |
| 2010 | 617,170 | | 2021 | 715,790 |
| 2011 | 554,484 | | 2022 | 742,074 |
| 2012 | 513,292 | | 2023 | 968,966 |
| 2013 | 524,322 | | 2024 | 1,088,612 |
| 2014 | 586,343 | | 2025 | 1,058,040 |
| 2015 | 641,750 | | | |

**Top source countries, 2024:** China 221,102 · India 180,509 · Nepal 86,858 · Philippines 56,653 · Colombia 54,439 · Vietnam 48,918 · Thailand 35,815 · Brazil 34,997 · Pakistan 32,409 · Indonesia 30,453 · Sri Lanka 23,449 · Bangladesh 22,118.

**Higher education, 2024 (perturbed):** Overseas 589,355 · Domestic 1,086,722 · Total 1,676,077 · Overseas share **35.16%**.

**Overseas share by provider, 2024 (perturbed):** Murdoch 57.1% · Sydney 50.8% · RMIT 50.1% · UNSW 46.7% … New England 6.0% · Avondale 7.9%.

**Sector enrolments, 2005 → 2018:** Higher Education 178,791 → 398,363 · VET 51,012 → 243,022 · ELICOS 65,838 → 154,655 · Schools 25,115 → 26,708 · Non-award 25,663 → 49,852.

---

## Part G — Change log

- **v1** — original integrated proposal, 16 charts.
- **v2** — added DoE Higher Education Statistics as a source; paired specs instead of JS signal wiring; moved the sector area chart into Act 1; Map 4 tint changed to per-1,000 residents; advanced ledger corrected to eight unambiguous idioms.
- **v3** — slopegraph dropped (two endpoints imply a straight path the data doesn't have); flow map moved to open Act 4 and re-pointed at origin→state; bump chart moved into Act 2 and re-pointed at source countries; UNESCO rank demoted from a chart to a header numeral.
- **v4** — written against the real data. Hook corrected from "1 in 4" to "more than 1 in 3" (35.2%); chart 2 series starts 2005; Act 5 gains the 2025 decline as its ending; region lookup derived from the detailed workbook instead of a new source; chart 14 flagged as blocked on a wrong trade file; palette, type scale and layout grid fixed to specific values; verified figures appendix added.
- **v4.1** (3 October) — World Bank population received and verified. Per-capita reveal confirmed: Nepal ≈290 per 100k vs China ≈16. Name-join issues catalogued, and Taiwan flagged for manual handling. Remaining gaps: DFAT commodity table and coordinate lookups.
- **v4.2** (3 October) — DFAT top-25 exports found; it's only published as a PDF, so it was transcribed to CSV. The chart 14 title "Bigger than gold" is confirmed: education $53.6 billion vs gold $46.9 billion, ranked 4th. The direction-of-trade workbook is marked unused. All external data is now in hand.
