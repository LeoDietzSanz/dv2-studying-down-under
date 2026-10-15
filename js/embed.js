/* ==========================================================================
   embed.js: finds every chart slot on the page and draws it as it nears
   the viewport.

   A chart slot is any element with a data-spec attribute:
       <div class="chart__vis" data-spec="charts/02-total-line.vl.json"></div>
   A slot with data-pending instead is a placeholder for a chart not yet built.

   Linked charts (maps 4+5, map 11 + beeswarm 12) are separate specs so they
   can sit side by side on desktop and stack on a phone. They talk through a
   tiny bridge: each linked slot names a group, the selection signal it
   captures, and the field to read; whatever one chart selects is written
   into the shared signal of every chart in the group.
       <div data-spec="..." data-link="countries"
            data-link-capture="hov" data-link-field="iso3" data-link-signal="hl">

   Why lazy: fourteen specs, four with map geometry, all parsed on page load
   make the first paint visibly slow. Drawing each one ~400px before it
   scrolls into view makes the page feel instant.
   ========================================================================== */

const THEME_URL = "charts/theme.json";
const LOOKAHEAD = "400px";
const DEV = ["localhost", "127.0.0.1"].includes(location.hostname);

let themePromise = null;
const loadTheme = () =>
  (themePromise ??= fetch(THEME_URL).then((r) => {
    if (!r.ok) throw new Error(`theme.json: HTTP ${r.status}`);
    return r.json();
  }));

/* ---------------------------------------------------------------- linking */
const groups = new Map();   // name -> { views: Set<View>, value: string }

function readSelection(value, field) {
  if (value == null) return "";
  if (typeof value === "string") return value;          // plain Vega signal
  const v = value[field];                                 // Vega-Lite point selection: {field: [value]}
  return Array.isArray(v) ? (v[0] ?? "") : (v ?? "");
}

function link(slot, view) {
  const name = slot.dataset.link;
  if (!name) return;
  const { linkCapture: capture, linkField: field, linkSignal: target } = slot.dataset;
  const g = groups.get(name) ?? { views: new Set(), value: "", target };
  g.target ??= target;
  groups.set(name, g);
  g.views.add(view);
  view.signal(target, g.value).runAsync();               // catch up if a partner already has a selection
  view.addSignalListener(capture, (_, value) => setLink(name, readSelection(value, field)));
  // a double-click on any chart in the group clears the pick for all of them,
  // whichever chart the pick was made on
  slot.addEventListener("dblclick", () => setLink(name, ""));
}

/* Set a link group's value from outside the charts too (the state tick-boxes
   in js/boards.js use this). Every chart in the group updates, and a
   "link:change" event lets HTML controls mirror the choice. */
function setLink(name, next) {
  const g = groups.get(name) ?? { views: new Set(), value: "", target: null };
  groups.set(name, g);
  if (next === g.value) return;
  g.value = next;
  for (const v of g.views) v.signal(g.target, next).runAsync();
  document.dispatchEvent(new CustomEvent("link:change", { detail: { name, value: next } }));
}
window.dv2 = { setLink, linkValue: (name) => groups.get(name)?.value ?? "" };

async function draw(slot) {
  const specUrl = slot.dataset.spec;
  try {
    const [config, spec] = await Promise.all([
      loadTheme(),
      fetch(specUrl).then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      }),
    ]);
    // Maps declare usermeta.aspect (height / width). A fixed height would leave
    // empty bands when the map shrinks to a phone's width, so the height is
    // taken from the slot's real width instead.
    const aspect = spec.usermeta?.aspect;
    if (aspect) spec.height = Math.round(slot.clientWidth * aspect);
    const result = await vegaEmbed(slot, spec, {
      config,
      renderer: "svg",
      // The "..." export menu is handy while building (Open in Vega Editor),
      // hidden on the published page.
      actions: DEV ? { export: true, source: false, compiled: false, editor: true } : false,
      tooltip: { theme: "custom" },
    });
    link(slot, result.view);
    slot.classList.add("is-drawn");
    // Other scripts (js/boards.js) attach their controls once a chart exists.
    slot.dispatchEvent(new CustomEvent("chart:ready", { bubbles: true, detail: { view: result.view } }));
  } catch (err) {
    console.error(`[chart] ${specUrl} failed:`, err);
    slot.textContent = `Chart failed to load (${specUrl}): ${err.message}`;
    slot.setAttribute("data-pending", "");
  }
}

function init() {
  const slots = [...document.querySelectorAll("[data-spec]")];
  if (!("IntersectionObserver" in window)) {
    slots.forEach(draw);
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        io.unobserve(e.target);
        draw(e.target);
      }
    },
    { rootMargin: `${LOOKAHEAD} 0px` }
  );
  slots.forEach((s) => io.observe(s));
}

// Vega measures label widths when it draws. If the web fonts haven't
// arrived yet it measures the fallback font and labels end up misplaced,
// so wait for fonts first.
(document.fonts?.ready ?? Promise.resolve()).then(init);
