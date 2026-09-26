/* curves.js: turns stored measurement sets into the plain curves the exporters write
 * (see app/exporters/common.js for the fields). */
import { familyOf, kindOf, levelOf, levelUnit, yAxisOf } from "./data.js";
import { quantitiesOf } from "./compare.js";

/** Curves of one set: one per quantity (series), or only the quantity ids given. Tables become one
 *  curve per numeric column with the row labels as x. Bars give the products. */
export function curvesOfSet(driver, set, { only = null, quantities = null, labelPrefix = "" } = {}) {
  const kind = kindOf(set), fam = familyOf(set);
  const qs = (quantities || quantitiesOf(set, kind)).filter(q => !only || only.includes(q.id));
  const level = levelOf(set);
  // what tells this set from the others of its kind: its level with the unit, else its drive voltage, else what
  // its type says in brackets (an impedance read from a chart to 70 ohm and from one to 15 ohm)
  const c0 = set.conditions || {};
  const bracket = (String(set.type || "").match(/\(([^)]*)\)\s*$/) || [])[1];
  const near = typeof c0.distance_mm === "number" && c0.distance_mm < 100 ? `near field ${c0.distance_mm} mm` : null;
  const tag = [level != null ? `${level} ${levelUnit(set)}` : c0.drive_v != null ? `${[].concat(c0.drive_v).join(" and ")} V` : bracket || null, near].filter(Boolean).join(" · ") || null;
  const ya = yAxisOf(set, kind);
  const base = {
    driver, source: fam ? fam.name : "unknown source", sourceText: set.source || "", kind: kind.id, kindLabel: kind.label,
    level, tag, conditions: set.conditions || {}, set,
    xLabel: (kind.x && kind.x.label) || ((set.axes || {}).x || {}).label || (set.columns || [""])[0] || "x",
    xUnit: (kind.x && kind.x.unit) || ((set.axes || {}).x || {}).unit || "",
    yLabel: ya.label || "",
    yUnit: ya.unit || "",
  };
  const out = [];
  for (const q of qs) {
    const label = `${labelPrefix || driver.name}${q.label && q.id !== "products" ? " · " + q.label : ""}${tag ? " · " + tag : ""}`;
    if (q.points) {
      out.push(Object.assign({}, base, { label, quantity: q.id, points: q.points.map(p => ({ x: p.x, y: p.y })),
        yUnit: q.relTo ? q.relTo.replace(/^dB /, "dB, ") : base.yUnit, xLabel: kind.view === "bars" ? ((kind.x && kind.x.label) || "Product frequency") : base.xLabel }));
    } else if (q.rows) {
      out.push(Object.assign({}, base, { label, quantity: q.id, category: true, yUnit: "", yLabel: q.id,
        points: q.rows.map(r => ({ x: r.label, y: r.value })) }));
    } else if (q.value != null) {
      out.push(Object.assign({}, base, { label, quantity: q.id, category: true, yUnit: q.relTo || "", yLabel: q.label, xLabel: "Quantity", xUnit: "",
        points: [{ x: q.label, y: q.value }] }));
    }
  }
  return out;
}

/** Every curve of a driver, optionally from one source family only. */
export function curvesOfDriver(driver, familyName = null) {
  return (driver.measurements || []).filter(s => !familyName || (familyOf(s) || {}).name === familyName)
    .flatMap(s => curvesOfSet(driver, s));
}
