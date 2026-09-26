#!/usr/bin/env python3
"""Find a manufacturer's datasheet PDF and write what its pages draw, as numbers and text only (runs on GitHub:
this repository's cloud sessions cannot reach Purifi; the PDF itself is never stored or committed).

For every line of capture/datasheet_request.txt ("record-id MODEL [pdf-address]"):
  1. the PDF address: the one given, else the first PDF linked from the manufacturer's product page for MODEL
     (found through the site's sitemap; Purifi: purifi-audio.com),
  2. per page: the page's text (figure captions, the datasheet's version), every number printed on it with its
     position (to read axis scales from), and on pages that speak of angles or off-axis response every coloured
     vector line with its points in page coordinates (Purifi draws its curves as vectors, so they are exact),
and writes capture/datasheet_probe.json. capture/pdf_vectors.py's calibration turns page positions into values.

  python3 capture/datasheet_probe.py [--ids ptt80x04nab01,...]
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
import chart_probe as CP  # noqa: E402  (fetch: a browser's user agent, a pause between requests)
import pdf_vectors as PV  # noqa: E402

SITES = {"purifi": ["https://purifi-audio.com/sitemap.xml", "https://purifi-audio.com/sitemap_index.xml",
                    "https://purifi-audio.com/product-sitemap.xml", "https://purifi-audio.com/page-sitemap.xml"]}
ANGLE = re.compile(r"off[- ]?axis|\bangle|degree|°|\bdeg\b|polar|horizontal|directivity|dispersion", re.I)
norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())


def text_of(data):
    return data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)


def sitemap_urls(starts, last, log):
    urls, seen = set(), set()
    todo = list(starts)
    while todo and len(seen) < 60:
        u = todo.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            t = text_of(CP.fetch(u, last, delay=3.0))
        except Exception as e:  # noqa: BLE001
            log(f"  cannot read {u}: {e}"); continue
        locs = [html.unescape(x) for x in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", t)]
        todo += [x for x in locs if re.search(r"\.xml(\.gz)?$", x) and x not in seen]
        urls |= {x for x in locs if not re.search(r"\.xml(\.gz)?$", x)}
    return urls


def find_pdf(model, urls, last, log):
    """The datasheet PDF for MODEL: a PDF address naming the model, else the PDFs linked from the product page."""
    key = norm(model)
    direct = sorted(u for u in urls if u.lower().endswith(".pdf") and key in norm(u.rsplit("/", 1)[-1]))
    if direct:
        return direct[0], "the sitemap lists it"
    pages = sorted(u for u in urls if key in norm(u))
    for pg in pages[:4]:
        try:
            t = text_of(CP.fetch(pg, last, delay=3.0))
        except Exception as e:  # noqa: BLE001
            log(f"  cannot read {pg}: {e}"); continue
        pdfs = [urllib.parse.urljoin(pg, html.unescape(h)) for h in re.findall(r"href=[\"']([^\"'#]+\.pdf)[\"']", t, re.I)]
        pdfs = sorted(set(pdfs), key=lambda h: (key not in norm(h), "data" not in h.lower(), h))
        if pdfs:
            return pdfs[0], f"linked from {pg}"
    return None, f"no PDF found (product pages tried: {', '.join(pages[:4]) or 'none'})"


def probe_pdf(path):
    import pymupdf
    doc = pymupdf.open(str(path))
    out = {"pages": len(doc), "metadata": {k: v for k, v in (doc.metadata or {}).items() if v}, "page": []}
    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        rec = {"page": i, "text": re.sub(r"[ \t]+", " ", text).strip()[:4000], "size": [round(page.rect.width, 1), round(page.rect.height, 1)]}
        rec["images"] = len(page.get_images())  # a figure drawn as a picture has no vector lines to read
        ticks = []
        for w in page.get_text("words"):
            t = w[4].replace(",", ".").replace("−", "-")
            mult = 1000 if t.lower().endswith("k") else 1
            core = t[:-1] if mult == 1000 else t
            try:
                v = float(core) * mult
            except ValueError:
                continue
            ticks.append({"text": w[4], "value": v, "x": round((w[0] + w[2]) / 2, 1), "y": round((w[1] + w[3]) / 2, 1)})
        rec["ticks"] = ticks
        if ANGLE.search(text):
            paths = []
            for j, d in enumerate(page.get_drawings()):
                pts = PV.path_points(d)
                if len(pts) < 20:
                    continue
                r = d["rect"]
                paths.append({"id": j, "color": PV.hexcolor(d.get("color")), "grey": PV.is_grey(d.get("color")), "width": round(d.get("width") or 0, 2),
                              "rect": [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)],
                              "points": [[round(x, 2), round(y, 2)] for x, y in pts]})
            rec["paths"] = paths
            # the grid: straight grey lines (axis positions for the calibration)
            grid = []
            for d in page.get_drawings():
                if not PV.is_grey(d.get("color")):
                    continue
                for it in d["items"]:
                    if it[0] == "l":
                        a, b = it[1], it[2]
                        if abs(a.x - b.x) < 0.2 or abs(a.y - b.y) < 0.2:
                            grid.append([round(a.x, 1), round(a.y, 1), round(b.x, 1), round(b.y, 1)])
            rec["grid_lines"] = grid[:600]
        out["page"].append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids")
    ap.add_argument("--out", default=str(ROOT / "capture" / "datasheet_probe.json"))
    a = ap.parse_args()
    lines = [x.strip() for x in (ROOT / "capture" / "datasheet_request.txt").read_text().splitlines() if x.strip() and not x.startswith("#")]
    if a.ids:
        want = set(a.ids.split(","))
        lines = [x for x in lines if x.split()[0] in want]
    prev = Path(a.out)
    out = {"date": dt.date.today().isoformat(), "drivers": json.loads(prev.read_text()).get("drivers", {}) if prev.exists() else {}}
    last = [0.0]
    log = lambda m: print(m, flush=True)
    urls = None
    for ln in lines:
        parts = ln.split()
        did, model = parts[0], parts[1]
        url, how = (parts[2], "given") if len(parts) > 2 else (None, "")
        if not url:
            if urls is None:
                urls = sitemap_urls(SITES["purifi"], last, log)
                log(f"{len(urls)} addresses in the sitemaps")
            url, how = find_pdf(model, urls, last, log)
        log(f"{did} {model}: {url} ({how})")
        rec = {"model": model, "pdf": url, "found": how}
        if url:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    p = Path(tmp) / "datasheet.pdf"
                    p.write_bytes(CP.fetch(url, last, delay=3.0))
                    rec.update(probe_pdf(p))
                log(f"  {rec['pages']} pages; pages about angles: {[pg['page'] for pg in rec['page'] if 'paths' in pg]}")
            except Exception as e:  # noqa: BLE001
                rec["error"] = f"{type(e).__name__}: {e}"
                log(f"  {rec['error']}")
        out["drivers"][did] = rec
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False) + "\n")
    print("written", a.out)


if __name__ == "__main__":
    main()
