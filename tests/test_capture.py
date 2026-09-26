"""Tests for the capture tools on charts drawn here with known curves.
Run: python3 -m unittest discover -s tests -p "test_*.py"   (skips when PyMuPDF, Pillow or numpy are missing)"""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRUE = lambda f: -60 + 12 * math.sin(math.log10(f) * 2.2)          # the curve we draw, in dB


def run(*args):
    out = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout)


class PdfVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pymupdf
        except ImportError:
            raise unittest.SkipTest("PyMuPDF not installed")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pdf = Path(cls.tmp.name) / "chart.pdf"
        doc = pymupdf.open()
        page = doc.new_page(width=600, height=400)
        # plot frame: x 100..500 = 20 Hz..20 kHz (log), y 350..50 = -100..0 dB
        page.draw_rect(pymupdf.Rect(100, 50, 500, 350), color=(0, 0, 0), width=0.5)
        fx = lambda f: 100 + (math.log10(f) - math.log10(20)) / 3 * 400
        fy = lambda v: 350 - (v + 100) / 100 * 300
        pts = [pymupdf.Point(fx(20 * 10 ** (3 * i / 400)), fy(TRUE(20 * 10 ** (3 * i / 400)))) for i in range(401)]
        page.draw_polyline(pts, color=(0.9, 0.2, 0.1), width=1)
        page.insert_text((95, 365), "20", fontsize=8)
        page.insert_text((490, 365), "20k", fontsize=8)
        doc.save(cls.pdf)

    def test_list_finds_the_coloured_line(self):
        rows = run("capture/pdf_vectors.py", "list", self.pdf, "--page", "1")
        self.assertEqual(len(rows), 1)
        self.assertIn(rows[0]["color"], ("#e5331a", "#e6331a"))   # 0.9 of 255 rounds either way
        self.assertGreaterEqual(rows[0]["points"], 400)

    def test_ticks_reads_numbers_with_k(self):
        vals = {t["value"] for t in run("capture/pdf_vectors.py", "ticks", self.pdf, "--page", "1")}
        self.assertIn(20000.0, vals)

    def test_extract_matches_the_drawn_curve(self):
        pid = run("capture/pdf_vectors.py", "list", self.pdf, "--page", "1")[0]["id"]
        s = run("capture/pdf_vectors.py", "extract", self.pdf, "--page", "1", "--paths", pid, "--names", "H2",
                "--x", "100:20,500:20000", "--xlog", "--y", "350:-100,50:0")["series"][0]
        self.assertEqual(s["name"], "H2")
        worst = max(abs(p["y"] - TRUE(p["x"])) for p in s["points"])
        self.assertLess(worst, 0.05)
        per_decade = len(s["points"]) / 3
        self.assertLessEqual(per_decade, 161)       # thinned to the 1/48 octave limit


class ImageCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy  # noqa: F401
            from PIL import Image, ImageDraw
        except ImportError:
            raise unittest.SkipTest("Pillow or numpy not installed")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.png = Path(cls.tmp.name) / "chart.png"
        img = Image.new("RGB", (1276, 635), "white")
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 90, 40, 1240, 590
        d.rectangle((x0, y0, x1, y1), outline="black")
        for k in range(1, 10):
            y = y0 + (y1 - y0) * k / 10
            d.line((x0, y, x1, y), fill=(200, 200, 200))
        fx = lambda f: x0 + (math.log10(f) - math.log10(20)) / 3 * (x1 - x0)
        fy = lambda v: y1 - (v + 100) / 100 * (y1 - y0)
        pts = [(fx(20 * 10 ** (3 * i / 2000)), fy(TRUE(20 * 10 ** (3 * i / 2000)))) for i in range(2001)]
        d.line(pts, fill=(232, 65, 44), width=3)
        d.line([(fx(f), fy(-90)) for f in (20, 20000)], fill=(40, 90, 220), width=3)     # a second series
        d.rectangle((1000, 50, 1230, 120), fill=(232, 65, 44))                           # legend swatch to skip
        img.save(cls.png)

    def test_colors_lists_both_series(self):
        out = subprocess.run([sys.executable, "capture/image_curves.py", "colors", str(self.png), "--plot", "90,40,1240,590"],
                             capture_output=True, text=True, cwd=ROOT).stdout
        self.assertIn("#e8", out)
        self.assertIn("#28", out)

    def test_extract_within_a_pixel(self):
        s = run("capture/image_curves.py", "extract", self.png, "--plot", "90,40,1240,590", "--x", "20,20000", "--xlog",
                "--y=-100,0", "--color", "#e8412c", "--name", "H2", "--skip", "990,45,1235,125")["series"][0]
        worst = max(abs(p["y"] - TRUE(p["x"])) for p in s["points"])
        self.assertLess(worst, 0.3)                  # 550 pixels for 100 dB: 0.18 dB per pixel
        self.assertAlmostEqual(len(s["points"]) / 3, 80, delta=2)   # 1/24 octave


if __name__ == "__main__":
    unittest.main()


class TwoToneSpectrum(unittest.TestCase):
    """capture/imd_read.py on a HiFiCompass-style two-tone chart drawn here: black, green grid, yellow
    spectrum, 0 to -100 dB, 0 to 600 Hz, a cursor readout below. The lower tone sits left of the first
    labelled grid line, where the first reader missed it."""

    @classmethod
    def setUpClass(cls):
        try:
            import numpy  # noqa: F401
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise unittest.SkipTest("Pillow or numpy not installed")
        import shutil
        if not shutil.which("tesseract"):
            raise unittest.SkipTest("tesseract not installed")
        font = next((p for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",) if Path(p).exists()), None)
        if not font:
            raise unittest.SkipTest("no font to draw the labels")
        sys.path.insert(0, str(ROOT / "capture"))
        import imd_read
        cls.I = imd_read
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "chart.png"
        im = Image.new("RGB", (1024, 701), (0, 0, 0)); d = ImageDraw.Draw(im)
        f = ImageFont.truetype(font, 13)
        top, bot, left, right = 46, 618, 33, 964
        Y = lambda db: top + (0 - db) / 100 * (bot - top)
        for i in range(0, 101, 2):
            y = round(Y(-i)); d.line([(left, y), (right, y)], fill=(8, 72, 8) if i % 10 else (16, 110, 16))
        for i in range(11):
            x = round(left + i * (right - left) / 10); d.line([(x, top), (x, bot)], fill=(16, 110, 16))
            d.text((2, round(Y(-10 * i)) - 7), f"{-10 * i:.1f}", font=f, fill=(220, 220, 220))
            if i:
                d.text((x - 10, bot + 8), str(60 * i), font=f, fill=(220, 220, 220))
        d.text((140, bot + 40), "254.88Hz,-23.10dB", font=f, fill=(220, 220, 220))
        cls.lines = {30: -11.0, 255: -23.1, 225: -61.0, 285: -59.4, 90: -57.3, 195: -74.4, 315: -71.8}
        prev = None
        for x in range(left, right + 1):
            hz = (x - left) / (right - left) * 600
            db = -95 + 2 * math.sin(x * 1.7)
            for lf, lv in cls.lines.items():
                if abs(hz - lf) < 0.33:
                    db = max(db, lv)
            p = (x, Y(db))
            if prev:
                d.line([prev, p], fill=(240, 240, 40))
            prev = p
        im.save(cls.path)
        cls.rec = imd_read.read_chart(cls.path, imd_read.test_of("mr16tx-8_30hz255hz_xmax30hz1mm_4to1text.png"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_file_names(self):
        t = self.I.test_of
        self.assertEqual(t("mr16tx-8_30hz255hz_xmax30hz1.5mm_4to1text.png"), {"f1": 30.0, "f2": 255.0, "x_pk_mm": 1.5, "ratio": "4:1"})
        self.assertEqual(t("ptt6.5w04-01a_30hz255hz_xmax30hz3mm.png")["ratio"], None)
        self.assertEqual(t("m74a-6_315mm_500hz2v834.25khz2v83.png"), {"f1": 500.0, "f2": 4250.0, "drive_v": 2.83, "ratio": "1:1"})
        self.assertEqual(t("tw29bnwg-4_315mm_2v83rms_1khz10khz-1to1_0.png")["drive_v"], 2.83)

    def test_both_tones_and_products(self):
        r = self.rec
        self.assertNotIn("error", r)
        tones = {x["f"]: x["level"] for x in r["tones"]}
        self.assertAlmostEqual(tones[30.0], -11.0, delta=0.6)       # left of the first labelled grid line
        self.assertAlmostEqual(tones[255.0], -23.1, delta=0.6)
        got = {p["f"]: p["level"] for p in r["products"]}
        for f in (90, 195, 225, 285, 315):
            self.assertAlmostEqual(got[f], self.lines[f], delta=0.6, msg=f"{f} Hz")
        self.assertFalse(set(got) - {90, 195, 225, 285, 315}, "a product in the noise was kept")

    def test_lost_minus_and_stray_column(self):
        self.assertEqual([w["text"] for w in self.I.negative_labels([{"text": "10.0"}, {"text": "-20.0"}, {"text": "s"}])], ["-10.0", "-20.0", "s"])
        cols = [[x, x] for x in (63, 191, 319, 448, 576, 704, 832, 874, 917, 960)]
        self.assertEqual([c[0] for c in self.I.lattice(cols)], [63, 191, 319, 448, 576, 704, 832, 960])

    def test_cursor_check(self):
        c = self.rec["check"]
        self.assertEqual((c["f"], c["stated_db"]), (254.88, -23.1))
        self.assertLess(abs(c["difference_db"]), 0.6)


class ChartTypes(unittest.TestCase):
    """The chart type from a file name, with or without the address's ?itok=… part."""

    def test_types(self):
        sys.path.insert(0, str(ROOT / "capture"))
        import chart_probe as CP
        cases = {
            "https://hificompass.com/sites/default/files/zamer/ptt10.0x04-nab-02_20mm_2v83_0deg.png?itok=L5Tl": "near-response",
            "https://hificompass.com/sites/default/files/zamer/afc520/ptt10.0x04-nab-02_20mm_11v2.png": "near-response",
            "mr16tx-8_5mm_1v_0deg.png?itok=x": "near-response",
            "https://hificompass.com/sites/default/files/zamer/spectr/ptt10.0x04-nab-02_50mm_8v_150hz.png?itok=q": "spectrum",
            "mw19tx-4_20mm_2v_40hz.png": "spectrum",
            "m74t-6-off-axis-normalized-5-30db.png": "off-axis",
            "ptt10.0x04-nab-02_315mm_2v83_0deg.png?itok=a": "response",
            "https://hificompass.com/sites/default/files/zamer/voice_coil_curr/ptt10.0x04-nab-02_chd_2v83.png?itok=L5": "current",
            "mr16tx-8_30hz255hz_xmax30hz1mm_4to1text.png": "intermodulation",
        }
        for url, want in cases.items():
            self.assertEqual(CP.chart_type(url), want, url)
        self.assertFalse(CP.SKIP.search("https://hificompass.com/sites/default/files/zamer/voice_coil_curr/ptt10.0x04-nab-02_chd_2v83.png"))
        self.assertTrue(CP.SKIP.search("ptt6.5x04-naa-08a_voice_coil2.jpg"))
        self.assertTrue(CP.SKIP.search("ptt8.0x04-nab-02_wires.jpg"))


class CutOffCurves(unittest.TestCase):
    def test_points_on_the_top_line_are_left_out(self):
        sys.path.insert(0, str(ROOT / "capture"))
        try:
            import chart_read as CR
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        kept, n = CR.off_top([(1, 36.0), (2, 36.5), (3, 40.0), (4, 80.0)], 36)
        self.assertEqual((kept, n), ([(3, 40.0), (4, 80.0)], 2))
