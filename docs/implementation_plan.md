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

## Part B — The design system (v5: "Entry Stamp × Arrivals")

**v5 replaces the v4 "editorial" look**, which was rejected as generic: beige paper, Source Serif with Inter, uppercase kickers, charts in boxed cards. It was a template that could have been about any topic. Following DV1, the new system takes its whole identity from the subject. **The paperwork of crossing a border** (passport security paper, ink stamps, visa field labels, the machine-readable zone) **meets the airport** (split-flap arrivals board, condensed signage type). Light background throughout.

### The rule every ornament obeys
**Nothing is purely decorative.** Every stamp holds a real figure, every flap tile shows real data, and the passport code lines carry real ICAO 9303 check digits. Decoration sits *around* charts and never replaces a mark that has to be read exactly. That was DV1's postbox-lollipop lesson.

### Colour (all sets validated with the dataviz palette checker on `--paper`)

| Role | Hex | Meaning |
|---|---|---|
| Paper | `#EEF1EC` | passport security paper: pale, cool |
| Ink | `#14213D` | passport-cover navy; all primary text, annotation rings |
| Ink-muted | `#4D5A70` | secondary text, axes (6.2:1) |
| Rule | `#C9D0D8` | gridlines (dashed), hairlines |
| **Stamp red** | `#C8371F` | **international students**: the subject; headline keywords |
| **Ink blue** | `#2F5FA7` | **domestic students** where compared; also the guilloche print |
| Other | `#9A9C94` | everything that isn't the point |

- **Sector (adjacent pairs, all pass):** Higher Education `#2F5FA7` · VET `#C8371F` · ELICOS `#6E4BA8` · Schools `#2E8754` · Non-award `#9A9C94`.
- **Region (all pairs, for maps):** South & Central Asia `#C8371F` · East & SE Asia `#2F5FA7` · Americas **flap amber** `#C99400` · Rest of world grey. Amber's contrast is under 3:1, so map circles get a 1px ink outline and direct labels.
- **Sequential:** counts use an ink-blue ramp `#E6ECF5 → #1C3C70`; rates use a stamp-red ramp.

### Type: three voices

| Voice | Face | Used for |
|---|---|---|
| Display (the printed document) | **Zilla Slab** 600/700, sentence case | page title, act headlines, chart titles, stamp numerals |
| Field (the visa) | **IBM Plex Mono** 400–600 | field labels, subtitles, axes, annotations, flap tiles, tooltips, MRZ |
| Text (reading) | **IBM Plex Sans** 400/600 | body, deck, captions |

Plex Sans and Plex Mono are one family, so the two small voices sit together and the display face is the deliberate contrast. The heavy slab also carries on DV1's slab headlines, which scored HD for typography. (Big Shoulders Display was tried in v5.0 and dropped in v5.1.) **Headline keywords take the colour of the marks they refer to**, so the title works as the legend (DV1's best-scoring device).

### Ornaments (`css/ornaments.css`, `js/ornaments.js`)
- **Guilloche:** generated interference-wave security print behind the header and footer.
- **Split-flap tiles:** the headline figure 1 058 040 and the header's departures-style board. Thousands are separated by a **wider gap**, not a comma tile (v5.2). Each tile is built like the real mechanism: fixed top and bottom halves, a hinge line with notches. A flip is two moving leaves: the old character's top leaf folds down (0 → −90°) and darkens as it turns away from the light, then the new character's bottom leaf falls into place (90° → 0). Each tile steps through its own character drum (blank, 0–9 or A–Z) from a random start until it reaches its character, so tiles stop at different moments.
- **Ink stamps:** rect and round shapes in four inks, roughened by an SVG ink filter, and they land with a "thunk" on first view. One per act, each holding a figure: ×3.1, 1 in 51, 41%, 69%, −2.8%.
- **Machine-readable zone:** two TD3 passport code lines in the header and visa-style lines in the footer, with real check digits.
- **Act labels as numbered visa fields:** 01 Entries · 02 Country of citizenship · 03 Course of study · 04 Address in Australia · 05 Conditions.
- **Captions** sit under a perforated tear line, like a boarding pass. **Tooltips** are boarding-pass stubs: ink border, heavy left edge, mono keys.
- **Footer** as the passport's observations page: holder, authority, date of issue and sources as data fields.
- All motion respects `prefers-reduced-motion`.

### Layout
Single column, one left sight-line (DV1's weakest mark: Credit for sightlines, centred text). Act gap 136px and chart gap 72px, up from 96 and 48, after DV1's white-space feedback. Charts sit directly on the paper, with no boxes. Headlines max 19ch; prose max 60ch. Below 900px everything stacks and the header stamp drops below the board.

### Writing voice (from DV1)
Short declarative claims in pairs ("Bigger than gold. Easier to lose."), one human-scale comparison per act (Bhutan: if Australia did the same, more than half a million Australians would be studying in one foreign country), and an ending that returns to the opening ("the export that walks in" → "Education out-earns gold"). **Proofread with Code Spell Checker (en-AU)**: grammar was a Distinction in DV1, from typos.

### Detail backlog: themed touches for charts still to build
- **Country labels as three-letter codes in flap tiles** (CHN, IND, NPL), as on the header board, on the bump chart's line ends and the heatmap's rows. The ISO3 codes already exist in `country_lookup.csv`.
- **Calendar heatmap as an arrivals board:** month columns headed like a departures board, cells as tiles with tile gaps; the 2020–21 rows visibly "blank".
- **Flow map as an airline route map:** thin ink coastlines, routes with round caps, origin dots like airport markers, destination labels as city codes (SYD, MEL, BNE, PER, ADL, CBR, HBA, DRW).
- **Waffle squares as stamp cells:** overseas squares filled stamp red, domestic as ink-blue outlines, like unstamped boxes on a form.
- **Map legends styled as a stamp** (a bordered mono key), never as a default Vega legend.
- **Page numbers in the act margins** ("PAGE 04"), as on visa pages.
- **Print stylesheet:** the page prints as a passport booklet, one act per page.

## Part C — The fourteen charts

Numbering matches `charts/NN-*.vl.json` and the sketch panels.

### Header band

Title **STUDYING DOWN UNDER**. Standfirst: one sentence establishing that this is Australia's largest services export and that the people behind the number are 1.06 million individuals from 200-plus countries.

Header figures (v5: the main figure is split-flap tiles 1,058,040 plus a departures board of four countries; "1 in 3" is a round stamp) (v4.6: the UNESCO "#3 destination" figure was dropped because it was never verified against a source in hand; it's replaced by a figure already in the data):
- **1 in 3**: students at Australian universities and colleges is from overseas (35.2%, `he_summary_2024.csv`)
- **$53.6bn**: earned from education in 2024–25, Australia's fourth-largest export (`exports_by_commodity.csv`)

---

### Act 1 — "A world-class classroom"
*Standfirst: the scale of the thing, and the three times it broke.*

**Chart 1 · Waffle / isotype grid** — ADVANCED · load-bearing
- **Title:** More than one in three
- **Subtitle:** Share of all Australian higher-education students who are overseas students, 2024
- **Caption:** 1 · Isotype grid. Each square is 1% of the 1,676,077 students enrolled in Australian higher education in 2024, and 35 of them are overseas students. At universities alone (excluding private colleges) the share is 33%. Figures are perturbed for confidentiality. Source: Department of Education, Higher Education Student Data, 2024.
- **Data:** `he_summary_2024.csv`, row "All higher-education providers" (35.2%). The "Universities only" row (32.7%) is for the caption. Either way "one in three" is accurate; "more than one in three" applies only to all providers, so keep the headline and the scope consistent.
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
- **Caption:** 4 · Proportional-symbol map, Equal Earth projection — circle area encodes enrolments; colour encodes region (South & Central Asia, East & South-East Asia, Americas, rest of world). Source: Department of Education, PRISMS.
- **Data:** `country_2025.csv` (has `enrolments`, `region_group`, `lat`, `lon` already joined) + `geo/world_countries.topo.json` (layer `countries`) for the basemap.
- **How:** `geoshape` basemap in `#F0EDE7` with `#E2DCD3` borders, `equalEarth` projection rotated so the Pacific isn't split. `circle` marks at centroids; **size scaled by `sqrt`** (area, not radius — the bubble-plot guidance is explicit), `opacity: 0.85`, thin white stroke. Colour = the 3-hue + grey region palette.

**Chart 5 · MAP 2 — Per-capita choropleth** — ADVANCED · load-bearing
- **Title:** …and where it's a big deal
- **Subtitle:** Enrolments in Australia per 100,000 people in the home country, 2025
- **Caption:** 5 · Choropleth, Equal Earth projection. Bhutan's enrolments in Australia equal almost 2% of its population (1,943 per 100,000), and Fiji's and Nepal's are 727 and 302. China sends the most students but ranks 32nd by rate (16 per 100,000); India ranks 39th (12.5). Countries under 200,000 people are shaded but not ranked; Taiwan's population is from its Ministry of the Interior because the World Bank doesn't publish it. Sources: Department of Education, PRISMS; World Bank, SP.POP.TOTL (2025).
- **Data:** `country_2025.csv` (`per_100k`, `small_population`, `rank_per_100k`), looked up onto `geo/world_countries.topo.json` by `iso3`. Cook Islands and St Helena have no population figure and stay grey.
- **Changed in v4.5:** the headline is now Bhutan rather than Nepal. Earlier versions expected Nepal to have the highest rate; it's third. Annotate Bhutan, Nepal and China directly on the map.
- **How:** `geoshape`, colour = Sequential B (ochre), **quantile or threshold bins, not linear** — the distribution is severely right-skewed and a linear ramp will show one dark country and 200 pale ones. Same projection and size as Map 4 so the pair reads as a genuine comparison.
- **This is the analytical core of the page.** It is the chart that makes the second data source do real work rather than sit there satisfying a rule.

**Chart 6 · Bump chart** — advanced (surplus)
- **Title:** Below the top two, everything moved
- **Subtitle:** Rank among source countries, positions 3–15, 2010–2025. China and India held first and second place in every year.
- **Caption:** 6 · Bump chart. It encodes rank, not volume. Nepal rose from 7th to 3rd, the Philippines from 22nd to 4th and Bangladesh from 19th to 7th, while South Korea fell from 3rd to 14th. Source: Department of Education, PRISMS.
- **Data:** `nationality_by_year.csv` (already has a `rank` column). Filter to countries that reached the top 15 in any year from 2010 onward, then clip the y-axis to ranks 3–15.
- **How:** `line` + `point` per country. y = rank, **reversed scale, 3 at top**, integer ticks. Colour four lines (Nepal, Philippines and Bangladesh in accent tones, Korea in counterpoint teal) and grey the rest; direct-label the four at both ends. No legend. China and India go in the subtitle rather than on the chart: two flat lines at the top would add data-ink without adding information.
- **Changed in v4.3:** earlier versions expected India to overtake China. The data shows it never did, in any year, so the chart now focuses on ranks 3–15, where the real changes happened.

---

### Act 3 — "What they come to study"
*Standfirst: your passport predicts your degree more than you'd expect.*

**Chart 7 · Marimekko / mosaic** — ADVANCED · load-bearing
- **Title:** Four in ten study business or IT
- **Subtitle:** Enrolments by field of study, split by sector, 2025
- **Caption:** 7 · Marimekko chart. Column width encodes each field's share of all enrolments and the vertical split shows which sector teaches it. Business & Commerce alone is 29%, taught almost equally by universities and VET colleges; IT adds 12%. English-language courses are shown as their own field, although the Department files them under Society & Culture. Source: Department of Education, PRISMS (detailed).
- **Data:** `field_by_sector_2025.csv`, 11 field columns, rectangle edges already computed (`x0`, `x1`, `y0`, `y1`, all 0–1).
- **How:** `rect` with `x: x0`, `x2: x1`, `y: y0`, `y2: y1`; colour = sector categorical. White 1–2 px stroke between rectangles. Label the columns along the top. Labels for narrow columns (under about 5%) go in the tooltip only.
- **Field regrouping (v4.4, in `prep/labels.py`):** ELICOS gets its own "English language" column, and school and foundation students form "School & other". Sciences, Creative Arts and Agriculture merge into one column; separately they'd be too narrow to read.

**Chart 8 · Dumbbell plot** — ADVANCED · load-bearing
- **Title:** The two cohorts study different things
- **Subtitle:** Share of enrolments in each field: domestic vs overseas students, higher education, 2024
- **Caption:** 8 · Dumbbell plot. Each row compares a field's share of domestic enrolments (teal) with its share of overseas enrolments (ochre). A third of overseas students study business (33.7%), against one in seven domestic students (14.5%). Domestic students are far more likely to study health (20.9% vs 8.9%) or society and culture (23.2% vs 10.2%). Combined degrees count in both fields. Figures are perturbed. Source: Department of Education, Higher Education Student Data, 2024.
- **Data:** `he_field_citizenship_2024.csv`: 10 rows, already sorted by `gap_pp`, from most overseas-leaning to most domestic-leaning.
- **How:** `rule` from domestic to overseas share, then two `circle` marks. Rows sorted by gap size, not alphabetically. Colour-coded words in the subtitle instead of a legend.

**Chart 9 · Country × field heatmap** — ADVANCED · load-bearing
- **Title:** Your passport predicts your degree
- **Subtitle:** Share of each country's enrolments by broad field, top 10 source countries, 2025
- **Caption:** 9 · Heatmap. Colour encodes each field's share *within* a country's enrolments, so rows are comparable despite very different totals. A third of Colombian and Brazilian enrolments are English-language courses. Bangladeshi students lean heavily towards IT (38%), Pakistani students towards engineering and architecture (39% combined), and Filipino students towards hospitality and community services. Source: Department of Education, PRISMS (detailed).
- **Data:** `country_field_2025.csv`: 10 countries × 11 fields, with `share` already normalised within each country.
- **Annotate three cells:** Brazil × English (33%), Bangladesh × IT (38%), Indonesia × Business (43%). These cells carry the title.
- **How:** `rect`, colour = Sequential A. **Normalise within row** — without it the map just re-shows that China and India are large. Countries sorted by total; fields in a fixed order shared with chart 7.

---

### Act 4 — "Where they land"
*Standfirst: different origins land in different states. The map that shows it is the hinge of this page.*

**Chart 10 · MAP 3 — Flow map** — ADVANCED · load-bearing
- **Title:** Different origins, different states
- **Subtitle:** Enrolments from the 12 largest source countries to each state's capital, 2025 (flows under 500 omitted)
- **Caption:** 10 · Flow map. Line thickness encodes enrolments and colour encodes origin region. 47% of Chinese students are in NSW, while 43% of Indian students are in Victoria; 62% of Nepali students are in NSW. Straight lines, Equal Earth projection. Source: Department of Education, PRISMS.
- **Data:** `flows_2025.csv`: 75 rows with `origin_lat/lon`, `dest_lat/lon` (state capital), `region_group` and `share_of_origin`, already filtered to the top 12 origins and flows of 500 or more.
- **How:** `rule` marks with `longitude`/`latitude` and `longitude2`/`latitude2`. `strokeWidth` scaled by `sqrt`, `opacity: 0.55`, `strokeCap: "round"`. Filter to the top 12 origins and drop flows below a threshold or it becomes a hairball. **The lines must visibly fan to different state endpoints** — that fanning is the chart's entire justification.

**Charts 11 + 12 build as one `hconcat` spec — clicking a state filters the beeswarm.**

**Chart 11 · MAP 4 — Australia hybrid** — ADVANCED · load-bearing
- **Title:** Two states take the lion's share
- **Subtitle:** State fill: international enrolments per 1,000 residents, 2025. Circles: overseas students at each university, 2024.
- **Caption:** 11 · Choropleth with proportional symbols, Albers conic equal-area projection. An equal-area projection is needed because the map compares areas and densities. Sources: Department of Education, PRISMS and Higher Education Student Data; ABS, National, state and territory population, Dec 2025.
- **Data:** `state_2025.csv` (fill: `per_1000`) + `he_institution_geo_2024.csv` (circles: `overseas`, `lat`, `lon`) + `geo/au_states.topo.json` (layer `states`, joined on `state`).
- **Verified (v4.5):** NSW and Victoria hold 69% of enrolments (403,139 and 322,347), but by rate the ACT (44.6 per 1,000) is level with NSW (46.7) and Victoria (45.3). Say this in the caption: the rate tells a different story from the raw count.
- **Changed in v4.4:** no source has enrolments by city, so the circles are now **universities at their main campus**, sized by overseas enrolments. The circles on Map 4 and the dots in the beeswarm are now the same 43 providers, so clicking a state highlights the same institutions in both views. `au_university_cities.csv` is replaced by `au_university_locations.csv` (43 rows: institution, lat, lon).
- **How:** `geoshape` with Sequential A fill, layered `circle` marks at city coordinates with `sqrt` size. `conicEqualArea`, parallels ≈ −18 and −36, rotate ≈ [−134, 0]. `params: [{name: "stateSel", select: {type: "point", fields: ["state"]}}]`.

**Chart 12 · Beeswarm** — advanced (surplus)
- **Title:** Some campuses are more international than others
- **Subtitle:** Each dot is one higher-education provider, 2024
- **Caption:** 12 · Beeswarm / unit chart — x encodes the overseas share of a provider's enrolments; dot area encodes total size. Murdoch (57%), Sydney (51%) and RMIT (50%) sit at one end; New England (6%) at the other. Figures are perturbed. Source: Department of Education, Higher Education Student Data.
- **Data:** `he_institution_geo_2024.csv` (same rows as `he_institution_2024.csv` plus campus coordinates, so Map 4 and the beeswarm share one dataset): 43 providers, with `state` (home state, used by the filter), `group` (Group of Eight / Other public / Private) and `short_name` for labels. The bucket rows are already excluded. ACU reports all enrolments as "Multi-State", so it's assigned to NSW, its head-office state.
- **How:** `circle` with a force-free jitter (`yOffset` from a `random()` transform, or a computed dodge in Python). x = overseas share, size = total enrolments (`sqrt`), colour = Go8 / other public / private. Filter `stateSel`. Direct-label the four named extremes only.
- **Note:** exclude the aggregate "Non-University Higher Education Providers" row — it is a bucket, not a provider, and it would sit at 58% and mislead.

---

### Act 5 — "The shock, and what's at stake"
*Standfirst: the system has a rhythm, and policy has just interrupted it.*

**Chart 13 · Calendar heatmap** — ADVANCED · load-bearing
- **Title:** The rhythm, and the hole in it
- **Subtitle:** Monthly commencements, 2015–2025
- **Caption:** 13 · Calendar heatmap — colour encodes commencements in each month. The February and July intakes recur every year. In 2020 the February intake still arrived (81,000) because borders closed in March; the July intake halved, and 2021 stayed low all year. Monthly values derived by differencing year-to-date totals. Source: Department of Education, PRISMS.
- **Verified values (v4.3):** February intake: 92,876 (2019) → 81,112 (2020) → 47,699 (2021) → 115,034 (2024) → 88,816 (2025). July intake: 96,796 → 50,926 → 43,551 → 110,593 → 85,639. The fall from 2024 to 2025 shows up in both intakes, which supports Act 5's ending.
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

### No gaps remaining

**1. ~~World Bank population~~ Resolved 3 October 2026.** See above.

**2. ~~DFAT composition of trade~~ Resolved 3 October 2026.**
DFAT publishes this table only as a one-page PDF, which is why it was hard to find; there's no XLSX version. The table was transcribed into `data/exports_by_commodity.csv`: 25 rows, 2022–23 to 2024–25. Totals and shares were checked against the PDF.
- **Cite:** DFAT, *Australia's top 25 exports, goods & services 2024–25*. `https://www.dfat.gov.au/sites/default/files/australias-goods-services-by-top-25-exports-2024-25.pdf`
- Download the PDF into `raw/` too. If a tutor asks where the CSV came from, you can show them the original.
- Footnote (c) in the PDF says how student fees are classified in the services data changed from January 2020 because of COVID-19. Mention it in the caption only if you also use the 2022–23 values.

**3. ~~Coordinate lookups~~ Resolved 4 October 2026.** `prep/50_lookups.py` plus the committed files in `geo/` (provenance in `geo/README.md`):
- `world_countries.topo.json`: Natural Earth 1:50m, simplified to 119 KB. 1:110m was rejected because it has no Hong Kong, Singapore, Macau or Mauritius.
- `au_states.topo.json`: 28 KB. `au_state_capitals.csv`: flow-line endpoints.
- `country_points.csv`: one point per country, with three hand overrides (Malaysia, Indonesia, New Zealand).
- `au_university_locations.csv`: 43 main campuses.
- All 220 Department of Education nationality names resolve to ISO3; 99.996% of 2025 enrolments are placed on a country, and the remaining 47 are in "Other".

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

## Part H: As built (v5.2, 7 October 2026)

All 14 charts are built, rendered and checked at 390, 800 and 1280px: 14/14 draw, no console errors, no horizontal overflow. Where the build differs from Part C:

| Fig. | File | What changed in the build, and why |
|---|---|---|
| 01 | `01-waffle.vl.json` | Squares drawn as **form boxes**: overseas stamped red, domestic inked blue outlines. Totals sit beside the grid in HTML (slab numerals "35 in 100", "65 in 100"). |
| 02 | `02-total-line.vl.json` | Unchanged from v5.1. |
| 03 | `03-sector-area.vl.json` | Crosshair tooltip lists all five sectors for the hovered year (pivot); "VET ×4.1 · 2005–09" annotation inside the band. |
| 04 + 05 | `04-origins-symbols`, `05-origins-percapita` | **Two separate specs**, not one hconcat, so they stack on phones. Linked hover through a small bridge in `js/embed.js` (`data-link` attributes). Map 2 labels BTN, NPL, CHN, FJI and **MNG** (237 per 100k: dark enough to be mistaken for China without a label), each with an atlas-style leader. Legends are HTML keys, not Vega legends. Height follows width (`usermeta.aspect`). |
| 06 | `06-bump.vl.json` | Line ends carry **ISO codes on navy flap tiles**; story lines also carry the name. PHL and BGD entry notes at the bottom edge. |
| 07 | `07-marimekko.vl.json` | Field names run up inside each column; each field's share sits above it. |
| 08 | `08-dumbbell.vl.json` | Values labelled where the gap is over 5 points; the subtitle says "sorted by gap" (DV1 feedback: unexplained sort order). |
| 09 | `09-country-field-heat.vl.json` | Values printed in cells of 10% or more; the three cells the title relies on are ringed with dashed stamp red. Column headers turn vertical below 640px. |
| 10 | `10-flow-map.vl.json` | **Projection changed** from world Equal Earth to **azimuthal equidistant centred on 110°E, framed on the region the routes cross**. On a world map Australia is about 150px wide and the routes could not visibly fan out to different capitals, which is the chart's whole point. Colombia and Brazil enter dashed from the right edge, "via the Pacific". Routes under 1,500 omitted (60 routes, 98.4% of mapped volume). Origins on flap tiles, capitals as airport codes (SYD MEL BNE PER ADL CBR HBA DRW). |
| 11 + 12 | `11-australia.vl.json`, `12-beeswarm.vg.json` | Separate specs, linked both ways: click a state **or a dot** to pick a state, double-click to clear. **Chart 12 is plain Vega**, because a true beeswarm needs Vega's force transform (collision + attraction to x), which Vega-Lite does not expose. Map state labels show code and rate per 1,000. |
| 13 | `13-calendar-heat.vl.json` | Built as an arrivals board: FEB and JUL flagged in red in the header row, their values printed on the tiles, July 2020 ringed. |
| 14 | `14-export-bar.vl.json` | Education in stamp red, **gold in amber** (the title compares the two), all else neutral; values at bar ends; note "up from $36.3bn in 2022–23". |

**Vega-Lite gotcha worth knowing for the interview:** a top-level `encoding` is inherited by every layer, including its validity filter. A layer with its own small data (an annotation band, aggregated labels) that lacks those fields is silently filtered to nothing. Either give such rows the fields (chart 2's border band) or move the encodings into the layers (chart 7).

---

## Part G — Change log

- **v1** — original integrated proposal, 16 charts.
- **v2** — added DoE Higher Education Statistics as a source; paired specs instead of JS signal wiring; moved the sector area chart into Act 1; Map 4 tint changed to per-1,000 residents; advanced ledger corrected to eight unambiguous idioms.
- **v3** — slopegraph dropped (two endpoints imply a straight path the data doesn't have); flow map moved to open Act 4 and re-pointed at origin→state; bump chart moved into Act 2 and re-pointed at source countries; UNESCO rank demoted from a chart to a header numeral.
- **v4** — written against the real data. Hook corrected from "1 in 4" to "more than 1 in 3" (35.2%); chart 2 series starts 2005; Act 5 gains the 2025 decline as its ending; region lookup derived from the detailed workbook instead of a new source; chart 14 flagged as blocked on a wrong trade file; palette, type scale and layout grid fixed to specific values; verified figures appendix added.
- **v4.1** (3 October) — World Bank population received and verified. Per-capita reveal confirmed: Nepal ≈290 per 100k vs China ≈16. Name-join issues catalogued, and Taiwan flagged for manual handling. Remaining gaps: DFAT commodity table and coordinate lookups.
- **v4.2** (3 October) — DFAT top-25 exports found; it's only published as a PDF, so it was transcribed to CSV. The chart 14 title "Bigger than gold" is confirmed: education $53.6 billion vs gold $46.9 billion, ranked 4th. The direction-of-trade workbook is marked unused. All external data is now in hand.
- **v4.3** (3 October) — `pivotcache.py` and `10_basic.py` were built and validated against the appendix figures. Three findings changed the plan. (1) China and India held ranks 1 and 2 in every year, so the bump chart now covers ranks 3–15 (Nepal, the Philippines and Bangladesh rising; Korea falling). (2) The 2020 February intake largely arrived before borders closed; the gap starts with July 2020, so the chart 13 caption was rewritten. (3) The flow-map premise is confirmed: in 2025 China enrolments are concentrated in NSW (106,094 vs 67,069 in VIC), India's in VIC (78,367 vs 44,632 in NSW), and Nepal's in NSW (55,279).
- **v4.4** (3 October) — `labels.py`, `20_detailed.py` and `30_higher_ed.py` were built and validated. The detailed workbook's Dec 2025 total matches the basic one (1,058,040). Changes: (1) English-language courses and school students are separated from the official field categories, and small fields are merged (11 display fields). (2) Chart 7 is retitled "Four in ten study business or IT" to match the data (29% + 12%). (3) Chart 1 scope is clarified: 35.2% for all providers, 32.7% for universities only. (4) Captions for charts 8 and 9 now use real figures. (5) Map 4 circles are now universities, not cities, because no source has city-level data; this also links Map 4 to the beeswarm.
- **v4.5** (4 October) — `50_lookups.py` and `geo/` were built and validated. All data prep is complete. Findings: (1) **Bhutan, not Nepal, has the highest per-capita rate** (1,943 per 100k vs Nepal's 302, 3rd after Fiji), so chart 5 is re-captioned around Bhutan. The small-population cutoff for ranking is set at 200,000 so Bhutan counts but Nauru doesn't. (2) Flow map confirmed: China 47% NSW, India 43% VIC, Nepal 62% NSW. (3) By rate per 1,000 residents, the ACT matches NSW and VIC; the Map 4 caption now says so. (4) Maps use pre-joined CSVs (`country_2025`, `flows_2025`, `state_2025`, `he_institution_geo_2024`) so the Vega-Lite specs contain no lookups beyond geometry.
- **v4.6** (4 October) — Page skeleton and chart 2 built. (1) All categorical palettes re-picked and validated (see Part B). (2) Regions regrouped to 3 + grey in `labels.py`, so 20 and 50 must be re-run. (3) The UNESCO header figure was replaced by $53.6bn. (4) Chart titles, subtitles and captions live in the HTML, not the Vega specs, so every chart shares the page's typography. (5) Chart 2's annotations switch to short labels below 520px so they don't collide on phones. (6) Charts attach with a `data-spec` attribute on their slot; `manifest.js` is dropped.
- **v5.0** (7 October) — **Visual identity rebuilt** after DV1 review (DV1 scored 20.78/25: HD everywhere except sightlines, Credit, and grammar, Distinction). New system "Entry Stamp × Arrivals" (Part B): security paper, ink stamps, visa fields, MRZ with real check digits, split-flap figures, Big Shoulders Display with IBM Plex Mono and Sans. Palettes re-picked from stamp inks and re-validated. Every headline rewritten as a claim with colour-coded keywords. Chart 2 restyled: border-closure band (20 Mar 2020 – 15 Dec 2021), dashed-ring annotations in mono, boarding-pass tooltip. Page title is now "The Export That Walks In". Author: Leo Dietz Sanz.
- **v5.1** (7 October) — Headline face changed back to **Zilla Slab** (sentence case) from Big Shoulders Display. Split-flap redone so every character, commas included, has its own tile, with flap shading, hinge line and notches.
- **v5.2** (7 October) — Split-flap rebuilt as a true two-leaf mechanism, with thousands separated by gaps instead of comma tiles. **All remaining charts built** (1, 3–14); see Part H for how the build differs from the plan. `js/embed.js` gained a linked-view bridge and aspect-ratio sizing; the chart grid collapses to one column under 900px.
- **v5.3** (13 October) — Review fixes. (1) Less white space: acts 136→104px apart, header to act 1 104→56px; the act stamp now sits in the intro's right third at a larger size instead of floating in the margin. (2) "Fig. NN · idiom" labels removed from captions and map panels. (3) Map 1 colours its circles by a group derived in the spec (pattern on `region_group` with an ISO fallback), so label variants no longer leave circles unfilled; Maps 1–2 outline Australia as the destination, and Map 2 gains a grey base layer so no-data countries still draw. (4) Bump chart pins ranks below 15th to a shaded "below 15th" strip instead of clipping lines at the frame. (5) **Flow map rebuilt**: new `prep/60_flow_paths.py` writes `data/flow_paths_2025.csv`. Each origin gets one trunk as wide as its students, which splits Sankey-style into one branch per capital; China and India are shown by default, and clicking a tile follows another country (shift-click to compare). The largest branch is labelled with its share.
- **v5.4** (13 October) — Second review round. (1) VET and ELICOS defined in the chart 3 caption; chart 3's legend moved into its subtitle. (2) The 2025 fall is explained: chart 2 annotation, caption and act 1 prose (visa fee $710 → $1,600 in July 2024 and $2,000 in July 2025; caps on new students via Ministerial Direction 111, Dec 2024; ELICOS −35%, new enrolments −15% in our data). (3) Act stamps back to tight proportions and set beside the paragraph instead of in an empty right-hand column. (4) Paired charts share edges: half-width figures sit on a CSS subgrid (title, plot and caption rows line up); waffle and area chart share top and bottom; heatmap and bar chart share top and bottom; the beeswarm is centred on the state map's midline (measured offsets in layout.css). (5) Maps 1 and 2 stacked, each full width; map 1's circles scale with width and its nine largest senders are labelled. (6) Heatmap: single-line column labels; every row's largest field is ringed (ink = business, dashed red = the four exceptions); title now leads with "nearly everyone comes for business". (7) **Flow map rebuilt as ribbons** (`prep/60_flow_paths.py` → `flow_ribbons_2025.json`, `flow_origins_2025.csv`): filled polygons, so branches exactly tile the trunk; 20 origins; a split-flap **departures board** beside the map toggles countries with a click (up to five, each in its own ink; status flaps to ON MAP). (8) **State map zooms**: tick-boxes styled as the visa form's address field (or a click on the map) refit the projection to the state; `prep/70_campus_dodge.py` precomputes non-overlapping circle positions and label columns for each view, with leader lines to the true campus.
- **v5.5** (14 October) — Third review round. (1) **Act stamps replaced by visa pages**: each act intro now has a printed panel of three real figures (visa-page fields) beside the paragraph, with the act's stamp pressed over its right side; no more stamp floating in empty space. Act 3 stamp corrected to 40% (28.9% + 11.6%). (2) Dumbbell: rows sorted by the average of the two shares; every value labelled; subtitle and caption say it is higher education only and reconcile its 52% business + IT with the 40% across all sectors. (3) Heatmap: only the four exceptions are ringed (dashed red). (4) Bump chart: every end label carries the country name (grey for non-story lines). (5) Chart 2's 2025 note cut to "visa fees up, new caps"; details live in the caption and the Act 5 visa page. (6) Captions and keys no longer describe how the charts were built. (7) Flow map trunks are curves that arrive at their own "gate" on an arc around south-east Australia, so neighbouring routes run side by side. (8) State map: zoom is animated (js/boards.js tweens the fit box and blends positions/sizes); frames fit all four corners and edge midpoints so WA and VIC no longer clip; providers with 15,000+ overseas students stay exactly on their campus, smaller ones are nudged; no labels or leader lines. (9) Beeswarm click-to-pick and double-click-to-clear fixed.
- **v5.6** (14 October) — Fourth review round. (1) A double-click on either the map or the beeswarm clears the state pick for both (js/embed.js listens on every linked chart). (2) Beeswarm labels removed; the beeswarm block (label, chart, key) is centred on the map's midline. (3) Map circles: new priority order (ease of reading, no overlap, then accuracy). Every circle is moved just clear of its neighbours in every view, with a hairline back to its campus when it moved more than a few pixels; positions are now computed in the chart's real conic projection and framing, so they hold in Melbourne as well as Sydney and Perth. (4) Visa pages start level with each section's field line; vertical spacing tightened (acts 88 px apart). (5) **New chart 15, split bars**: each of the 20 largest source countries as a 100% bar split by state, grouped by the state that takes most of its students. Chosen over a Sankey (bands sized by head-count make small countries unreadable), small-multiple maps and a heatmap (less precise for parts of a whole). Linked to the departures board: picked countries are framed in their ink, and clicking a bar toggles the country on the board and flow map.
- **v5.7** (14 October) — Fifth review round, and a narrative thread. (1) **New thread, "study or business?"**: the header deck, each act's paragraph and the state-map caption now carry one line on education as an export business; **new Act 6, "Purpose of visit"**, with chart 16 (share of international students taught by private providers, by sector, 2005–2025: 35% → 59% overall, 97% in VET) and chart 17 (overseas share by university course level, 2020 vs 2024: coursework master's cross 50%), closing on a reader's "declaration" that poses the question and sets out both cases. New prep script `40_business.py` (provider type from Pivot_Basic; course level from the HE pivot). (2) Heatmap extended to the 20 largest countries; 14 of 20 lead with business. (3) Colour-blind fixes, all checked with the dataviz validator: the departures-board inks are now blue, red, amber, teal, violet (all pairs pass); the page-wide violet/green pair became violet/teal; the bump chart and beeswarm follow; chart 15's states are a single-hue ramp with labelled segments. (4) Chart 15: no frames; picked countries' names are bold, larger and in their ink; names sit on the page's left edge; smaller gap above it. (5) ACT label moved beside the ACT. (6) Visa pages start level with the act headline.
- **v5.8** (15 October) — (1) Chart 15 states back to hues: NSW blue, VIC orange, QLD violet, WA teal (all pairs pass the colour-blind check) plus grey for the smaller states; wide segments keep their state labels. (2) Display names: `labels.py` gains `DISPLAY_NAME`/`display_name()`; `country_2025.csv` has a `name` column (South Korea, Hong Kong, United States) used by maps 1–2; the bump chart and heatmap tooltips use short names too. (3) Act 4 visa page header now "Students per 1,000 residents". (4) Act 6: the stamp now carries a real figure (59% taught privately in 2024); the closing declaration has working tick-boxes, and ticking one presses a dated "Declared" stamp. Data sources for strengthening Act 6 are listed in the chat reply (finance, staff, QILT).
- **v5.9** (24 October) — Section 06 removed (charts 16 and 17 deleted; `prep/40_business.py` and its CSVs stay as the source for the figures quoted in the text). The "study or business?" thread now lives in the header deck, the chart 3 and chart 8 captions (97% of international VET students at private colleges; coursework master's majority-overseas), the act 3 intro, and a short afterword at the end of section 05. Maps 1 and 2 are now linked by click: clicking a country pins it on both maps with its name and figure, clicking empty space or double-clicking clears it. VET annotation moved clear of the line. All chart titles, subtitles, captions and act intros rewritten: exploratory charts (maps, Marimekko, dumbbell, heatmap, bump, flow map, split bars) now have descriptive titles; finding-led titles kept where a chart has one clear finding.
- **v5.10** (24 October) — Pinning a country on maps 1–2 hides the other direct labels on both maps, so only the pinned country's label shows. The enrolment line chart (chart 2) is now ink navy; red is kept for the border closure.
- **v5.11** (24 October) — Footer rebalanced: the AI acknowledgement moved under the sources as body text; a 'Context' list cites the visa-fee and Ministerial Direction 111 articles the text relies on; the right column gains typefaces and hosting.
- **v5.12** (24 October) — Merged the author's rewritten text into index.html (final wording is the author's; fixed two typos, one missing article, and Mongolia's state: NSW, not Victoria). Drafting markers removed from the source. Footer v5.11 kept. Calendar heatmap legend ticks now 5k/20k/45k/80k/125k, evenly spaced on the square-root scale.
