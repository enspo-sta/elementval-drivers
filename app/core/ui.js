/* ui.js: page helpers shared by the views: tab bar, charts, badges, test-condition chips and the
 * export controls. */
import { getViews, getExporters } from "./registry.js";
import { store, fmtHz } from "./data.js";
import { makeZip } from "./zip.js";
import { uniqueNames } from "../exporters/common.js";
import { dbToPct } from "./sim.js";

export const $ = id => document.getElementById(id);
export const app = () => document.getElementById("app");
export const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---------- tab bar ----------
export function navHtml(active) {
  return `<nav class="tabs">${getViews().filter(v => v.nav).map(v =>
    `<a href="#${v.routes[0]}" class="${v.id === active ? "on" : ""}">${esc(v.label)}</a>`).join("")}</nav>`;
}

/** Start drawing a view: clears old charts and sets the page width. */
export function beginView(wide) {
  clearCharts();
  app().classList.toggle("wide", !!wide);
}

// ---------- charts ----------
let charts = [];
export function clearCharts() { charts.forEach(c => c.destroy()); charts = []; }
export function newChart(canvas, cfg) {
  if (!canvas || typeof Chart === "undefined") return null;
  const c = new Chart(canvas, cfg);
  charts.push(c);
  return c;
}
export const noChart = () => typeof Chart === "undefined";
export const noChartMsg = `<div class="warn">The chart library did not load (no internet connection?). The settings still work; reload the page when you are online.</div>`;

const GRID = "#2b3344", TICK = "#a3acc2", TITLE = "#7b859c";
export function tickLog(v) {
  const e = Math.floor(Math.log10(v) + 1e-9), m = v / Math.pow(10, e);
  if (![1, 2, 5].some(k => Math.abs(m - k) < 1e-6)) return "";
  return v >= 1000 ? v / 1000 + "k" : String(+v.toPrecision(3));
}
export function xAxis(log, title, min, max) {
  const ticks = { color: TICK, font: { size: 11 }, maxRotation: 0 };
  // 20, 50, 100, 200, 500, ... on a log axis; on a narrow phone only 100, 500, 1k, 5k so labels do not touch
  const narrow = typeof window !== "undefined" && window.innerWidth < 420;
  if (log) { ticks.autoSkip = false; ticks.callback = v => { const t = tickLog(v); return narrow && /^2/.test(t) ? "" : t; }; }
  return { type: log ? "logarithmic" : "linear", min, max, grid: { color: GRID }, ticks,
           title: { display: !!title, text: title, color: TITLE, font: { size: 11 } } };
}
export function yAxis(units, title, extra) {
  const ticks = { color: TICK, font: { size: 11 } };
  if (units === "pct") ticks.callback = v => { const t = tickLog(v); return t && t + " %"; };
  return Object.assign({ type: units === "pct" ? "logarithmic" : "linear", grid: { color: GRID }, ticks,
           title: { display: !!title, text: title, color: TITLE, font: { size: 11 } } }, extra || {});
}
export function categoryAxis(title, rotate = 40) {
  return { grid: { display: false }, ticks: { color: TICK, font: { size: 11 }, maxRotation: rotate, autoSkip: false },
           title: { display: !!title, text: title, color: TITLE, font: { size: 11 } } };
}
export function chartOptions(scales, tooltipLabel) {
  return { responsive: true, maintainAspectRatio: false, animation: false, normalized: true,
    interaction: { mode: "nearest", intersect: false },
    plugins: { legend: { display: false }, tooltip: { callbacks: tooltipLabel ? { label: tooltipLabel } : {} } }, scales };
}
/** A marker on every n-th point, staggered per line so markers of different lines do not overlap. */
export function markerRadius(n, slot) {
  const step = Math.max(1, Math.round(n / 9)), off = Math.floor((slot * step) / 5) % step;
  return ctx => (ctx.dataIndex % step === off ? 4 : 0);
}
// Bars grow up from the bottom, so a taller bar always means more distortion, also for negative dB.
export function barBase(values) {
  const v = values.filter(x => x != null);
  // ends on a multiple of 20 dB, so the axis's own ticks (every 10 or 20 dB) end there too and no extra tick
  // label crowds the last regular one
  return v.length && v.every(x => x <= 0) ? Math.floor((Math.min(...v) - 5) / 20) * 20 : 0;
}
export function barTop(values) {
  const v = values.filter(x => x != null);
  return v.length && v.every(x => x <= 0) ? Math.min(0, Math.ceil((Math.max(...v) + 5) / 20) * 20) : undefined;
}
/** Colours for several levels of one driver, from cool (lowest level) to warm (highest). */
const LEVEL_RAMP = ["#56B4E9", "#009E73", "#F0E442", "#E69F00", "#D55E00", "#CC79A7", "#9ecae1", "#eef0f6"];
export const levelColors = n => Array.from({ length: n }, (_, i) => LEVEL_RAMP[i % LEVEL_RAMP.length]);

// ---------- numbers ----------
export const pct = v => (v == null ? null : dbToPct(v));
export const fmtDb = v => (v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(1) + " dB");
export function fmtPct(v) {
  if (v == null) return "—";
  const p = dbToPct(v);
  return (p >= 10 ? p.toFixed(0) : p >= 1 ? p.toFixed(1) : p >= 0.1 ? p.toFixed(2) : p.toFixed(3)) + " %";
}
export { fmtHz };

// ---------- sources and test conditions ----------
const REL_COLORS = { 1: "#6fd19a", 2: "#56b6c2", 3: "#f0a44a", 4: "#a3acc2", 5: "#e98b8b" };
export function badge(f) {
  if (!f || !f.reliability) return "";
  const c = REL_COLORS[f.rank] || "#7b859c";
  return `<span class="rel" style="color:${c};border-color:${c}66" title="${esc(f.reliability_note || "")}">${esc(f.reliability)}</span>`;
}
export const familyByName = name => store.families.find(f => f.name === name) || null;

const COND = { spl_db: v => v + " dB at 1 m", spl_db_1khz: v => v + " dB at 1 kHz", spl_note: v => "level: " + v, test: v => String(v).replace(/_/g, " "), distance_mm: v => v + " mm", drive_v: v => (Array.isArray(v) ? v.join(" and ") : v) + " V", drive_V: v => v + " V",
  f1: v => "f1 " + v + (typeof v === "number" ? " Hz" : ""), f2: v => "f2 " + v + (typeof v === "number" ? " Hz" : ""), f0: v => "tone " + v + " Hz",
  ratio: v => v, x_pk_mm: v => "peak excursion " + v + " mm", angles_deg: v => "angles " + [].concat(v).map(a => a + "°").join(", "),
  chart_range_db: v => "chart range " + v + " dB", band: v => v, angle_deg: v => v + "°",
  hpf: v => v, lab: v => v, test: v => v, standard: v => v, space: v => v, ref: v => "re " + v, ref_spl_db: v => "ref " + v + " dB" };
export function condChips(c, source) {
  if (!c || typeof c !== "object") c = c ? { note: c } : {};
  let h = "";
  for (const [k, v] of Object.entries(c)) { if (v === "" || v == null) continue; h += `<span class="chip">${esc(COND[k] ? COND[k](v) : k + ": " + v)}</span>`; }
  if (source) h += `<span class="chip src">· ${esc(source)}</span>`;
  return h ? `<div class="chips">${h}</div>` : "";
}

// ---------- export controls ----------
let exportSeq = 0;
/**
 * HTML for an export control; call wireExports() after putting it on the page.
 * getCurves: () => curves (see app/exporters/common.js). title: file name stem.
 */
const exportSources = new Map();
export function exportHtml(getCurves, title, label = "Export") {
  const id = "exp" + (++exportSeq);
  exportSources.set(id, { getCurves, title });
  return `<div class="export" data-exp="${id}"><select class="sel mini" aria-label="Export format"></select>
    <button class="tog" data-dl>${esc(label)}</button><button class="tog" data-copy title="Copy the file's text">copy</button><span class="expmsg"></span></div>`;
}
/** Mark tables that scroll sideways, so the stylesheet can say so on phones. */
export function markScrollables(root = document) {
  root.querySelectorAll(".tscroll").forEach(el => { if (el.scrollWidth > el.clientWidth + 2) el.dataset.scrolls = "1"; else delete el.dataset.scrolls; });
}
export function wireExports(root = document) {
  markScrollables(root);
  root.querySelectorAll("[data-exp]").forEach(el => {
    const src = exportSources.get(el.dataset.exp);
    if (!src) return;
    const curves = src.getCurves();
    const sel = el.querySelector("select"), msg = el.querySelector(".expmsg");
    // a kind may name the formats that make sense for it (schema/kinds.json "export"); csv-se counts as csv
    const kindAllows = (c, x) => { const k = store.kindById[c.kind]; return !k || !k.export || k.export.includes(x.id.split("-")[0]); };
    const usable = getExporters().filter(x => curves.some(c => x.accepts(c) && kindAllows(c, x)));
    sel.innerHTML = usable.map(x => `<option value="${esc(x.id)}">${esc(x.label)}</option>`).join("");
    if (!usable.length) { el.hidden = true; return; }
    const build = () => {
      const x = usable.find(e => e.id === sel.value) || usable[0];
      return uniqueNames(x.files(curves.filter(c => x.accepts(c) && kindAllows(c, x)), { title: src.title }));
    };
    el.querySelector("[data-dl]").onclick = () => {
      const files = build();
      if (!files.length) { msg.textContent = "nothing to export in this format"; return; }
      if (files.length === 1) download(files[0].name, files[0].text, (usable.find(e => e.id === sel.value) || {}).mime);
      else download(`${src.title}_${sel.value}`.replace(/[^\w.+-]+/g, "-") + ".zip", makeZip(files), "application/zip");
      msg.textContent = files.length === 1 ? files[0].name : `${files.length} files in one ZIP`;
    };
    el.querySelector("[data-copy]").onclick = async () => {
      const files = build();
      const text = files.map(f => (files.length > 1 ? `==> ${f.name} <==\n` : "") + f.text).join("\n");
      try { await navigator.clipboard.writeText(text); msg.textContent = "copied"; }
      catch (e) { msg.textContent = "copying is blocked here; use Export"; }
    };
  });
}
export function download(name, data, mime = "text/plain") {
  const blob = new Blob([data], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name; a.style.display = "none";
  document.body.appendChild(a); a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1500);
}
