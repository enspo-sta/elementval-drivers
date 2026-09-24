# Prompt for a scheduled Claude Code session (optional second stage)

Use this as the prompt of a weekly Claude Code routine on the `enspo-sta/elementval-drivers`
repository, scheduled after the Monday scan (for example Mondays 07:00 UTC). The routine's
cloud environment must allow these hosts: purifi-audio.com, hificompass.com,
www.erinsaudiocorner.com, erinsaudiocorner.com, dl.dropboxusercontent.com (Erin's newer charts
are hosted there) and audiohorn.net.

Not included on purpose:
- audioXpress: its robots.txt blocks Anthropic's crawlers, so Test Bench articles are captured by
  hand. The weekly scan still lists them (it reads only the tag listing pages).
- HiFiCompass Premium content: the routine cannot log in. Premium-only pages need Claude Code on your
  own computer with Claude in Chrome (`claude --chrome`), which uses your browser's login.

---

Work through the open GitHub issues labelled `new-driver` and `driver-update` in
enspo-sta/elementval-drivers, oldest first, at most three per run. Follow CAPTURE.md.

For each `new-driver` issue:
1. Read the issue. For every linked measurement page except audioXpress, download the page and its
   charts with curl. Pause 10 seconds between HiFiCompass requests and 2 seconds between audiohorn
   requests. Take the most exact form each source offers (CAPTURE.md, "Where to take the data from"):
   PDF vector data for Purifi datasheets, raw .frd/.zma files where offered, otherwise the largest
   original image (for HiFiCompass, remove `/styles/<style>/public/` from the image address).
   Erin's T/S and large-signal tables are plain text in the page: take them from the text.
2. Use the driver-analysis skill for the database conventions and the pixel-extraction skill for
   curves that exist only as images. Capture at 1/24 octave (80 points per decade) and 0.1 dB.
3. Add one record to drivers.json following the existing records: T/S parameters in `ts`, and one
   measurement set per source and chart, each with `source` naming that source, `confidence`,
   `chartType` (line, bar or table), `axes` and `series`. Never blend two sources in one set, and
   never merge the new driver into an existing identity; proxy variants are separate records.
   Set `meta.updated` to today.
4. Run `python3 watch/validate_db.py` and fix every error and every capture-resolution warning for
   the new record. Run `python3 watch/coverage.py --stdout` and check the driver's row.
5. Push a branch `driver/<id>` and open a pull request titled "Add <name>" whose description lists
   every source URL, says for each measurement set whether it came from vector data, a data file or
   pixel extraction, and includes `Closes #<issue>`. Do not merge it.

For a `driver-update` issue: open each linked page, decide whether it holds data the record does
not have (a new lab test, a new datasheet revision), and either open a pull request adding it as a
new measurement set with its own source, or comment on the issue saying why nothing changed.

If a datasheet cannot be downloaded or a plot cannot be digitised reliably, comment on the issue
with what is missing and leave it open.
