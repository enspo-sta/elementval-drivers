#!/usr/bin/env python3
"""Scan manufacturer and measurement sites for driver model numbers.

Compares what it finds with drivers.json, drivers_survey_midbass.json and the
previous scan (watch/state.json), then writes:

  watch/state.json      every model seen so far, per source, with the pages it was seen on
  watch/catalogue.md    every model seen that is not in the database (browse list)
  <--out>               JSON list of findings for watch/open_issues.py

The first run (no state.json yet) is a baseline: it records everything and
reports nothing as new, so the manufacturers' whole back catalogues do not
arrive as hundreds of issues.

Standard library only. Usage:
  python3 watch/watch_sources.py [--dry-run] [--out findings.json] [--summary summary.md]
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "watch" / "config.json"
STATE = ROOT / "watch" / "state.json"
CATALOGUE = ROOT / "watch" / "catalogue.md"
DATABASES = [ROOT / "drivers.json", ROOT / "drivers_survey_midbass.json"]

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 elementval-drivers-watcher/1.0 "
      "(+https://github.com/enspo-sta/elementval-drivers)")
IMAGE = re.compile(r"\.(jpe?g|png|gif|webp|svg|avif)(\?|$)", re.I)   # gallery file names are not products
FOLLOW_HINT = re.compile(r"product|produkt|driver|speaker|lautsprecher|chassis|woofer|tweeter|hocht|tieft|mitt|mid|bass|satori|ptt|measure|shop|range|series",
                         re.I)
MAX_CHILD_SITEMAPS = 40
MAX_FOLLOW_PAGES = 60
DELAY_S = 1.0


def key_of(model):
    """Canonical identity: upper-case letters and digits only (PTT6.5X04-NAA-08 == ptt6-5x04-naa-08)."""
    return re.sub(r"[^A-Z0-9]", "", model.upper())


def pretty(model):
    """Display form. Slugs such as ptt6-5x04-naa-08 get their decimal point back."""
    m = model.upper().replace(" ", "")
    m = re.sub(r"^PTT(\d{1,2})-(\d{1,2})(?=[A-Z])", r"PTT\1.\2", m)
    return re.sub(r"^(PTT[\d.]+[A-Z])-(\d{2})", r"\1\2", m)       # ptt6.5m-08 -> PTT6.5M08


def fetch(url):
    """GET a page; one retry after 5 s on a server error (5xx) or timeout."""
    try:
        return _fetch(url)
    except (urllib.error.HTTPError, TimeoutError, urllib.error.URLError) as e:
        if isinstance(e, urllib.error.HTTPError) and e.code < 500:
            raise
        if isinstance(e, urllib.error.URLError) and not isinstance(e, urllib.error.HTTPError) \
                and "timed out" not in str(e.reason):
            raise                   # refused / unknown host: retrying will not help
        time.sleep(5)
        return _fetch(url)


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                               "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
            body = gzip.decompress(body)
        return r.geturl(), body.decode(r.headers.get_content_charset() or "utf-8", "replace")


def page_parts(base, text):
    """Yield (evidence_url, text) chunks: every link target, every link label, and the page text."""
    if re.search(r"<(urlset|sitemapindex)\b", text[:2000]):
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text):
            loc = html.unescape(loc)
            if not IMAGE.search(loc):
                yield loc, urllib.parse.unquote(loc)
        return
    for href, label in re.findall(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", text, re.I | re.S):
        url = urllib.parse.urljoin(base, html.unescape(href))
        if IMAGE.search(url):
            continue
        yield url, urllib.parse.unquote(url)
        yield url, html.unescape(re.sub(r"<[^>]+>", " ", label))
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)
    yield base, html.unescape(re.sub(r"<[^>]+>", " ", body))


def match_models(pattern, text):
    """Model numbers in text; a named group 'model' narrows the match to just the model number."""
    for m in pattern.finditer(text):
        yield m.group("model") if "model" in pattern.groupindex else m.group(0)


def scan_source(src, patterns, log):
    """Return ({key: {brand, display, urls}}, health) for one source."""
    found, health = {}, {"ok": [], "failed": []}
    host = urllib.parse.urlparse(src["home"]).netloc.removeprefix("www.")
    queue, seen = list(src["start"]), set()
    child_sitemaps = followed = 0

    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            final, text = fetch(url)
            health["ok"].append(url)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            health["failed"].append(f"{url} ({getattr(e, 'code', '') or e.__class__.__name__})")
            log(f"  ! {url}: {e}")
            continue
        finally:
            time.sleep(DELAY_S)

        is_index = bool(re.search(r"<sitemapindex\b", text[:2000]))
        for ev, chunk in page_parts(final, text):
            if is_index:
                if child_sitemaps < MAX_CHILD_SITEMAPS and ev not in seen:
                    queue.append(ev)
                    child_sitemaps += 1
                continue
            for pname in src["patterns"]:
                brand, rx = patterns[pname]
                for model in match_models(rx, chunk):
                    k = key_of(model)
                    rec = found.setdefault(k, {"brand": brand, "display": pretty(model), "urls": []})
                    if "." in model and not ev.endswith(".xml"):
                        rec["display"] = pretty(model)          # prefer the printed form over a slug
                    if ev not in rec["urls"]:
                        rec["urls"].append(ev)
            # Follow same-site product-looking links from HTML start pages (one level only).
            if (url in src["start"] and not ev.lower().endswith((".pdf", ".jpg", ".png", ".zip", ".xml"))
                    and urllib.parse.urlparse(ev).netloc.removeprefix("www.") == host
                    and FOLLOW_HINT.search(urllib.parse.urlparse(ev).path)
                    and followed < MAX_FOLLOW_PAGES and ev not in seen and ev not in queue
                    and not re.search(r"<urlset\b", text[:2000])):
                queue.append(ev)
                followed += 1
        log(f"  {url} -> {len(found)} models so far")
    return found, health


def database_keys(patterns):
    keys = {}
    for path in DATABASES:
        if not path.exists():
            continue
        for d in json.loads(path.read_text()).get("drivers", []):
            for _, rx in patterns.values():
                for model in match_models(rx, f"{d.get('name', '')} {d.get('id', '')}"):
                    keys.setdefault(key_of(model), d.get("id"))
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="scan and report, but do not write state or catalogue")
    ap.add_argument("--out", default="findings.json")
    ap.add_argument("--summary", default=None, help="append a Markdown report here (e.g. $GITHUB_STEP_SUMMARY)")
    args = ap.parse_args()
    log = lambda s: print(s, flush=True)

    cfg = json.loads(CONFIG.read_text())
    patterns = {n: (p["brand"], re.compile(p["regex"], re.I)) for n, p in cfg["patterns"].items()}
    ignore = {key_of(x) for x in cfg.get("ignore", [])}
    in_db = database_keys(patterns)
    baseline = not STATE.exists()
    state = {"sources": {}} if baseline else json.loads(STATE.read_text())
    today = dt.date.today().isoformat()

    previously_seen = {k for s in state["sources"].values() for k in s.get("models", {})}
    new_drivers, new_material, health_rows = {}, {}, []

    for src in cfg["sources"]:
        log(f"== {src['name']}")
        found, health = scan_source(src, patterns, log)
        health_rows.append((src["name"], len(health["ok"]), health["failed"], len(found)))
        sstate = state["sources"].setdefault(src["name"], {"models": {}})
        sstate["last_scan"] = today
        sstate["last_ok_pages"] = len(health["ok"])
        for k, rec in found.items():
            old = sstate["models"].get(k)
            fresh_urls = [u for u in rec["urls"] if not old or u not in old["urls"]]
            if old is None:
                sstate["models"][k] = {"brand": rec["brand"], "display": rec["display"],
                                       "first_seen": today, "urls": rec["urls"][:25]}
            else:
                old["urls"] = (old["urls"] + fresh_urls)[:50]
                if "." in rec["display"]:
                    old["display"] = rec["display"]
            if baseline or k in ignore:
                continue
            if k in in_db:
                # A driver already in the database: only interesting if a source has new pages/PDFs for it.
                if old is not None and fresh_urls:
                    item = new_material.setdefault(k, {"key": k, "display": rec["display"], "brand": rec["brand"],
                                                       "db_id": in_db[k], "sources": {}})
                    item["sources"].setdefault(src["name"], []).extend(fresh_urls[:10])
            elif k not in previously_seen:
                item = new_drivers.setdefault(k, {"key": k, "display": rec["display"], "brand": rec["brand"],
                                                  "sources": {}})
                item["sources"].setdefault(src["name"], []).extend(rec["urls"][:10])

    findings = {"date": today, "baseline": baseline,
                "new_drivers": sorted(new_drivers.values(), key=lambda x: x["display"]),
                "new_material": sorted(new_material.values(), key=lambda x: x["display"]),
                "health": [{"source": n, "pages_ok": ok, "failed": f, "models": m} for n, ok, f, m in health_rows]}
    Path(args.out).write_text(json.dumps(findings, indent=2, ensure_ascii=False))

    # Catalogue: everything seen anywhere that is not in the database.
    cat = {}
    for sname, s in state["sources"].items():
        for k, m in s["models"].items():
            if k in in_db or k in ignore:
                continue
            c = cat.setdefault(k, {"display": m["display"], "brand": m["brand"], "first_seen": m["first_seen"], "links": []})
            c["first_seen"] = min(c["first_seen"], m["first_seen"])
            if "." in m["display"]:
                c["display"] = m["display"]
            c["links"].append(f"[{sname}]({m['urls'][0]})")
    lines = [f"# Drivers seen at the watched sources but not in the database",
             "", f"Last scan: {today}. Generated by `watch/watch_sources.py`; do not edit by hand.",
             "", f"{len(cat)} models.", "", "| Brand | Model | First seen | Where |", "|---|---|---|---|"]
    for k, c in sorted(cat.items(), key=lambda kv: (kv[1]["brand"], kv[1]["display"])):
        lines.append(f"| {c['brand']} | {c['display']} | {c['first_seen']} | {' · '.join(c['links'])} |")

    report = [f"## Driver watch {today}{' (baseline run)' if baseline else ''}", "",
              "| Source | Pages read | Pages failed | Models found |", "|---|---|---|---|"]
    for n, ok, failed, m in health_rows:
        report.append(f"| {n} | {ok} | {len(failed)} | {m} |")
    report += ["", f"New drivers: **{len(new_drivers)}** · new material for drivers already in the database: "
                   f"**{len(new_material)}** · models in catalogue: {len(cat)}", ""]
    for d in findings["new_drivers"]:
        report.append(f"- NEW {d['brand']} {d['display']}: " +
                      ", ".join(f"[{s}]({u[0]})" for s, u in d["sources"].items()))
    for d in findings["new_material"]:
        report.append(f"- UPDATE {d['brand']} {d['display']} ({d['db_id']}): " +
                      ", ".join(f"[{s}]({u[0]})" for s, u in d["sources"].items()))
    failed_all = [f"- {n}: {'; '.join(f[:5])}" for n, ok, f, m in health_rows if f]
    if failed_all:
        report += ["", "### Pages that could not be read", *failed_all]
    text = "\n".join(report) + "\n"
    print(text)
    if args.summary:
        with open(args.summary, "a") as fh:
            fh.write(text)

    if not args.dry_run:
        STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
        CATALOGUE.write_text("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))

    dead = [n for n, ok, f, m in health_rows if ok == 0]
    if len(dead) == len(health_rows):
        print("::error::no source could be read at all", file=sys.stderr)
        return 1
    for n in dead:
        print(f"::warning::source '{n}' could not be read this run", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
