// Tests for app/core/compare.js and app/core/data.js on the real database. Run: node --test tests/
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { setData, store, allDrivers, kindOf, levelOf } from "../app/core/data.js";
import * as CC from "../app/core/compare.js";

const read = f => JSON.parse(readFileSync(new URL("../" + f, import.meta.url)));
const db = read("drivers.json"), survey = read("drivers_survey_midbass.json"), config = read("watch/config.json"), kinds = read("schema/kinds.json");
setData({ db, survey, config, kinds });
const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} is not within ${tol} of ${b}`);

test("five distinct colours, markers and line styles", () => {
  assert.equal(CC.MAX_PICK, 5);
  assert.equal(new Set(CC.COLORS.map(c => c.toLowerCase())).size, 5);
  assert.equal(new Set(CC.MARKERS).size, 5);
  assert.equal(new Set(CC.DASHES.map(String)).size, 5);
});

test("every stored set names a known kind, and level kinds state their level", () => {
  const ids = new Set(kinds.kinds.map(k => k.id));
  for (const d of allDrivers()) for (const m of d.measurements) {
    assert.ok(ids.has(m.kind), `${d.id} ${m.type}: kind ${m.kind}`);
    if (["spl", "spl-near", "stated"].includes(kindOf(m).level)) assert.equal(typeof levelOf(m), "number", `${d.id} ${m.type}: level`);
  }
});

test("sources are ranked; Purifi's datasheets first, HiFiCompass second", () => {
  const rank = n => config.families.find(f => f.name === n).rank;
  for (const f of config.families) { assert.equal(typeof f.rank, "number"); assert.ok(f.reliability); }
  assert.ok(rank("Manufacturer datasheet") < rank("HiFiCompass"));
  assert.ok(rank("HiFiCompass") < rank("Erin's Audio Corner"));
  assert.equal(rank("Erin's Audio Corner"), rank("audioXpress"));
  assert.equal(rank("diyAudio"), rank("Parts Express"));
  const srcs = CC.sourcesOf(CC.buildGroups(), store.families).map(f => f.name);
  assert.deepEqual(srcs.slice(0, 2), ["Manufacturer datasheet", "HiFiCompass"]);
});

test("groups never mix sources unless asked", () => {
  for (const g of CC.buildGroups()) for (const e of g.entries) assert.equal(e.family.name, g.family, `${g.key}: ${e.driver.name}`);
  const mixed = CC.buildGroups({ mix: true }).find(g => g.key === "hd-frequency");
  assert.deepEqual([...new Set(mixed.entries.map(e => e.family.name))].sort(), ["Derived (model or calculation)", "HiFiCompass", "Manufacturer datasheet"]);
});

test("levels are not a reason to split a chart: every HiFiCompass harmonic level shares one group", () => {
  const g = CC.buildGroups().find(x => x.key === "HiFiCompass::hd-frequency");
  assert.deepEqual(g.levels, [...new Set(g.levels)].sort((a, b) => a - b), "levels are unique and ascending");
  assert.ok(g.levels.length >= 50, "the drivers read from charts bring their own levels");
  for (const k of ["H2", "H3", "H5"]) assert.ok(g.quantityIds.includes(k), k);
  // a driver's entry holds every level it was measured at (superseded hand captures left out)
  const ptt8 = g.entries.find(e => e.driver.id === "purifi-ptt8-0x04-nab-02");
  const stored = db.drivers.find(d => d.id === "purifi-ptt8-0x04-nab-02").measurements
    .filter(m => m.kind === "hd-frequency" && !m.superseded_by && /HiFiCompass/.test(m.source) && !(m.conditions.distance_mm < 100))
    .map(m => m.conditions.spl_db).sort((a, b) => a - b);
  assert.deepEqual(ptt8.sets.map(s => s.level), stored);
  assert.ok(!ptt8.sets.some(s => s.set.superseded_by), "superseded sets are not compared");
  const nf = CC.buildGroups().find(x => x.key === "HiFiCompass::hd-frequency|near field");
  assert.ok(nf && nf.entries.some(e => e.driver.id === "purifi-ptt8-0x04-nab-02"), "near-field harmonics are a measurement of their own");
  // the default level is the one most drivers were measured at
  const count = L => g.entries.filter(e => e.sets.some(s => s.level === L)).length;
  assert.equal(count(CC.defaultLevel(g)), Math.max(...g.levels.map(count)));
});

test("pickSet uses the level closest to the target", () => {
  const g = CC.buildGroups().find(x => x.key === "HiFiCompass::hd-frequency");
  const ptt8 = g.entries.find(e => e.driver.id === "purifi-ptt8-0x04-nab-02");
  const L = ptt8.sets.map(s => s.level);
  assert.ok(L.length >= 4);
  assert.equal(CC.pickSet(ptt8, L[1]).level, L[1], "a measured level is used as it is");
  assert.equal(CC.pickSet(ptt8, L[1]).delta, 0);
  const between = L[1] + 0.3 * (L[2] - L[1]);
  assert.equal(CC.pickSet(ptt8, between).level, L[1], "between two levels: the closer one");
  near(CC.pickSet(ptt8, between).delta, L[1] - between, 1e-9, "delta = level used minus target");
  assert.equal(CC.pickSet(ptt8, L[L.length - 1] + 20).level, L[L.length - 1], "above every level: the highest");
  const survey = CC.buildGroups().find(x => x.key === "diyAudio::imd-spectrum|40+96");
  assert.deepEqual(survey.levels, [70, 80, 85, 90]);
});

test("the level rule moves harmonic curves and rebuilds THD", () => {
  const g = CC.buildGroups().find(x => x.key === "HiFiCompass::hd-frequency");
  const e = g.entries.find(x => x.driver.id === "ptt525x04naa05");   // a set with H2 to H5 (THD can be built)
  const s = CC.pickSet(e, 94);
  const moved = CC.shiftQuantities(s.quantities, s.level, s.level + 3);
  const at = (qs, id) => qs.find(q => q.id === id).points[0].y;
  near(at(moved, "H2") - at(s.quantities, "H2"), 3, 1e-9, "H2 +1.0 dB per dB");
  near(at(moved, "H3") - at(s.quantities, "H3"), 2.1, 1e-9, "H3 +0.7 dB per dB");
  const thd = 10 * Math.log10(["H2", "H3", "H4", "H5"].reduce((t, k) => t + Math.pow(10, at(moved, k) / 10), 0));
  near(at(moved, "THD"), thd, 1e-9, "THD from the moved orders");
});

test("harmonics stored as sound pressure become ratios (minus the test level)", () => {
  const set = db.drivers.find(x => x.id === "ptt65m08naa08").measurements.find(m => m.type === "HD (orders)");
  const q = CC.quantitiesOf(set).find(x => x.id === "H2");
  near(q.points[0].y, set.series[0].points[0].y - 94, 1e-9, "first H2 point");
});

test("intermodulation bars: products relative to the upper tone, tones left out, sum as power", () => {
  const set = db.drivers.find(x => x.id === "ptt80x04nab01").measurements.find(m => m.chartType === "bar" && /30 \+ 255/.test(m.method));
  const [each, sum] = CC.quantitiesOf(set);
  assert.ok(!each.points.some(p => p.x === 255));
  const tone = set.series[0].points.find(p => p.x === 255).y;
  near(each.points[0].y, set.series[0].points[0].y - tone, 1e-9, "first product");
  near(sum.value, 10 * Math.log10(each.points.reduce((t, p) => t + Math.pow(10, p.y / 10), 0)), 1e-9, "sum");
});

test("the calculated two-driver curve is filed as Derived, not HiFiCompass", () => {
  const g = CC.buildGroups().find(x => x.key === "HiFiCompass::hd-frequency");
  assert.ok(!g.entries.some(e => e.driver.id === "sb-sb34nrxl75-8-dual"));
  assert.ok(CC.buildGroups().find(x => x.key === "Derived (model or calculation)::hd-frequency").entries.some(e => e.driver.id === "sb-sb34nrxl75-8-dual"));
});

import { nearLevels } from "../app/core/compare.js";
test("nearLevels: levels within 1 dB share one button, given as their mean", () => {
  assert.deepEqual(nearLevels([91.67, 91.1, 91.15, 94]), [91.3, 94]);
  assert.deepEqual(nearLevels([80, 85, 90]), [80, 85, 90]);
  assert.deepEqual(nearLevels([]), []);
});
