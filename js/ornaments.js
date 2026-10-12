/* ==========================================================================
   ornaments.js: the three pieces of the page that aren't charts.

   1. Guilloche: the fine interlaced line pattern printed on passport pages
      as an anti-forgery measure. Drawn once into any <svg class="guilloche">.
   2. Split-flap: <span class="flap" data-flap="1,058,040"> becomes a row of
      tiles that flip through digits and settle, like an arrivals board.
   3. Stamps: .stamp[data-stamp] lands with a thunk the first time it
      scrolls into view.

   All three respect prefers-reduced-motion: the final state, no animation.
   ========================================================================== */

const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
document.documentElement.classList.add("js");

/* ---------------------------------------------------------------- guilloche */
function drawGuilloche(svg) {
  const W = 1600, H = 600;
  const seed = Number(svg.dataset.seed || 1);
  const lines = Number(svg.dataset.lines || 28);
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  svg.setAttribute("aria-hidden", "true");
  let out = "";
  for (let k = 0; k < lines; k++) {
    // Two beating sine waves per line; the phase drift between lines makes
    // the woven, moiré look of real security print.
    const amp = 70 + k * 3.2, ph = k * 0.36 + seed;
    let d = "";
    for (let x = 0; x <= W; x += 5) {
      const y = H * 0.56
        + Math.sin(x / 64 + ph) * amp * Math.sin(x / 390 + k * 0.045 + seed)
        + Math.sin(x / 23 + k) * 3;
      d += (x ? "L" : "M") + x + "," + y.toFixed(1);
    }
    out += `<path d="${d}" fill="none" stroke="var(--guilloche)" stroke-opacity="${(0.045 + k * 0.0022).toFixed(3)}" stroke-width="0.9"/>`;
  }
  svg.innerHTML = out;
}
document.querySelectorAll("svg.guilloche").forEach(drawGuilloche);

/* --------------------------------------------------------------- split-flap */
// Each tile carries a drum of characters in a fixed order, like the real
// thing. Starting from a random position, every tile flips through its drum
// one character at a time until it reaches its target, so tiles stop at
// different moments and the number "settles" rather than appearing.
const DRUM_DIGITS = " 0123456789";
const DRUM_ALPHA  = " ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const FLIP_MS = 55;            // each leaf; one character = two leaves

function glyph(ch) {
  const g = document.createElement("span");
  g.className = "flap__glyph";
  g.textContent = ch === " " ? "\u00A0" : ch;
  return g;
}
function half(cls, ch) {
  const h = document.createElement("span");
  h.className = cls;
  h.appendChild(glyph(ch));
  return h;
}
function setCell(cell, ch) {
  cell.dataset.cur = ch;
  cell.replaceChildren(half("flap__half flap__half--top", ch), half("flap__half flap__half--bot", ch));
}

function buildFlap(el) {
  const target = el.dataset.flap;               // may contain commas: "1,058,040"
  el.setAttribute("role", "img");
  el.setAttribute("aria-label", el.dataset.label || target);
  el.innerHTML = "";
  let gapNext = false;
  for (const ch of target) {
    if (ch === ",") { gapNext = true; continue; }   // a comma becomes a gap, not a tile
    const cell = document.createElement("span");
    cell.className = "flap__cell" + (gapNext ? " flap__cell--gap" : "");
    cell.setAttribute("aria-hidden", "true");
    cell.dataset.final = ch;
    const drum = /[0-9]/.test(ch) ? DRUM_DIGITS : DRUM_ALPHA;
    cell.dataset.drum = drum;
    // Reduced motion: show the final character. Otherwise start somewhere
    // random on the drum, at least three flips away from the target.
    let start = ch;
    if (!REDUCED) {
      const ti = drum.indexOf(ch);
      start = drum[(ti - 3 - Math.floor(Math.random() * (drum.length - 3)) + drum.length * 2) % drum.length];
    }
    setCell(cell, start);
    el.appendChild(cell);
    gapNext = false;
  }
}

function flipOnce(cell, next) {
  const cur = cell.dataset.cur;
  const top = cell.querySelector(".flap__half--top");
  // behind: the next character's top half is revealed as the old leaf falls
  top.replaceChildren(glyph(next));
  const leafTop = half("flap__leaf flap__leaf--top", cur);
  const leafBot = half("flap__leaf flap__leaf--bot", next);
  leafTop.style.setProperty("--t", FLIP_MS + "ms");
  leafBot.style.setProperty("--t", FLIP_MS + "ms");
  cell.append(leafTop, leafBot);
  return new Promise((resolve) => setTimeout(() => { setCell(cell, next); resolve(); }, FLIP_MS * 2 + 5));
}

async function runCell(cell, delay) {
  await new Promise((r) => setTimeout(r, delay));
  const drum = cell.dataset.drum;
  while (cell.dataset.cur !== cell.dataset.final) {
    const next = drum[(drum.indexOf(cell.dataset.cur) + 1) % drum.length];
    await flipOnce(cell, next);
  }
}

function runFlap(el) {
  if (REDUCED) return;
  // the whole board starts together, each tile a few ms apart (motors
  // aren't perfectly synchronised)
  [...el.querySelectorAll(".flap__cell")].forEach((cell, i) => runCell(cell, i * 18 + Math.random() * 40));
}

/* ------------------------------------------------------------------- stamps */
function stamp(el) { el.classList.add("is-stamped"); }

/* ------------------------------------------- trigger on first sight, once */
const flaps = [...document.querySelectorAll(".flap[data-flap]")];
flaps.forEach(buildFlap);
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    io.unobserve(e.target);
    if (e.target.matches(".flap")) runFlap(e.target);
    else stamp(e.target);
  }
}, { threshold: 0.6 });
[...flaps, ...document.querySelectorAll(".stamp[data-stamp]")].forEach((el) => io.observe(el));
