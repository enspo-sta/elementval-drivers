#!/usr/bin/env python3
"""Measure chart images so curves can be read from them without a person setting the axes by hand.

Runs on GitHub (the cloud sessions cannot reach hificompass.com). For every chart of the drivers named
in capture/chart_probe_request.txt (one record id per line; charts from capture/inventory.json) it
downloads the image to the runner's disk only and records numbers and text about it:
size; the plot frame (the rectangle of long dark axis lines); the curve colours inside the frame; the
axis tick labels read with tesseract along the bottom and left edges, each with its pixel position;
and the text in the top band (the chart's own title). Results go to capture/chart_probe.json. No image
is stored in the repository. Obeys the site's 10-second pause between requests.

  python3 capture/chart_probe.py [--ids m74a-6,t25a-6] [--limit N]
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 elementval-drivers-probe/1.0"
SKIP = re.compile(r"_side|_front|_back|_box|title|logo|SoundImports|clarity|eton|wood|acuton|no_data|banner|_coil\.|_coil\d|_wires\.", re.I)   # photos and banners, not charts (a photo: …_coil.jpg, …_voice_coil2.jpg; the folder voice_coil_curr/ holds charts)


TYPES = [("current", r"chd"), ("impedance", r"impedance|^imp_"), ("intermodulation", r"\d+hz\d|khz|to1|^imd\.|^spectra\."),
         ("harmonics", r"hpf|hd\.png|hd_|vhd|^hd315|^hd20"),
         ("off-axis", r"offaxis|off-axis"),
         # a near-field response (microphone at 5 or 20 mm, one drive voltage) and a one-tone spectrum (one sine, its
         # harmonics, microphone at 20 or 50 mm: mw19tx-4_20mm_2v_40hz.png)
         ("near-response", r"_(?:5|20)mm_\d+v\d*(?:_0grad|_0deg)?\.(?:png|jpg)$"),
         ("spectrum", r"_\d+mm_\d+v\d*_\d+(?:\.\d+)?hz\.(?:png|jpg)$"),
         ("near-field", r"_\d+mm_.*_\d+hz|_5mm_|_20mm_|^nf\."), ("response", r"_0grad|_0deg|^onaxis"),
         ("step", r"step"), ("waterfall", r"waterfall|^wf\."), ("etc", r"_etc|^etc\.")]
# the older HiFiCompass template (one JPEG per quantity, every level on it: onaxis_…jpg, hd315_0.jpg, hd20.jpg,
# chd.jpg, imp_…jpg) is typed by the file name's start


def chart_type(url):
    name = url.split("?")[0].rsplit("/", 1)[-1].lower()      # the file name without the address's ?itok=… part
    for t, rx in TYPES:
        if re.search(rx, name):
            return t
    return "other"


def fetch(url, last, delay=10.0):
    gap = last[0] + delay - time.time()
    if gap > 0:
        time.sleep(gap)
    last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def frame_of(img):
    """The plot frame: the outermost long dark horizontal and vertical lines (left, top, right, bottom)."""
    import numpy as np
    g = img.mean(axis=2)
    dark = g < 110
    h, w = dark.shape
    rows = np.nonzero(dark.sum(axis=1) > 0.5 * w)[0]
    cols = np.nonzero(dark.sum(axis=0) > 0.5 * h)[0]
    if rows.size < 2 or cols.size < 2:
        # fall back to the largest run of dark pixels along the middle row and column
        return None
    return [int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1])]


def colours(img, frame, top=8):
    import numpy as np
    x0, y0, x1, y1 = frame
    px = img[y0 + 2:y1 - 2, x0 + 2:x1 - 2].reshape(-1, 3)
    spread = px.max(axis=1) - px.min(axis=1)
    px = px[spread > 40]
    if not px.size:
        return []
    q = (px // 16) * 16 + 8
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = counts.argsort()[::-1][:top]
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), "pixels": int(counts[i])} for i in order]


def ocr_words(path, crop, scale=3):
    """Words with their boxes (in the full image's pixels) in a crop [x0, y0, x1, y1], read by tesseract."""
    from PIL import Image
    im = Image.open(path).convert("L")
    x0, y0, x1, y1 = crop
    part = im.crop((x0, y0, x1, y1))
    part = part.resize((part.width * scale, part.height * scale))
    tmp = path.with_suffix(".crop.png")
    part.save(tmp)
    try:
        out = subprocess.run(["tesseract", str(tmp), "stdout", "--psm", "11", "-c", "tessedit_char_whitelist=0123456789.,-kKHzdBmsOhm%", "tsv"],
                             capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return [{"error": str(e)}]
    words = []
    for line in out.splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 12 or not f[11].strip():
            continue
        left, top, width, height, conf = int(f[6]), int(f[7]), int(f[8]), int(f[9]), float(f[10])
        words.append({"text": f[11].strip(), "conf": conf, "x": round(x0 + (left + width / 2) / scale), "y": round(y0 + (top + height / 2) / scale)})
    return words


def background(img):
    """The most common colour (the chart's background) and the mean brightness."""
    import numpy as np
    q = (img.reshape(-1, 3) // 8) * 8
    keys, counts = np.unique(q, axis=0, return_counts=True)
    i = counts.argmax()
    return "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), round(float(img.mean()), 1), round(float(counts[i]) / q.shape[0], 3)


def line_candidates(img, bg_dark):
    """Rows and columns that look like axis or grid lines: at least 60 % of their pixels differ from the
    background in the same direction (dark lines on a light chart, light lines on a dark one)."""
    import numpy as np
    g = img.mean(axis=2)
    h, w = g.shape
    mark = (g > 140) if bg_dark else (g < 110)
    rows = [int(r) for r in np.nonzero(mark.sum(axis=1) > 0.6 * w)[0]]
    cols = [int(c) for c in np.nonzero(mark.sum(axis=0) > 0.6 * h)[0]]
    def runs(v):                                        # consecutive pixels become one line: first..last
        out = []
        for x in v:
            if out and x == out[-1][1] + 1:
                out[-1][1] = x
            else:
                out.append([x, x])
        return out[:40]
    return runs(rows), runs(cols)


def frame_from_lines(rows, cols, w, h):
    """The plot frame from the line candidates: the outermost lines that are not at the image edge."""
    rs = [r for r in rows if r[0] > 2 and r[1] < h - 3]
    cs = [c for c in cols if c[0] > 2 and c[1] < w - 3]
    if len(rs) < 2 or len(cs) < 2:
        return None
    return [cs[0][0], rs[0][0], cs[-1][1], rs[-1][1]]


def safe_ocr(path, crop, w, h):
    x0, y0, x1, y1 = [max(0, int(v)) for v in crop]
    x1, y1 = min(w, x1), min(h, y1)
    if x1 - x0 < 8 or y1 - y0 < 6:
        return []
    return ocr_words(path, [x0, y0, x1, y1])


def plot_box(img, bg_hex):
    """The plot area: the bounding box of the rows and columns that are mostly the background colour."""
    import numpy as np
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    near = (np.abs(img - bg).sum(axis=2) < 40)
    h, w = near.shape
    rows = np.nonzero(near.sum(axis=1) > 0.5 * w)[0]
    cols = np.nonzero(near.sum(axis=0) > 0.3 * h)[0]
    if rows.size < 10 or cols.size < 10:
        return None
    return [int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1])]


def grid_lines(img, box, bg_hex):
    """Rows and columns inside the plot area where most pixels differ from the background (grid lines),
    with the colour they share."""
    import numpy as np
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    x0, y0, x1, y1 = box
    sub = img[y0:y1 + 1, x0:x1 + 1]
    diff = np.abs(sub - bg).sum(axis=2) >= 40
    rows = [int(y0 + r) for r in np.nonzero(diff.sum(axis=1) > 0.7 * diff.shape[1])[0]]
    cols = [int(x0 + c) for c in np.nonzero(diff.sum(axis=0) > 0.7 * diff.shape[0])[0]]
    def runs(v):
        out = []
        for x in v:
            if out and x == out[-1][1] + 1:
                out[-1][1] = x
            else:
                out.append([x, x])
        return out
    def colour_at(rs, axis):
        if not rs:
            return None
        r = rs[len(rs) // 2][0]
        line = img[r, x0:x1 + 1] if axis == "row" else img[y0:y1 + 1, r]
        q = (line // 16) * 16 + 8
        keys, counts = np.unique(q, axis=0, return_counts=True)
        return "#%02x%02x%02x" % tuple(int(v) for v in keys[counts.argmax()])
    rr, cc = runs(rows), runs(cols)
    return rr[:400], cc[:400], colour_at(rr, "row"), colour_at(cc, "col")


def all_colours(img, box, bg_hex, top=12):
    """Every colour inside the plot area but the background, greys included (a black or white curve counts)."""
    import numpy as np
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    x0, y0, x1, y1 = box
    px = img[y0 + 2:y1 - 2, x0 + 2:x1 - 2].reshape(-1, 3)
    px = px[np.abs(px - bg).sum(axis=1) >= 40]
    if not px.size:
        return []
    q = (px // 16) * 16 + 8
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = counts.argsort()[::-1][:top]
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), "pixels": int(counts[i])} for i in order]


def probe(path):
    import numpy as np
    from PIL import Image
    img = np.asarray(Image.open(path).convert("RGB")).astype(int)
    h, w = img.shape[:2]
    rec = {"width": w, "height": h}
    bg, bright, share = background(img)
    rec.update({"background": bg, "background_share": share, "mean_brightness": bright})
    box = plot_box(img, bg)
    rec["plot_box"] = box
    if box:
        rr, cc, rcol, ccol = grid_lines(img, box, bg)
        rec.update({"grid_rows": rr, "grid_cols": cc, "grid_row_colour": rcol, "grid_col_colour": ccol})
        rec["colours"] = all_colours(img, box, bg)
    x0, y0, x1, y1 = box or [int(w * 0.08), int(h * 0.06), int(w * 0.97), int(h * 0.9)]
    gr, gc = rec.get("grid_rows") or [], rec.get("grid_cols") or []
    # HiFiCompass charts fill the whole image: the label bands lie left of the first grid column and below
    # the last grid row; the chart's own title sits below the labels
    left_edge = gc[0][0] - 2 if gc else x0 - 1
    bottom_edge = gr[-1][1] + 2 if gr else y1 + 1
    rec["left_words"] = safe_ocr(path, [0, 0, max(left_edge, 40), h], w, h)
    rec["bottom_words"] = safe_ocr(path, [0, bottom_edge, w, h], w, h)
    rec["right_words"] = safe_ocr(path, [(gc[-1][1] + 2) if gc else x1 + 1, 0, w, h], w, h)
    rec["top_words"] = safe_ocr(path, [0, 0, w, max(8, (gr[0][0] - 2) if gr else y0 - 1)], w, h)
    rec["type"] = chart_type(str(path))
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", help="record ids, comma-separated (default: capture/chart_probe_request.txt)")
    ap.add_argument("--limit", type=int, default=0, help="at most N charts of each type per driver (0 = all)")
    ap.add_argument("--out", default=str(ROOT / "capture" / "chart_probe.json"))
    a = ap.parse_args()
    # a request line is a record id, optionally followed by its HiFiCompass page address (for a record captured by
    # hand before, which has no page address of its own)
    lines = [x.strip() for x in (a.ids.split(",") if a.ids else (ROOT / "capture" / "chart_probe_request.txt").read_text().splitlines()) if x.strip() and not x.strip().startswith("#")]
    ids = [ln.split()[0] for ln in lines]
    page_of = {ln.split()[0]: ln.split()[1] for ln in lines if len(ln.split()) > 1}
    inv = json.loads((ROOT / "capture" / "inventory.json").read_text())
    db = json.loads((ROOT / "drivers.json").read_text())
    byid = {d["id"]: d for d in db["drivers"]}
    out = {"date": dt.date.today().isoformat(), "drivers": {}}
    last = [0.0]
    for did in ids:
        d = byid.get(did)
        page = None
        for m, rec in inv["models"].items():
            for pg in rec["pages"]:
                if d and pg.get("url") == (page_of.get(did) or d.get("source")):
                    page = pg
        if not page:
            print(f"{did}: no inventory page matches the record's source", flush=True); continue
        charts = [im for im in page["charts"] if not SKIP.search(im["original"])]
        if a.limit:                                     # a few charts of every type rather than the first N
            groups = {}
            for im in charts:
                groups.setdefault(chart_type(im["original"]), []).append(im)
            charts = [im for g in groups.values() for im in g[:a.limit]]
        print(f"{did}: {len(charts)} charts", flush=True)
        res = []
        with tempfile.TemporaryDirectory() as tmp:
            for im in charts:
                url = im["original"].split("?")[0]
                name = url.rsplit("/", 1)[-1]
                try:
                    data = fetch(url, last)
                except Exception as e:
                    print(f"  {name}: cannot fetch ({e})", flush=True)
                    res.append({"file": name, "url": url, "error": str(e)}); continue
                path = Path(tmp) / name
                path.write_bytes(data)
                try:
                    rec = probe(path)
                except Exception as e:
                    rec = {"error": f"probe failed: {e}"}
                rec.update({"file": name, "url": url, "bytes": len(data)})
                print(f"  {name}: {rec.get('width')}x{rec.get('height')} bg {rec.get('background')} box {rec.get('plot_box')} grid {len(rec.get('grid_rows', []))} rows {len(rec.get('grid_cols', []))} cols colours {[c['hex'] for c in rec.get('colours', [])[:5]]} bottom {[w['text'] for w in rec.get('bottom_words', []) if 'text' in w][:12]} left {[w['text'] for w in rec.get('left_words', []) if 'text' in w][:8]}", flush=True)
                res.append(rec)
        out["drivers"][did] = res
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"written {a.out}")


if __name__ == "__main__":
    main()
