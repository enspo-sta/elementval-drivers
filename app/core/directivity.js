/* directivity.js: a driver's measured off-axis response relative to its own on-axis response, for Simulate.
 * No DOM, so it is tested on its own (node --test tests/).
 *
 * From the source's own relative charts (kind off-axis-normalized) when they have the angle, the finer chart
 * range first (5-30 dB before 10-50 dB); else from the off-axis sound pressure (kind off-axis) as the angle's
 * curve minus the 0° curve. Where lines lie on top of each other the chart reading has gaps; a line hidden
 * under others lies where they are, so the curve is interpolated across its gaps here. Outside the measured
 * range there is no value (null). Superseded sets are not used. */
import { interpLog } from "./sim.js";

const angleOf = name => { const m = String(name).match(/^(\d+)°$/); return m ? Number(m[1]) : null; };
const pts = s => (s.points || []).filter(p => p && p.x > 0 && p.y != null).map(p => ({ x: Number(p.x), y: Number(p.y) })).sort((a, b) => a.x - b.x);
const offSets = driver => (driver.measurements || []).filter(m => !m.superseded_by && (m.kind === "off-axis-normalized" || m.kind === "off-axis"));

/** Angles (degrees) the driver has off-axis data for, 0 excluded. */
export function anglesOf(driver) {
  const out = new Set();
  for (const m of offSets(driver)) for (const s of m.series || []) { const a = angleOf(s.name); if (a) out.add(a); }
  return [...out].sort((a, b) => a - b);
}

/** { fn(f) -> dB re on axis | null, from } for one angle, or null when the driver has none. 0° is 0 dB. */
export function directivityOf(driver, angle) {
  if (!angle) return { fn: () => 0, from: "on axis" };
  const norm = offSets(driver).filter(m => m.kind === "off-axis-normalized")
    .sort((a, b) => rangeOrder(a) - rangeOrder(b));
  for (const m of norm) {
    const s = (m.series || []).find(x => angleOf(x.name) === angle);
    if (s && pts(s).length > 1) return { fn: curveFn(pts(s)), from: m.type, set: m };
  }
  for (const m of offSets(driver).filter(m => m.kind === "off-axis")) {
    const s = (m.series || []).find(x => angleOf(x.name) === angle), s0 = (m.series || []).find(x => angleOf(x.name) === 0);
    if (s && s0 && pts(s).length > 1 && pts(s0).length > 1) {
      const a = curveFn(pts(s)), b = curveFn(pts(s0));
      return { fn: f => { const u = a(f), v = b(f); return u == null || v == null ? null : u - v; }, from: m.type + " (the angle minus 0°)", set: m };
    }
  }
  return null;
}

const rangeOrder = m => { const r = (m.conditions || {}).chart_range_db || ""; return r === "5-30" ? 0 : r ? 1 : 2; };
function curveFn(p) {
  const lo = p[0].x, hi = p[p.length - 1].x;
  return f => (f < lo || f > hi ? null : interpLog(p, f));
}
