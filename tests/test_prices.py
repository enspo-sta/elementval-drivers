"""Tests for watch/prices.py that need no internet: price parsing, model matching, robots rules,
structured-data reading and the ECB conversion. Run: python3 -m unittest discover -s tests -p "test_*.py" """
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
