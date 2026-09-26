/* sim.js: crossover and speaker-distortion maths for the Simulate view. No page code here, so it
 * is tested on its own (node --test tests/).
 *
 * Model used by simulate():
 *  - Each way gets the input signal through its crossover filter (electrical = acoustic;
 *    drivers assumed flat and level-matched, so each way's output is target SPL x |H(f)|).
 *  - A driver may have been measured at several levels. At every frequency the harmonic ratio is
 *    taken at the level the driver actually plays at: between two measured levels the curves are
 *    interpolated (linear in dB against level); beyond the measured levels the nearest curve is moved
 *    with the level rule  HD_k(f, L) = HD_k(f, L0) + s_k * (L - L0)  (s_k in dB per dB).
 *  - n identical drivers in one way each play 20*log10(n) dB lower; being identical, their harmonics
 *    add in step, so the way's harmonic ratio is one driver's ratio at that lower level.
 *  - Harmonics from different drivers add as powers (no fixed phase between them); the result is
 *    expressed relative to the speaker's summed fundamental.
 *  - A driver playing more than 40 dB below the target at f is ignored there; if a driver that
 *    matters at f has no data at f, the speaker value at f is left empty rather than guessed.
 */

// ---- complex numbers ----
const C = (re, im) => ({ re, im: im || 0 });
const mul = (a, b) => C(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
const div = (a, b) => { const d = b.re * b.re + b.im * b.im; return C((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d); };
const add = (a, b) => C(a.re + b.re, a.im + b.im);
const abs = a => Math.hypot(a.re, a.im);
const db = x => 20 * Math.log10(Math.max(x, 1e-12));

// Normalised Butterworth denominators as products of quadratic/linear sections (highest power first).
const BW = {
  1: [[1, 1]],
  2: [[1, Math.SQRT2, 1]],
  3: [[1, 1], [1, 1, 1]],
  4: [[1, 0.7653668647, 1], [1, 1.8477590650, 1]],
};
// Crossover types: which Butterworth section is used, how many times, and whether the upper side
// is wired in reverse polarity (standard practice for LR2 and BW2, which otherwise notch at fc).
export const TYPES = {
  LR2: { bw: 1, times: 2, invert: true, label: "Linkwitz-Riley 2nd order (12 dB/oct)" },
  LR4: { bw: 2, times: 2, invert: false, label: "Linkwitz-Riley 4th order (24 dB/oct)" },
  LR8: { bw: 4, times: 2, invert: false, label: "Linkwitz-Riley 8th order (48 dB/oct)" },
  BW1: { bw: 1, times: 1, invert: false, label: "Butterworth 1st order (6 dB/oct)" },
  BW2: { bw: 2, times: 1, invert: true, label: "Butterworth 2nd order (12 dB/oct)" },
  BW3: { bw: 3, times: 1, invert: false, label: "Butterworth 3rd order (18 dB/oct)" },
  BW4: { bw: 4, times: 1, invert: false, label: "Butterworth 4th order (24 dB/oct)" },
};

function polyAt(coeffs, s) {                 // coeffs highest power first
  let r = C(0, 0);
  for (const k of coeffs) r = add(mul(r, s), C(k, 0));
  return r;
}
function section(type, f, fc, high) {        // complex response of one low- or high-pass
  const t = TYPES[type];
  if (!t) throw new Error("unknown crossover type " + type);
  const s = C(0, f / fc);
  let h = C(1, 0);
  for (let i = 0; i < t.times; i++) {
    for (const q of BW[t.bw]) {
      const den = polyAt(q, s);
      const order = q.length - 1;
      let num = C(1, 0);
      if (high) for (let j = 0; j < order; j++) num = mul(num, s);
      h = mul(h, div(num, den));
    }
  }
  return h;
}

/** Complex response of every way at frequency f.
 *  points: [{fc, type}] between way i and way i+1, ordered low to high.
 *  aligned = false: plain filters, way i = HP(i-1) x LP(i). With three or more ways the sum dips
 *    between crossovers that are close together (about -8 dB for LR4 at 500 and 1000 Hz).
 *  aligned = true: the usual all-pass correction of multi-way crossovers. Way i also gets every
 *    lower high-pass and, for each higher crossover k, the all-pass LP(k) + HP(k). The ways then sum
 *    to the product of those all-passes, which is flat in level for Linkwitz-Riley and for
 *    Butterworth 1st and 3rd order. */
export function wayResponses(f, points, aligned) {
  const n = points.length + 1, out = [];
  const lp = points.map(p => section(p.type, f, p.fc, false));
  const hp = points.map(p => section(p.type, f, p.fc, true));
  const sg = points.map(p => (TYPES[p.type].invert ? -1 : 1));
  for (let i = 0; i < n; i++) {
    let h = C(1, 0), sign = 1;
    if (aligned) { for (let k = 0; k < i; k++) h = mul(h, hp[k]); }
    else if (i > 0) h = mul(h, hp[i - 1]);
    if (i < n - 1) h = mul(h, lp[i]);
    if (aligned) for (let k = i + 1; k < n - 1; k++) h = mul(h, add(lp[k], C(sg[k] * hp[k].re, sg[k] * hp[k].im)));
    for (let k = 0; k < i; k++) sign *= sg[k];
    out.push(C(h.re * sign, h.im * sign));
  }
  return out;
}

/** Log-spaced frequency grid, `perOctave` points per octave (24 = 1/24 octave). */
export function logGrid(fLo, fHi, perOctave) {
  const n = Math.floor(Math.log2(fHi / fLo) * perOctave), out = [];
  for (let i = 0; i <= n; i++) out.push(fLo * Math.pow(2, i / perOctave));
  return out;
}

/** Value of a measured curve at f: linear in dB between neighbouring points on a log-frequency
 *  axis. Returns null outside the measured range or next to a missing point. */
export function interpLog(points, f) {
  const p = points.filter(q => q && typeof q.x === "number" && q.x > 0).sort((a, b) => a.x - b.x);
  if (!p.length || f < p[0].x || f > p[p.length - 1].x) return null;
  for (let i = 0; i < p.length - 1; i++) {
    const a = p[i], b = p[i + 1];
    if (f >= a.x && f <= b.x) {
      if (a.y == null || b.y == null) return null;
      if (b.x === a.x) return a.y;
      const t = Math.log(f / a.x) / Math.log(b.x / a.x);
      return a.y + t * (b.y - a.y);
    }
  }
  return p[p.length - 1].x === f ? p[p.length - 1].y : null;
}

/** Slope (dB of harmonic ratio per dB of level) from a level sweep, fitted over [lo, hi] dB. */
export function slopeFromSweep(points, lo, hi) {
  const q = points.filter(p => p.y != null && p.x >= lo && p.x <= hi);
  if (q.length < 3) return null;
  const mx = q.reduce((s, p) => s + p.x, 0) / q.length, my = q.reduce((s, p) => s + p.y, 0) / q.length;
  const sxx = q.reduce((s, p) => s + (p.x - mx) ** 2, 0);
  if (sxx === 0) return null;
  return q.reduce((s, p) => s + (p.x - mx) * (p.y - my), 0) / sxx;
}

/** Slopes measured at a few frequencies -> a function of frequency (log-interpolated, held flat
 *  beyond the first and last measured frequency). byFreq: [{f, slope}] */
export function slopeCurve(byFreq) {
  const p = byFreq.filter(q => q.slope != null).sort((a, b) => a.f - b.f);
  if (!p.length) return null;
  return f => {
    if (f <= p[0].f) return p[0].slope;
    if (f >= p[p.length - 1].f) return p[p.length - 1].slope;
    for (let i = 0; i < p.length - 1; i++) if (f <= p[i + 1].f) {
      const t = Math.log(f / p[i].f) / Math.log(p[i + 1].f / p[i].f);
      return p[i].slope + t * (p[i + 1].slope - p[i].slope);
    }
    return p[p.length - 1].slope;
  };
}

export const LAWS = {
  typical: { label: "Typical from your data: H2 +1.0, H3 to H5 +0.7 dB per dB", slopes: { H2: 1.0, H3: 0.7, H4: 0.7, H5: 0.7 } },
  classic: { label: "Textbook (n-1) rule: H2 +1, H3 +2, H4 +3, H5 +4 dB per dB", slopes: { H2: 1, H3: 2, H4: 3, H5: 4 } },
  none: { label: "No level change (use the curves as measured)", slopes: { H2: 0, H3: 0, H4: 0, H5: 0 } },
};

/**
 * Harmonic ratio of one way's driver for order k at fundamental f when the driver plays at level L.
 * Uses every measured level that has data at f: interpolates between the two levels around L, or
 * moves the nearest measured level with the way's slope when L is outside them. null when no curve
 * has data at f.
 */
export function harmonicAt(way, k, f, L) {
  const curves = way.curves || [{ L0: way.L0, hd: way.hd }];
  const at = [];
  for (const c of curves) {
    const pts = c.hd && c.hd[k];
    const v = pts ? interpLog(pts, f) : null;
    if (v != null) at.push({ L0: c.L0, v });
  }
  if (!at.length) return null;
  at.sort((a, b) => a.L0 - b.L0);
  const lo = at[0], hi = at[at.length - 1];
  if (L <= lo.L0) return lo.v + way.slope(k, f) * (L - lo.L0);
  if (L >= hi.L0) return hi.v + way.slope(k, f) * (L - hi.L0);
  for (let i = 0; i < at.length - 1; i++) {
    const a = at[i], b = at[i + 1];
    if (L >= a.L0 && L <= b.L0) return b.L0 === a.L0 ? a.v : a.v + (b.v - a.v) * (L - a.L0) / (b.L0 - a.L0);
  }
  return hi.v;
}

/**
 * Simulate a speaker's harmonic distortion.
 * opts = {
 *   freqs: [Hz], target: dB SPL at 1 m, orders: ["H2","H3",...],
 *   points: [{fc, type}]   (ways - 1 entries, low to high), aligned: true for all-pass correction,
 *   ways: [{ name, curves: [{ L0, hd: {H2: [{x,y}], ...} }] (one per measured level; or L0 and hd for a
 *            single level), slope: (order, f) => dB per dB, count: identical drivers (1) }],
 *   ignoreBelowDb: -40
 * }
 * Returns { freqs, response: {ways: [[dB]], sum: [dB]}, system: {H2: [dB|null], ..., THD: [...]},
 *           partial: {H2: [bool], ..., THD: [bool]}, contrib: [{H2: [...], ...}] per way, gaps: [{way, order, from, to}] }
 * Where a way that matters has no data for an order, the speaker's value is the sum of the ways that do have
 * data and partial is true there: the real value is at least that high. It is null only when no way that
 * matters has data.
 */
export function simulate(opts) {
  const { freqs, target, orders, points, ways } = opts;
  const ignore = opts.ignoreBelowDb == null ? -40 : opts.ignoreBelowDb;
  const system = {}, partial = {}, contrib = ways.map(() => ({})), gapsRaw = [];
  for (const k of orders) { system[k] = []; partial[k] = []; ways.forEach((w, i) => (contrib[i][k] = [])); }
  system.THD = []; partial.THD = [];
  const response = { ways: ways.map(() => []), sum: [] };

  freqs.forEach((f, fi) => {
    const hs = wayResponses(f, points, !!opts.aligned);
    const sum = hs.reduce(add, C(0, 0));
    const lsys = target + db(abs(sum));
    response.sum.push(db(abs(sum)));
    hs.forEach((h, i) => response.ways[i].push(db(abs(h))));
    let thdPower = 0, thdOk = false, thdPartial = false;
    for (const k of orders) {
      let power = 0, missing = false;
      ways.forEach((w, i) => {
        const magDb = db(abs(hs[i]));
        if (magDb < ignore) { contrib[i][k].push(null); return; }
        const ld = target + magDb;                          // what the way plays at f
        const each = ld - 20 * Math.log10(w.count || 1);   // identical drivers share it equally
        const hd = harmonicAt(w, k, f, each);
        if (hd == null) { missing = true; contrib[i][k].push(null); gapsRaw.push({ way: i, order: k, f, fi }); return; }
        const absLevel = ld + hd;                          // their harmonics add in step (same ratio)
        contrib[i][k].push(absLevel - lsys);
        power += Math.pow(10, absLevel / 10);
      });
      const v = power === 0 ? null : 10 * Math.log10(power) - lsys;
      system[k].push(v);
      partial[k].push(v != null && missing);
      // THD from the orders that have a value; an order with no value, or a partial one, makes THD a lower bound
      if (v == null) thdPartial = true; else { thdOk = true; thdPower += Math.pow(10, v / 10); if (missing) thdPartial = true; }
    }
    const thd = thdOk && thdPower > 0 ? 10 * Math.log10(thdPower) : null;
    system.THD.push(thd);
    partial.THD.push(thd != null && thdPartial);
  });

  // merge gap points into ranges per way and order
  const gaps = [];
  for (const g of gapsRaw) {
    const last = gaps.find(x => x.way === g.way && x.order === g.order && x.lastIndex === g.fi - 1);
    if (last) { last.to = g.f; last.lastIndex = g.fi; }
    else gaps.push({ way: g.way, order: g.order, from: g.f, to: g.f, lastIndex: g.fi });
  }
  gaps.forEach(g => delete g.lastIndex);
  return { freqs, response, system, partial, contrib, gaps };
}

/** A measured curve with its unseen stretches marked: where two neighbouring points are further apart than
 *  1/6 octave and three times the curve's typical spacing (the automatic chart reading leaves out what it
 *  could not see), a null point is put between them, so interpLog gives null there instead of a straight
 *  line across. Sparse hand captures (a point every 2/3 octave) are not split. */
export function markGaps(points) {
  const p = (points || []).filter(q => q && typeof q.x === "number" && q.x > 0 && q.y != null).sort((a, b) => a.x - b.x);
  if (p.length < 3) return p;
  const steps = p.slice(1).map((q, i) => Math.log2(q.x / p[i].x)).sort((a, b) => a - b);
  const limit = Math.max(1 / 6, 3 * steps[Math.floor(steps.length / 2)]);
  const out = [p[0]];
  for (let i = 1; i < p.length; i++) {
    if (Math.log2(p[i].x / p[i - 1].x) > limit) out.push({ x: Math.sqrt(p[i].x * p[i - 1].x), y: null });
    out.push(p[i]);
  }
  return out;
}

/** Where a way plays within `ignoreDb` of the speaker's level: [lowest, highest] frequency on a 1/12-octave
 *  grid from 20 Hz to 20 kHz, one pair per way. */
export function audibleBands(points, aligned, ignoreDb = -40) {
  const grid = logGrid(20, 20000, 12), n = points.length + 1;
  const bands = Array.from({ length: n }, () => [null, null]);
  for (const f of grid) {
    wayResponses(f, points, aligned).forEach((h, i) => {
      if (db(abs(h)) >= ignoreDb) { if (bands[i][0] == null) bands[i][0] = f; bands[i][1] = f; }
    });
  }
  return bands.map(b => [b[0] ?? 20, b[1] ?? 20000]);
}

/** dB re fundamental -> percent */
export const dbToPct = v => (v == null ? null : 100 * Math.pow(10, v / 20));


export const _c = { C, abs, add };
