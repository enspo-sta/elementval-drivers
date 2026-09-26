#!/usr/bin/env python3
"""Measurement sets from capture/imd_read.json (HiFiCompass two-tone intermodulation spectra read on GitHub).

For every chart read without error: one set of kind imd-products. Its bars are the spectrum's peaks at the
two tones and at every product up to the 5th order that stands at least 6 dB above the noise floor around
it, in dB on the chart's own scale (as the chart shows them; Compare gives the products relative to the
upper tone). The test comes from the file name: the tones, their ratio, and the low tone's peak excursion
(x_pk_mm) or the drive voltage (drive_v), which is the set's level. Every set says it was read
automatically (confidence "medium"); the chart's printed cursor readout is compared with the reading at
the same frequency and the difference written in the note. A chart whose check differs by more than
1.5 dB, or whose upper tone was not found, is listed as waiting and not stored. Nothing is added twice: a
set from the same file replaces the earlier one.

  python3 capture/sets_from_imd_read.py [--write]
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from validate_db import validate  # noqa: E402

ORD = {1: "tone", 2: "2nd order", 3: "3rd order", 4: "4th order", 5: "5th order"}


def num(v):
    return int(v) if float(v).is_integer() else v


def product_name(m, n):
    """m·f1 + n·f2 written out: "f2 − f1", "2·f1 + f2", "3·f1"."""
    t = lambda k, f: f if abs(k) == 1 else f"{abs(k)}·{f}"
    if n == 0:
        return t(m, "f1")
    if m == 0:
        return t(n, "f2")
    if m > 0 and n > 0:
        return f"{t(m, 'f1')} + {t(n, 'f2')}"
    return f"{t(n, 'f2')} − {t(m, 'f1')}" if n > 0 else f"{t(m, 'f1')} − {t(n, 'f2')}"


HARM = {2: "2nd", 3: "3rd"}


def one_tone(c, t):
    """A set of kind hd-spectrum from a one-tone chart, or the reason it waits."""
    name = c.get("file", "")
    tone = (c.get("tones") or [{}])[0]
    level = tone.get("level")
    if level is None:
        return None, "the tone was not found on the chart"
    chk = dict(c.get("check") or {})
    px = [r[2] for r in (chk.get("column") or {}).get("pixels") or []]
    note = [f"read from {c['url']}"]
    if px and chk.get("difference_db") is not None and abs(chk["difference_db"]) <= 3 and sum(v == "#ff0000" for v in px) >= 0.8 * len(px):
        note.append(f"the chart's red cursor line covers the tone's peak, whose top is hidden (read {level:.2f} dB beside it); "
                    f"its level is the {chk['stated_db']} dB the chart prints")
        level = chk["stated_db"]
        chk.update(difference_db=None, note="the cursor line covers the tone's peak; the printed level is used")
    elif chk.get("difference_db") is not None:
        if abs(chk["difference_db"]) > 1.5:
            return None, f"the reading differs from the chart's printed readout by {chk['difference_db']} dB"
        note.append(f"check: the chart prints {chk['stated_db']} dB at {chk['f']} Hz, read {chk['read_db']} dB ({chk['difference_db']:+.2f} dB)")
    elif chk:
        note.append(f"no check: {chk.get('note') or 'the cursor readout could not be used'}")
    else:
        note.append("no check: no cursor readout found on the chart")
    if c.get("below_floor"):
        note.append(f"{c['below_floor']} harmonic(s) under the noise floor left out")
    f0 = num(t["f0"])
    pts = [{"x": f0, "y": round(level, 2), "label": "tone"}]
    pts += [{"x": num(p["f"]), "y": p["level"], "label": f"H{p['order']} ({HARM.get(p['order'], str(p['order']) + 'th')} harmonic)"} for p in c.get("products") or []]
    cond = {"f0": f0, "drive_v": num(t["drive_v"]), "distance_mm": t["distance_mm"], "lab": "HiFiCompass"}
    return {
        "type": f"Harmonics of one tone, {f0} Hz at {num(t['drive_v'])} V (microphone at {t['distance_mm']} mm)",
        "kind": "hd-spectrum",
        "method": f"one-tone spectrum {f0} Hz, automated pixel reading on GitHub (capture/imd_read.py: axes from the chart's grid and labels, the spectrum by colour, its highest point within 3 pixels of the tone and each harmonic)",
        "conditions": cond,
        "source": f"HiFiCompass ({name}, automated reading)",
        "confidence": "medium",
        "note": "; ".join(note),
        "chartType": "bar",
        "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "linear"}, "y": {"label": "Level", "unit": "dB (the chart's scale)"}},
        "series": [{"name": "tone and harmonics", "points": sorted(pts, key=lambda p: p["x"])}],
        "file": name,
        **({"check": {"cursor": {k: v for k, v in chk.items() if k != "column"}}} if chk else {}),
    }, None


def build(read, db):
    byid = {d["id"]: d for d in db["drivers"]}
    made, waiting = [], []
    for did, charts in read["drivers"].items():
        if did not in byid:
            waiting.append((did, "", "no record with this id")); continue
        for c in charts:
            name = c.get("file", "")
            t = c.get("test") or {}
            if c.get("error"):
                waiting.append((did, name, c["error"])); continue
            if "f0" in t:
                st, why = one_tone(c, t)
                if st:
                    made.append((did, st))
                else:
                    waiting.append((did, name, why))
                continue
            tones = {round(x["f"], 3): x for x in c.get("tones") or []}
            up = tones.get(round(t.get("f2", -1), 3)) or {}
            if up.get("level") is None:
                waiting.append((did, name, "the upper tone was not found on the chart")); continue
            chk = dict(c.get("check") or {})
            covered = None
            col = chk.get("column") or {}
            px = [r[2] for r in col.get("pixels") or []]
            if px and chk.get("difference_db") is not None and abs(chk["difference_db"]) <= 3 and sum(v == "#ff0000" for v in px) >= 0.8 * len(px):
                # (within 3 dB: further than that the flanks beside the line cannot belong to the printed peak, and the
                # chart waits like any other that disagrees with its readout)
                # the chart's red cursor line is drawn over the tone's own column and hides the top of its peak (the
                # columns beside it show the flanks only): the tone's level is then the one the chart prints
                near = min(tones, key=lambda f: abs(f - chk["f"]))
                covered = (near, tones[near].get("level"))
                tones[near] = dict(tones[near], level=chk["stated_db"])
                chk.update(difference_db=None, note=f"the chart's red cursor line covers the {num(near)} Hz tone's peak, whose top "
                           f"is hidden (read {covered[1]:.2f} dB beside it); its level is the {chk['stated_db']} dB the chart prints")
                up = tones.get(round(t.get("f2", -1), 3)) or {}
            if chk.get("difference_db") is not None and abs(chk["difference_db"]) > 1.5:
                waiting.append((did, name, f"the reading differs from the chart's printed readout by {chk['difference_db']} dB")); continue
            pts = []
            for f, x in sorted(tones.items()):
                if x.get("level") is not None:
                    pts.append({"x": num(f), "y": round(x["level"], 2), "label": "f1 (lower tone)" if f == round(t["f1"], 3) else "f2 (upper tone)"})
            harm, both = [], []
            for p in c.get("products") or []:
                # every way (m, n) up to the 5th order of reaching this frequency: when the upper tone is a whole
                # multiple of the lower (2 + 10 kHz), a harmonic of one tone and a mixed product fall together and the
                # bar holds both; it is named by every way and kept out of the intermodulation series
                ways = [(m, n) for m in range(-5, 6) for n in range(-5, 6) if 2 <= abs(m) + abs(n) <= 5
                        and abs(m * t["f1"] + n * t["f2"] - p["f"]) < 1e-6]
                pure = [w for w in ways if w[0] == 0 or w[1] == 0]
                mixed = [w for w in ways if w[0] != 0 and w[1] != 0]
                name_of = lambda w: f"{product_name(*w)} ({ORD[abs(w[0]) + abs(w[1])]})"
                bar = {"x": num(p["f"]), "y": p["level"], "label": " = ".join(name_of(w) for w in sorted(ways, key=lambda w: abs(w[0]) + abs(w[1])))}
                (both if pure and mixed else harm if pure else pts).append(bar)
            pts.sort(key=lambda p: p["x"]); harm.sort(key=lambda p: p["x"]); both.sort(key=lambda p: p["x"])
            f1, f2 = num(t["f1"]), num(t["f2"])
            cond = {"f1": f1, "f2": f2}
            if t.get("ratio"):
                cond["ratio"] = t["ratio"]
            if isinstance(t.get("x_pk_mm"), (int, float)):
                cond["x_pk_mm"] = num(t["x_pk_mm"]); what = f"low tone {num(t['x_pk_mm'])} mm peak excursion"
            elif isinstance(t.get("drive_v"), (int, float)):
                cond["drive_v"] = num(t["drive_v"]); what = f"{num(t['drive_v'])} V per tone"
            else:
                waiting.append((did, name, "the level (excursion or voltage) is not in the file name")); continue
            m = re.search(r"_(\d+)mm_", name)
            if m:
                cond["distance_mm"] = int(m.group(1))
            cond["lab"] = "HiFiCompass"
            # short: the same card lists one note per level (how the reading works is in the method and in the
            # kind's note in schema/kinds.json)
            note = [f"read from {c['url']}"]
            if chk and chk.get("difference_db") is not None:
                note.append(f"check: the chart prints {chk['stated_db']} dB at {chk['f']} Hz, read {chk['read_db']} dB ({chk['difference_db']:+.2f} dB)")
            elif covered:
                note.append(chk["note"])
            elif chk:
                note.append(f"no check: {chk.get('note') or 'the cursor readout could not be used'}")
            else:
                note.append("no check: no cursor readout found on the chart")
            if c.get("below_floor"):
                note.append(f"{c['below_floor']} product(s) under the noise floor left out")
            if f1 not in [p["x"] for p in pts]:
                note.append(f"lower tone ({f1} Hz) not found")
            if not t.get("ratio"):
                note.append("tone ratio not stated")
            elif "to1" not in name.lower():
                note.append(f"ratio {t['ratio']} from the voltage of each tone in the file name")
            if both:
                note.append(f"{len(both)} bar(s) where a harmonic of one tone and an intermodulation product fall at the same frequency "
                            "(the upper tone is a whole multiple of the lower): kept apart, not counted as intermodulation")
            if "distance_mm" not in cond:
                note.append("microphone distance not stated")
            ratio = f", {t['ratio']}" if t.get("ratio") else ""
            made.append((did, {
                "type": f"Intermodulation {f1} + {f2} Hz{ratio}, {what}",
                "kind": "imd-products",
                "method": f"two-tone spectrum {f1} + {f2} Hz, automated pixel reading on GitHub (capture/imd_read.py: axes from the chart's grid and labels, the spectrum by colour, its highest point within 3 pixels of each tone and product)",
                "conditions": cond,
                "source": f"HiFiCompass ({name}, automated reading)",
                "confidence": "medium",
                "note": "; ".join(note),
                "chartType": "bar",
                "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "linear"}, "y": {"label": "Level", "unit": "dB (the chart's scale)"}},
                # the intermodulation products (both tones take part) first: Compare sums that series; the
                # harmonics of each tone alone (2·f1, 3·f1, 2·f2 ...) are distortion of one tone and kept apart
                "series": [{"name": "tones and intermodulation products", "points": pts}]
                          + ([{"name": "harmonics of each tone", "points": harm}] if harm else [])
                          + ([{"name": "a harmonic and a product at the same frequency", "points": both}] if both else []),
                "file": name,
                **({"check": {"cursor": {k: v for k, v in chk.items() if k != "column"}}} if chk else {}),
            }))
    level_check(made)
    return made, waiting


def level_check(made):
    """Across the levels of one test of one driver the tones should rise with the drive: by 20 log10 of the voltage
    ratio, or of the excursion ratio (a motor below its limits). Where a step between neighbouring levels rises less
    than half of that, or falls, the chart's scale is likely set per measurement, so only values relative to a tone
    compare across levels; the notes of every set of that test say so."""
    groups = {}
    for did, s in made:
        c = s["conditions"]
        key = "x_pk_mm" if isinstance(c.get("x_pk_mm"), (int, float)) else "drive_v" if isinstance(c.get("drive_v"), (int, float)) else None
        if s["kind"] != "imd-products" or not key:
            continue
        groups.setdefault((did, c["f1"], c["f2"], key), []).append(s)
    for (did, f1, f2, key), sets in groups.items():
        if len(sets) < 2:
            continue
        sets.sort(key=lambda s: s["conditions"][key])
        up = lambda s: next(p["y"] for p in s["series"][0]["points"] if p["x"] == s["conditions"]["f2"])
        unit = "mm" if key == "x_pk_mm" else "V"
        bad = []
        for lo, hi in zip(sets, sets[1:]):
            a, b = lo["conditions"][key], hi["conditions"][key]
            expect, rise = 20 * math.log10(b / a), up(hi) - up(lo)
            if expect >= 1 and rise < expect / 2:
                bad.append(f"{a:g} to {b:g} {unit}: {rise:+.1f} dB where {expect:+.1f} dB is expected")
        if bad:
            for s in sets:
                s["note"] += ("; the upper tone does not rise with the drive as expected (" + ", ".join(bad) + "): the chart's scale looks "
                              "set per measurement, so compare values relative to the tone (as Compare does), not the tone levels themselves")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--read", default=str(ROOT / "capture" / "imd_read.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    read = json.loads(Path(a.read).read_text())
    dbp = ROOT / "drivers.json"
    db = json.loads(dbp.read_text())
    made, waiting = build(read, db)
    for did, s in made:
        print(f"{did}: {s['type']} {sum(len(x['points']) for x in s['series'])} bars; {s['note'][-140:]}")
    for did, f, why in waiting:
        print(f"waiting {did} {f}: {why}")
    if a.write and made:
        byid = {d["id"]: d for d in db["drivers"]}
        for did, s in made:
            d = byid[did]
            d["measurements"] = [m for m in d["measurements"] if m.get("source") != s["source"]]
            d["measurements"].append(s)
            d["updated"] = read["date"]
        tmp = ROOT / "capture" / "_imd_read_candidate.json"
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
