#!/usr/bin/env python3
"""Read HiFiCompass chart images saved on your own computer (the charts HiFiCompass shows only when logged in with
Premium) with the same reader the GitHub job uses (capture/chart_read.py), and add the results to
capture/chart_read.json; then `python3 capture/sets_from_chart_read.py --write` stores them as sets, exactly as it
does for the job's readings.

Save each chart's original image under incoming/<driver id>/ and list them in incoming/<driver id>/charts.tsv, one
line per image, separated by tabs:

  file name        chart type (empty: from the file name)        the image's address on hificompass.com

Chart types: response, near-response, off-axis, harmonics, current, impedance. Name each file the way HiFiCompass
names its newer charts, so the importer reads the conditions from it: the drive voltage as _2v83_ or _4v_, the
distance as _315mm_, a normalized off-axis chart as _offaxis_normalized_5-30db (its range in dB).

  python3 capture/read_local_charts.py --id sb-satori-wo24p-8
"""
import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
import chart_probe as CP  # noqa: E402
import chart_read as CR  # noqa: E402

TYPES = {"response", "near-response", "off-axis", "harmonics", "current", "impedance"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True, help="the driver's id in drivers.json")
    ap.add_argument("--dir", help="the folder with the images (default incoming/<id>)")
    ap.add_argument("--out", default=str(ROOT / "capture" / "chart_read.json"))
    a = ap.parse_args()
    folder = Path(a.dir) if a.dir else ROOT / "incoming" / a.id
    db = json.loads((ROOT / "drivers.json").read_text())
    d = next((x for x in db["drivers"] if x["id"] == a.id), None)
    if not d:
        sys.exit(f"no driver {a.id} in drivers.json")
    listing = folder / "charts.tsv"
    if not listing.exists():
        sys.exit(f"{listing} is missing: one line per image, tab-separated: file, type, address")
    res = []
    for row in csv.reader(listing.read_text().splitlines(), delimiter="\t"):
        if not row or not row[0].strip() or row[0].startswith("#"):
            continue
        name = row[0].strip()
        ctype = (row[1].strip() if len(row) > 1 else "") or CP.chart_type(name)
        url = row[2].strip() if len(row) > 2 else ""
        if ctype not in TYPES:
            print(f"  {name}: type {ctype!r} is not one the reader takes ({', '.join(sorted(TYPES))}); skipped")
            continue
        path = folder / name
        if not path.exists():
            print(f"  {name}: not in {folder}; skipped")
            continue
        try:
            rec = CR.read_chart(path, {"near-response": "response", "off-axis": "off-axis-read"}.get(ctype, ctype))
        except Exception as e:  # noqa: BLE001
            rec = {"error": f"read failed: {e}"}
        rec.update({"file": name, "url": url, "type": ctype, "read_on": "your computer (capture/read_local_charts.py)"})
        rec["checks"] = CR.checks(a.id, d, ctype, name, rec) if not rec.get("error") else []
        cv = rec.get("curves", [])
        print(f"  {name}: {ctype}; x {rec.get('x_axis')} y {rec.get('y_axis')}; curves "
              f"{[(c.get('name') or c['colour'], len(c['points'])) for c in cv]}; checks {rec['checks']} {rec.get('error', '')}")
        res.append(rec)
    CR.share_names(res)
    prev = Path(a.out)
    out = json.loads(prev.read_text()) if prev.exists() else {"drivers": {}}
    fresh = {r["file"] for r in res}
    out["drivers"][a.id] = [r for r in out["drivers"].get(a.id, []) if r.get("file") not in fresh] + res
    out["date"] = dt.date.today().isoformat()
    prev.write_text(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"{len(res)} chart(s) read into {a.out}; next: python3 capture/sets_from_chart_read.py (to see), then --write")


if __name__ == "__main__":
    main()
