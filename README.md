# elementval-drivers

Loudspeaker driver database (`drivers.json`, `drivers_survey_midbass.json`) and its viewer (`index.html`),
published at <https://enspo-sta.github.io/elementval-drivers/>.

## The viewer

| Tab | What it does |
|---|---|
| Drivers | Every driver. A driver's page shows every curve, from all sources or one source at a time (buttons with each source's reliability). Curves of the same kind measured at several levels share one chart, one colour per level. Every chart has an export control, and "Export all curves" exports the driver. |
| Compare | Overlays up to five drivers, each in its own colour and marker shape (Okabe and Ito's colour-blind safe colours). Pick a source, a measurement and what to show (for example only H3, or only the intermodulation products). Levels are matched: each driver is drawn at its measured level closest to the target level, the level used is shown next to its name, and harmonic curves can be moved the rest of the way with the level rule. |
| Simulate | Estimates a 2-, 3- or 4-way speaker's harmonic distortion (H2 to H5 and THD) from the drivers' measured curves. Choose the driver for each way, how many of them, and each crossover's frequency and filter (Linkwitz-Riley 2nd, 4th or 8th order, Butterworth 1st to 4th order). Every measured level of a driver is used: at each frequency the curves are interpolated at the level the driver actually plays at. |

Exports: CSV (and a variant for Excel with Swedish settings), text for REW, FRD for VituixCAD and
XSim (sound pressure curves), ZMA (impedance), and JSON with the stored data. Several files download
as one ZIP. The same formats work from the command line: `node tools/export.mjs --help` lists the
options (for example `node tools/export.mjs --source HiFiCompass --format csv,rew`).

Both tools use one source at a time, because sources measure in different ways and their numbers do
not line up. Mixing can be switched on, with a warning. Sources are listed most reliable first; the
ranking lives in `watch/config.json` (`rank` and `reliability` of each family):

| Rank | Source | Reliability |
|---|---|---|
| 1 | Manufacturer datasheet (Purifi) | best |
| 2 | HiFiCompass | state of the art |
| 3 | Erin's Audio Corner, audioXpress | less reliable |
| 4 | audiohorn | not rated yet |
| 5 | diyAudio, Parts Express | varies: some measurements are well made, most are not |
| 9 | Derived (model or calculation) | calculated, not measured |

The settings of a comparison or simulation are kept in the page address, so a link or bookmark
opens the same view again.

The viewer is built from small parts: every tab and every export format is one file, listed in
`app/modules.js`, and the kinds of measurement are listed in `schema/kinds.json`. How to add a
feature: `EXTENDING.md`.

## Prices

`prices.json` holds the lowest price found for each driver at European shops (`watch/prices_config.json`
lists the shops; add or remove one there). `watch/prices.py` rebuilds it every Monday
(`.github/workflows/prices.yml`): it obeys each shop's `robots.txt`, finds product pages through the
shop's sitemap, reads the price from the page's structured data (schema.org offers) and converts to
Swedish kronor with the European Central Bank's daily rates. The viewer shows the offers on each
driver's page and the lowest price on its card. Prices are as found on the day in `prices.json`
(`meta.updated`); check the shop before buying. `prices.md` is the same as a table.

What the scan cannot see: Toutlehautparleur refuses automatic reading and shows its best prices only
when logged in, so it is checked by hand on David's computer (step 8 of `capture/CHROME_CAPTURE.md`
writes `price_logged_in` into the offer); a shop that sells whole boxes (Purifi's own shop, `"pack"`
in the config) is listed with its box price but never counted as the lowest; a shop without a sitemap
can be given its product pages by hand (`"pages"`) or pages to follow links from (`"hubs"`); without
either, the scanner follows links from the front page and from brand pages found in the sitemap, two
levels at most. A page without structured price data is read from its price element (marked in the offer). audio-hi.fi is the European distributor for
BlieSMa. A shop's server that sends an incomplete certificate chain is completed the way a browser
does (the missing intermediate certificate is fetched from the address in the certificate);
verification is never turned off.

## Tests

| Command | Checks |
|---|---|
| `python3 watch/validate_db.py` | the database files against the rules |
| `node --test tests/*.test.mjs` | the viewer's maths, comparison rules and exports |
| `python3 -m unittest discover -s tests -p "test_*.py"` | the capture tools, the datasheet PDF reader and the price scanner (no internet needed) |
| `npm install && npx playwright install chromium && npm run test:browser` | the viewer in a real browser: every tab, exports, an empty search, and screen sizes from a 320 px phone to a 1440 px laptop |

GitHub runs all of them on every push (`.github/workflows/validate-db.yml`).

## Data quality

| File | What it holds |
|---|---|
| `watch/consistency.md` | values that should agree with each other, checked on every driver: Thiele/Small parameters against each other, Purifi's harmonic curves against their level sweeps, band-THD tables against their curves, calculated curves against their recipe, excursion limits against Sd and Xmax, test-tone levels |
| `capture/WORKLIST.md` | what to capture next: curves below the capture minimum, disagreements to check at the source, every curve HiFiCompass and Purifi publish that is not stored yet, and a weekly random spot check |
| `capture/CHROME_CAPTURE.md` | how to capture from HiFiCompass (with your login) and Purifi on your own computer, with Claude Code and Chrome |

## Automatic updates

| What | When | Where |
|---|---|---|
| Scan the watched sites for driver model numbers | Mondays 04:17 UTC, or by hand from the Actions tab | `.github/workflows/watch-new-drivers.yml` |
| Open an issue for every model that appears on a measurement page for the first time | after each scan | issues labelled `new-driver` |
| Open one issue for new measurement pages about drivers already in the database | after each scan | issues labelled `driver-update` |
| Rebuild the list of where every driver is measured | after each scan, and after each database change on `main` | `watch/coverage.md` |
| Check both database files; test the viewer, the exports and the capture tools | every push and pull request that changes them | `.github/workflows/validate-db.yml` |
| Rebuild the consistency report and the capture work list | after each change on `main` | `watch/consistency.md`, `capture/WORKLIST.md` |
| Back up everything (software, database, full history) | Sundays 03:40 UTC | `.github/workflows/backup.yml`, see `BACKUP.md` |
| Find the lowest price of every driver at European shops | Mondays 05:40 UTC | `.github/workflows/prices.yml`, result in `prices.json` and `prices.md` |

Watched sites, each kept as a separate source (edit `watch/config.json` to change them):

| Source | Kind | What is read |
|---|---|---|
| Purifi: <https://purifi-audio.com/> | manufacturer datasheets (with distortion curves) | home page and sitemap |
| HiFiCompass: <https://hificompass.com/en/speakers/measurements> | test lab | home page, sitemap and measurement listing, 10 s between pages (its `robots.txt`) |
| Erin's Audio Corner: <https://www.erinsaudiocorner.com/driveunits/> | test lab | home page, sitemap and drive-unit index |
| audioXpress Test Bench: <https://audioxpress.com/tags/test-bench> | test lab | the Test Bench, Purifi and Satori tag listings only, 5 s between pages (its `robots.txt`) |
| audiohorn: <https://audiohorn.net/> | test lab | sitemap and the six driver test pages |

SB Acoustics and BlieSMa's own sites are not scanned: they publish no distortion measurements.
Their drivers are still found when one of the test labs measures them.

A model is reported only when it appears on a measurement page, so a driver that is merely listed
in a shop does not open an issue. The first scheduled run is a baseline: it records the current
state and opens no issues. A source added later gets the same treatment on its first scan.

### Files the watch keeps up to date

- `watch/coverage.md`: every driver, which sources its stored data comes from, which other sources have
  measured it, and a shortlist of drivers not yet in the database that two or more sources have measured.
- `watch/catalogue.md`: every model seen at the watched sites that is not in the database.
- `watch/state.json`: what has been seen, so nothing is reported twice. Do not edit it by hand.

### Adding a driver an issue reports

1. Collect the measurements linked in the issue.
2. Capture them as described in `CAPTURE.md`: 1/24 octave, from PDF vector data or the largest original
   image, one measurement set per source.
3. Add the record to `drivers.json`. The issue contains an empty record to start from.
4. Open a pull request with `Closes #<issue>` in the description. The validation check must pass.
5. Merge it. The coverage list is rebuilt and the viewer republished automatically.

Close an issue without adding the driver if you do not want it: it will not be reported again.
To stop a model being tracked at all, add it to `ignore` in `watch/config.json`.

### Running it yourself

```sh
python3 watch/watch_sources.py --dry-run   # scan and print, change nothing
python3 watch/validate_db.py               # check the database files
python3 watch/coverage.py --stdout         # print where each driver is measured
python3 watch/check_consistency.py         # rebuild watch/consistency.md
python3 capture/worklist.py                # rebuild capture/WORKLIST.md
python3 watch/prices.py --dry-run          # scan the shops and print the prices found
node --test tests/*.test.mjs               # test the viewer: maths, comparison rules, exports
python3 -m unittest discover -s tests -p "test_*.py"   # test the capture tools and the price scanner
npm run test:browser                       # test the viewer in a real browser (after npm install)
```

The watch scripts use only the Python standard library; the capture tools also need PyMuPDF,
Pillow and numpy (`python3 -m pip install pymupdf pillow numpy`); the viewer's tests need Node.js.
To try the viewer on your own computer, run `python3 -m http.server` in the repository folder and
open <http://localhost:8000/>.
