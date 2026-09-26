#!/usr/bin/env python3
"""Turn off-axis charts read from a lab's page (capture/datasheet_probe.json: the chart reader's curves and the colour of
the legend line beside each printed angle) into sets in drivers.json. Used for Erin's Audio Corner's driver tests: a
"Horizontal Frequency Response" chart (sound pressure at 0°, 15°, 30° and 60°) and the same normalized against 0°.

Each curve is named by its legend line's colour: black, red, green or blue (a thin line's legend swatch is drawn
lighter, so the colour family counts, not the exact shade). Where lines lie on top of each other the lower one is
hidden, so a curve has gaps there (no points; the note lists them). Checks written into the note: the 0° response's
mean from 300 to 1000 Hz against the "Mean SPL" the chart prints, and each angle relative to 0° from the sound-pressure
chart against the normalized chart.

  python3 capture/sets_from_page_charts.py            # show what would be made
  python3 capture/sets_from_page_charts.py --write    # write drivers.json (after the validator passes)
"""
import argparse
import json
import math
import re
import statistics
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from common import dumps_db  # noqa: E402  (the database's layout: each curve's points on one line)
from validate_db import validate  # noqa: E402

LAB = {"erin": "Erin's Audio Corner"}
NAMES = {"k": "black", "r": "red", "g": "green", "b": "blue"}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def family(h, strict=True):
    """The colour family of a drawn colour: 'k' (black or dark grey) or the strongest of red, green and blue.
    strict: only saturated or dark colours count (a light tint is a legend swatch or a shaded area, not a curve)."""
    r, g, b = hexrgb(h)
    if max(r, g, b) < 90:
        return "k"
    if strict and min(r, g, b) > 70:
        return None
    if max(r, g, b) - min(r, g, b) < 60:
        return None
    return "rgb"[(r, g, b).index(max(r, g, b))]


def curve_fn(points):
    p = sorted((q["x"], q["y"]) for q in points)
    xs = [math.log10(x) for x, _ in p]

    def f(x):
        lx = math.log10(x)
        if not p or lx < xs[0] or lx > xs[-1]:
            return None
        for i in range(1, len(p)):
            if xs[i] >= lx:
                # a gap wider than a third of an octave is not bridged
                if xs[i] - xs[i - 1] > math.log10(2) / 3 + 1e-9:
                    return None
                t = 0 if xs[i] == xs[i - 1] else (lx - xs[i - 1]) / (xs[i] - xs[i - 1])
                return p[i - 1][1] + t * (p[i][1] - p[i - 1][1])
        return p[-1][1]
    return f


def gaps_of(points, factor=2 ** (1 / 3)):
    xs = sorted(q["x"] for q in points)
    return [(a, b) for a, b in zip(xs, xs[1:]) if b / a > factor]


def islands(points, factor=2 ** (1 / 3), least=3):
    """(kept, dropped): runs of fewer than `least` points cut off by gaps on both sides are stray marks the reader
    caught (a tick, a letter's edge), not the curve."""
    p = sorted(points, key=lambda q: q["x"])
    runs, cur = [], []
    for q in p:
        if cur and q["x"] / cur[-1]["x"] > factor:
            runs.append(cur); cur = []
        cur.append(q)
    if cur:
        runs.append(cur)
    if len(runs) < 2:
        return p, []
    kept = [q for r in runs if len(r) >= least for q in r]
    dropped = [q for r in runs if len(r) < least for q in r]
    return kept, dropped


def fmt_hz(f):
    return f"{f / 1000:.1f} kHz" if f >= 1000 else f"{f:.0f} Hz"


def signed(v):
    return "0.0" if abs(v) < 0.05 else f"{v:+.1f}"


def chart_series(img):
    """[(angle, colour, points, columns)] from one image's reading, each angle's curve chosen by its legend colour."""
    ds = img.get("describe", {})
    curves = (ds.get("off_axis_read") or {}).get("curves") or []
    by_angle = {}
    for sw in ds.get("legend_swatches", []):
        if sw.get("swatch"):
            by_angle.setdefault(sw["angle"], family(sw["swatch"]["colour"], strict=False))
    out = []
    for angle, fam in sorted(by_angle.items()):
        if fam is None:
            continue
        cands = [c for c in curves if c.get("points") and family(c["colour"]) == fam]
        if not cands:
            out.append((angle, NAMES[fam], [], 0))
            continue
        best = max(cands, key=lambda c: c.get("columns") or 0)
        kept, dropped = islands(best["points"])
        best["stray"] = dropped
        best["kept"] = kept
        out.append((angle, NAMES[fam], kept, best.get("columns") or 0))
    return out


def printed_mean(img):
    words = img.get("describe", {}).get("words", [])
    for i, w in enumerate(words):
        if w["text"] == "Mean":
            for nxt in words[i + 1:i + 5]:
                m = re.match(r"([\d.]+)dB", nxt["text"])
                if m:
                    return float(m.group(1))
    return None


def build(probe, db):
    byid = {d["id"]: d for d in db["drivers"]}
    made, skipped = [], []
    for did, pg in probe.get("pages", {}).items():
        lab = LAB.get(pg.get("site"))
        if not lab or did not in byid:
            continue
        page = next((r for r in pg.get("found", []) if r.get("url") and "error" not in r), None)
        text = (page or {}).get("text", "")
        stated = re.search(r"Frequency Response data is generated using ([^.]*)\.[^.]*?\.\s*Data is represented at ([\d.]+) ?v ?/ ?([\d.]+) ?m", text, re.I)
        imgs = [i for i in probe.get("images", []) if i.get("id") == did and "describe" in i]
        charts = {}
        for img in imgs:
            name = urllib.parse.unquote(img["url"].rsplit("/", 1)[-1])
            if re.search(r"Horizontal[ _]FR[ _]Normalized", name, re.I):
                charts["off-axis-normalized"] = (img, name)
            elif re.search(r"Horizontal[ _]FR\.", name, re.I):
                charts["off-axis"] = (img, name)
        read = {}
        for kind, (img, name) in charts.items():
            ser = chart_series(img)
            if len([s for s in ser if s[2]]) < 2:
                skipped.append((did, f"{name}: fewer than two angles read")); continue
            read[kind] = (img, name, ser)
        # each angle relative to 0°: from the sound-pressure chart, and as the normalized chart draws it
        rel = {}
        if "off-axis" in read:
            fs = {a: curve_fn(p) for a, _, p, _ in read["off-axis"][2] if p}
            if 0 in fs:
                for a, f in fs.items():
                    if a:
                        rel.setdefault(a, {})["abs"] = (lambda x, f=f, f0=fs[0]: None if f(x) is None or f0(x) is None else f(x) - f0(x))
        if "off-axis-normalized" in read:
            for a, _, p, _ in read["off-axis-normalized"][2]:
                if a and p:
                    rel.setdefault(a, {})["norm"] = curve_fn(p)
        grid = [20 * 2 ** (i / 6) for i in range(60)]          # 20 Hz to 20 kHz, the charts' span
        agree = {}
        for a, d in rel.items():
            if "abs" in d and "norm" in d:
                both = [(x, abs(d["abs"](x) - d["norm"](x))) for x in grid if d["abs"](x) is not None and d["norm"](x) is not None]
                if len(both) >= 5:
                    worst = max(both, key=lambda t: t[1])
                    agree[a] = (statistics.median(t[1] for t in both), len(both), both[0][0], both[-1][0], worst)
        for kind, (img, name, ser) in read.items():
            o = img["describe"]["off_axis_read"]
            cal = o.get("calibration") or {}
            parts = [f"read automatically from {img['url']} on GitHub (capture/datasheet_probe.py with capture/chart_read.py's reader): "
                     f"axes from the chart's grid and labels, each curve by its colour at 1/24 octave; the page: {page['url'] if page else pg.get('model')}"]
            if stated:
                parts.append(f"the page states: frequency response data generated using {stated.group(1).strip()}, represented at {stated.group(2)} V / {stated.group(3)} m")
            parts.append("angles named by the colour of the legend line beside each printed angle: " +
                         ", ".join(f"{a}° {c}" for a, c, _, _ in ser))
            for a, c, p, cols in ser:
                g = gaps_of(p) if p else []
                cv = next((x for x in (img["describe"]["off_axis_read"].get("curves") or []) if x.get("kept") is p), {})
                if cv.get("stray"):
                    parts.append(f"{a}°: {len(cv['stray'])} stray point(s) left out (a run of fewer than three points between gaps, at " +
                                 ", ".join(fmt_hz(q["x"]) for q in cv["stray"][:5]) + ": a mark the reader caught, not the curve)")
                if cv.get("clipped_bottom"):
                    parts.append(f"{a}°: lies on the chart's floor line in {cv['clipped_bottom']} pixel column(s): below the chart there, left out")
                if cv.get("clipped_top"):
                    parts.append(f"{a}°: lies on the chart's top line in {cv['clipped_top']} pixel column(s): above the chart there, left out")
                if not p:
                    parts.append(f"{a}°: its {c} line was not found in the chart (hidden under the others or drawn as a grid line); not stored")
                elif g:
                    parts.append(f"{a}°: no points between " + ", ".join(f"{fmt_hz(x)} and {fmt_hz(y)}" for x, y in g[:6]) +
                                 (" and elsewhere" if len(g) > 6 else "") + " (hidden under another line, or below the chart's floor)")
            if kind == "off-axis":
                pm = printed_mean(img)
                zero = next((p for a, _, p, _ in ser if a == 0 and p), None)
                if pm is not None and zero:
                    ys = [q["y"] for q in zero if 300 <= q["x"] <= 1000]
                    if ys:
                        got = sum(ys) / len(ys)
                        parts.append(f"check: the 0° curve's mean from 300 to 1000 Hz reads {got:.1f} dB; the chart prints 'Mean SPL = {pm:.1f}dB' ({signed(got - pm)} dB)")
            for a in sorted(agree):
                med, n, lo, hi, worst = agree[a]
                parts.append(f"{a}° relative to 0°, the sound-pressure chart against the normalized chart, at {n} sixth-octave frequencies from "
                             f"{fmt_hz(lo)} to {fmt_hz(hi)} where both have points: median difference {med:.2f} dB, largest {worst[1]:.1f} dB at {fmt_hz(worst[0])}")
            series = [{"name": f"{a}°", "points": [{"x": q["x"], "y": q["y"]} for q in p]} for a, _, p, _ in ser if p]
            angles = [a for a, _, p, _ in ser if p]
            y_label = ("Level relative to on axis", "dB re 0°") if kind == "off-axis-normalized" else ("SPL", "dB")
            made.append((did, {
                "type": "Off-axis response" + (" (normalized against 0°)" if kind == "off-axis-normalized" else ""),
                "kind": kind,
                "method": "automated pixel reading (GitHub), calibrated from the chart's own grid and labels",
                "conditions": {"lab": lab, "angles_deg": angles, **({"drive_v": float(stated.group(2)), "distance_mm": round(float(stated.group(3)) * 1000)} if stated else {})},
                "source": f"{lab} ({name}, automated reading)",
                "confidence": "medium",
                "note": "; ".join(parts),
                "chartType": "line",
                "axes": {"x": {"label": "Frequency", "unit": "Hz", "scale": "log"}, "y": {"label": y_label[0], "unit": y_label[1]}},
                "calibration": cal,
                "series": series,
            }))
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
    for did, s in made:
        print(f"{did}: {s['type']}: {[x['name'] + ' ' + str(len(x['points'])) for x in s['series']]}\n   {s['note']}")
    for did, why in skipped:
        print(f"not made {did}: {why}")
    if a.write and made:
        byid = {d["id"]: d for d in db["drivers"]}
        for did, s in made:
            d = byid[did]
            d["measurements"] = [m for m in d["measurements"] if m.get("source") != s["source"]]
            d["measurements"].append(s)
            d["updated"] = probe["date"]
        tmp = ROOT / "capture" / "_page_charts_candidate.json"
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
