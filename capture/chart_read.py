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
The green charts are RGBA images with a transparent canvas: under the transparent pixels lie a green field
and a black band across the middle that a browser never shows. Transparent pixels are painted in the
background colour before anything is read, so neither is a grid row or a curve. Solid regions of a colour
are left out of a curve as well (bold text), and where a curve is not visible for more than a few columns
the gap is reported instead of bridged. Everything it writes is numbers and text (capture/chart_read.json);
no image is stored.
  python3 capture/chart_read.py [--ids m74a-6,...] [--types response,near-response,harmonics,current,impedance]
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


def monotone(pairs, increasing=True):
    """The largest subset of (pos, value) pairs whose values run strictly one way with position: an axis
    label split by the OCR ("10000" read as "10" and "00") or misread out of order is left out."""
    import itertools
    pairs = sorted(pairs)
    for n in range(len(pairs), 1, -1):
        for sub in itertools.combinations(pairs, n):
            ok = all((b[1] > a[1]) if increasing else (b[1] < a[1]) for a, b in zip(sub, sub[1:]))
            if ok:
                return list(sub)
    return pairs


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
        near = min(cols, key=lambda c: abs(c[0] - x), default=None)   # the nearest decade line, not the first within reach
        if near and abs(near[0] - x) <= 12:
            pairs.append((near[0], math.log10(v)))
    pairs = monotone(pairs, increasing=True)
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
        near = min(rows, key=lambda r: abs(r[0] - w["y"]), default=None)   # the nearest grid line (a 2-ohm grid is 8 px apart)
        if near and abs(near[0] - w["y"]) <= 9:
            pairs.append((near[0], v))
    pairs = monotone(pairs, increasing=False)
    return fit_line(pairs)


def grid_rows_only(img, rows, box):
    """Which of the candidate rows are grid lines. The grid's colours are the quantised colours that are the
    most common colour of at least three rows (an impedance chart alternates a lighter major and a darker
    minor grey); a row is a grid row when those colours cover at least 30 % of it (the watermark text across
    the middle of a chart covers part of a grid row, the black frame lines and a flat curve none of it).
    Then the grid's spacing is the median over every pair of rows of their distance divided by the whole
    number of steps it spans (robust to a missing row and to an extra one), and a row off that lattice is
    not grid."""
    import numpy as np
    import statistics
    from collections import Counter
    x0, y0, x1, y1 = box
    width = x1 - x0 + 1
    detail = {}
    for r in rows:
        line = img[r[0], x0:x1 + 1]
        q = (line // 32) * 32
        keys, counts = np.unique(q, axis=0, return_counts=True)
        detail[tuple(r)] = {tuple(int(v) for v in k): int(c) for k, c in zip(keys, counts)}
    if not detail:
        return rows
    tops = Counter(max(d, key=d.get) for d in detail.values())
    grid_colours = {c for c, n in tops.items() if n >= 3} or {tops.most_common(1)[0][0]}
    rows = [r for r in rows if sum(detail[tuple(r)].get(c, 0) for c in grid_colours) >= 0.3 * width]
    if len(rows) >= 4:
        ys = [r[0] for r in rows]
        d = statistics.median(b - a for a, b in zip(ys, ys[1:]))
        for _ in range(3):                                # a whole-pixel first guess drifts over 70 rows: refine
            ests = []
            for i in range(len(ys)):
                for j in range(i + 1, len(ys)):
                    span = ys[j] - ys[i]
                    k = round(span / d) if d else 0
                    if k >= 1:
                        ests.append(span / k)
            if not ests:
                break
            d = statistics.median(ests)
        def kept(base):
            return {y for y in ys if abs(((y - base) / d) - round((y - base) / d)) <= 0.25}
        best = max(ys, key=lambda b: len(kept(b)))
        keep = kept(best)
        rows = [r for r in rows if r[0] in keep]
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
    if max(target) - min(target) < 30 and tol == 60:
        tol = 40                                       # a black or grey curve: keep other greys out
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


def off_top(pts, top_edge, bottom_edge=None):
    """Points drawn on the chart's top line are a curve that runs above the chart (cut off there), not a value: they
    are left out (their stretch becomes a gap, reported like any other) and counted. The same for points on the
    floor line (bottom_edge: the last pixel row above it), a curve that runs below the chart."""
    top = [(x, y) for x, y in pts if y > top_edge + 1]
    kept = [(x, y) for x, y in top if bottom_edge is None or y < bottom_edge]
    return kept, (len(pts) - len(top), len(top) - len(kept))


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


def load(path):
    """The image as RGB with its transparent pixels painted in the background colour: the green charts are
    drawn on a transparent canvas (RGBA, most pixels at alpha 0; under them lies a green field and a black
    band that a browser never shows), so only what is actually drawn is left for the grid and curve reading."""
    import numpy as np
    from PIL import Image
    im = Image.open(path)
    rgba = np.asarray(im.convert("RGBA")).astype(int)
    img = rgba[:, :, :3].copy()
    alpha = rgba[:, :, 3]
    clear = alpha < 64
    if im.mode in ("RGBA", "LA", "P") and clear.any():
        bg, _, _ = CP.background(img)
        img[clear] = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return img, im.mode, (round(float(clear.mean()), 3) if clear.any() else 0.0)


def row_detail(img, rows, box):
    """For each grid-row candidate: its height, and the two most common quantised colours along it with
    their counts (a diagnostic written with the reading)."""
    import numpy as np
    x0, y0, x1, y1 = box
    out = []
    for r in rows[:60]:
        line = img[r[0], x0:x1 + 1]
        q = (line // 32) * 32
        keys, counts = np.unique(q, axis=0, return_counts=True)
        order = counts.argsort()[::-1][:2]
        out.append([r[0], r[1] - r[0] + 1] + [["#%02x%02x%02x" % tuple(int(v) for v in keys[i]), int(counts[i])] for i in order])
    return out


def drawn_colours(path, top=10):
    """The exact colours of the drawn pixels (alpha 64 or more) with their counts and mean alpha, or of every
    pixel when the image has no alpha (a diagnostic)."""
    import numpy as np
    from PIL import Image
    im = Image.open(path)
    rgba = np.asarray(im.convert("RGBA"))
    px = rgba.reshape(-1, 4)
    if im.mode in ("RGBA", "LA", "P"):
        px = px[px[:, 3] >= 64]
    keys, inv, counts = np.unique(px[:, :3], axis=0, return_inverse=True, return_counts=True)
    order = counts.argsort()[::-1][:top]
    out = []
    for i in order:
        al = px[inv.ravel() == i, 3]
        out.append({"hex": "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), "pixels": int(counts[i]), "alpha_mean": round(float(al.mean()), 1), "alpha_min": int(al.min())})
    return out


def read_chart(path, ctype, mask=None):
    """mask: boxes [x0, y0, x1, y1] painted in the background colour before the curves are read (text printed
    inside the plot, such as Erin's 'Mean SPL = ...' caption, is not a curve)."""
    import numpy as np
    img, mode, clear_share = load(path)
    h, w = img.shape[:2]
    bg, bright, share = CP.background(img)
    box = CP.plot_box(img, bg) or [0, 0, w - 1, h - 1]
    rows, cols, rcol, ccol = CP.grid_lines(img, box, bg)
    # a run taller than a few pixels is not a grid line: the dark watermark band across the HiFiCompass charts
    bands = [r for r in rows if r[1] - r[0] >= 4]
    rows_all = [r for r in rows if r[1] - r[0] < 4]
    rows = grid_rows_only(img, rows_all, box)
    left = CP.safe_ocr(path, [0, 0, max(cols[0][0] - 2 if cols else 40, 40), h], w, h)
    bottom = CP.safe_ocr(path, [0, rows[-1][1] + 2 if rows else int(h * 0.9), w, h], w, h)
    xa, ya = x_axis(cols, bottom), y_axis(rows, left)
    rec = {"background": bg, "grid_rows": len(rows), "grid_cols": [c[0] for c in cols], "x_axis": xa, "y_axis": ya,
           "left_labels": [(wd["text"], wd["y"]) for wd in left if "text" in wd], "bottom_labels": [(wd["text"], wd["x"]) for wd in bottom if "text" in wd],
           "bands": bands, "band_colours": band_colours(path, img, bands, box, bg), "image_mode": mode, "transparent_share": clear_share,
           "rows_found": [r[0] if r[0] == r[1] else r for r in rows_all][:80], "rows_kept": [r[0] for r in rows][:80], "grid_row_colour": rcol, "grid_col_colour": ccol,
           "rows_detail": row_detail(img, rows_all, box), "drawn_colours": drawn_colours(path)}
    if not xa or not ya:
        rec["error"] = "axes could not be fitted"
        return rec
    # the frequency labels share one baseline: the plot ends above the largest group of words at one height
    # (a value label of the left axis that strayed into the band below the last grid row is not that group)
    label_top = baseline([wd["y"] for wd in bottom if "text" in wd], h) - 6
    # the plot ends just above the chart's floor line (a curve at the floor, -100 dB or 50 dB, is clipped there and
    # is not read as a value). The floor is the bottom frame line, one grid step below the last grey grid row
    # (black on the HiFiCompass charts, so not kept as grid; it carries the lowest label), else the last grid row
    floor_row = rows[-1][0] if rows else None
    if rows and len(rows) > 1:
        step = rows[1][0] - rows[0][0]
        # the lowest line with a value label printed beside it (the labels decide, not the line's colour) ...
        labelled = [r[0] for r in rows_all if r[0] > rows[-1][0] and
                    any("text" in wd and re.fullmatch(r"-?\d+(?:\.\d+)?", wd["text"]) and abs(wd["y"] - r[0]) <= 6 for wd in left)]
        below = [r for r in rows_all if rows[-1][0] + 0.6 * step <= r[0] <= rows[-1][0] + 1.4 * step]
        if labelled:
            floor_row = max(labelled)
        elif below:                                    # ... else the frame line one grid step below the last grid row
            floor_row = min(r[0] for r in below)
    rec["plot_floor_row"] = floor_row
    bottom_edge = min(floor_row - 1, h - 1) if rows else min(label_top, h - 1)
    # the plot starts at the chart's top line, which may be a frame line left out of the grid (the HiFiCompass
    # harmonics charts draw it at -20 dB, 5 dB above the first grey grid line): a curve in that band is read
    top_edge = rows[0][0] + 1 if rows else box[1]
    if rows and len(rows) > 1:
        step = rows[1][0] - rows[0][0]
        above = [r for r in rows_all if rows[0][0] - 1.6 * step <= r[0] < rows[0][0] - 2]
        if above:
            top_edge = min(r[0] for r in above) + 2
    rec["plot_top"] = top_edge
    plot = [cols[0][0] + 1, top_edge, cols[-1][1] - 1, bottom_edge] if rows and cols else box
    if mask:
        bgv = np.array([int(bg[i:i + 2], 16) for i in (1, 3, 5)])
        img = img.copy()
        for x0, y0, x1, y1 in mask:
            img[max(0, int(y0)):int(y1) + 1, max(0, int(x0)):int(x1) + 1] = bgv
        rec["masked"] = [[int(v) for v in b] for b in mask]
    curves = []
    candidates = CP.all_colours(img, plot, bg, top=12)
    dist = lambda a, b: sum(abs(int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) for i in (1, 3, 5))
    for c in candidates:
        hexv = c["hex"]
        if hexv in (ccol, rcol) or c["pixels"] < MIN_CURVE_PIXELS:
            continue
        r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
        grey = max(r, g, b) - min(r, g, b) < 30
        if grey and ctype not in ("response", "off-axis-read"):
            continue                                   # grey: text, anti-aliasing (a grey harmonic is read by its legend name)
        # the on-axis response is a dark-grey line close to the grid's grey: a tolerance below their distance keeps
        # the grid lines out of its mask (they are masked off as well)
        tol = min(60, max(12, int(0.6 * min(dist(hexv, rcol or "#ffffff"), dist(hexv, ccol or "#ffffff"))))) if grey else 60
        pts, runs = read_curve(img, hexv, bg, plot, (rows, cols), tol=tol)
        if len(pts) < 50 or runs >= 3:
            rec.setdefault("skipped", []).append({"colour": hexv, "pixels": c["pixels"], "columns": len(pts), "lines_per_column": runs})
            continue                                   # a dotted grid gives several runs per column; a curve gives one
        pts, clipped = off_top(pts, top_edge, bottom_edge)
        points, gaps = resample(pts, xa, ya)
        curves.append({"colour": hexv, "pixels": c["pixels"] if hexv != rcol else len(pts), "columns": len(pts), "lines_per_column": runs, "points": points, "gaps": gaps,
                       **({"clipped_top": clipped[0]} if clipped[0] else {}), **({"clipped_bottom": clipped[1]} if clipped[1] else {})})
    if ctype == "off-axis-read":
        # one curve per angle, each in a colour of its own: every saturated colour the image draws (the exact colours,
        # not the quantised candidates) that is not a curve yet is tried too
        for dc in rec["drawn_colours"] or []:
            hexv = dc["hex"]
            r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
            if max(r, g, b) - min(r, g, b) < 60 or dc["pixels"] < MIN_CURVE_PIXELS or any(dist(hexv, cv["colour"]) <= 60 for cv in curves):
                continue
            pts, runs = read_curve(img, hexv, bg, plot, (rows, cols))
            if len(pts) >= 50 and runs < 3:
                pts, clipped = off_top(pts, top_edge, bottom_edge)
                points, gaps = resample(pts, xa, ya)
                curves.append({"colour": hexv, "pixels": dc["pixels"], "columns": len(pts), "lines_per_column": runs, "points": points, "gaps": gaps,
                               **({"clipped_top": clipped[0]} if clipped[0] else {}), **({"clipped_bottom": clipped[1]} if clipped[1] else {})})
            else:
                rec.setdefault("skipped", []).append({"colour": hexv, "pixels": dc["pixels"], "columns": len(pts), "lines_per_column": runs})
        for cv in curves:
            cv["legend_text"] = legend_of_colour(path, img, rows, w, h, cv["colour"])
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
        if any(dist(hexv, c["colour"]) <= 150 for c in curves) or hexv in (rcol, ccol):
            continue                                    # already read in a near colour, or the grid's own colour
        pts, runs = read_curve(img, hexv, bg, plot, (rows, cols))
        if len(pts) >= 50 and runs < 3:
            pts, clipped = off_top(pts, top_edge, bottom_edge)
            points, gaps = resample(pts, xa, ya)
            curves.append({"colour": hexv, "pixels": len(pts), "columns": len(pts), "lines_per_column": runs, "points": points, "gaps": gaps,
                           **({"clipped_top": clipped[0]} if clipped[0] else {}), **({"clipped_bottom": clipped[1]} if clipped[1] else {})})
    # every curve gets the legend name whose colour is nearest (one name per curve)
    taken = set()
    for c in sorted(curves, key=lambda c: -c["columns"]):
        best = min(((dist(c["colour"], hexv), name) for name, hexv in named.items() if name not in taken), default=None)
        if best and best[0] <= 200:
            c["name"] = best[1]; taken.add(best[1])
    # the check a person would do by eye: every read point put back on the image, and the share that lands on
    # the curve's own colour (within 2 px); where the curve is drawn under another it counts as a miss
    for c in curves:
        c["on_curve"] = on_curve_share(img, c["colour"], c["points"], xa, ya)
    rec["curves"] = curves
    rec["calibration"] = {"width": w, "height": h, "plot": [int(v) for v in plot], "x": [xa[0], xa[1]], "y": [ya[0], ya[1]]}
    return rec


def on_curve_share(img, colour_hex, points, xa, ya, tol=60, reach=2):
    """Share of the read points that, put back on the image with the axis fits, land within `reach` pixels of a
    pixel of the curve's colour. 1.0 means every point sits on the drawn curve."""
    import numpy as np
    if not points:
        return None
    target = np.array([int(colour_hex[i:i + 2], 16) for i in (1, 3, 5)])
    if max(target) - min(target) < 30:
        tol = 40
    mask = np.sqrt(((img - target) ** 2).sum(axis=2)) <= tol
    h, w = mask.shape
    hits = n = 0
    for p in points:
        if p.get("y") is None or p.get("x", 0) <= 0:
            continue
        x = (math.log10(p["x"]) - xa[0]) / xa[1]
        y = (p["y"] - ya[0]) / ya[1]
        xi, yi = int(round(x)), int(round(y))
        if not (0 <= xi < w and 0 <= yi < h):
            continue
        n += 1
        if mask[max(0, yi - reach):yi + reach + 1, max(0, xi - 1):xi + 2].any():
            hits += 1
    return round(hits / n, 3) if n else None


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
        out = subprocess.run([CP.TESSERACT or "tesseract", str(tmp), "stdout", "--psm", "11", "tsv"], capture_output=True, encoding="utf-8", errors="replace", timeout=120).stdout
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


def legend_of_colour(path, img, rows, w, h, colour_hex, tol=90):
    """The legend text drawn in one colour: the band below the grid with only that colour's pixels kept (black on
    white), read by tesseract. Each off-axis angle's label is in its curve's colour, so this reads one label at a
    time even where the whole band read together loses one (light green on white)."""
    import subprocess
    import numpy as np
    from PIL import Image
    y0 = (rows[-1][1] + 2) if rows else int(h * 0.9)
    if h - y0 < 8:
        return ""
    target = np.array([int(colour_hex[i:i + 2], 16) for i in (1, 3, 5)])
    band = img[y0:h, 0:w, :3].astype(int)
    near = np.abs(band - target).sum(axis=2) <= tol
    if near.sum() < 20:
        return ""
    im = Image.fromarray(np.where(near, 0, 255).astype("uint8"))
    im = im.resize((im.width * 3, im.height * 3))
    tmp = path.with_suffix(".legend_%s.png" % colour_hex.strip("#"))
    im.save(tmp)
    try:
        out = subprocess.run([CP.TESSERACT or "tesseract", str(tmp), "stdout", "--psm", "11"], capture_output=True, encoding="utf-8", errors="replace", timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return re.sub(r"\s+", " ", out).strip()


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
    ap.add_argument("--types", default="response,near-response,off-axis,harmonics,current,impedance")
    ap.add_argument("--limit", type=int, default=0, help="at most N charts of each type per driver (0 = all)")
    ap.add_argument("--out", default=str(ROOT / "capture" / "chart_read.json"))
    ap.add_argument("--keep", help="a directory to keep the fetched images in (a short-lived workflow artifact, never committed)")
    a = ap.parse_args()
    # a request line is a driver id, optionally followed by its HiFiCompass page address (a record captured
    # by hand before has no page address of its own)
    lines = [x.strip() for x in (a.ids.split(",") if a.ids else (ROOT / "capture" / "chart_read_request.txt").read_text(encoding="utf-8").splitlines()) if x.strip() and not x.strip().startswith("#")]
    # a "types: off-axis,response" line in the request reads only those chart types this run
    for ln in [x for x in lines if x.lower().startswith("types:")]:
        a.types = ln.split(":", 1)[1].replace(" ", "")
    lines = [x for x in lines if not x.lower().startswith("types:")]
    ids = [ln.split()[0] for ln in lines]
    page_of = {ln.split()[0]: ln.split()[1] for ln in lines if len(ln.split()) > 1}
    types = set(a.types.split(","))
    inv = json.loads((ROOT / "capture" / "inventory.json").read_text(encoding="utf-8"))
    db = json.loads((ROOT / "drivers.json").read_text(encoding="utf-8"))
    byid = {d["id"]: d for d in db["drivers"]}
    # the drivers requested this time replace their own earlier results; the others' stay as they were read
    prev = Path(a.out)
    out = {"date": dt.date.today().isoformat(), "drivers": json.loads(prev.read_text(encoding="utf-8")).get("drivers", {}) if prev.exists() else {}}
    last = [0.0]
    for did in ids:
        d = byid.get(did)
        want = page_of.get(did) or (d or {}).get("source")
        page = next((pg for rec in inv["models"].values() for pg in rec["pages"] if d and pg.get("url") == want), None)
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
                if a.keep:
                    Path(a.keep).mkdir(parents=True, exist_ok=True)
                    (Path(a.keep) / name).write_bytes(data)
                try:
                    # a near-field response and the off-axis responses (one curve per angle) are drawn like a response
                    rec = read_chart(path, {"near-response": "response", "off-axis": "off-axis-read"}.get(ctype, ctype))
                except Exception as e:
                    rec = {"error": f"read failed: {e}"}
                rec.update({"file": name, "url": url, "type": ctype})
                rec["checks"] = checks(did, d, ctype, name, rec) if not rec.get("error") else []
                cv = rec.get("curves", [])
                print(f"  {name}: legend {[(wd['text'], wd['colour']) for wd in rec.get('legend', [])][:10]} x {rec.get('x_axis')} y {rec.get('y_axis')} curves {[(c['colour'], c['columns'], c['lines_per_column'], len(c['points'])) for c in cv]} checks {rec['checks']} {rec.get('error', '')}", flush=True)
                res.append(rec)
        share_names(res)
        # charts read this run replace their earlier results; the driver's other charts keep theirs
        fresh = {r.get("file") for r in res}
        out["drivers"][did] = [r for r in out["drivers"].get(did, []) if r.get("file") not in fresh] + res
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"written {a.out}")


if __name__ == "__main__":
    main()
