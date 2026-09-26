#!/usr/bin/env python3
"""Measurement sets from capture/chart_read.json (curves read on GitHub from HiFiCompass chart images).

For every chart read without error: the drive voltage, distance and high-pass filter from the file name
(m74a-6_315mm_2v83_hpf2-300.png), the kind from the chart type, the curves as series. A response chart
becomes one frequency-response set (its 2.83 V curve at 1 kHz is compared with the page's stated
sensitivity, and the difference is written in the note); an impedance chart one impedance set; a
harmonics or current chart one hd-frequency or hd-current set only when the chart's legend names the
colours (H2, H3, ...), else it is listed as waiting. Every set says it was read automatically
(confidence "medium") so it can be spot-checked by eye later. Nothing is added twice: a set from the
same file replaces the earlier one.

  python3 capture/sets_from_chart_read.py [--write]
"""
import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from validate_db import validate  # noqa: E402

KIND = {"response": "frequency-response", "near-response": "frequency-response", "impedance": "impedance", "harmonics": "hd-frequency", "current": "hd-current"}
TYPE = {"response": "Axial frequency response", "near-response": "Near-field frequency response", "impedance": "Impedance", "harmonics": "HD (orders) vs frequency", "current": "Voice-coil current HD vs frequency"}
AXES = {"frequency-response": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "SPL", "unit": "dB"}},
        "impedance": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Impedance", "unit": "ohm"}},
        "hd-frequency": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Harmonic ratio", "unit": "dB re fund"}},
        "hd-current": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": "Current harmonic", "unit": "dB"}}}


def volts(name):
    m = re.search(r"_(\d+)v(\d*)(?:_|hd|\.)", name)
    if not m:
        return None
    return float(m.group(1) + ("." + m.group(2) if m.group(2) else ""))


def conditions(name):
    c = {}
    v = volts(name)
    if v is not None:
        c["drive_v"] = v
    m = re.search(r"_(\d+)mm_", name)
    if m:
        c["distance_mm"] = int(m.group(1))
    m = re.search(r"hpf(\d)-(\d+)", name)
    if m:
        c["hpf"] = f"HPF{m.group(1)}-{m.group(2)}"
    m = re.search(r"hpf(\d{2,})hz", name)
    if m:
        c["hpf"] = f"HPF {m.group(1)} Hz"
    if "nosmoothing" in name:
        c["smoothing"] = "none"
    if re.search(r"_0(grad|deg)", name):
        c["angle_deg"] = 0
    c["lab"] = "HiFiCompass"
    return c


def series_names(chart):
    """Colour -> harmonic name from the legend (H2, H3, H4, H5, THD), when the legend was read."""
    names = {}
    for wd in chart.get("legend") or []:
        t = wd["text"].upper().strip(",;:")
        if re.fullmatch(r"H[2-9]|THD", t) and wd.get("colour"):
            names[wd["colour"]] = t
    return names


def close(a, b, tol=90):
    return sum(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5)) <= tol


def level_by_volts(charts):
    """Drive voltage -> sound pressure at 1 kHz read from that voltage's response chart (HiFiCompass
    states its levels at 1 m: the response chart's scale is that level)."""
    out = {}
    for ch in charts:
        if ch.get("type") == "response" and ch.get("curves") and not ch.get("error"):
            v = volts(ch["file"])
            cv = max(ch["curves"], key=lambda c: c["pixels"])
            at1k = [p["y"] for p in cv["points"] if 900 <= p["x"] <= 1100]
            if v is not None and at1k:
                out[v] = round(statistics.mean(at1k), 1)
    return out


def name_across_types(charts):
    """A curve the legend reading left unnamed takes the name the same colour has in the driver's other charts
    (the HiFiCompass template draws H2 blue, H3 black and H5 red on every harmonics and current chart)."""
    dist = lambda a, b: sum(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    known = {}
    for ch in charts:
        for cv in ch.get("curves") or []:
            if cv.get("name") and not cv.get("name_from"):
                known.setdefault(cv["colour"], set()).add(cv["name"])
    for ch in charts:
        if ch.get("type") not in ("harmonics", "current"):
            continue
        taken = {cv["name"] for cv in ch.get("curves") or [] if cv.get("name")}
        for cv in ch.get("curves") or []:
            if cv.get("name"):
                continue
            near = sorted((dist(cv["colour"], k), k) for k in known)
            if near and near[0][0] <= 30 and len(known[near[0][1]]) == 1:
                nm = next(iter(known[near[0][1]]))
                if nm not in taken:
                    cv["name"], cv["name_from"] = nm, "the legend of another chart of this driver"
                    taken.add(nm)


def build(read, db):
    byid = {d["id"]: d for d in db["drivers"]}
    made, waiting = [], []
    for did, charts in read["drivers"].items():
        d = byid.get(did)
        if not d:
            continue
        name_across_types(charts)
        levels = level_by_volts(charts)
        for ch in charts:
            if ch.get("error") or not ch.get("curves"):
                waiting.append((did, ch["file"], ch.get("error") or "no curve read")); continue
            ctype, name = ch["type"], ch["file"]
            typed_note = None
            named = [cv for cv in ch["curves"] if cv.get("name") in ("H2", "H3", "H4", "H5")]
            if ctype == "near-response" and len(named) >= 2 and max(p["y"] for cv in named for p in cv["points"]) < -10:
                # a near-field chart whose name does not say what it holds (ptt10.0x04-nab-02_20mm_4v.png in the folder
                # afc520/): several curves in the harmonic colours, all well below the fundamental, are harmonics
                ctype = "harmonics"
                typed_note = ("typed from its content, as the file name does not say: " + ", ".join(cv["name"] for cv in named) +
                              " in the harmonic colours of this driver's other charts, all below -10 dB; the same folder (afc520/) holds the "
                              "other drivers' near-field harmonic charts, named …_20mm_2v83_hd.png")
            kind = KIND.get(ctype)
            if not kind:
                continue
            xa, ya = ch.get("x_axis") or [0, 0], ch.get("y_axis") or [0, 0]
            if not (0.001 < xa[1] < 0.006) or not (ya[1] < 0):
                waiting.append((did, name, f"axis fit not credible (x slope {xa[1]:.5f} per px, y slope {ya[1]:.4f} per px)")); continue
            cond = conditions(name)
            # what the chart is, beyond kind and voltage: an impedance chart's full-scale, a near-field distance, no smoothing
            extra = []
            m = re.search(r"_(\d+)_ohm", name)
            if m and ctype == "impedance":
                extra.append(f"chart to {m.group(1)} ohm")
            if cond.get("distance_mm") and cond["distance_mm"] < 100:
                extra.append(f"near field {cond['distance_mm']} mm")
            if cond.get("smoothing") == "none":
                extra.append("no smoothing")
            note = [f"read automatically from {ch['url']} on GitHub (capture/chart_read.py): axes from the chart's grid and labels, curve by colour, 1/24 octave"]
            if typed_note:
                note.append(typed_note)
            if ch["type"] == "near-response" and ctype == "near-response":
                note.append("a near-field response on the chart's own dB scale (not sound pressure at 1 m), kept apart from the 315 mm responses")
            scale = re.search(r"_(\d+)_ohm", name)
            for c in ch.get("checks", []):
                if "peak" in c.get("check", "") and scale and c.get("read_ohm", 0) >= 0.97 * float(scale.group(1)):
                    note.append(f"the resonance peak lies above this chart's {scale.group(1)} ohm scale (clipped), so it is not checked against Fs {c.get('stated_fs')}")
                    continue
                note.append(", ".join(f"{k.replace('_', ' ')} {v}" for k, v in c.items()))
                if "1 kHz" in c.get("check", "") and "tweeter" in (d.get("role") or ""):
                    note.append("a tweeter's stated sensitivity is an average over its band, so a difference at 1 kHz is expected")
            for cv in ch["curves"]:
                if cv.get("clipped_top"):
                    note.append(f"{cv.get('name') or cv['colour']}: runs above the chart's top line in {cv['clipped_top']} pixel column(s); "
                                "those stretches are left out (the chart cuts the curve off there)")
                if cv.get("gaps"):
                    note.append(f"{cv.get('name') or cv['colour']}: not visible in the chart between " + ", ".join(f"{g[0]:g} and {g[1]:g} Hz" for g in cv["gaps"]) + " (no points there)")
                if cv.get("name_from"):
                    note.append(f"{cv['name']} named after {cv['name_from']}")
            if kind in ("hd-frequency", "hd-current"):
                # the reader attaches the legend's name to each curve; a curve without one is left out and noted
                series = [{"name": cv["name"], "points": cv["points"]} for cv in ch["curves"] if cv.get("name") and cv.get("lines_per_column", 1) <= 1.5]
                unnamed = [cv["colour"] for cv in ch["curves"] if not cv.get("name")]
                if not series:
                    waiting.append((did, name, f"no curve carries a legend name: {[(w['text'], w['colour']) for w in ch.get('legend', []) if '(' in w['text']][:8]}")); continue
                if unnamed:
                    note.append(f"curves without a legend name left out: {', '.join(unnamed)}")
                series.sort(key=lambda s: s["name"])
                # the level of a harmonic set: the sound pressure the same drive voltage gives at 1 kHz on the response chart
                v = cond.get("drive_v")
                if kind == "hd-frequency":
                    if v in levels:
                        cond["spl_db"] = levels[v]
                        note.append(f"level {levels[v]} dB at 1 m = the {v:g} V response read at 1 kHz")
                    elif levels and v:
                        # no response chart at this voltage: the nearest voltage's response at 1 kHz, scaled by the
                        # voltage ratio (20 log10), which is how a sensitivity is restated for another voltage
                        v0 = min(levels, key=lambda x: abs(math.log(x / v)))
                        cond["spl_db"] = round(levels[v0] + 20 * math.log10(v / v0), 1)
                        cond["spl_note"] = f"level from the {v0:g} V response at 1 kHz ({levels[v0]} dB) scaled by 20 log10({v:g}/{v0:g})"
                        note.append(cond["spl_note"])
                    else:
                        waiting.append((did, name, f"no response chart to take the level from")); continue
            elif kind == "frequency-response":
                cv = max(ch["curves"], key=lambda c: c["pixels"])
                if cv.get("lines_per_column", 1) > 1.5:
                    waiting.append((did, name, "more than one line in the response colour")); continue
                series = [{"name": "SPL", "points": cv["points"]}]
                at1k = [p["y"] for p in cv["points"] if 900 <= p["x"] <= 1100]
                if at1k:
                    cond["spl_db_1khz"] = round(statistics.mean(at1k), 1)
            else:
                cv = max(ch["curves"], key=lambda c: c["pixels"])
                series = [{"name": "Z", "points": cv["points"]}]
            # how well the reading sits on the chart: every read point put back on the image (chart_read.py)
            shares = {s["name"]: cv.get("on_curve") for s in series for cv in ch["curves"] if cv.get("points") is s["points"] and cv.get("on_curve") is not None}
            if shares:
                note.append("check on the image: " + ", ".join(f"{k} {round(100 * v)} %" for k, v in shares.items()) + " of the read points lie on the drawn curve (within 2 px)")
            cal = None
            if ch.get("calibration"):
                cal = dict(ch["calibration"], image=ch["url"],
                           colours={s["name"]: next((cv["colour"] for cv in ch["curves"] if cv.get("points") is s["points"]), None) for s in series})
            made.append((did, {"type": TYPE[ctype] + (f" @ {cond['drive_v']:g} V" if cond.get("drive_v") is not None else "") + (f" ({', '.join(extra)})" if extra else ""), "kind": kind,
                              "method": "automated pixel reading (GitHub), calibrated from the chart's own grid and labels",
                              "conditions": cond, "source": f"HiFiCompass ({name}, automated reading)", "confidence": "medium",
                              "note": "; ".join(note), "chartType": "line", "axes": AXES[kind], "series": series, "file": name,
                              **({"calibration": cal} if cal else {}),
                              **({"check": {"on_curve": shares}} if shares else {})}))
    return made, waiting


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--read", default=str(ROOT / "capture" / "chart_read.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    read = json.loads(Path(a.read).read_text())
    dbp = ROOT / "drivers.json"
    db = json.loads(dbp.read_text())
    made, waiting = build(read, db)
    for did, s in made:
        print(f"{did}: {s['type']} ({s['kind']}) {len(s['series'])} series, {len(s['series'][0]['points'])} points; {s['note'][:160]}")
    for did, f, why in waiting:
        print(f"waiting {did} {f}: {why}")
    if a.write and made:
        byid = {d["id"]: d for d in db["drivers"]}
        for did, s in made:
            d = byid[did]
            d["measurements"] = [m for m in d["measurements"] if m.get("source") != s["source"]]
            d["measurements"].append(s)
            d["updated"] = read["date"]
        # an earlier hand capture of the same HiFiCompass harmonics (a composite cut at 500 Hz, a curve normalised
        # to one level) and the band figures taken from it are superseded once every level has been read in full:
        # kept on the driver page as captured, left out of Compare, Simulate and the cross-checks
        sys.path.insert(0, str(ROOT / "watch"))
        from common import families_of, load_config
        cfg = load_config()
        for did in sorted({did for did, s in made if s["kind"] == "hd-frequency"}):
            for m in byid[did]["measurements"]:
                if m.get("superseded_by") or "automated" in str(m.get("method", "")):
                    continue
                if (families_of(m.get("source"), cfg) or [""])[0] == "HiFiCompass" and m.get("kind") in ("hd-frequency", "thd-bands"):
                    m["superseded_by"] = (f"the automatic reading of the same HiFiCompass harmonic charts on {read['date']}, "
                                          "every drive level at 1/24 octave over the range each chart shows (capture/chart_read.py)")
                    print(f"superseded {did}: {m['type']} ({m.get('source')})")
        tmp = ROOT / "capture" / "_chart_read_candidate.json"
        tmp.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n")
        result = validate([str(tmp), str(ROOT / "drivers_survey_midbass.json")])
        errors = result[0] if isinstance(result, tuple) else result
        tmp.unlink()
        if errors:
            sys.exit("not written, the validator says: " + "; ".join(str(e) for e in errors[:5]))
        dbp.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n")
        print(f"{len(made)} set(s) written")


if __name__ == "__main__":
    main()
