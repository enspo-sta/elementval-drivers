/* simulate.js: the Simulate tab. Estimates a 2-, 3- or 4-way speaker's harmonic distortion from the
 * drivers' measured curves and the crossover chosen (maths in app/core/sim.js). Every level a driver
 * was measured at is used: at each frequency the curves are interpolated at the level the driver
 * actually plays at, and only beyond the measured levels does the level rule take over. */
import { registerView } from "../core/registry.js";
import { store, familyOf, kindOf, fmtHz } from "../core/data.js";
import { COLORS, MARKERS, MARK_CHARS, buildGroups } from "../core/compare.js";
import * as SC from "../core/sim.js";
import { writeHash, hasParams } from "../core/state.js";
import { $, app, esc, navHtml, beginView, newChart, noChart, noChartMsg, xAxis, yAxis, chartOptions, markerRadius, badge,
         familyByName, condChips, exportHtml, wireExports, pct, fmtDb, fmtPct } from "../core/ui.js";

const ORDER_COLORS = { H2: "#f0a44a", H3: "#7aa2f7", H4: "#6fd19a", H5: "#c4a3ff", THD: "#eef0f6" };
const WAY_NAMES = { 2: ["low", "high"], 3: ["low", "mid", "high"], 4: ["low", "low mid", "high mid", "high"] };
const XO_DEFAULT = { 2: [2000], 3: [350, 3000], 4: [120, 700, 4000] };
const ORDERS = ["H2", "H3", "H4", "H5"];
const TYPICAL = SC.LAWS.typical.slopes;
const sim = { mix: false, src: null, n: 3, w: null, c: [1, 1, 1, 1], x: null, t: null, L: 94, law: "measured",
              s: Object.assign({}, TYPICAL), al: true, o: null, u: "db", sh: null };
const cache = {};

function load(params) {
  if (!hasParams(params)) return;
  const nums = k => (params.get(k) || "").split(",").filter(x => x !== "").map(Number);
  sim.mix = params.get("mix") === "1";
  sim.src = params.get("src");
  sim.n = [2, 3, 4].includes(Number(params.get("n"))) ? Number(params.get("n")) : 3;
  sim.w = params.get("w") ? params.get("w").split(",") : null;
  const c = nums("c"); if (c.length) sim.c = [0, 1, 2, 3].map(i => (c[i] >= 1 && c[i] <= 4 ? c[i] : 1));
  sim.x = nums("x").length ? nums("x") : null;
  sim.t = params.get("t") ? params.get("t").split(",") : null;
  if (params.get("L") && isFinite(Number(params.get("L")))) sim.L = Number(params.get("L"));
  if (["measured", "typical", "classic", "none"].includes(params.get("law"))) sim.law = params.get("law");
  const s = nums("s"); if (s.length === 4 && s.every(isFinite)) ORDERS.forEach((k, i) => (sim.s[k] = s[i]));
  sim.al = params.get("al") !== "0";
  sim.o = params.get("o") ? params.get("o").split(",") : null;
  sim.u = params.get("u") === "pct" ? "pct" : "db";
  sim.sh = params.get("sh") || null;
}
function save() {
  writeHash("simulate", { mix: sim.mix ? "1" : "", src: sim.mix ? "" : sim.src, n: sim.n, w: sim.w.join(","), c: sim.c.slice(0, sim.n).join(","),
    x: sim.x.join(","), t: sim.t.join(","), L: sim.L, law: sim.law, s: ORDERS.map(k => sim.s[k]).join(","), al: sim.al ? "" : "0",
    o: sim.o.join(","), u: sim.u === "pct" ? "pct" : "", sh: sim.sh || "" });
}

// Candidates: one per driver and source, holding every harmonic-distortion level of that driver.
function candidates(mix, src) {
  const key = (mix ? "mix" : "one") + "|" + (src || "");
  if (cache[key]) return cache[key];
  const out = [];
  for (const g of cache.groups || (cache.groups = buildGroups({ mix: false }))) {
    if (g.kind.id !== "hd-frequency") continue;
    for (const e of g.entries) {
      if (!mix && e.family.name !== src) continue;
      const curves = e.sets.filter(s => s.level != null).map(s => {
        const hd = {};
        s.quantities.forEach(q => { if (ORDERS.includes(q.id)) hd[q.id] = q.points; });
        return { L0: s.level, hd, set: s.set };
      }).filter(c => c.hd.H2 || c.hd.H3);
      if (!curves.length) continue;
      const xs = curves.flatMap(c => Object.values(c.hd).flat().map(p => p.x));
      out.push({ id: e.id, e, curves, levels: curves.map(c => c.L0), orders: ORDERS.filter(k => curves.some(c => c.hd[k])),
                 lo: Math.min(...xs), hi: Math.max(...xs) });
    }
  }
  return (cache[key] = out.sort((a, b) => a.e.driver.name.localeCompare(b.e.driver.name) || (a.e.family.rank || 99) - (b.e.family.rank || 99)));
}
function sources() {
  const names = new Set(candidates(true).map(c => c.e.family.name));
  return store.families.filter(f => names.has(f.name));
}
// Where a driver's role puts it in a speaker: 0 = lowest way, 1 = highest.
function rolePos(role) {
  const r = (role || "").toLowerCase();
  if (/tweeter/.test(r)) return 1;
  if (/^midrange/.test(r)) return 0.6;
  if (/^midbass \/ mid/.test(r)) return 0.42;
  if (/^midbass/.test(r)) return 0.38;
  if (/^woofer \/ midbass/.test(r)) return 0.22;
  if (/woofer/.test(r)) return 0.05;
  return 0.5;
}
// Default driver per way: role fits the way and data covers the way's band (an octave beyond its crossovers).
function autoPick(n, x, cands) {
  const used = new Set(), out = [];
  for (let i = 0; i < n; i++) {
    const lo = Math.max(20, (i === 0 ? 20 : x[i - 1]) / 2), hi = Math.min(20000, (i === n - 1 ? 20000 : x[i]) * 2);
    const width = Math.log(hi / lo), pos = i / (n - 1);
    const score = c => Math.max(0, Math.log(Math.min(hi, c.hi) / Math.max(lo, c.lo))) / width - 1.2 * Math.abs(rolePos(c.e.driver.role) - pos) +
      c.orders.length * 0.01 + c.levels.length * 0.005 + (used.has(c.id) ? -2 : 0);
    const best = cands.slice().sort((a, b) => score(b) - score(a))[0];
    out.push(best ? best.id : null);
    if (best) used.add(best.id);
  }
  return out;
}
function normalise() {
  const srcs = sources();
  if (!srcs.some(f => f.name === sim.src)) sim.src = srcs.length ? srcs[0].name : null;
  const cands = candidates(sim.mix, sim.src);
  const nx = sim.n - 1;
  if (!sim.x || sim.x.length !== nx || sim.x.some(v => !(v >= 20 && v <= 20000))) sim.x = XO_DEFAULT[sim.n].slice();
  sim.x = sim.x.slice().sort((a, b) => a - b);
  if (!sim.t || sim.t.length !== nx || sim.t.some(t => !SC.TYPES[t])) sim.t = Array(nx).fill("LR4");
  if (!sim.w || sim.w.length !== sim.n || sim.w.some(id => !cands.some(c => c.id === id))) sim.w = autoPick(sim.n, sim.x, cands);
  if (!(sim.L >= 60 && sim.L <= 125)) sim.L = 94;
  ORDERS.forEach(k => { if (!isFinite(sim.s[k])) sim.s[k] = TYPICAL[k]; });
  const chosen = sim.w.map(id => cands.find(c => c.id === id)).filter(Boolean);
  const avail = ORDERS.filter(k => chosen.length && chosen.every(c => c.orders.includes(k)));
  const shows = avail.concat(avail.length ? ["THD"] : []);
  sim.o = (sim.o || []).filter(k => shows.includes(k));
  if (!sim.o.length) sim.o = shows.filter(k => ["H2", "H3", "THD"].includes(k));
  if (!shows.includes(sim.sh)) sim.sh = shows[0] || null;
  return { srcs, cands, chosen, avail, shows };
}

/** How a driver's distortion moves with level beyond its measured levels: {fn(order, f), text}. */
function slopeFor(c) {
  const base = k => (sim.law === "classic" ? SC.LAWS.classic.slopes[k] : sim.law === "none" ? 0 : sim.s[k]);
  const lv = c.levels.length > 1 ? `measured at ${c.levels.join(" and ")} dB, interpolated between them; ` : `measured at ${c.levels[0]} dB; `;
  if (sim.law !== "measured") return { fn: k => base(k), text: lv + (sim.law === "none" ? "no level change beyond that" : sim.law === "classic" ? "beyond that the textbook (n−1) rule" : "beyond that the slopes set below") };
  const L0 = c.levels[0], centre = (L0 + sim.L) / 2, half = Math.max(6, Math.abs(sim.L - L0) / 2 + 3);
  const byOrder = {};
  let clamped = false;
  (c.e.driver.measurements || []).forEach(set => {
    if (kindOf(set).id !== "hd-level") return;
    const fam = familyOf(set);
    if (!fam || fam.name !== c.e.family.name) return;
    (set.series || []).forEach(s => {
      const m = String(s.name).match(/^(H\d)\s+(\d+(?:\.\d+)?)\s*(k?)Hz$/i);
      if (!m) return;
      let slope = SC.slopeFromSweep((s.points || []).map(p => ({ x: Number(p.x), y: p.y == null ? null : Number(p.y) })), centre - half, centre + half);
      if (slope == null) return;
      if (slope < 0) { slope = 0; clamped = true; }
      (byOrder[m[1].toUpperCase()] = byOrder[m[1].toUpperCase()] || []).push({ f: Number(m[2]) * (m[3] ? 1000 : 1), slope });
    });
  });
  const curves = {};
  Object.entries(byOrder).forEach(([k, list]) => (curves[k] = SC.slopeCurve(list)));
  const measured = Object.keys(curves);
  const text = lv + (measured.length
    ? "beyond that the measured sweep: " + measured.sort().map(k => k + " " + byOrder[k].sort((a, b) => a.f - b.f).map(x => x.slope.toFixed(2) + " at " + fmtHz(x.f)).join(", ")).join("; ") +
      (ORDERS.some(k => !curves[k] && c.orders.includes(k)) ? "; other orders from the slopes below" : "") +
      (clamped ? ". A falling measured slope counts as 0: the sweep is at the measurement's noise floor there" : "")
    : "no level sweep from this source, so beyond that the slopes below");
  return { fn: (k, f) => (curves[k] ? curves[k](f) : base(k)), text };
}

function render() {
  beginView(true);
  const { srcs, cands, chosen, avail, shows } = normalise();
  save();
  let h = navHtml("simulate") + `<h1>Simulate a speaker</h1>
    <p class="lede">Estimates a 2-, 3- or 4-way speaker's harmonic distortion from each driver's measured curves and the crossover you choose. Drivers come from one source at a time. Every level a driver was measured at is used; between them the curves are interpolated at the level the driver actually plays at.</p>`;
  if (!srcs.length) { app().innerHTML = h + `<div class="empty">No harmonic distortion curves in the database yet.</div>`; return; }
  const names = WAY_NAMES[sim.n];
  h += `<div class="panel"><div class="lbl"><span>Source</span><span class="hint">most reliable first</span></div><div class="srcrow">${srcs.map(f => {
    const n = new Set(candidates(false, f.name).map(c => c.e.driver.id)).size;
    return `<button class="srcbtn${!sim.mix && f.name === sim.src ? " on" : ""}" data-ssrc="${esc(f.name)}" ${sim.mix ? "disabled" : ""}><span class="sn">${esc(f.name)}</span>${badge(f)}<span class="cnt">${n} driver${n !== 1 ? "s" : ""}</span></button>`;
  }).join("")}</div>
    <label class="ds" style="margin:10px 0 0"><input type="checkbox" id="smix" ${sim.mix ? "checked" : ""}> mix sources (not recommended)</label>
    <div class="grid2">
      <div><div class="lbl"><span>Ways</span></div><div class="togrow">${[2, 3, 4].map(n => `<button class="tog${sim.n === n ? " on" : ""}" data-n="${n}">${n}-way</button>`).join("")}</div></div>
      <div><div class="lbl"><span>Level</span><span class="hint">dB SPL at 1 m</span></div><input type="number" class="num" id="sL" min="60" max="125" step="1" value="${sim.L}"></div>
    </div>
    <div class="lbl"><span>Drivers and crossovers</span><span class="hint">low to high</span></div><div class="ways">`;
  for (let i = 0; i < sim.n; i++) {
    h += `<div class="way"><span class="wdot" style="background:${COLORS[i]}">${MARK_CHARS[MARKERS[i]]}</span><div class="wbody">
      <div class="wname">Way ${i + 1} · ${names[i]}</div>
      <select class="sel" data-way="${i}">${cands.map(c => `<option value="${esc(c.id)}"${c.id === sim.w[i] ? " selected" : ""}>${esc(c.e.driver.name)}${sim.mix ? " · " + esc(c.e.family.name) : ""} · ${c.levels.join(" and ")} dB · ${fmtHz(c.lo)} to ${fmtHz(c.hi)} · ${c.orders.join(" ")}</option>`).join("")}</select>
      <div class="wmeta"><label>drivers in this way <select class="sel mini" data-count="${i}">${[1, 2, 3, 4].map(k => `<option${sim.c[i] === k ? " selected" : ""}>${k}</option>`).join("")}</select></label></div>
    </div></div>`;
    if (i < sim.n - 1) h += `<div class="xo"><span class="xol">crossover ${i + 1}</span>
      <input type="number" class="num" data-xf="${i}" min="20" max="20000" step="10" value="${sim.x[i]}"><span class="dim">Hz</span>
      <select class="sel mini" data-xt="${i}">${Object.entries(SC.TYPES).map(([k, t]) => `<option value="${k}"${sim.t[i] === k ? " selected" : ""}>${esc(t.label)}</option>`).join("")}</select></div>`;
  }
  h += `</div><div class="grid2">
    <div><div class="lbl"><span>Summing</span></div><select class="sel" id="sal">
      <option value="1"${sim.al ? " selected" : ""}>Ways sum flat (lower ways phase-matched with all-pass filters)</option>
      <option value="0"${sim.al ? "" : " selected"}>Plain filters (the sum dips between close crossovers)</option></select></div>
    <div><div class="lbl"><span>Beyond the measured levels</span></div><select class="sel" id="slaw">
      <option value="measured"${sim.law === "measured" ? " selected" : ""}>Measured sweeps (Purifi datasheets), else the slopes below</option>
      <option value="typical"${sim.law === "typical" ? " selected" : ""}>The slopes below for every driver</option>
      <option value="classic"${sim.law === "classic" ? " selected" : ""}>Textbook rule: H2 +1, H3 +2, H4 +3, H5 +4 (over-predicts)</option>
      <option value="none"${sim.law === "none" ? " selected" : ""}>No change: the nearest measured level as it is</option></select></div>
  </div>`;
  if (sim.law === "measured" || sim.law === "typical") h += `<div class="lbl"><span>Slopes</span><span class="hint">dB of distortion per dB of level · typical from your data: H2 1.0, H3 to H5 0.7</span></div><div class="togrow">${ORDERS.map(k =>
    `<label class="slope">${k} <input type="number" class="num mini" data-slope="${k}" step="0.05" min="-1" max="5" value="${sim.s[k]}"></label>`).join("")}<button class="tog" id="sreset">typical</button></div>`;
  h += `</div>`;

  const warnings = [];
  let res = null;
  if (chosen.length === sim.n && avail.length) {
    const slopes = chosen.map(c => slopeFor(c));
    let fLo = Math.max(20, chosen[0].lo), fHi = Math.min(20000, chosen[sim.n - 1].hi);
    if (!(fHi > fLo * 1.5)) { fLo = 20; fHi = 20000; }
    res = SC.simulate({ freqs: SC.logGrid(fLo, fHi, 24), target: sim.L, orders: avail, aligned: sim.al,
      points: sim.x.map((fc, i) => ({ fc, type: sim.t[i] })),
      ways: chosen.map((c, i) => ({ name: c.e.driver.name, curves: c.curves, slope: slopes[i].fn, count: sim.c[i] })) });
    res.slopes = slopes;
    res.range = [res.freqs[0], res.freqs[res.freqs.length - 1]];
    const merged = [];
    for (const gp of res.gaps) {
      const m = merged.find(x => x.way === gp.way && x.from === gp.from && x.to === gp.to);
      if (m) m.orders.push(gp.order); else merged.push({ way: gp.way, from: gp.from, to: gp.to, orders: [gp.order] });
    }
    const list = a => (a.length > 1 ? a.slice(0, -1).join(", ") + " and " + a[a.length - 1] : a[0]);
    for (const gp of merged) warnings.push(`Way ${gp.way + 1} (${esc(chosen[gp.way].e.driver.name)}) has no ${list(gp.orders)} data from ${fmtHz(gp.from)} to ${fmtHz(gp.to)}, where it still plays within 40 dB of the other ways. The speaker's ${list(gp.orders)} and THD are left empty there rather than guessed.`);
    chosen.forEach((c, i) => {
      const mx = (c.e.driver.measurements || []).find(m => kindOf(m).id === "max-spl" && m.series && m.series[0]);
      if (!mx) return;
      const pts = mx.series[0].points.map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
      const over = res.freqs.filter((f, j) => { const m = SC.interpLog(pts, f); return m != null && sim.L + res.response.ways[i][j] > m + 20 * Math.log10(sim.c[i]); });
      if (over.length) warnings.push(`Way ${i + 1} (${esc(c.e.driver.name)}${sim.c[i] > 1 ? " ×" + sim.c[i] : ""}) cannot reach ${sim.L} dB from ${fmtHz(over[0])} to ${fmtHz(over[over.length - 1])}: it runs out of excursion there (${esc(mx.type)}, calculated, not measured). Its distortion there is higher than shown.`);
      const lo = Math.min(...c.levels), hi = Math.max(...c.levels);
      if (sim.L > hi + 6) warnings.push(`Way ${i + 1} (${esc(c.e.driver.name)}) was measured at up to ${hi} dB; at ${sim.L} dB its result leans on the level rule more than on measurements.`);
      else if (sim.L < lo - 12) warnings.push(`Way ${i + 1} (${esc(c.e.driver.name)}) was measured at ${lo} dB and above; at ${sim.L} dB its result leans on the level rule.`);
    });
    sim.x.forEach((fc, i) => { if (i > 0 && fc / sim.x[i - 1] < 2) warnings.push(`Crossovers ${i} and ${i + 1} are less than an octave apart (${fmtHz(sim.x[i - 1])} and ${fmtHz(fc)}); the middle way then never plays at full level.`); });
  } else if (chosen.length === sim.n) warnings.push("The picked drivers share no harmonic order (one source has only H2 and H3, another only H4 and H5).");
  const thdLabel = avail.length === 4 ? "THD" : `THD (${avail.join(" + ")} only)`;
  const fam = familyByName(sim.src);
  h += `<div class="panel"><div class="ptitle">Speaker distortion at ${sim.L} dB · ${sim.n}-way${sim.mix ? " · sources mixed" : " · " + esc(sim.src) + " " + badge(fam)}</div>`;
  if (sim.mix) h += `<div class="warn"><b>Sources mixed.</b> The drivers were measured by different sources, which measure in different ways; the result mixes their errors. Prefer one source.</div>`;
  h += `<div class="togrow">${shows.map(k => `<button class="tog${sim.o.includes(k) ? " on" : ""}" data-o="${k}"><span class="odot" style="background:${ORDER_COLORS[k]}"></span>${k === "THD" ? esc(thdLabel) : k}</button>`).join("")}
    <span class="sep"></span><button class="tog${sim.u === "db" ? " on" : ""}" data-su="db">dB</button><button class="tog${sim.u === "pct" ? " on" : ""}" data-su="pct">%</button></div>`;
  h += res ? (noChart() ? noChartMsg : `<div class="chartbox tall"><canvas id="schart"></canvas></div>`) : `<div class="empty">Nothing to show.</div>`;
  if (res) h += `<div class="hint2">Simulated from ${fmtHz(res.range[0])} to ${fmtHz(res.range[1])}, where the lowest and the highest way have data.</div><div id="ssum"></div>
    <div class="exportrow">${exportHtml(() => exportCurves(res, chosen, avail, thdLabel), `simulation_${sim.n}-way_${sim.L}dB`, "Export the results")}</div>`;
  h += warnings.map(w => `<div class="warn">${w}</div>`).join("") + `</div>`;
  if (res) {
    h += `<div class="panel"><div class="ptitle">Each driver's share</div><div class="togrow">${shows.map(k => `<button class="tog${sim.sh === k ? " on" : ""}" data-sh="${k}">${k === "THD" ? esc(thdLabel) : k}</button>`).join("")}</div>
      <div class="legend">${chosen.map((c, i) => `<span class="lg"><span class="lgm" style="color:${COLORS[i]}">${MARK_CHARS[MARKERS[i]]}</span><span class="lgl dashed" style="border-color:${COLORS[i]}"></span>Way ${i + 1}: ${esc(c.e.driver.name)}${sim.c[i] > 1 ? " ×" + sim.c[i] : ""}</span>`).join("")}<span class="lg"><span class="lgl" style="background:#eef0f6"></span>speaker</span></div>
      ${noChart() ? "" : `<div class="chartbox"><canvas id="sshare"></canvas></div>`}
      <div class="hint2">Each way's harmonics relative to the speaker's summed output, so the shares add up (as power) to the speaker line.</div></div>
      <div class="panel"><div class="ptitle">Crossover: level of each way</div>
      <div class="legend">${chosen.map((c, i) => `<span class="lg"><span class="lgl" style="background:${COLORS[i]}"></span>Way ${i + 1}</span>`).join("")}<span class="lg"><span class="lgl" style="background:#eef0f6"></span>sum</span></div>
      ${noChart() ? "" : `<div class="chartbox"><canvas id="sresp"></canvas></div>`}</div>
      <div class="panel"><div class="ptitle">Levels used for each driver</div>${chosen.map((c, i) =>
        `<div class="cond"><span style="color:${COLORS[i]}">${MARK_CHARS[MARKERS[i]]} Way ${i + 1}: ${esc(c.e.driver.name)}</span> <span class="dim">${esc(res.slopes[i].text)}</span>${c.curves.map(cv => condChips(cv.set.conditions, cv.set.source)).join("")}</div>`).join("")}
      <details class="conds"><summary>How this is calculated</summary><ul class="how">
        <li>Each way receives the signal through its crossover filters. The drivers are assumed to be level-matched and flat, so a way plays at the chosen level times its filter response.</li>
        <li>At every frequency each driver's harmonic ratio is taken at the level it actually plays at there. Between two measured levels the measured curves are interpolated; beyond the measured levels the nearest curve is moved by slope × level difference. Near a crossover a driver plays 6 dB lower (Linkwitz-Riley) or 3 dB lower (Butterworth), so its distortion drops.</li>
        <li>Several identical drivers in one way share the level: two drivers each play 6 dB lower.</li>
        <li>Harmonics of different drivers are added as powers, because their phases are unknown. The result is relative to the speaker's summed output.</li>
        <li>A driver more than 40 dB below the others at a frequency is ignored there. Where a driver that matters has no data, the result is left empty.</li>
        <li>Not included: the drivers' own frequency response and baffle, Doppler intermodulation between ways, and cabinet or port noise. Intermodulation is compared in the Compare tab instead.</li>
      </ul></details></div>`;
  }
  app().innerHTML = h;
  wire();
  if (res && !noChart()) draw(res, chosen, avail, thdLabel);
  wireExports(app());
}

function exportCurves(res, chosen, avail, thdLabel) {
  const base = { driver: { id: `simulation-${sim.n}-way`, name: `${sim.n}-way simulation at ${sim.L} dB` }, source: sim.mix ? "mixed sources" : sim.src,
    sourceText: `Simulated from ${chosen.map(c => c.e.driver.name).join(", ")}; crossovers ${sim.x.map((f, i) => `${f} Hz ${sim.t[i]}`).join(", ")}`,
    kind: "hd-frequency", kindLabel: "Simulated speaker harmonic distortion", level: sim.L, xLabel: "Frequency", xUnit: "Hz", yLabel: "Harmonic", yUnit: "dB re fundamental" };
  const curve = (label, quantity, ys) => Object.assign({}, base, { label, quantity, points: res.freqs.map((f, i) => ({ x: f, y: ys[i] })).filter(p => p.y != null) });
  const out = ORDERS.filter(k => avail.includes(k)).map(k => curve(`speaker · ${k}`, k, res.system[k]));
  out.push(curve(`speaker · ${thdLabel}`, "THD", res.system.THD));
  chosen.forEach((c, i) => avail.forEach(k => out.push(curve(`way ${i + 1} ${c.e.driver.name} · ${k} share`, `way${i + 1}-${k}`, res.contrib[i][k]))));
  chosen.forEach((c, i) => out.push(Object.assign(curve(`way ${i + 1} ${c.e.driver.name} · crossover level`, `way${i + 1}-level`, res.response.ways[i]), { kind: "frequency-response", yLabel: "Level", yUnit: "dB" })));
  return out;
}

function wire() {
  const rerender = () => render();
  document.querySelectorAll("[data-ssrc]").forEach(b => b.onclick = () => { sim.src = b.dataset.ssrc; sim.w = null; rerender(); });
  const mix = $("smix"); if (mix) mix.onchange = () => { sim.mix = mix.checked; if (!sim.mix) sim.w = null; rerender(); };
  document.querySelectorAll("[data-n]").forEach(b => b.onclick = () => { const n = Number(b.dataset.n); if (n !== sim.n) { sim.n = n; sim.x = null; sim.t = null; sim.w = null; } rerender(); });
  const L = $("sL"); if (L) L.onchange = () => { const v = Number(L.value); if (v >= 60 && v <= 125) sim.L = v; rerender(); };
  document.querySelectorAll("[data-way]").forEach(s => s.onchange = () => { sim.w[Number(s.dataset.way)] = s.value; rerender(); });
  document.querySelectorAll("[data-count]").forEach(s => s.onchange = () => { sim.c[Number(s.dataset.count)] = Number(s.value); rerender(); });
  document.querySelectorAll("[data-xf]").forEach(inp => inp.onchange = () => { const v = Number(inp.value); if (v >= 20 && v <= 20000) sim.x[Number(inp.dataset.xf)] = v; rerender(); });
  document.querySelectorAll("[data-xt]").forEach(s => s.onchange = () => { sim.t[Number(s.dataset.xt)] = s.value; rerender(); });
  const al = $("sal"); if (al) al.onchange = () => { sim.al = al.value === "1"; rerender(); };
  const law = $("slaw"); if (law) law.onchange = () => { sim.law = law.value; rerender(); };
  document.querySelectorAll("[data-slope]").forEach(inp => inp.onchange = () => { const v = Number(inp.value); if (isFinite(v)) sim.s[inp.dataset.slope] = v; rerender(); });
  const rs = $("sreset"); if (rs) rs.onclick = () => { sim.s = Object.assign({}, TYPICAL); rerender(); };
  document.querySelectorAll("[data-o]").forEach(b => b.onclick = () => {
    const k = b.dataset.o;
    if (sim.o.includes(k)) { if (sim.o.length > 1) sim.o = sim.o.filter(x => x !== k); } else sim.o = sim.o.concat(k);
    rerender();
  });
  document.querySelectorAll("[data-su]").forEach(b => b.onclick = () => { sim.u = b.dataset.su; rerender(); });
  document.querySelectorAll("[data-sh]").forEach(b => b.onclick = () => { sim.sh = b.dataset.sh; rerender(); });
}

function draw(res, chosen, avail, thdLabel) {
  const u = sim.u, conv = v => (u === "pct" ? pct(v) : v);
  const yT = u === "pct" ? "% of fundamental" : "dB re fundamental";
  const series = k => res.freqs.map((f, i) => ({ x: f, y: conv(res.system[k][i]) }));
  const lbl = k => (k === "THD" ? thdLabel : k);
  const tip = c => `${c.dataset.label}: ${c.parsed.y == null ? "—" : u === "pct" ? c.parsed.y.toPrecision(3) + " %" : c.parsed.y.toFixed(1) + " dB"} at ${fmtHz(c.parsed.x)}`;
  newChart($("schart"), { type: "line", data: { datasets: sim.o.map(k => ({ label: lbl(k), data: series(k), borderColor: ORDER_COLORS[k], backgroundColor: ORDER_COLORS[k],
    borderWidth: k === "THD" ? 3 : 2, pointRadius: 0, spanGaps: false, tension: 0.15 })) },
    options: chartOptions({ x: xAxis(true, "Frequency of the fundamental (Hz)", 20, 20000), y: yAxis(u, yT) }, tip) });
  const k = sim.sh;
  const clip = v => (v == null || v < -120 ? null : conv(v));   // shares 120 dB down do not matter
  const shareSets = chosen.map((c, i) => ({ label: `Way ${i + 1}`, borderColor: COLORS[i], backgroundColor: COLORS[i], borderDash: [6, 4], borderWidth: 2,
    pointStyle: MARKERS[i], pointRadius: markerRadius(res.freqs.length, i), pointBackgroundColor: COLORS[i], spanGaps: false, tension: 0.15,
    data: res.freqs.map((f, j) => {
      if (k !== "THD") return { x: f, y: clip(res.contrib[i][k][j]) };
      const parts = avail.map(o => res.contrib[i][o][j]);
      return { x: f, y: parts.every(v => v == null) ? null : clip(10 * Math.log10(parts.reduce((s, v) => s + (v == null ? 0 : Math.pow(10, v / 10)), 0))) };
    }) }));
  shareSets.push({ label: "speaker", data: series(k), borderColor: "#eef0f6", backgroundColor: "#eef0f6", borderWidth: 2.5, pointRadius: 0, spanGaps: false, tension: 0.15 });
  newChart($("sshare"), { type: "line", data: { datasets: shareSets }, options: chartOptions({ x: xAxis(true, "Frequency (Hz)", 20, 20000), y: yAxis(u, yT) }, tip) });
  const resp = chosen.map((c, i) => ({ label: `Way ${i + 1}`, borderColor: COLORS[i], backgroundColor: COLORS[i], borderWidth: 2, pointRadius: 0,
    data: res.freqs.map((f, j) => ({ x: f, y: Math.max(-60, res.response.ways[i][j]) })) }));
  resp.push({ label: "sum", borderColor: "#eef0f6", backgroundColor: "#eef0f6", borderWidth: 2.5, pointRadius: 0, data: res.freqs.map((f, j) => ({ x: f, y: res.response.sum[j] })) });
  newChart($("sresp"), { type: "line", data: { datasets: resp }, options: chartOptions({ x: xAxis(true, "Frequency (Hz)", 20, 20000),
    y: yAxis("db", "Level (dB)", { min: -40, max: 6 }) }, c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} dB at ${fmtHz(c.parsed.x)}`) });
  const bands = [[20, 200, "20 to 200 Hz"], [200, 2000, "200 Hz to 2 kHz"], [2000, 20000, "2 to 20 kHz"], [20, 20000, "whole range"]];
  const fv = v => (v == null ? "—" : u === "pct" ? fmtPct(v) : fmtDb(v));
  let t = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>median<br>highest</th>${bands.map(b => `<th>${b[2]}</th>`).join("")}</tr></thead><tbody>`;
  for (const o of sim.o) {
    t += `<tr><td><span class="odot" style="background:${ORDER_COLORS[o]}"></span>${esc(lbl(o))}</td>`;
    for (const [lo, hi] of bands) {
      const pts = res.freqs.map((f, i) => ({ f, v: res.system[o][i] })).filter(p => p.f >= lo && p.f <= hi && p.v != null);
      if (!pts.length) { t += `<td>—</td>`; continue; }
      const vs = pts.map(p => p.v).sort((a, b) => a - b), med = vs[Math.floor((vs.length - 1) / 2)];
      const top = pts.reduce((a, b) => (b.v > a.v ? b : a));
      t += `<td>${fv(med)}<br><span class="dim">${fv(top.v)} at ${fmtHz(top.f)}</span></td>`;
    }
    t += `</tr>`;
  }
  $("ssum").innerHTML = t + `</tbody></table></div>`;
}

registerView({
  id: "simulate", label: "Simulate", order: 30, routes: ["simulate"],
  show({ params }) { load(params); render(); },
});
