#!/usr/bin/env node
/* sim_coverage.mjs: where each driver's harmonic data leaves Simulate without data.
 * For every source, every driver and every way of a 2-, 3- and 4-way speaker with the default crossovers
 * (LR4, summing flat), the band where that way plays within 40 dB of the others is compared with the
 * frequencies the driver has data for (H2 to H5 at any measured level; a stretch its source curve does not
 * show counts as missing). The default choice of drivers per speaker is checked the same way.
 * Writes watch/sim_coverage.md.     node tools/sim_coverage.mjs [--out watch/sim_coverage.md] */
import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { setData, store } from "../app/core/data.js";
import { buildGroups } from "../app/core/compare.js";
import * as SC from "../app/core/sim.js";
import { buildCandidates, autoPick, coverage, missingIn, rolePos } from "../app/core/simpick.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = f => JSON.parse(readFileSync(join(root, f), "utf8"));
const args = Object.fromEntries(process.argv.slice(2).map((a, i, all) => a.startsWith("--") ? [a.slice(2), all[i + 1]] : null).filter(Boolean));
setData({ db: read("drivers.json"), survey: read("drivers_survey_midbass.json"), config: read("watch/config.json"), kinds: read("schema/kinds.json") });

const XO = { 2: [2000], 3: [350, 3000], 4: [120, 700, 4000] };
const NAMES = { 2: ["low", "high"], 3: ["low", "mid", "high"], 4: ["low", "low mid", "high mid", "high"] };
const hz = f => (f >= 1000 ? `${+(f / 1000).toPrecision(3)} kHz` : `${Math.round(f)} Hz`);
const groups = buildGroups({ mix: false });
const sources = store.families.filter(f => buildCandidates(groups, false, f.name).length);
const lines = ["# Simulate: where the harmonic data runs out", "",
  `Written by \`tools/sim_coverage.mjs\` on ${new Date().toISOString().slice(0, 10)}. For each way of a speaker with the default crossovers ` +
  "(2-way 2 kHz; 3-way 350 Hz and 3 kHz; 4-way 120 Hz, 700 Hz and 4 kHz; Linkwitz-Riley 24 dB per octave, summing flat), the band where " +
  "that way still plays within 40 dB of the others is compared with the frequencies the driver has data for. Where they differ, Simulate " +
  "draws the speaker's curve dashed there (the other ways alone, the least the speaker can have). A driver is listed only for the ways " +
  "its role fits (within 0.35 of the way's position; tweeters at the top, woofers at the bottom). Simulate runs from the lowest way's " +
  "first point to the highest way's last, so nothing is missing below the one or above the other. A HiFiCompass tweeter's H5 ends near " +
  "8.6 kHz and its H3 near 14.5 kHz because those harmonics would lie above about 43 kHz, beyond what the measurement records.", ""];
let gapsDefault = 0, rows = 0;
for (const fam of sources) {
  const cands = buildCandidates(groups, false, fam.name);
  lines.push(`## ${fam.name}`, "", "| Driver | Data (every order) | Speaker and way | Band it plays in | Covered | Missing |", "|---|---|---|---|---|---|");
  for (const c of cands) {
    for (const n of [2, 3, 4]) {
      const bands = SC.audibleBands(XO[n].map(fc => ({ fc, type: "LR4" })), true);
      bands.forEach(([lo0, hi0], i) => {
        const pos = i / (n - 1);
        // Simulate runs from the lowest way's first point to the highest way's last: nothing is missing beyond them
        const lo = i === 0 ? Math.max(lo0, c.lo) : lo0, hi = i === n - 1 ? Math.min(hi0, c.hi) : hi0;
        if (Math.abs(rolePos(c.e.driver.role) - pos) > 0.35) return;
        const cov = coverage(c, lo, hi), miss = missingIn(c, lo, hi);
        const merged = [];
        for (const m of miss) { const x = merged.find(y => y.from === m.from && y.to === m.to); if (x) x.orders.push(m.order); else merged.push({ from: m.from, to: m.to, orders: [m.order] }); }
        rows++;
        lines.push(`| ${c.e.driver.name} | ${hz(c.lo)}–${hz(c.hi)} · ${c.orders.join(" ")} | ${n}-way, way ${i + 1} (${NAMES[n][i]}) | ${hz(lo)}–${hz(hi)} | ${Math.round(cov * 100)} % | ${merged.length ? merged.map(m => `${m.orders.join(" ")} ${hz(m.from)}–${hz(m.to)}`).join("; ") : "—"} |`);
      });
    }
  }
  lines.push("", "Default choice per speaker (what Simulate picks when it opens):", "");
  for (const n of [2, 3, 4]) {
    const pick = autoPick(n, XO[n], XO[n].map(() => "LR4"), true, cands);
    const bands = SC.audibleBands(XO[n].map(fc => ({ fc, type: "LR4" })), true);
    const parts = pick.map((id, i) => {
      const c = cands.find(x => x.id === id); if (!c) return `way ${i + 1}: none`;
      const lo = i === 0 ? Math.max(bands[i][0], c.lo) : bands[i][0], hi = i === n - 1 ? Math.min(bands[i][1], c.hi) : bands[i][1];
      const miss = missingIn(c, lo, hi); if (miss.length) gapsDefault++;
      return `way ${i + 1} ${c.e.driver.name}${miss.length ? ` (no data: ${miss.map(m => `${m.order} ${hz(m.from)}–${hz(m.to)}`).join(", ")})` : ""}`;
    });
    lines.push(`- ${n}-way: ${parts.join("; ")}`);
  }
  lines.push("");
}
const out = join(root, args.out || "watch/sim_coverage.md");
writeFileSync(out, lines.join("\n") + "\n");
console.log(`${out.replace(root + "/", "")}: ${sources.length} sources, ${rows} driver-and-way rows, ${gapsDefault} default way(s) with missing data`);
