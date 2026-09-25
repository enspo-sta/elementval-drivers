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
SKIP = re.compile(r"_side|_front|_back|_box|title|logo|SoundImports|clarity|eton|wood|acuton|no_data|banner", re.I)


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


def probe(path):
    import numpy as np
    from PIL import Image
    img = np.asarray(Image.open(path).convert("RGB")).astype(int)
    h, w = img.shape[:2]
    fr = frame_of(img)
    rec = {"width": w, "height": h, "frame": fr}
    if fr:
        x0, y0, x1, y1 = fr
        rec["colours"] = colours(img, fr)
        rec["x_labels"] = ocr_words(path, [max(0, x0 - 30), y1 + 1, min(w, x1 + 30), min(h, y1 + 40)])
        rec["y_labels"] = ocr_words(path, [max(0, x0 - 70), max(0, y0 - 12), x0 - 1, min(h, y1 + 12)])
        rec["y_labels_right"] = ocr_words(path, [x1 + 1, max(0, y0 - 12), min(w, x1 + 70), min(h, y1 + 12)])
        rec["top_text"] = " ".join(wd["text"] for wd in ocr_words(path, [0, 0, w, max(1, y0 - 1)]) if "text" in wd)
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", help="record ids, comma-separated (default: capture/chart_probe_request.txt)")
    ap.add_argument("--limit", type=int, default=0, help="at most N charts per driver (0 = all)")
    ap.add_argument("--out", default=str(ROOT / "capture" / "chart_probe.json"))
    a = ap.parse_args()
    ids = [x.strip() for x in (a.ids.split(",") if a.ids else (ROOT / "capture" / "chart_probe_request.txt").read_text().splitlines()) if x.strip()]
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
                if d and pg.get("url") == d.get("source"):
                    page = pg
        if not page:
            print(f"{did}: no inventory page matches the record's source", flush=True); continue
        charts = [im for im in page["charts"] if not SKIP.search(im["original"])]
        if a.limit:
            charts = charts[:a.limit]
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
                print(f"  {name}: {rec.get('width')}x{rec.get('height')} frame {rec.get('frame')} x-labels {[w['text'] for w in rec.get('x_labels', []) if 'text' in w][:14]} y-labels {[w['text'] for w in rec.get('y_labels', []) if 'text' in w][:12]}", flush=True)
                res.append(rec)
        out["drivers"][did] = res
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"written {a.out}")


if __name__ == "__main__":
    main()
