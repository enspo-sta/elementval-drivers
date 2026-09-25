/* zma.js: ZMA impedance files (frequency, ohm, phase) for crossover programs. Only impedance curves;
 * the phase column is 0 when the database has no phase. One file per curve. */
import { registerExporter } from "../core/registry.js";
import { curveFileName, describeCurve, fmt, isFrequencyAxis, today } from "./common.js";

registerExporter({
  id: "zma", label: "ZMA (impedance, for crossover programs)", ext: "zma", mime: "text/plain", order: 40,
  accepts: c => isFrequencyAxis(c) && c.kind === "impedance",
  files: curves => curves.filter(c => isFrequencyAxis(c) && c.kind === "impedance").map(c => ({
    name: curveFileName(c, "zma"),
    text: [`* ${describeCurve(c)}`, `* source: ${c.source}; exported ${today()}`, "* Freq(Hz)  Z(ohm)  Phase(deg)",
           ...c.points.map(p => `${fmt(p.x)}\t${fmt(p.y)}\t${fmt(p.phase ?? 0)}`)].join("\n") + "\n",
  })),
});
