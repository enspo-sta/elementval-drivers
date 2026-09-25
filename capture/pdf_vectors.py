#!/usr/bin/env python3
"""Read curves that a PDF draws as vector lines (Purifi's datasheets do), exactly, without pixels.

  python3 capture/pdf_vectors.py list  datasheet.pdf --page 5
      every coloured line on the page: id, colour, number of points, where it is on the page
  python3 capture/pdf_vectors.py ticks datasheet.pdf --page 5
      every number printed on the page with its position, to read the axis scales from
  python3 capture/pdf_vectors.py extract datasheet.pdf --page 5 --paths 12,14 --names H2,H3 \
      --x 101.2:20,480.7:20000 --xlog --y 300.5:-100,120.3:0 > curves.json
      page positions -> values: two points per axis ("position:value"); --xlog for a logarithmic
      frequency axis. Writes {"series": [{"name", "points": [{"x","y"}]}]} thinned to at most
      1/48 octave (CAPTURE.md upper limit) on a logarithmic axis.

Needs PyMuPDF:  pip install pymupdf
"""
import argparse
import json
import math
import sys


def open_page(path, page):
    import pymupdf
    doc = pymupdf.open(path)
    if not 1 <= page <= len(doc):
        sys.exit(f"{path} has {len(doc)} pages; --page counts from 1")
    return doc[page - 1]


def path_points(drawing):
    """The drawing's points in order (line ends and curve ends)."""
    pts = []
    for item in drawing["items"]:
        op = item[0]
        if op == "l":
            seg = [item[1], item[2]]
        elif op == "c":
            seg = [item[1], item[4]]
        else:
            continue
        for p in seg:
            if not pts or (abs(pts[-1][0] - p.x) > 1e-6 or abs(pts[-1][1] - p.y) > 1e-6):
                pts.append((p.x, p.y))
    return pts


def hexcolor(c):
    return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in c) if c else "none"


def is_grey(c):
    return c is None or (max(c) - min(c) < 0.08)


def cmd_list(a):
    page = open_page(a.pdf, a.page)
    rows = []
    for i, d in enumerate(page.get_drawings()):
        pts = path_points(d)
        if len(pts) < a.min_points or (is_grey(d.get("color")) and not a.grey):
            continue
        r = d["rect"]
        rows.append({"id": i, "color": hexcolor(d.get("color")), "points": len(pts), "width": round(d.get("width") or 0, 2),
                     "x": [round(r.x0, 1), round(r.x1, 1)], "y": [round(r.y0, 1), round(r.y1, 1)]})
    print(json.dumps(rows, indent=1))


def cmd_ticks(a):
    page = open_page(a.pdf, a.page)
    out = []
    for w in page.get_text("words"):
        txt = w[4].replace(",", ".").replace("−", "-")
        mult = 1000 if txt.lower().endswith("k") else 1
        core = txt[:-1] if mult == 1000 else txt
        try:
            v = float(core) * mult
        except ValueError:
            continue
        out.append({"text": w[4], "value": v, "x_center": round((w[0] + w[2]) / 2, 1), "y_center": round((w[1] + w[3]) / 2, 1)})
    print(json.dumps(out, indent=1))


def calib(spec, log):
    (p0, v0), (p1, v1) = [tuple(map(float, s.split(":"))) for s in spec.split(",")]
    if log:
        l0, l1 = math.log10(v0), math.log10(v1)
        return lambda p: 10 ** (l0 + (p - p0) * (l1 - l0) / (p1 - p0))
    return lambda p: v0 + (p - p0) * (v1 - v0) / (p1 - p0)


def thin_log(points, per_octave=48):
    """Average points that fall in the same 1/48-octave bin (only thins, never invents points)."""
    bins = {}
    for x, y in points:
        if x <= 0:
            continue
        bins.setdefault(math.floor(math.log2(x) * per_octave), []).append((x, y))
    out = []
    for k in sorted(bins):
        b = bins[k]
        out.append((sum(p[0] for p in b) / len(b), sum(p[1] for p in b) / len(b)))
    return out


def cmd_extract(a):
    page = open_page(a.pdf, a.page)
    drawings = page.get_drawings()
    fx, fy = calib(a.x, a.xlog), calib(a.y, a.ylog)
    ids = [int(s) for s in a.paths.split(",")]
    names = a.names.split(",") if a.names else [f"path {i}" for i in ids]
    series = []
    for i, name in zip(ids, names):
        pts = sorted((fx(px), fy(py)) for px, py in path_points(drawings[i]))
        if a.xlog:
            pts = thin_log(pts)
        series.append({"name": name, "points": [{"x": round(x, 2 if x < 1000 else 1), "y": round(y, 2)} for x, y in pts]})
    print(json.dumps({"series": series}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "ticks", "extract"):
        s = sub.add_parser(name)
        s.add_argument("pdf")
        s.add_argument("--page", type=int, required=True)
        if name == "list":
            s.add_argument("--min-points", type=int, default=20)
            s.add_argument("--grey", action="store_true", help="also list grey and black lines (grid, frame)")
        if name == "extract":
            s.add_argument("--paths", required=True)
            s.add_argument("--names")
            s.add_argument("--x", required=True)
            s.add_argument("--y", required=True)
            s.add_argument("--xlog", action="store_true")
            s.add_argument("--ylog", action="store_true")
    a = ap.parse_args()
    {"list": cmd_list, "ticks": cmd_ticks, "extract": cmd_extract}[a.cmd](a)


if __name__ == "__main__":
    main()
