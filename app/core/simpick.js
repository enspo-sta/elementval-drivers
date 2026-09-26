/* simpick.js: the drivers Simulate can use and the default choice per way, shared by the Simulate tab,
 * tools/sim_coverage.mjs and the tests. No DOM. */
import * as SC from "./sim.js";

export const ORDERS = ["H2", "H3", "H4", "H5"];
export const GRID = SC.logGrid(20, 20000, 12);          // 1/12 octave, for coverage

/** true when a gap-marked, sorted curve has a value at f (both neighbouring points present) */
export function hasData(pts, f) {
  let lo = 0, hi = pts.length - 1;
  if (!pts.length || f < pts[0].x || f > pts[hi].x) return false;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (pts[m].x <= f) lo = m; else hi = m; }
  return pts[lo].y != null && (pts[lo].x === f || pts[hi].y != null);
}

/** One candidate per driver and source from the harmonic-distortion groups of buildGroups(): every level of
 *  that driver, its curves gap-marked (a stretch the source curve does not show counts as missing), and on
 *  GRID where every order has data at one level or more. */
export function buildCandidates(groups, mix, src) {
  const out = [];
  for (const g of groups) {
    if (g.kind.id !== "hd-frequency" || /near field/.test(g.key)) continue;   // near-field curves are not the driver's far-field output
    for (const e of g.entries) {
      if (!mix && e.family.name !== src) continue;
      const curves = e.sets.filter(s => s.level != null).map(s => {
        const hd = {};
        s.quantities.forEach(q => { if (ORDERS.includes(q.id)) hd[q.id] = SC.markGaps(q.points); });
        return { L0: s.level, hd, set: s.set };
      }).filter(c => c.hd.H2 || c.hd.H3);
      if (!curves.length) continue;
      const xs = curves.flatMap(c => Object.values(c.hd).flat().filter(p => p.y != null).map(p => p.x));
      const orders = ORDERS.filter(k => curves.some(c => c.hd[k]));
      const byOrder = Object.fromEntries(orders.map(k => [k, GRID.map(f => curves.some(c => c.hd[k] && hasData(c.hd[k], f)))]));
      const covered = GRID.map((f, j) => orders.every(k => byOrder[k][j]));
      out.push({ id: e.id, e, curves, levels: curves.map(c => c.L0), orders, covered, byOrder,
                 lo: Math.min(...xs), hi: Math.max(...xs) });
    }
  }
  return out.sort((a, b) => a.e.driver.name.localeCompare(b.e.driver.name) || (a.e.family.rank || 99) - (b.e.family.rank || 99));
}

/** Where a driver's role puts it in a speaker: 0 = lowest way, 1 = highest. */
export function rolePos(role) {
  const r = (role || "").toLowerCase();
  if (/tweeter/.test(r)) return 1;
  if (/^midrange/.test(r)) return 0.6;
  if (/^midbass \/ mid/.test(r)) return 0.42;
  if (/^midbass/.test(r)) return 0.38;
  if (/^woofer \/ midbass/.test(r)) return 0.22;
  if (/woofer/.test(r)) return 0.05;
  return 0.5;
}

/** Share of a band [lo, hi] (on GRID) where a candidate has data for every order. */
export function coverage(c, lo, hi) {
  const idx = GRID.map((f, j) => j).filter(j => GRID[j] >= lo && GRID[j] <= hi);
  return idx.length ? idx.filter(j => c.covered[j]).length / idx.length : 0;
}

/** The stretches of [lo, hi] where the candidate has no data for an order: [{order, from, to}] (Hz). */
export function missingIn(c, lo, hi) {
  const out = [];
  for (const k of c.orders) {
    let run = null;
    GRID.forEach((f, j) => {
      const miss = f >= lo && f <= hi && !c.byOrder[k][j];
      if (miss && !run) run = { order: k, from: f, to: f };
      else if (miss) run.to = f;
      else if (run) { out.push(run); run = null; }
    });
    if (run) out.push(run);
  }
  return out;
}

/** Default driver per way: its data covers the whole band where the way still plays within 40 dB of the
 *  others (a gap there leaves the speaker's curve incomplete), and its role fits the way. */
export function autoPick(n, x, types, aligned, cands) {
  const used = new Set(), out = [];
  const bands = SC.audibleBands(x.map((fc, i) => ({ fc, type: (types && types[i]) || "LR4" })), aligned);
  for (let i = 0; i < n; i++) {
    const [lo, hi] = bands[i], pos = i / (n - 1);
    const score = c => 2 * coverage(c, lo, hi) - 1.2 * Math.abs(rolePos(c.e.driver.role) - pos) +
      c.orders.length * 0.01 + c.levels.length * 0.005 + (used.has(c.id) ? -2 : 0);
    const best = cands.slice().sort((a, b) => score(b) - score(a))[0];
    out.push(best ? best.id : null);
    if (best) used.add(best.id);
  }
  return out;
}
