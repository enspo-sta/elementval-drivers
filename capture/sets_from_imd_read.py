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
            tones = {round(x["f"], 3): x for x in c.get("tones") or []}
            up = tones.get(round(t.get("f2", -1), 3)) or {}
            if up.get("level") is None:
                waiting.append((did, name, "the upper tone was not found on the chart")); continue
            chk = c.get("check") or {}
            if chk.get("difference_db") is not None and abs(chk["difference_db"]) > 1.5:
                waiting.append((did, name, f"the reading differs from the chart's printed readout by {chk['difference_db']} dB")); continue
            pts = []
            for f, x in sorted(tones.items()):
                if x.get("level") is not None:
                    pts.append({"x": num(f), "y": round(x["level"], 1), "label": "f1 (lower tone)" if f == round(t["f1"], 3) else "f2 (upper tone)"})
            for p in c.get("products") or []:
                pts.append({"x": num(p["f"]), "y": p["level"], "label": f"{product_name(p['m'], p['n'])} ({ORD[p['order']]})"})
            pts.sort(key=lambda p: p["x"])
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
            note = [f"read automatically from {c['url']} on GitHub (capture/imd_read.py): axes from the chart's grid and labels, "
                    "the spectrum by colour, its highest point within 3 pixels of each tone and product"]
            if chk:
                if chk.get("difference_db") is not None:
                    note.append(f"check against the cursor readout the chart prints: {chk['f']} Hz, printed {chk['stated_db']} dB, "
                                f"read {chk['read_db']} dB, difference {chk['difference_db']} dB")
                else:
                    note.append(f"the chart's cursor readout ({chk['f']} Hz, {chk['stated_db']} dB) is off its scale, so no check")
            else:
                note.append("no cursor readout found on the chart to check against")
            if c.get("below_floor"):
                note.append(f"{c['below_floor']} product(s) less than 6 dB above the noise floor left out")
            if f1 not in [p["x"] for p in pts]:
                note.append(f"the lower tone ({f1} Hz) was not found on the chart")
            if not t.get("ratio"):
                note.append("the tone ratio is not stated in the file name")
            if "distance_mm" not in cond:
                note.append("the microphone distance is not stated in the file name")
            ratio = f", {t['ratio']}" if t.get("ratio") else ""
            made.append((did, {
                "type": f"Intermodulation {f1} + {f2} Hz{ratio}, {what}",
                "kind": "imd-products",
                "method": f"two-tone spectrum {f1} + {f2} Hz, automated pixel reading (GitHub)",
                "conditions": cond,
                "source": f"HiFiCompass ({name}, automated reading)",
                "confidence": "medium",
                "note": "; ".join(note),
                "chartType": "bar",
                "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "linear"}, "y": {"label": "Level", "unit": "dB (the chart's scale)"}},
                "series": [{"name": "tones and products", "points": pts}],
                "file": name,
                **({"check": {"cursor": chk}} if chk else {}),
            }))
    return made, waiting


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
        print(f"{did}: {s['type']} {len(s['series'][0]['points'])} bars; {s['note'][-140:]}")
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
