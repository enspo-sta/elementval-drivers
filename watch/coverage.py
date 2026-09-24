#!/usr/bin/env python3
"""Write the coverage shortlist: where every driver is measured, and by how many sources.

Reads both database files, watch/config.json and the scan state (watch/state.json,
written by the weekly scan), and writes:

  watch/coverage.md     readable shortlist (renders on GitHub, also on a phone)
  watch/coverage.json   the same data for scripts

Sections:
  1. Drivers in the database: which sources the stored data comes from (each source
     family counted separately), which other sources have measured the same driver,
     and whether any curve is below the capture minimum.
  2. Not in the database, measured by two or more sources (the shortlist).
  3. Not in the database, measured by one source.

Standard library only. Usage: python3 watch/coverage.py [--state path/to/state.json]
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from common import (ROOT, STATE, driver_keys, families_of, family_kind, load_config, load_databases,
                    points_per_decade)

OUT_MD = ROOT / "watch" / "coverage.md"
OUT_JSON = ROOT / "watch" / "coverage.json"


def lab_evidence(state, cfg):
    """{model key: {family: [measurement urls]}} from the scan state, plus display names and brands."""
    fam_of_source = {s["name"]: s["family"] for s in cfg["sources"]}
    ev, names = {}, {}
    for sname, s in (state or {}).get("sources", {}).items():
        fam = s.get("family") or fam_of_source.get(sname)
        if fam is None:
            continue                     # a source no longer in the settings (for example SB Acoustics)
        for k, m in s.get("models", {}).items():
            if m.get("measured"):
                ev.setdefault(k, {}).setdefault(fam, []).extend(u for u in m["measured"] if u)
                if k not in names or "." in m["display"]:
                    names[k] = (m["brand"], m["display"])
    return ev, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=str(STATE))
    ap.add_argument("--stdout", action="store_true", help="print the Markdown instead of writing the files")
    args = ap.parse_args()

    cfg = load_config()
    floor = cfg.get("capture", {}).get("minimum_points_per_decade", 40)
    state_path = Path(args.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    evidence, names = lab_evidence(state, cfg)
    today = dt.date.today().isoformat()

    # 1. Drivers in the database
    in_db, db_keys = [], set()
    for fname, db in load_databases():
        for d in db.get("drivers", []):
            captured, derived, low = {}, 0, []
            for m in d.get("measurements", []):
                fams = families_of(m.get("source"), cfg)
                fam = fams[0] if len(fams) == 1 else "Unclassified"
                if family_kind(fam, cfg) == "derived":
                    derived += 1
                    continue
                captured[fam] = captured.get(fam, 0) + 1
                dens = points_per_decade(m)
                if dens is not None and dens < floor:
                    low.append(f"{m.get('type', '?')} ({dens:.0f}/decade)")
            keys = driver_keys(d, cfg)
            db_keys |= keys
            elsewhere = {}
            for k in keys:
                for fam, urls in evidence.get(k, {}).items():
                    if fam not in captured:
                        elsewhere.setdefault(fam, urls[0])
            in_db.append({"id": d.get("id"), "name": d.get("name"), "role": d.get("role"), "file": fname,
                          "captured": captured, "derived_sets": derived,
                          "also_measured_at": elsewhere, "tracked": bool(keys),
                          "independent_sources": len(captured) + len(elsewhere),
                          "below_capture_minimum": low})

    # 2 and 3. Drivers measured somewhere but not in the database
    outside = []
    for k, fams in evidence.items():
        if k in db_keys:
            continue
        brand, display = names[k]
        outside.append({"key": k, "brand": brand, "model": display, "sources": {f: u[0] for f, u in fams.items()}})
    outside.sort(key=lambda x: (-len(x["sources"]), x["brand"], x["model"]))
    multi = [x for x in outside if len(x["sources"]) >= 2]
    single = [x for x in outside if len(x["sources"]) == 1]

    data = {"date": today, "scan_state": bool(state), "in_database": in_db,
            "shortlist_multiple_sources": multi, "single_source": single}

    def link(fam, url):
        return f"[{fam}]({url})"

    md = ["# Where each driver is measured", "",
          f"Generated {today} by `watch/coverage.py` from the database and the weekly scan; do not edit by hand.", "",
          "Each source is counted separately: a driver measured by HiFiCompass and by Erin's Audio Corner has two "
          "sources, and their data is stored as separate measurement sets. Models and calculations "
          "(\"Derived\") are not counted as sources.", ""]
    if not state:
        md += ["> The weekly scan has not run yet, so only the sources stored in the database are shown. "
               "The \"also measured at\" column and sections 2 and 3 fill in after the first scan.", ""]
    def driver_table(rows):
        out = ["| Driver | Role | Stored from (measurement sets) | Also measured at, not yet stored | Sources | "
               "Below capture minimum |", "|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: (-r["independent_sources"], r["name"] or "")):
            stored = ", ".join(f"{f} ({n})" for f, n in sorted(r["captured"].items())) or "none"
            if r["derived_sets"]:
                stored += f"; derived ({r['derived_sets']})"
            also = ", ".join(link(f, u) for f, u in sorted(r["also_measured_at"].items()))
            if not also:
                also = "none found" if r["tracked"] else "not tracked (no model number the scan follows)"
            low = "; ".join(r["below_capture_minimum"]) or "none"
            out.append(f"| {r['name']} | {r['role']} | {stored} | {also} | {r['independent_sources']} | {low} |")
        return out

    main_rows = [r for r in in_db if r["file"] == "drivers.json"]
    survey_rows = [r for r in in_db if r["file"] != "drivers.json"]
    md += [f"## 1. In the database ({len(main_rows)} drivers in drivers.json)", ""] + driver_table(main_rows)
    if survey_rows:
        md += ["", f"### Midbass survey ({len(survey_rows)} drivers in drivers_survey_midbass.json)", ""]
        md += driver_table(survey_rows)
    md += ["", f"## 2. Shortlist: not in the database, measured by two or more sources ({len(multi)})", ""]
    if multi:
        md += ["| Brand | Model | Sources | Where |", "|---|---|---|---|"]
        md += [f"| {x['brand']} | {x['model']} | {len(x['sources'])} | "
               f"{', '.join(link(f, u) for f, u in sorted(x['sources'].items()))} |" for x in multi]
    else:
        md.append("None yet." if state else "Appears after the first scan.")
    md += ["", f"## 3. Not in the database, measured by one source ({len(single)})", ""]
    if single:
        md += ["| Brand | Model | Where |", "|---|---|---|"]
        md += [f"| {x['brand']} | {x['model']} | "
               f"{', '.join(link(f, u) for f, u in x['sources'].items())} |" for x in single]
    else:
        md.append("None yet." if state else "Appears after the first scan.")
    text = "\n".join(md) + "\n"

    if args.stdout:
        print(text)
    else:
        OUT_MD.write_text(text)
        OUT_JSON.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        print(f"coverage: {len(in_db)} in database, {len(multi)} on the shortlist, {len(single)} single-source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
