/* compare-core.js: decides which measurement sets can be overlaid in the viewer's Compare and
 * Simulate views. No page code here, so it can be tested on its own (node tests/compare-core.test.js).
 * In the browser it becomes window.CompareCore; in node it is module.exports.
 *
 * Two sets are comparable when they come from the same source family (watch/config.json) and
 * measure the same thing under the same conditions: the same kind of chart, the same test tones,
 * the same level. That rule is the "kind" below. With mixing switched on, the source family is
 * left out of the rule and sets from different sources can share a chart.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CompareCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // Okabe and Ito's colour-blind safe palette; the viewer never draws more than five drivers at once.
  const COLORS = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#CC79A7"];
  const MARKERS = ["circle", "triangle", "rect", "rectRot", "star"];
  const DASHES = [[], [7, 4], [2, 3], [10, 3, 2, 3], [14, 5]];
  const MAX_PICK = 5;
  const ORDER_RANK = ["H2", "H3", "H4", "H5", "THD", "Gm"];

  const num = v => {
    if (typeof v === "number") return v;
    const m = String(v == null ? "" : v).match(/-?\d+(?:\.\d+)?/);
    return m ? Number(m[0]) : null;
  };
  const fmtHz = f => (f >= 1000 ? (Math.round(f / 100) / 10) + " kHz" : Math.round(f) + " Hz");

  function familyOf(set, families) {
    for (const f of families || []) {
      try { if (new RegExp(f.match, "i").test(set.source || "")) return f; } catch (e) { /* bad pattern in config */ }
    }
    return null;
  }

  /** Test tones of an intermodulation set as [f1, f2] in Hz, or null. */
  function tonesOf(set) {
    const text = [set.method, set.type].join(" ");
    const m = text.match(/(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*Hz/i);
    if (m) return [Number(m[1]), Number(m[2])];
    const c = set.conditions || {};
    const f1 = num(c.f1), f2 = num(c.f2);
    return f1 != null && f2 != null ? [f1, f2] : null;
  }
  const isImd = set => /\bimd\b|two-tone|intermod/i.test((set.type || "") + " " + (set.method || ""));

  /** What a set measures, as a comparable key plus how to draw it. */
  function kindOf(set) {
    const t = (set.type || "").toLowerCase(), c = set.conditions || {}, ax = set.axes || {};
    const spl = num(c.spl_db != null ? c.spl_db : c.ref_spl_db);
    const tones = isImd(set) ? tonesOf(set) : null;
    const toneText = tones ? `${tones[0]} + ${tones[1]} Hz` : "";
    if (set.chartType === "table") {
      if (tones) return { key: `imd-table|${tones.join("+")}`, view: "table", label: `Intermodulation ${toneText}${c.ratio ? ", " + c.ratio : ""} (summary values)` };
      return { key: `table|${set.type}`, view: "table", label: set.type };
    }
    if (set.chartType === "bar") {
      if (tones) {
        const each = /each tone/i.test(c.note || "");
        const lvl = spl != null ? (each ? `, each tone ${spl} dB` : ` at ${spl} dB`) : "";
        return { key: `imd-bars|${tones.join("+")}|${spl}|${each ? "each" : "ref"}`, view: "bars", tones,
                 label: `Intermodulation ${toneText}${lvl}` };
      }
      return { key: `bars|${set.type}`, view: "bars", label: set.type };
    }
    const xl = ((ax.x && ax.x.label) || "").toLowerCase(), yl = ((ax.y && ax.y.label) || "").toLowerCase();
    if (/current/.test(t) || /current/.test(yl)) return { key: "hd-current", view: "curve", xlog: true, ratio: true,
      label: "Current distortion vs frequency (electrical, not sound pressure)", xTitle: "Frequency (Hz)", yTitle: "Current harmonic (dB)" };
    if (/^hd/.test(t) && (/spl|level/.test(xl) || /level sweep|vs spl/.test(t))) return { key: "hd-level", view: "curve", xlog: false, ratio: true,
      label: "Harmonic distortion vs level (level sweep)", xTitle: "Fundamental level (dB SPL at 1 m)", yTitle: "dB re fundamental" };
    if (/^hd/.test(t)) {
      // Harmonic levels stored as sound pressure are turned into ratios by subtracting the test level.
      const offset = /^spl$/.test(yl) && spl != null ? -spl : 0;
      return { key: `hd-f|${spl}`, view: "curve", xlog: true, ratio: true, offset, level: spl,
               label: `Harmonic distortion vs frequency at ${spl} dB`, xTitle: "Frequency (Hz)", yTitle: "dB re fundamental" };
    }
    const unit = u => (u ? ` (${u})` : "");
    return { key: `curve|${set.type}`, view: "curve", xlog: (ax.x && ax.x.scale) === "log", label: set.type,
             xTitle: ((ax.x && ax.x.label) || "") + unit(ax.x && ax.x.unit), yTitle: ((ax.y && ax.y.label) || "") + unit(ax.y && ax.y.unit) };
  }

  /** Log-frequency interpolation used for the computed THD curve (null outside the data). */
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

  /** The quantities a set offers for comparison. Curves: one per series (plus THD when H2 to H5 are
   *  all there). Bars: each product, and the power sum of all products. Tables: each numeric column. */
  function quantitiesOf(set, kind) {
    if (kind.view === "curve") {
      const out = [], by = {};
      for (const s of set.series || []) {
        const pts = (s.points || []).filter(p => p && p.x != null && p.y != null)
          .map(p => ({ x: Number(p.x), y: Number(p.y) + (kind.offset || 0) })).sort((a, b) => a.x - b.x);
        if (!pts.length) continue;
        out.push({ id: s.name, label: s.name, points: pts });
        by[s.name] = pts;
      }
      if (kind.ratio && kind.key.startsWith("hd-f") && ["H2", "H3", "H4", "H5"].every(k => by[k])) {
        const pts = [];
        for (const p of by.H2) {
          const v = ["H2", "H3", "H4", "H5"].map(k => interp(by[k], p.x));
          if (v.every(x => x != null)) pts.push({ x: p.x, y: 10 * Math.log10(v.reduce((s, x) => s + Math.pow(10, x / 10), 0)) });
        }
        if (pts.length) out.push({ id: "THD", label: "THD (H2 to H5)", points: pts, computed: true });
      }
      return out;
    }
    if (kind.view === "bars") {
      const pts = ((set.series && set.series[0] && set.series[0].points) || []).filter(p => p && p.y != null)
        .map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
      const tones = kind.tones || [];
      const toneBar = pts.find(p => tones.length && Math.abs(p.x - tones[1]) < 0.5);
      const ref = toneBar ? toneBar.y : 0;
      const products = pts.filter(p => !tones.some(t => Math.abs(p.x - t) < 0.5)).map(p => ({ x: p.x, y: p.y - ref }));
      const relTo = toneBar ? `dB relative to the ${fmtHz(tones[1])} tone` : "dB relative to the fundamental, as published";
      const total = products.length ? 10 * Math.log10(products.reduce((s, p) => s + Math.pow(10, p.y / 10), 0)) : null;
      return [
        { id: "products", label: "Each product", points: products, relTo },
        { id: "sum", label: "Sum of all products", value: total, relTo, computed: true },
      ];
    }
    // table: first column names the row, numeric columns become quantities
    const cols = set.columns || [], rows = set.rows || [];
    const out = [];
    for (let j = 1; j < cols.length; j++) {
      const vals = rows.map(r => r[j]);
      if (!vals.some(v => typeof v === "number") || vals.some(v => v != null && typeof v !== "number")) continue;
      out.push({ id: cols[j], label: cols[j], rows: rows.map(r => ({ label: String(r[0]), value: typeof r[j] === "number" ? r[j] : null })) });
    }
    return out;
  }

  // Harmonic orders first (H2, H3, ...), level-sweep series by order then by frequency ("H3 125 Hz"
  // before "H3 1kHz"); anything else keeps the order it was found in.
  function sortQuantities(ids) {
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

  /**
   * All comparable groups. drivers: records with id, name, measurements[]. families: config families.
   * mix: false keeps every source apart (the default). Returns groups sorted by source rank, then label:
   * [{ key, family (name or null when mixed), rank, kind, label, entries: [{ id, driver, set, family, quantities }] }]
   */
  function buildGroups(drivers, families, mix) {
    const groups = new Map();
    for (const d of drivers || []) {
      if (d.isComparison) continue;
      (d.measurements || []).forEach((set, i) => {
        const fam = familyOf(set, families);
        if (!fam) return;
        const kind = kindOf(set);
        const quantities = quantitiesOf(set, kind);
        if (!quantities.length) return;
        const key = (mix ? "" : fam.name + "::") + kind.key;
        if (!groups.has(key)) groups.set(key, { key, family: mix ? null : fam.name, rank: mix ? 0 : (fam.rank || 99), kind, label: kind.label, entries: [] });
        groups.get(key).entries.push({ id: `${d.id}#${i}`, driver: d, set, index: i, family: fam, quantities });
      });
    }
    const list = [...groups.values()];
    for (const g of list) {
      const ids = new Set();
      g.entries.forEach(e => e.quantities.forEach(q => ids.add(q.id)));
      g.quantityIds = sortQuantities([...ids]);
      g.entries.sort((a, b) => (a.family.rank || 99) - (b.family.rank || 99) || a.driver.name.localeCompare(b.driver.name));
    }
    return list.sort((a, b) => a.rank - b.rank || (a.family || "").localeCompare(b.family || "") || a.label.localeCompare(b.label, undefined, { numeric: true }));
  }

  /** Families that have something to compare, most reliable first. */
  function sourcesOf(groups, families) {
    const names = [...new Set(groups.filter(g => g.family).map(g => g.family))];
    return (families || []).filter(f => names.includes(f.name)).slice().sort((a, b) => (a.rank || 99) - (b.rank || 99));
  }

  /** Short description of one entry's data, for pick lists. */
  function describe(entry) {
    const q = entry.quantities[0], c = entry.set.conditions || {};
    const bits = [];
    if (q.points && q.points.length && entry.set.chartType !== "bar") {
      const xs = q.points.map(p => p.x);
      bits.push(`${q.points.length} points`);
      if (/Hz/.test(((entry.set.axes || {}).x || {}).unit || "")) bits.push(`${fmtHz(Math.min(...xs))} to ${fmtHz(Math.max(...xs))}`);
    }
    if (c.drive_v != null && c.drive_v !== "") bits.push(`${Array.isArray(c.drive_v) ? c.drive_v.join(" and ") : c.drive_v} V`);
    if (c.x_pk_mm != null) bits.push(`${c.x_pk_mm} mm peak excursion`);
    if (c.spl_db != null && entry.set.chartType === "table") bits.push(`${c.spl_db} dB`);
    if (entry.set.confidence) bits.push(`${entry.set.confidence} confidence`);
    return bits.join(" · ");
  }

  return { COLORS, MARKERS, DASHES, MAX_PICK, num, fmtHz, familyOf, tonesOf, kindOf, quantitiesOf, buildGroups, sourcesOf, describe, interp };
});
