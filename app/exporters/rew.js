/* rew.js: plain two-column text (frequency, value) with '*' comment lines. REW imports it as a
 * frequency response (File > Import > Import frequency response), and most measurement and
 * crossover programs read the same layout. One file per curve. */
import { registerExporter } from "../core/registry.js";
import { curveFileName, describeCurve, fmt, isFrequencyCurve, today } from "./common.js";

registerExporter({
  id: "rew", label: "Text for REW (frequency, value; one file per curve)", ext: "txt", mime: "text/plain", order: 20,
  accepts: c => isFrequencyCurve(c),
  files: curves => curves.filter(isFrequencyCurve).map(c => ({
    name: curveFileName(c, "txt"),
    text: [`* ${describeCurve(c)}`, `* ${c.kindLabel}; source: ${c.sourceText || c.source}`, `* exported ${today()} from the driver database viewer`,
           `* Freq(Hz) ${c.yLabel || "Value"}(${c.yUnit || ""})`,
           ...c.points.map(p => `${fmt(p.x)}\t${fmt(p.y)}`)].join("\n") + "\n",
  })),
});
