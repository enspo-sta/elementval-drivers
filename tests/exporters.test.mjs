// Tests for the export formats and the ZIP writer. Run: node --test tests/
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { setData, driverById } from "../app/core/data.js";
import { getExporters } from "../app/core/registry.js";
import { curvesOfSet, curvesOfDriver } from "../app/core/curves.js";
import { makeZip, crc32 } from "../app/core/zip.js";
import "../app/exporters/csv.js";
import "../app/exporters/rew.js";
import "../app/exporters/frd.js";
import "../app/exporters/zma.js";
import "../app/exporters/json.js";

const read = f => JSON.parse(readFileSync(new URL("../" + f, import.meta.url)));
setData({ db: read("drivers.json"), survey: read("drivers_survey_midbass.json"), config: read("watch/config.json"), kinds: read("schema/kinds.json") });
const exp = id => getExporters().find(e => e.id === id);
const hd = () => { const d = driverById("ptt525x04naa05"); return curvesOfSet(d, d.measurements.find(m => m.kind === "hd-frequency" && /HiFiCompass/.test(m.source))); };

test("all five formats are registered", () => {
  assert.deepEqual(getExporters().map(e => e.id), ["csv", "csv-se", "rew", "frd", "zma", "json"]);
});

test("CSV: one frequency column and one column per curve, values unchanged", () => {
  const curves = hd();
  const [f] = exp("csv").files(curves, { title: "t" });
  const rows = f.text.split("\n").filter(l => l && !l.startsWith("#"));
  assert.equal(rows[0].split(",").length, 1 + curves.length);
  assert.match(rows[0], /^Frequency \(Hz\),/);
  const first = rows[1].split(",").map(Number);
  assert.equal(first[0], curves[0].points[0].x);
  assert.equal(first[1], curves[0].points[0].y);
  assert.equal(rows.length - 1, new Set(curves.flatMap(c => c.points.map(p => p.x))).size);
});

test("CSV for Swedish Excel: semicolons and decimal commas", () => {
  const [f] = exp("csv-se").files(hd(), { title: "t" });
  const row = f.text.split("\n").filter(l => l && !l.startsWith("#"))[1];
  assert.ok(row.includes(";"));
  assert.ok(/\d,\d/.test(row), "decimal comma");
  assert.ok(!/\d\.\d/.test(row), "no decimal point");
});

test("REW text: one file per curve, two numeric columns", () => {
  const curves = hd();
  const files = exp("rew").files(curves);
  assert.equal(files.length, curves.length);
  const data = files[0].text.split("\n").filter(l => l && !l.startsWith("*"));
  assert.equal(data.length, curves[0].points.length);
  assert.ok(data.every(l => l.split("\t").length === 2 && l.split("\t").every(v => isFinite(Number(v)))));
});

test("FRD only takes sound pressure curves; ZMA only impedance", () => {
  const d = driverById("ptt80x04nab01");
  const all = curvesOfDriver(d);
  assert.ok(!exp("frd").accepts(all.find(c => c.kind === "hd-frequency")), "not harmonic ratios");
  const maxSpl = all.find(c => c.kind === "max-spl");
  assert.ok(exp("frd").accepts(maxSpl));
  const [f] = exp("frd").files([maxSpl]);
  const line = f.text.split("\n").find(l => l && !l.startsWith("*"));
  assert.equal(line.split("\t").length, 3);
  // Purifi's measured impedance file: the only curve a ZMA takes, written row for row
  const zs = all.filter(c => exp("zma").accepts(c));
  assert.ok(zs.length >= 1 && zs.every(c => c.kind === "impedance"), "only impedance curves");
  assert.ok(!exp("frd").accepts(zs[0]), "FRD does not take impedance");
  const rows = exp("zma").files([zs[0]])[0].text.split("\n").filter(l => l && !l.startsWith("*"));
  assert.equal(rows.length, zs[0].points.length);
  const z = { driver: d, source: "test", kind: "impedance", xUnit: "Hz", points: [{ x: 20, y: 7.1 }, { x: 40, y: 12.5 }] };
  assert.ok(exp("zma").accepts(z));
  assert.match(exp("zma").files([z])[0].text, /^20\t7\.1\t0$/m);
});

test("JSON keeps the stored sets complete", () => {
  const d = driverById("m74t-6");
  const [f] = exp("json").files(curvesOfDriver(d), { title: "m74t" });
  const j = JSON.parse(f.text);
  assert.equal(j.measurements.length, d.measurements.length);
  assert.deepEqual(j.measurements[0].set, d.measurements[0]);
});

test("tables and bars export with their row labels or product frequencies", () => {
  const d = driverById("purifi-ptt10-0x04-nab-02");
  const table = curvesOfSet(d, d.measurements.find(m => m.kind === "imd-summary"));
  assert.equal(table[0].points[0].x, "IMA2_rel_f30");
  const [f] = exp("csv").files(table, { title: "t" });
  assert.match(f.text, /IMD2_rel_carrier,-34/);
});

test("ZIP: valid archive that Python's zipfile can read", () => {
  const files = [{ name: "a.txt", text: "hello" }, { name: "ö/b.csv", text: "x,y\n1,2\n" }];
  const zip = makeZip(files);
  assert.equal(crc32(new TextEncoder().encode("hello")), 0x3610a686);
  assert.deepEqual([...zip.slice(0, 4)], [0x50, 0x4b, 0x03, 0x04]);
  const dir = mkdtempSync(join(tmpdir(), "zip-"));
  writeFileSync(join(dir, "t.zip"), zip);
  // python3 on Linux and macOS; on Windows python or py (python3 there is often a store placeholder that exits with 9009)
  const env = { ...process.env, PYTHONUTF8: "1", PYTHONIOENCODING: "utf-8" };
  const script = "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); assert z.testzip() is None; sys.stdout.write('|'.join(n+'='+z.read(n).decode() for n in z.namelist()))";
  let py = null;
  for (const cmd of ["python3", "python", "py"]) {
    const r = spawnSync(cmd, ["-c", script, join(dir, "t.zip")], { encoding: "utf8", env });
    if (!r.error && r.status !== 9009 && !/Python was not found/.test(r.stderr || "")) { py = r; break; }
  }
  if (!py) return;          // no Python on this machine: the signature and CRC checks above still ran
  assert.equal(py.status, 0, py.stderr);
  assert.equal(py.stdout, "a.txt=hello|ö/b.csv=x,y\n1,2\n");
});

test("CSV of a whole driver: one file per kind of table, so frequencies and row labels never share a column", () => {
  const d = driverById("purifi-ptt8-0x04-nab-02");
  const curves = curvesOfDriver(d, "HiFiCompass");
  const files = exp("csv").files(curves, { title: "ptt8" });
  const kinds = new Set(curves.map(c => c.kind));
  assert.ok(files.length >= kinds.size, files.map(f => f.name).join(", "));   // a table of its own columns gets its own file
  for (const f of files) {
    const header = f.text.split("\n").find(l => l && !l.startsWith("#"));
    const rows = f.text.split("\n").filter(l => l && !l.startsWith("#")).slice(1);
    const numericX = rows.every(r => r.split(",")[0] === "" || isFinite(Number(r.split(",")[0])));
    const frequencyFile = /^Frequency/.test(header);
    assert.equal(numericX, frequencyFile || rows.every(r => isFinite(Number(r.split(",")[0]))), `${f.name}: one kind of first column`);
  }
  const hdFile = files.find(f => f.name.includes("hd-frequency"));
  const hdHeader = hdFile.text.split("\n").find(l => l.startsWith("Frequency"));
  const series = curves.filter(c => c.kind === "hd-frequency").length;
  assert.equal(hdHeader.split(",").length, 1 + series, "one column per harmonic curve, every level");
});
