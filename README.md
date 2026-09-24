# elementval-drivers

Loudspeaker driver database (`drivers.json`, `drivers_survey_midbass.json`) and its viewer (`index.html`, published with GitHub Pages).

## Automatic updates

| What | When | Where |
|---|---|---|
| Scan the watched sites for driver model numbers | Mondays 04:17 UTC, or by hand from the Actions tab | `.github/workflows/watch-new-drivers.yml` |
| Open an issue for every model not seen before | after each scan | issues labelled `new-driver` |
| Open one issue for new pages or datasheets about drivers already in the database | after each scan | issues labelled `driver-update` |
| Check both database files | every push and pull request that changes them | `.github/workflows/validate-db.yml` |

Watched sites (edit `watch/config.json` to add or remove):

- Purifi: <https://purifi-audio.com/>
- SB Acoustics and Satori: <https://sbacoustics.com/>
- BlieSMa: <https://www.bliesma.de/>
- HiFiCompass: <https://hificompass.com/>
- Erin's Audio Corner: <https://www.erinsaudiocorner.com/driveunits/>

`watch/catalogue.md` lists every model seen at those sites that is not yet in the database.
`watch/state.json` remembers what has been seen, so nothing is reported twice. Do not edit it by hand.

The first scheduled run is a baseline: it records the current catalogues and opens no issues.
From the second run on, only models that appear after that are reported.

### Adding a driver an issue reports

1. Collect the datasheet and measurements linked in the issue.
2. Add the record to `drivers.json`. The issue contains an empty record to start from.
   Every measurement needs a `source`, and `chartType` must be `line`, `bar` or `table`.
3. Open a pull request with `Closes #<issue>` in the description. The validation check must pass.
4. Merge it. GitHub Pages republishes the viewer within a minute or two.

Close an issue without adding the driver if you do not want it: it will not be reported again.
To stop a model being tracked at all, add it to `ignore` in `watch/config.json`.

### Running it yourself

```sh
python3 watch/watch_sources.py --dry-run   # scan and print, change nothing
python3 watch/validate_db.py               # check the database files
```

Both scripts use only the Python standard library.
