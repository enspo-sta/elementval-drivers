/* json.js: the measurement sets exactly as stored in the database, with the driver and source, for
 * other programs or for sharing a selection. One file. */
import { registerExporter } from "../core/registry.js";
import { safeName, today } from "./common.js";

registerExporter({
  id: "json", label: "JSON (the stored data, complete)", ext: "json", mime: "application/json", order: 90,
  accepts: c => !!c.set,
  files: (curves, opts = {}) => {
    const sets = [];
    for (const c of curves) {
      if (!c.set || sets.some(s => s.set === c.set)) continue;
      sets.push({ driver: { id: c.driver.id, name: c.driver.name, manufacturer: c.driver.manufacturer, ts: c.driver.ts }, source: c.source, set: c.set });
    }
    return [{ name: safeName(opts.title || "export") + ".json",
              text: JSON.stringify({ exported: today(), from: "driver database viewer", measurements: sets }, null, 2) + "\n" }];
  },
});
