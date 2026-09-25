#!/usr/bin/env python3
"""Read a curve of one colour from a chart image (HiFiCompass, Erin's Audio Corner, audiohorn).

  python3 capture/image_curves.py colors chart.png --plot 88,40,1240,590
      the most common colours inside the plot area (ignores greys), to find each series' colour
  python3 capture/image_curves.py extract chart.png --plot 88,40,1240,590 --x 20,20000 --xlog \
      --y=-100,0 --color "#e8412c" --name H2 [--tol 60] [--skip x0,y0,x1,y1 ...] > h2.json

  --plot   left,top,right,bottom pixel of the plot frame (where the axis ends sit)
  --x      axis values at the left and right frame edges; --xlog for a logarithmic axis
  --y      axis values at the bottom and top frame edges; write --y=-100,0 (with "=") when the
           first value is negative
  --skip   rectangles to ignore (legend boxes, printed labels), in pixels
Each pixel column's matching pixels give one point (their middle); the result is resampled to
1/24 octave on a logarithmic axis (CAPTURE.md target). Writes {"series": [{"name", "points"}]}.

Needs Pillow and numpy:  pip install pillow numpy
"""
import argparse
import json
import math


def load(path):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB")).astype(int)


def rect(s):
    return [int(float(v)) for v in s.split(",")]


def cmd_colors(a):
    import numpy as np
    img = load(a.image)
    x0, y0, x1, y1 = rect(a.plot)
    px = img[y0:y1, x0:x1].reshape(-1, 3)
    spread = px.max(axis=1) - px.min(axis=1)
    px = px[spread > 40]                            # leave out greys, black and white
    q = (px // 16) * 16 + 8
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = counts.argsort()[::-1][: a.top]
    for k, c in zip(keys[order], counts[order]):
        print("#%02x%02x%02x  %d pixels" % (k[0], k[1], k[2], c))


def cmd_extract(a):
    import numpy as np
    img = load(a.image)
    x0, y0, x1, y1 = rect(a.plot)
    target = np.array([int(a.color[i:i + 2], 16) for i in (1, 3, 5)])
    dist = np.sqrt(((img - target) ** 2).sum(axis=2))
    mask = dist <= a.tol
    for s in a.skip or []:
        sx0, sy0, sx1, sy1 = rect(s)
        mask[sy0:sy1, sx0:sx1] = False
    xa, xb = [float(v) for v in a.x.split(",")]
    ya, yb = [float(v) for v in a.y.split(",")]

    def xval(col):
        t = (col - x0) / (x1 - x0)
        return 10 ** (math.log10(xa) + t * (math.log10(xb) - math.log10(xa))) if a.xlog else xa + t * (xb - xa)

    def yval(row):
        return ya + (y1 - row) / (y1 - y0) * (yb - ya)

    raw = []
    for col in range(x0, x1 + 1):
        rows = np.nonzero(mask[y0:y1 + 1, col])[0]
        if rows.size:
            raw.append((xval(col), yval(y0 + float(np.median(rows)))))
    if a.xlog and raw:
        lo, hi = raw[0][0], raw[-1][0]
        n = int(math.log2(hi / lo) * a.per_octave)
        grid = [lo * 2 ** (i / a.per_octave) for i in range(n + 1)]
        pts = []
        j = 0
        for f in grid:
            while j < len(raw) - 2 and raw[j + 1][0] < f:
                j += 1
            (fa, va), (fb, vb) = raw[j], raw[min(j + 1, len(raw) - 1)]
            if fb == fa:
                pts.append((f, va))
                continue
            if not (fa <= f <= fb):
                continue
            if math.log(fb / fa) > math.log(2) / 12:   # gap wider than 1/12 octave: leave it out
                continue
            t = math.log(f / fa) / math.log(fb / fa)
            pts.append((f, va + t * (vb - va)))
    else:
        pts = raw
    print(json.dumps({"series": [{"name": a.name, "points": [{"x": round(x, 2 if x < 1000 else 1), "y": round(y, 2)} for x, y in pts]}]}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("colors")
    c.add_argument("image")
    c.add_argument("--plot", required=True)
    c.add_argument("--top", type=int, default=12)
    e = sub.add_parser("extract")
    e.add_argument("image")
    e.add_argument("--plot", required=True)
    e.add_argument("--x", required=True)
    e.add_argument("--y", required=True)
    e.add_argument("--xlog", action="store_true")
    e.add_argument("--color", required=True)
    e.add_argument("--name", required=True)
    e.add_argument("--tol", type=float, default=60)
    e.add_argument("--skip", action="append")
    e.add_argument("--per-octave", type=int, default=24)
    a = ap.parse_args()
    {"colors": cmd_colors, "extract": cmd_extract}[a.cmd](a)


if __name__ == "__main__":
    main()
