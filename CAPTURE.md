# Capture standard

How finely curves are captured into `drivers.json`, and why the limits are where they are.
The validation check warns when a curve is below the minimum; `capture/WORKLIST.md` lists those
curves so they can be captured again. How to capture on your own computer, with your HiFiCompass
login: `capture/CHROME_CAPTURE.md`.

## Resolution

| What | Target | Minimum | Upper limit |
|---|---|---|---|
| Curves on a logarithmic frequency axis (harmonic distortion, current distortion, compression, frequency response) | 1/24 octave = 80 points per decade | 1/12 octave = 40 points per decade | 1/48 octave = 160 points per decade |
| Level (y axis) | 0.1 dB steps | | |
| Bar spectra (intermodulation products) | every product the chart shows | | |
| Drive levels | every level the source publishes, each as its own series | | |

A 20 Hz – 20 kHz curve at the target is about 240 points.

**Why 1/24 octave.** The smallest charts in use are audiohorn's, at 800 pixels wide. Across three
decades that gives about 230 pixels per decade, so 80 points per decade leaves roughly 3 pixels
between neighbouring points. Each point is then read from its own part of the curve. Going finer
than about 1 pixel per point adds file size without adding information. The upper limit applies to
exact data (PDF vectors, raw data files), where more points than 160 per decade are thinned out.

## Levels

Store every level a source measured, each as its own measurement set, exactly as measured:

- `conditions.spl_db`: the sound pressure the fundamental reaches at 1 m, as the source states it.
  HiFiCompass already states its levels at 1 m (the 315 mm microphone distance is corrected on the
  site), so take its numbers as shown and never correct them again. Only for a source that states
  the level at the microphone, convert with 20 × log10(distance / 1 m), far field only (for example
  −10.0 dB from 315 mm to 1 m);
- `conditions.drive_v` and `conditions.distance_mm` as the source states them.

Do not normalise curves to a common level. The viewer does the matching: Compare draws every driver
at its measured level closest to the target level (and says how far off it is), the driver page
overlays all levels of a curve, and Simulate interpolates between measured levels at the level a
driver actually plays at. HiFiCompass shows axial sound pressure and harmonics at several drive
levels; capture all of them.

Every set also names its `kind` from `schema/kinds.json` (frequency response, impedance, harmonics
vs frequency, level sweep, intermodulation, ...). See `EXTENDING.md` for the full format.

## Where to take the data from

Always use the most exact form a source publishes, in this order:

1. **Vector data in a PDF.** Purifi's datasheets draw their graphs as vector lines. Checked on the
   PTT5.25X04-NAA-05 datasheet v1.00 (December 2025): figures 5 to 11 (frequency response, current
   harmonic distortion, sound pressure harmonic distortion against level, intermodulation) are
   coloured vector paths with 200 to 600 points each. Read them with `capture/pdf_vectors.py`
   (PyMuPDF), which lists the paths and the printed axis numbers and maps page coordinates to Hz and dB. The result is the
   manufacturer's own data points, with no pixel rounding. Record it as
   `"method": "... (PDF vector)"` with `"confidence": "high"`.
2. **Raw data files.** HiFiCompass offers `.frd` and `.zma` files (frequency response and
   impedance) for some drivers. Keep their native resolution, thinned to the upper limit.
3. **The largest original image**, pixel-extracted with `capture/image_curves.py`:
   - HiFiCompass: remove `/styles/<style>/public/` from the image address to get the original upload.
     Checked: `.../styles/1000_px/public/afc/ptt5.25x04-naa-05_315mm_2v83_0deg.png` is 1000 × 498 pixels,
     `.../afc/ptt5.25x04-naa-05_315mm_2v83_0deg.png` is 1276 × 635.
   - Erin's Audio Corner: the Dropbox-hosted charts are the originals (1600 × 900); older reviews use
     images on his own site (1264 × 730).
   - audiohorn: charts are 800 pixels wide JPEG (the only size offered).
   - audioXpress: charts are shown at 1200 pixels wide. Its `robots.txt` excludes the original image
     folder and blocks Anthropic's crawlers, so audioXpress figures are only captured by hand from
     articles you open yourself.

## Keeping sources separate

Each measurement set comes from exactly one source, and its `source` text names that source
(for example `HiFiCompass HD ...`, `datasheet Fig.9 ...`, `Erin's Audio Corner ...`,
`audioXpress Test Bench ...`, `audiohorn ...`). The validation check fails when a set names no
known source or more than one. Data from two sources is never averaged or merged into one set;
compare them side by side instead. The families are listed in `watch/config.json` under `families`.

## File size

`drivers.json` is 615 KB today for 17 drivers and 5,736 curve points (about 109 bytes per point as
written, 51 KB when the web server compresses it). A richly measured driver at the target
resolution (15 curves of 240 points) adds about 390 KB as written today, or about 105 KB if the
points are written compactly (`{"x":81.2,"y":-52.3}` on one line). Keep the file below about
10 MB so the viewer stays quick on a phone: that is roughly 100 such drivers written compactly.
Beyond that, split the data into one file per driver.
