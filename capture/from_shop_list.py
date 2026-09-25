#!/usr/bin/env python3
"""Drivers from a shop's wishlist or cart (read while logged in, on David's computer) into the database.

Reads capture/tlhp_wishlist.json, written by the Chrome routine (capture/CHROME_CAPTURE.md):
  {"date": "2026-09-26", "shop": "Toutlehautparleur", "country": "FR", "currency": "EUR",
   "items": [{"name": "Purifi PTT6.5X04-NAA-08", "url": "https://www.toutlehautparleur.com/...",
              "price_logged_in": 389.0, "price_public": 420.0, "list": "wishlist", "quantity": 1}]}
For every item: the matching record (by model number) gets the shop page in `shop_pages`; a driver not
in the database gets a new record (name, manufacturer, the shop page; no parameters and no measurement
yet: those come from its measurement page through capture/inventory.py and the capture routine); the
logged-in price goes into prices.json as that shop's offer (kept by the weekly scan); new models are
added to capture/inventory_request.txt so GitHub reads their HiFiCompass pages; the work list is rebuilt.

  python3 capture/from_shop_list.py [--list capture/tlhp_wishlist.json] [--root <repository>]
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
import prices as P  # noqa: E402  (models_of, model_regex, norm, to_sek)

TWO_WORD_BRANDS = ["SB Acoustics", "Dayton Audio", "Scan-Speak", "Parts Express", "Peerless by Tymphany", "Eton", "Wavecor", "Audio Technology", "Acoustic Technology"]


def brand_of(name):
    for b in TWO_WORD_BRANDS:
        if name.lower().startswith(b.lower()):
            return b
    return name.split()[0] if name.split() else ""


def record_id(name):
    return re.sub(r"[^a-z0-9.]+", "-", name.lower()).strip("-.")


def match_record(name, drivers):
    """The record whose model number appears in the shop's name for the driver, or None."""
    text = P.norm(name)
    for d in drivers:
        for m in P.models_of(d):
            if P.model_regex(m).search(text):
                return d
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default=None)
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    root = Path(a.root)
    lst = json.loads(Path(a.list or root / "capture" / "tlhp_wishlist.json").read_text())
    shop, country, currency = lst.get("shop", "Toutlehautparleur"), lst.get("country", "FR"), lst.get("currency", "EUR")
    today = lst.get("date") or dt.date.today().isoformat()
    dbp = root / "drivers.json"
    db = json.loads(dbp.read_text())
    drivers = db["drivers"]
    pricesp = root / "prices.json"
    try:
        prices = json.loads(pricesp.read_text())
    except (OSError, ValueError):
        prices = {"meta": {"updated": today, "rates_per_eur": {}, "shops_scanned": [], "notes": []}, "drivers": {}}
    rates = dict(prices.get("meta", {}).get("rates_per_eur") or {}, EUR=1.0)
    reqp = root / "capture" / "inventory_request.txt"
    requested = [l.strip() for l in reqp.read_text().splitlines() if l.strip()] if reqp.exists() else []
    added, matched = [], []
    for item in lst["items"]:
        name = item["name"].strip()
        d = match_record(name, drivers)
        if not d:
            d = {"id": record_id(name), "name": name, "manufacturer": brand_of(name), "role": "", "band": "", "ts": {}, "findings": "",
                 "source": "", "updated": today, "measurements": []}
            drivers.append(d)
            added.append(d["id"])
            if name not in requested:
                requested.append(name)
        else:
            matched.append(d["id"])
        d.setdefault("shop_pages", {})[shop] = item["url"]
        rec = prices["drivers"].setdefault(d["id"], {"name": d["name"], "offers": []})
        rec["offers"] = [o for o in rec["offers"] if o["shop"] != shop]
        public = item.get("price_public")
        logged = item.get("price_logged_in")
        price = public if public is not None else logged
        if price is not None:
            offer = {"shop": shop, "country": country, "url": item["url"], "model": (P.models_of(d) or [name])[0],
                     "price": float(price), "currency": item.get("currency", currency), "availability": item.get("availability"),
                     "login_prices": True, "checked": today, "hand_written": True, "list": item.get("list", "wishlist")}
            if logged is not None:
                offer["price_logged_in"] = float(logged)
            offer["price_sek"] = P.to_sek(offer["price"], offer["currency"], rates) if rates.get("SEK") else None
            rec["offers"].append(offer)
            rec["offers"].sort(key=lambda o: (o.get("price_sek") is None, o.get("price_sek") or o["price"]))
    db["meta"] = dict(db.get("meta") or {}, updated=today)
    dbp.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n")
    pricesp.write_text(json.dumps(prices, indent=1, ensure_ascii=False) + "\n")
    reqp.write_text("\n".join(requested) + "\n")
    print(f"{len(matched)} item(s) matched existing records ({', '.join(matched)}); {len(added)} new record(s) ({', '.join(added) or 'none'}); "
          f"{len(lst['items'])} {shop} offer(s) written; inventory request: {len(requested)} model(s)")
    if root == ROOT:
        subprocess.run([sys.executable, str(ROOT / "watch" / "validate_db.py")], check=True)
        subprocess.run([sys.executable, str(ROOT / "capture" / "worklist.py")], check=True)


if __name__ == "__main__":
    main()
