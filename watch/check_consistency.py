#!/usr/bin/env python3
"""Cross-check the stored driver data for values that should agree with each other.

Checks that need no internet access, run on every driver (not a sample):

  notes        a note that records a corrected parameter ("Pe corrected to 350W") matches the stored value.
  parameters   Thiele/Small parameters are numbers, and the ones that follow from each other agree:
               Qts from Qes and Qms, Fs from Mms and Cms, Vas from Cms and Sd, Vd from Sd and Xmax,
               Qes from Fs, Mms, Re and Bl.
  sources      a set that says it was calculated (model, derived, "from single ...") is filed under
               the Derived family, never under a lab, so calculations are not shown as measurements.
  sweep        Purifi datasheets: the harmonic curve at 94 dB and the level sweep at 94 dB describe
               the same thing at the sweep's frequencies (125 Hz, 1 kHz, ...).
  band THD     a stored band-THD table matches the THD integrated again from the stored curve.
  levels       the same driver and source at two levels: the difference follows the typical
               level slopes (H2 1.0, H3 to H5 0.7 dB per dB) within a few dB.
  pair         a two-driver record derived from a single driver matches that derivation again.
  excursion    a calculated maximum level matches Sd and Xmax (half space, 1 m).
  test tones   intermodulation bars: the upper test tone sits at the stated test level.
  curves       every curve has increasing frequencies, no duplicates and no missing values.

Writes watch/consistency.md (and prints it with --stdout). Exit code is 0 unless --strict is given
and something failed, so it can run in the validation workflow as a report.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

from common import ROOT, families_of, family_kind, load_config

OUT = ROOT / "watch" / "consistency.md"
RHO, C = 1.204, 343.2                  # air at 20 °C
TYPICAL = {"H2": 1.0, "H3": 0.7, "H4": 0.7, "H5": 0.7}


def num(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*$", str(v or ""))
    return float(m.group(1)) if m else None


def interp_log(points, f):
    pts = sorted((p for p in points if p.get("y") is not None), key=lambda p: p["x"])
    for a, b in zip(pts, pts[1:]):
        if a["x"] <= f <= b["x"]:
            if a["x"] == b["x"]:
                return a["y"]
            t = math.log(f / a["x"]) / math.log(b["x"] / a["x"])
            return a["y"] + t * (b["y"] - a["y"])
    return None


def series(m, name):
    return next((s["points"] for s in m.get("series", []) if s.get("name") == name), None)


class Report:
    def __init__(self):
        self.rows = []          # (check, driver, result, detail)

    def add(self, check, driver, ok, detail):
        self.rows.append((check, driver, "ok" if ok is True else ("check" if ok is None else "differs"), detail))

    def failed(self):
        return [r for r in self.rows if r[2] == "differs"]


def check_parameters(d, rep):
    ts = d.get("ts") or {}
    if not ts:
        return
    text = {k: v for k, v in ts.items() if v not in ("", None) and num(v) is None}
    stored_as_text = {k: v for k, v in ts.items() if isinstance(v, str) and num(v) is not None}
    empty = [k for k, v in ts.items() if v == ""]
    if stored_as_text or empty:
        rep.add("parameters", d["id"], False, "stored as text instead of numbers: " + ", ".join(sorted(stored_as_text)) +
                (("; empty: " + ", ".join(empty)) if empty else ""))
    if text:
        rep.add("parameters", d["id"], None, "not a number: " + "; ".join(f"{k} = {v!r}" for k, v in text.items()))
    g = {k: num(v) for k, v in ts.items()}

    def compare(label, stored, calc, tol):
        if stored is None or calc is None:
            return
        dev = abs(calc - stored) / abs(stored) if stored else abs(calc)
        rep.add("parameters", d["id"], dev <= tol, f"{label}: stored {stored:g}, from the others {calc:.3g} ({dev * 100:.1f} % apart)")

    if g.get("Qes") and g.get("Qms"):
        compare("Qts", g.get("Qts"), g["Qes"] * g["Qms"] / (g["Qes"] + g["Qms"]), 0.03)
    if g.get("Mms") and g.get("Cms"):
        compare("Fs", g.get("Fs"), 1 / (2 * math.pi * math.sqrt(g["Mms"] / 1000 * g["Cms"] / 1000)), 0.03)
    if g.get("Cms") and g.get("Sd"):
        compare("Vas", g.get("Vas"), RHO * C * C * (g["Sd"] / 1e4) ** 2 * g["Cms"] / 1000 * 1000, 0.05)
    if g.get("Sd") and g.get("Xmax"):
        compare("Vd", g.get("Vd"), g["Sd"] * g["Xmax"] / 10, 0.03)
    if g.get("Fs") and g.get("Mms") and g.get("Re") and g.get("Bl"):
        compare("Qes", g.get("Qes"), 2 * math.pi * g["Fs"] * g["Mms"] / 1000 * g["Re"] / g["Bl"] ** 2, 0.06)


CALCULATED = re.compile(r"^from single|\bderived\b|\bcalculat|\bmodell?ed\b|\bsimulat", re.I)


def check_notes(d, rep):
    """A note that records a corrected parameter must match the stored parameter."""
    ts = d.get("ts") or {}
    for m in d.get("measurements", []) + [d]:
        for mm in re.finditer(r"\b(Pe|Xmax|Fs|Qts|Vas|Sd|Re|Bl)\s+corrected to\s+(\d+(?:\.\d+)?)", str(m.get("note") or m.get("findings") or "")):
            key, val = mm.group(1), float(mm.group(2))
            stored = num(ts.get(key))
            rep.add("notes", d["id"], stored is not None and abs(stored - val) <= 0.01 * val,
                    f"a note says {key} was corrected to {val:g}, the stored {key} is {ts.get(key)!r}")


def active(d):
    """The sets the cross-checks compare: an earlier capture superseded by a full reading of the same charts
    (superseded_by) is left out, as Compare and Simulate leave it out."""
    return [m for m in d.get("measurements", []) if not m.get("superseded_by")]


def check_sources(d, rep, cfg):
    for i, m in enumerate(d.get("measurements", [])):
        fams = families_of(m.get("source"), cfg)
        kind = family_kind(fams[0], cfg) if len(fams) == 1 else None
        says_calculated = any(CALCULATED.search(str(m.get(k) or "")) for k in ("note", "method"))
        if kind and kind != "derived" and says_calculated:
            rep.add("sources", d["id"], False, f"set {i} ({m['type']}) is filed under {fams[0]} but its notes say it was "
                    f"calculated: {str(m.get('note') or m.get('method'))[:90]}")


def check_sweep(d, rep, cfg):
    for m in active(d):
        if m.get("type") != "HD vs SPL (level sweep)":
            continue
        fam = families_of(m.get("source"), cfg)
        curve = next((c for c in d["measurements"] if c.get("type", "").startswith("HD vs frequency")
                      and families_of(c.get("source"), cfg) == fam and (c.get("conditions") or {}).get("spl_db") == 94), None)
        if not curve:
            continue
        for s in m.get("series", []):
            mm = re.match(r"^(H\d)\s+(\d+(?:\.\d+)?)\s*(k?)Hz$", s["name"], re.I)
            if not mm:
                continue
            order, f = mm.group(1).upper(), float(mm.group(2)) * (1000 if mm.group(3) else 1)
            at94 = next((p["y"] for p in sorted(s["points"], key=lambda p: abs(p["x"] - 94)) if abs(p["x"] - 94) <= 1.5), None)
            pts = series(curve, order)
            fromcurve = interp_log(pts, f) if pts else None
            if at94 is None or fromcurve is None:
                continue
            diff = at94 - fromcurve
            rep.add("sweep", d["id"], abs(diff) <= 4, f"{order} at {f:g} Hz, 94 dB: sweep {at94:.1f} dB, curve {fromcurve:.1f} dB ({diff:+.1f} dB)")


def thd_from(m, lo, hi):
    """Power-averaged THD in % over [lo, hi] Hz from the H2..H5 series of a set (log-spaced resampling)."""
    names = [n for n in ("H2", "H3", "H4", "H5") if series(m, n)]
    if not names:
        return None
    total, n = 0.0, 0
    for i in range(0, 241):
        f = lo * (hi / lo) ** (i / 240)
        vals = [interp_log(series(m, k), f) for k in names]
        if any(v is None for v in vals):
            continue
        total += sum(10 ** (v / 10) for v in vals)
        n += 1
    return 100 * math.sqrt(total / n) if n else None


def check_band_thd(d, rep, cfg):
    ms = active(d)
    for t in ms:
        if t.get("chartType") != "table" or "THD %" not in (t.get("columns") or []):
            continue
        spl = (t.get("conditions") or {}).get("spl_db")
        col = t["columns"].index("THD %")
        curve = next((c for c in ms if c.get("chartType") == "line" and c.get("type", "").startswith("HD")
                      and (c.get("conditions") or {}).get("spl_db") == spl and series(c, "H2")), None)
        if not curve:
            continue
        for row in t.get("rows", []):
            mm = re.match(r"^(\d+)\D+(\d+)$", str(row[0]))
            if not mm or row[col] is None:
                continue
            lo, hi = float(mm.group(1)), float(mm.group(2))
            again = thd_from(curve, lo, hi)
            if again is None:
                rep.add("band THD", d["id"], None, f"{row[0]} Hz at {spl} dB: the curve does not cover this band")
                continue
            ratio = 20 * math.log10(again / row[col]) if row[col] else 99
            rep.add("band THD", d["id"], abs(ratio) <= 1.5, f"{row[0]} Hz at {spl} dB: table {row[col]:.3g} %, from the curve {again:.3g} % ({ratio:+.1f} dB)")


def check_levels(d, rep, cfg):
    curves = [c for c in active(d) if c.get("chartType") == "line" and c.get("type", "").startswith("HD")
              and "level sweep" not in c.get("type", "") and "current" not in c.get("type", "")
              and num((c.get("conditions") or {}).get("spl_db")) is not None]
    for i, a in enumerate(curves):
        for b in curves[i + 1:]:
            if families_of(a.get("source"), cfg) != families_of(b.get("source"), cfg):
                continue
            la, lb = num(a["conditions"]["spl_db"]), num(b["conditions"]["spl_db"])
            if la == lb:
                continue
            lo, hi = (a, b) if la < lb else (b, a)
            dl = abs(lb - la)
            for k in ("H2", "H3"):
                pl, ph = series(lo, k), series(hi, k)
                if not pl or not ph:
                    continue
                # a harmonic ratio near the measurement's floor (HiFiCompass charts end at -100 dB re fundamental)
                # does not move with the level: only frequencies where both curves are above -80 dB count
                diffs = [interp_log(ph, p["x"]) - p["y"] for p in pl
                         if interp_log(ph, p["x"]) is not None and (p["y"] >= 0 or (p["y"] > -80 and interp_log(ph, p["x"]) > -80))]
                if len(diffs) < 12:
                    continue
                mean = sum(diffs) / len(diffs)
                expect = TYPICAL[k] * dl
                rep.add("levels", d["id"], abs(mean - expect) <= 4,
                        f"{k}: {num(hi['conditions']['spl_db']):g} dB curve minus {num(lo['conditions']['spl_db']):g} dB curve = {mean:+.1f} dB on average "
                        f"over {len(diffs)} shared frequencies (typical slope expects {expect:+.1f} dB)")


def check_pair(d, rep, cfg, byid):
    note = " ".join(str(m.get("note") or "") for m in active(d))
    mm = re.search(r"s_n measured: H2 ([\d.]+), H3 ([\d.]+), H4 ~?([\d.]+), H5 ([\d.]+)", note)
    if not mm or "dual" not in d["id"]:
        return
    single = byid.get(d["id"].replace("-dual", ""))
    if not single:
        return
    slopes = dict(zip(("H2", "H3", "H4", "H5"), map(float, mm.groups())))
    pair = next(m for m in active(d) if m.get("chartType") == "line" and series(m, "H2"))
    one = next((m for m in single["measurements"] if m.get("chartType") == "line" and m.get("type") == pair.get("type")), None)
    if not one:
        return
    for k, s in slopes.items():
        diffs = []
        for p in series(pair, k) or []:
            q = interp_log(series(one, k), p["x"])
            if q is not None:
                diffs.append(p["y"] - q)
        if not diffs:
            continue
        mean, spread = sum(diffs) / len(diffs), max(diffs) - min(diffs)
        expect = -6.02 * s
        rep.add("pair", d["id"], abs(mean - expect) <= 2.0,
                f"{k}: pair minus single = {mean:+.1f} dB on average (note's slope {s:g} expects {expect:+.1f} dB); "
                f"varies by {spread:.1f} dB across frequency, so slopes per frequency were used")


def check_excursion(d, rep):
    ts = d.get("ts") or {}
    sd, xmax = num(ts.get("Sd")), num(ts.get("Xmax"))
    if not sd or not xmax:
        return
    for m in active(d):
        if not m.get("type", "").startswith("Max SPL") or not m.get("series"):
            continue
        n = 2 if "dual" in d["id"] else 1
        for p in m["series"][0]["points"][:3]:
            f = p["x"]
            vol = sd / 1e4 * xmax / 1000 * n
            pk = RHO * (2 * math.pi * f) ** 2 * vol / (2 * math.pi * 1.0)
            spl = 20 * math.log10(pk / math.sqrt(2) / 2e-5)
            rep.add("excursion", d["id"], abs(spl - p["y"]) <= 1.0, f"{f:g} Hz: stored {p['y']:.1f} dB, from Sd and Xmax {spl:.1f} dB")


def check_tones(d, rep):
    for m in active(d):
        if m.get("chartType") != "bar":
            continue
        tones = re.findall(r"(\d+)\s*\+\s*(\d+)\s*Hz", " ".join(str(m.get(k) or "") for k in ("method", "type")))
        c = m.get("conditions") or {}
        level = num(c.get("spl_db"))
        if not tones or level is None:
            continue
        f2 = float(tones[0][1])
        bar = next((p["y"] for p in m["series"][0]["points"] if abs(p["x"] - f2) < 0.5), None)
        if bar is not None:
            rep.add("test tones", d["id"], abs(bar - level) <= 1.0, f"{m.get('method') or m['type']}: {f2:g} Hz tone at {bar:.1f} dB, stated {level:g} dB")


def check_curves(d, rep):
    for i, m in enumerate(d.get("measurements", [])):
        for s in m.get("series", []):
            xs = [p.get("x") for p in s.get("points", [])]
            badx = [p for p in s.get("points", []) if not isinstance(p.get("x"), (int, float))]
            nully = [p for p in s.get("points", []) if p.get("y") is None]
            if badx:
                rep.add("curves", d["id"], False, f"set {i} {s['name']}: {len(badx)} point(s) without a frequency")
            if nully:
                rep.add("curves", d["id"], None, f"set {i} ({m['type']}, {(m.get('conditions') or {}).get('ref_spl_db') or (m.get('conditions') or {}).get('spl_db')} dB) "
                        f"{s['name']}: {len(nully)} value(s) left empty, as captured (not readable in the source chart)")
            if m.get("chartType") == "line" and any(b <= a for a, b in zip(xs, xs[1:]) if isinstance(a, (int, float)) and isinstance(b, (int, float))):
                rep.add("curves", d["id"], False, f"set {i} ({m['type']}) {s['name']}: frequencies not strictly increasing")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a check differs")
    args = ap.parse_args()
    cfg = load_config()
    rep = Report()
    drivers = []
    for name in ("drivers.json", "drivers_survey_midbass.json"):
        p = ROOT / name
        if p.exists():
            drivers += json.loads(p.read_text(encoding="utf-8"))["drivers"]
    byid = {d["id"]: d for d in drivers}
    for d in drivers:
        check_parameters(d, rep)
        check_notes(d, rep)
        check_sources(d, rep, cfg)
        check_sweep(d, rep, cfg)
        check_band_thd(d, rep, cfg)
        check_levels(d, rep, cfg)
        check_pair(d, rep, cfg, byid)
        check_excursion(d, rep)
        check_tones(d, rep)
        check_curves(d, rep)
    counts = {k: sum(1 for r in rep.rows if r[2] == k) for k in ("ok", "differs", "check")}
    lines = ["# Consistency of the stored data", "",
             "Written by `watch/check_consistency.py`. Values that should agree with each other, checked on every driver.",
             "\"differs\" means the stored values disagree by more than the tolerance and need a look at the source;",
             "\"check\" means the value could not be tested (text where a number belongs, or a curve that does not cover the band).", "",
             f"{counts['ok']} ok, {counts['differs']} differ, {counts['check']} to check.", "",
             "| Result | Check | Driver | Detail |", "|---|---|---|---|"]
    order = {"differs": 0, "check": 1, "ok": 2}
    for check, drv, res, detail in sorted(rep.rows, key=lambda r: (order[r[2]], r[0], r[1])):
        lines.append(f"| {res} | {check} | {drv} | {detail.replace('|', '/')} |")
    text = "\n".join(lines) + "\n"
    if args.stdout:
        print(text)
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"{OUT.relative_to(ROOT)}: {counts['ok']} ok, {counts['differs']} differ, {counts['check']} to check")
    return 1 if args.strict and rep.failed() else 0


if __name__ == "__main__":
    sys.exit(main())
