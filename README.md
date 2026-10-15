# geo/: map geometry and coordinates

Everything here is committed, small, and read by the page or by `prep/50_lookups.py`.

| File | What it is | Source |
|---|---|---|
| `world_countries.topo.json` | 238 country outlines; layer `countries`; properties `iso3`, `name`. 119 KB. | Natural Earth 1:50m Admin 0 Countries (public domain), simplified |
| `country_points.csv` | One point inside each country (`iso3`, `lon`, `lat`) for circles and flow-line origins | Generated from the same file |
| `au_states.topo.json` | 8 state and territory outlines; layer `states`; properties `state` (NSW…), `name`. 28 KB. | ABS ASGS state boundaries via github.com/rowanhogan/australian-states, simplified |
| `au_state_capitals.csv` | Capital city of each state; the flow lines end here | Entered by hand |
| `au_university_locations.csv` | Main campus of each of the 43 providers in the higher-education data | Entered by hand; accurate to roughly 1 km, which is well under one pixel at the map's scale |

## How the geometry was made

With [mapshaper](https://github.com/mbloch/mapshaper) (`npm i -g mapshaper`), from
`ne_50m_admin_0_countries.geojson` (github.com/nvkelso/natural-earth-vector):

```bash
mapshaper ne_50m_admin_0_countries.geojson \
  -filter 'ADM0_A3 != "ATA"' \
  -each 'iso3 = ({KOS:"XKX",PSX:"PSE",SDS:"SSD",SOL:"SOM",CYN:"CYP",KAS:"IND"})[ADM0_A3] || ADM0_A3' \
  -dissolve iso3 copy-fields=NAME -rename-fields name=NAME -rename-layers countries \
  -simplify 10% weighted keep-shapes -clean \
  -o world_countries.topo.json format=topojson quantization=100000 \
  -points inner -each 'lon=+this.x.toFixed(3), lat=+this.y.toFixed(3)' \
  -o country_points.csv format=csv

mapshaper states.geojson \
  -each 'state = ({"New South Wales":"NSW","Victoria":"VIC","Queensland":"QLD","South Australia":"SA","Western Australia":"WA","Tasmania":"TAS","Northern Territory":"NT","Australian Capital Territory":"ACT"})[STATE_NAME]' \
  -rename-fields name=STATE_NAME -filter-fields state,name -rename-layers states \
  -simplify 12% weighted keep-shapes -clean \
  -o au_states.topo.json format=topojson quantization=100000
```

### Why these choices

- **1:50m, not 1:110m.** The 110m file has no Hong Kong, Singapore, Macau or Mauritius, which all send students.
- **Codes recoded to World Bank ISO3** (Kosovo, Palestine, South Sudan) so joins use one code system. Somaliland, Northern Cyprus and Siachen are merged into the internationally recognised country, matching how the Department of Education and the World Bank report them.
- **Antarctica removed.** Nobody comes from there, and it takes a third of the map's height.
- **Simplified to 10–12%** with `keep-shapes`, so small island states don't vanish. Checked visually at the page's chart sizes.
- **Three points moved by hand** in `prep/50_lookups.py` (`POINT_OVERRIDE`): Malaysia, Indonesia and New Zealand, whose "inside point" landed on Borneo, Sumatra and the South Island respectively.
