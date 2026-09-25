#!/usr/bin/env python3
"""What a HiFiCompass measurement page offers, for the capture work list.

Runs on GitHub (this repository's cloud sessions cannot reach hificompass.com): finds the measurement
page of each model through the site's sitemap or measurements index, reads it, and writes
capture/inventory.json and capture/inventory.md with, per page: the address, title, headings, every
chart image (address, original address without the Drupal style folder, alt text, the text around
it), every data file linked (.frd, .zma, .txt, .csv, .zip, .pdf), every table as text, and whether
the page mentions a premium or login-only part. Nothing but this inventory is written: no image or
page is stored (the repository is public). Obeys the site's 10-second pause between pages.

  python3 capture/inventory.py --models "BlieSMa M74A, BlieSMa T25A" [--out capture/inventory.json]
"""
import argparse
import datetime as dt
import gzip
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
from common import load_config  # noqa: E402

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 elementval-drivers-inventory/1.0")
DATA_FILE = re.compile(r"\.(frd|zma|txt|csv|zip|pdf|mdat|wav)(\?|$)", re.I)
IMAGE = re.compile(r"\.(png|jpe?g|gif|webp|svg)(\?|$)", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def fetch(url, delay, last):
    gap = last[0] + delay - time.time()
    if gap > 0:
        time.sleep(gap)
    last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip", "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=40) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
            body = gzip.decompress(body)
        return r.geturl(), body.decode(r.headers.get_content_charset() or "utf-8", "replace")


class Page(HTMLParser):
    """Headings, images with the text around them, links, tables and the plain text of a page."""
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.title, self.h1, self.headings, self.images, self.links, self.tables = "", "", [], [], [], []
        self._tag, self._text, self._tbl, self._row, self._cell = [], [], None, None, None
        self._words = []                      # running plain text, to quote the text around each image

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._tag.append(tag)
        if tag in ("script", "style"):
            return
        if tag == "img":
            src = a.get("src") or a.get("data-src") or ""
            if src and not src.startswith("data:"):
                u = urllib.parse.urljoin(self.base, html.unescape(src))
                self.images.append({"src": u, "original": re.sub(r"/styles/[^/]+/public/", "/", u),
                                    "alt": html.unescape(a.get("alt") or ""), "title": html.unescape(a.get("title") or ""),
                                    "width": a.get("width"), "height": a.get("height"),
                                    "before": " ".join(self._words[-30:]), "after_index": len(self._words)})
        if tag == "a" and a.get("href"):
            u = urllib.parse.urljoin(self.base, html.unescape(a["href"]))
            self.links.append({"href": u, "text": ""})
        if tag == "table":
            self._tbl = []
        if tag == "tr" and self._tbl is not None:
            self._row = []
        if tag in ("td", "th") and self._row is not None:
            self._cell = []
        if tag in ("h1", "h2", "h3", "h4", "figcaption", "title"):
            self._text = []

    def handle_endtag(self, tag):
        if self._tag and self._tag[-1] == tag:
            self._tag.pop()
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", " ".join(self._cell)).strip()); self._cell = None
        if tag == "tr" and self._row is not None and self._tbl is not None:
            if any(self._row):
                self._tbl.append(self._row)
            self._row = None
        if tag == "table" and self._tbl is not None:
            if self._tbl:
                self.tables.append(self._tbl)
            self._tbl = None
        if tag in ("h1", "h2", "h3", "h4", "figcaption", "title"):
            t = re.sub(r"\s+", " ", " ".join(self._text)).strip()
            if tag == "title":
                self.title = t
            elif tag == "h1":
                self.h1 = self.h1 or t
            elif t:
                self.headings.append({"level": tag, "text": t})
            self._text = []

    def handle_data(self, data):
        if self._tag and self._tag[-1] in ("script", "style"):
            return
        t = html.unescape(data)
        if self._cell is not None:
            self._cell.append(t)
        if self._text is not None:
            self._text.append(t)
        if self.links and self._tag and "a" in self._tag[-3:]:
            self.links[-1]["text"] += t
        self._words += t.split()

    def finish(self):
        for im in self.images:
            i = im.pop("after_index")
            im["after"] = " ".join(self._words[i:i + 30])
        for l in self.links:
            l["text"] = re.sub(r"\s+", " ", l["text"]).strip()
        return self


def find_pages(models, src, delay, last, log):
    """Measurement-page addresses per model, from the sitemap(s) and the measurements index."""
    rx = re.compile(src["measurement_url"])
    urls = set()
    for start in src["start"]:
        try:
            base, text = fetch(start, delay, last)
        except Exception as e:
            log(f"  cannot read {start}: {e}"); continue
        if re.search(r"<(urlset|sitemapindex)\b", text[:3000]):
            locs = [html.unescape(l) for l in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)]
            children = [l for l in locs if re.search(r"\.xml(\.gz)?(\?|$)", l)]
            for child in children[:40]:
                try:
                    _, t2 = fetch(child, delay, last)
                    locs += [html.unescape(l) for l in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", t2)]
                except Exception as e:
                    log(f"  cannot read {child}: {e}")
            urls |= {l for l in locs if rx.search(l)}
        else:
            for href in re.findall(r"href=[\"']([^\"'#]+)[\"']", text, re.I):
                u = urllib.parse.urljoin(base, html.unescape(href))
                if rx.search(u):
                    urls.add(u.split("#")[0])
    log(f"  {len(urls)} measurement pages known on the site")
    found = {}
    for m in models:
        key = norm(m.split()[-1])                       # the model word: "T25A" of "BlieSMa T25A"
        hits = sorted(u for u in urls if key in norm(u.rsplit("/", 1)[-1]))
        en = [u for u in hits if "/en/" in u]
        found[m] = en or hits
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", required=True, help="comma-separated, e.g. 'BlieSMa M74A, SB Acoustics Satori TW29TX'")
    ap.add_argument("--source", default="HiFiCompass")
    ap.add_argument("--out", default=str(ROOT / "capture" / "inventory.json"))
    ap.add_argument("--md", default=str(ROOT / "capture" / "inventory.md"))
    a = ap.parse_args()
    cfg = load_config()
    src = next(s for s in cfg["sources"] if s["name"] == a.source)
    delay = float(src.get("delay_s", 10))
    last = [0.0]
    log = lambda *x: print(*x, flush=True)
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    log(f"{a.source}: looking for {len(models)} models")
    pages = find_pages(models, src, delay, last, log)
    out = {"date": dt.date.today().isoformat(), "source": a.source, "models": {}}
    for m in models:
        rec = {"pages": []}
        if not pages.get(m):
            log(f"  {m}: no measurement page found")
        for url in pages.get(m, [])[:3]:
            try:
                base, text = fetch(url, delay, last)
            except Exception as e:
                log(f"  {m}: cannot read {url}: {e}")
                rec["pages"].append({"url": url, "error": str(e)}); continue
            p = Page(base); p.feed(text); p.finish()
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)))
            charts = [im for im in p.images if "/sites/default/files/" in im["src"] or IMAGE.search(im["src"]) and not re.search(r"logo|icon|avatar|flag|badge", im["src"], re.I)]
            files = [l for l in p.links if DATA_FILE.search(l["href"])]
            rec["pages"].append({
                "url": base, "title": p.title, "h1": p.h1, "headings": p.headings,
                "charts": charts, "data_files": files, "tables": p.tables,
                "levels_mentioned": sorted({x for x in re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:dB|V\b)", plain)}, key=lambda s: float(s.replace(",", "."))),
                "premium_or_login": bool(re.search(r"premium|log ?in|subscri|paid content|для подписчиков", plain, re.I)),
                "text_length": len(plain),
            })
            log(f"  {m}: {base} — {len(charts)} chart images, {len(files)} data files, {len(p.tables)} tables, {len(p.headings)} headings")
        out["models"][m] = rec
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    lines = [f"# {a.source} inventory ({out['date']})", "", "Written by `capture/inventory.py` on GitHub. What each measurement page offers, for `capture/CHROME_CAPTURE.md`.", ""]
    for m, rec in out["models"].items():
        lines.append(f"## {m}")
        if not rec["pages"]:
            lines.append("No measurement page found on the site."); lines.append(""); continue
        for pg in rec["pages"]:
            if pg.get("error"):
                lines.append(f"- {pg['url']}: {pg['error']}"); continue
            lines.append(f"- Page: <{pg['url']}> — {pg['title']}" + (" — mentions premium or login" if pg["premium_or_login"] else ""))
            lines.append(f"  - Headings: " + " · ".join(h["text"] for h in pg["headings"]))
            lines.append(f"  - Levels mentioned: " + ", ".join(pg["levels_mentioned"]))
            for im in pg["charts"]:
                lines.append(f"  - Chart: <{im['original']}>" + (f" — alt: {im['alt']}" if im["alt"] else "") + (f" — before: “{im['before'][-120:]}”" if im["before"] else ""))
            for f in pg["data_files"]:
                lines.append(f"  - Data file: <{f['href']}> {f['text']}")
            for t in pg["tables"]:
                lines.append("  - Table:")
                for row in t[:40]:
                    lines.append("    | " + " | ".join(row) + " |")
        lines.append("")
    Path(a.md).write_text("\n".join(lines) + "\n")
    log(f"written {a.out} and {a.md}")


if __name__ == "__main__":
    main()
