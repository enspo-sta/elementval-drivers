# elementval-drivers

Loudspeaker driver database (`drivers.json`, `drivers_survey_midbass.json`) and its viewer (`index.html`),
published at <https://enspo-sta.github.io/elementval-drivers/>.

## The viewer

| Tab | What it does |
|---|---|
| Drivers | Every driver with its measurements, grouped by source. "Compare with other drivers" on a driver's page opens Compare with that driver picked. |
| Compare | Overlays up to five drivers, each in its own colour and marker shape (Okabe and Ito's colour-blind safe colours). Pick a source, a measurement (for example harmonic distortion at 94 dB, or intermodulation 30 + 255 Hz) and what to show (for example only H3, or only the intermodulation products). |
| Simulate | Estimates a 2-, 3- or 4-way speaker's harmonic distortion (H2 to H5 and THD) from the drivers' measured curves. Choose the driver for each way, how many of them, and each crossover's frequency and filter (Linkwitz-Riley 2nd, 4th or 8th order, Butterworth 1st to 4th order). |

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

How the simulation works: each way plays through its crossover filters; a driver's measured harmonic
curve is moved to the level the driver actually plays at (harmonic ratio + slope × level change),
with the slopes taken from Purifi's measured level sweeps where they exist and otherwise from the
slopes on the page (typical from this database's data: H2 1.0 and H3 to H5 0.7 dB per dB);
harmonics of different drivers add as powers. Where a driver that matters has no data the result is
left empty rather than guessed. The maths is in `sim-core.js`, the rules for which measurements may
share a chart in `compare-core.js`, and the page code in `tools.js`.

## Automatic updates

| What | When | Where |
|---|---|---|
| Scan the watched sites for driver model numbers | Mondays 04:17 UTC, or by hand from the Actions tab | `.github/workflows/watch-new-drivers.yml` |
| Open an issue for every model that appears on a measurement page for the first time | after each scan | issues labelled `new-driver` |
| Open one issue for new measurement pages about drivers already in the database | after each scan | issues labelled `driver-update` |
| Rebuild the list of where every driver is measured | after each scan, and after each database change on `main` | `watch/coverage.md` |
| Check both database files, and test the viewer's maths | every push and pull request that changes them | `.github/workflows/validate-db.yml` |
| Back up everything (software, database, full history) | Sundays 03:40 UTC | `.github/workflows/backup.yml`, see `BACKUP.md` |

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
node --test tests/*.test.js                # test the crossover maths and the comparison rules
```

The Python scripts use only the Python standard library; the tests need only Node.js.
To try the viewer on your own computer, run `python3 -m http.server` in the repository folder and
open <http://localhost:8000/>.
