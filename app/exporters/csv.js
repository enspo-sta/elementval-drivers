/* csv.js: comma-separated table, one column per curve, for spreadsheets and most programs.
 * A second variant uses semicolons and decimal commas, which Excel expects with Swedish settings. */
import { registerExporter } from "../core/registry.js";
import { fmt, safeName, today } from "./common.js";
import { store } from "../core/data.js";

function table(curves, { title = "export", sep = ",", decimal = "." } = {}) {
  const cell = v => {
    let s = typeof v === "number" ? fmt(v) : String(v == null ? "" : v);
    if (typeof v === "number" && decimal !== ".") s = s.replace(".", decimal);
    return /[",;\n]/.test(s) || (sep === "," && s.includes(",")) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const first = curves[0] || {};
  const xs = [];
  const seen = new Set();
  curves.forEach(c => c.points.forEach(p => { const k = String(p.x); if (!seen.has(k)) { seen.add(k); xs.push(p.x); } }));
  if (curves.every(c => !c.category)) xs.sort((a, b) => a - b);
  const lookup = curves.map(c => new Map(c.points.map(p => [String(p.x), p.y])));
  const lines = [
    [cell(`${first.xLabel || "x"}${first.xUnit ? " (" + first.xUnit + ")" : ""}`), ...curves.map(c => cell(`${c.label}${c.yUnit ? " (" + c.yUnit + ")" : ""}`))].join(sep),
    ...xs.map(x => [cell(x), ...lookup.map(m => cell(m.has(String(x)) ? m.get(String(x)) : ""))].join(sep)),
  ];
  const notes = [`# ${title}`, `# exported ${today()} from the driver database viewer`,
    ...curves.map(c => `# ${c.label}: ${c.source}${c.sourceText ? " (" + c.sourceText.replace(/\s+/g, " ").slice(0, 160) + ")" : ""}`)];
  return notes.join("\n") + "\n" + lines.join("\n") + "\n";
}

// Curves that can share one table: same kind, and the same kind of first column (frequency or row
// labels); tables of different types each get their own file. Several files are zipped by the viewer.
function files(curves, opts, suffix) {
  const groups = new Map();
  for (const c of curves) {
    // a table's rows: one file per table type; a computed value (the sum of all products) at several levels: one file
    const tableType = (store.kindById[c.kind] || {}).view === "table" ? (c.set && c.set.type) || "" : c.quantity || "";
    const key = [c.kind, c.category ? "rows" : "x", c.category ? tableType : ""].join("|");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(c);
  }
  const title = opts.title || "export";
  return [...groups.values()].map((g, i, all) => ({
    name: safeName(title, all.length > 1 ? g[0].kind : null, all.length > 1 && g[0].category ? ((store.kindById[g[0].kind] || {}).view === "table" ? (g[0].set && g[0].set.type) : g[0].quantity) : null) + suffix + ".csv",
    text: table(g, Object.assign({}, opts, { title })),
  }));
}

registerExporter({
  id: "csv", label: "CSV (spreadsheet, comma separated)", ext: "csv", mime: "text/csv", order: 10,
  accepts: () => true,
  files: (curves, opts = {}) => files(curves, opts, ""),
});

registerExporter({
  id: "csv-se", label: "CSV for Excel with Swedish settings (semicolon, decimal comma)", ext: "csv", mime: "text/csv", order: 11,
  accepts: () => true,
  files: (curves, opts = {}) => files(curves, Object.assign({}, opts, { sep: ";", decimal: "," }), "_se"),
});

export { table as csvTable };
