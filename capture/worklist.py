#!/usr/bin/env python3
"""Write capture/WORKLIST.md: what to capture next from HiFiCompass and Purifi, and why.

  1. sets below the capture minimum (CAPTURE.md), to capture again at 1/24 octave
  2. stored values that disagree with each other (watch/check_consistency.py), to check against the source
  3. per driver: what HiFiCompass and Purifi publish that is not stored yet (every curve, every level)
  4. a random spot check: three drivers whose stored curves are compared point by point with the source
  5. the sets read automatically from chart images, to check by eye

Run it after any database change:  python3 capture/worklist.py
"""
import datetime as dt
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from common import families_of, load_config, points_per_decade  # noqa: E402
import check_consistency as cc  # noqa: E402

OUT = ROOT / "capture" / "WORKLIST.md"
HOW = {
    "Manufacturer datasheet": "PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines)",
    "HiFiCompass": "original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py`",
    "Erin's Audio Corner": "original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py`",
}
# What each source publishes per driver, as kinds (schema/kinds.json). HiFiCompass shows axial sound
# pressure and harmonics at several drive levels; Purifi's datasheets have the figures listed.
PUBLISHES = {
    "HiFiCompass": [
        ("frequency-response", "axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m)"),
        ("hd-frequency", "harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates)"),
        ("impedance", "impedance (use the .zma file when offered)"),
        ("imd-summary", "two-tone intermodulation, where measured"),
    ],
    "Manufacturer datasheet": [
        ("frequency-response", "frequency response figure"),
        ("impedance", "impedance figure"),
        ("hd-frequency", "harmonic distortion vs frequency at 94 dB"),
        ("hd-level", "harmonic distortion vs level (level sweeps)"),
        ("hd-current", "current distortion"),
        ("imd-spectrum", "intermodulation spectra (both tone pairs)"),
    ],
}


def main():
    cfg = load_config()
    db = json.loads((ROOT / "drivers.json").read_text())
    floor = cfg["capture"]["minimum_points_per_decade"]
    lines = ["# Capture work list", "",
             f"Written by `capture/worklist.py` on {dt.date.today().isoformat()}. How to work through it: `capture/CHROME_CAPTURE.md`.", ""]

    lines += ["## 1. Capture again at higher resolution", "",
              f"Below {floor} points per decade (target 80, CAPTURE.md). Replace each set with `capture/add_set.py --replace <set>`.", "",
              "| Driver | Set | What | Source | Now | How |", "|---|---|---|---|---|---|"]
    n1 = 0
    for d in db["drivers"]:
        for i, m in enumerate(d["measurements"]):
            fams = families_of(m.get("source"), cfg)
            dens = points_per_decade(m)
            if dens is None or dens >= floor or not fams or fams[0].startswith("Derived"):
                continue
            n1 += 1
            lines.append(f"| {d['name']} (`{d['id']}`) | {i} | {m['type']} | {fams[0]} | {dens:.0f} per decade | {HOW.get(fams[0], 'original chart, then `capture/image_curves.py`')} |")
    if not n1:
        lines.append("| — | | nothing below the minimum | | | |")

    rep = cc.Report()
    drivers = db["drivers"] + json.loads((ROOT / "drivers_survey_midbass.json").read_text())["drivers"]
    byid = {d["id"]: d for d in drivers}
    for d in drivers:
        cc.check_parameters(d, rep); cc.check_notes(d, rep); cc.check_sources(d, rep, cfg); cc.check_sweep(d, rep, cfg)
        cc.check_band_thd(d, rep, cfg); cc.check_levels(d, rep, cfg); cc.check_pair(d, rep, cfg, byid)
        cc.check_excursion(d, rep); cc.check_tones(d, rep); cc.check_curves(d, rep)
    lines += ["", "## 2. Values that disagree: check against the source", "",
              "From `watch/check_consistency.py` (full list in `watch/consistency.md`).", "",
              "| Check | Driver | Detail |", "|---|---|---|"]
    diffs = [r for r in rep.rows if r[2] == "differs" and r[0] != "levels"]
    lines += [f"| {c} | `{drv}` | {det.replace('|', '/')} |" for c, drv, _, det in sorted(diffs)] or ["| — | | nothing disagrees |"]
    slopes = [r for r in rep.rows if r[2] == "differs" and r[0] == "levels"]
    if slopes:
        lines += ["", "Level slopes that differ from the typical rule (H2 +1.0, H3 +0.7 dB per dB). Information, not an error: "
                  "each drive level is stored as the source measured it and the viewer prefers a measured level over a scaled "
                  "one; a slope far off the rule says only that the rule would mislead for this driver. Look at the curve "
                  "if it also looks wrong beside its chart.", "", "| Driver | Detail |", "|---|---|"]
        lines += [f"| `{drv}` | {det.replace('|', '/')} |" for c, drv, _, det in sorted(slopes)]

    lines += ["", "## 3. Every curve HiFiCompass and Purifi publish", "",
              "Stored now, and what to add. Capture each drive level as its own set with the SPL it gives at 1 m.", ""]
    for d in db["drivers"]:
        by_fam = {}
        for m in d["measurements"]:
            fams = families_of(m.get("source"), cfg)
            if fams:
                lvl = (m.get("conditions") or {}).get("spl_db")
                by_fam.setdefault(fams[0], []).append(f"{m.get('kind')}{' ' + str(lvl) + ' dB' if isinstance(lvl, (int, float)) else ''}")
        # a record whose `source` names a measurement page but holds no set yet (a driver just added) is listed in full
        page_fams = families_of(d.get("source") or "", cfg) if not d["measurements"] else []
        for fam, wants in PUBLISHES.items():
            if fam not in by_fam and fam not in page_fams and not (fam == "Manufacturer datasheet" and d["manufacturer"] == "Purifi" and "proxy" not in d["name"]):
                continue
            have = sorted(set(by_fam.get(fam, [])))
            missing = [w for k, w in wants if not any(h.startswith(k) for h in have)]
            normalised = [m for m in d["measurements"] if (families_of(m.get("source"), cfg) or [""])[0] == fam
                          and m.get("kind") == "hd-frequency" and "normali" in (str(m.get("source")) + str(m.get("note"))).lower()]
            if normalised:
                missing.insert(0, "the harmonics at each drive level actually measured (the stored "
                               f"{normalised[0]['conditions'].get('spl_db')} dB curve was normalised from them; keep it until they are in)")
            prefix = "if Purifi publishes a datasheet for this exact variant: " if fam == "Manufacturer datasheet" and not have else ""
            page = f" Page: <{d['source']}> (what it offers: `capture/inventory.md`)." if fam in page_fams else ""
            lines.append(f"- **{d['name']}** (`{d['id']}`), {fam}: stored {', '.join(have) or 'nothing'}.{page}")
            lines.append(f"  Add{' (' + prefix.rstrip(': ') + ')' if prefix else ''}: {'; '.join(missing) if missing else 'check every drive level is stored, as measured'}.")

    week = int(dt.date.today().strftime("%G%V"))
    pool = [d for d in db["drivers"] if any((families_of(m.get("source"), cfg) or [""])[0] in ("HiFiCompass", "Manufacturer datasheet") for m in d["measurements"])]
    pick = random.Random(week).sample(pool, k=min(3, len(pool)))
    lines += ["", "## 4. Random spot check", "",
              f"Chosen at random for week {str(week)[4:]} of {str(week)[:4]} (the choice changes weekly). For each, capture the source's curve again and compare "
              "with the stored one; differences above 1 dB outside the noise floor need a note or a recapture.", ""]
    for d in pick:
        sets = [f"{i}: {m['type']}" for i, m in enumerate(d["measurements"])
                if (families_of(m.get("source"), cfg) or [""])[0] in ("HiFiCompass", "Manufacturer datasheet") and m.get("chartType") == "line"]
        lines.append(f"- **{d['name']}** (`{d['id']}`): sets {'; '.join(sets)}")
    auto = [(d, i, m) for d in db["drivers"] for i, m in enumerate(d["measurements"]) if "automated" in str(m.get("method", ""))]
    if auto:
        lines += ["", "## 5. Sets read automatically from chart images (check by eye)", "",
                  "Read on GitHub by `capture/chart_read.py` from the source's chart images and stored with confidence *medium*. "
                  "Open the chart named in the set's note beside the viewer's curve; a difference above 1 dB (0.3 ohm for impedance) "
                  "outside the noise floor needs a note or a recapture. The self-checks in each note compare the reading with the page's table.", ""]
        for d, i, m in auto:
            checks = [part for part in str(m.get("note", "")).split("; ") if part.startswith("check ")]
            lines.append(f"- **{d['name']}** (`{d['id']}`), set {i}: {m['type']} — {'; '.join(checks) if checks else 'no self-check possible for this kind'}")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {n1} to recapture, {len(diffs)} disagreements, {len(slopes)} level slopes off the rule, spot check {', '.join(d['id'] for d in pick)}, {len(auto)} automated sets")


if __name__ == "__main__":
    main()
