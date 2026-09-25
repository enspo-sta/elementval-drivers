#!/usr/bin/env python3
"""Find the lowest price of every driver in the database at European shops, and write prices.json.

For each shop in watch/prices_config.json the script reads robots.txt (and obeys it: disallowed
paths are skipped, a crawl delay is honoured), reads the sitemaps, finds the product pages whose
address contains a driver's model number, and reads the price from the page's structured data
(schema.org Product/Offer in JSON-LD, or the product:price meta tags). Prices are converted to
Swedish kronor with the European Central Bank's daily reference rates.

  python3 watch/prices.py                # scan every shop, write prices.json and prices.md
  python3 watch/prices.py --dry-run      # scan and print, write nothing
  python3 watch/prices.py --shop SoundImports --driver ptt525x04naa05   # one shop or driver
  python3 watch/prices.py --summary "$GITHUB_STEP_SUMMARY"             # also append a report

Standard library only. Runs weekly from .github/workflows/prices.yml; the viewer shows the
result on each driver's page. Prices are as found on the day in meta.updated; check the shop
before buying.
"""
import argparse
import datetime as dt
import gzip
import html
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "watch" / "prices_config.json"
OUT = ROOT / "prices.json"
OUT_MD = ROOT / "prices.md"
UA = "elementval-drivers-prices/1.0 (+https://github.com/enspo-sta/elementval-drivers)"
ECB = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
MAX_CHILD_SITEMAPS = 40
MAX_PAGES_PER_SHOP = 120
MAX_HUBS = 8                 # hub pages (brand pages, the front page) followed per shop
MAX_HUB_LINKS = 25           # brand-named links followed from each hub
CURRENCY_SIGNS = {"€": "EUR", "£": "GBP", "EUR": "EUR", "GBP": "GBP", "SEK": "SEK", "DKK": "DKK", "NOK": "NOK", "CHF": "CHF", "PLN": "PLN", "CZK": "CZK"}
TIMEOUT = 30


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- fetching, politely
class Site:
    def __init__(self, shop):
        self.shop = shop
        u = urllib.parse.urlparse(shop["home"])
        self.host = u.netloc
        self.origin = f"{u.scheme}://{u.netloc}"          # robots.txt and the default sitemap live at the root
        self.delay = float(shop.get("delay_s", 3))
        self.last = 0.0
        self.disallow, self.allow, self.sitemaps = [], [], []
        self.fetched = 0
        self.ssl = None                                    # set when the shop's chain needed completing (fix_chain)
        self.read_robots()

    def wait(self):
        gap = self.last + self.delay - time.time()
        if gap > 0:
            time.sleep(gap)
        self.last = time.time()

    def get(self, url, binary=False, retry=False):
        ok, rule = self.rule_for(url)
        if not ok:
            log(f"  {self.shop['name']}: robots.txt disallows {url} (rule: Disallow: {rule})")
            return None
        self.wait()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip", "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=self.ssl) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
                    try:
                        data = gzip.decompress(data)
                    except OSError:
                        pass
                self.fetched += 1
                return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            log(f"  {self.shop['name']}: HTTP {e.code} for {url}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e) and not retry:
                if self.fix_chain(urllib.parse.urlparse(url).netloc):
                    return self.get(url, binary, retry=True)
                other = swap_www(url)                     # the other host form often has a complete certificate chain
                log(f"  {self.shop['name']}: certificate problem at {urllib.parse.urlparse(url).netloc}, trying {urllib.parse.urlparse(other).netloc}")
                return self.get(other, binary, retry=True)
            log(f"  {self.shop['name']}: cannot fetch {url}: {e}")
        return None

    def fix_chain(self, netloc):
        """The server sends an incomplete certificate chain (a common misconfiguration; browsers hide it by
        fetching the missing certificate themselves). Do the same: read the 'CA Issuers' address from the
        certificate, fetch the intermediate certificate(s) and verify against them plus the system roots.
        Verification stays on: nothing is accepted that the system roots do not sign."""
        pems = missing_intermediates(netloc)
        if not pems:
            return False
        ctx = ssl.create_default_context()
        ctx.load_verify_locations(cadata="".join(pems))
        self.ssl = ctx
        log(f"  {self.shop['name']}: {netloc} sends an incomplete certificate chain; fetched {len(pems)} intermediate certificate(s) from the issuer address in the certificate")
        return True

    def _robots(self, origin):
        """("ok", text), ("cert", None) for a certificate problem, or ("none", None) when there is no robots.txt."""
        self.wait()
        req = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=self.ssl) as r:
                return "ok", r.read().decode("utf-8", "replace")
        except Exception as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                return "cert", None
            log(f"  {self.shop['name']}: no robots.txt ({e})")
            return "none", None

    def read_robots(self):
        text = None
        for origin in (self.origin, swap_www(self.origin)):
            state, text = self._robots(origin)
            if state == "cert" and self.fix_chain(urllib.parse.urlparse(origin).netloc):
                state, text = self._robots(origin)
            if state == "none":                          # no robots.txt: everything allowed
                return
            if state == "cert":
                log(f"  {self.shop['name']}: certificate problem at {origin}")
                continue
            if origin != self.origin:
                log(f"  {self.shop['name']}: using {origin} (the other host form failed)")
                self.origin = origin
                self.host = urllib.parse.urlparse(origin).netloc
            break
        if text is None:
            return
        applies = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, val = [s.strip() for s in line.split(":", 1)]
            k = key.lower()
            if k == "user-agent":
                applies = val == "*" or val.lower() in UA.lower()
            elif k == "sitemap":
                self.sitemaps.append(val)
            elif applies and k == "disallow" and val:
                self.disallow.append(val)
            elif applies and k == "allow" and val:
                self.allow.append(val)
            elif applies and k == "crawl-delay":
                try:
                    self.delay = max(self.delay, float(val))
                except ValueError:
                    pass

    def rule_for(self, url):
        """(allowed, the robots.txt rule that decided it or None): the longest matching rule wins."""
        path = urllib.parse.urlparse(url).path or "/"
        best, verdict, which = -1, True, None
        for rule, ok in [(r, False) for r in self.disallow] + [(r, True) for r in self.allow]:
            pat = "^" + re.escape(rule).replace(r"\*", ".*").rstrip("\\$") + ("$" if rule.endswith("$") else "")
            if re.match(pat, path) and len(rule) > best:
                best, verdict, which = len(rule), ok, rule
        return verdict, which

    def allowed(self, url):
        return self.rule_for(url)[0]


# ---------------------------------------------------------------- incomplete certificate chains
def missing_intermediates(netloc, hops=3):
    """PEM texts of the intermediate certificates a server forgot to send: the chain it does send is read
    with openssl, and the 'CA Issuers' address of its last certificate is followed (up to `hops` times), as a
    browser does. Returns [] when openssl is missing, the server cannot be reached or the certificate names
    no issuer address."""
    host, _, port = netloc.partition(":")
    try:
        out = subprocess.run(["openssl", "s_client", "-connect", f"{host}:{port or 443}", "-servername", host, "-showcerts"],
                             input=b"", capture_output=True, timeout=TIMEOUT).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.TimeoutExpired):
        return []
    sent = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----\n?", out, re.S)
    if not sent:
        return []
    pems, last = [], sent[-1]
    for _ in range(hops):
        url = ca_issuers_url(last)
        if not url:
            break
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=TIMEOUT) as r:
                raw = r.read()
        except Exception:
            break
        pem = raw.decode("ascii", "replace") if raw.startswith(b"-----BEGIN") else der_to_pem(raw)
        if not pem or pem in pems:
            break
        pems.append(pem)
        last = pem
    return pems


def ca_issuers_url(pem):
    """The 'CA Issuers' address in a certificate's Authority Information Access extension, or None."""
    try:
        txt = subprocess.run(["openssl", "x509", "-noout", "-text"], input=pem.encode(), capture_output=True, timeout=30).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"CA Issuers - URI:(\S+)", txt)
    return m.group(1) if m else None


def der_to_pem(raw):
    """A certificate (DER) or a PKCS#7 bundle as PEM text, or None."""
    for cmd in (["openssl", "x509", "-inform", "DER"], ["openssl", "pkcs7", "-inform", "DER", "-print_certs"]):
        try:
            r = subprocess.run(cmd, input=raw, capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode == 0 and b"BEGIN CERTIFICATE" in r.stdout:
            return "\n".join(re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", r.stdout.decode("utf-8", "replace"), re.S)) + "\n"
    return None


# ---------------------------------------------------------------- matching model numbers
def swap_www(url):
    u = urllib.parse.urlparse(url)
    host = u.netloc[4:] if u.netloc.startswith("www.") else "www." + u.netloc
    return urllib.parse.urlunparse(u._replace(netloc=host))


def norm(s):
    """lower case, letters and digits kept, every run of other characters becomes one '|'."""
    return re.sub(r"[^a-z0-9]+", "|", s.lower()).strip("|")


def model_regex(model):
    """Matches the model number in a normalised address, with any separators inside it, and a
    separator or the end on both sides (so PTT6.5X04-NAA-08 does not match ...-NAA-08A)."""
    parts = [re.escape(c) for c in re.sub(r"[^a-z0-9]", "", model.lower())]
    return re.compile(r"(?:^|\|)" + r"\|?".join(parts) + r"(?:\||$)")


def models_of(driver):
    """Model numbers to look for: the record's model, plus the base model of a pair or proxy.
    A model is a token with letters and digits (PTT6.5X04-NAA-08, M74T-6); when a name has none
    (Dayton RS 180-4), the last word before the digits and the digits together (RS 180-4)."""
    name = driver.get("name", "")
    body = re.sub(r"\(.*?\)", " ", name)                     # drop "(proxy)", "(Norex)"
    body = re.sub(r"×\s*\d+|\bx\d+\b", " ", body)
    tokens = [t.strip(",.;") for t in body.split()]
    out = []
    for t in tokens:
        if re.search(r"\d", t) and re.search(r"[A-Za-z]", t) and len(t) >= 5 and t not in out:
            out.append(t)
    if not out:
        for i, t in enumerate(tokens):
            if re.search(r"\d", t) and i > 0 and tokens[i - 1].isalpha():
                model = " ".join(tokens[i - 1:i + 1 + sum(1 for u in tokens[i + 1:] if re.search(r"\d", u))])
                if len(re.sub(r"[^A-Za-z0-9]", "", model)) >= 5:
                    out.append(model)
                break
    return out


# ---------------------------------------------------------------- sitemaps
def sitemap_urls(site, url, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if url in seen or depth > 2:
        return []
    seen.add(url)
    data = site.get(url, binary=True)
    if not data:
        return []
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError:
        return []
    tag = root.tag.lower()
    locs = [e.text.strip() for e in root.iter() if e.tag.lower().endswith("}loc") and e.text]
    if not tag.endswith("sitemapindex") and locs and all(re.search(r"\.xml(\.gz)?(\?|$)", l) for l in locs):
        tag = "sitemapindex"                          # a plain list whose entries are themselves sitemaps
    if tag.endswith("sitemapindex"):
        out = []
        children = [l for l in locs if not re.search(r"image|blog|news|cms|category|categories|tag", l, re.I)]
        for child in children[:MAX_CHILD_SITEMAPS]:
            out += sitemap_urls(site, child, depth + 1, seen)
        if len(children) > MAX_CHILD_SITEMAPS:
            log(f"  {site.shop['name']}: only the first {MAX_CHILD_SITEMAPS} of {len(children)} child sitemaps read")
        return out
    return locs


def candidate_pages(site):
    starts = list(site.shop.get("sitemaps") or []) + site.sitemaps
    if not starts:
        starts = [site.origin + p for p in ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml", "/sitemap.xml.gz",
                                            "/sitemaps/sitemap.xml", "/media/sitemap.xml", "/pub/sitemap.xml", "/sitemap_products_1.xml")]
        if site.shop["home"].rstrip("/") != site.origin:
            starts.insert(1, site.shop["home"].rstrip("/") + "/sitemap.xml")
    urls = []
    for s in dict.fromkeys(starts):
        urls += sitemap_urls(site, s)
        if urls and not site.shop.get("sitemaps") and not site.sitemaps:
            break                                     # the first address that works is enough
    host = site.host.lower().removeprefix("www.")
    return list(dict.fromkeys(u for u in urls if u.startswith("http")
                              and urllib.parse.urlparse(u).netloc.lower().removeprefix("www.") == host
                              and not re.search(r"\.(jpe?g|png|gif|webp|svg|pdf|zip|mp4)(\?|$)", u, re.I)))


def links_of(site, url, text):
    """Addresses linked from a page, on the shop's own host, without images, styles or scripts."""
    host = site.host.lower().removeprefix("www.")
    out = []
    for h in re.findall(r'href=["\']([^"\'#>]+)', text, re.I):
        u = urllib.parse.urljoin(url, html.unescape(h.strip())).split("#")[0]
        if u.startswith("http") and urllib.parse.urlparse(u).netloc.lower().removeprefix("www.") == host \
                and not re.search(r"\.(jpe?g|png|gif|webp|svg|pdf|zip|mp4|css|js|ico)(\?|$)", u, re.I):
            out.append(u)
    return list(dict.fromkeys(out))


def crawl_hubs(site, hubs, wanted, makers):
    """Product pages reached from hub pages (a brand page in the sitemap, a page named in the config, or
    the front page when there is no sitemap): the hub's own links that match a model, plus the links of the
    hub's brand-named links. Two levels, bounded by MAX_HUBS and MAX_HUB_LINKS."""
    hits, seen = [], set()
    def match(urls):
        for u in urls:
            n = norm(urllib.parse.urlparse(u).path)
            for did, model, rx in wanted:
                if rx.search(n):
                    hits.append((did, model, u))
    for hub in hubs[:MAX_HUBS]:
        text = site.get(hub)
        if not text:
            continue
        links = links_of(site, hub, text)
        match(links)
        brand = [u for u in links if u != hub and u not in seen and any(m in u.lower() for m in makers)][:MAX_HUB_LINKS]
        for u in brand:
            seen.add(u)
            t2 = site.get(u)
            if t2:
                match(links_of(site, u, t2))
    return list(dict.fromkeys(hits))


def maker_words(drivers):
    """Words that name a manufacturer in an address: 'dayton', 'purifi', 'sbacoustics', ... (short or common words left out)."""
    words = {(d.get("manufacturer") or d.get("name") or "").split()[0].lower() for d in drivers if d.get("name")}
    words = {w for w in words if len(w) >= 4 and w not in ("sound", "group", "audio")}
    return sorted(words | {"sbacoustics", "sb-acoustics", "sb_acoustics", "satori", "bliesma"})


# ---------------------------------------------------------------- prices from a page
def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def to_number(v):
    """A price as printed anywhere in Europe: 329, 329.00, 329,00, 3 495,00, 3.495,00, 3,495.00, 1 234."""
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[\s\u00a0\u202f']", "", str(v or ""))
    m = re.search(r"\d[\d.,]*", s)
    if not m:
        return None
    s = m.group(0).rstrip(".,")
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        s = s.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        s = head.replace(",", "") + ("." + tail if len(tail) != 3 or "," in head else tail)
    elif "." in s:
        head, _, tail = s.rpartition(".")
        if len(tail) == 3 and "." in head:                # 1.234.567
            s = head.replace(".", "") + tail
    try:
        return float(s)
    except ValueError:
        return None


def offers_from_page(text, default_currency=None):
    """[{price, currency, availability}] from JSON-LD, else from meta tags, else from an Odoo price span."""
    out = []
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.S | re.I):
        raw = html.unescape(m.group(1)).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            try:
                data = json.loads(re.sub(r",\s*([}\]])", r"\1", raw))
            except json.JSONDecodeError:
                continue
        for node in walk(data):
            t = node.get("@type")
            types = [t] if isinstance(t, str) else list(t or [])
            if any(x in ("Offer", "AggregateOffer") for x in types):
                price = to_number(node.get("lowPrice") if "lowPrice" in node else node.get("price"))
                cur = node.get("priceCurrency")
                spec = node.get("priceSpecification")
                if price is None and isinstance(spec, (dict, list)):
                    for s in walk(spec):
                        if s.get("price") is not None:
                            price, cur = to_number(s.get("price")), s.get("priceCurrency", cur)
                            break
                if price is not None and cur:
                    avail = str(node.get("availability") or "").split("/")[-1]
                    out.append({"price": price, "currency": str(cur).upper(), "availability": avail or None})
    if not out:
        amount = re.search(r'<meta[^>]+(?:property|name)=["\'](?:product|og):price:amount["\'][^>]+content=["\']([^"\']+)', text, re.I)
        cur = re.search(r'<meta[^>]+(?:property|name)=["\'](?:product|og):price:currency["\'][^>]+content=["\']([^"\']+)', text, re.I)
        if amount and cur:
            p = to_number(amount.group(1))
            if p is not None:
                out.append({"price": p, "currency": cur.group(1).upper(), "availability": None})
    if not out:
        amounts = [to_number(v) for v in re.findall(r'data-price-type="finalPrice"[^>]*data-price-amount="([\d.]+)"', text)]
        amounts += [to_number(v) for v in re.findall(r'"finalPrice"\s*:\s*\{\s*"amount"\s*:\s*"?([\d.]+)', text)]
        amounts = [a for a in amounts if a]
        if amounts:
            cur = re.search(r'"currencyCode"\s*:\s*"([A-Z]{3})"', text) or re.search(r'itemprop=["\']priceCurrency["\'][^>]*content=["\']([^"\']+)', text, re.I)
            out.append({"price": min(amounts), "currency": (cur.group(1) if cur else default_currency or "").upper(),
                        "availability": "OutOfStock" if re.search(r"out of stock|nicht lieferbar|uitverkocht|ausverkauft", text, re.I) else None})
    if not out:
        vals = [to_number(v) for v in re.findall(r'class="[^"]*oe_currency_value[^"]*"[^>]*>\s*([\d.,\s\u00a0]+)\s*<', text)]
        vals = [v for v in vals if v]
        if vals:
            cur = re.search(r'itemprop=["\']priceCurrency["\'][^>]*content=["\']([^"\']+)', text, re.I)
            sym = "EUR" if re.search(r"€|EUR", text) else None
            out.append({"price": min(vals), "currency": (cur.group(1) if cur else sym or default_currency or "").upper(), "availability": None,
                        "prices_on_page": sorted(set(vals))})
    if not out:
        ip = re.search(r'itemprop=["\']price["\'][^>]*content=["\']([^"\']+)', text, re.I)
        ic = re.search(r'itemprop=["\']priceCurrency["\'][^>]*content=["\']([^"\']+)', text, re.I)
        if ip and ic:
            p = to_number(ip.group(1))
            if p is not None:
                out.append({"price": p, "currency": ic.group(1).upper(), "availability": None})
    if not out:
        out += plain_prices(text, default_currency)
    return [o for o in out if o["price"] > 0 and o["currency"]]


AMOUNT = r"(?:€|£|EUR|GBP|SEK|DKK|NOK|CHF|PLN|CZK|kr)\s*(\d[\d\s.,\u00a0]*\d|\d)|(\d[\d\s.,\u00a0]*\d|\d)\s*(?:€|£|EUR|GBP|SEK|DKK|NOK|CHF|PLN|CZK|kr)(?![A-Za-z])"


def plain_prices(text, default_currency=None):
    """Prices from plain shop markup (osCommerce, Zen Cart, older PrestaShop): an element whose class or id
    says 'price' (not shipping or tax), followed within 300 characters by an amount with a currency sign or
    code. The lowest amount in the first currency seen is the price; all amounts are kept for the reader."""
    found = []
    for m in re.finditer(r'<(?:span|div|p|td|b|strong|em|dd|li|h\d)\b[^>]*\b(?:class|id)=["\']([^"\']*price[^"\']*)["\']', text, re.I):
        if re.search(r"ship|deliver|postage|tax|vat|per.?unit|unit.?price|old|regular|before|strike|was|month|instal|klarna|financ|rate", m.group(1), re.I):
            continue
        window = html.unescape(re.sub(r"<[^>]+>", " ", text[m.end():m.end() + 300]))
        # an instalment ("from 17,80 €/month", Finnish "/kk", Swedish "/mån") is not the price
        if re.search(r"/\s*(kk|mån|month|mo|monat|mois|md)\b|per month|kuukau|instal|klarna|financ", window, re.I):
            continue
        for am in re.finditer(AMOUNT, window):
            num = am.group(1) or am.group(2)
            sym = re.search(r"€|£|EUR|GBP|SEK|DKK|NOK|CHF|PLN|CZK|kr", am.group(0)).group(0)
            v = to_number(num)
            if not v:
                continue
            cur = CURRENCY_SIGNS.get(sym.upper()) or (default_currency if default_currency in ("SEK", "DKK", "NOK") else "SEK")
            found.append((v, cur))
            break                                          # one amount per element: the first is the price shown
    if not found:
        return []
    # the first price element on the page is the product's price (the ones after it are related products or
    # other amounts); every amount seen is kept for the reader
    price, cur = found[0]
    vals = sorted({v for v, c in found if c == cur})
    return [{"price": price, "currency": cur, "availability": None, "prices_on_page": vals,
             "price_note": "read from the page's price element, not from structured data; check the page"}]


def why_no_price(text):
    """Short diagnosis for the log when a product page shows no structured price."""
    types = sorted({str(n.get("@type")) for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', text, re.S | re.I)
                    for n in _ld_nodes(m.group(1))})
    bits = [f"JSON-LD types: {', '.join(types) or 'none'}"]
    if re.search(r'itemprop=["\']price["\']', text, re.I):
        bits.append("has itemprop=price")
    if re.search(r"oe_currency_value", text):
        bits.append("has an Odoo price span")
    if re.search(r"out of stock|nicht lieferbar|rupture|slut i lager|uitverkocht|ausverkauft", text, re.I):
        bits.append("page says out of stock")
    plain = re.sub(r"<[^>]+>", " ", text)
    m = re.search(r".{0,50}(?:€|£|EUR|SEK|GBP|\bkr\b).{0,40}", html.unescape(plain), re.S)
    if m:
        bits.append("text near the first currency sign: " + re.sub(r"\s+", " ", m.group(0)).strip()[:100])
    else:
        bits.append("no currency sign in the page text")
    return "; ".join(bits)


def _ld_nodes(raw):
    try:
        data = json.loads(html.unescape(raw).strip())
    except json.JSONDecodeError:
        return []
    return [n for n in walk(data) if isinstance(n, dict) and n.get("@type")]


def page_title(text):
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    return " ".join(html.unescape(m.group(1)).split())[:120] if m else ""


# ---------------------------------------------------------------- exchange rates
def ecb_rates():
    """{'EUR': 1.0, 'SEK': 11.2, ...} units of currency per euro, and the rate date."""
    req = urllib.request.Request(ECB, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            root = ElementTree.fromstring(r.read())
    except Exception as e:
        log(f"ECB rates unavailable: {e}")
        return {"EUR": 1.0}, None
    rates, date = {"EUR": 1.0}, None
    for cube in root.iter():
        if cube.tag.endswith("Cube"):
            if "time" in cube.attrib:
                date = cube.attrib["time"]
            if "currency" in cube.attrib:
                rates[cube.attrib["currency"]] = float(cube.attrib["rate"])
    return rates, date


def to_sek(price, currency, rates):
    if currency not in rates or "SEK" not in rates:
        return None
    return round(price / rates[currency] * rates["SEK"])


# ---------------------------------------------------------------- main
def load_drivers():
    out = []
    for f in ("drivers.json", "drivers_survey_midbass.json"):
        p = ROOT / f
        if p.exists():
            out += json.loads(p.read_text())["drivers"]
    return out


def scan(cfg, drivers, only_shop=None, only_driver=None):
    wanted = []
    for d in drivers:
        if only_driver and d["id"] != only_driver:
            continue
        for m in models_of(d):
            wanted.append((d["id"], m, model_regex(m)))
    offers = {}
    shop_notes = []
    for shop in cfg["shops"]:
        if only_shop and shop["name"].lower() != only_shop.lower():
            continue
        log(f"{shop['name']} ({shop['country']})")
        site = Site(shop)
        pages = list(dict.fromkeys(candidate_pages(site) + list(shop.get("pages") or [])))   # explicit product pages from the config too
        hubs = list(shop.get("hubs") or [])
        if not pages:
            log(f"  no sitemap found (robots.txt lists none and the usual sitemap addresses gave nothing); {len(site.disallow)} disallow rule(s) in robots.txt")
            if not hubs:
                hubs = [shop["home"]]                      # no sitemap: follow links from the front page instead
        hits = []
        for url in pages:
            n = norm(urllib.parse.urlparse(url).path)
            for did, model, rx in wanted:
                if rx.search(n):
                    hits.append((did, model, url))
        log(f"  {len(pages)} addresses in sitemaps, {len(hits)} product pages match a driver")
        makers = maker_words(drivers)
        if pages and not hits:
            log("  no match; addresses look like: " + " | ".join(pages[len(pages) // 2:len(pages) // 2 + 4]))
            named = [u for u in pages if any(m in u.lower() for m in makers)][:MAX_HUBS]
            log("  addresses naming a manufacturer: " + (" | ".join(named) if named else "none") + f" (looked for {', '.join(makers)})")
            hubs = list(dict.fromkeys(hubs + named))       # brand pages usually link to the product pages
        if hubs:
            more = [h for h in crawl_hubs(site, hubs, wanted, makers) if h not in hits]
            log(f"  {len(more)} product pages found by following links from {min(len(hubs), MAX_HUBS)} hub page(s)")
            hits += more
        if not pages and not hits:
            shop_notes.append(f"{shop['name']}: no sitemap found and no product page reached from the front page")
            continue
        if len(hits) > MAX_PAGES_PER_SHOP:
            shop_notes.append(f"{shop['name']}: {len(hits)} matching pages, only the first {MAX_PAGES_PER_SHOP} read")
        found = 0
        for did, model, url in hits[:MAX_PAGES_PER_SHOP]:
            text = site.get(url)
            if not text:
                continue
            page_offers = offers_from_page(text, shop.get("currency"))
            if not page_offers:
                log(f"  no structured price on {url} ({why_no_price(text)})")
                continue
            best = min(page_offers, key=lambda o: o["price"])
            offer = make_offer(shop, url, text, model, best)
            same = [o for o in offers.get(did, []) if o["shop"] == shop["name"]]
            if same:                                   # the same product in another language: keep the cheaper, prefer /en/
                keep = same[0]
                if offer["price"] < keep["price"] or (offer["price"] == keep["price"] and "/en/" in url and "/en/" not in keep["url"]):
                    offers[did].remove(keep); offers[did].append(offer)
                continue
            offers.setdefault(did, []).append(offer)
            found += 1
        shop_notes.append(f"{shop['name']}: {len(pages)} addresses, {len(hits)} matching pages, {found} prices read")
    return offers, shop_notes


def make_offer(shop, url, text, model, best):
    """One offer record from the best price on a page and the shop's settings."""
    offer = {"shop": shop["name"], "country": shop["country"], "url": url, "page_title": page_title(text), "model": model,
             "price": best["price"], "currency": best["currency"], "availability": best["availability"]}
    if len(best.get("prices_on_page") or []) > 1:
        offer["prices_on_page"] = best["prices_on_page"]
        offer["price_note"] = "the page shows several prices (quantity prices?); the lowest is used, check the page"
    if best.get("price_note"):
        offer["price_note"] = best["price_note"] + ("; several amounts on the page, the lowest is used" if len(best.get("prices_on_page") or []) > 1 else "")
    if shop.get("note"):
        offer["shop_note"] = shop["note"]
    if shop.get("login_prices"):
        offer["login_prices"] = True                  # the public price; logged in it is often lower
    if shop.get("pack"):
        offer["pack"] = True                          # the price is for a box of several drivers, not one
        offer["pack_note"] = shop["pack"]
    return offer


def mark_doubtful(lst):
    """A price read from a page element (no structured data) that is below 30 % of the median of the driver's
    structured-data prices is marked doubtful: kept in the list, never the lowest."""
    solid = sorted(o["price_sek"] for o in lst if o.get("price_sek") and "price element" not in (o.get("price_note") or "") and not o.get("pack"))
    if not solid:
        return
    median = solid[len(solid) // 2]
    for o in lst:
        if o.get("price_sek") and "price element" in (o.get("price_note") or "") and o["price_sek"] < 0.3 * median:
            o["doubtful"] = True
            o["price_note"] += f"; far below the other shops ({median} kr): probably not the product's price"


def carry_hand_written(offers, previous):
    """Fields written by hand into the previous prices.json (a logged-in price from the Chrome routine:
    price_logged_in, checked; a hand-added offer without a public price) survive the rebuild: matched by
    driver and shop."""
    for did, rec in (previous.get("drivers") or {}).items():
        for old in rec.get("offers") or []:
            if not any(k in old for k in ("price_logged_in", "checked", "hand_written")):
                continue
            mine = [o for o in offers.get(did, []) if o["shop"] == old["shop"]]
            if mine:
                for k in ("price_logged_in", "checked", "hand_written"):
                    if k in old:
                        mine[0][k] = old[k]
            else:
                offers.setdefault(did, []).append(dict(old, hand_written=True))
    return offers


def write_outputs(offers, shop_notes, rates, rate_date, drivers, cfg, dry_run, summary):
    today = dt.date.today().isoformat()
    byid = {d["id"]: d for d in drivers}
    try:
        carry_hand_written(offers, json.loads(OUT.read_text()))
    except (OSError, ValueError):
        pass
    for lst in offers.values():
        for o in lst:
            o["price_sek"] = to_sek(o["price"], o["currency"], rates)
        mark_doubtful(lst)
        lst.sort(key=lambda o: (bool(o.get("pack")) or bool(o.get("doubtful")), o["price_sek"] is None, o["price_sek"] or o["price"]))
    data = {"meta": {"updated": today, "rates_date": rate_date, "rates_per_eur": {k: rates[k] for k in sorted(rates) if k in ("SEK", "EUR", "GBP", "DKK", "NOK", "PLN", "CZK", "CHF", "HUF")},
                     "shops_scanned": [s["name"] for s in cfg["shops"]], "notes": shop_notes,
                     "how": "watch/prices.py: shop sitemaps searched for the model number, price read from the page's structured data, converted with ECB reference rates. Check the shop before buying."},
            "drivers": {did: {"name": byid[did]["name"], "offers": lst} for did, lst in sorted(offers.items()) if did in byid}}
    lines = [f"# Lowest prices in Europe ({today})", "",
             "Found by `watch/prices.py` in the shops' own product pages (structured price data), converted to kronor with the "
             f"European Central Bank's rates of {rate_date or 'unknown date'}. Check the shop before buying: prices and stock change.", "",
             "| Driver | Lowest | Shop | Others |", "|---|---|---|---|"]
    for did, rec in data["drivers"].items():
        o = rec["offers"][0]
        rest = "; ".join(f"{x['shop']} {x['price']:g} {x['currency']}" + (" (public price; lower when logged in)" if x.get("login_prices") else "") + (" (box price)" if x.get("pack") else "") + (" (doubtful)" if x.get("doubtful") else "") for x in rec["offers"][1:])
        lines.append(f"| {rec['name']} | {o['price']:g} {o['currency']}" + (f" ≈ {o['price_sek']} kr" if o["price_sek"] else "") +
                     f" | [{o['shop']}]({o['url']})" + (" (public price; lower when logged in)" if o.get("login_prices") else "") + (" (box price)" if o.get("pack") else "") + f" | {rest or '—'} |")
    missing = [d["name"] for d in drivers if d["id"] not in data["drivers"]]
    lines += ["", f"No price found for {len(missing)} driver(s): {', '.join(missing) if missing else 'none'}.", "", "Shops:"]
    lines += [f"- {n}" for n in shop_notes]
    text = "\n".join(lines) + "\n"
    if dry_run:
        print(json.dumps(data, indent=1, ensure_ascii=False))
        print(text)
    else:
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        OUT_MD.write_text(text)
        print(f"prices.json: {len(data['drivers'])} drivers with a price, {len(missing)} without")
    if summary:
        Path(summary).open("a").write(text)
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--shop")
    ap.add_argument("--driver")
    ap.add_argument("--summary", help="append the report to this file (for example $GITHUB_STEP_SUMMARY)")
    a = ap.parse_args()
    cfg = json.loads(CONFIG.read_text())
    drivers = load_drivers()
    rates, rate_date = ecb_rates()
    offers, notes = scan(cfg, drivers, a.shop, a.driver)
    write_outputs(offers, notes, rates, rate_date, drivers, cfg, a.dry_run, a.summary)


if __name__ == "__main__":
    main()
