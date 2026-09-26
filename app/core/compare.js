/* compare.js: which measurement sets may share a chart, and at which level.
 *
 * Sets share a chart when they have the same kind (schema/kinds.json), the same test conditions
 * that the kind lists under "match" (for example the two test tones) and, unless mixing is
 * switched on, the same source family. The level is not part of that rule: a driver measured at
 * several levels offers all of them, and the chart uses, for every driver, the level closest to the
 * target level (pickSet), so levels are always matched as closely as the data allows.
 */
import { allDrivers, familyOf, kindOf, levelOf, tonesOf, fmtHz, num, levelUnit } from "./data.js";

// Okabe and Ito's colour-blind safe palette; never more than five drivers at once.
export const COLORS = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#CC79A7"];
export const MARKERS = ["circle", "triangle", "rect", "rectRot", "star"];
export const MARK_CHARS = { circle: "●", triangle: "▲", rect: "■", rectRot: "◆", star: "★" };
export const DASHES = [[], [7, 4], [2, 3], [10, 3, 2, 3], [14, 5]];
export const MAX_PICK = 5;
export const TYPICAL_SLOPES = { H2: 1.0, H3: 0.7, H4: 0.7, H5: 0.7 };
const ORDER_RANK = ["H2", "H3", "H4", "H5", "THD", "Gm"];

/** The test conditions that must be equal, as text, for the kind's "match" list. */
export function matchKey(set, kind) {
  const c = set.conditions || {};
  return (kind.match || []).map(m => {
    if (m === "tones") { const t = tonesOf(set); return t ? t.join("+") : ""; }
    if (m === "type") return set.type || "";
    // a near-field measurement (the microphone within 100 mm of the cone) is not compared with far-field ones
    if (m === "field") return typeof c.distance_mm === "number" && c.distance_mm < 100 ? "near field" : "";
    return String(c[m] == null ? "" : c[m]);
  }).join("|");
}

/** Short text for the match conditions, shown after the kind's label. */
export function matchLabel(set, kind) {
  const bits = [];
  for (const m of kind.match || []) {
    if (m === "tones") { const t = tonesOf(set); if (t) bits.push(`${t[0]} + ${t[1]} Hz`); }
    else if (m === "type") { if (set.type && set.type !== kind.label) bits.push(set.type); }
    else if (m === "field") { const v = (set.conditions || {}).distance_mm; if (typeof v === "number" && v < 100) bits.push(`near field, ${v} mm`); }
    else if (m === "ratio") { const r = (set.conditions || {}).ratio; if (r) bits.push(r); }
    else if (m === "f0") { const f = num((set.conditions || {}).f0); if (f != null) bits.push(`${fmtHz(f)} tone`); }
    else if (m === "distance_mm") { const v = (set.conditions || {}).distance_mm; if (v) bits.push(`${v} mm`); }
    else if (m === "angle_deg") { const v = (set.conditions || {}).angle_deg; if (v != null && v !== "") bits.push(`${v}°`); }
  }
  return bits.join(", ");
}

function interp(points, f) {
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i], b = points[i + 1];
    if (f >= a.x && f <= b.x) {
      if (a.y == null || b.y == null) return null;
      if (a.x === b.x) return a.y;
      return a.y + (b.y - a.y) * Math.log(f / a.x) / Math.log(b.x / a.x);
    }
  }
  return null;
}
export { interp as interpLogCurve };

/** The quantities a set offers. Curves: one per series (plus THD when H2 to H5 are all there).
 *  Bars: each product and the power sum of all products. Tables: each numeric column. */
export function quantitiesOf(set, kind = kindOf(set)) {
  if (kind.view === "curve") {
    // harmonics stored as sound pressure become ratios by subtracting the test level
    const yl = (((set.axes || {}).y || {}).label || "").toLowerCase();
    const offset = kind.ratio && /^spl$/.test(yl) && levelOf(set) != null ? -levelOf(set) : 0;
    const out = [], by = {};
    for (const s of set.series || []) {
      const pts = (s.points || []).filter(p => p && p.x != null && p.y != null)
        .map(p => ({ x: Number(p.x), y: Number(p.y) + offset })).sort((a, b) => a.x - b.x);
      if (!pts.length) continue;
      out.push({ id: s.name, label: s.name, points: pts });
      by[s.name] = pts;
    }
    if (kind.id === "hd-frequency" && ["H2", "H3", "H4", "H5"].every(k => by[k])) { const thd = thdOf(by); if (thd.points.length) out.push(thd); }
    return out;
  }
  if (kind.view === "bars") {
    const pts = ((set.series && set.series[0] && set.series[0].points) || []).filter(p => p && p.y != null)
      .map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
    // two tones: relative to the upper one; one tone (a harmonic spectrum): relative to that tone
    const f0 = num((set.conditions || {}).f0);
    const tones = tonesOf(set) || (f0 != null ? [f0] : []);
    const refTone = tones[tones.length - 1];
    const toneBar = pts.find(p => tones.length && Math.abs(p.x - refTone) < 0.5);
    const ref = toneBar ? toneBar.y : 0;
    const products = pts.filter(p => !tones.some(t => Math.abs(p.x - t) < 0.5)).map(p => ({ x: p.x, y: p.y - ref }));
    const relTo = toneBar ? `dB relative to the ${fmtHz(refTone)} tone` : "dB relative to the fundamental, as published";
    const total = products.length ? 10 * Math.log10(products.reduce((s, p) => s + Math.pow(10, p.y / 10), 0)) : null;
    return [
      { id: "products", label: kind.id === "hd-spectrum" ? "Each harmonic" : "Each product", points: products, relTo },
      { id: "sum", label: kind.id === "hd-spectrum" ? "Sum of all harmonics" : "Sum of all products", value: total, relTo, computed: true },
    ];
  }
  const cols = set.columns || [], rows = set.rows || [];
  const out = [];
  for (let j = 1; j < cols.length; j++) {
    const vals = rows.map(r => r[j]);
    if (!vals.some(v => typeof v === "number") || vals.some(v => v != null && typeof v !== "number")) continue;
    out.push({ id: cols[j], label: cols[j], rows: rows.map(r => ({ label: String(r[0]), value: typeof r[j] === "number" ? r[j] : null })) });
  }
  return out;
}

/** THD (H2 to H5, power sum) on the H2 curve's frequencies. by: {H2: points, ...} */
export function thdOf(by) {
  const pts = [];
  for (const p of by.H2) {
    const v = ["H2", "H3", "H4", "H5"].map(k => interp(by[k], p.x));
    if (v.every(x => x != null)) pts.push({ x: p.x, y: 10 * Math.log10(v.reduce((s, x) => s + Math.pow(10, x / 10), 0)) });
  }
  return { id: "THD", label: "THD (H2 to H5)", points: pts, computed: true };
}

/** Move harmonic curves from the level they were measured at to another level with the level rule
 *  (dB of distortion per dB of level). Only for harmonic kinds; THD is rebuilt from the moved orders. */
export function shiftQuantities(quantities, from, to, slopes = TYPICAL_SLOPES) {
  const moved = quantities.filter(q => q.id !== "THD").map(q => {
    const s = slopes[q.id];
    if (s == null || !q.points) return q;
    return Object.assign({}, q, { points: q.points.map(p => ({ x: p.x, y: p.y + s * (to - from) })), shifted: to - from });
  });
  const by = Object.fromEntries(moved.filter(q => q.points).map(q => [q.id, q.points]));
  if (quantities.some(q => q.id === "THD") && ["H2", "H3", "H4", "H5"].every(k => by[k])) moved.push(thdOf(by));
  return moved;
}

// Harmonic orders first, level-sweep series by order then frequency, anything else in the order found.
export function sortQuantities(ids) {
  const key = id => {
    const r = ORDER_RANK.indexOf(id);
    if (r >= 0) return [r, 0];
    const m = id.match(/^H(\d+)\s+(\d+(?:\.\d+)?)\s*(k?)Hz$/i);
    if (m) return [Number(m[1]), Number(m[2]) * (m[3] ? 1000 : 1)];
    return [99, 0];
  };
  return ids.map((id, i) => ({ id, i, k: key(id) }))
    .sort((a, b) => a.k[0] - b.k[0] || a.k[1] - b.k[1] || a.i - b.i).map(x => x.id);
}

const pointCount = set => (set.series || []).reduce((n, s) => Math.max(n, (s.points || []).length), (set.rows || []).length);

/**
 * All comparable groups, most reliable source first.
 * Returns [{ key, family (name, or null when mixed), rank, kind, label, levels: [dB...],
 *            entries: [{ id, driver, family, sets: [{ set, index, level, quantities }] }], quantityIds }]
 * One entry is one driver from one source; its sets are that source's measurements of this kind at
 * different levels.
 */
export function buildGroups({ mix = false, drivers = allDrivers() } = {}) {
  const groups = new Map();
  for (const d of drivers) {
    (d.measurements || []).forEach((set, index) => {
      const fam = familyOf(set);
      if (!fam) return;
      if (set.superseded_by) return;       // an earlier capture of charts read again in full: kept on the driver page only
      const kind = kindOf(set);
      const quantities = quantitiesOf(set, kind);
      if (!quantities.length) return;
      const mk = matchKey(set, kind);
      const key = (mix ? "" : fam.name + "::") + kind.id + (mk ? "|" + mk : "");
      if (!groups.has(key)) {
        const ml = matchLabel(set, kind);
        groups.set(key, { key, family: mix ? null : fam.name, rank: mix ? 0 : (fam.rank || 99), kind,
                          label: kind.label + (ml ? " · " + ml : ""), entries: [] });
      }
      const g = groups.get(key);
      const eid = `${d.id}@${fam.name}`;
      let e = g.entries.find(x => x.id === eid);
      if (!e) { e = { id: eid, driver: d, family: fam, sets: [] }; g.entries.push(e); }
      e.sets.push({ set, index, level: levelOf(set), quantities });
    });
  }
  const list = [...groups.values()];
  for (const g of list) {
    const ids = new Set(), levels = new Set();
    // "spl-near" kinds: levels meant to be the same but stated slightly apart (91.1, 91.2, 91.7 dB) share one button
    const near = g.kind.level === "spl-near";
    g.entries.forEach(e => e.sets.forEach(s => { s.quantities.forEach(q => ids.add(q.id)); if (s.level != null) levels.add(s.level); }));
    g.quantityIds = sortQuantities([...ids]);
    const first = g.entries.flatMap(e => e.sets)[0];
    g.levelUnit = first ? levelUnit(first.set) : "dB";
    g.levels = near ? nearLevels([...levels]) : [...levels].sort((a, b) => a - b);
    g.entries.forEach(e => e.sets.sort((a, b) => (a.level ?? 0) - (b.level ?? 0)));
    g.entries.sort((a, b) => (a.family.rank || 99) - (b.family.rank || 99) || a.driver.name.localeCompare(b.driver.name));
  }
  return list.sort((a, b) => a.rank - b.rank || (a.family || "").localeCompare(b.family || "") || a.label.localeCompare(b.label, undefined, { numeric: true }));
}

/** Source families that have something to compare, most reliable first. */
export function sourcesOf(groups, families) {
  const names = new Set(groups.filter(g => g.family).map(g => g.family));
  return families.filter(f => names.has(f.name));
}

/** The level most drivers in a group were measured at (the higher one on a tie), or null. */
/** Levels that lie within 1 dB of each other, each group given as its mean to 0.1 dB: [91.1, 91.15, 91.67, 94] -> [91.3, 94]. */
export function nearLevels(levels) {
  const out = [];
  for (const L of levels.slice().sort((a, b) => a - b)) {
    if (out.length && L - out[out.length - 1][0] <= 1) out[out.length - 1].push(L); else out.push([L]);
  }
  return out.map(c => Math.round(c.reduce((a, b) => a + b, 0) / c.length * 10) / 10);
}

export function defaultLevel(group) {
  const count = new Map();
  group.entries.forEach(e => new Set(e.sets.map(s => s.level).filter(v => v != null)).forEach(L => count.set(L, (count.get(L) || 0) + 1)));
  return [...count.entries()].sort((a, b) => b[1] - a[1] || b[0] - a[0]).map(x => x[0])[0] ?? null;
}

/** The set of an entry closest to the target level (ties: more points, then higher level).
 *  Returns { ...set entry, delta: level - target (null when the kind has no level) }. */
export function pickSet(entry, target) {
  const sets = entry.sets;
  if (target == null || sets.every(s => s.level == null)) {
    const best = sets.slice().sort((a, b) => pointCount(b.set) - pointCount(a.set))[0];
    return Object.assign({}, best, { delta: null });
  }
  const best = sets.filter(s => s.level != null).sort((a, b) =>
    Math.abs(a.level - target) - Math.abs(b.level - target) || pointCount(b.set) - pointCount(a.set) || b.level - a.level)[0];
  return Object.assign({}, best, { delta: best.level - target });
}

/** Short description of an entry's data for pick lists. */
export function describe(entry) {
  const s = entry.sets[entry.sets.length - 1];
  const q = s.quantities[0], c = s.set.conditions || {};
  const bits = [];
  const levels = entry.sets.map(x => x.level).filter(v => v != null);
  const unit = levelUnit(s.set), stated = unit !== "dB";
  if (levels.length) bits.push(levels.length > 1 ? `measured at ${levels.map(v => Math.round(v * 100) / 100).join(", ")} ${unit}` : `${Math.round(levels[0] * 100) / 100} ${unit}`);
  if (q.points && q.points.length && s.set.chartType !== "bar") {
    const xs = entry.sets.flatMap(x => (x.quantities[0].points || []).map(p => p.x));
    bits.push(`${Math.max(...entry.sets.map(x => (x.quantities[0].points || []).length))} points`);
    if (/Hz/.test(((s.set.axes || {}).x || {}).unit || "")) bits.push(`${fmtHz(Math.min(...xs))} to ${fmtHz(Math.max(...xs))}`);
  }
  if (c.x_pk_mm != null && !stated) bits.push(`${c.x_pk_mm} mm peak excursion`);
  if (stated) bits.push(unit === "mm" ? "peak excursion of the low tone" : "drive per tone");
  if (s.set.confidence) bits.push(`${s.set.confidence} confidence`);
  return bits.join(" · ");
}

export { num };
