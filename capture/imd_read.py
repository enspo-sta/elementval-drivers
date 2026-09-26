#!/usr/bin/env python3
"""Read HiFiCompass two-tone intermodulation spectra on GitHub (this repository's cloud sessions cannot reach
the site). The charts are 1024 x 701, black, a green grid, the spectrum in yellow, dB on the left (0 to -100),
frequency linear below. For every chart of the drivers in capture/imd_read_request.txt (an id, optionally its
page address), this tool:
  1. reads the test from the file name (a one-tone chart: its tone, voltage and microphone distance): the two tones, their ratio, and the low tone's peak excursion
     (30hz255hz_xmax30hz3mm_4to1) or the drive voltage (500hz2v834.25khz2v83, 2v83rms_1khz10khz-1to1),
  2. fits the axes from the grid lines and the labels read by tesseract (dB rows, frequency columns, linear),
  3. reads the spectrum's highest point at the tones and at every product m*f1 + n*f2 up to the 5th order
     that falls on the chart, and the noise floor around each (a product less than 6 dB above its floor is
     left out and counted); the chart runs from the plot's own left edge (0 Hz), not from the first grid
     line, so a low tone left of it is read too,
  4. checks the reading against the cursor readout the chart prints ("254.88Hz,-26.59dB"): the reading at
     that frequency beside the printed level, when the level is on the chart,
and writes capture/imd_read.json (numbers and text only; no image is stored).

  python3 capture/imd_read.py [--ids mr16tx-8,...] [--limit N]
"""
import argparse
import datetime as dt
import json
import math
import re
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
import chart_probe as CP  # noqa: E402
import chart_read as CR  # noqa: E402

V = r"(1v41|2v83|5v6|11v2|22v5|\d+v)"


def volts_of(t):
    m = re.fullmatch(r"(\d+)v(\d*)", t)
    return float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) if m else None


def test_of(name):
    """The test a chart shows, from its file name, or None: two tones (f1, f2), or one tone (f0) whose harmonics
    the chart shows (ptt10.0x04-nab-02_50mm_2v83_20hz.png: 20 Hz at 2.83 V, microphone at 50 mm)."""
    n = name.lower()
    m = re.search(r"_(\d+)mm_" + V + r"_(\d+(?:\.\d+)?)hz\.(?:png|jpg)$", n)
    if m:
        return {"f0": float(m.group(3)), "drive_v": volts_of(m.group(2)), "distance_mm": int(m.group(1))}
    m = re.search(r"(\d+(?:\.\d+)?)hz(\d+(?:\.\d+)?)hz_xmax(\d+(?:\.\d+)?)hz(\d+(?:\.\d+)?)mm(?:_(\d+)to(\d+))?", n)
    if m:   # a file name without the ratio (ptt6.5w04-01a_30hz255hz_xmax30hz3mm.png) leaves it unstated
        return {"f1": float(m.group(1)), "f2": float(m.group(2)), "x_pk_mm": float(m.group(4)),
                "ratio": f"{m.group(5)}:{m.group(6)}" if m.group(5) else None}
    m = re.search(r"(\d+(?:\.\d+)?)(k?)hz" + V + r"(\d+(?:\.\d+)?)(k?)hz" + V, n)
    if m:
        f1 = float(m.group(1)) * (1000 if m.group(2) else 1); f2 = float(m.group(4)) * (1000 if m.group(5) else 1)
        v1, v2 = volts_of(m.group(3)), volts_of(m.group(6))
        return {"f1": f1, "f2": f2, "drive_v": v1 if v1 == v2 else [v1, v2], "ratio": "1:1" if v1 == v2 else f"{v1}:{v2}"}
    m = re.search(r"(\d+)v(\d*)rms_(\d+(?:\.\d+)?)(k?)hz(\d+(?:\.\d+)?)(k?)hz[-_](\d+)to(\d+)", n)
    if m:
        return {"f1": float(m.group(3)) * (1000 if m.group(4) else 1), "f2": float(m.group(5)) * (1000 if m.group(6) else 1),
                "drive_v": volts_of(m.group(1) + "v" + m.group(2)), "ratio": f"{m.group(7)}:{m.group(8)}"}
    return None


def x_linear(cols, words):
    """frequency = a + b*x from the grid columns and the numbers under them."""
    pairs = []
    for w in words:
        v = CR.number(w.get("text", ""))
        if v is None or v < 0:
            continue
        near = min(cols, key=lambda c: abs(c[0] - w["x"]), default=None)
        if near and abs(near[0] - w["x"]) <= 14:
            pairs.append((near[0], v))
    pairs = CR.monotone(pairs, increasing=True)
    return CR.fit_line(pairs)


def plot_span(img, row, inside, bg_hex):
    """The plot's left and right edges: the grid row drawn through `inside`, followed out to where it ends."""
    import numpy as np
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    line = np.abs(img[row].astype(int) - bg).sum(axis=1) >= 40
    lo = hi = inside
    while lo > 0 and line[lo - 1]:
        lo -= 1
    while hi < line.size - 1 and line[hi + 1]:
        hi += 1
    return lo, hi


CURSOR = re.compile(r"(\d+\.\d+)\s*Hz\s*,\s*(-?\d+(?:\.\d+)?)\s*dB", re.I)


def cursor_of(words):
    """The cursor readout the chart prints (frequency, level), or None."""
    for w in words:
        m = CURSOR.search(w.get("text", ""))
        if m:
            return float(m.group(1)), float(m.group(2))
    return None


def hexc(k):
    return "#%02x%02x%02x" % tuple(int(v) for v in k[:3])


def dist(a, b):
    return sum(abs(int(a[i]) - int(b[i])) for i in range(3))


def rgb(hx):
    return [int(hx[i:i + 2], 16) for i in (1, 3, 5)]


def trace_colour(img, y0, y1, x0, x1, bg, grid):
    """The spectrum's colour: the most common saturated colour in the plot that is neither the background nor the
    grid (the two-tone charts draw it yellow on black). When the most common colour of the whole image is itself
    saturated and differs from the image's corner, the spectrum is drawn filled in it (a coloured area under the
    curve) and its top edge is the level. Returns (colour, how, the candidates seen)."""
    import numpy as np
    sub = img[y0:y1 + 1, x0:x1 + 1, :3].reshape(-1, 3).astype(int)
    keys, counts = np.unique((sub // 16) * 16 + 8, axis=0, return_counts=True)
    order = counts.argsort()[::-1]
    seen, cand = [], []
    for i in order[:24]:
        k = keys[i]
        seen.append([hexc(k), int(counts[i])])
        if dist(k, rgb(bg)) < 60 or (grid and dist(k, rgb(grid)) < 60) or max(k) - min(k) < 60 or max(k) < 120:   # greys, text, dark grid
            continue
        cand.append(hexc(k))
    corner = img[3, 3, :3].astype(int)
    b = rgb(bg)
    if max(b) - min(b) > 100 and dist(b, corner) > 60:
        return bg, "filled", seen
    return (cand[0] if cand else None), "line", seen


def lattice(cols):
    """The grid columns: the largest set of candidates on one evenly spaced lattice (a tall spectral line,
    such as a tone near the top of the chart, is found as a column too and is not on it)."""
    xs = [c[0] for c in cols]
    if len(xs) < 3:
        return cols
    best = []
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            step = xs[j] - xs[i]
            if step < 20:
                continue
            on = [c for c in cols if abs((c[0] - xs[i]) / step - round((c[0] - xs[i]) / step)) * step <= 2]
            if len(on) > len(best):
                best = on
    return best or cols


def negative_labels(words):
    """The dB labels of these charts run from 0 down to -100; the OCR sometimes drops the minus sign
    ("10.0" for "-10.0"), so every label is taken as zero or below."""
    out = []
    for w in words:
        v = CR.number(w.get("text", ""))
        out.append(dict(w, text=str(-abs(v))) if v is not None else w)
    return out


def tones_of(test):
    return [test["f0"]] if "f0" in test else [test["f1"], test["f2"]]


def lines_of(test, fmax):
    """The products a chart can show: the harmonics of one tone (order 2 to 10), or the two-tone products."""
    if "f0" in test:
        return [{"f": round(k * test["f0"], 3), "m": k, "n": 0, "order": k} for k in range(2, 11) if k * test["f0"] <= fmax]
    return products(test["f1"], test["f2"], fmax)


def products(f1, f2, fmax):
    out = []
    for m in range(-5, 6):
        for n in range(-5, 6):
            order = abs(m) + abs(n)
            if order < 2 or order > 5:
                continue
            f = m * f1 + n * f2
            if f <= 0 or f > fmax or any(abs(f - t) < 1e-6 for t in (f1, f2)) or any(abs(f - p["f"]) < 1e-6 for p in out):
                continue
            out.append({"f": round(f, 3), "m": m, "n": n, "order": order})
    return sorted(out, key=lambda p: p["f"])


def read_chart(path, test):
    import numpy as np
    img, mode, _ = CR.load(path)
    h, w = img.shape[:2]
    bg, _, _ = CP.background(img)
    box = CP.plot_box(img, bg) or [0, 0, w - 1, h - 1]
    rows, cols, rcol, ccol = CP.grid_lines(img, box, bg)
    rows = [r for r in rows if r[1] - r[0] < 4]
    cols = lattice([c for c in cols if c[1] - c[0] < 4])
    rec = {"size": [w, h], "background": bg, "rows": len(rows), "cols": [c[0] for c in cols][:40], "grid_row_colour": rcol}
    if len(rows) < 4 or len(cols) < 3:
        rec["error"] = "grid not found"; return rec
    left = CP.safe_ocr(path, [0, 0, max(cols[0][0] - 2, 40), h], w, h)
    bottom = CP.safe_ocr(path, [0, rows[-1][1] + 2, w, h], w, h)
    ya, xa = CR.y_axis(rows, negative_labels(left)), x_linear(cols, bottom)
    rec.update({"y_axis": ya, "x_axis": xa, "left_labels": [(t.get("text"), t.get("y")) for t in left][:16],
                "bottom_labels": [(t.get("text"), t.get("x")) for t in bottom][:16]})
    if not ya or not xa or xa[1] <= 0 or ya[1] >= 0:
        rec["error"] = "axes could not be fitted"; return rec
    top0, bot0 = rows[0][0], rows[-1][0]
    mid = rows[len(rows) // 2][0]
    x0, x1 = plot_span(img, mid, cols[0][0], bg)
    x0 = max(x0, int(math.ceil((0 - xa[0]) / xa[1])))     # nothing left of 0 Hz
    # the spectrum: its highest pixel of the trace colour in every column is the level there
    tc, how, seen = trace_colour(img, top0, bot0, x0, x1, bg, rcol)
    rec.update({"trace_colour": tc, "trace_drawn": how, "colours_seen": seen[:12], "corner": hexc(img[3, 3])})
    if not tc:
        rec["error"] = "no spectrum colour found"; return rec
    near = np.abs(img[:, :, :3].astype(int) - np.array(rgb(tc))).sum(axis=2)
    mask = near < (60 if how == "line" else 40)
    rec["plot_x"] = [x0, x1]
    level = {}
    for c in range(x0, x1 + 1):
        ys = np.nonzero(mask[top0:bot0 + 1, c])[0]
        if ys.size:
            level[c] = ya[0] + ya[1] * (top0 + int(ys.min()))
    rec["columns_with_trace"] = len(level)
    col_of = lambda f: (f - xa[0]) / xa[1]
    fmax = xa[0] + xa[1] * x1
    lines = tones_of(test) + [p["f"] for p in lines_of(test, fmax)]
    near_line = set()
    for f in lines:
        c = int(round(col_of(f)))
        near_line.update(range(c - 4, c + 5))

    def peak(f):
        c = col_of(f)
        if c < x0 or c > x1:
            return None, None
        win = [level[k] for k in range(int(c) - 3, int(c) + 4) if k in level]
        flo = [level[k] for k in range(int(c) - 30, int(c) + 31) if k in level and k not in near_line]
        return (max(win) if win else None), (statistics.median(flo) if len(flo) >= 8 else None)

    rec["tones"] = []
    for f in tones_of(test):
        lv, fl = peak(f)
        rec["tones"].append({"f": f, "level": lv, "floor": fl})
    kept, low = [], 0
    for p in lines_of(test, fmax):
        lv, fl = peak(p["f"])
        if lv is None:
            continue
        if fl is not None and lv < fl + 6:
            low += 1; continue
        kept.append(dict(p, level=round(lv, 1), floor=None if fl is None else round(fl, 1)))
    rec["products"] = kept
    rec["below_floor"] = low
    cur = cursor_of(bottom + left)
    if cur:
        f, stated = cur
        read, _ = peak(f)
        on = ya[0] + ya[1] * bot0 <= stated <= ya[0] + ya[1] * top0
        tone = min(tones_of(test), key=lambda t: abs(t - f))
        at_tone = abs(tone - f) <= max(3 * xa[1], 0.01 * tone)
        note = None
        if not at_tone:
            note = "the cursor is not on a tone (the printed level is one point of the noise or a product, not a peak), so no check"
        elif not on:
            note = "the printed level is off the chart's scale"
        elif read is None:
            note = "the cursor's frequency is outside the part of the chart that was read"
        rec["check"] = {"f": f, "stated_db": stated, "read_db": None if read is None else round(read, 2),
                        "difference_db": round(read - stated, 2) if note is None else None, "note": note}
        # the pixels of the cursor's column from 6 px above the printed level to 6 px below the reading, for a
        # reading that disagrees (to see what is drawn there without the image)
        c = int(round(col_of(f)))
        if note is None and abs(read - stated) > 0.3 and 0 <= c < w:
            y_st = int(round((stated - ya[0]) / ya[1])); y_rd = int(round((read - ya[0]) / ya[1]))
            ys = range(max(0, min(y_st, y_rd) - 6), min(h, max(y_st, y_rd) + 7))
            rec["check"]["column"] = {"x": c, "y_printed": y_st, "y_read": y_rd,
                                      "pixels": [[y] + ["#%02x%02x%02x" % tuple(int(v) for v in img[y, cc, :3]) for cc in (c - 1, c, c + 1)] for y in ys]}
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "capture" / "imd_read.json"))
    a = ap.parse_args()
    lines = [x.strip() for x in (a.ids.split(",") if a.ids else (ROOT / "capture" / "imd_read_request.txt").read_text().splitlines()) if x.strip() and not x.strip().startswith("#")]
    inv = json.loads((ROOT / "capture" / "inventory.json").read_text())
    byid = {d["id"]: d for d in json.loads((ROOT / "drivers.json").read_text())["drivers"]}
    pages = {pg["url"]: pg for rec in inv["models"].values() for pg in rec["pages"]}
    # the drivers requested this time replace their own earlier results; the others' stay as they were read
    prev = Path(a.out)
    out = {"date": dt.date.today().isoformat(), "drivers": json.loads(prev.read_text()).get("drivers", {}) if prev.exists() else {}}
    last = [0.0]
    for ln in lines:
        did = ln.split()[0]
        url = ln.split()[1] if len(ln.split()) > 1 else (byid.get(did) or {}).get("source")
        pg = pages.get(url)
        if not pg:
            print(f"{did}: no inventory page", flush=True); continue
        charts = [im for im in pg["charts"] if not CP.SKIP.search(im["original"]) and test_of(im["original"].split("?")[0].rsplit("/", 1)[-1])]
        if a.limit:
            charts = charts[:a.limit]
        print(f"{did}: {len(charts)} intermodulation charts", flush=True)
        res = []
        with tempfile.TemporaryDirectory() as tmp:
            for im in charts:
                link = im["original"].split("?")[0]
                name = link.rsplit("/", 1)[-1]
                test = test_of(name)
                try:
                    data = CP.fetch(link, last)
                    path = Path(tmp) / name
                    path.write_bytes(data)
                    rec = read_chart(path, test)
                except Exception as e:  # noqa: BLE001
                    rec = {"error": f"read failed: {e}"}
                rec.update({"file": name, "url": link, "test": test})
                print(f"  {name}: {test} axes x {rec.get('x_axis')} y {rec.get('y_axis')} tones {rec.get('tones')} products {len(rec.get('products', []))} (below floor {rec.get('below_floor')}) {rec.get('error', '')}", flush=True)
                res.append(rec)
        out["drivers"][did] = res
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False) + "\n")
    print("written", a.out)


if __name__ == "__main__":
    main()
