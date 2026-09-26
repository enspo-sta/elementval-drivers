/* directivity.js: a driver's measured off-axis response relative to its own on-axis response, for Simulate.
 * No DOM, so it is tested on its own (node --test tests/).
 *
 * From the source's own relative charts (kind off-axis-normalized) when they have the angle, the chart drawn
 * over the smallest range of dB first (10-25 or 5-30 dB before 10-50 dB); else from the off-axis sound pressure (kind off-axis) as the angle's
 * curve minus the 0° curve. Where lines lie on top of each other the chart reading has gaps; a line hidden
 * under others lies where they are, so the curve is interpolated across its gaps here. Outside the measured
 * range there is no value (null). Superseded sets are not used. */

const angleOf = name => { const m = String(name).match(/^(\d+)°$/); return m ? Number(m[1]) : null; };
const pts = s => (s.points || []).filter(p => p && p.x > 0 && p.y != null).map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
const offSets = driver => (driver.measurements || []).filter(m => !m.superseded_by && (m.kind === "off-axis-normalized" || m.kind === "off-axis"));

/** Angles (degrees) the driver has off-axis data for, 0 excluded. */
export function anglesOf(driver) {
  const out = new Set();
  for (const m of offSets(driver)) for (const s of m.series || []) { const a = angleOf(s.name); if (a) out.add(a); }
  return [...out].sort((a, b) => a - b);
}

/** { fn(f) -> dB re on axis | null, from, set } for one angle, or null when the driver has none. 0° is 0 dB.
 * opts.order(set) -> number: sets with a lower number are tried first (Simulate: the chosen source first, then the
 * others by reliability), so one source's measurements are not mixed with another's while the chosen one has them. */
export function directivityOf(driver, angle, opts = {}) {
  if (!angle) return { fn: () => 0, from: "on axis" };
  const order = opts.order || (() => 0);
  const groups = [...new Set(offSets(driver).map(order))].sort((a, b) => a - b);
  for (const g of groups) {
    const found = fromSets(offSets(driver).filter(m => order(m) === g), angle);
    if (found) return found;
  }
  return null;
}

function fromSets(sets, angle) {
  const norm = sets.filter(m => m.kind === "off-axis-normalized").sort((a, b) => rangeOrder(a) - rangeOrder(b));
  for (const m of norm) {
    const s = (m.series || []).find(x => angleOf(x.name) === angle);
    const p = s ? pts(s) : [];
    if (p.length > 1) return { fn: curveFn(p), from: m.type, set: m };
  }
  for (const m of sets.filter(m => m.kind === "off-axis")) {
    const s = (m.series || []).find(x => angleOf(x.name) === angle), s0 = (m.series || []).find(x => angleOf(x.name) === 0);
    const p = s ? pts(s) : [], p0 = s0 ? pts(s0) : [];
    if (p.length > 1 && p0.length > 1) {
      const a = curveFn(p), b = curveFn(p0);
      return { fn: f => { const u = a(f), v = b(f); return u == null || v == null ? null : u - v; }, from: m.type + " (the angle minus 0°)", set: m };
    }
  }
  return null;
}

// the chart drawn over the smallest range of dB first (5-30 or 10-25 before 10-50): its reading is the finest
const rangeOrder = m => { const r = String((m.conditions || {}).chart_range_db || "").match(/^(\d+)-(\d+)$/); return r ? Number(r[2]) - Number(r[1]) : 999; };
// p is sorted once (pts); each lookup is a binary search, so a file of 20 000 points costs nothing per frequency
function curveFn(p) {
  const lo = p[0].x, hi = p[p.length - 1].x;
  return f => {
    if (!(f >= lo && f <= hi)) return null;
    let i = 0, j = p.length - 1;
    while (j - i > 1) { const k = (i + j) >> 1; if (p[k].x <= f) i = k; else j = k; }
    const a = p[i], b = p[j];
    if (b.x === a.x || f === a.x) return a.y;
    return a.y + (Math.log(f / a.x) / Math.log(b.x / a.x)) * (b.y - a.y);
  };
}
