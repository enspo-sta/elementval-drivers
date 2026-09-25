"""Tests for watch/prices.py that need no internet: price parsing, model matching, robots rules,
structured-data reading and the ECB conversion. Run: python3 -m unittest discover -s tests -p "test_*.py" """
import importlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "watch"))
import prices as P  # noqa: E402


class Numbers(unittest.TestCase):
    def test_european_price_formats(self):
        for text, want in [("329", 329.0), ("329.00", 329.0), ("329,00", 329.0), ("3 495,00", 3495.0), ("3.495,00", 3495.0),
                           ("3,495.00", 3495.0), ("1 234", 1234.0), ("1,234", 1234.0), ("12,5", 12.5), ("€ 1.234,50", 1234.5),
                           ("SEK 3495", 3495.0), (249, 249.0), ("", None), ("n/a", None)]:
            self.assertEqual(P.to_number(text), want, text)

    def test_sek_conversion_uses_ecb_rates_per_euro(self):
        rates = {"EUR": 1.0, "SEK": 11.20, "GBP": 0.85, "DKK": 7.46}
        self.assertEqual(P.to_sek(100, "EUR", rates), 1120)
        self.assertEqual(P.to_sek(85, "GBP", rates), 1120)
        self.assertEqual(P.to_sek(1120, "SEK", rates), 1120)
        self.assertIsNone(P.to_sek(10, "XXX", rates))


class Matching(unittest.TestCase):
    def test_models_of_every_driver_in_the_database(self):
        drivers = P.load_drivers()
        main = json.loads((ROOT / "drivers.json").read_text())["drivers"]
        for d in main:
            self.assertTrue(P.models_of(d), d["name"])
        survey = [d for d in drivers if d not in main]
        self.assertGreaterEqual(sum(1 for d in survey if P.models_of(d)), 12, "survey drivers with a usable model number")
        byid = {d["id"]: P.models_of(d) for d in drivers}
        self.assertEqual(byid["rs-180-4"], ["RS 180-4"])
        self.assertEqual(byid["ptt65x04naa08"], ["PTT6.5X04-NAA-08"])
        self.assertEqual(byid["sb-sb34nrxl75-8-dual"], ["SB34NRXL75-8"])       # the pair points at the single driver
        self.assertEqual(byid["sb17cac35-4"], ["SB17CAC35-4"])                # proxy: the driver itself
        self.assertEqual(byid["m74t-6"], ["M74T-6"])

    def test_model_regex_respects_variant_boundaries(self):
        rx = P.model_regex("PTT6.5X04-NAA-08")
        for url, want in [("/purifi-ptt6-5x04-naa-08", True), ("/en/ptt6.5x04-naa-08.html", True), ("/ptt65x04naa08", True),
                          ("/product/purifi-ptt6.5x04-naa-08-4-ohm", True), ("/purifi-ptt6-5x04-naa-08a", False),
                          ("/purifi-ptt6-5x04-naa-08a-8-ohm", False), ("/sb17nbac35-8", False)]:
            self.assertEqual(bool(rx.search(P.norm(url))), want, url)
        self.assertFalse(P.model_regex("WO24P-8").search(P.norm("/satori-wo24p-8-4-ohm-wo24p-4")) is None)
        self.assertIsNone(P.model_regex("WO24P-8").search(P.norm("/satori-wo24p-4")))


class Robots(unittest.TestCase):
    def test_disallow_allow_and_crawl_delay(self):
        site = P.Site.__new__(P.Site)
        site.shop = {"name": "t", "home": "https://shop.example/"}
        site.delay, site.disallow, site.allow = 3, ["/cart", "/search*", "/private/"], ["/private/products/"]
        self.assertTrue(site.allowed("https://shop.example/products/ptt"))
        self.assertFalse(site.allowed("https://shop.example/cart/add"))
        self.assertFalse(site.allowed("https://shop.example/search?q=ptt"))
        self.assertFalse(site.allowed("https://shop.example/private/x"))
        self.assertTrue(site.allowed("https://shop.example/private/products/x"))


PAGE_LD = """<html><head><title>Purifi PTT6.5X04-NAA-08 | Shop</title>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Product","name":"PTT6.5X04-NAA-08",
"offers":{"@type":"AggregateOffer","lowPrice":"329.00","highPrice":"349.00","priceCurrency":"EUR","availability":"https://schema.org/InStock"}}]}</script>
</head><body></body></html>"""
PAGE_META = """<html><head><meta property="product:price:amount" content="3 495,00"><meta property="product:price:currency" content="SEK"></head></html>"""
PAGE_ITEMPROP = """<div itemprop="offers"><span itemprop="price" content="45.90">45,90 €</span><meta itemprop="priceCurrency" content="EUR"></div>"""


class Pages(unittest.TestCase):
    def test_json_ld_aggregate_offer(self):
        self.assertEqual(P.offers_from_page(PAGE_LD), [{"price": 329.0, "currency": "EUR", "availability": "InStock"}])
        self.assertEqual(P.page_title(PAGE_LD), "Purifi PTT6.5X04-NAA-08 | Shop")

    def test_meta_tags_and_itemprop_fallbacks(self):
        self.assertEqual(P.offers_from_page(PAGE_META), [{"price": 3495.0, "currency": "SEK", "availability": None}])
        self.assertEqual(P.offers_from_page(PAGE_ITEMPROP), [{"price": 45.9, "currency": "EUR", "availability": None}])
        self.assertEqual(P.offers_from_page("<html>no price here</html>"), [])

    def test_config_is_valid(self):
        cfg = json.loads((ROOT / "watch" / "prices_config.json").read_text())
        names = [s["name"] for s in cfg["shops"]]
        self.assertEqual(len(names), len(set(names)))
        for s in cfg["shops"]:
            self.assertTrue(s["home"].startswith("https://"), s)
            self.assertEqual(len(s["country"]), 2, s)


if __name__ == "__main__":
    unittest.main()


class Scanner(unittest.TestCase):
    def test_odoo_price_span_with_shop_currency(self):
        odoo = '<div><span class="oe_price"><span class="oe_currency_value">1,234.00</span> €</span></div>'
        self.assertEqual(P.offers_from_page(odoo, "EUR"), [{"price": 1234.0, "currency": "EUR", "availability": None, "prices_on_page": [1234.0]}])
        self.assertEqual(P.offers_from_page('<span class="oe_currency_value">99</span>', None), [], "no currency known: no offer")

    def test_why_no_price_names_what_the_page_has(self):
        d = P.why_no_price('<script type="application/ld+json">{"@type":"WebPage"}</script> Nicht lieferbar')
        self.assertIn("WebPage", d)
        self.assertIn("out of stock", d)

    def test_only_pages_on_the_shop_host_and_never_images(self):
        site = P.Site.__new__(P.Site)
        site.shop = {"name": "t", "home": "https://www.shop.example/"}
        site.host, site.delay, site.last, site.disallow, site.allow, site.sitemaps, site.fetched = "www.shop.example", 0, 0, [], [], [], 0
        site.origin = "https://www.shop.example"
        urls = ["https://shop.example/p/ptt", "https://www.shop.example/p/ptt.jpg", "https://cdn.other.com/p/ptt", "https://www.shop.example/en/ptt.html"]
        P.sitemap_urls = lambda s, u, depth=0, seen=None: urls
        try:
            self.assertEqual(P.candidate_pages(site), ["https://shop.example/p/ptt", "https://www.shop.example/en/ptt.html"])
        finally:
            importlib.reload(P)


class MoreShops(unittest.TestCase):
    def test_magento_price_markup(self):
        mag = '<span data-price-type="finalPrice" data-price-amount="469.95"></span><script>"currencyCode":"EUR"</script>'
        self.assertEqual(P.offers_from_page(mag, "EUR"), [{"price": 469.95, "currency": "EUR", "availability": None}])

    def test_odoo_quantity_prices_take_the_lowest_and_keep_all(self):
        odoo = '<span class="oe_currency_value">3,750.00</span> € <span class="oe_currency_value">375.00</span>'
        o = P.offers_from_page(odoo, "EUR")[0]
        self.assertEqual(o["price"], 375.0)
        self.assertEqual(o["prices_on_page"], [375.0, 3750.0])

    def test_swap_www(self):
        self.assertEqual(P.swap_www("https://audio-hi.fi/robots.txt"), "https://www.audio-hi.fi/robots.txt")
        self.assertEqual(P.swap_www("https://www.shop.example/a?b=1"), "https://shop.example/a?b=1")


class Certificates(unittest.TestCase):
    """The scanner completes an incomplete certificate chain the way a browser does (watch/prices.py fix_chain)."""
    def test_ca_issuers_address_is_read_from_a_certificate(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", tmp + "/k.pem", "-out", tmp + "/c.pem",
                                "-days", "1", "-subj", "/CN=shop.example", "-addext", "authorityInfoAccess=caIssuers;URI:http://ca.example/int.der"],
                               capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            pem = Path(tmp + "/c.pem").read_text()
            self.assertEqual(P.ca_issuers_url(pem), "http://ca.example/int.der")
            self.assertIsNone(P.ca_issuers_url("-----BEGIN CERTIFICATE-----\nnot a certificate\n-----END CERTIFICATE-----\n"))
            der = subprocess.run(["openssl", "x509", "-in", tmp + "/c.pem", "-outform", "DER"], capture_output=True).stdout
            self.assertIn("BEGIN CERTIFICATE", P.der_to_pem(der))
            self.assertIsNone(P.der_to_pem(b"garbage"))

    def test_unreachable_server_gives_no_intermediates(self):
        self.assertEqual(P.missing_intermediates("127.0.0.1:9"), [])


class Offers(unittest.TestCase):
    def test_make_offer_marks_box_prices_login_prices_and_several_prices(self):
        best = {"price": 375.0, "currency": "EUR", "availability": None, "prices_on_page": [375.0, 3750.0]}
        shop = {"name": "Purifi (direct)", "country": "DK", "pack": "sold by the box"}
        o = P.make_offer(shop, "https://purifi-audio.com/shop/x", "<title>PTT6.5X04</title>", "PTT6.5X04-NAA-08", best)
        self.assertEqual((o["price"], o["currency"], o["page_title"], o["pack"], o["pack_note"]), (375.0, "EUR", "PTT6.5X04", True, "sold by the box"))
        self.assertEqual(o["prices_on_page"], [375.0, 3750.0])
        self.assertIn("several prices", o["price_note"])
        o2 = P.make_offer({"name": "T", "country": "FR", "login_prices": True, "note": "cheap when logged in"}, "u", "", "M", {"price": 1, "currency": "EUR", "availability": "InStock"})
        self.assertTrue(o2["login_prices"]); self.assertEqual(o2["shop_note"], "cheap when logged in"); self.assertNotIn("pack", o2)

    def test_config_marks_purifi_direct_as_box_prices(self):
        cfg = json.loads((ROOT / "watch" / "prices_config.json").read_text())
        purifi = next(s for s in cfg["shops"] if s["name"] == "Purifi (direct)")
        self.assertIn("box", purifi["pack"])


class PlainMarkup(unittest.TestCase):
    """Shops without structured price data (osCommerce-style pages such as audio-hi.fi)."""
    def test_price_element_with_currency_sign(self):
        page = '<div class="productPrice"><span>1 234,00</span> €</div>'
        o = P.offers_from_page(page, None)[0]
        self.assertEqual((o["price"], o["currency"]), (1234.0, "EUR"))
        self.assertIn("price element", o["price_note"])

    def test_shipping_and_old_prices_are_not_the_price(self):
        page = '<span class="shipping-price">5,90 €</span><span class="old-price">129 €</span><span id="price">99 €</span>'
        self.assertEqual(P.offers_from_page(page, None)[0]["price"], 99.0)

    def test_kronor_use_the_shop_currency(self):
        self.assertEqual(P.offers_from_page('<td class="price"><b>3 495</b> kr</td>', "SEK")[0]["currency"], "SEK")
        self.assertEqual(P.offers_from_page('<td class="price">3 495 kr</td>', "DKK")[0]["currency"], "DKK")
        self.assertEqual(P.offers_from_page('<p>no price element 12 €</p>', "EUR"), [])

    def test_why_no_price_quotes_the_text_near_the_currency_sign(self):
        d = P.why_no_price("<html><body><p>Price incl. VAT: 199,00 €</p></body></html>")
        self.assertIn("199,00 €", d)


class Hubs(unittest.TestCase):
    def fake_site(self, pages):
        site = P.Site.__new__(P.Site)
        site.shop = {"name": "t", "home": "https://www.shop.example/"}
        site.host, site.delay, site.last, site.disallow, site.allow, site.sitemaps, site.fetched, site.ssl = "www.shop.example", 0, 0, [], [], [], 0, None
        site.origin = "https://www.shop.example"
        site.get = lambda url, binary=False, retry=False: pages.get(url)
        return site

    def test_links_of_keeps_own_host_pages_only(self):
        site = self.fake_site({})
        text = '<a href="/chassis/dayton.htm">Dayton</a> <a href="https://cdn.other.com/x.htm">x</a> <a href="pic.jpg">img</a> <a href="https://shop.example/a.htm#top">a</a>'
        self.assertEqual(P.links_of(site, "https://www.shop.example/hifi/", text),
                         ["https://www.shop.example/chassis/dayton.htm", "https://shop.example/a.htm"])

    def test_crawl_hubs_reaches_product_pages_two_levels_down(self):
        pages = {"https://www.shop.example/": '<a href="/chassis/dayton.htm">Dayton</a><a href="/about.htm">about</a>',
                 "https://www.shop.example/chassis/dayton.htm": '<a href="/chassis/dayton_rs180-4.htm">RS180-4</a><a href="/chassis/dayton_rs225-8.htm">RS225-8</a>',
                 "https://www.shop.example/about.htm": "nothing"}
        site = self.fake_site(pages)
        wanted = [("rs-180-4", "RS 180-4", P.model_regex("RS 180-4"))]
        self.assertEqual(P.crawl_hubs(site, ["https://www.shop.example/"], wanted, ["dayton"]),
                         [("rs-180-4", "RS 180-4", "https://www.shop.example/chassis/dayton_rs180-4.htm")])

    def test_maker_words(self):
        words = P.maker_words([{"name": "Dayton Audio RS 180-4", "manufacturer": "Dayton Audio"}, {"name": "SB Acoustics X", "manufacturer": "SB Acoustics"}, {"name": "DIY Sound Group Anarchy", "manufacturer": "DIY Sound Group"}])
        self.assertIn("dayton", words); self.assertIn("sbacoustics", words); self.assertNotIn("sb", words); self.assertNotIn("diy", words)

    def test_robots_rule_is_named(self):
        site = self.fake_site({})
        site.disallow = ["/sitemap"]
        self.assertEqual(site.rule_for("https://www.shop.example/sitemap.xml"), (False, "/sitemap"))
        self.assertEqual(site.rule_for("https://www.shop.example/p/x"), (True, None))


class PlainMarkupOrder(unittest.TestCase):
    def test_first_price_element_wins_and_instalments_are_skipped(self):
        page = ('<div class="klarna-price">alk. 17,80 €/kk</div><span class="productSpecialPrice">399,00 €</span>'
                '<div class="related"><span class="price">89,00 €</span></div>')
        o = P.offers_from_page(page, None)[0]
        self.assertEqual(o["price"], 399.0)
        self.assertEqual(o["prices_on_page"], [89.0, 399.0])
        self.assertEqual(P.offers_from_page('<span class="price">from 17,80 € / month</span>', None), [])

    def test_doubtful_page_element_price_is_never_the_lowest(self):
        lst = [{"price": 220.0, "currency": "EUR", "price_sek": 2464, "shop": "A"},
               {"price": 17.8, "currency": "EUR", "price_sek": 199, "shop": "B", "price_note": "read from the page's price element, not from structured data; check the page"},
               {"price": 250.0, "currency": "EUR", "price_sek": 2800, "shop": "C"}]
        P.mark_doubtful(lst)
        self.assertTrue(lst[1]["doubtful"]); self.assertNotIn("doubtful", lst[0])
        lst.sort(key=lambda o: (bool(o.get("pack")) or bool(o.get("doubtful")), o["price_sek"] is None, o["price_sek"] or o["price"]))
        self.assertEqual([o["shop"] for o in lst], ["A", "C", "B"])
