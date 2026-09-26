#!/usr/bin/env python3
"""Scan manufacturer and test-lab sites for driver model numbers.

Compares what it finds with drivers.json, drivers_survey_midbass.json and the
previous scan (watch/state.json), then writes:

  watch/state.json      every model seen so far, per source, with the pages it was seen on
  watch/catalogue.md    every model seen that is not in the database (browse list)
  <--out>               JSON list of findings for watch/open_issues.py

A model is only reported when it appears on one of a source's measurement pages
(see 'measurement_url' in watch/config.json), so a driver that is merely listed
in a shop does not open an issue. Each source is scanned and stored separately.

The first run (no state.json yet) is a baseline: it records everything and
reports nothing as new, so whole back catalogues do not arrive as hundreds of
issues. A source added later gets the same treatment on its first scan.

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

from common import ROOT, STATE, database_keys, key_of, load_config, match_models, pretty

CATALOGUE = ROOT / "watch" / "catalogue.md"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 elementval-drivers-watcher/1.1")
IMAGE = re.compile(r"\.(jpe?g|png|gif|webp|svg|avif)(\?|$)", re.I)   # gallery file names are not products
FOLLOW_HINT = (r"product|produkt|driver|speaker|lautsprecher|chassis|woofer|tweeter|hocht|tieft|mitt|"
               r"mid|bass|satori|ptt|measure|shop|range|series")
MAX_CHILD_SITEMAPS = 40
MAX_FOLLOW_PAGES = 60
DELAY_S = 1.0                 # default pause between pages; a source can set its own 'delay_s'


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


def scan_source(src, patterns, log, aliases=None):
    """Return ({key: {brand, display, urls, measured}}, health) for one source."""
    found, health = {}, {"ok": [], "failed": []}
    host = urllib.parse.urlparse(src["home"]).netloc.removeprefix("www.")
    follow = src.get("follow", FOLLOW_HINT)
    follow = re.compile(follow, re.I) if follow else None
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
            time.sleep(src.get("delay_s", DELAY_S))

        is_index = bool(re.search(r"<sitemapindex\b", text[:2000]))
        is_urlset = bool(re.search(r"<urlset\b", text[:2000]))
        may_follow = follow and not is_urlset and (url in src["start"] or src.get("follow_recursive"))
        for ev, chunk in page_parts(final, text):
            if is_index:
                if child_sitemaps < MAX_CHILD_SITEMAPS and ev not in seen:
                    queue.append(ev)
                    child_sitemaps += 1
                continue
            for pname in src["patterns"]:
                brand, rx = patterns[pname]
                for model in match_models(rx, chunk, aliases):
                    k = key_of(model)
                    rec = found.setdefault(k, {"brand": brand, "display": pretty(model), "urls": [], "measured": []})
                    if "." in model and not ev.endswith(".xml"):
                        rec["display"] = pretty(model)          # prefer the printed form over a slug
                    if ev not in rec["urls"]:
                        rec["urls"].append(ev)
                    evp = urllib.parse.urlparse(ev)
                    if (evp.netloc.removeprefix("www.") == host and src["_measured"].search(evp.path)
                            and ev not in rec["measured"]):
                        rec["measured"].append(ev)          # a measurement page on the source's own site
            # Follow same-site links that match the source's 'follow' pattern.
            if may_follow and not ev.lower().endswith((".pdf", ".jpg", ".png", ".zip", ".xml")):
                p = urllib.parse.urlparse(ev)
                if (p.netloc.removeprefix("www.") == host and follow.search(p.path)
                        and followed < src.get("max_pages", MAX_FOLLOW_PAGES)
                        and ev not in seen and ev not in queue):
                    queue.append(ev)
                    followed += 1
        log(f"  {url} -> {len(found)} models so far")
    return found, health


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="scan and report, but do not write state or catalogue")
    ap.add_argument("--out", default="findings.json")
    ap.add_argument("--summary", default=None, help="append a Markdown report here (e.g. $GITHUB_STEP_SUMMARY)")
    args = ap.parse_args()
    log = lambda s: print(s, flush=True)

    cfg = load_config()
    patterns = cfg["_patterns"]
    ignore = {key_of(x) for x in cfg.get("ignore", [])}
    in_db = database_keys(cfg)
    baseline = not STATE.exists()
    state = {"sources": {}} if baseline else json.loads(STATE.read_text(encoding="utf-8"))
    today = dt.date.today().isoformat()

    # Models already reported (or recorded at the baseline). Older state files without the list
    # count every model they have seen as reported.
    reported = set(state.get("reported") or {k for s in state["sources"].values() for k in s.get("models", {})})
    new_drivers, new_material, health_rows = {}, {}, []

    for src in cfg["sources"]:
        log(f"== {src['name']} ({src['family']})")
        # A source added since the last scan gets its own baseline: its back catalogue is recorded, not reported.
        quiet = baseline or src["name"] not in state["sources"]
        found, health = scan_source(src, patterns, log, cfg["_aliases"])
        n_measured = sum(1 for r in found.values() if r["measured"])
        health_rows.append((src["name"], len(health["ok"]), health["failed"], len(found), n_measured))
        sstate = state["sources"].setdefault(src["name"], {"models": {}})
        sstate["family"] = src["family"]
        sstate["last_scan"] = today
        sstate["last_ok_pages"] = len(health["ok"])
        for k, rec in found.items():
            old = sstate["models"].get(k)
            fresh_measured = [u for u in rec["measured"] if not old or u not in old.get("measured", [])]
            if old is None:
                sstate["models"][k] = {"brand": rec["brand"], "display": rec["display"], "first_seen": today,
                                       "urls": rec["urls"][:25], "measured": rec["measured"][:20]}
            else:
                old["urls"] = (old["urls"] + [u for u in rec["urls"] if u not in old["urls"]])[:50]
                old["measured"] = (old.get("measured", []) + fresh_measured)[:20]
                if rec["measured"] and not old.get("first_measured"):
                    old["first_measured"] = today
                if "." in rec["display"]:
                    old["display"] = rec["display"]
            if rec["measured"]:
                sstate["models"][k].setdefault("first_measured", today)
            if k in ignore or not rec["measured"]:
                continue
            if k in in_db:
                # A driver already in the database: interesting when a source has new measurement pages for it.
                if not quiet and fresh_measured:
                    item = new_material.setdefault(k, {"key": k, "display": rec["display"], "brand": rec["brand"],
                                                       "db_id": in_db[k], "sources": {}})
                    item["sources"].setdefault(src["name"], []).extend(fresh_measured[:10])
            elif k not in reported:
                if not quiet:
                    item = new_drivers.setdefault(k, {"key": k, "display": rec["display"], "brand": rec["brand"],
                                                      "sources": {}})
                    item["sources"].setdefault(src["name"], []).extend(rec["measured"][:10])
    # Everything with a measurement page now counts as reported, so it is never reported twice.
    for s in state["sources"].values():
        reported.update(k for k, m in s["models"].items() if m.get("measured"))
    state["reported"] = sorted(reported)

    findings = {"date": today, "baseline": baseline,
                "new_drivers": sorted(new_drivers.values(), key=lambda x: x["display"]),
                "new_material": sorted(new_material.values(), key=lambda x: x["display"]),
                "health": [{"source": n, "pages_ok": ok, "failed": f, "models": m, "measured": mm}
                           for n, ok, f, m, mm in health_rows]}
    Path(args.out).write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    # Catalogue: everything seen anywhere that is not in the database, measured or not.
    cat = {}
    for sname, s in state["sources"].items():
        for k, m in s["models"].items():
            if k in in_db or k in ignore:
                continue
            c = cat.setdefault(k, {"display": m["display"], "brand": m["brand"], "first_seen": m["first_seen"],
                                   "links": [], "measured": False})
            c["first_seen"] = min(c["first_seen"], m["first_seen"])
            c["measured"] |= bool(m.get("measured"))
            if "." in m["display"]:
                c["display"] = m["display"]
            c["links"].append(f"[{sname}]({(m.get('measured') or m['urls'])[0]})")
    lines = ["# Drivers seen at the watched sources but not in the database",
             "", f"Last scan: {today}. Generated by `watch/watch_sources.py`; do not edit by hand.",
             "Where each one is measured, and by how many sources, is in `watch/coverage.md`.",
             "", f"{len(cat)} models, {sum(c['measured'] for c in cat.values())} of them on a measurement page.",
             "", "| Brand | Model | Measured | First seen | Where |", "|---|---|---|---|---|"]
    for k, c in sorted(cat.items(), key=lambda kv: (kv[1]["brand"], kv[1]["display"])):
        lines.append(f"| {c['brand']} | {c['display']} | {'yes' if c['measured'] else 'no'} | {c['first_seen']} | "
                     f"{' · '.join(c['links'])} |")

    report = [f"## Driver watch {today}{' (baseline run)' if baseline else ''}", "",
              "| Source | Pages read | Pages failed | Models found | On a measurement page |", "|---|---|---|---|---|"]
    for n, ok, failed, m, mm in health_rows:
        report.append(f"| {n} | {ok} | {len(failed)} | {m} | {mm} |")
    report += ["", f"New drivers: **{len(new_drivers)}** · new measurement pages for drivers already in the database: "
                   f"**{len(new_material)}** · models in catalogue: {len(cat)}", ""]
    for d in findings["new_drivers"]:
        report.append(f"- NEW {d['brand']} {d['display']}: " +
                      ", ".join(f"[{s}]({u[0]})" for s, u in d["sources"].items()))
    for d in findings["new_material"]:
        report.append(f"- UPDATE {d['brand']} {d['display']} ({d['db_id']}): " +
                      ", ".join(f"[{s}]({u[0]})" for s, u in d["sources"].items()))
    failed_all = [f"- {n}: {'; '.join(f[:5])}" for n, ok, f, m, mm in health_rows if f]
    if failed_all:
        report += ["", "### Pages that could not be read", *failed_all]
    text = "\n".join(report) + "\n"
    print(text)
    if args.summary:
        with open(args.summary, "a") as fh:
            fh.write(text)

    if not args.dry_run:
        STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        CATALOGUE.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    else:
        print("\n".join(lines))
        Path(args.out).with_suffix(".state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")

    dead = [n for n, ok, f, m, mm in health_rows if ok == 0]
    if len(dead) == len(health_rows):
        print("::error::no source could be read at all", file=sys.stderr)
        return 1
    for n in dead:
        print(f"::warning::source '{n}' could not be read this run", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
