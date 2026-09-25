#!/usr/bin/env python3
"""Read curves from HiFiCompass chart images on GitHub, calibrated from each chart's own grid and labels.

What capture/chart_probe.py found: the response, harmonics and current-distortion charts are a green
canvas (1276 × 635) with a black horizontal grid (2 dB or 5 dB per line), grey vertical decade lines
and the axis labels printed left and below; the on-axis response is a dark-grey line, harmonics are
red and blue lines; impedance charts are black with a grey grid, a green curve and a linear ohm scale.
For every chart of those types, this tool:
  1. finds the grid lines and reads the labels with tesseract (positions included),
  2. fits the axes (log frequency from the decade lines and their labels; linear dB or ohm from the
     row labels, outliers such as a '30' read for '90' rejected by a median-of-slopes fit),
  3. reads every curve colour column by column (the middle of the colour's pixels) and resamples at
     1/24 octave (CAPTURE.md), and
  4. checks itself where it can: the 2.83 V response at 1 kHz against the sensitivity the page states;
     the impedance minimum against Re; the impedance peak against Fs.
A dark band across the middle of the green charts (a watermark) is not a grid row and not a curve: solid
regions of a colour are left out of a curve, and where the curve is hidden for more than a few columns the
gap is reported instead of bridged. Everything it writes is numbers and text (capture/chart_read.json);
no image is stored.
  python3 capture/chart_read.py [--ids m74a-6,...] [--types response,harmonics,current,impedance]
"""
import argparse
import datetime as dt
import json
import math
import re
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
import chart_probe as CP  # noqa: E402  (fetch, background, grid_lines, all_colours, safe_ocr, chart_type)

PER_OCTAVE = 24
MIN_CURVE_PIXELS = 700


def number(s):
    """A label's value; a grid line touching the text reads as a trailing dash ("110-")."""
    s = s.strip().rstrip("-").replace("O", "0").replace("o", "0").replace(",", ".")
    m = re.fullmatch(r"-?\d+(?:\.\d+)?", s)
    if m:
        return float(s)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*k(?:hz)?", s.lower())
    return float(m.group(1)) * 1000 if m else None


def fit_line(pairs):
    """value = a + b·pos from (pos, value) pairs; the slope is the median of all pairwise slopes and
    the offset the median of the offsets, so a misread label does not pull the fit."""
    pairs = [(p, v) for p, v in pairs if v is not None]
    if len(pairs) < 2:
        return None
    slopes = []
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            if pairs[j][0] != pairs[i][0]:
                slopes.append((pairs[j][1] - pairs[i][1]) / (pairs[j][0] - pairs[i][0]))
    if not slopes:
        return None
    b = statistics.median(slopes)
    a = statistics.median(v - b * p for p, v in pairs)
    resid = [abs(v - (a + b * p)) for p, v in pairs]
    good = [pv for pv, r in zip(pairs, resid) if r <= max(0.6 * abs(b) * 5, 1e-9) or r <= 1.0]
    if len(good) >= 2 and len(good) < len(pairs):
        return fit_line(good)
    return a, b, len(pairs), len(pairs) - len(good)


def x_axis(cols, bottom_words):
    """log10(f) = a + b·x from the grey decade lines and the labels below them."""
    pairs = []
    for w in bottom_words:
        v = number(w["text"]) if "text" in w else None
        if v is None or v <= 0:
            continue
        if abs(math.log10(v) - round(math.log10(v))) > 0.02 and v not in (20, 50, 200, 500, 2000, 5000, 20000):
            continue
        x = w["x"]
        near = [c for c in cols if abs(c[0] - x) <= 12]
        if near:
            pairs.append((near[0][0], math.log10(v)))
    fit = fit_line(pairs)
    if fit is None and len(cols) >= 2 and pairs:
        # one label only: the decade lines are one decade apart
        step = statistics.median(cols[i + 1][0] - cols[i][0] for i in range(len(cols) - 1) if cols[i + 1][0] - cols[i][0] > 100)
        p, v = pairs[0]
        return v - p / step, 1 / step, 1, 0
    return fit


def y_axis(rows, left_words):
    """value = a + b·y from the horizontal grid lines and the labels beside them."""
    pairs = []
    for w in left_words:
        v = number(w["text"]) if "text" in w else None
        if v is None:
            continue
        near = [r for r in rows if abs(r[0] - w["y"]) <= 9]
        if near:
            pairs.append((near[0][0], v))
    return fit_line(pairs)


def grid_rows_only(img, rows, box):
    """A flat curve spans the width like a grid line: keep only the rows drawn in the grid's own colour
    (the colour most of the candidate rows share)."""
    import numpy as np
    from collections import Counter
    x0, y0, x1, y1 = box
    def colour(r):
        line = img[r[0], x0:x1 + 1]
        q = (line // 32) * 32
        keys, counts = np.unique(q, axis=0, return_counts=True)
        return tuple(int(v) for v in keys[counts.argmax()])
    cols = {tuple(r): colour(r) for r in rows}
    if not cols:
        return rows
    counts = Counter(cols.values())
    keep = {c for c, n in counts.items() if n >= 3} or {counts.most_common(1)[0][0]}
    rows = [r for r in rows if cols[tuple(r)] in keep]
    # grid rows are evenly spaced: a row off the regular spacing (a flat curve in the grid's colour) is not grid
    import statistics
    if len(rows) >= 4:
        ys = [r[0] for r in rows]
        # the spacing: the span divided by n-1, n-2 or n-3 (one or two rows may be a flat curve), from the first
        # or the second row, whichever keeps the most rows on a whole multiple; then refined from every row
        def kept(base, d):
            return [y for y in ys if abs(((y - base) / d) - round((y - base) / d)) <= 0.25]
        best = None
        for bi in (0, 1):
            base = ys[bi]
            for extra in (0, 1, 2):
                k = len(ys) - 1 - bi - extra
                if k >= 2:
                    d = (ys[-1] - base) / k
                    n = len(kept(base, d))
                    if best is None or n > best[0]:
                        best = (n, base, d)
        _, base, d = best
        for _ in range(2):
            ks = [round((y - base) / d) for y in ys]
            d = statistics.median([(y - base) / k for y, k in zip(ys, ks) if k > 0]) or d
        rows = [r for r in rows if abs(((r[0] - base) / d) - round((r[0] - base) / d)) <= 0.25]
    return rows


def opened(mask, r=3):
    """Morphological opening with a (2r+1)-square: what is left is the solid regions of the mask (a block of
    colour, a watermark band, bold text); lines thinner than the square vanish. Separable min then max."""
    import numpy as np
    e = mask.copy()
    for ax in (0, 1):
        acc = e.copy()
        for sft in range(1, r + 1):
            acc &= np.roll(e, sft, axis=ax) & np.roll(e, -sft, axis=ax)
        e = acc
    d = e.copy()
    for ax in (0, 1):
        acc = d.copy()
        for sft in range(1, r + 1):
            acc |= np.roll(d, sft, axis=ax) | np.roll(d, -sft, axis=ax)
        d = acc
    return d


def read_curve(img, colour_hex, bg_hex, box, grid=((), ()), tol=60):
    import numpy as np
    target = np.array([int(colour_hex[i:i + 2], 16) for i in (1, 3, 5)])
    if max(target) - min(target) < 30:
        tol = 40                                       # a black or grey curve: keep the dark-grey dotted grid out
    x0, y0, x1, y1 = box
    dist = np.sqrt(((img - target) ** 2).sum(axis=2))
    mask = dist <= tol
    # a curve is a thin line: solid regions of the same colour (the dark watermark band across the HiFiCompass
    # charts, a block, bold text) are left out, so the middle of a column's pixels stays on the curve
    mask &= ~opened(mask, 3)
    # a black or grey curve shares its colour with the grid lines: leave those rows and columns out (the curve
    # is interpolated across them); a coloured curve is far from the grey grid and needs no such gap
    if max(target) - min(target) < 30:
        for r in grid[0]:
            mask[r[0]:r[1] + 1, :] = False
        for c in grid[1]:
            mask[:, c[0]:c[1] + 1] = False
    pts, runs = [], []
    for col in range(x0, x1 + 1):
        ys = np.nonzero(mask[y0:y1 + 1, col])[0]
        if ys.size:
            # runs of consecutive rows: one run = one line crossing this column
            breaks = np.nonzero(np.diff(ys) > 2)[0]
            runs.append(len(breaks) + 1)
            pts.append((col, float(y0 + np.median(ys))))
    return pts, (statistics.median(runs) if runs else 0)


GAP_PX = 12   # columns without the curve: up to this many are bridged, more is a gap left out and reported


def resample(points, xa, xb):
    """(x pixel, y pixel) -> 1/24-octave points in (f, value) with the axis fits, and the gaps (in Hz) where
    the curve was not visible for more than GAP_PX columns (hidden behind the watermark band, or drawn on
    a grid line of its own colour): no point is made up there."""
    if not points:
        return [], []
    fx = lambda x: 10 ** (xa[0] + xa[1] * x)
    fy = lambda y: xb[0] + xb[1] * y
    raw = [(fx(x), fy(y), x) for x, y in points]
    lo, hi = raw[0][0], raw[-1][0]
    n = int(math.log2(hi / lo) * PER_OCTAVE)
    out, gaps, j = [], [], 0
    for i in range(n + 1):
        f = lo * 2 ** (i / PER_OCTAVE)
        while j < len(raw) - 2 and raw[j + 1][0] < f:
            j += 1
        (f0, v0, x0), (f1, v1, x1) = raw[j], raw[j + 1]
        if x1 - x0 > GAP_PX and f0 < f < f1:
            g = [round(f0, 1), round(f1, 1)]
            if not gaps or gaps[-1] != g:
                gaps.append(g)
            continue
        t = 0 if f1 == f0 else (math.log(f / f0) / math.log(f1 / f0))
        out.append({"x": round(f, 2), "y": round(v0 + t * (v1 - v0), 2)})
    return out, gaps


def baseline(ys, h):
    """The height most of the words share (within 3 px); the image height when there are none."""
    if not ys:
        return h
    best = max(ys, key=lambda y: sum(1 for v in ys if abs(v - y) <= 3))
    group = [v for v in ys if abs(v - best) <= 3]
    return min(group)


def band_colours(path, img, bands, box, bg_hex):
    """What the band across the plot is made of (a diagnostic written with the reading): the image mode,
    its transparency if any, and the exact colours of the first band with their share of it."""
    import numpy as np
    from PIL import Image
    out = {}
    try:
        im = Image.open(path)
        out["mode"] = im.mode
        if "transparency" in im.info:
            out["transparency"] = str(im.info["transparency"])[:40]
        if im.mode in ("RGBA", "LA"):
            al = np.asarray(im.convert("RGBA"))[:, :, 3]
            out["alpha_min"] = int(al.min()); out["alpha_mean"] = round(float(al.mean()), 1)
            if bands:
                b = bands[0]
                out["alpha_band_mean"] = round(float(al[b[0]:b[1] + 1, box[0]:box[2] + 1].mean()), 1)
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)
    if bands:
        b = bands[0]
        region = img[b[0]:b[1] + 1, box[0]:box[2] + 1].reshape(-1, 3)
        keys, counts = np.unique(region, axis=0, return_counts=True)
        order = counts.argsort()[::-1][:6]
        out["first_band"] = b
        out["colours"] = [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), "share": round(float(counts[i]) / region.shape[0], 3)} for i in order]
        # the band's profile: share of pixels away from the background in a few rows and at a few columns
        bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
        far = np.abs(img - bg).sum(axis=2) >= 40
        out["row_shares"] = {str(y): round(float(far[y, box[0]:box[2] + 1].mean()), 2) for y in range(b[0], b[1] + 1, max(1, (b[1] - b[0]) // 6))}
        out["column_runs"] = {}
        for x in range(box[0] + 100, box[2], max(1, (box[2] - box[0]) // 6)):
            col = far[max(0, b[0] - 10):b[1] + 11, x]
            ys = np.nonzero(col)[0]
            runs = []
            for y in ys:
                if runs and y == runs[-1][1] + 1:
                    runs[-1][1] = int(y)
                else:
                    runs.append([int(y), int(y)])
            out["column_runs"][str(x)] = [[max(0, b[0] - 10) + r0, max(0, b[0] - 10) + r1] for r0, r1 in runs][:12]
    return out


def read_chart(path, ctype):
    import numpy as np
    from PIL import Image
    img = np.asarray(Image.open(path).convert("RGB")).astype(int)
    h, w = img.shape[:2]
    bg, bright, share = CP.background(img)
    box = CP.plot_box(img, bg) or [0, 0, w - 1, h - 1]
    rows, cols, rcol, ccol = CP.grid_lines(img, box, bg)
    # a run taller than a few pixels is not a grid line: the dark watermark band across the HiFiCompass charts
    bands = [r for r in rows if r[1] - r[0] >= 4]
    rows = [r for r in rows if r[1] - r[0] < 4]
    rows = grid_rows_only(img, rows, box)
    left = CP.safe_ocr(path, [0, 0, max(cols[0][0] - 2 if cols else 40, 40), h], w, h)
    bottom = CP.safe_ocr(path, [0, rows[-1][1] + 2 if rows else int(h * 0.9), w, h], w, h)
    xa, ya = x_axis(cols, bottom), y_axis(rows, left)
    rec = {"background": bg, "grid_rows": len(rows), "grid_cols": [c[0] for c in cols], "x_axis": xa, "y_axis": ya,
           "left_labels": [(wd["text"], wd["y"]) for wd in left if "text" in wd], "bottom_labels": [(wd["text"], wd["x"]) for wd in bottom if "text" in wd],
           "bands": bands, "band_colours": band_colours(path, img, bands, box, bg)}
    if not xa or not ya:
        rec["error"] = "axes could not be fitted"
        return rec
    # the frequency labels share one baseline: the plot ends above the largest group of words at one height
    # (a value label of the left axis that strayed into the band below the last grid row is not that group)
    label_top = baseline([wd["y"] for wd in bottom if "text" in wd], h) - 6
    bottom_edge = max(rows[-1][1] + 1, min(label_top, h - 1)) if rows else min(label_top, h - 1)
    plot = [cols[0][0] + 1, rows[0][0] + 1, cols[-1][1] - 1, bottom_edge] if rows and cols else box
    curves = []
    candidates = CP.all_colours(img, plot, bg, top=12)
    # the on-axis response is drawn in the grid's own colour (black on green): read that colour too, off the grid lines
    if ctype == "response" and rcol and not any(c["hex"] == rcol for c in candidates):
        candidates.append({"hex": rcol, "pixels": MIN_CURVE_PIXELS})
    for c in candidates:
        hexv = c["hex"]
        if hexv == ccol or c["pixels"] < MIN_CURVE_PIXELS:
            continue
        if hexv == rcol and ctype != "response":
            continue
        r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
        if max(r, g, b) - min(r, g, b) < 30 and hexv != rcol:
            continue                                   # grey: minor grid, text, anti-aliasing
        pts, runs = read_curve(img, hexv, bg, plot, (rows, cols))
        if len(pts) < 50 or runs >= 3:
            continue                                   # a dotted grid gives several runs per column; a curve gives one
        points, gaps = resample(pts, xa, ya)
        curves.append({"colour": hexv, "pixels": c["pixels"] if hexv != rcol else len(pts), "columns": len(pts), "lines_per_column": runs, "points": points, "gaps": gaps})
    curves.sort(key=lambda c: -c["columns"])
    rec["legend"] = legend(path, img, rows, w, h, bg)
    # every colour the legend names is read as a curve too (H3 in black, H4 in grey): the legend's own
    # names decide, not the colour's saturation
    named = {}
    for wd in rec["legend"]:
        t = wd["text"].upper().strip("(),;:")
        if re.fullmatch(r"H[2-9]|THD", t) and wd.get("colour"):
            named[t] = wd["colour"]
    dist = lambda a, b: sum(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    for name, hexv in named.items():
        if any(dist(hexv, c["colour"]) <= 150 for c in curves):
            continue                                    # already read in a near colour
        pts, runs = read_curve(img, hexv, bg, plot, (rows, cols))
        if len(pts) >= 50 and runs < 3:
            points, gaps = resample(pts, xa, ya)
            curves.append({"colour": hexv, "pixels": len(pts), "columns": len(pts), "lines_per_column": runs, "points": points, "gaps": gaps})
    # every curve gets the legend name whose colour is nearest (one name per curve)
    taken = set()
    for c in sorted(curves, key=lambda c: -c["columns"]):
        best = min(((dist(c["colour"], hexv), name) for name, hexv in named.items() if name not in taken), default=None)
        if best and best[0] <= 200:
            c["name"] = best[1]; taken.add(best[1])
    rec["curves"] = curves
    return rec


def legend(path, img, rows, w, h, bg_hex="#000000"):
    """Words in the band below the grid read with letters allowed (the chart's legend: "H2 H3 THD", the
    title), each with the colour of its own text."""
    import subprocess
    import numpy as np
    from PIL import Image
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    y0 = (rows[-1][1] + 2) if rows else int(h * 0.9)
    if h - y0 < 8:
        return []
    # the band as "distance from the background": text of any colour (grey on green too) becomes dark on white
    band = img[y0:h, 0:w]
    dist = np.abs(band - bg).sum(axis=2)
    gray = (255 - np.clip(dist * 255 / max(1, dist.max()), 0, 255)).astype("uint8")
    im = Image.fromarray(gray)
    im = im.resize((im.width * 3, im.height * 3))
    tmp = path.with_suffix(".legend.png")
    im.save(tmp)
    try:
        out = subprocess.run(["tesseract", str(tmp), "stdout", "--psm", "11", "tsv"], capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    words = []
    for line in out.splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 12 or not f[11].strip() or float(f[10]) < 30:
            continue
        left, top, width, height = (int(v) // 3 for v in f[6:10])
        cx, cy = left + width // 2, y0 + top + height // 2
        # the colour of the word's own pixels (the legend text is drawn in its curve's colour, black included):
        # the most common colour inside the word's box that is not the background
        patch = img[max(0, y0 + top - 1):y0 + top + height + 2, max(0, left - 2):min(w, left + width + 3)].reshape(-1, 3)
        col = None
        if patch.size:
            d = np.abs(patch - bg).sum(axis=1)
            far = patch[d >= 60]
            if far.size:
                # the pixels farthest from the background are the stroke centres: the text's own colour, not the
                # anti-aliased mix with the background
                dd = np.abs(far - bg).sum(axis=1)
                top_q = far[dd >= np.percentile(dd, 80)]
                col = np.median(top_q, axis=0).astype(int)
        words.append({"text": f[11].strip(), "x": cx, "y": cy, "colour": "#%02x%02x%02x" % tuple(int(v) for v in col) if col is not None else None})
    return words


def checks(did, d, ctype, name, rec):
    out = []
    ts = d.get("ts") or {}
    if ctype == "response" and rec.get("curves") and ts.get("sens"):
        m = re.search(r"_(\d+)v(\d*)(?:_|\.)", name)
        volts = float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) if m else None
        c = rec["curves"][0]
        at1k = [p["y"] for p in c["points"] if 900 <= p["x"] <= 1100]
        if at1k and volts:
            v = statistics.mean(at1k)
            expected = ts["sens"] + 20 * math.log10(volts / 2.83)
            out.append({"check": f"{volts:g} V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage)", "read": round(v, 1), "expected": round(expected, 1), "stated_sens": ts["sens"], "difference_db": round(v - expected, 1)})
    if ctype == "impedance" and rec.get("curves"):
        c = max(rec["curves"], key=lambda c: c["pixels"])
        ys = [p["y"] for p in c["points"]]
        if ys and ts.get("Re"):
            out.append({"check": "impedance minimum against Re", "read": round(min(ys), 2), "stated": ts["Re"]})
        if ys and ts.get("Fs"):
            low = [p for p in c["points"] if p["x"] < 2000] or c["points"]
            peak = max(low, key=lambda p: p["y"])
            out.append({"check": "impedance peak against Fs", "read_hz": peak["x"], "read_ohm": peak["y"], "stated_fs": ts["Fs"]})
    return out


def share_names(res):
    """A colour the legend named in one chart names the same colour in the driver's other charts of that
    type when their own legend missed it (the OCR of a legend word fails now and then)."""
    dist = lambda a, b: sum(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    by_type = {}
    for rec in res:
        for c in rec.get("curves", []):
            if c.get("name"):
                by_type.setdefault(rec["type"], {}).setdefault(c["colour"], set()).add(c["name"])
    for rec in res:
        known = by_type.get(rec["type"], {})
        taken = {c["name"] for c in rec.get("curves", []) if c.get("name")}
        for c in rec.get("curves", []):
            if c.get("name"):
                continue
            near = sorted((dist(c["colour"], hexv), hexv) for hexv in known)
            if near and near[0][0] <= 60:
                names = known[near[0][1]] - taken
                if len(names) == 1:
                    c["name"] = next(iter(names)); c["name_from"] = "the legend of another chart of this driver"; taken.add(c["name"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids")
    ap.add_argument("--types", default="response,harmonics,current,impedance")
    ap.add_argument("--limit", type=int, default=0, help="at most N charts of each type per driver (0 = all)")
    ap.add_argument("--out", default=str(ROOT / "capture" / "chart_read.json"))
    a = ap.parse_args()
    ids = [x.strip() for x in (a.ids.split(",") if a.ids else (ROOT / "capture" / "chart_read_request.txt").read_text().splitlines()) if x.strip()]
    types = set(a.types.split(","))
    inv = json.loads((ROOT / "capture" / "inventory.json").read_text())
    db = json.loads((ROOT / "drivers.json").read_text())
    byid = {d["id"]: d for d in db["drivers"]}
    out = {"date": dt.date.today().isoformat(), "drivers": {}}
    last = [0.0]
    for did in ids:
        d = byid.get(did)
        page = next((pg for rec in inv["models"].values() for pg in rec["pages"] if d and pg.get("url") == d.get("source")), None)
        if not page:
            print(f"{did}: no inventory page", flush=True); continue
        charts = [im for im in page["charts"] if not CP.SKIP.search(im["original"]) and CP.chart_type(im["original"]) in types]
        if a.limit:
            groups = {}
            for im in charts:
                groups.setdefault(CP.chart_type(im["original"]), []).append(im)
            charts = [im for g in groups.values() for im in g[:a.limit]]
        print(f"{did}: {len(charts)} charts", flush=True)
        res = []
        with tempfile.TemporaryDirectory() as tmp:
            for im in charts:
                url = im["original"].split("?")[0]
                name = url.rsplit("/", 1)[-1]
                ctype = CP.chart_type(url)
                try:
                    data = CP.fetch(url, last)
                except Exception as e:
                    res.append({"file": name, "url": url, "type": ctype, "error": str(e)}); print(f"  {name}: cannot fetch ({e})", flush=True); continue
                path = Path(tmp) / name
                path.write_bytes(data)
                try:
                    rec = read_chart(path, ctype)
                except Exception as e:
                    rec = {"error": f"read failed: {e}"}
                rec.update({"file": name, "url": url, "type": ctype})
                rec["checks"] = checks(did, d, ctype, name, rec) if not rec.get("error") else []
                cv = rec.get("curves", [])
                print(f"  {name}: legend {[(wd['text'], wd['colour']) for wd in rec.get('legend', [])][:10]} x {rec.get('x_axis')} y {rec.get('y_axis')} curves {[(c['colour'], c['columns'], c['lines_per_column'], len(c['points'])) for c in cv]} checks {rec['checks']} {rec.get('error', '')}", flush=True)
                res.append(rec)
        share_names(res)
        out["drivers"][did] = res
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"written {a.out}")


if __name__ == "__main__":
    main()
