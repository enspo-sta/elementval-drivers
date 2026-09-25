# Extending the driver database

The viewer and the tools are built from small parts that plug into each other, so a new feature is
usually one new file plus one line in a list. Nothing needs to be compiled: the browser loads the
files as they are.

## How the parts fit together

```
index.html                 page shell: loads Chart.js, app/styles.css and app/main.js
app/main.js                starts the viewer: loads the data, loads every feature, shows the view in the address
app/modules.js             THE LIST OF FEATURES: one line per file in app/views and app/exporters
app/core/                  shared parts, no features
  registry.js              registerView() and registerExporter(): how features plug in
  data.js                  loads drivers.json, the survey, watch/config.json and schema/kinds.json
  compare.js               which measurements may share a chart; level matching; quantities (H2, H3, ...)
  sim.js                   crossover filters and the speaker distortion model
  curves.js                turns stored measurements into plain curves for the exporters
  ui.js                    tab bar, charts, badges, export controls
  state.js                 settings kept in the page address (#compare?src=...)
  zip.js                   packs several exported files into one ZIP
app/views/                 one file per tab: drivers.js, compare.js, simulate.js
app/exporters/             one file per export format: csv.js, rew.js, frd.js, zma.js, json.js
app/styles.css             the look
schema/kinds.json          THE LIST OF MEASUREMENT KINDS (frequency response, harmonics, intermodulation, ...)
watch/config.json          the sources, their reliability rank, and the sites the weekly scan reads
watch/validate_db.py       rules every database change must pass
watch/check_consistency.py values that should agree with each other
capture/                   tools for capturing curves (see capture/CHROME_CAPTURE.md)
tools/export.mjs           the export formats from the command line
tests/                     tests for all of the above (node --test tests/*.test.mjs, python3 -m unittest)
```

The files in `app/core` never draw anything themselves, so the tests and `tools/export.mjs` use the
same code as the page.

## Add a tab

Create `app/views/myview.js`:

```js
import { registerView } from "../core/registry.js";
import { allDrivers } from "../core/data.js";
import { app, navHtml, beginView, esc } from "../core/ui.js";

registerView({
  id: "myview", label: "My view", order: 40, routes: ["myview"],
  show({ params }) {                   // params: the settings after '?' in the address
    beginView(true);                   // true: use the wide page
    app().innerHTML = navHtml("myview") + `<h1>My view</h1>` +
      allDrivers().map(d => `<div>${esc(d.name)}</div>`).join("");
  },
});
```

and add `"./views/myview.js",` to `app/modules.js`. The tab appears in the tab bar and opens at
`#myview`. Keep settings in the address with `writeHash()` from `app/core/state.js` if the view has
any, so a link reopens it the same way.

## Add an export format

Create `app/exporters/myformat.js`:

```js
import { registerExporter } from "../core/registry.js";
import { curveFileName, fmt, isFrequencyCurve } from "./common.js";

registerExporter({
  id: "myformat", label: "My format (for program X)", ext: "txt", order: 50,
  accepts: c => isFrequencyCurve(c),          // which curves the format can hold
  files: curves => curves.map(c => ({         // return one or more files
    name: curveFileName(c, "txt"),
    text: c.points.map(p => `${fmt(p.x)} ${fmt(p.y)}`).join("\n") + "\n",
  })),
});
```

and add `"./exporters/myformat.js",` to `app/modules.js`. It then shows in every export menu of the
viewer (only where it accepts the curves) and in `node tools/export.mjs --list-formats`. A curve has
`label, driver, source, kind, quantity, level, conditions, xLabel, xUnit, yLabel, yUnit, points`
(see `app/exporters/common.js`).

## Add a kind of measurement

Add an entry to `schema/kinds.json`, for example an off-axis response:

```json
{"id": "off-axis", "label": "Off-axis response", "view": "curve",
 "x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Sound pressure", "unit": "dB SPL"},
 "level": "drive", "match": ["angle_deg", "distance_mm"], "export": ["csv", "frd", "json"]}
```

- `view`: `curve`, `bars` or `table`.
- `ratio: true` when the values are dB relative to the fundamental (the viewer can show percent).
- `level`: `"spl"` when every set of this kind is taken at a stated sound pressure level
  (`conditions.spl_db`); sets at different levels are then matched by level in Compare, overlaid per
  level on the driver page, and interpolated in Simulate. `"drive"` when the level is a drive voltage.
  `"spl-near"` for kinds whose stated levels differ slightly between drivers although they were meant
  to be the same (an intermodulation summary at 91.1, 91.2 and 91.7 dB): Compare then offers one level
  button per whole dB and treats a set within 1 dB of the target as measured at it.
- `match`: conditions that must be equal before two sets share a chart (for example the test tones
  of intermodulation, or the angle of an off-axis curve).

Measurement sets then name it with `"kind": "off-axis"`. The validation check refuses a set whose
kind is missing from this file. The viewer draws the new kind on the driver pages and offers it in
Compare with no code change.

## Add a source

Add a family to `watch/config.json` under `families`: `name`, `kind` (manufacturer, lab, forum,
retailer, derived), `match` (a pattern the `source` text of its measurements matches), `url`,
`rank` (1 = most reliable) and `reliability` (the label the viewer shows). If the weekly scan should
read its site, add it under `sources` too.

## Add a consistency check

Add a function to `watch/check_consistency.py` that calls `rep.add(check, driver_id, ok, detail)`
(`ok`: True, False, or None when it cannot be tested) and call it in `main()` and in
`capture/worklist.py`. Its disagreements then appear in `watch/consistency.md` and in the capture
work list.

## A measurement set in drivers.json

```json
{
  "type": "HD (orders) vs frequency",           // title as the source names it
  "kind": "hd-frequency",                       // from schema/kinds.json
  "method": "swept sine, ratio to fundamental",
  "source": "HiFiCompass HD 4 V (original image)",   // must name exactly one source family
  "confidence": "high",                         // high, medium, low or none
  "conditions": {"spl_db": 93.0, "drive_v": 4.0, "distance_mm": 315},
  "chartType": "line",                          // line, bar or table
  "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Harmonic ratio", "unit": "dB re fund"}},
  "series": [{"name": "H2", "points": [{"x": 20.0, "y": -32.1}]}],
  "note": "anything a reader should know"
}
```

Tables use `columns` and `rows` instead of `axes` and `series`. Rules that never change: every set
comes from one source; a calculation is filed under the Derived source; driver identities are
never merged (a variant is its own record); curves are captured as described in `CAPTURE.md`.

## Before you push

```sh
python3 watch/validate_db.py
python3 watch/check_consistency.py
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -p "test_*.py"
```

GitHub runs the same checks on every push (`.github/workflows/validate-db.yml`).
