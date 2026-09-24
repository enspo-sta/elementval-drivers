// Tests for app/core/sim.js (crossover and distortion maths). Run: node --test tests/
import test from "node:test";
import assert from "node:assert/strict";
import * as S from "../app/core/sim.js";
const { abs, add, C } = S._c;
const dB = x => 20 * Math.log10(x);
const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} is not within ${tol} of ${b}`);
const sumDb = (f, points) => dB(abs(S.wayResponses(f, points).reduce(add, C(0, 0))));
const wayDb = (f, points, i) => dB(abs(S.wayResponses(f, points)[i]));
const sweep = [20, 50, 100, 200, 500, 1000, 1999, 2000, 2001, 4000, 8000, 20000];

test("LR4 two-way sums flat and each side is -6.02 dB at the crossover", () => {
  const p = [{ fc: 2000, type: "LR4" }];
  for (const f of sweep) near(sumDb(f, p), 0, 1e-9, `sum at ${f} Hz`);
  near(wayDb(2000, p, 0), -6.0206, 1e-3, "low-pass at fc");
  near(wayDb(2000, p, 1), -6.0206, 1e-3, "high-pass at fc");
  near(wayDb(1000, p, 1), -24.4, 0.5, "high-pass one octave below fc (24 dB per octave slope region)");
});

test("LR2 sums flat with the upper way reversed, and notches when it is not", () => {
  const p = [{ fc: 1000, type: "LR2" }];
  for (const f of sweep) near(sumDb(f, p), 0, 1e-9, `sum at ${f} Hz`);
  near(wayDb(1000, p, 0), -6.0206, 1e-3, "low-pass at fc");
  // same polarity would cancel at fc: check the maths behind the invert flag
  const hs = S.wayResponses(1000, p);
  const samePolarity = add(hs[0], C(-hs[1].re, -hs[1].im));
  assert.ok(dB(abs(samePolarity)) < -100, "LR2 without reversed polarity cancels at fc");
});

test("LR8 sums flat and is -6.02 dB at fc", () => {
  const p = [{ fc: 300, type: "LR8" }];
  for (const f of sweep) near(sumDb(f, p), 0, 1e-9, `sum at ${f} Hz`);
  near(wayDb(300, p, 0), -6.0206, 1e-3, "low-pass at fc");
});

test("Butterworth sides are -3.01 dB at fc; BW1 and BW3 sum flat in magnitude", () => {
  for (const type of ["BW1", "BW2", "BW3", "BW4"]) {
    const p = [{ fc: 1000, type }];
    near(wayDb(1000, p, 0), -3.0103, 1e-3, `${type} low-pass at fc`);
    near(wayDb(1000, p, 1), -3.0103, 1e-3, `${type} high-pass at fc`);
  }
  for (const type of ["BW1", "BW3"]) for (const f of sweep) near(sumDb(f, [{ fc: 1000, type }]), 0, 1e-9, `${type} sum at ${f} Hz`);
  // BW2 with reversed upper way: +3 dB peak at fc, as expected for this alignment
  near(sumDb(1000, [{ fc: 1000, type: "BW2" }]), 3.0103, 1e-3, "BW2 sum at fc");
});

test("multi-way: aligned ways sum flat; plain filters dip between close crossovers", () => {
  const three = [{ fc: 300, type: "LR4" }, { fc: 3000, type: "LR4" }];
  const four = [{ fc: 100, type: "LR2" }, { fc: 800, type: "LR4" }, { fc: 5000, type: "LR8" }];
  const close = [{ fc: 500, type: "LR4" }, { fc: 1000, type: "LR4" }];
  const odd = [{ fc: 200, type: "BW3" }, { fc: 2000, type: "BW1" }];
  const sumA = (f, p) => dB(abs(S.wayResponses(f, p, true).reduce(add, C(0, 0))));
  for (const f of S.logGrid(10, 40000, 24)) {
    for (const [name, p] of Object.entries({ three, four, close, odd })) near(sumA(f, p), 0, 1e-9, `aligned ${name} at ${f.toFixed(1)} Hz`);
    near(sumDb(f, three), 0, 0.15, `plain 3-way, crossovers a decade apart, at ${f.toFixed(0)} Hz`);
  }
  near(sumDb(Math.sqrt(500 * 1000), close), -7.96, 0.05, "plain 3-way LR4 at 500 and 1000 Hz dips about 8 dB between them");
  // in both modes each way keeps its own level: -6.02 dB at its crossovers
  near(dB(abs(S.wayResponses(300, three, true)[0])), -6.0206, 1e-3, "aligned low way at fc1");
  near(dB(abs(S.wayResponses(3000, three, true)[2])), -6.0206, 0.01, "aligned top way at fc2");
});

test("logGrid gives the requested points per octave", () => {
  const g = S.logGrid(20, 20000, 24);
  assert.equal(g[0], 20);
  near(g[24], 40, 1e-9, "one octave up");
  assert.equal(g.length, Math.floor(Math.log2(1000) * 24) + 1);
});

test("interpLog is linear in dB on a log-frequency axis and returns null outside the data", () => {
  const pts = [{ x: 100, y: -40 }, { x: 1000, y: -60 }, { x: 2000, y: null }, { x: 4000, y: -50 }];
  near(S.interpLog(pts, Math.sqrt(100 * 1000)), -50, 1e-9, "geometric midpoint");
  assert.equal(S.interpLog(pts, 100), -40);
  assert.equal(S.interpLog(pts, 50), null);
  assert.equal(S.interpLog(pts, 5000), null);
  assert.equal(S.interpLog(pts, 1500), null, "next to a missing point");
});

test("slopeFromSweep recovers a straight line and slopeCurve holds the ends", () => {
  const pts = [80, 84, 88, 92, 96, 100, 104].map(x => ({ x, y: -70 + 0.66 * (x - 80) }));
  near(S.slopeFromSweep(pts, 84, 100), 0.66, 1e-9, "fitted slope");
  assert.equal(S.slopeFromSweep(pts.slice(0, 2), 0, 200), null, "too few points");
  const sc = S.slopeCurve([{ f: 125, slope: 1.2 }, { f: 1000, slope: 0.6 }]);
  assert.equal(sc(50), 1.2);
  assert.equal(sc(5000), 0.6);
  near(sc(Math.sqrt(125 * 1000)), 0.9, 1e-9, "log midpoint");
});

// Two identical drivers at -60 dB for every harmonic, measured at the target level.
function flatDriver(name, level) {
  const curve = [{ x: 10, y: -60 }, { x: 30000, y: -60 }];
  return { name, L0: level, hd: { H2: curve, H3: curve }, slope: () => 0 };
}

test("simulate: identical drivers with no level dependence give the driver's own distortion away from fc", () => {
  const freqs = [100, 200, 20000];
  const r = S.simulate({ freqs, target: 94, orders: ["H2", "H3"], points: [{ fc: 2000, type: "LR4" }],
    ways: [flatDriver("low", 94), flatDriver("high", 94)] });
  near(r.system.H2[0], -60, 0.01, "H2 at 100 Hz");
  near(r.system.H3[2], -60, 0.01, "H3 at 20 kHz");
  near(r.system.THD[0], -60 + 10 * Math.log10(2), 0.01, "THD is the power sum of H2 and H3");
  assert.deepEqual(r.gaps, []);
});

test("simulate: at an LR4 crossover two uncorrelated -60 dB drivers give -63 dB", () => {
  const r = S.simulate({ freqs: [2000], target: 94, orders: ["H2"], points: [{ fc: 2000, type: "LR4" }],
    ways: [flatDriver("low", 94), flatDriver("high", 94)] });
  // each way plays 6.02 dB down (-66.02 dB SPL relative), powers add (+3.01), summed fundamental is 0 dB
  near(r.system.H2[0], -60 - 6.0206 + 3.0103, 0.01, "H2 at fc");
  near(r.contrib[0].H2[0], -66.02, 0.01, "one driver's share");
});

test("simulate: level law moves the distortion with the level each driver plays at", () => {
  const w = flatDriver("low", 94);
  w.slope = k => (k === "H2" ? 1 : 0.7);
  const r = S.simulate({ freqs: [100], target: 104, orders: ["H2", "H3"], points: [{ fc: 2000, type: "LR4" }],
    ways: [w, flatDriver("high", 94)] });
  near(r.system.H2[0], -50, 0.01, "H2 up 10 dB for +10 dB level");
  near(r.system.H3[0], -53, 0.01, "H3 up 7 dB for +10 dB level");
});

test("simulate: two identical drivers in a way each play 6 dB lower", () => {
  const w = flatDriver("low", 94);
  w.slope = k => (k === "H2" ? 1 : 0.7);
  w.count = 2;
  const r = S.simulate({ freqs: [100], target: 94, orders: ["H2", "H3"], points: [{ fc: 2000, type: "LR4" }],
    ways: [w, flatDriver("high", 94)] });
  near(r.system.H2[0], -60 - 6.0206, 0.01, "H2 falls 6 dB with slope 1");
  near(r.system.H3[0], -60 - 0.7 * 6.0206, 0.01, "H3 falls 4.2 dB with slope 0.7");
});

test("simulate: a missing curve where a driver matters leaves a gap; far outside its band it is ignored", () => {
  const low = flatDriver("low", 94);
  const high = { name: "high", L0: 94, hd: { H2: [{ x: 1000, y: -55 }, { x: 20000, y: -55 }] }, slope: () => 0 };
  const r = S.simulate({ freqs: [50, 1500, 5000], target: 94, orders: ["H2", "H3"], points: [{ fc: 2000, type: "LR4" }],
    ways: [low, high] });
  assert.notEqual(r.system.H2[0], null, "at 50 Hz the tweeter is > 40 dB down and ignored");
  assert.equal(r.system.H3[1], null, "at 1.5 kHz the high way matters and has no H3");
  assert.equal(r.system.THD[1], null, "THD needs every order");
  near(r.system.H2[2], -55, 0.3, "H2 at 5 kHz comes from the high way");
  assert.ok(r.gaps.some(g => g.way === 1 && g.order === "H3"), "gap reported for the high way's H3");
});

test("dbToPct converts dB re fundamental to percent", () => {
  near(S.dbToPct(-40), 1, 1e-12, "-40 dB");
  near(S.dbToPct(-60), 0.1, 1e-12, "-60 dB");
  assert.equal(S.dbToPct(null), null);
});

test("simulate: several measured levels are interpolated at the level the driver plays at", () => {
  const at = y => [{ x: 10, y }, { x: 30000, y }];
  const way = { name: "two levels", curves: [{ L0: 90, hd: { H2: at(-60) } }, { L0: 100, hd: { H2: at(-50) } }], slope: () => 1 };
  near(S.harmonicAt(way, "H2", 1000, 95), -55, 1e-9, "halfway between 90 and 100 dB");
  near(S.harmonicAt(way, "H2", 1000, 90), -60, 1e-9, "at the lower level");
  near(S.harmonicAt(way, "H2", 1000, 104), -46, 1e-9, "above the highest level: slope 1 from 100 dB");
  near(S.harmonicAt(way, "H2", 1000, 85), -65, 1e-9, "below the lowest level: slope 1 from 90 dB");
  assert.equal(S.harmonicAt(way, "H3", 1000, 95), null, "no curve for H3");
  // a level that covers only part of the band: outside it the other level is used alone
  const part = { name: "part", curves: [{ L0: 90, hd: { H2: at(-60) } }, { L0: 100, hd: { H2: [{ x: 100, y: -50 }, { x: 500, y: -50 }] } }], slope: () => 1 };
  near(S.harmonicAt(part, "H2", 2000, 95), -55, 1e-9, "only the 90 dB curve has 2 kHz: moved up 5 dB");
  const r = S.simulate({ freqs: [100], target: 95, orders: ["H2"], points: [{ fc: 2000, type: "LR4" }], ways: [way, flatDriver("high", 95)] });
  near(r.system.H2[0], -55, 0.01, "speaker H2 from the interpolated level");
});
