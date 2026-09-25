#!/usr/bin/env python3
"""Extract curve data exactly from the vector graphics of a PDF datasheet (Purifi draws its graphs
as coloured vector paths), so datasheet curves need no pixel extraction.

  python3 watch/pdf_curves.py datasheet.pdf --list
      per page: every figure (caption, plot frame) and the coloured curve paths inside it
  python3 watch/pdf_curves.py datasheet.pdf --figure 7 --x 10:20000:log --y=-80:0:lin
      the curves of figure 7 in data units, as JSON "series" ready for a measurement set

Axis ranges are given on the command line: --x and --y are "value at the frame's left (bottom)
edge : value at the right (top) edge : log|lin". Tick labels are often drawn as glyph outlines, so
they are not read. Write --y=-80:0:lin (with "=") when the first value is negative.

The plot frame is found from the vector lines themselves: the outer rectangle of the plot, or the
extreme grid lines that span it. The frame's edges are taken to be the axis ends you give. When no
frame is found, or a caption could belong to more than one frame, the tool stops and says so;
--frame N picks a frame by the number --list shows.

Curves are the stroked, coloured paths with at least --min-points points (default 20) that are not
straight axis-parallel lines (frame, grid, ticks) and do not end where they start (legend boxes).
Glyph outlines (filled, not stroked) are ignored.
Points are mapped exactly (no pixels), clipped to the frame, and thinned only where they are denser
than 1/48 octave (160 points per decade, the CAPTURE.md upper limit) on a logarithmic axis, or 400
points on a linear one, by interpolating along the drawn line. A path that turns back on itself
(for example the spikes of an intermodulation spectrum) keeps its drawn vertices unthinned.
y is rounded to 0.01, x to 4 significant digits.

Options: --page P (when figure numbers repeat), --frame N, --names red=H2,blue=H3,
--min-points N, --json (with --list).

Needs PyMuPDF (python3 -m pip install pymupdf); the other watch/ scripts use only the standard
library. See CAPTURE.md, "PDF vector data".
"""
import argparse
import json
import math
import re
import sys

try:
    import pymupdf
except ImportError:                                        # pragma: no cover
    sys.exit("watch/pdf_curves.py needs PyMuPDF: python3 -m pip install pymupdf")

TOL = 1.5          # page points: how far two lines may differ and still count as the same edge
MIN_EDGE = 20      # page points: shorter axis-parallel lines are ticks, not frame or grid
NAMED = {"red": (1, 0, 0), "black": (0, 0, 0), "blue": (0, 0, 1), "orange": (1, 0.655, 0.098),
         "purple": (0.749, 0, 1), "green": (0, 1, 0.078), "grey": (0.5, 0.5, 0.5)}
CAPTION = re.compile(r"^\s*Fig(?:ure|\.)?\s*(\d+)", re.I)


def colour_name(c):
    best = min(NAMED, key=lambda n: sum((a - b) ** 2 for a, b in zip(NAMED[n], c)))
    return best if sum((a - b) ** 2 for a, b in zip(NAMED[best], c)) < 0.01 else hexcol(c)


def hexcol(c):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in c)


def bezier(p0, p1, p2, p3, n=6):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t ** 3 * p3.x,
                    u ** 3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t ** 3 * p3.y))
    return out


def vertices(drawing):
    """The drawing's points in drawing order (curve segments sampled)."""
    pts = []

    def add(p):
        if not pts or abs(pts[-1][0] - p[0]) > 1e-6 or abs(pts[-1][1] - p[1]) > 1e-6:
            pts.append(p)
    for it in drawing["items"]:
        if it[0] == "l":
            add((it[1].x, it[1].y)); add((it[2].x, it[2].y))
        elif it[0] == "c":
            add((it[1].x, it[1].y))
            for p in bezier(*it[1:5]):
                add(p)
    return pts


def edges(drawing):
    """Axis-parallel stroked lines of a drawing: [("h", y, x0, x1) | ("v", x, y0, y1)]."""
    out = []
    if drawing.get("color") is None:          # fill only: glyph outlines, backgrounds
        return out
    for it in drawing["items"]:
        if it[0] == "l":
            a, b = it[1], it[2]
            if abs(a.y - b.y) < 0.05 and abs(a.x - b.x) >= MIN_EDGE:
                out.append(("h", (a.y + b.y) / 2, min(a.x, b.x), max(a.x, b.x)))
            elif abs(a.x - b.x) < 0.05 and abs(a.y - b.y) >= MIN_EDGE:
                out.append(("v", (a.x + b.x) / 2, min(a.y, b.y), max(a.y, b.y)))
        elif it[0] == "re":
            r = it[1]
            if r.width >= MIN_EDGE and r.height >= MIN_EDGE:
                out += [("h", r.y0, r.x0, r.x1), ("h", r.y1, r.x0, r.x1), ("v", r.x0, r.y0, r.y1), ("v", r.x1, r.y0, r.y1)]
    return out


def near(a, b):
    return abs(a - b) <= TOL


def find_frames(drawings):
    """Plot frames: groups of horizontal lines sharing their ends and vertical lines sharing their
    ends, meeting at the four corners. Grid lines join the group; the frame is its extreme lines."""
    hs, vs = [], []
    for d in drawings:
        for e in edges(d):
            (hs if e[0] == "h" else vs).append(e)

    def group(lines):
        groups = []
        for _, pos, a, b in lines:
            for g in groups:
                if near(g["a"], a) and near(g["b"], b):
                    g["pos"].append(pos)
                    break
            else:
                groups.append({"a": a, "b": b, "pos": [pos]})
        return [g for g in groups if len(g["pos"]) >= 2]
    frames = []
    for h in group(hs):
        for v in group(vs):
            # plots stacked or side by side can share line ends: keep the lines within each other's span
            ys = [y for y in h["pos"] if v["a"] - TOL <= y <= v["b"] + TOL]
            xs = [x for x in v["pos"] if h["a"] - TOL <= x <= h["b"] + TOL]
            if len(ys) < 2 or len(xs) < 2:
                continue
            top, bottom, left, right = min(ys), max(ys), min(xs), max(xs)
            if near(h["a"], left) and near(h["b"], right) and near(v["a"], top) and near(v["b"], bottom):
                box = (left, top, right, bottom)
                if not any(all(near(p, q) for p, q in zip(box, f)) for f in frames):
                    frames.append(box)
    return sorted(frames, key=lambda f: (round(f[1]), f[0]))


def captions(page):
    out = []
    for b in page.get_text("blocks"):
        m = CAPTION.match(b[4] or "")
        if m:
            out.append({"number": int(m.group(1)), "text": " ".join(b[4].split()), "box": tuple(b[:4])})
    return out


def assign_captions(frames, caps):
    """Match each caption to the nearest frame whose width overlaps it (below the frame first).
    Returns {frame index: caption}; raises ValueError when a caption fits two frames equally well."""
    pairs = []
    for ci, c in enumerate(caps):
        cx0, cy0, cx1, cy1 = c["box"]
        scored = []
        for fi, (x0, y0, x1, y1) in enumerate(frames):
            if min(cx1, x1) - max(cx0, x0) <= 0:
                continue
            if cy0 >= y1 - TOL:
                dist = cy0 - y1                  # caption below the frame (usual)
            elif cy1 <= y0 + TOL:
                dist = (y0 - cy1) + 1000         # above: only when nothing is below
            else:
                continue
            scored.append((dist, fi))
        scored.sort()
        if len(scored) > 1 and abs(scored[0][0] - scored[1][0]) < 2:
            raise ValueError(f"{c['text'][:60]!r} is as close to frame {scored[0][1] + 1} as to frame "
                             f"{scored[1][1] + 1}; pick one with --frame")
        if scored:
            pairs.append((scored[0][0], scored[0][1], ci))
    out, used = {}, set()
    for dist, fi, ci in sorted(pairs):
        if fi not in out and ci not in used:
            out[fi] = caps[ci]
            used.add(ci)
    return out


def curves_in(frame, drawings, min_points):
    x0, y0, x1, y1 = frame
    out = []
    for d in drawings:
        col = d.get("color")
        if col is None or d.get("type") == "f":
            continue
        pts = vertices(d)
        if len(pts) < min_points:
            continue
        if all(abs(a[0] - b[0]) < 0.05 or abs(a[1] - b[1]) < 0.05 for a, b in zip(pts, pts[1:])):
            continue                               # only axis-parallel steps: grid or frame
        if d.get("closePath") or math.dist(pts[0], pts[-1]) < 1:
            continue                               # closed outline: legend box or marker, not a curve
        inside = [p for p in pts if x0 - TOL <= p[0] <= x1 + TOL and y0 - TOL <= p[1] <= y1 + TOL]
        if len(inside) >= 0.8 * len(pts):
            r = d["rect"]
            out.append({"color": tuple(round(v, 3) for v in col), "points": pts, "width": d.get("width"),
                        "box": (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1))})
    return out


def figures(doc, min_points=20):
    """[{page, number, caption, frame, curves}] for every frame (number None when uncaptioned)."""
    out = []
    for pno in range(len(doc)):
        page = doc[pno]
        drawings = page.get_drawings()
        frames = find_frames(drawings)
        try:
            caps = assign_captions(frames, captions(page))
        except ValueError as e:
            caps = {}
            sys.stderr.write(f"page {pno + 1}: {e}\n")
        for fi, fr in enumerate(frames):
            c = caps.get(fi)
            out.append({"page": pno + 1, "frame_index": len(out) + 1, "number": c["number"] if c else None,
                        "caption": c["text"] if c else None, "frame": tuple(round(v, 2) for v in fr),
                        "curves": curves_in(fr, drawings, min_points)})
    return out


def axis(spec, name):
    try:
        a, b, scale = spec.split(":")
        a, b = float(a), float(b)
    except ValueError:
        sys.exit(f"--{name} must be start:end:log or start:end:lin, for example 10:20000:log (got {spec!r})")
    if scale not in ("log", "lin"):
        sys.exit(f"--{name}: the scale must be log or lin, not {scale!r}")
    if scale == "log" and (a <= 0 or b <= 0):
        sys.exit(f"--{name}: a logarithmic axis needs values above 0")
    return a, b, scale


def mapper(lo_pt, hi_pt, a, b, scale):
    """Page coordinate -> value; lo_pt is where value a sits, hi_pt where b sits."""
    if scale == "log":
        la, lb = math.log10(a), math.log10(b)
        return lambda p: 10 ** (la + (p - lo_pt) / (hi_pt - lo_pt) * (lb - la))
    return lambda p: a + (p - lo_pt) / (hi_pt - lo_pt) * (b - a)


def sig(v, n=4):
    return 0.0 if v == 0 else round(v, n - 1 - int(math.floor(math.log10(abs(v)))))


def thin(pts, frame, xscale, xrange):
    """pts in page coordinates, left to right. Resample along the drawn line where denser than the limit."""
    x0, _, x1, _ = frame
    if xscale == "log":
        decades = abs(math.log10(xrange[1]) - math.log10(xrange[0]))
        step_pt = (x1 - x0) / (decades * 160)             # 1/48 octave ~ 160 per decade
    else:
        step_pt = (x1 - x0) / 400
    span = pts[-1][0] - pts[0][0]
    if span <= 0 or len(pts) <= span / step_pt + 1:
        return pts
    out, j = [], 0
    n = int(span / step_pt)
    grid = [pts[0][0] + i * step_pt for i in range(n + 1)] + [pts[-1][0]]
    for gx in grid:
        while j < len(pts) - 2 and pts[j + 1][0] < gx:
            j += 1
        (ax, ay), (bx, by) = pts[j], pts[j + 1]
        y = ay if bx == ax else ay + (by - ay) * (gx - ax) / (bx - ax)
        if not out or gx - out[-1][0] > 1e-9:
            out.append((gx, y))
    return out


def extract(fig, xspec, yspec, names):
    x0, y0, x1, y1 = fig["frame"]
    fx = mapper(x0, x1, *xspec)
    fy = mapper(y1, y0, *yspec)            # bottom edge = first value
    series, notes, count = [], [], {}
    for c in fig["curves"]:
        pts = [(min(max(px, x0), x1), min(max(py, y0), y1)) for px, py in c["points"]
               if x0 - 0.5 <= px <= x1 + 0.5 and y0 - 0.5 <= py <= y1 + 0.5]
        if len(pts) < 2:
            continue
        if pts[0][0] > pts[-1][0]:
            pts.reverse()
        monotonic = all(b[0] - a[0] >= -0.05 for a, b in zip(pts, pts[1:]))
        cname = colour_name(c["color"])
        count[cname] = count.get(cname, 0) + 1
        label = names.get(cname, cname) + (f" {count[cname]}" if count[cname] > 1 else "")
        if monotonic:
            pts = thin(pts, fig["frame"], xspec[2], xspec[:2])
        else:
            notes.append(f"{label}: the line turns back on itself (spectrum or loop); its drawn vertices are kept unthinned")
        series.append({"name": label, "color": hexcol(c["color"]),
                       "points": [{"x": sig(fx(px)), "y": round(fy(py), 2)} for px, py in pts]})
    return series, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true", help="with --list: print JSON")
    ap.add_argument("--figure", type=int)
    ap.add_argument("--frame", type=int, help="frame number as --list shows it")
    ap.add_argument("--page", type=int)
    ap.add_argument("--x")
    ap.add_argument("--y")
    ap.add_argument("--names", default="", help="colour=name pairs, for example red=H2,blue=H3")
    ap.add_argument("--min-points", type=int, default=20)
    a = ap.parse_args()
    try:
        doc = pymupdf.open(a.pdf)
    except Exception as e:
        sys.exit(f"cannot open {a.pdf}: {e}")
    figs = figures(doc, a.min_points)
    if a.page:
        figs = [f for f in figs if f["page"] == a.page]

    if a.list:
        if a.json:
            print(json.dumps([{k: v for k, v in f.items() if k != "curves"} | {"curves": [
                {"color": hexcol(c["color"]), "name": colour_name(c["color"]), "points": len(c["points"]), "box": c["box"]}
                for c in f["curves"]]} for f in figs], indent=1))
            return
        if not figs:
            print("No plot frames found (no rectangle or grid of lines spanning a plot).")
        for f in figs:
            print(f"page {f['page']}  frame {f['frame_index']}  " +
                  (f"{f['caption'][:90]}" if f["number"] else "(no caption found)"))
            print(f"    plot frame {f['frame']} (left, top, right, bottom in page points)")
            for c in f["curves"]:
                print(f"    curve {colour_name(c['color']):>8} {hexcol(c['color'])}  {len(c['points']):4d} points  box {c['box']}")
            if not f["curves"]:
                print("    no coloured curves inside")
        return

    if a.figure is None and a.frame is None:
        sys.exit("give --list, or --figure N (or --frame N) with --x and --y")
    if not (a.x and a.y):
        sys.exit("give the axis ranges: --x start:end:log|lin --y=start:end:log|lin (tick labels are not read)")
    xs, ys = axis(a.x, "x"), axis(a.y, "y")
    if a.frame is not None:
        pick = [f for f in figs if f["frame_index"] == a.frame]
        what = f"frame {a.frame}"
    else:
        pick = [f for f in figs if f["number"] == a.figure]
        what = f"figure {a.figure}"
    if not pick:
        found = sorted({f["number"] for f in figs if f["number"]})
        caps = sorted({c["number"] for p in doc for c in captions(p)})
        if a.figure in caps:
            sys.exit(f"{what}: the caption is there but no plot frame was found next to it (no rectangle or "
                     f"grid of lines spanning the plot). Check with --list; use --frame N if the frame is listed without a caption.")
        sys.exit(f"{what} not found. Figures with a plot frame: {found or 'none'}")
    if len(pick) > 1:
        sys.exit(f"{what} appears on pages {[f['page'] for f in pick]}; add --page")
    fig = pick[0]
    if not fig["curves"]:
        sys.exit(f"{what}: the plot frame {fig['frame']} has no coloured curves with {a.min_points} points or more")
    names = dict(p.split("=", 1) for p in a.names.split(",") if "=" in p)
    series, notes = extract(fig, xs, ys, names)
    print(json.dumps({"figure": fig["number"], "caption": fig["caption"], "page": fig["page"], "frame_pt": fig["frame"],
                      "axes": {"x": {"scale": "log" if xs[2] == "log" else "linear", "range": xs[:2]},
                               "y": {"scale": "log" if ys[2] == "log" else "linear", "range": ys[:2]}},
                      "notes": notes, "series": series}, indent=1))


if __name__ == "__main__":
    main()
