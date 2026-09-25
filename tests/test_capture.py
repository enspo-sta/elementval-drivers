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
