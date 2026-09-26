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
import io
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
import chart_probe as CP  # noqa: E402  (fetch: a browser's user agent, a pause between requests)
import pdf_vectors as PV  # noqa: E402

SITES = {"erin": ["https://www.erinsaudiocorner.com/sitemap.xml", "https://www.erinsaudiocorner.com/driveunits/"],
         "purifi": ["https://purifi-audio.com/sitemap.xml", "https://purifi-audio.com/sitemap_index.xml",
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
        if not locs:  # an HTML index page: its links on the same site
            host = urllib.parse.urlparse(u).netloc
            urls |= {h for h in (urllib.parse.urljoin(u, html.unescape(x)) for x in re.findall(r"href=[\"']([^\"'#]+)[\"']", t))
                     if urllib.parse.urlparse(h).netloc == host}
    return urls


def find_pdf(model, urls, last, log):
    """The datasheet PDF for MODEL: a PDF address naming the model, else the document links of its pages
    (Purifi's shop links datasheets as /web/content/... downloads without a .pdf ending: a link counts only
    when the file it returns starts as a PDF does)."""
    key = norm(model)
    direct = sorted(u for u in urls if u.lower().endswith(".pdf") and key in norm(u.rsplit("/", 1)[-1]))
    if direct:
        return direct[0], "the sitemap lists it", []
    pages = sorted(u for u in urls if key in norm(u))
    seen = []
    for pg in pages[:6]:
        try:
            t = text_of(CP.fetch(pg, last, delay=3.0))
        except Exception as e:  # noqa: BLE001
            log(f"  cannot read {pg}: {e}"); continue
        links = []
        for m in re.finditer(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", t, re.I | re.S):
            h, label = html.unescape(m.group(1)), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
            if re.search(r"\.pdf|/web/content|/documents?/|download|attachment|datasheet|data-sheet", h + " " + label, re.I):
                links.append((urllib.parse.urljoin(pg, h), label[:80]))
        links = sorted(set(links), key=lambda x: ("sheet" not in (x[0] + x[1]).lower(), x[0]))
        seen += [{"page": pg, "href": h, "label": lb} for h, lb in links]
        for h, lb in links[:8]:
            try:
                data = CP.fetch(h, last, delay=3.0)
            except Exception as e:  # noqa: BLE001
                log(f"  cannot read {h}: {e}"); continue
            if data[:5] == b"%PDF-":
                return h, f"linked from {pg} as '{lb}'", seen
    return None, f"no PDF found (product pages tried: {', '.join(pages[:6]) or 'none'})", seen


DATA = re.compile(r"frequency response|\bfrd\b|\bzma\b|impedance data", re.I)
NUM = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")


def table_of(text):
    """A measurement file's rows of numbers (frequency and level, or frequency and ohm; the phase column is counted,
    not kept), written to the precision the database stores (six significant digits of frequency, 0.001 of a unit):
    the committed result holds the numbers the importer needs, not a copy of the file. Also the lines before the rows
    (the header: names the angle, the distance, the units), the file's column count and the most decimals it prints."""
    head, rows, columns, digits = [], [], 0, 0
    for ln in text.splitlines():
        cells = [c for c in re.split(r"[\s,;]+", ln.strip()) if c]
        if len(cells) >= 2 and all(NUM.match(c) for c in cells):
            columns = max(columns, len(cells))
            digits = max(digits, *(len(c.split(".")[1]) if "." in c else 0 for c in cells[:2]))
            rows.append([float(f"{float(cells[0]):.6g}"), round(float(cells[1]), 3)])
        elif ln.strip() and not rows:
            head.append(ln.strip()[:200])
    return head[:20], rows, columns, digits


def probe_data(data, name):
    """The measurement files in a download (a zip of .frd/.zma/.txt files, or one such file)."""
    files = []
    if data[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > 3_000_000:
                    continue
                if not re.search(r"\.(frd|zma|txt|csv|dat)$", info.filename, re.I):
                    files.append({"name": info.filename, "skipped": "not a measurement file"}); continue
                head, rows, cols, digits = table_of(z.read(info).decode("latin-1"))
                files.append({"name": info.filename, "header": head, "columns": cols, "digits": digits, "rows": rows})
    else:
        head, rows, cols, digits = table_of(data.decode("latin-1"))
        files.append({"name": name, "header": head, "columns": cols, "digits": digits, "rows": rows})
    return files


def probe_page(url, last):
    """A measurement page as text: title, headings, every image (address, alt text, caption), links to data files,
    and the sentences that speak of angles (off axis, horizontal, vertical, polar, directivity)."""
    t = text_of(CP.fetch(url, last, delay=3.0))
    strip = lambda x: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
    body = strip(re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t))
    out = {"url": url, "title": strip((re.search(r"(?is)<title>(.*?)</title>", t) or [None, ""])[1]),
           "headings": [strip(h) for h in re.findall(r"(?is)<h[1-4][^>]*>(.*?)</h[1-4]>", t)][:80],
           "images": [], "data_links": [],
           "text": " ".join(m.group(0) for m in re.finditer(r"Frequency Response data is generated[^.]*\.[^.]*\.[^.]*?Data is represented at [^.]*\.[^.]*\.?", body))[:1500],
           "angle_sentences": sorted({m.strip()[:300] for m in re.findall(r"[^.]*\b(?:off[- ]?axis|horizontal|vertical|polar|directivity|spinorama|degrees?)\b[^.]*\.", body, re.I)})[:60]}
    for m in re.finditer(r"(?is)<img\b([^>]*)>", t):
        attrs = dict((k.lower(), html.unescape(v)) for k, v in re.findall(r'([\w-]+)=["\']([^"\']*)["\']', m.group(1)))
        src = attrs.get("src") or attrs.get("data-src") or ""
        if src:
            out["images"].append({"src": urllib.parse.urljoin(url, src), "alt": attrs.get("alt", "")[:200]})
    for h, label in re.findall(r"(?is)<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", t):
        if re.search(r"\.(zip|frd|zma|txt|csv|xlsx?|mdat|pdf)(\?|$)", h, re.I):
            out["data_links"].append({"href": urllib.parse.urljoin(url, html.unescape(h)), "label": strip(label)[:120]})
    return out


def describe_image(path):
    """An image as numbers and text: every word printed on it with its box, the background, the plot box, grid lines
    and colours (capture/chart_probe.py), and a try of the HiFiCompass off-axis reader (capture/chart_read.py)."""
    import subprocess
    import numpy as np
    from PIL import Image
    out = {}
    im = Image.open(path).convert("RGB")
    big = im.resize((im.width * 2, im.height * 2))
    tmp = path.with_suffix(".ocr.png")
    big.save(tmp)
    tsv = subprocess.run([CP.TESSERACT or "tesseract", str(tmp), "stdout", "--psm", "11", "tsv"], capture_output=True, encoding="utf-8", errors="replace", timeout=300).stdout
    words = []
    for row in tsv.splitlines()[1:]:
        c = row.split("\t")
        if len(c) == 12 and c[11].strip() and float(c[10]) > 30:
            x, y, w, h = (int(v) / 2 for v in c[6:10])
            words.append({"text": c[11], "x": round(x), "y": round(y), "w": round(w), "h": round(h), "conf": round(float(c[10]))})
    out["words"] = words
    img = np.asarray(im).astype(int)
    bg, mean, share = CP.background(img)
    out["background"] = {"colour": bg, "mean": mean, "share": share}
    try:
        box = CP.plot_box(img, bg)
        out["plot_box"] = [int(v) for v in box]
        out["grid"] = CP.grid_lines(img, box, bg)
        out["colours"] = CP.all_colours(img, box, bg, top=16)
    except Exception as e:  # noqa: BLE001
        out["plot_error"] = f"{type(e).__name__}: {e}"
    try:
        import chart_read as CR
        # text printed inside the plot is not a curve: the caption ('Mean SPL = 89.1dB (300 - 1000Hz @ 0°)'), a blue
        # 'F3= 54Hz' note, and the legend's labels with the line drawn beside each ('0°', '15°', ...)
        g = out.get("grid") or [[], []]
        mask = []
        if g[0] and g[1]:
            gx0, gx1, gy0, gy1 = g[1][0][0], g[1][-1][1], g[0][0][0], g[0][-1][1]
            for wd in words:
                cx, cy = wd["x"] + wd["w"] / 2, wd["y"] + wd["h"] / 2
                if gx0 < cx < gx1 and gy0 < cy < gy1:
                    extra = 72 if re.match(r"^\d{1,2}°", wd["text"]) else 0      # the legend line left of an angle
                    mask.append([wd["x"] - 3 - extra, wd["y"] - 3, wd["x"] + wd["w"] + 3, wd["y"] + wd["h"] + 3])
        out["mask"] = mask
        rec = CR.read_chart(path, "off-axis-read", mask=mask)
        out["off_axis_read"] = {k: rec.get(k) for k in ("x_axis", "y_axis", "legend", "skipped", "error", "calibration", "plot_floor_row", "masked", "rows_found", "rows_kept", "left_labels")}
        out["off_axis_read"]["curves"] = [{k: c.get(k) for k in ("colour", "name", "columns", "lines_per_column", "gaps", "points", "clipped_top", "clipped_bottom", "on_curve")} for c in rec.get("curves", [])]
    except Exception as e:  # noqa: BLE001
        out["off_axis_read"] = {"error": f"{type(e).__name__}: {e}"}
    out["legend_swatches"] = legend_swatches(img, words, bg)
    return out


def legend_swatches(img, words, bg_hex):
    """For every printed angle ('0°', '15°', ...): the colour of the line drawn beside it (the legend's swatch),
    looked for to the left of the label first, then to the right. Light greys and the background do not count."""
    import numpy as np
    bg = np.array([int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)])
    h, w, _ = img.shape
    out = []
    for wd in words:
        m = re.match(r"^(\d{1,2})°", wd["text"])
        if not m:
            continue
        found = None
        for side in ("left", "right"):
            x0, x1 = (wd["x"] - 70, wd["x"] - 2) if side == "left" else (wd["x"] + wd["w"] + 2, wd["x"] + wd["w"] + 70)
            y0, y1 = wd["y"] - 2, wd["y"] + wd["h"] + 2
            x0, x1, y0, y1 = max(0, x0), min(w, x1), max(0, y0), min(h, y1)
            if x1 - x0 < 5 or y1 - y0 < 3:
                continue
            px = img[y0:y1, x0:x1].reshape(-1, 3)
            spread = px.max(axis=1) - px.min(axis=1)
            keep = px[(np.abs(px - bg).sum(axis=1) >= 60) & ((spread > 60) | (px.max(axis=1) < 90))]
            if len(keep) >= 8:
                q = (keep // 16) * 16 + 8
                keys, counts = np.unique(q, axis=0, return_counts=True)
                found = {"side": side, "colour": "#%02x%02x%02x" % tuple(int(v) for v in keys[counts.argmax()]), "pixels": int(len(keep))}
                break
        out.append({"angle": int(m.group(1)), "text": wd["text"], "x": wd["x"], "y": wd["y"], "swatch": found})
    return out


KEEP = re.compile(r"Setup:|Microphone:|Stimulus:|Gating|^Figure \d+|SPL ?@|Minimum impedance|Maximum impedance|Resonance freq|DC resistance|"
                  r"\(rev\.|\(v\d|Polar angles|Listening Window", re.I)


def excerpt(text):
    """The lines of a datasheet page the importer reads (measurement conditions, figure captions, sensitivity,
    impedance and resonance lines, the version), each with the two lines after it: not the page's whole text."""
    lines = [re.sub(r"[ \t]+", " ", x).strip() for x in text.splitlines()]
    keep = set()
    for i, ln in enumerate(lines):
        if KEEP.search(ln):
            keep.update(range(i, min(len(lines), i + 3)))
    return "\n".join(lines[i] for i in sorted(keep))[:3000]


def probe_pdf(path):
    import pymupdf
    doc = pymupdf.open(str(path))
    out = {"pages": len(doc), "metadata": {k: v for k, v in (doc.metadata or {}).items() if v}, "page": []}
    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        rec = {"page": i, "text": excerpt(text), "size": [round(page.rect.width, 1), round(page.rect.height, 1)]}
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
    ap.add_argument("--keep", help="a directory to keep chart images in (a one-day workflow artifact, never committed)")
    a = ap.parse_args()
    lines = [x.strip() for x in (ROOT / "capture" / "datasheet_request.txt").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    # a line too short for its form is reported and skipped, never a crash after the downloads
    def well_formed(ln):
        p_ = ln.split()
        need = 3 if p_[0] in SITES or p_[0] == "image" else 2
        if len(p_) < need:
            print(f"request line skipped (needs {need} words): {ln}", flush=True)
            return False
        return True
    lines = [x for x in lines if well_formed(x)]
    # "image record-id ADDRESS": a chart image kept for a look (--keep), with its size and colours noted here
    images = [x.split()[1:3] for x in lines if x.split()[0] == "image"]
    lines = [x for x in lines if x.split()[0] != "image"]
    pages = [(site, *rest) for site, rest in ((x.split()[0], x.split()[1:]) for x in lines if x.split()[0] in SITES)]
    lines = [x for x in lines if x.split()[0] not in SITES]
    if a.ids:
        want = set(a.ids.split(","))
        lines = [x for x in lines if x.split()[0] in want]
        pages = [x for x in pages if x[1] in want]
    prev = Path(a.out)
    before = json.loads(prev.read_text(encoding="utf-8")) if prev.exists() else {}
    # the drivers, pages and images requested this run replace their own earlier results; the others stay
    out = {"date": dt.date.today().isoformat(), "drivers": before.get("drivers", {}), "pages": before.get("pages", {})}
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
                out["sitemap_documents"] = sorted(u for u in urls if re.search(r"\.pdf|datasheet|download|/web/content|/documents?/", u, re.I))[:300]
            url, how, links = find_pdf(model, urls, last, log)
        else:
            links = []
        log(f"{did} {model}: {url} ({how})")
        rec = {"model": model, "pdf": url, "found": how, "links": links}
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
        rec["data"] = []
        for ln_ in links:
            if not DATA.search(html.unescape(ln_["label"])):
                continue
            try:
                blob = CP.fetch(ln_["href"], last, delay=3.0)
                files = probe_data(blob, ln_["label"])
                rec["data"].append({"href": ln_["href"], "label": html.unescape(ln_["label"]), "files": files})
                log(f"  data {ln_['label']}: {[(f['name'], len(f.get('rows', []))) for f in files]}")
            except Exception as e:  # noqa: BLE001
                rec["data"].append({"href": ln_["href"], "label": ln_["label"], "error": f"{type(e).__name__}: {e}"})
                log(f"  data {ln_['label']}: {type(e).__name__}: {e}")
        out["drivers"][did] = rec
    site_urls = {}
    for site, did, model, *given in pages:
        if site not in site_urls:
            site_urls[site] = sitemap_urls(SITES[site], last, log) | set()
            log(f"{site}: {len(site_urls[site])} addresses in the sitemaps")
        key = norm(model)
        found = given or sorted(u for u in site_urls[site] if key in norm(u))[:4]
        recs = []
        for u in found:
            try:
                recs.append(probe_page(u, last))
                log(f"{did} {model}: {u}: {len(recs[-1]['images'])} images, {len(recs[-1]['data_links'])} data links, {len(recs[-1]['angle_sentences'])} sentences about angles")
            except Exception as e:  # noqa: BLE001
                recs.append({"url": u, "error": f"{type(e).__name__}: {e}"})
                log(f"{did} {model}: {u}: {type(e).__name__}: {e}")
        if not found:
            log(f"{did} {model}: no page on {site} names the model")
        out["pages"][did] = {"site": site, "model": model, "found": recs,
                             "candidates": sorted(u for u in site_urls[site] if key[:6] in norm(u))[:20]}
    keep = Path(a.keep) if a.keep else None
    if keep:
        keep.mkdir(parents=True, exist_ok=True)
    wanted = [(did, u) for did, u in images]
    for did, pg in out["pages"].items():
        for rec in pg.get("found", []):
            for im in rec.get("images", []):
                if re.search(r"FRonoffaxis|FRnormalized|FR_Linearity", im.get("alt", "")):
                    wanted.append((did, im["src"]))
    fresh_ids = {did for did, _ in wanted}
    out["images"] = [i for i in before.get("images", []) if i.get("id") not in fresh_ids]
    for did, u in wanted:
        try:
            parts_ = urllib.parse.urlsplit(u)
            u = urllib.parse.urlunsplit(parts_._replace(path=urllib.parse.quote(urllib.parse.unquote(parts_.path))))
            data = CP.fetch(u, last, delay=3.0)
            name = f"{did}__" + re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.unquote(u.rsplit("/", 1)[-1].split("?")[0]))
            info = {"id": did, "url": u, "file": name, "bytes": len(data)}
            try:
                from PIL import Image
                with Image.open(io.BytesIO(data)) as img:
                    info["size"] = list(img.size)
            except Exception:  # noqa: BLE001
                pass
            with tempfile.TemporaryDirectory() as tmpd:
                pth = Path(tmpd) / name
                pth.write_bytes(data)
                try:
                    info["describe"] = describe_image(pth)
                except Exception as e:  # noqa: BLE001
                    info["describe"] = {"error": f"{type(e).__name__}: {e}"}
            if keep:
                (keep / name).write_bytes(data)
            out["images"].append(info)
            log(f"image {did}: {u} {info.get('size')} {len(data)} bytes")
        except Exception as e:  # noqa: BLE001
            out["images"].append({"id": did, "url": u, "error": f"{type(e).__name__}: {e}"})
            log(f"image {did}: {u}: {type(e).__name__}: {e}")
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("written", a.out)


if __name__ == "__main__":
    main()
