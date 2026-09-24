# Prompt for a scheduled Claude Code session (optional second stage)

Use this as the prompt of a weekly Claude Code routine on the `enspo-sta/elementval-drivers`
repository, scheduled after the Monday scan (for example Mondays 07:00 UTC). The routine's
cloud environment must allow these hosts: purifi-audio.com, sbacoustics.com, www.bliesma.de,
hificompass.com, www.erinsaudiocorner.com, erinsaudiocorner.com.

---

Work through the open GitHub issues labelled `new-driver` and `driver-update` in
enspo-sta/elementval-drivers, oldest first, at most three per run.

For each `new-driver` issue:
1. Read the issue and download the manufacturer datasheet (PDF) and any HiFiCompass or
   Erin's Audio Corner measurement pages it links, with curl.
2. Use the driver-analysis skill for the database conventions and the pixel-extraction skill
   for any curve that exists only as a plot image.
3. Add one record to drivers.json following the existing records: T/S parameters in `ts`,
   every measurement with `source`, `confidence`, `chartType` (line, bar or table), `axes` and
   `series`. Never merge the new driver into an existing identity; proxy variants are separate
   records. Set `meta.updated` to today.
4. Run `python3 watch/validate_db.py` and fix every error.
5. Push a branch `driver/<id>` and open a pull request titled "Add <name>" whose description
   lists every source URL and says which curves were pixel-extracted, with `Closes #<issue>`.
   Do not merge it.

For a `driver-update` issue: open each linked page, decide whether it holds data the record
does not have (a new datasheet revision, a new measurement), and either open a pull request
updating the record or comment on the issue saying why nothing changed.

If a datasheet cannot be downloaded or a plot cannot be digitised reliably, comment on the
issue with what is missing and leave it open.
