/* drivers.js: the Drivers tab. The list of drivers, and each driver's page with every curve,
 * one source at a time or all sources. Curves of the same kind measured at several levels (for
 * example HiFiCompass's axial sound pressure and harmonics at several drive levels) share one chart,
 * one colour per level. */
import { registerView } from "../core/registry.js";
import { store, allDrivers, familyOf, kindOf, levelOf, isSurvey } from "../core/data.js";
import { quantitiesOf, matchKey, matchLabel, sortQuantities } from "../core/compare.js";
import { curvesOfSet, curvesOfDriver } from "../core/curves.js";
import { readHash, writeHash } from "../core/state.js";
import { $, app, esc, navHtml, beginView, newChart, noChart, noChartMsg, xAxis, yAxis, categoryAxis, chartOptions,
         barBase, barTop, levelColors, badge, condChips, exportHtml, wireExports, fmtHz } from "../core/ui.js";

const BRAND = "driver database";     // shown above the list; change to rebrand
const PALETTE = ["#f0a44a", "#6fd19a", "#7aa2f7", "#e98b8b", "#c4a3ff", "#f6c48a"];
const CONF = { high: "#6fd19a", medium: "#f0a44a", low: "#e98b8b", none: "#7b859c" };
const TS = [["Fs", "Hz"], ["Qts", ""], ["Vas", "L"], ["Sd", "cm²"], ["Xmax", "mm"], ["Bl", "T·m"], ["Re", "Ω"], ["Le", "mH"]];
const TS_EXTRA = { Vd: "cm³", Pe: "W", sens: "dB", sens1W: "dB/W", Mms: "g", Cms: "mm/N", Qms: "", Qes: "", Z: "Ω" };
const ROLE_ORDER = ["tweeter", "tweeter (waveguide)", "midrange", "midbass", "midbass / mid", "midbass (survey)",
                    "woofer / midbass", "woofer", "woofer (pair)", "comparison"];
const list = { filter: "", survey: false, scroll: 0 };
const cardState = {};                  // chosen harmonic per chart card, remembered while the page is open

// Comparison charts stored in drivers.json 'comparisons' are shown as extra records.
function comparisonRecords() {
  return ((store.db && store.db.comparisons) || []).map(c => ({ id: c.id, name: c.title, manufacturer: "", role: "comparison", band: "",
    isComparison: true, comparesN: (c.drivers || []).length, ts: {}, findings: "", measurements: [c] }));
}
function records() {
  return allDrivers({ survey: list.survey }).concat(comparisonRecords());
}
const roleRank = r => { const i = ROLE_ORDER.indexOf(r); return i < 0 ? 99 : i; };
function sourceNames(d) {
  const out = [];
  (d.measurements || []).forEach(m => { const f = familyOf(m); if (f && f.kind !== "derived" && !out.includes(f.name)) out.push(f.name); });
  return out;
}

function showList() {
  beginView(false);
  const q = list.filter.toLowerCase();
  const items = records().filter(d => (d.name + d.manufacturer + d.role + d.band + (d.findings || "")).toLowerCase().includes(q))
    .sort((a, b) => roleRank(a.role) - roleRank(b.role) || (a.name || "").localeCompare(b.name || ""));
  const surveyN = store.survey ? store.survey.drivers.length : 0;
  app().innerHTML = navHtml("drivers") + `<div class="kick"><span>${BRAND}</span><span style="color:var(--dim)">${items.length} shown</span></div>
    <h1>Driver database</h1>
    <input class="filter" id="flt" placeholder="filter by name, role, finding…" value="${esc(list.filter)}">
    <label class="ds"><input type="checkbox" id="surv" ${list.survey ? "checked" : ""}>
      include midbass intermodulation survey${surveyN ? ` (${surveyN} drivers · indicative)` : " (unavailable)"}</label>
    <div id="list"></div>`;
  const box = $("list");
  let lastRole = null;
  for (const d of items) {
    if (d.role !== lastRole) { const hd = document.createElement("div"); hd.className = "rolehdr"; hd.textContent = d.role || "—"; box.appendChild(hd); lastRole = d.role; }
    const n = (d.measurements || []).length;
    const b = document.createElement("button");
    b.className = "card";
    const sub = d.isComparison ? `compares ${d.comparesN} drivers · ${(d.measurements[0].series || []).length} series`
      : `${[d.manufacturer, d.band].filter(Boolean).join(" · ") || "—"} · ${n} measurement${n !== 1 ? "s" : ""}`;
    const srcs = d.isComparison ? [] : sourceNames(d);
    b.innerHTML = `<div class="nm">${esc(d.name || "(unnamed)")}</div><div class="sub">${esc(sub)}</div>` +
      (srcs.length ? `<div class="srcs">${srcs.length > 1 ? srcs.length + " sources: " : "source: "}${esc(srcs.join(" · "))}</div>` : "");
    b.onclick = () => { list.scroll = window.scrollY; location.hash = "driver/" + encodeURIComponent(d.id); };
    box.appendChild(b);
  }
  $("flt").addEventListener("input", e => {
    list.filter = e.target.value; showList();
    const x = $("flt"); x.focus(); x.setSelectionRange(list.filter.length, list.filter.length);
  });
  $("surv").addEventListener("change", e => { list.survey = e.target.checked; showList(); });
  window.scrollTo(0, list.scroll);
}

// Sets of one driver grouped into chart cards: same source, kind and test conditions; levels together.
function cardsOf(d, sourceName) {
  const cards = [];
  (d.measurements || []).forEach((set, index) => {
    const fam = familyOf(set);
    if (sourceName && (!fam || fam.name !== sourceName)) return;
    const kind = kindOf(set);
    const key = `${fam ? fam.name : "?"}::${kind.id}|${matchKey(set, kind)}|${kind.level ? "" : index}`;
    let c = cards.find(x => x.key === key);
    if (!c) { c = { key, fam, kind, sets: [] }; cards.push(c); }
    c.sets.push({ set, index, level: levelOf(set), quantities: quantitiesOf(set, kind) });
  });
  const order = store.families.map(f => f.name);
  cards.forEach(c => c.sets.sort((a, b) => (a.level ?? 0) - (b.level ?? 0)));
  return cards.sort((a, b) => order.indexOf(a.fam && a.fam.name) - order.indexOf(b.fam && b.fam.name));
}

const levelName = s => (s.level != null ? `${Math.round(s.level * 10) / 10} dB` :
  (s.set.conditions || {}).drive_v != null ? `${[].concat(s.set.conditions.drive_v).join(" and ")} V` : s.set.method || `set ${s.index + 1}`);

function showDetail(id, params) {
  const d = records().find(x => x.id === id) || (store.survey && store.survey.drivers.find(x => x.id === id));
  if (!d) return showList();
  beginView(false);
  const fams = [...new Set((d.measurements || []).map(m => familyOf(m)).filter(Boolean))]
    .sort((a, b) => (a.rank || 99) - (b.rank || 99));
  let src = params.get("src");
  if (src && !fams.some(f => f.name === src)) src = null;
  writeHash("driver/" + encodeURIComponent(d.id), { src });
  const extra = Object.entries(TS_EXTRA).filter(([k]) => d.ts && d.ts[k] != null && d.ts[k] !== "")
    .map(([k, u]) => `<b>${k}</b> ${esc(d.ts[k])}${u ? " " + u : ""}`).join("  ·  ");
  let h = navHtml("drivers") + `<button class="back" id="bk">← all drivers</button>${d.isComparison ? "" : `<button class="cmpbtn" id="cmpd">compare with other drivers</button>`}
    <h2>${esc(d.name)}</h2><div class="meta">${esc(d.isComparison ? "comparison · " + (d.comparesN || 0) + " drivers" : [d.manufacturer, d.role, d.band].filter(Boolean).join(" · "))}</div>`;
  if (!d.isComparison) {
    h += `<div class="tsgrid">${TS.map(([k, u]) => `<div class="ts"><div class="k">${k}</div><div class="v">${d.ts && d.ts[k] != null && d.ts[k] !== "" ? esc(d.ts[k]) + (u ? `<span style="color:#7b859c;font-size:10px"> ${u}</span>` : "") : "—"}</div></div>`).join("")}</div>
      ${extra ? `<div class="tsmore">${extra}</div>` : ""}`;
  }
  if (fams.length && !d.isComparison) {
    h += `<div class="srcrow small">${[{ name: null }].concat(fams).map(f => {
      const n = (d.measurements || []).filter(m => !f.name || (familyOf(m) || {}).name === f.name).length;
      return `<button class="srcbtn${(src || null) === f.name ? " on" : ""}" data-src="${esc(f.name || "")}"><span class="sn">${esc(f.name || "All sources")}</span>${f.name ? badge(f) : ""}<span class="cnt">${n} set${n !== 1 ? "s" : ""}</span></button>`;
    }).join("")}</div>`;
    h += `<div class="exportrow">${exportHtml(() => curvesOfDriver(d, src), `${d.id}_${src || "all-sources"}`, "Export all curves")}</div>`;
  }
  const cards = d.isComparison ? [{ key: "cmp", fam: null, kind: kindOf(d.measurements[0]), sets: [{ set: d.measurements[0], index: 0, level: null, quantities: quantitiesOf(d.measurements[0]) }] }] : cardsOf(d, src);
  let lastFam;
  const draws = [];
  cards.forEach((c, ci) => {
    const famName = c.fam ? c.fam.name : "Other";
    if (!d.isComparison && famName !== lastFam) {
      const n = cards.filter(x => (x.fam ? x.fam.name : "Other") === famName).reduce((k, x) => k + x.sets.length, 0);
      h += `<div class="srchdr"><span>${esc(famName)}${c.fam && c.fam.reliability ? ` <b class="relt">· ${esc(c.fam.reliability)}</b>` : ""}</span><span>${n} set${n !== 1 ? "s" : ""}</span></div>`;
      lastFam = famName;
    }
    const first = c.sets[0].set;
    const multi = c.sets.length > 1;
    const conf = CONF[first.confidence] || CONF.none;
    const title = multi ? `${c.kind.label}${matchLabel(first, c.kind) ? " · " + matchLabel(first, c.kind) : ""} · ${c.sets.length} levels`
      : `${first.type}${first.method ? " · " + first.method : ""}`;
    h += `<div class="setttl"><span>${esc(title)}</span><span class="conf" style="color:${conf};border:1px solid ${conf}55">${esc(first.confidence || "none")}</span></div>`;
    const has = c.sets.some(s => s.quantities.length);
    if (!has) { h += `<div class="empty">no data</div>`; return; }
    if (multi && c.kind.view === "curve") {
      const ids = sortQuantities([...new Set(c.sets.flatMap(s => s.quantities.map(q => q.id)))]);
      const pick = cardState[d.id + c.key] && ids.includes(cardState[d.id + c.key]) ? cardState[d.id + c.key] : ids[0];
      h += `<div class="togrow">${ids.map(q => `<button class="tog small${q === pick ? " on" : ""}" data-card="${ci}" data-q="${esc(q)}">${esc(q)}</button>`).join("")}</div>`;
      const cols = levelColors(c.sets.length);
      h += `<div class="legend">${c.sets.map((s, i) => `<span class="lg"><span class="lgl" style="background:${cols[i]}"></span>${esc(levelName(s))}</span>`).join("")}</div>`;
      h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}"></canvas></div>`;
      draws.push(() => drawLevels($("ch" + ci), c, pick, cols));
    } else {
      for (const s of c.sets) {
        if (s.set.chartType === "table") h += renderTable(s.set);
        else h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}_${s.index}"></canvas></div>`;
        if (s.set.chartType !== "table") draws.push(() => drawSet($("ch" + ci + "_" + s.index), s.set));
      }
    }
    for (const s of c.sets) {
      h += condChips(s.set.conditions, s.set.source);
      if (s.set.note) h += `<div class="setnote">${esc(s.set.note)}</div>`;
    }
    if (!d.isComparison) h += `<div class="exportrow">${exportHtml(() => c.sets.flatMap(s => curvesOfSet(d, s.set)), `${d.id}_${c.kind.id}${c.fam ? "_" + c.fam.name : ""}`)}</div>`;
  });
  if (!cards.length) h += `<div class="empty">No measurements from this source.</div>`;
  if (d.findings) h += `<div class="findings">${esc(d.findings)}</div>`;
  app().innerHTML = h;
  $("bk").onclick = () => { location.hash = ""; };
  const cb = $("cmpd");
  if (cb) cb.onclick = () => { location.hash = "compare?driver=" + encodeURIComponent(d.id); };
  document.querySelectorAll("[data-src]").forEach(b => b.onclick = () => {
    const p = new URLSearchParams(); if (b.dataset.src) p.set("src", b.dataset.src);
    showDetail(d.id, p);
  });
  document.querySelectorAll("[data-card]").forEach(b => b.onclick = () => {
    cardState[d.id + cards[Number(b.dataset.card)].key] = b.dataset.q;
    showDetail(d.id, readHash().params);
  });
  draws.forEach(f => f());
  wireExports(app());
  window.scrollTo(0, 0);
}

function renderTable(set) {
  const cols = set.columns || [], rows = set.rows || [];
  const fmt = v => (v === null || v === undefined || v === "" ? "—" : typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(2)) : esc(v));
  return `<div class="tscroll"><table class="dtable"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead>` +
    `<tbody>${rows.map(r => `<tr>${r.map(c => `<td>${fmt(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function drawSet(canvas, set) {
  if (!canvas) return;
  const ax = set.axes || { x: {}, y: {} };
  const xt = ((ax.x && ax.x.label) || "") + (ax.x && ax.x.unit ? " (" + ax.x.unit + ")" : "");
  const yt = ((ax.y && ax.y.label) || "") + (ax.y && ax.y.unit ? " (" + ax.y.unit + ")" : "");
  const isBar = set.chartType === "bar";
  const ds = (set.series || []).map((s, i) => ({
    label: s.name, data: (s.points || []).map(p => ({ x: Number(p.x), y: p.y == null ? null : Number(p.y) })),
    backgroundColor: isBar ? "#f0a44a" : PALETTE[i % PALETTE.length], borderColor: PALETTE[i % PALETTE.length],
    borderWidth: isBar ? 0 : 2, pointRadius: 0, tension: 0.25, barThickness: isBar ? 6 : undefined,
  }));
  const opts = chartOptions({ x: xAxis(!isBar && ax.x && ax.x.scale === "log", xt), y: yAxis("db", yt) });
  opts.plugins.legend = { display: (set.series || []).length > 1, labels: { color: "#a3acc2", font: { size: 11 }, boxWidth: 10 } };
  newChart(canvas, { type: isBar ? "bar" : "line", data: { datasets: ds }, options: opts });
}

function drawLevels(canvas, card, quantity, cols) {
  if (!canvas) return;
  const ds = card.sets.map((s, i) => {
    const q = s.quantities.find(x => x.id === quantity);
    return { label: levelName(s), data: q ? q.points.map(p => ({ x: p.x, y: p.y })) : [], borderColor: cols[i], backgroundColor: cols[i],
             borderWidth: 2, pointRadius: 0, tension: 0.2 };
  });
  const k = card.kind;
  newChart(canvas, { type: "line", data: { datasets: ds }, options: chartOptions({
    x: xAxis((k.x || {}).scale === "log", `${(k.x || {}).label || ""}${(k.x || {}).unit ? " (" + k.x.unit + ")" : ""}`),
    y: yAxis("db", `${quantity} (${(k.y || {}).unit || ""})`) },
    c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} at ${(k.x || {}).scale === "log" ? fmtHz(c.parsed.x) : c.parsed.x}`) });
}

registerView({
  id: "drivers", label: "Drivers", order: 10, routes: ["", "driver"],
  show({ page, rest, params }) {
    if (page === "driver" && rest) {
      const d = records().find(x => x.id === rest) || (store.survey && store.survey.drivers.find(x => x.id === rest));
      if (d && isSurvey(d)) list.survey = true;
      return showDetail(rest, params);
    }
    return showList();
  },
});
