#!/usr/bin/env python3
"""Add a captured measurement set to drivers.json, or replace one, and keep the file valid.

  python3 capture/add_set.py --driver ptt525x04naa05 --set meta.json --series h2.json --series h3.json
  python3 capture/add_set.py --driver ptt525x04naa05 --set meta.json --series curves.json --replace 0
  python3 capture/add_set.py --new-driver driver.json          (a new record with no measurements yet)

meta.json holds everything except the curves, for example:
  {"kind": "hd-frequency", "type": "HD vs frequency (ratio)", "method": "PDF vector",
   "source": "datasheet v1.00 Fig.7 (PDF vector)", "confidence": "high", "chartType": "line",
   "conditions": {"spl_db": 94, "distance_mm": 1000},
   "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Harmonic ratio", "unit": "dB re fund"}}}
Each --series file is the output of capture/pdf_vectors.py or capture/image_curves.py.

The change is written only when watch/validate_db.py finds no error in the result.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from common import dumps_db  # noqa: E402  (the database's layout: each curve's points on one line)
from validate_db import validate  # noqa: E402

DB = ROOT / "drivers.json"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--driver")
    ap.add_argument("--set")
    ap.add_argument("--series", action="append", default=[])
    ap.add_argument("--replace", type=int, help="index of the set to replace (see the driver's page or drivers.json)")
    ap.add_argument("--new-driver")
    ap.add_argument("--file", default=str(DB))
    a = ap.parse_args()
    path = Path(a.file)
    db = json.loads(path.read_text())
    today = dt.date.today().isoformat()
    if a.new_driver:
        rec = json.loads(Path(a.new_driver).read_text())
        rec.setdefault("measurements", [])
        if any(d["id"] == rec.get("id") for d in db["drivers"]):
            sys.exit(f"{rec.get('id')} is already in {path.name}; identities are never merged, pick a new id for a variant")
        rec["updated"] = today
        db["drivers"].append(rec)
        what = f"added driver {rec.get('id')}"
    else:
        if not (a.driver and a.set):
            sys.exit("give --driver and --set (or --new-driver)")
        d = next((x for x in db["drivers"] if x["id"] == a.driver), None)
        if not d:
            sys.exit(f"no driver {a.driver} in {path.name}")
        m = json.loads(Path(a.set).read_text())
        series = list(m.get("series") or [])
        for f in a.series:
            series += json.loads(Path(f).read_text())["series"]
        if series:
            m["series"] = series
        m["captured"] = today
        if a.replace is not None:
            if not 0 <= a.replace < len(d["measurements"]):
                sys.exit(f"{a.driver} has sets 0 to {len(d['measurements']) - 1}")
            old = d["measurements"][a.replace]
            m.setdefault("replaces", f"{old.get('type')} ({old.get('source')}), replaced {today}")
            d["measurements"][a.replace] = m
            what = f"replaced set {a.replace} of {a.driver}"
        else:
            d["measurements"].append(m)
            what = f"added set {len(d['measurements']) - 1} to {a.driver}"
        d["updated"] = today
    db["meta"]["updated"] = today
    tmp = path.with_suffix(".check.json")
    tmp.write_text(dumps_db(db))
    try:
        errors, warnings, _ = validate([tmp])
    finally:
        tmp.unlink()
    if errors:
        print("Not written; the result would have these errors:", *errors, sep="\n  ")
        sys.exit(1)
    path.write_text(dumps_db(db))
    print(f"{what} in {path.name}. {len(warnings)} warning(s) in the file:", *warnings[:20], sep="\n  ")


if __name__ == "__main__":
    main()
