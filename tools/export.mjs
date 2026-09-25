#!/usr/bin/env node
/* export.mjs: export curves from the database to files for other programs, without the browser.
 * Uses the same export formats as the viewer (app/exporters).
 *
 *   node tools/export.mjs --format csv                         every driver, one CSV per measurement
 *   node tools/export.mjs --driver ptt525x04naa05 --format rew,csv
 *   node tools/export.mjs --source HiFiCompass --format frd --out exports
 *   node tools/export.mjs --list-formats
 *   node tools/export.mjs --help
 *
 * Files go to ./exports (or --out). Needs only Node.js. */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { setData, allDrivers, familyOf, kindOf } from "../app/core/data.js";
import { getExporters } from "../app/core/registry.js";
import { curvesOfSet } from "../app/core/curves.js";
import MODULES from "../app/modules.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = f => { try { return JSON.parse(readFileSync(join(root, f), "utf8")); } catch (e) { return null; } };
const args = Object.fromEntries(process.argv.slice(2).map((a, i, all) => a.startsWith("--") ? [a.slice(2), all[i + 1] && !all[i + 1].startsWith("--") ? all[i + 1] : true] : null).filter(Boolean));

setData({ db: read("drivers.json"), survey: read("drivers_survey_midbass.json"), config: read("watch/config.json"), kinds: read("schema/kinds.json") });
for (const m of MODULES.filter(m => m.includes("/exporters/"))) await import(new URL("../app/" + m.replace(/^\.\//, ""), import.meta.url));

if (args.help) {
  console.log(`Export curves from the database for other programs.

  node tools/export.mjs [--driver <id>] [--source <source name>] [--format csv,rew,...] [--out <folder>]
  node tools/export.mjs --list-formats

  --driver   one driver (its id, as in the viewer's address #driver/<id>); default every driver
  --source   one source, for example HiFiCompass or "Manufacturer datasheet"
  --format   one or more formats, comma separated (default csv); see --list-formats
  --out      folder for the files (default ./exports)`);
  process.exit(0);
}
if (args["list-formats"]) {
  for (const e of getExporters()) console.log(`${e.id.padEnd(8)} ${e.label}`);
  process.exit(0);
}
const formats = String(args.format || "csv").split(",");
const unknown = formats.filter(f => !getExporters().some(e => e.id === f));
if (unknown.length) { console.error(`unknown format ${unknown.join(", ")}; see --list-formats`); process.exit(1); }
const out = resolve(process.cwd(), String(args.out || "exports"));   // an absolute --out is used as it is
mkdirSync(out, { recursive: true });

let n = 0;
for (const d of allDrivers()) {
  if (args.driver && d.id !== args.driver) continue;
  (d.measurements || []).forEach((set, i) => {
    const fam = familyOf(set);
    if (args.source && (!fam || fam.name !== args.source)) return;
    const curves = curvesOfSet(d, set);
    for (const id of formats) {
      const e = getExporters().find(x => x.id === id);
      const ok = curves.filter(c => e.accepts(c) && (!kindOf(set).export || kindOf(set).export.includes(e.id.split("-")[0])));   // the kind's own format list
      if (!ok.length) continue;
      for (const f of e.files(ok, { title: `${d.id}_${kindOf(set).id}_${i}` })) {
        writeFileSync(join(out, f.name), f.text);
        n++;
      }
    }
  });
}
console.log(`${n} file(s) written to ${out}`);
