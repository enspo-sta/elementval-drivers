/* frd.js: FRD files (frequency, dB, phase) for crossover programs such as VituixCAD and XSim.
 * Only for sound pressure curves. The database stores no phase, so the phase column is 0; let the
 * crossover program calculate minimum phase before summing drivers. One file per curve. */
import { registerExporter } from "../core/registry.js";
import { curveFileName, describeCurve, fmt, isFrequencyAxis, today } from "./common.js";

const SPL_KINDS = new Set(["frequency-response", "max-spl"]);

registerExporter({
  id: "frd", label: "FRD (VituixCAD, XSim; sound pressure curves)", ext: "frd", mime: "text/plain", order: 30,
  accepts: c => isFrequencyAxis(c) && SPL_KINDS.has(c.kind),
  files: curves => curves.filter(c => isFrequencyAxis(c) && SPL_KINDS.has(c.kind)).map(c => ({
    name: curveFileName(c, "frd"),
    text: [`* ${describeCurve(c)}`, `* source: ${c.source}; exported ${today()}`, "* phase not measured (0): use minimum phase in the crossover program",
           "* Freq(Hz)  SPL(dB)  Phase(deg)", ...c.points.map(p => `${fmt(p.x)}\t${fmt(p.y)}\t0`)].join("\n") + "\n",
  })),
});
