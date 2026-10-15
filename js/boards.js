/* ==========================================================================
   boards.js: the two on-page controls that drive the Act 4 maps.

   1. Departures board (chart 10, flow map, and chart 15, split bars). Each
      row is a flight from one source country. Clicking a row, the country's
      tile or ribbon on the map, or its bar in chart 15 toggles that country
      in both charts. Up to five countries at once,
      each in its own ink; a sixth pick replaces the oldest. The status
      column flips like a split-flap board: "ON MAP" or blank.

   3. State zoom (chart 11). Whenever the picked state changes, from any of
      the controls, the map glides to its new frame: the projection's fit
      box, the circles' positions and their sizes are blended from the old
      view to the new one over about 0.8 s.

   2. Residence boxes (chart 11 + 12). A row of tick-boxes like the address
      field on a visa form. Ticking a state zooms the map to it and filters
      the beeswarm; "All" goes back. Clicking a state on the map ticks its
      box, because both write to the same link group in js/embed.js.
   ========================================================================== */

// blue, red, amber, teal, violet: checked for colour-blind separation, all pairs
const INKS = ["#2F5FA7", "#C8371F", "#C99400", "#13A39A", "#9E5BD0"];

/* ---------------------------------------------------- 1. departures board */
function initDepartures() {
  const board = document.querySelector(".departures");
  // the flow map and the split bars both follow the board
  const slots = [...document.querySelectorAll("#fig-10 [data-spec], #fig-15 [data-spec]")];
  if (!board || !slots.length) return;
  const rows = new Map([...board.querySelectorAll(".dep[data-iso]")].map((b) => [b.dataset.iso, b]));

  // picks[i] holds the ISO code drawn in INKS[i]; order remembers pick age
  const picks = ["CHN", "IND", "", "", ""];
  let order = ["CHN", "IND"];
  const views = [];

  function render() {
    for (const [iso, btn] of rows) {
      const i = picks.indexOf(iso);
      const on = i >= 0;
      btn.setAttribute("aria-pressed", on);
      btn.style.setProperty("--ink-pick", on ? INKS[i] : "transparent");
      const status = btn.querySelector(".dep__status");
      status.setAttribute("aria-label", on ? "on map" : "not shown");
      if (window.flapTo) window.flapTo(status, on ? "ON MAP" : "");
    }
    for (const v of views) v.signal("picked", picks.slice()).runAsync();
  }

  function toggle(iso) {
    const i = picks.indexOf(iso);
    if (i >= 0) {
      picks[i] = "";
      order = order.filter((c) => c !== iso);
    } else {
      let free = picks.indexOf("");
      if (free < 0) {                       // board full: the oldest pick leaves
        const oldest = order.shift();
        free = picks.indexOf(oldest);
      }
      picks[free] = iso;
      order.push(iso);
    }
    render();
  }

  rows.forEach((btn, iso) => btn.addEventListener("click", () => toggle(iso)));
  slots.forEach((slot) => slot.addEventListener("chart:ready", (e) => {
    const view = e.detail.view;
    views.push(view);
    view.addEventListener("click", (_, item) => {
      const d = item?.datum;
      const iso = d?.iso3 ?? d?.properties?.iso3;
      if (iso && rows.has(iso)) toggle(iso);
    });
    render();
  }));
}

/* ------------------------------------------------------ 2. residence boxes */
function initResidence() {
  const form = document.querySelector(".residence");
  if (!form) return;
  const boxes = [...form.querySelectorAll("input[name=state]")];
  const show = (value) => boxes.forEach((b) => { b.checked = b.value === value; });
  boxes.forEach((b) => b.addEventListener("change", () => {
    // ticking the box that's already ticked unticks it, like a paper form
    const value = b.checked ? b.value : "";
    window.dv2?.setLink("states", value);
    show(value);
  }));
  document.addEventListener("link:change", (e) => {
    if (e.detail.name === "states") show(e.detail.value);
  });
  show("");
}

/* ------------------------------------------------------- 3. state zoom */
// Frames for each view: [lon_min, lat_max, lon_max, lat_min].
// Must match VIEWS in prep/70_campus_dodge.py.
const BOXES = {
  ALL: [112.5, -9.5, 155.0, -44.0],
  NSW: [140.8, -28.0, 155.0, -37.6], VIC: [140.8, -33.9, 150.2, -39.3],
  QLD: [137.8, -10.5, 153.8, -29.3], WA: [112.8, -13.5, 129.2, -35.3],
  SA: [128.8, -25.8, 141.2, -38.2], TAS: [143.6, -39.4, 148.6, -43.8],
  NT: [128.8, -10.8, 138.2, -26.2], ACT: [148.7, -35.05, 149.45, -36.0],
};
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

function initStateZoom() {
  const slot = document.querySelector('#fig-11-12 [data-spec*="11-australia"]');
  if (!slot) return;
  slot.addEventListener("chart:ready", (e) => {
    const view = e.detail.view;
    let box = BOXES.ALL.slice();
    let to = "ALL";
    let run = 0;
    view.addSignalListener("st", async (_, st) => {
      const next = st && BOXES[st] ? st : "ALL";
      if (next === to) return;
      const from = to, start = box.slice(), end = BOXES[next], id = ++run;
      to = next;
      // the listener fires mid-update; start on the next frame
      await new Promise(requestAnimationFrame);
      if (id !== run) return;
      view.signal("vfrom", from).signal("vto", next).signal("t", 0);
      const dur = REDUCED ? 0 : 800, t0 = performance.now();
      while (id === run) {
        const k = dur ? Math.min(1, (performance.now() - t0) / dur) : 1;
        const f = ease(k);
        box = start.map((v, i) => v + (end[i] - v) * f);
        await view.signal("box", box).signal("t", f).runAsync();
        if (k >= 1) break;
        await new Promise(requestAnimationFrame);
      }
    });
  });
}

initDepartures();
initResidence();
initStateZoom();
