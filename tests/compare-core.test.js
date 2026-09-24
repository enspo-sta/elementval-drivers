// Tests for compare-core.js (which measurement sets may share a chart). Run: node --test tests/*.test.js
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const CC = require("../compare-core.js");
const db = require("../drivers.json");
const survey = require("../drivers_survey_midbass.json");
const cfg = require("../watch/config.json");
const drivers = db.drivers.concat(survey.drivers);
const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} is not within ${tol} of ${b}`);

test("five distinct colours, markers and line styles", () => {
  assert.equal(CC.MAX_PICK, 5);
  assert.equal(new Set(CC.COLORS.map(c => c.toLowerCase())).size, 5);
  assert.equal(new Set(CC.MARKERS).size, 5);
  assert.equal(new Set(CC.DASHES.map(String)).size, 5);
});

test("every source family carries a reliability rank; Purifi's datasheets rank first, HiFiCompass second", () => {
  for (const f of cfg.families) {
    assert.equal(typeof f.rank, "number", `${f.name} has a rank`);
    assert.ok(f.reliability, `${f.name} has a reliability label`);
  }
  const rank = n => cfg.families.find(f => f.name === n).rank;
  assert.ok(rank("Manufacturer datasheet") < rank("HiFiCompass"));
  assert.ok(rank("HiFiCompass") < rank("Erin's Audio Corner"));
  assert.equal(rank("Erin's Audio Corner"), rank("audioXpress"));
  assert.equal(rank("diyAudio"), rank("Parts Express"));
  assert.equal(CC.familyOf({ source: "Parts Express product page chart" }, cfg.families).name, "Parts Express");
});

test("groups never mix sources unless asked", () => {
  const groups = CC.buildGroups(drivers, cfg.families, false);
  for (const g of groups) for (const e of g.entries) assert.equal(e.family.name, g.family, `${g.key}: ${e.driver.name}`);
  const sources = CC.sourcesOf(groups, cfg.families).map(f => f.name);
  assert.equal(sources[0], "Manufacturer datasheet");
  assert.equal(sources[1], "HiFiCompass");
  const mixed = CC.buildGroups(drivers, cfg.families, true).find(g => g.key === "hd-f|94");
  assert.deepEqual([...new Set(mixed.entries.map(e => e.family.name))], ["Manufacturer datasheet", "HiFiCompass"]);
});

test("harmonic distortion at different levels stays apart; the same level from one source is one group", () => {
  const groups = CC.buildGroups(drivers, cfg.families, false);
  const hf94 = groups.find(g => g.key === "HiFiCompass::hd-f|94");
  const hf91 = groups.find(g => g.key === "HiFiCompass::hd-f|91");
  assert.ok(hf94 && hf91);
  assert.deepEqual(hf94.quantityIds, ["H2", "H3", "H4", "H5", "THD"]);
  assert.ok(hf94.entries.every(e => e.set.conditions.spl_db === 94));
  assert.ok(hf91.entries.every(e => e.set.conditions.spl_db === 91));
});

test("harmonics stored as sound pressure become ratios (minus the test level)", () => {
  const d = db.drivers.find(x => x.id === "ptt65m08naa08");
  const set = d.measurements.find(m => m.type === "HD (orders)");
  const kind = CC.kindOf(set);
  assert.equal(kind.key, "hd-f|94");
  const q = CC.quantitiesOf(set, kind).find(x => x.id === "H2");
  near(q.points[0].y, set.series[0].points[0].y - 94, 1e-9, "first H2 point");
});

test("computed THD is the power sum of H2 to H5", () => {
  const d = db.drivers.find(x => x.id === "ptt525x04naa05");
  const set = d.measurements.find(m => /HiFiCompass/.test(m.source) && m.chartType === "line");
  const qs = CC.quantitiesOf(set, CC.kindOf(set));
  const thd = qs.find(q => q.id === "THD");
  const at = k => qs.find(q => q.id === k).points[0].y;
  const expect = 10 * Math.log10(["H2", "H3", "H4", "H5"].reduce((s, k) => s + Math.pow(10, at(k) / 10), 0));
  near(thd.points[0].y, expect, 1e-9, "THD at the first point");
  assert.ok(thd.points[0].y >= at("H2"), "THD is never below its largest part");
});

test("intermodulation bars: products relative to the upper tone, tones left out, sum as power", () => {
  const d = db.drivers.find(x => x.id === "ptt80x04nab01");
  const set = d.measurements.find(m => m.chartType === "bar" && /30 \+ 255/.test(m.method));
  const kind = CC.kindOf(set);
  assert.deepEqual(kind.tones, [30, 255]);
  const [each, sum] = CC.quantitiesOf(set, kind);
  assert.ok(!each.points.some(p => p.x === 255), "the 255 Hz tone is not a product");
  const tone = set.series[0].points.find(p => p.x === 255).y;
  near(each.points[0].y, set.series[0].points[0].y - tone, 1e-9, "first product");
  const expect = 10 * Math.log10(each.points.reduce((s, p) => s + Math.pow(10, p.y / 10), 0));
  near(sum.value, expect, 1e-9, "sum of products");
});

test("survey intermodulation (already relative) keeps its values and splits by level", () => {
  const groups = CC.buildGroups(drivers, cfg.families, false).filter(g => g.family === "diyAudio");
  assert.ok(groups.length >= 2);
  const g70 = groups.find(g => g.key === "diyAudio::imd-bars|40+96|70|ref");
  const e = g70.entries[0];
  assert.deepEqual(e.quantities[0].points.map(p => p.y), e.set.series[0].points.map(p => p.y));
});

test("tables: numeric columns only, rows keep their labels", () => {
  const g = CC.buildGroups(drivers, cfg.families, false).find(x => x.key === "HiFiCompass::table|94 dB band metrics");
  assert.deepEqual(g.quantityIds, ["THD %", "Gw dB"]);
  const q = g.entries[0].quantities[0];
  assert.equal(typeof q.rows[0].label, "string");
  assert.equal(typeof q.rows[0].value, "number");
});
