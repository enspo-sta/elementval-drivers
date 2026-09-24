/* tools.js: the Compare and Simulate views of the driver viewer (index.html).
 *
 * Compare  overlays up to five drivers measured by one source (Purifi datasheets, HiFiCompass, ...),
 *          one measurement at a time, showing only the quantities you pick (for example only H3,
 *          or only the intermodulation products).
 * Simulate estimates a 2-, 3- or 4-way speaker's harmonic distortion from the drivers' measured
 *          curves and the crossover you choose (sim-core.js holds the maths).
 *
 * Uses compare-core.js and sim-core.js, and from index.html: DB, SURVEY, FAMILIES, newChart(),
 * clearCharts(), navHtml(), condChips(). The current settings are kept in the address after '#',
 * so a comparison or simulation can be bookmarked or sent as a link.
 */
(function () {
  "use strict";
  const CC = window.CompareCore, SC = window.SimCore;
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtHz = CC.fmtHz;
  const ORDER_COLORS = { H2: "#f0a44a", H3: "#7aa2f7", H4: "#6fd19a", H5: "#c4a3ff", THD: "#eef0f6" };
  const MARK_CHARS = { circle: "●", triangle: "▲", rect: "■", rectRot: "◆", star: "★" };
  const REL_COLORS = { 1: "#6fd19a", 2: "#56b6c2", 3: "#f0a44a", 4: "#a3acc2", 5: "#e98b8b" };
  const GRID = "#2b3344", TICK = "#a3acc2", TITLE = "#7b859c";
  const WAY_NAMES = { 2: ["low", "high"], 3: ["low", "mid", "high"], 4: ["low", "low mid", "high mid", "high"] };
  const XO_DEFAULT = { 2: [2000], 3: [350, 3000], 4: [120, 700, 4000] };
  const ORDERS = ["H2", "H3", "H4", "H5"];
  const $ = id => document.getElementById(id);

  // ---------- shared helpers ----------
  const allDrivers = () => ((typeof DB !== "undefined" && DB && DB.drivers) || []).concat((typeof SURVEY !== "undefined" && SURVEY && SURVEY.drivers) || []);
  const cache = {};
  function groups(mix) {
    const k = mix ? "mix" : "one";
    return cache[k] || (cache[k] = CC.buildGroups(allDrivers(), FAMILIES, mix));
  }
  function badge(f) {
    if (!f || !f.reliability) return "";
    const c = REL_COLORS[f.rank] || "#7b859c";
    return `<span class="rel" style="color:${c};border-color:${c}66" title="${esc(f.reliability_note || "")}">${esc(f.reliability)}</span>`;
  }
  function params() {
    const h = location.hash.slice(1), i = h.indexOf("?");
    return new URLSearchParams(i < 0 ? "" : h.slice(i + 1));
  }
  function save(page, obj) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(obj)) if (v != null && v !== "") p.set(k, v);
    const s = p.toString();
    try { history.replaceState(null, "", "#" + page + (s ? "?" + s : "")); } catch (e) { /* some embedded frames refuse; the view still works */ }
  }
  const pct = v => (v == null ? null : SC.dbToPct(v));
  const fmtDb = v => (v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(1) + " dB");
  function fmtPct(v) {
    if (v == null) return "—";
    const p = SC.dbToPct(v);
    return (p >= 10 ? p.toFixed(0) : p >= 1 ? p.toFixed(1) : p >= 0.1 ? p.toFixed(2) : p.toFixed(3)) + " %";
  }
  function tickLog(v) {
    const e = Math.floor(Math.log10(v) + 1e-9), m = v / Math.pow(10, e);
    if (![1, 2, 5].some(k => Math.abs(m - k) < 1e-6)) return "";
    return v >= 1000 ? v / 1000 + "k" : String(+v.toPrecision(3));
  }
  function xAxis(log, title, min, max) {
    const ticks = { color: TICK, font: { size: 10 }, maxRotation: 0 };
    if (log) { ticks.autoSkip = false; ticks.callback = v => tickLog(v); }
    return { type: log ? "logarithmic" : "linear", min, max, grid: { color: GRID }, ticks,
             title: { display: !!title, text: title, color: TITLE, font: { size: 11 } } };
  }
  function yAxis(units, title, extra) {
    const ticks = { color: TICK, font: { size: 10 } };
    if (units === "pct") ticks.callback = v => { const t = tickLog(v); return t && t + " %"; };
    return Object.assign({ type: units === "pct" ? "logarithmic" : "linear", grid: { color: GRID }, ticks,
             title: { display: !!title, text: title, color: TITLE, font: { size: 11 } } }, extra || {});
  }
  function chartOptions(scales, tooltipLabel) {
    return { responsive: true, maintainAspectRatio: false, animation: false, normalized: true,
      interaction: { mode: "nearest", intersect: false },
      plugins: { legend: { display: false }, tooltip: { callbacks: tooltipLabel ? { label: tooltipLabel } : {} } },
      scales };
  }
  // Show a marker on every n-th point, staggered per driver so markers of different drivers do not sit on top of each other.
  function markerRadius(n, slot) {
    const step = Math.max(1, Math.round(n / 9)), off = Math.floor((slot * step) / 5) % step;
    return ctx => (ctx.dataIndex % step === off ? 4 : 0);
  }
  const noChart = () => typeof Chart === "undefined";
  const noChartMsg = `<div class="warn">The chart library did not load (no internet connection?). The settings above still work; reload the page when you are online.</div>`;

  // =====================================================================================
  // Compare
  // =====================================================================================
  const cmp = { mix: false, src: null, g: null, q: [], picks: null, u: "db", rows: null };

  function loadCompare() {
    const p = params();
    if (![...p.keys()].length) return;
    cmp.mix = p.get("mix") === "1";
    cmp.src = p.get("src");
    cmp.g = p.get("g");
    cmp.q = (p.get("q") || "").split(",").filter(Boolean);
    const d = (p.get("d") || "").split(",").filter(Boolean).slice(0, CC.MAX_PICK);
    cmp.picks = d.length ? d.map((id, slot) => ({ id, slot })) : [];
    cmp.u = p.get("u") === "pct" ? "pct" : "db";
    cmp.rows = p.get("r") ? p.get("r").split("|") : null;
  }
  function saveCompare() {
    save("compare", {
      mix: cmp.mix ? "1" : "", src: cmp.mix ? "" : cmp.src, g: cmp.g, q: cmp.q.join(","),
      d: (cmp.picks || []).slice().sort((a, b) => a.slot - b.slot).map(p => p.id).join(","),
      u: cmp.u === "pct" ? "pct" : "", r: cmp.rows ? cmp.rows.join("|") : "",
    });
  }
  const driversIn = g => new Set(g.entries.map(e => e.driver.id)).size;
  function defaultGroup(list) {
    const score = g => (g.kind.key.startsWith("hd-f") ? 1000 : 0) + driversIn(g);
    return list.slice().sort((a, b) => score(b) - score(a))[0] || null;
  }
  function rowLabels(g, qid) {
    const out = [];
    g.entries.forEach(e => e.quantities.filter(q => q.id === qid).forEach(q => q.rows.forEach(r => { if (!out.includes(r.label)) out.push(r.label); })));
    return out;
  }
  function normCompare() {
    const srcs = CC.sourcesOf(groups(false), FAMILIES);
    if (!srcs.some(f => f.name === cmp.src)) cmp.src = srcs.length ? srcs[0].name : null;
    const avail = cmp.mix ? groups(true) : groups(false).filter(g => g.family === cmp.src);
    let g = avail.find(x => x.key === cmp.g);
    if (!g) { g = defaultGroup(avail); cmp.g = g ? g.key : null; cmp.picks = null; cmp.rows = null; }
    if (!g) return { srcs, avail, g: null };
    cmp.q = cmp.q.filter(id => g.quantityIds.includes(id));
    if (g.kind.view !== "curve") cmp.q = cmp.q.slice(0, 1);
    if (!cmp.q.length) cmp.q = [g.quantityIds[0]];
    if (cmp.picks) cmp.picks = cmp.picks.filter(p => g.entries.some(e => e.id === p.id));
    if (!cmp.picks) cmp.picks = g.entries.slice(0, CC.MAX_PICK).map((e, slot) => ({ id: e.id, slot }));
    if (g.kind.view === "table") {
      const labels = rowLabels(g, cmp.q[0]);
      cmp.rows = (cmp.rows || []).filter(r => labels.includes(r));
      if (!cmp.rows.length) cmp.rows = labels.slice();
    } else cmp.rows = null;
    return { srcs, avail, g };
  }
  function freeSlot() {
    for (let s = 0; s < CC.MAX_PICK; s++) if (!cmp.picks.some(p => p.slot === s)) return s;
    return -1;
  }
  const entryName = (e, withSource) => e.driver.name + (withSource ? " · " + e.family.name : "");

  /** Point a comparison at one driver (from its detail page) and open the Compare view. */
  function compareDriver(id) {
    const own = groups(false).filter(g => g.entries.some(e => e.driver.id === id));
    if (!own.length) { location.hash = "compare"; return; }
    const g = own.slice().sort((a, b) => a.rank - b.rank || (b.kind.key.startsWith("hd-f") - a.kind.key.startsWith("hd-f")) || driversIn(b) - driversIn(a))[0];
    const mine = g.entries.find(e => e.driver.id === id);
    cmp.mix = false; cmp.src = g.family; cmp.g = g.key; cmp.q = []; cmp.rows = null;
    cmp.picks = [{ id: mine.id, slot: 0 }].concat(g.entries.filter(e => e !== mine).slice(0, CC.MAX_PICK - 1).map((e, i) => ({ id: e.id, slot: i + 1 })));
    location.hash = "compare";
  }

  // Opening the view (from a link or the tabs) reads the settings in the address; changes made on
  // the page redraw it from memory and write the settings back to the address.
  function showCompare() { loadCompare(); renderCompare(); }
  function renderCompare() {
    clearCharts();
    const { srcs, avail, g } = normCompare();
    saveCompare();
    const app = $("app");
    app.classList.add("wide");
    let h = navHtml("compare") + `<h1>Compare drivers</h1>
      <p class="lede">Overlay up to five drivers, each in its own colour and marker. Pick one source, one measurement and what to show. Sources are kept apart because each measures in its own way, so their numbers do not line up.</p>`;
    if (!g) { app.innerHTML = h + `<div class="empty">Nothing to compare yet.</div>`; return; }
    const picked = cmp.picks.map(p => ({ p, e: g.entries.find(x => x.id === p.id) })).filter(x => x.e).sort((a, b) => a.p.slot - b.p.slot);
    const full = cmp.picks.length >= CC.MAX_PICK;
    const view = g.kind.view;

    h += `<div class="panel">`;
    h += `<div class="lbl"><span>Source</span><span class="hint">most reliable first</span></div>`;
    h += `<div class="srcrow">${srcs.map(f => {
      const n = new Set(groups(false).filter(x => x.family === f.name).flatMap(x => x.entries.map(e => e.driver.id))).size;
      return `<button class="srcbtn${!cmp.mix && f.name === cmp.src ? " on" : ""}" data-src="${esc(f.name)}" ${cmp.mix ? "disabled" : ""}>
        <span class="sn">${esc(f.name)}</span>${badge(f)}<span class="cnt">${n} driver${n !== 1 ? "s" : ""}</span></button>`;
    }).join("")}</div>`;
    h += `<label class="ds" style="margin:10px 0 0"><input type="checkbox" id="cmix" ${cmp.mix ? "checked" : ""}> mix sources in one chart (not recommended)</label>`;
    h += `<div class="lbl"><span>Measurement</span></div><select id="cgrp" class="sel">${avail.map(x =>
      `<option value="${esc(x.key)}"${x.key === g.key ? " selected" : ""}>${esc(x.label)} · ${driversIn(x)} driver${driversIn(x) !== 1 ? "s" : ""}${cmp.mix ? " · " + [...new Set(x.entries.map(e => e.family.name))].join(" + ") : ""}</option>`).join("")}</select>`;
    h += `<div class="lbl"><span>Show</span><span class="hint">${view === "curve" ? "one or more; each gets its own line style" : "one at a time"}</span></div><div class="togrow">`;
    h += g.quantityIds.map((id, i) => {
      const on = cmp.q.includes(id);
      const lbl = (g.entries.flatMap(e => e.quantities).find(q => q.id === id) || {}).label || id;
      const dash = view === "curve" && on ? dashSvg(CC.DASHES[cmp.q.indexOf(id) % CC.DASHES.length], "#eef0f6") : "";
      return `<button class="tog${on ? " on" : ""}" data-q="${esc(id)}">${dash}${esc(lbl)}</button>`;
    }).join("");
    if (view === "curve" && g.kind.ratio) h += `<span class="sep"></span><button class="tog${cmp.u === "db" ? " on" : ""}" data-u="db">dB</button><button class="tog${cmp.u === "pct" ? " on" : ""}" data-u="pct">%</button>`;
    h += `</div>`;
    if (view === "table") {
      h += `<div class="lbl"><span>Rows</span><span class="hint">tap to leave a row out</span></div><div class="togrow">${rowLabels(g, cmp.q[0]).map(r =>
        `<button class="tog small${cmp.rows.includes(r) ? " on" : ""}" data-row="${esc(r)}">${esc(r)}</button>`).join("")}</div>`;
    }
    h += `<div class="lbl"><span>Drivers</span><span class="hint">${picked.length} picked · up to ${CC.MAX_PICK}</span></div>`;
    if (g.entries.length > 8) h += `<input class="filter small" id="cfilt" placeholder="filter drivers…">`;
    h += `<div class="picks">${g.entries.map(e => {
      const p = cmp.picks.find(x => x.id === e.id), on = !!p, dis = !on && full;
      const sw = on ? `<span class="sw" style="background:${CC.COLORS[p.slot]};border-color:${CC.COLORS[p.slot]}">${MARK_CHARS[CC.MARKERS[p.slot]]}</span>` : `<span class="sw"></span>`;
      return `<label class="pick${on ? " on" : ""}${dis ? " dis" : ""}" data-text="${esc((e.driver.name + " " + e.family.name).toLowerCase())}">
        <input type="checkbox" data-pick="${esc(e.id)}" ${on ? "checked" : ""} ${dis ? "disabled" : ""}>${sw}
        <span class="pn">${esc(entryName(e, cmp.mix))}</span><span class="pd">${esc(CC.describe(e))}</span></label>`;
    }).join("")}</div>`;
    if (full) h += `<div class="hint2">Five drivers picked: untick one to pick another.</div>`;
    h += `</div>`;

    // chart panel
    h += `<div class="panel"><div class="ptitle">${esc(g.label)}${cmp.mix ? "" : " · " + esc(g.family)} ${cmp.mix ? "" : badge(FAMILIES.find(f => f.name === g.family))}</div>`;
    if (cmp.mix) h += `<div class="warn"><b>Sources mixed.</b> Each source measures differently (distance, room or anechoic, windowing, smoothing, calibration), so differences between sources can be larger than differences between drivers. Use this to see how sources disagree, not to rank drivers. Most reliable first: ${srcs.map(f => esc(f.name) + " (" + esc(f.reliability) + ")").join(", ")}.</div>`;
    if (!picked.length) h += `<div class="empty">Pick at least one driver above.</div>`;
    else {
      h += `<div class="legend">${picked.map(({ p, e }) => `<span class="lg"><span class="lgm" style="color:${CC.COLORS[p.slot]}">${MARK_CHARS[CC.MARKERS[p.slot]]}</span><span class="lgl${view === "curve" ? "" : " sq"}" style="background:${CC.COLORS[p.slot]}"></span>${esc(entryName(e, cmp.mix))}</span>`).join("")}</div>`;
      h += noChart() ? noChartMsg : `<div class="chartbox tall"><canvas id="cchart"></canvas></div>`;
      h += `<div id="csum"></div>`;
      h += `<details class="conds"><summary>Test conditions and sources of the picked drivers</summary>${picked.map(({ p, e }) =>
        `<div class="cond"><span style="color:${CC.COLORS[p.slot]}">${MARK_CHARS[CC.MARKERS[p.slot]]} ${esc(e.driver.name)}</span> <span class="dim">${esc(e.set.type)}${e.set.method ? " · " + esc(e.set.method) : ""}</span>${condChips(e.set.conditions, e.set.source)}${e.set.note ? `<div class="setnote">${esc(e.set.note)}</div>` : ""}</div>`).join("")}</details>`;
    }
    const fam = FAMILIES.find(f => f.name === g.family);
    if (fam && fam.reliability_note) h += `<div class="hint2">${esc(g.family)}: ${esc(fam.reliability_note)}</div>`;
    h += `</div>`;
    app.innerHTML = h;
    wireCompare(g);
    if (picked.length && !noChart()) drawCompare(g, picked);
  }

  function dashSvg(dash, color) {
    return `<svg class="dash" width="22" height="8" aria-hidden="true"><line x1="1" y1="4" x2="21" y2="4" stroke="${color}" stroke-width="2" stroke-dasharray="${(dash || []).join(",")}"/></svg>`;
  }

  function wireCompare(g) {
    document.querySelectorAll("[data-src]").forEach(b => b.onclick = () => { cmp.src = b.dataset.src; cmp.g = null; cmp.q = []; renderCompare(); });
    const mix = $("cmix"); if (mix) mix.onchange = () => {
      cmp.mix = mix.checked;
      const keep = g.kind.key;            // stay on the same measurement where possible
      const target = (cmp.mix ? groups(true) : groups(false)).find(x => x.kind.key === keep && (cmp.mix || x.family === cmp.src));
      cmp.g = target ? target.key : null;
      renderCompare();
    };
    const sel = $("cgrp"); if (sel) sel.onchange = () => { cmp.g = sel.value; cmp.q = []; cmp.picks = null; cmp.rows = null; renderCompare(); };
    document.querySelectorAll("[data-q]").forEach(b => b.onclick = () => {
      const id = b.dataset.q;
      if (g.kind.view !== "curve") cmp.q = [id];
      else if (cmp.q.includes(id)) { if (cmp.q.length > 1) cmp.q = cmp.q.filter(x => x !== id); }
      else cmp.q = cmp.q.concat(id);
      if (g.kind.view === "table") cmp.rows = null;
      renderCompare();
    });
    document.querySelectorAll("[data-u]").forEach(b => b.onclick = () => { cmp.u = b.dataset.u; renderCompare(); });
    document.querySelectorAll("[data-row]").forEach(b => b.onclick = () => {
      const r = b.dataset.row;
      if (cmp.rows.includes(r)) { if (cmp.rows.length > 1) cmp.rows = cmp.rows.filter(x => x !== r); }
      else cmp.rows = rowLabels(g, cmp.q[0]).filter(x => x === r || cmp.rows.includes(x));
      renderCompare();
    });
    document.querySelectorAll("[data-pick]").forEach(cb => cb.onchange = () => {
      const id = cb.dataset.pick;
      if (cb.checked) { const s = freeSlot(); if (s >= 0) cmp.picks.push({ id, slot: s }); }
      else cmp.picks = cmp.picks.filter(p => p.id !== id);
      renderCompare();
    });
    const f = $("cfilt"); if (f) f.oninput = () => {
      const q = f.value.toLowerCase();
      document.querySelectorAll(".pick").forEach(l => { l.style.display = l.dataset.text.includes(q) ? "" : "none"; });
    };
  }

  function drawCompare(g, picked) {
    const cv = $("cchart"), view = g.kind.view;
    if (view === "curve") return drawCompareCurves(g, picked, cv);
    if (view === "bars") return drawCompareBars(g, picked, cv);
    return drawCompareTable(g, picked, cv);
  }

  function drawCompareCurves(g, picked, cv) {
    const units = g.kind.ratio ? cmp.u : "db";
    const ds = [];
    for (const { p, e } of picked) {
      cmp.q.forEach((qid, qi) => {
        const q = e.quantities.find(x => x.id === qid);
        if (!q) return;
        const pts = q.points.map(pt => ({ x: pt.x, y: units === "pct" ? pct(pt.y) : pt.y }));
        const color = CC.COLORS[p.slot];
        ds.push({ label: `${entryName(e, cmp.mix)} · ${q.label}`, data: pts, borderColor: color, backgroundColor: color,
          borderDash: CC.DASHES[qi % CC.DASHES.length], borderWidth: 2.2, tension: 0.2, spanGaps: false,
          pointStyle: CC.MARKERS[p.slot], pointRadius: markerRadius(pts.length, p.slot), pointHoverRadius: 5,
          pointBackgroundColor: color, pointBorderColor: color });
      });
    }
    const yTitle = g.kind.ratio ? (units === "pct" ? "% of fundamental" : "dB re fundamental") : g.kind.yTitle;
    const xFmt = v => (g.kind.xlog ? fmtHz(v) : v.toFixed(1) + " dB");
    newChart(cv, { type: "line", data: { datasets: ds },
      options: chartOptions({ x: xAxis(g.kind.xlog, g.kind.xTitle), y: yAxis(units, yTitle) },
        c => `${c.dataset.label}: ${units === "pct" ? c.parsed.y.toPrecision(3) + " %" : c.parsed.y.toFixed(1) + (g.kind.ratio ? " dB" : "")} at ${xFmt(c.parsed.x)}`) });
    // summary over the range every picked driver covers
    const rows = [];
    cmp.q.forEach(qid => {
      const curves = picked.map(({ p, e }) => ({ p, e, q: e.quantities.find(x => x.id === qid) })).filter(x => x.q);
      if (!curves.length) return;
      const lo = Math.max(...curves.map(c => c.q.points[0].x)), hi = Math.min(...curves.map(c => c.q.points[c.q.points.length - 1].x));
      curves.forEach(c => {
        const inR = c.q.points.filter(pt => pt.x >= lo && pt.x <= hi);
        if (!inR.length) { rows.push({ c, qid, none: true }); return; }
        const ys = inR.map(pt => pt.y).sort((a, b) => a - b);
        const med = ys.length % 2 ? ys[(ys.length - 1) / 2] : (ys[ys.length / 2 - 1] + ys[ys.length / 2]) / 2;
        const hiPt = inR.reduce((a, b) => (b.y > a.y ? b : a)), loPt = inR.reduce((a, b) => (b.y < a.y ? b : a));
        rows.push({ c, qid, med, hiPt, loPt, lo, hi });
      });
    });
    const fv = v => (g.kind.ratio ? (units === "pct" ? fmtPct(v) : fmtDb(v)) : v.toFixed(1));
    const where = x => (g.kind.xlog ? fmtHz(x) : x.toFixed(1) + " dB");
    let t = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Driver</th><th>Shows</th><th>Range used</th><th>Median</th><th>Highest</th><th>Lowest</th></tr></thead><tbody>`;
    t += rows.map(r => `<tr><td><span style="color:${CC.COLORS[r.c.p.slot]}">${MARK_CHARS[CC.MARKERS[r.c.p.slot]]}</span> ${esc(r.c.e.driver.name)}</td><td>${esc(r.qid)}</td>` +
      (r.none ? `<td colspan="4">no range shared with the other picked drivers</td>` :
        `<td>${where(r.lo)} to ${where(r.hi)}</td><td>${fv(r.med)}</td><td>${fv(r.hiPt.y)} at ${where(r.hiPt.x)}</td><td>${fv(r.loPt.y)} at ${where(r.loPt.x)}</td>`) + `</tr>`).join("");
    t += `</tbody></table></div><div class="hint2">Figures are taken over the range all picked drivers cover, so they compare like with like.</div>`;
    $("csum").innerHTML = t;
  }

  // Bars grow up from the bottom of the chart, so a taller bar always means more distortion, also
  // when every value is negative (dB below the fundamental).
  function barBase(values) {
    const v = values.filter(x => x != null);
    if (!v.length) return 0;
    if (v.every(x => x <= 0)) return Math.floor(Math.min(...v) / 10) * 10 - 10;
    return 0;
  }
  function barTop(values) {
    const v = values.filter(x => x != null);
    return v.length && v.every(x => x <= 0) ? Math.min(0, Math.ceil(Math.max(...v) / 10) * 10 + 5) : undefined;
  }

  function drawCompareBars(g, picked, cv) {
    const qid = cmp.q[0];
    const qs = picked.map(({ p, e }) => ({ p, e, q: e.quantities.find(x => x.id === qid) })).filter(x => x.q);
    const relTo = (qs[0] && qs[0].q.relTo) || "dB";
    if (qid === "sum") {
      const vals = qs.map(x => x.q.value);
      const base = barBase(vals);
      newChart(cv, { type: "bar", data: { labels: qs.map(x => x.e.driver.name), datasets: [{ label: "Sum of all products", data: vals,
        backgroundColor: qs.map(x => CC.COLORS[x.p.slot]), base, barPercentage: 0.6 }] },
        options: chartOptions({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 10 }, maxRotation: 30, autoSkip: false } },
          y: yAxis("db", relTo, { min: base, max: barTop(vals) }) }, c => `${c.label}: ${c.parsed.y.toFixed(1)} dB`) });
      $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Driver</th><th>Sum of all products</th><th>as %</th></tr></thead><tbody>${qs.map(x =>
        `<tr><td><span style="color:${CC.COLORS[x.p.slot]}">${MARK_CHARS[CC.MARKERS[x.p.slot]]}</span> ${esc(x.e.driver.name)}</td><td>${fmtDb(x.q.value)}</td><td>${fmtPct(x.q.value)}</td></tr>`).join("")}</tbody></table></div>
        <div class="hint2">Power sum of every product the chart shows, ${esc(relTo)}. Lower is better.</div>`;
      return;
    }
    const freqs = [...new Set(qs.flatMap(x => x.q.points.map(pt => pt.x)))].sort((a, b) => a - b);
    const all = qs.flatMap(x => x.q.points.map(pt => pt.y));
    const base = barBase(all);
    const ds = qs.map(x => ({ label: x.e.driver.name, backgroundColor: CC.COLORS[x.p.slot], base,
      data: freqs.map(f => { const pt = x.q.points.find(q => q.x === f); return pt ? pt.y : null; }) }));
    newChart(cv, { type: "bar", data: { labels: freqs.map(f => fmtHz(f)), datasets: ds },
      options: chartOptions({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 10 }, maxRotation: 50, autoSkip: false },
          title: { display: true, text: "Product frequency", color: TITLE, font: { size: 11 } } },
        y: yAxis("db", relTo, { min: base, max: barTop(all) }) }, c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} dB at ${c.label}`) });
    $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Product</th>${qs.map(x =>
      `<th style="color:${CC.COLORS[x.p.slot]}">${MARK_CHARS[CC.MARKERS[x.p.slot]]} ${esc(x.e.driver.name)}</th>`).join("")}</tr></thead><tbody>${freqs.map(f =>
      `<tr><td>${fmtHz(f)}</td>${qs.map(x => { const pt = x.q.points.find(q => q.x === f); return `<td>${pt ? pt.y.toFixed(1) : "—"}</td>`; }).join("")}</tr>`).join("")}
      <tr class="sumrow"><td>sum</td>${qs.map(x => { const s = x.e.quantities.find(q => q.id === "sum"); return `<td>${s && s.value != null ? s.value.toFixed(1) : "—"}</td>`; }).join("")}</tr></tbody></table></div>
      <div class="hint2">Values in ${esc(relTo)}; the test tones themselves are left out. Taller bars mean more distortion.</div>`;
  }

  function drawCompareTable(g, picked, cv) {
    const qid = cmp.q[0], rows = cmp.rows;
    const qs = picked.map(({ p, e }) => ({ p, e, q: e.quantities.find(x => x.id === qid) })).filter(x => x.q);
    const val = (x, r) => { const row = x.q.rows.find(y => y.label === r); return row ? row.value : null; };
    const tvals = qs.flatMap(x => rows.map(r => val(x, r)));
    const base = barBase(tvals);
    newChart(cv, { type: "bar", data: { labels: rows, datasets: qs.map(x => ({ label: x.e.driver.name, backgroundColor: CC.COLORS[x.p.slot], base,
      data: rows.map(r => val(x, r)) })) },
      options: chartOptions({ x: { grid: { display: false }, ticks: { color: TICK, font: { size: 10 }, maxRotation: 40, autoSkip: false } },
        y: yAxis("db", qid, { min: base || undefined, max: barTop(tvals) }) }, c => `${c.dataset.label}: ${c.parsed.y} (${c.label})`) });
    $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>${esc((g.entries[0].set.columns || [""])[0])}</th>${qs.map(x =>
      `<th style="color:${CC.COLORS[x.p.slot]}">${MARK_CHARS[CC.MARKERS[x.p.slot]]} ${esc(x.e.driver.name)}</th>`).join("")}</tr></thead><tbody>${rows.map(r =>
      `<tr><td>${esc(r)}</td>${qs.map(x => { const v = val(x, r); return `<td>${v == null ? "—" : v}</td>`; }).join("")}</tr>`).join("")}</tbody></table></div>
      <div class="hint2">Column: ${esc(qid)}.</div>`;
  }

  // =====================================================================================
  // Simulate
  // =====================================================================================
  const TYPICAL = SC.LAWS.typical.slopes;
  const sim = { mix: false, src: null, n: 3, w: null, c: [1, 1, 1, 1], x: null, t: null, L: 94, law: "measured",
                s: Object.assign({}, TYPICAL), al: true, o: null, u: "db", sh: null };

  function loadSim() {
    const p = params();
    if (![...p.keys()].length) return;
    const nums = k => (p.get(k) || "").split(",").filter(x => x !== "").map(Number);
    sim.mix = p.get("mix") === "1";
    sim.src = p.get("src");
    sim.n = [2, 3, 4].includes(Number(p.get("n"))) ? Number(p.get("n")) : 3;
    sim.w = p.get("w") ? p.get("w").split(",") : null;
    const c = nums("c"); if (c.length) sim.c = [0, 1, 2, 3].map(i => (c[i] >= 1 && c[i] <= 4 ? c[i] : 1));
    sim.x = nums("x").length ? nums("x") : null;
    sim.t = p.get("t") ? p.get("t").split(",") : null;
    if (p.get("L") && isFinite(Number(p.get("L")))) sim.L = Number(p.get("L"));
    if (["measured", "typical", "classic", "none"].includes(p.get("law"))) sim.law = p.get("law");
    const s = nums("s"); if (s.length === 4 && s.every(isFinite)) ORDERS.forEach((k, i) => (sim.s[k] = s[i]));
    sim.al = p.get("al") !== "0";
    sim.o = p.get("o") ? p.get("o").split(",") : null;
    sim.u = p.get("u") === "pct" ? "pct" : "db";
    sim.sh = p.get("sh") || null;
  }
  function saveSim() {
    save("simulate", { mix: sim.mix ? "1" : "", src: sim.mix ? "" : sim.src, n: sim.n, w: sim.w.join(","), c: sim.c.slice(0, sim.n).join(","),
      x: sim.x.join(","), t: sim.t.join(","), L: sim.L, law: sim.law, s: ORDERS.map(k => sim.s[k]).join(","), al: sim.al ? "" : "0",
      o: sim.o.join(","), u: sim.u === "pct" ? "pct" : "", sh: sim.sh || "" });
  }

  // Candidates: every sound-pressure harmonic distortion curve with a known test level.
  function candidates(mix, src) {
    const out = [];
    for (const g of groups(mix)) {
      if (!g.kind.key.startsWith("hd-f|") || g.kind.level == null) continue;
      for (const e of g.entries) if (mix || e.family.name === src) {
        const hd = {};
        e.quantities.forEach(q => { if (ORDERS.includes(q.id)) hd[q.id] = q.points; });
        if (!hd.H2 && !hd.H3) continue;
        const xs = Object.values(hd).flat().map(p => p.x);
        out.push({ id: e.id, e, hd, L0: g.kind.level, orders: ORDERS.filter(k => hd[k]), lo: Math.min(...xs), hi: Math.max(...xs) });
      }
    }
    return out.sort((a, b) => a.e.driver.name.localeCompare(b.e.driver.name) || a.L0 - b.L0);
  }
  function simSources() {
    const names = new Set(candidates(true).map(c => c.e.family.name));
    return FAMILIES.filter(f => names.has(f.name)).slice().sort((a, b) => (a.rank || 99) - (b.rank || 99));
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
  // Default driver for each way: the one whose role fits the way and whose data covers the way's band
  // (one octave either side of its crossovers), each driver used once where possible.
  function autoPick(n, x, cands) {
    const used = new Set(), out = [];
    for (let i = 0; i < n; i++) {
      const lo = Math.max(20, (i === 0 ? 20 : x[i - 1]) / 2), hi = Math.min(20000, (i === n - 1 ? 20000 : x[i]) * 2);
      const width = Math.log(hi / lo), pos = i / (n - 1);
      const score = c => Math.max(0, Math.log(Math.min(hi, c.hi) / Math.max(lo, c.lo))) / width - 1.2 * Math.abs(rolePos(c.e.driver.role) - pos) +
        c.orders.length * 0.01 + (used.has(c.id) ? -2 : 0);
      const best = cands.slice().sort((a, b) => score(b) - score(a))[0];
      out.push(best ? best.id : null);
      if (best) used.add(best.id);
    }
    return out;
  }
  function normSim() {
    const srcs = simSources();
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
    const avail = ORDERS.filter(k => chosen.length && chosen.every(c => c.hd[k]));
    const shows = avail.concat(avail.length ? ["THD"] : []);
    sim.o = (sim.o || []).filter(k => shows.includes(k));
    if (!sim.o.length) sim.o = shows.filter(k => ["H2", "H3", "THD"].includes(k));
    if (!shows.includes(sim.sh)) sim.sh = shows[0] || null;
    return { srcs, cands, chosen, avail, shows };
  }

  /** How a driver's distortion moves with level: returns {fn(order, f), text}. */
  function slopeFor(c) {
    const base = k => (sim.law === "classic" ? SC.LAWS.classic.slopes[k] : sim.law === "none" ? 0 : sim.s[k]);
    if (sim.law !== "measured") return { fn: k => base(k), text: sim.law === "none" ? "no level change" : sim.law === "classic" ? "textbook (n−1) rule" : "slopes set below" };
    // Level sweeps of the same driver from the same source (Purifi datasheets have them).
    const centre = (c.L0 + sim.L) / 2, half = Math.max(6, Math.abs(sim.L - c.L0) / 2 + 3);
    const byOrder = {};
    let clamped = false;
    (c.e.driver.measurements || []).forEach(set => {
      if (CC.kindOf(set).key !== "hd-level") return;
      const fam = CC.familyOf(set, FAMILIES);
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
    const text = measured.length
      ? "measured sweep: " + measured.sort().map(k => k + " " + byOrder[k].sort((a, b) => a.f - b.f).map(x => x.slope.toFixed(2) + " at " + fmtHz(x.f)).join(", ")).join("; ") +
        (ORDERS.some(k => !curves[k] && c.hd[k]) ? "; others from the slopes below" : "") +
        (clamped ? ". A falling measured slope counts as 0: the sweep is at the measurement's noise floor there" : "")
      : "no level sweep from this source: slopes below";
    return { fn: (k, f) => (curves[k] ? curves[k](f) : base(k)), text };
  }

  function showSimulate() { loadSim(); renderSimulate(); }
  function renderSimulate() {
    clearCharts();
    const { srcs, cands, chosen, avail, shows } = normSim();
    saveSim();
    const app = $("app");
    app.classList.add("wide");
    let h = navHtml("simulate") + `<h1>Simulate a speaker</h1>
      <p class="lede">Estimates a 2-, 3- or 4-way speaker's harmonic distortion from each driver's measured curves and the crossover you choose. Drivers come from one source at a time, the same as in Compare.</p>`;
    if (!srcs.length) { app.innerHTML = h + `<div class="empty">No harmonic distortion curves in the database yet.</div>`; return; }
    const names = WAY_NAMES[sim.n];
    h += `<div class="panel">`;
    h += `<div class="lbl"><span>Source</span><span class="hint">most reliable first</span></div><div class="srcrow">${srcs.map(f => {
      const n = new Set(candidates(false, f.name).map(c => c.e.driver.id)).size;
      return `<button class="srcbtn${!sim.mix && f.name === sim.src ? " on" : ""}" data-ssrc="${esc(f.name)}" ${sim.mix ? "disabled" : ""}><span class="sn">${esc(f.name)}</span>${badge(f)}<span class="cnt">${n} driver${n !== 1 ? "s" : ""}</span></button>`;
    }).join("")}</div>`;
    h += `<label class="ds" style="margin:10px 0 0"><input type="checkbox" id="smix" ${sim.mix ? "checked" : ""}> mix sources (not recommended)</label>`;
    h += `<div class="grid2">
      <div><div class="lbl"><span>Ways</span></div><div class="togrow">${[2, 3, 4].map(n => `<button class="tog${sim.n === n ? " on" : ""}" data-n="${n}">${n}-way</button>`).join("")}</div></div>
      <div><div class="lbl"><span>Level</span><span class="hint">dB SPL at 1 m</span></div><input type="number" class="num" id="sL" min="60" max="125" step="1" value="${sim.L}"></div>
    </div>`;
    h += `<div class="lbl"><span>Drivers and crossovers</span><span class="hint">low to high</span></div><div class="ways">`;
    for (let i = 0; i < sim.n; i++) {
      const col = CC.COLORS[i];
      h += `<div class="way"><span class="wdot" style="background:${col}">${MARK_CHARS[CC.MARKERS[i]]}</span><div class="wbody">
        <div class="wname">Way ${i + 1} · ${names[i]}</div>
        <select class="sel" data-way="${i}">${cands.map(c => `<option value="${esc(c.id)}"${c.id === sim.w[i] ? " selected" : ""}>${esc(c.e.driver.name)}${sim.mix ? " · " + esc(c.e.family.name) : ""} · ${c.L0} dB · ${fmtHz(c.lo)} to ${fmtHz(c.hi)} · ${c.orders.join(" ")}</option>`).join("")}</select>
        <div class="wmeta"><label>drivers in this way <select class="sel mini" data-count="${i}">${[1, 2, 3, 4].map(k => `<option${sim.c[i] === k ? " selected" : ""}>${k}</option>`).join("")}</select></label></div>
      </div></div>`;
      if (i < sim.n - 1) h += `<div class="xo"><span class="xol">crossover ${i + 1}</span>
        <input type="number" class="num" data-xf="${i}" min="20" max="20000" step="10" value="${sim.x[i]}"><span class="dim">Hz</span>
        <select class="sel mini" data-xt="${i}">${Object.entries(SC.TYPES).map(([k, t]) => `<option value="${k}"${sim.t[i] === k ? " selected" : ""}>${esc(t.label)}</option>`).join("")}</select></div>`;
    }
    h += `</div>`;
    h += `<div class="grid2">
      <div><div class="lbl"><span>Summing</span></div><select class="sel" id="sal">
        <option value="1"${sim.al ? " selected" : ""}>Ways sum flat (lower ways phase-matched with all-pass filters)</option>
        <option value="0"${sim.al ? "" : " selected"}>Plain filters (the sum dips between close crossovers)</option></select></div>
      <div><div class="lbl"><span>How distortion changes with level</span></div><select class="sel" id="slaw">
        <option value="measured"${sim.law === "measured" ? " selected" : ""}>Measured sweeps (Purifi datasheets), else the slopes below</option>
        <option value="typical"${sim.law === "typical" ? " selected" : ""}>The slopes below for every driver</option>
        <option value="classic"${sim.law === "classic" ? " selected" : ""}>Textbook rule: H2 +1, H3 +2, H4 +3, H5 +4 (over-predicts)</option>
        <option value="none"${sim.law === "none" ? " selected" : ""}>No change: the curves as measured</option></select></div>
    </div>`;
    if (sim.law === "measured" || sim.law === "typical") {
      h += `<div class="lbl"><span>Slopes</span><span class="hint">dB of distortion per dB of level · typical from your data: H2 1.0, H3 to H5 0.7</span></div><div class="togrow">${ORDERS.map(k =>
        `<label class="slope">${k} <input type="number" class="num mini" data-slope="${k}" step="0.05" min="-1" max="5" value="${sim.s[k]}"></label>`).join("")}<button class="tog" id="sreset">typical</button></div>`;
    }
    h += `</div>`;

    // results
    const warnings = [];
    let res = null;
    if (chosen.length === sim.n && avail.length) {
      const slopes = chosen.map(c => slopeFor(c));
      let fLo = Math.max(20, chosen[0].lo), fHi = Math.min(20000, chosen[sim.n - 1].hi);
      if (!(fHi > fLo * 1.5)) { fLo = 20; fHi = 20000; }
      res = SC.simulate({ freqs: SC.logGrid(fLo, fHi, 24), target: sim.L, orders: avail, aligned: sim.al,
        points: sim.x.map((fc, i) => ({ fc, type: sim.t[i] })),
        ways: chosen.map((c, i) => ({ name: c.e.driver.name, L0: c.L0, hd: c.hd, slope: slopes[i].fn, count: sim.c[i] })) });
      res.slopes = slopes;
      res.range = [res.freqs[0], res.freqs[res.freqs.length - 1]];
      const merged = [];
      for (const gp of res.gaps) {
        const m = merged.find(x => x.way === gp.way && x.from === gp.from && x.to === gp.to);
        if (m) m.orders.push(gp.order); else merged.push({ way: gp.way, from: gp.from, to: gp.to, orders: [gp.order] });
      }
      const list = a => (a.length > 1 ? a.slice(0, -1).join(", ") + " and " + a[a.length - 1] : a[0]);
      for (const gp of merged) {
        warnings.push(`Way ${gp.way + 1} (${esc(chosen[gp.way].e.driver.name)}) has no ${list(gp.orders)} data from ${fmtHz(gp.from)} to ${fmtHz(gp.to)}, where it still plays within 40 dB of the other ways. The speaker's ${list(gp.orders)} and THD are left empty there rather than guessed.`);
      }
      // Excursion: calculated maximum level (Derived source) against the level the way has to play.
      chosen.forEach((c, i) => {
        const mx = (c.e.driver.measurements || []).find(m => /^max spl/i.test(m.type || "") && m.series && m.series[0]);
        if (!mx) return;
        const pts = mx.series[0].points.map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
        const over = res.freqs.filter((f, j) => { const m = SC.interpLog(pts, f); return m != null && sim.L + res.response.ways[i][j] > m + 20 * Math.log10(sim.c[i]); });
        if (over.length) warnings.push(`Way ${i + 1} (${esc(c.e.driver.name)}${sim.c[i] > 1 ? " ×" + sim.c[i] : ""}) cannot reach ${sim.L} dB from ${fmtHz(over[0])} to ${fmtHz(over[over.length - 1])}: it runs out of excursion there (${esc(mx.type)}, calculated, not measured). Its distortion there is higher than shown.`);
      });
      sim.x.forEach((fc, i) => { if (i > 0 && fc / sim.x[i - 1] < 2) warnings.push(`Crossovers ${i} and ${i + 1} are less than an octave apart (${fmtHz(sim.x[i - 1])} and ${fmtHz(fc)}); the middle way then never plays at full level.`); });
      if (sim.L > 100) warnings.push(`At ${sim.L} dB the drivers play well above the level they were measured at, so the result leans on the level rule more than on the measurements.`);
    } else if (chosen.length === sim.n) warnings.push("The picked drivers share no harmonic order (one source has only H2 and H3, another only H4 and H5).");
    const thdLabel = avail.length === 4 ? "THD" : `THD (${avail.join(" + ")} only)`;
    h += `<div class="panel"><div class="ptitle">Speaker distortion at ${sim.L} dB · ${sim.n}-way${sim.mix ? " · sources mixed" : " · " + esc(sim.src) + " " + badge(FAMILIES.find(f => f.name === sim.src))}</div>`;
    if (sim.mix) h += `<div class="warn"><b>Sources mixed.</b> The drivers were measured by different sources, which measure in different ways; the result mixes their errors. Prefer one source.</div>`;
    h += `<div class="togrow">${shows.map(k => `<button class="tog${sim.o.includes(k) ? " on" : ""}" data-o="${k}"><span class="odot" style="background:${ORDER_COLORS[k]}"></span>${k === "THD" ? esc(thdLabel) : k}</button>`).join("")}
      <span class="sep"></span><button class="tog${sim.u === "db" ? " on" : ""}" data-su="db">dB</button><button class="tog${sim.u === "pct" ? " on" : ""}" data-su="pct">%</button></div>`;
    h += res ? (noChart() ? noChartMsg : `<div class="chartbox tall"><canvas id="schart"></canvas></div>`) : `<div class="empty">Nothing to show.</div>`;
    if (res) h += `<div class="hint2">Simulated from ${fmtHz(res.range[0])} to ${fmtHz(res.range[1])}, where the lowest and the highest way have data.</div><div id="ssum"></div>`;
    h += warnings.map(w => `<div class="warn">${w}</div>`).join("");
    h += `</div>`;
    if (res) {
      h += `<div class="panel"><div class="ptitle">Each driver's share</div><div class="togrow">${shows.map(k => `<button class="tog${sim.sh === k ? " on" : ""}" data-sh="${k}">${k === "THD" ? esc(thdLabel) : k}</button>`).join("")}</div>
        <div class="legend">${chosen.map((c, i) => `<span class="lg"><span class="lgm" style="color:${CC.COLORS[i]}">${MARK_CHARS[CC.MARKERS[i]]}</span><span class="lgl dashed" style="border-color:${CC.COLORS[i]}"></span>Way ${i + 1}: ${esc(c.e.driver.name)}${sim.c[i] > 1 ? " ×" + sim.c[i] : ""}</span>`).join("")}<span class="lg"><span class="lgl" style="background:#eef0f6"></span>speaker</span></div>
        ${noChart() ? "" : `<div class="chartbox"><canvas id="sshare"></canvas></div>`}
        <div class="hint2">Each way's harmonics relative to the speaker's summed output, so the shares add up (as power) to the speaker line.</div></div>`;
      h += `<div class="panel"><div class="ptitle">Crossover: level of each way</div>
        <div class="legend">${chosen.map((c, i) => `<span class="lg"><span class="lgl" style="background:${CC.COLORS[i]}"></span>Way ${i + 1}</span>`).join("")}<span class="lg"><span class="lgl" style="background:#eef0f6"></span>sum</span></div>
        ${noChart() ? "" : `<div class="chartbox"><canvas id="sresp"></canvas></div>`}</div>`;
      h += `<div class="panel"><div class="ptitle">How the level rule was applied</div>${chosen.map((c, i) =>
        `<div class="cond"><span style="color:${CC.COLORS[i]}">${MARK_CHARS[CC.MARKERS[i]]} Way ${i + 1}: ${esc(c.e.driver.name)}</span> <span class="dim">measured at ${c.L0} dB · ${esc(res.slopes[i].text)}</span>${condChips(c.e.set.conditions, c.e.set.source)}</div>`).join("")}
        <details class="conds"><summary>How this is calculated</summary><ul class="how">
          <li>Each way receives the signal through its crossover filters. The drivers are assumed to be level-matched and flat, so a way plays at the chosen level times its filter response.</li>
          <li>A driver's harmonic curve (measured at ${[...new Set(chosen.map(c => c.L0))].join(" and ")} dB) is moved to the level the driver actually plays at each frequency: harmonic ratio + slope × (level − measured level). Near a crossover a driver plays 6 dB lower (Linkwitz-Riley) or 3 dB lower (Butterworth), so its distortion drops.</li>
          <li>Several identical drivers in one way share the level: two drivers each play 6 dB lower.</li>
          <li>Harmonics of different drivers are added as powers, because their phases are unknown. The result is relative to the speaker's summed output.</li>
          <li>A driver more than 40 dB below the others at a frequency is ignored there. Where a driver that matters has no data, the result is left empty.</li>
          <li>Not included: the drivers' own frequency response and baffle, Doppler intermodulation between ways, and cabinet or port noise. Intermodulation is compared in the Compare view instead.</li>
        </ul></details></div>`;
    }
    app.innerHTML = h;
    wireSimulate();
    if (res && !noChart()) drawSimulate(res, chosen, avail, thdLabel);
  }

  function wireSimulate() {
    const rerender = () => renderSimulate();
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

  function drawSimulate(res, chosen, avail, thdLabel) {
    const u = sim.u, conv = v => (u === "pct" ? pct(v) : v);
    const yT = u === "pct" ? "% of fundamental" : "dB re fundamental";
    const series = k => res.freqs.map((f, i) => ({ x: f, y: conv(res.system[k][i]) }));
    const lbl = k => (k === "THD" ? thdLabel : k);
    const tip = c => `${c.dataset.label}: ${c.parsed.y == null ? "—" : u === "pct" ? c.parsed.y.toPrecision(3) + " %" : c.parsed.y.toFixed(1) + " dB"} at ${fmtHz(c.parsed.x)}`;
    newChart($("schart"), { type: "line", data: { datasets: sim.o.map(k => ({ label: lbl(k), data: series(k), borderColor: ORDER_COLORS[k], backgroundColor: ORDER_COLORS[k],
      borderWidth: k === "THD" ? 3 : 2, pointRadius: 0, spanGaps: false, tension: 0.15 })) },
      options: chartOptions({ x: xAxis(true, "Frequency of the fundamental (Hz)", 20, 20000), y: yAxis(u, yT) }, tip) });
    // share chart
    const k = sim.sh;
    const shareSets = chosen.map((c, i) => ({ label: `Way ${i + 1}`, borderColor: CC.COLORS[i], backgroundColor: CC.COLORS[i], borderDash: [6, 4], borderWidth: 2,
      pointStyle: CC.MARKERS[i], pointRadius: markerRadius(res.freqs.length, i), pointBackgroundColor: CC.COLORS[i], spanGaps: false, tension: 0.15,
      data: res.freqs.map((f, j) => {
        const clip = v => (v == null || v < -120 ? null : conv(v));   // shares 120 dB down do not matter
        if (k !== "THD") return { x: f, y: clip(res.contrib[i][k][j]) };
        const parts = avail.map(o => res.contrib[i][o][j]);
        return { x: f, y: parts.every(v => v == null) ? null : clip(10 * Math.log10(parts.reduce((s, v) => s + (v == null ? 0 : Math.pow(10, v / 10)), 0))) };
      }) }));
    shareSets.push({ label: "speaker", data: series(k), borderColor: "#eef0f6", backgroundColor: "#eef0f6", borderWidth: 2.5, pointRadius: 0, spanGaps: false, tension: 0.15 });
    newChart($("sshare"), { type: "line", data: { datasets: shareSets }, options: chartOptions({ x: xAxis(true, "Frequency (Hz)", 20, 20000), y: yAxis(u, yT) }, tip) });
    // crossover response
    const resp = chosen.map((c, i) => ({ label: `Way ${i + 1}`, borderColor: CC.COLORS[i], backgroundColor: CC.COLORS[i], borderWidth: 2, pointRadius: 0,
      data: res.freqs.map((f, j) => ({ x: f, y: Math.max(-60, res.response.ways[i][j]) })) }));
    resp.push({ label: "sum", borderColor: "#eef0f6", backgroundColor: "#eef0f6", borderWidth: 2.5, pointRadius: 0, data: res.freqs.map((f, j) => ({ x: f, y: res.response.sum[j] })) });
    newChart($("sresp"), { type: "line", data: { datasets: resp }, options: chartOptions({ x: xAxis(true, "Frequency (Hz)", 20, 20000),
      y: yAxis("db", "Level (dB)", { min: -40, max: 6 }) }, c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} dB at ${fmtHz(c.parsed.x)}`) });
    // worst and median per shown order, in three bands
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
    t += `</tbody></table></div>`;
    $("ssum").innerHTML = t;
  }

  window.Tools = { showCompare, showSimulate, compareDriver };
})();
