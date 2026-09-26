/* common.js: helpers shared by the export formats.
 *
 * Every exporter receives "curves": [{ label, driver: {id, name}, source, sourceText, kind, kindLabel,
 *   quantity, level, conditions, xLabel, xUnit, yLabel, yUnit, category (true when x are row labels),
 *   points: [{x, y}], set }] and returns files: [{ name, text }]. */

import { store } from "../core/data.js";

export const today = () => new Date().toISOString().slice(0, 10);

export function safeName(...parts) {
  return parts.filter(p => p != null && p !== "").join("_").normalize("NFKD").replace(/[^\w.+-]+/g, "-")
    .replace(/-+/g, "-").replace(/^-|-$/g, "").slice(0, 120);
}

/** File names made unique within one ZIP: a repeated name gets _2, _3 before its extension. */
export function uniqueNames(files) {
  const seen = new Map();
  return files.map(f => {
    const n = seen.get(f.name) || 0;
    seen.set(f.name, n + 1);
    return n ? Object.assign({}, f, { name: f.name.replace(/(\.[^.]+)?$/, m => `_${n + 1}${m}`) }) : f;
  });
}

/** Up to 4 decimals, no trailing zeros, "." as decimal mark. */
export function fmt(v) {
  if (v == null || !isFinite(v)) return "";
  return String(Math.round(v * 10000) / 10000);
}

export const numericX = c => !c.category && c.points.length && c.points.every(p => typeof p.x === "number");
export const isFrequencyAxis = c => numericX(c) && /hz/i.test(c.xUnit || "");
/** A continuous curve against frequency (not bars of intermodulation products, not table rows). */
export const isFrequencyCurve = c => isFrequencyAxis(c) && ((store.kindById[c.kind] || {}).view || "curve") === "curve";

export function describeCurve(c) {
  const bits = [c.driver && c.driver.name, c.quantity, c.tag || (c.level != null ? `${c.level} dB` : null)].filter(Boolean);
  return bits.join(" · ");
}

export function curveFileName(c, ext) {
  return safeName(c.driver && c.driver.id, c.kind, c.quantity, c.tag || (c.level != null ? `${c.level}dB` : null), c.source) + "." + ext;
}
