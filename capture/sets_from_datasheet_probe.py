#!/usr/bin/env python3
"""Turn the measured files Purifi publishes beside its datasheets (off-axis responses, impedance, on-axis response) (capture/datasheet_probe.json, written on
GitHub by capture/datasheet_probe.py) into off-axis sets in drivers.json.

One set per driver whose download holds responses at two or more angles: one series per angle ("0°", "5°", ...),
the rows as the files print them (to six significant digits of frequency and 0.001 dB). Left out, and said so in the set's note: a row at 0 Hz (it has no place on
a logarithmic frequency axis) and the phase column (the viewer draws sound pressure only). The level is checked
against the sensitivity the datasheet states; a file whose 0° response misses it by more than 1.5 dB is not used.

  python3 capture/sets_from_datasheet_probe.py            # show what would be made
  python3 capture/sets_from_datasheet_probe.py --write    # write drivers.json (after the validator passes)
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from common import dumps_db  # noqa: E402  (the database's layout: each curve's points on one line)
from validate_db import validate  # noqa: E402

fx = lambda f: float(f"{f:.6g}")  # six significant digits: 0.366211 Hz and 19981 Hz alike stay apart
ANGLE = re.compile(r"(?:\bhor\s*(\d+)|_(\d+)\s*deg)\.(?:txt|frd|csv)$", re.I)


def angle_of(name):
    m = ANGLE.search(name)
    return int(m.group(1) or m.group(2)) if m else None


def conditions_text(pages):
    """The datasheet's measurement conditions and figure captions (the lines the note quotes)."""
    text = "\n".join(p.get("text", "") for p in pages)
    out = {}
    for key, pat in [("setup", r"Setup:\s*\n?(.*?)\s*\n"), ("microphone", r"Microphone:\s*\n?(.*?)\s*\n"),
                     ("stimulus", r"Stimulus:\s*\n?(.*?)\s*\n"), ("gating", r"Gating / Smo+thing:\s*\n?(.*?)\s*\n")]:
        m = re.search(pat, text)
        if m:
            out[key] = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"(Figure \d+ Axial Frequency Response[^\n]*)", text)
    if m:
        out["figure"] = re.sub(r"\s+", " ", m.group(1)).strip()
    return out, text


def stated_sensitivity(text):
    """(dB, low Hz, high Hz) from the datasheet's 'SPL@2.83 Vrms/1 m, <frequency>, ref. 20 µPa ... <dB>' line."""
    m = re.search(r"SPL ?@ ?2\.83 ?V ?rms ?/ ?1 ?m, ?([^,]+?) ?, ?ref\.[^\n]*\n\s*([\d.]+)", text)
    if not m:
        return None
    f = m.group(1).replace(" ", "")
    nums = [float(x) * (1000 if "kHz" in f else 1) for x in re.findall(r"[\d.]+", f)]
    if not nums:
        return None
    return float(m.group(2)), nums[0], nums[-1]


def level_at(points, lo, hi):
    """The mean level between lo and hi (for the check only; nothing stored is averaged)."""
    ys = [p["y"] for p in points if lo <= p["x"] <= hi]
    if not ys:
        near = min(points, key=lambda p: abs(math.log(p["x"] / math.sqrt(lo * hi))))
        return near["y"]
    return sum(ys) / len(ys)


def version_of(driver):
    m = re.search(r"(v\d+\.\d+ \([^)]*\))", driver.get("source", ""))
    return m.group(1) if m else ""


def build(probe, db):
    byid = {d["id"]: d for d in db["drivers"]}
    made, skipped = [], []
    for did, rec in probe["drivers"].items():
        if did not in byid:
            skipped.append((did, "no record with this id")); continue
        for dl in rec.get("data", []):
            files = [f for f in dl.get("files", []) if f.get("rows") and angle_of(f["name"]) is not None]
            angles = sorted({angle_of(f["name"]) for f in files})
            if len(angles) < 2 or 0 not in angles:
                skipped.append((did, f"{dl['label']}: {'no off-axis files (on axis only)' if len(angles) < 2 else 'no 0° file'}")); continue
            series, zero_rows, phase = [], 0, False
            digits = max((f.get("digits") or 0) for f in files)
            for a in angles:
                f = next(x for x in files if angle_of(x["name"]) == a)
                pts = [{"x": fx(r[0]), "y": round(r[1], 3)} for r in f["rows"] if r[0] > 0]
                zero_rows += sum(1 for r in f["rows"] if r[0] <= 0)
                phase = phase or (f.get("columns") or max(len(r) for r in f["rows"])) > 2
                series.append({"name": f"{a}°", "points": pts})
            cond, text = conditions_text(rec.get("page", []))
            sens = stated_sensitivity(text)
            zero = series[0]["points"]
            check = ""
            if sens:
                db_, lo, hi = sens
                got = level_at(zero, lo, hi)
                where = f"{lo:g} Hz" if lo == hi else f"{lo:g} to {hi:g} Hz"
                check = f"level check: the 0° file reads {got:.1f} dB at {where} against {db_:.1f} dB the datasheet states at 2.83 V and 1 m ({got - db_:+.1f} dB)"
                if abs(got - db_) > 1.5:
                    skipped.append((did, f"{dl['label']}: {check}; not used")); continue
            header = next((f.get("header") for f in files if f.get("header")), [])
            model = rec["model"]
            steps = sorted({b - a for a, b in zip(angles, angles[1:])})
            spacing = zero[1]["x"] - zero[0]["x"] if len(zero) > 1 else 0
            linear = len(zero) > 3 and spacing > 10 and abs((zero[2]["x"] - zero[1]["x"]) - spacing) < 1e-3 * spacing
            parts = [f"Purifi's measured files from the data download beside the datasheet ({dl['label']}, {dl['href']}): "
                     f"horizontal angles {angles[0]}° to {angles[-1]}°" + (f" in {steps[0]}° steps" if len(steps) == 1 else f" ({', '.join(str(a) + '°' for a in angles)})"),
                     f"the files run from {zero[0]['x']:g} Hz to {zero[-1]['x']:g} Hz",
                     "the rows as the files print them" + (f", written to six significant digits of frequency and 0.001 dB (the files print up to {digits} decimals, far finer than any measurement)" if digits > 3 else "")]
            if cond.get("setup"):
                parts.append(f"datasheet's measurement conditions: {cond['setup']}; microphone: {cond.get('microphone', 'not stated')}; "
                             f"stimulus: {cond.get('stimulus', 'not stated')}; gating and smoothing: {cond.get('gating', 'not stated')}")
            elif cond.get("figure"):
                parts.append(f"the datasheet's conditions for its responses: {cond['figure']}; infinite baffle (2π), as its sensitivity line says")
            if header and "dBV" in " ".join(header):
                parts.append("the files' header names the level column 'dBV'; the levels match the stated sensitivity at 2.83 V, so they are sound pressure in dB")
            if linear:
                parts.append(f"the files have {len(zero)} frequencies {spacing:.1f} Hz apart (a linear spacing), so below about 1 kHz there are few points")
            if check:
                parts.append(check)
            left = []
            if zero_rows:
                left.append("the row at 0 Hz of each file (no place on a logarithmic frequency axis)")
            if phase:
                left.append("the phase column (not drawn)")
            if left:
                parts.append("left out: " + " and ".join(left))
            s = {
                "type": "Off-axis response (Purifi's measured files)",
                "kind": "off-axis",
                "method": "measured files published by the manufacturer, read as numbers",
                "conditions": {"lab": "Purifi", "angles_deg": angles, "distance_mm": 1000, "drive_v": 2.83},
                "source": f"Purifi datasheet data download {model} {version_of(byid[did])}".strip(),
                "confidence": "high",
                "note": "; ".join(parts),
                "chartType": "line",
                "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "SPL", "unit": "dB"}},
                "series": series,
            }
            made.append((did, s))
    return made, skipped


AXES = {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}}


def build_others(probe, db):
    """The impedance file of every download, and the on-axis sound pressure file where the download has no
    off-axis files (the off-axis set's 0° series is that response already)."""
    byid = {d["id"]: d for d in db["drivers"]}
    made, skipped = [], []
    for did, rec in probe["drivers"].items():
        if did not in byid:
            continue
        _, text = conditions_text(rec.get("page", []))
        source = f"Purifi datasheet data download {rec['model']} {version_of(byid[did])}".strip()
        for dl in rec.get("data", []):
            where = f"Purifi's measured file from the data download beside the datasheet ({dl['label']}, {dl['href']})"
            for f in dl.get("files", []):
                if not f.get("rows"):
                    continue
                head = " ".join(f.get("header", []))
                name = f["name"]
                pts = [r for r in f["rows"] if r[0] > 0]
                left = [x for x in (("the row at 0 Hz (no place on a logarithmic frequency axis)" if len(pts) < len(f["rows"]) else ""),
                                    ("the phase column (not drawn)" if (f.get("columns") or max(len(r) for r in pts)) > 2 else "")) if x]
                tail = (f"; the file runs from {fx(pts[0][0]):g} Hz to {fx(pts[-1][0]):g} Hz; the rows as the file prints them" +
                        (f", written to six significant digits of frequency and 0.001 of a unit (the file prints up to {f.get('digits')} decimals)" if (f.get("digits") or 0) > 3 else "") +
                        ("; left out: " + " and ".join(left) if left else ""))
                if re.search(r"\bZ\b|ZMA|Ohm|Zmag", name + " " + head) and angle_of(name) is None:
                    m = re.search(r"Impedance Response @ ?([\d.]+) ?V", text)
                    zmin = re.search(r"Minimum impedance above resonance\s*\n\s*([\d.]+)", text)
                    fs = re.search(r"Resonance freq(?:uency|\.)[^\n]*\n\s*([\d.]+) ?Hz", text)
                    check = ""
                    if zmin and fs:
                        above = [r for r in pts if r[0] > float(fs.group(1)) * 1.5]
                        low = min(above, key=lambda r: r[1]) if above else None
                        if low:
                            check = f"; check: the file's lowest impedance above resonance is {low[1]:.2f} ohm at {low[0]:.0f} Hz, the datasheet states {zmin.group(1)} ohm"
                    zo = re.search(r"Maximum impedance\s*\n\s*([\d.]+)", text)
                    peak = max(pts, key=lambda r: r[1])
                    if zo:
                        check += f"; its peak is {peak[1]:.1f} ohm at {peak[0]:.0f} Hz, the datasheet states a maximum of {zo.group(1)} ohm"
                    rdc = re.search(r"DC resistance(?:, R\s*DC)?\s*\n\s*([\d.]+) ?Ω", text)
                    if rdc:
                        under = [r for r in pts if r[1] < 0.97 * float(rdc.group(1))]
                        if under:
                            check += (f"; below {max(r[0] for r in under):.1f} Hz the file reads under the {rdc.group(1)} ohm DC resistance the datasheet states "
                                      f"(down to {min(r[1] for r in under):.2f} ohm): not possible for a voice coil, so a measurement artefact at the lowest frequencies, kept as published")
                    # the drive level is not stated for the file: the figure's caption names one, but the same download's
                    # sound-pressure file does not follow its figure's caption (it is at 1 V, the figure at 2.83 V)
                    cond = {"lab": "Purifi"}
                    made.append((did, {
                        "type": "Impedance (Purifi's measured file)", "kind": "impedance",
                        "method": "measured file published by the manufacturer, read as numbers", "conditions": cond,
                        "source": source, "confidence": "high",
                        "note": where + ("; the file does not state its drive level" + (f" (the datasheet's impedance figure is drawn at {m.group(1)} V, but the sound-pressure file of a Purifi download need not match its figure's caption)" if m else "")) + check + tail,
                        "chartType": "line", "axes": {**AXES, "y": {"label": "Impedance", "unit": "ohm"}},
                        "series": [{"name": "Z", "points": [{"x": fx(r[0]), "y": round(r[1], 3)} for r in pts]}]}))
                elif re.search(r"SPL", name) and angle_of(name) is None:
                    sens = stated_sensitivity(text)
                    if not sens:
                        skipped.append((did, f"{name}: no stated sensitivity to check the level against")); continue
                    db_, lo, hi = sens
                    got = level_at([{"x": r[0], "y": r[1]} for r in pts], lo, hi)
                    diff = got - db_
                    span = f"{lo:g} Hz" if lo == hi else f"{lo:g} to {hi:g} Hz"
                    if abs(diff) <= 1.5:
                        volts, why = 2.83, f"it reads {got:.1f} dB at {span} against {db_:.1f} dB stated at 2.83 V and 1 m ({diff:+.1f} dB)"
                    elif abs(diff - 20 * math.log10(1 / 2.83)) <= 0.5:
                        volts, why = 1.0, (f"it reads {got:.1f} dB at {span}, {abs(diff):.1f} dB under the {db_:.1f} dB stated at 2.83 V and 1 m, "
                                           f"which is what 1 V gives (−9.0 dB); the drive is stated as 1 V from that (the file's header does not say: it names the level column 'dBV', as the 2.83 V files of other Purifi downloads do)")
                    else:
                        skipped.append((did, f"{name}: reads {got:.1f} dB against {db_:.1f} dB stated; level not known, not used")); continue
                    at1k = min(pts, key=lambda r: abs(math.log(r[0] / 1000)))[1]
                    made.append((did, {
                        "type": f"Axial frequency response @ {volts:g} V (Purifi's measured file)", "kind": "frequency-response",
                        "method": "measured file published by the manufacturer, read as numbers",
                        "conditions": {"lab": "Purifi", "drive_v": volts, "distance_mm": 1000, "angle_deg": 0, "spl_db_1khz": round(at1k, 1)},
                        "source": source, "confidence": "high",
                        "note": where + f"; level: {why}; the datasheet's conditions for its responses: Figure 5 Axial Frequency Response @ 1m, 2.83Vrms, infinite baffle (2π)" + tail,
                        "chartType": "line", "axes": {**AXES, "y": {"label": "SPL", "unit": "dB"}},
                        "series": [{"name": "SPL", "points": [{"x": fx(r[0]), "y": round(r[1], 3)} for r in pts]}]}))
    return made, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", default=str(ROOT / "capture" / "datasheet_probe.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    probe = json.loads(Path(a.probe).read_text())
    dbp = ROOT / "drivers.json"
    db = json.loads(dbp.read_text())
    made, skipped = build(probe, db)
    more, more_skipped = build_others(probe, db)
    made += more
    skipped += more_skipped
    for did, s in made:
        print(f"{did}: {len(s['series'])} angles, {sum(len(x['points']) for x in s['series'])} points; {s['note'][-200:]}")
    for did, why in skipped:
        print(f"not made {did}: {why}")
    if a.write and made:
        byid = {d["id"]: d for d in db["drivers"]}
        for did, s in made:
            d = byid[did]
            d["measurements"] = [m for m in d["measurements"] if not (m.get("source") == s["source"] and m.get("kind") == s["kind"])]
            d["measurements"].append(s)
            d["updated"] = probe["date"]
        tmp = ROOT / "capture" / "_datasheet_candidate.json"
        tmp.write_text(dumps_db(db))
        result = validate([str(tmp), str(ROOT / "drivers_survey_midbass.json")])
        errors = result[0] if isinstance(result, tuple) else result
        tmp.unlink()
        if errors:
            sys.exit("not written, the validator says: " + "; ".join(str(e) for e in errors[:5]))
        dbp.write_text(dumps_db(db))
        print(f"{len(made)} set(s) written")


if __name__ == "__main__":
    main()
