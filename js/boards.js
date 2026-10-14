/* ==========================================================================
   boards.js: the two on-page controls that drive the Act 4 maps.

   1. Departures board (chart 10, flow map). Each row is a flight from one
      source country. Clicking a row, the country's tile on the map, or its
      ribbon toggles that country on the map. Up to five countries at once,
      each in its own ink; a sixth pick replaces the oldest. The status
      column flips like a split-flap board: "ON MAP" or blank.

   2. Residence boxes (chart 11 + 12). A row of tick-boxes like the address
      field on a visa form. Ticking a state zooms the map to it and filters
      the beeswarm; "All" goes back. Clicking a state on the map ticks its
      box, because both write to the same link group in js/embed.js.
   ========================================================================== */

const INKS = ["#2F5FA7", "#C8371F", "#2E8754", "#6E4BA8", "#C99400"];

/* ---------------------------------------------------- 1. departures board */
function initDepartures() {
  const board = document.querySelector(".departures");
  const slot = document.querySelector("#fig-10 [data-spec]");
  if (!board || !slot) return;
  const rows = new Map([...board.querySelectorAll(".dep[data-iso]")].map((b) => [b.dataset.iso, b]));

  // slots[i] holds the ISO code drawn in INKS[i]; order remembers pick age
  const slots = ["CHN", "IND", "", "", ""];
  let order = ["CHN", "IND"];
  let view = null;

  function render() {
    for (const [iso, btn] of rows) {
      const i = slots.indexOf(iso);
      const on = i >= 0;
      btn.setAttribute("aria-pressed", on);
      btn.style.setProperty("--ink-pick", on ? INKS[i] : "transparent");
      const status = btn.querySelector(".dep__status");
      status.setAttribute("aria-label", on ? "on map" : "not shown");
      if (window.flapTo) window.flapTo(status, on ? "ON MAP" : "");
    }
    view?.signal("picked", slots.slice()).runAsync();
  }

  function toggle(iso) {
    const i = slots.indexOf(iso);
    if (i >= 0) {
      slots[i] = "";
      order = order.filter((c) => c !== iso);
    } else {
      let free = slots.indexOf("");
      if (free < 0) {                       // board full: the oldest pick leaves
        const oldest = order.shift();
        free = slots.indexOf(oldest);
      }
      slots[free] = iso;
      order.push(iso);
    }
    render();
  }

  rows.forEach((btn, iso) => btn.addEventListener("click", () => toggle(iso)));
  slot.addEventListener("chart:ready", (e) => {
    view = e.detail.view;
    view.addEventListener("click", (_, item) => {
      const d = item?.datum;
      const iso = d?.iso3 ?? d?.properties?.iso3;
      if (iso && rows.has(iso)) toggle(iso);
    });
    render();
  });
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

initDepartures();
initResidence();
