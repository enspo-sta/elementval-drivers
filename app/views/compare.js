/* compare.js: the Compare tab. Overlays up to five drivers from one source, one measurement at a
 * time, showing only the quantities picked (for example only H3, or only the intermodulation
 * products). Levels are matched: every driver is drawn at its measured level closest to the target
 * level, and harmonic curves can be moved the rest of the way with the level rule. */
import { registerView } from "../core/registry.js";
import { store, driverById, fmtHz } from "../core/data.js";
import { COLORS, MARKERS, MARK_CHARS, DASHES, MAX_PICK, TYPICAL_SLOPES, buildGroups, sourcesOf, defaultLevel, pickSet,
         shiftQuantities, describe } from "../core/compare.js";
import { curvesOfSet } from "../core/curves.js";
import { writeHash, hasParams } from "../core/state.js";
import { $, app, esc, navHtml, beginView, newChart, noChart, noChartMsg, xAxis, yAxis, categoryAxis, chartOptions, markerRadius,
         barBase, barTop, badge, familyByName, condChips, exportHtml, wireExports, pct, fmtDb, fmtPct } from "../core/ui.js";

const cmp = { mix: false, src: null, g: null, q: [], picks: null, u: "db", rows: null, L: null, shift: false, filt: "", pickScroll: 0 };
const cache = {};
const groups = mix => cache[mix ? "mix" : "one"] || (cache[mix ? "mix" : "one"] = buildGroups({ mix }));
const driversIn = g => new Set(g.entries.map(e => e.driver.id)).size;

function load(params) {
  if (!hasParams(params)) return;
  if (params.get("driver")) return focusDriver(params.get("driver"));
  cmp.mix = params.get("mix") === "1";
  cmp.src = params.get("src");
  cmp.g = params.get("g");
  cmp.q = (params.get("q") || "").split(",").filter(Boolean);
  const d = (params.get("d") === "none" ? [] : (params.get("d") || "").split(",").filter(Boolean)).slice(0, MAX_PICK);
  cmp.picks = d.length ? d.map((id, slot) => ({ id, slot })) : (params.has("d") ? [] : null);
  cmp.u = params.get("u") === "pct" ? "pct" : "db";
  cmp.rows = params.get("r") ? params.get("r").split("|") : null;
  cmp.L = params.get("L") != null && isFinite(Number(params.get("L"))) ? Number(params.get("L")) : null;
  cmp.shift = params.get("shift") === "1";
}
function save() {
  writeHash("compare", {
    mix: cmp.mix ? "1" : "", src: cmp.mix ? "" : cmp.src, g: cmp.g, q: cmp.q.join(","),
    d: cmp.picks && !cmp.picks.length ? "none" : (cmp.picks || []).slice().sort((a, b) => a.slot - b.slot).map(p => p.id).join(","),
    u: cmp.u === "pct" ? "pct" : "", r: cmp.rows ? cmp.rows.join("|") : "", L: cmp.L, shift: cmp.shift ? "1" : "",
  });
}

/** Open Compare on one driver (from its page): its best-ranked source, preferring harmonic curves. */
function focusDriver(id) {
  const own = groups(false).filter(g => g.entries.some(e => e.driver.id === id));
  if (!own.length) return;
  const g = own.slice().sort((a, b) => a.rank - b.rank || (b.kind.id === "hd-frequency") - (a.kind.id === "hd-frequency") || driversIn(b) - driversIn(a))[0];
  const mine = g.entries.find(e => e.driver.id === id);
  Object.assign(cmp, { mix: false, src: g.family, g: g.key, q: [], rows: null, shift: false,
    // the level the driver you came from was measured at (its level closest to the group's usual one)
    L: mine.sets.some(s => s.level != null) ? pickSet(mine, defaultLevel(g)).level : null,
    picks: [{ id: mine.id, slot: 0 }].concat(g.entries.filter(e => e !== mine).slice(0, MAX_PICK - 1).map((e, i) => ({ id: e.id, slot: i + 1 }))) });
}

function rowLabels(g, qid) {
  const out = [];
  g.entries.forEach(e => e.sets.forEach(s => s.quantities.filter(q => q.id === qid).forEach(q => q.rows.forEach(r => { if (!out.includes(r.label)) out.push(r.label); }))));
  return out;
}
function defaultGroup(list) {
  const score = g => (g.kind.id === "hd-frequency" ? 1000 : 0) + driversIn(g);
  return list.slice().sort((a, b) => score(b) - score(a))[0] || null;
}

function normalise() {
  const srcs = sourcesOf(groups(false), store.families);
  if (!srcs.some(f => f.name === cmp.src)) cmp.src = srcs.length ? srcs[0].name : null;
  const avail = cmp.mix ? groups(true) : groups(false).filter(g => g.family === cmp.src);
  let g = avail.find(x => x.key === cmp.g);
  if (!g) { g = defaultGroup(avail); cmp.g = g ? g.key : null; cmp.picks = null; cmp.rows = null; cmp.L = null; }
  if (!g) return { srcs, avail, g: null };
  cmp.q = cmp.q.filter(id => g.quantityIds.includes(id));
  if (g.kind.view !== "curve") cmp.q = cmp.q.slice(0, 1);
  if (!cmp.q.length) cmp.q = [g.quantityIds[0]];
  if (cmp.picks) cmp.picks = cmp.picks.filter(p => g.entries.some(e => e.id === p.id));
  if (!cmp.picks) cmp.picks = g.entries.slice(0, MAX_PICK).map((e, slot) => ({ id: e.id, slot }));
  if (g.levels.length) { if (cmp.L == null || !(cmp.L >= 40 && cmp.L <= 140)) cmp.L = defaultLevel(g); }
  else cmp.L = null;
  if (!g.kind.ratio || g.kind.id !== "hd-frequency") cmp.shift = false;
  if (g.kind.view === "table") {
    const labels = rowLabels(g, cmp.q[0]);
    cmp.rows = (cmp.rows || []).filter(r => labels.includes(r));
    if (!cmp.rows.length) cmp.rows = labels.slice();
  } else cmp.rows = null;
  return { srcs, avail, g };
}
const freeSlot = () => { for (let s = 0; s < MAX_PICK; s++) if (!cmp.picks.some(p => p.slot === s)) return s; return -1; };
const entryName = e => e.driver.name + (cmp.mix ? " · " + e.family.name : "");
const lv = L => (L == null ? "" : `${Math.round(L * 10) / 10} dB`);

/** Picked entries with the set used for each (closest level) and its quantities (moved if asked). */
function resolvePicks(g) {
  return cmp.picks.map(p => ({ p, e: g.entries.find(x => x.id === p.id) })).filter(x => x.e).sort((a, b) => a.p.slot - b.p.slot).map(x => {
    const chosen = pickSet(x.e, cmp.L);
    let quantities = chosen.quantities;
    if (cmp.shift && chosen.delta) quantities = shiftQuantities(quantities, chosen.level, cmp.L, TYPICAL_SLOPES);
    return Object.assign(x, { chosen, quantities });
  });
}
const levelNote = x => (x.chosen.level == null ? "" : ` · ${lv(x.chosen.level)}${x.chosen.delta ? (cmp.shift && x.chosen.delta ? `, moved to ${lv(cmp.L)}` : ` (${x.chosen.delta > 0 ? "+" : ""}${Math.round(x.chosen.delta * 10) / 10} dB from target)`) : ""}`);

function render() {
  beginView(true);
  const { srcs, avail, g } = normalise();
  save();
  let h = navHtml("compare") + `<h1>Compare drivers</h1>
    <p class="lede">Overlay up to five drivers, each in its own colour and marker. Pick one source, one measurement and what to show. Levels are matched: each driver is drawn at its measured level closest to the target.</p>`;
  if (!g) { app().innerHTML = h + `<div class="empty">Nothing to compare yet.</div>`; return; }
  const picked = resolvePicks(g);
  const full = cmp.picks.length >= MAX_PICK, view = g.kind.view;
  h += `<div class="panel"><div class="lbl"><span>Source</span><span class="hint">most reliable first</span></div><div class="srcrow">${srcs.map(f => {
    const n = new Set(groups(false).filter(x => x.family === f.name).flatMap(x => x.entries.map(e => e.driver.id))).size;
    return `<button class="srcbtn${!cmp.mix && f.name === cmp.src ? " on" : ""}" data-src="${esc(f.name)}" ${cmp.mix ? "disabled" : ""}><span class="sn">${esc(f.name)}</span>${badge(f)}<span class="cnt">${n} driver${n !== 1 ? "s" : ""}</span></button>`;
  }).join("")}</div>
    <label class="ds" style="margin:10px 0 0"><input type="checkbox" id="cmix" ${cmp.mix ? "checked" : ""}> mix sources in one chart (not recommended)</label>
    <div class="lbl"><span>Measurement</span></div><select id="cgrp" class="sel">${avail.map(x =>
      `<option value="${esc(x.key)}"${x.key === g.key ? " selected" : ""}>${esc(x.label)} · ${driversIn(x)} driver${driversIn(x) !== 1 ? "s" : ""}${x.levels.length > 1 ? " · " + x.levels.length + " levels" : ""}${cmp.mix ? " · " + [...new Set(x.entries.map(e => e.family.name))].join(" + ") : ""}</option>`).join("")}</select>`;
  if (g.levels.length) {
    const count = L => g.entries.filter(e => e.sets.some(s => (g.kind.level === "spl-near" ? Math.abs(s.level - L) <= 1 : s.level === L))).length;
    h += `<div class="lbl"><span>Level</span><span class="hint">each driver uses its measured level closest to this</span></div>
      <div class="togrow"><input type="number" class="num" id="cL" min="40" max="140" step="1" value="${cmp.L}"><span class="dim">dB SPL at 1 m</span><span class="sep"></span>
      ${g.levels.map(L => `<button class="tog small${L === cmp.L ? " on" : ""}" data-lvl="${L}">${lv(L)} · ${count(L)}</button>`).join("")}</div>`;
    if (g.kind.id === "hd-frequency") h += `<label class="ds" style="margin:8px 0 0"><input type="checkbox" id="cshift" ${cmp.shift ? "checked" : ""}> move each curve the rest of the way to the target with the level rule (H2 +1.0, H3 to H5 +0.7 dB per dB)</label>`;
  }
  h += `<div class="lbl"><span>Show</span><span class="hint">${view === "curve" ? "one or more; each gets its own line style" : "one at a time"}</span></div><div class="togrow">`;
  h += g.quantityIds.map(id => {
    const on = cmp.q.includes(id);
    const lbl = (g.entries.flatMap(e => e.sets.flatMap(s => s.quantities)).find(q => q.id === id) || {}).label || id;
    return `<button class="tog${on ? " on" : ""}" data-q="${esc(id)}">${view === "curve" && on ? dashSvg(DASHES[cmp.q.indexOf(id) % DASHES.length]) : ""}${esc(lbl)}</button>`;
  }).join("");
  if (view === "curve" && g.kind.ratio) h += `<span class="sep"></span><button class="tog${cmp.u === "db" ? " on" : ""}" data-u="db">dB</button><button class="tog${cmp.u === "pct" ? " on" : ""}" data-u="pct">%</button>`;
  h += `</div>`;
  if (view === "table") h += `<div class="lbl"><span>Rows</span><span class="hint">tap to leave a row out</span></div><div class="togrow">${rowLabels(g, cmp.q[0]).map(r =>
    `<button class="tog small${cmp.rows.includes(r) ? " on" : ""}" data-row="${esc(r)}">${esc(r)}</button>`).join("")}</div>`;
  h += `<div class="lbl"><span>Drivers</span><span class="hint">${picked.length} picked · up to ${MAX_PICK}</span></div>`;
  if (g.entries.length > 8) h += `<input class="filter small" id="cfilt" placeholder="filter drivers…" value="${esc(cmp.filt)}" autocomplete="off">`;
  h += `<div class="picks">${g.entries.map(e => {
    const p = cmp.picks.find(x => x.id === e.id), on = !!p, dis = !on && full;
    const sw = on ? `<span class="sw" style="background:${COLORS[p.slot]};border-color:${COLORS[p.slot]}">${MARK_CHARS[MARKERS[p.slot]]}</span>` : `<span class="sw"></span>`;
    return `<label class="pick${on ? " on" : ""}${dis ? " dis" : ""}" data-text="${esc((e.driver.name + " " + e.family.name).toLowerCase())}">
      <input type="checkbox" data-pick="${esc(e.id)}" ${on ? "checked" : ""} ${dis ? "disabled" : ""}>${sw}
      <span class="pn">${esc(entryName(e))}</span><span class="pd">${esc(describe(e))}</span></label>`;
  }).join("")}</div>${full ? `<div class="hint2">Five drivers picked: untick one to pick another.</div>` : ""}</div>`;

  const fam = familyByName(g.family);
  h += `<div class="panel"><div class="ptitle">${esc(g.label)}${cmp.L != null ? " · target " + lv(cmp.L) : ""}${cmp.mix ? "" : " · " + esc(g.family) + " " + badge(fam)}</div>`;
  if (cmp.mix) h += `<div class="warn"><b>Sources mixed.</b> Each source measures differently (distance, room or anechoic, windowing, smoothing, calibration), so differences between sources can be larger than differences between drivers. Use this to see how sources disagree, not to rank drivers. Most reliable first: ${srcs.map(f => esc(f.name) + " (" + esc(f.reliability) + ")").join(", ")}.</div>`;
  const off = picked.filter(x => x.chosen.delta && !(g.kind.level === "spl-near" && Math.abs(x.chosen.delta) < 1));
  if (off.length && !cmp.shift) h += `<div class="warn">Not measured at ${lv(cmp.L)}: ${off.map(x => `${esc(x.e.driver.name)} (nearest ${lv(x.chosen.level)})`).join(", ")}. Its nearest level is drawn${g.kind.id === "hd-frequency" ? "; tick “move each curve” to correct the rest with the level rule" : ""}.</div>`;
  if (!picked.length) h += `<div class="empty">Pick at least one driver above.</div>`;
  else {
    const drawn = x => cmp.q.some(qid => x.quantities.some(q => q.id === qid));
    h += `<div class="legend">${picked.map(x => `<span class="lg${drawn(x) ? "" : " off"}"><span class="lgm" style="color:${COLORS[x.p.slot]}">${MARK_CHARS[MARKERS[x.p.slot]]}</span><span class="lgl${view === "curve" ? "" : " sq"}" style="background:${COLORS[x.p.slot]}"></span>${esc(entryName(x.e))}<span class="dim">${esc(drawn(x) ? levelNote(x) : " · no " + cmp.q.join(", ") + " in this set")}</span></span>`).join("")}</div>`;
    h += noChart() ? noChartMsg : `<div class="chartbox tall"><canvas id="cchart"></canvas></div>`;
    h += `<div id="csum"></div><div class="exportrow">${exportHtml(() => exportCurves(g, picked), "comparison_" + g.kind.id, "Export this comparison")}</div>`;
    h += `<details class="conds"><summary>Test conditions and sources of the picked drivers</summary>${picked.map(x =>
      `<div class="cond"><span style="color:${COLORS[x.p.slot]}">${MARK_CHARS[MARKERS[x.p.slot]]} ${esc(x.e.driver.name)}</span> <span class="dim">${esc(x.chosen.set.type)}${x.chosen.set.method ? " · " + esc(x.chosen.set.method) : ""}</span>${condChips(x.chosen.set.conditions, x.chosen.set.source)}${x.chosen.set.note ? `<div class="setnote">${esc(x.chosen.set.note)}</div>` : ""}</div>`).join("")}</details>`;
  }
  if (fam && fam.reliability_note) h += `<div class="hint2">${esc(g.family)}: ${esc(fam.reliability_note)}</div>`;
  h += `</div>`;
  app().innerHTML = h;
  wire(g);
  if (picked.length && !noChart()) {
    if (view === "curve") drawCurves(g, picked);
    else if (view === "bars") drawBars(g, picked);
    else drawTable(g, picked);
  }
  wireExports(app());
}

function exportCurves(g, picked) {
  return picked.flatMap(x => {
    const only = g.kind.view === "table" ? null : cmp.q.filter(q => q !== "sum");
    const curves = curvesOfSet(x.e.driver, x.chosen.set, { quantities: x.quantities, only: only && only.length ? only : null });
    if (g.kind.view === "table") curves.forEach(c => { c.points = c.points.filter(p => cmp.rows.includes(p.x)); });
    const moved = cmp.shift && x.chosen.delta;
    return curves.map(c => Object.assign(c, moved ? { level: cmp.L, label: c.label.replace(/ · [\d.]+ dB$/, "") + ` · ${cmp.L} dB (moved from ${x.chosen.level} dB with the level rule)`,
      sourceText: `${c.sourceText}; moved from ${x.chosen.level} dB to ${cmp.L} dB with the level rule (H2 +1.0, H3 to H5 +0.7 dB per dB)` } : {}));
  });
}

const dashSvg = dash => `<svg class="dash" width="22" height="8" aria-hidden="true"><line x1="1" y1="4" x2="21" y2="4" stroke="#eef0f6" stroke-width="2" stroke-dasharray="${(dash || []).join(",")}"/></svg>`;

function wire(g) {
  document.querySelectorAll("[data-src]").forEach(b => b.onclick = () => { cmp.src = b.dataset.src; cmp.g = null; cmp.q = []; render(); });
  const mix = $("cmix"); if (mix) mix.onchange = () => {
    cmp.mix = mix.checked;
    const target = groups(cmp.mix).find(x => x.kind.id === g.kind.id && x.key.endsWith(g.key.split("::").pop()) && (cmp.mix || x.family === cmp.src));
    cmp.g = target ? target.key : null;
    render();
  };
  const sel = $("cgrp"); if (sel) sel.onchange = () => { cmp.g = sel.value; cmp.q = []; cmp.picks = null; cmp.rows = null; cmp.L = null; render(); };
  const L = $("cL"); if (L) L.onchange = () => { const v = Number(L.value); if (v >= 40 && v <= 140) cmp.L = v; render(); };
  document.querySelectorAll("[data-lvl]").forEach(b => b.onclick = () => { cmp.L = Number(b.dataset.lvl); render(); });
  const sh = $("cshift"); if (sh) sh.onchange = () => { cmp.shift = sh.checked; render(); };
  document.querySelectorAll("[data-q]").forEach(b => b.onclick = () => {
    const id = b.dataset.q;
    if (g.kind.view !== "curve") cmp.q = [id];
    else if (cmp.q.includes(id)) { if (cmp.q.length > 1) cmp.q = cmp.q.filter(x => x !== id); }
    else cmp.q = cmp.q.concat(id);
    if (g.kind.view === "table") cmp.rows = null;
    render();
  });
  document.querySelectorAll("[data-u]").forEach(b => b.onclick = () => { cmp.u = b.dataset.u; render(); });
  document.querySelectorAll("[data-row]").forEach(b => b.onclick = () => {
    const r = b.dataset.row;
    if (cmp.rows.includes(r)) { if (cmp.rows.length > 1) cmp.rows = cmp.rows.filter(x => x !== r); }
    else cmp.rows = rowLabels(g, cmp.q[0]).filter(x => x === r || cmp.rows.includes(x));
    render();
  });
  document.querySelectorAll("[data-pick]").forEach(cb => cb.onchange = () => {
    const id = cb.dataset.pick;
    if (cb.checked) { const s = freeSlot(); if (s >= 0) cmp.picks.push({ id, slot: s }); }
    else cmp.picks = cmp.picks.filter(p => p.id !== id);
    render();
  });
  const f = $("cfilt");
  const applyFilter = () => {
    const q = cmp.filt.trim().toLowerCase();
    let shown = 0;
    document.querySelectorAll(".pick").forEach(l => { l.hidden = !l.dataset.text.includes(q); if (!l.hidden) shown++; });
    let msg = $("cnomatch");
    if (!msg) { msg = document.createElement("div"); msg.id = "cnomatch"; msg.className = "empty"; document.querySelector(".picks").appendChild(msg); }
    msg.hidden = shown > 0;
    msg.textContent = `No driver matches “${cmp.filt.trim()}” in this source and measurement.`;
  };
  if (f) { f.oninput = () => { cmp.filt = f.value; applyFilter(); }; if (cmp.filt) applyFilter(); }
  // the pick list keeps its scroll position when a tick redraws the panel
  const box = document.querySelector(".picks");
  if (box) { box.scrollTop = cmp.pickScroll; box.onscroll = () => { cmp.pickScroll = box.scrollTop; }; }
}

function drawCurves(g, picked) {
  const units = g.kind.ratio ? cmp.u : "db";
  const log = (g.kind.x || {}).scale === "log";
  const ds = [];
  for (const x of picked) {
    cmp.q.forEach((qid, qi) => {
      const q = x.quantities.find(y => y.id === qid);
      if (!q) return;
      const pts = q.points.map(pt => ({ x: pt.x, y: units === "pct" ? pct(pt.y) : pt.y }));
      const color = COLORS[x.p.slot];
      ds.push({ label: `${entryName(x.e)} · ${q.label}${x.chosen.level != null ? " · " + lv(cmp.shift && x.chosen.delta ? cmp.L : x.chosen.level) : ""}`, data: pts,
        borderColor: color, backgroundColor: color, borderDash: DASHES[qi % DASHES.length], borderWidth: 2.2, tension: 0.2, spanGaps: false,
        pointStyle: MARKERS[x.p.slot], pointRadius: markerRadius(pts.length, x.p.slot), pointHoverRadius: 5, pointBackgroundColor: color, pointBorderColor: color });
    });
  }
  const xt = `${(g.kind.x || {}).label || ""}${(g.kind.x || {}).unit ? " (" + g.kind.x.unit + ")" : ""}`;
  const yT = g.kind.ratio ? (units === "pct" ? "% of fundamental" : "dB re fundamental") : `${(g.kind.y || {}).label || ""}${(g.kind.y || {}).unit ? " (" + g.kind.y.unit + ")" : ""}`;
  const xFmt = v => (log ? fmtHz(v) : v.toFixed(1) + " dB");
  newChart($("cchart"), { type: "line", data: { datasets: ds }, options: chartOptions({ x: xAxis(log, xt), y: yAxis(units, yT) },
    c => `${c.dataset.label}: ${units === "pct" ? c.parsed.y.toPrecision(3) + " %" : c.parsed.y.toFixed(1) + (g.kind.ratio ? " dB" : "")} at ${xFmt(c.parsed.x)}`) });
  // median, highest and lowest over the range every picked driver covers
  const rows = [];
  cmp.q.forEach(qid => {
    const curves = picked.map(x => ({ x, q: x.quantities.find(y => y.id === qid) })).filter(c => c.q && c.q.points.length);
    if (!curves.length) return;
    const lo = Math.max(...curves.map(c => c.q.points[0].x)), hi = Math.min(...curves.map(c => c.q.points[c.q.points.length - 1].x));
    curves.forEach(c => {
      const inR = c.q.points.filter(pt => pt.x >= lo && pt.x <= hi);
      if (!inR.length) { rows.push({ c, qid, none: true }); return; }
      const ys = inR.map(pt => pt.y).sort((a, b) => a - b);
      const med = ys.length % 2 ? ys[(ys.length - 1) / 2] : (ys[ys.length / 2 - 1] + ys[ys.length / 2]) / 2;
      rows.push({ c, qid, med, hiPt: inR.reduce((a, b) => (b.y > a.y ? b : a)), loPt: inR.reduce((a, b) => (b.y < a.y ? b : a)), lo, hi });
    });
  });
  const fv = v => (g.kind.ratio ? (units === "pct" ? fmtPct(v) : fmtDb(v)) : v.toFixed(1));
  const where = v => (log ? fmtHz(v) : v.toFixed(1) + " dB");
  $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Driver</th><th>Shows</th><th>Level</th><th>Range used</th><th>Median</th><th>Highest</th><th>Lowest</th></tr></thead><tbody>${rows.map(r =>
    `<tr><td><span style="color:${COLORS[r.c.x.p.slot]}">${MARK_CHARS[MARKERS[r.c.x.p.slot]]}</span> ${esc(r.c.x.e.driver.name)}</td><td>${esc(r.qid)}</td><td>${esc(lv(cmp.shift && r.c.x.chosen.delta ? cmp.L : r.c.x.chosen.level) || "—")}</td>` +
    (r.none ? `<td colspan="4">no range shared with the other picked drivers</td>` :
      `<td>${where(r.lo)} to ${where(r.hi)}</td><td>${fv(r.med)}</td><td>${fv(r.hiPt.y)} at ${where(r.hiPt.x)}</td><td>${fv(r.loPt.y)} at ${where(r.loPt.x)}</td>`) + `</tr>`).join("")}</tbody></table></div>
    <div class="hint2">Figures are taken over the range all picked drivers cover, so they compare like with like.</div>`;
}

function drawBars(g, picked) {
  const qid = cmp.q[0];
  const qs = picked.map(x => ({ x, q: x.quantities.find(y => y.id === qid) })).filter(y => y.q);
  const relTo = (qs[0] && qs[0].q.relTo) || "dB";
  if (qid === "sum") {
    const vals = qs.map(y => y.q.value), base = barBase(vals);
    newChart($("cchart"), { type: "bar", data: { labels: qs.map(y => y.x.e.driver.name), datasets: [{ label: "Sum of all products", data: vals,
      backgroundColor: qs.map(y => COLORS[y.x.p.slot]), base, barPercentage: 0.6 }] },
      options: chartOptions({ x: categoryAxis("", 30), y: yAxis("db", relTo, { min: base, max: barTop(vals) }) }, c => `${c.label}: ${c.parsed.y.toFixed(1)} dB`) });
    $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Driver</th><th>Level</th><th>Sum of all products</th><th>as %</th></tr></thead><tbody>${qs.map(y =>
      `<tr><td><span style="color:${COLORS[y.x.p.slot]}">${MARK_CHARS[MARKERS[y.x.p.slot]]}</span> ${esc(y.x.e.driver.name)}</td><td>${esc(lv(y.x.chosen.level))}</td><td>${fmtDb(y.q.value)}</td><td>${fmtPct(y.q.value)}</td></tr>`).join("")}</tbody></table></div>
      <div class="hint2">Power sum of every product the chart shows, ${esc(relTo)}. Lower is better.</div>`;
    return;
  }
  const freqs = [...new Set(qs.flatMap(y => y.q.points.map(pt => pt.x)))].sort((a, b) => a - b);
  const all = qs.flatMap(y => y.q.points.map(pt => pt.y)), base = barBase(all);
  newChart($("cchart"), { type: "bar", data: { labels: freqs.map(fmtHz), datasets: qs.map(y => ({ label: y.x.e.driver.name, backgroundColor: COLORS[y.x.p.slot], base,
    data: freqs.map(f => { const pt = y.q.points.find(q => q.x === f); return pt ? pt.y : null; }) })) },
    options: chartOptions({ x: categoryAxis("Product frequency", 50), y: yAxis("db", relTo, { min: base, max: barTop(all) }) }, c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} dB at ${c.label}`) });
  $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Product</th>${qs.map(y =>
    `<th style="color:${COLORS[y.x.p.slot]}">${MARK_CHARS[MARKERS[y.x.p.slot]]} ${esc(y.x.e.driver.name)}</th>`).join("")}</tr></thead><tbody>${freqs.map(f =>
    `<tr><td>${fmtHz(f)}</td>${qs.map(y => { const pt = y.q.points.find(q => q.x === f); return `<td>${pt ? pt.y.toFixed(1) : "—"}</td>`; }).join("")}</tr>`).join("")}
    <tr class="sumrow"><td>sum</td>${qs.map(y => { const s = y.x.quantities.find(q => q.id === "sum"); return `<td>${s && s.value != null ? s.value.toFixed(1) : "—"}</td>`; }).join("")}</tr></tbody></table></div>
    <div class="hint2">Values in ${esc(relTo)}; the test tones themselves are left out. Taller bars mean more distortion.</div>`;
}

function drawTable(g, picked) {
  const qid = cmp.q[0], rows = cmp.rows;
  const qs = picked.map(x => ({ x, q: x.quantities.find(y => y.id === qid) })).filter(y => y.q);
  const val = (y, r) => { const row = y.q.rows.find(z => z.label === r); return row ? row.value : null; };
  const tvals = qs.flatMap(y => rows.map(r => val(y, r))), base = barBase(tvals);
  newChart($("cchart"), { type: "bar", data: { labels: rows, datasets: qs.map(y => ({ label: y.x.e.driver.name, backgroundColor: COLORS[y.x.p.slot], base,
    data: rows.map(r => val(y, r)) })) },
    options: chartOptions({ x: categoryAxis(""), y: yAxis("db", qid, { min: base || undefined, max: barTop(tvals) }) }, c => `${c.dataset.label}: ${c.parsed.y} (${c.label})`) });
  $("csum").innerHTML = `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>${esc((picked[0].chosen.set.columns || [""])[0])}</th>${qs.map(y =>
    `<th style="color:${COLORS[y.x.p.slot]}">${MARK_CHARS[MARKERS[y.x.p.slot]]} ${esc(y.x.e.driver.name)}</th>`).join("")}</tr></thead><tbody>${rows.map(r =>
    `<tr><td>${esc(r)}</td>${qs.map(y => { const v = val(y, r); return `<td>${v == null ? "—" : v}</td>`; }).join("")}</tr>`).join("")}</tbody></table></div>
    <div class="hint2">Column: ${esc(qid)}.${qs.some(y => y.x.chosen.level != null) ? " Levels: " + qs.map(y => `${esc(y.x.e.driver.name)} ${esc(lv(y.x.chosen.level))}`).join(", ") + "." : ""}</div>`;
}

registerView({
  id: "compare", label: "Compare", order: 20, routes: ["compare"],
  show({ params }) { load(params); render(); },
});

export { driverById };
