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
            "https://hificompass.com/sites/default/files/zamer/afc520/ptt10.0x04-nab-02_20mm_11v2.png": "harmonics",   # the near-field harmonics folder
            "mr16tx-8_5mm_1v_0deg.png?itok=x": "near-response",
            "https://hificompass.com/sites/default/files/zamer/spectr/ptt10.0x04-nab-02_50mm_8v_150hz.png?itok=q": "spectrum",
            "mw19tx-4_20mm_2v_40hz.png": "spectrum",
            "m74t-6-off-axis-normalized-5-30db.png": "off-axis",
            "ptt10.0x04-nab-02_315mm_2v83_0deg.png?itok=a": "response",
            "https://hificompass.com/sites/default/files/zamer/voice_coil_curr/ptt10.0x04-nab-02_chd_2v83.png?itok=L5": "current",
            "mr16tx-8_30hz255hz_xmax30hz1mm_4to1text.png": "intermodulation",
            "https://hificompass.com/sites/default/files/afc/wo24tx-8_315mm_4v-0deg.png?itok=x": "response",
            "https://hificompass.com/sites/default/files/afc/wo24tx-8-315mm_2v83_0deg.png": "response",
            "https://hificompass.com/sites/default/files/zamer/wo24tx-8_3mm_1v_0deg.png": "near-response",
        }
        for url, want in cases.items():
            self.assertEqual(CP.chart_type(url), want, url)
        self.assertFalse(CP.SKIP.search("https://hificompass.com/sites/default/files/zamer/voice_coil_curr/ptt10.0x04-nab-02_chd_2v83.png"))
        self.assertTrue(CP.SKIP.search("ptt6.5x04-naa-08a_voice_coil2.jpg"))
        self.assertTrue(CP.SKIP.search("ptt8.0x04-nab-02_wires.jpg"))
        import sets_from_chart_read as S
        self.assertEqual(S.conditions("wo24tx-8_315mm_4v-0deg.png")["drive_v"], 4.0)
        self.assertEqual(S.conditions("wo24tx-8-315mm_2v83_0deg.png")["distance_mm"], 315)
        self.assertEqual(S.conditions("wo24tx-8_315mm_11v2-0deg.png")["angle_deg"], 0)


class CutOffCurves(unittest.TestCase):
    def test_points_on_the_top_line_are_left_out(self):
        sys.path.insert(0, str(ROOT / "capture"))
        try:
            import chart_read as CR
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        kept, n = CR.off_top([(1, 36.0), (2, 36.5), (3, 40.0), (4, 80.0)], 36)
        self.assertEqual((kept, n), ([(3, 40.0), (4, 80.0)], (2, 0)))
        # and on the floor line: bottom_edge is the last pixel row above it
        kept, n = CR.off_top([(1, 36.0), (3, 40.0), (4, 79.0), (5, 80.0)], 36, 80)
        self.assertEqual((kept, n), ([(3, 40.0), (4, 79.0)], (1, 1)))


class DatasheetFiles(unittest.TestCase):
    """capture/sets_from_datasheet_probe.py: Purifi's measured files into sets, checked against the datasheet."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "capture"))
        import sets_from_datasheet_probe as S
        self.S = S

    def page(self, text):
        return [{"page": 2, "text": text}]

    def probe(self, files, text):
        return {"date": "2026-09-26", "drivers": {"x": {"model": "PTT1-TEST", "page": self.page(text),
                "data": [{"label": "Frequency Response & Impedance Data", "href": "https://purifi-audio.com/doc/1", "files": files}]}}}

    def db(self):
        return {"drivers": [{"id": "x", "source": "Purifi datasheet PTT1-TEST v1.00 (Jan 2026)", "measurements": []}]}

    def test_angles_from_file_names(self):
        self.assertEqual(self.S.angle_of("PTT1.3T04-HAG-10 FRD hor 85.txt"), 85)
        self.assertEqual(self.S.angle_of("PTT5.25X04-NAA-05 - SPL_30deg.txt"), 30)
        self.assertIsNone(self.S.angle_of("PTT5.25X04-NAA-05 - SPL.txt"))
        self.assertIsNone(self.S.angle_of("PTT1.3T04-HAG-10 ZMA.txt"))

    def test_stated_sensitivity(self):
        text = "SPL@2.83 Vrms/1 m, 3 kHz, ref. 20 µPa (infinite baffle / 2pi) \n96.0 \ndB"
        self.assertEqual(self.S.stated_sensitivity(text), (96.0, 3000.0, 3000.0))
        text = "SPL@2.83V rms/1m, 300Hz -800Hz , ref. 20µPa (infinite baffle / 2pi) \n84.9 \ndB"
        self.assertEqual(self.S.stated_sensitivity(text), (84.9, 300.0, 800.0))

    def test_off_axis_set_as_published_and_level_checked(self):
        text = "SPL@2.83 Vrms/1 m, 1 kHz, ref. 20 µPa (infinite baffle / 2pi) \n90.0 \ndB"
        rows = lambda y: [[0.0, 50.0, 0.0], [500.0, y, 1.0], [1000.0, y, 2.0], [2000.0, y - 1, 3.0]]
        files = [{"name": f"T FRD hor {a}.txt", "header": ["f_Hz,spl_dB,phase_deg"], "rows": rows(90.123456 - a / 10)} for a in (0, 5, 10)]
        made, skipped = self.S.build(self.probe(files, text), self.db())
        self.assertEqual(len(made), 1, skipped)
        s = made[0][1]
        self.assertEqual([x["name"] for x in s["series"]], ["0°", "5°", "10°"])
        self.assertEqual(s["series"][0]["points"][0], {"x": 500.0, "y": 90.123})  # the 0 Hz row left out
        self.assertIn("left out: the row at 0 Hz", s["note"])
        self.assertIn("+0.1 dB", s["note"])
        # a file whose level misses the stated sensitivity is not used
        made, skipped = self.S.build(self.probe(files, text.replace("90.0", "80.0")), self.db())
        self.assertEqual(made, [])
        self.assertIn("not used", skipped[0][1])

    def test_on_axis_file_at_one_volt_and_impedance(self):
        text = ("SPL@2.83Vrms/1m, 300Hz -800Hz , ref. 20µPa (infinite baffle / 2pi) \n89.0 \ndB\n"
                "Resonance frequency \n30 Hz\nMinimum impedance above resonance \n4.2 \nΩ\nFigure 2 Impedance Response @ 2.83V \n")
        spl = [[f, 80.0, 0.0] for f in (100.0, 300.0, 500.0, 800.0, 1000.0)]
        z = [[0.366211, 3.1, 0.0], [0.366212, 3.2, 0.0], [300.0, 4.21, 0.0], [1000.0, 6.0, 0.0]]
        files = [{"name": "W - SPL.txt", "header": ["freq [Hz]          dBV  Phase [deg]"], "rows": spl},
                 {"name": "W - Z.txt", "header": ["freq [Hz]          Ohm  Phase [deg]"], "rows": z}]
        made, skipped = self.S.build_others(self.probe(files, text), self.db())
        kinds = {s["kind"]: s for _, s in made}
        self.assertEqual(set(kinds), {"frequency-response", "impedance"}, skipped)
        self.assertEqual(kinds["frequency-response"]["conditions"]["drive_v"], 1.0)  # 9.0 dB under 2.83 V
        self.assertIn("what 1 V gives", kinds["frequency-response"]["note"])
        zp = kinds["impedance"]["series"][0]["points"]
        self.assertLess(zp[0]["x"], zp[1]["x"])  # close low frequencies stay apart
        self.assertNotIn("drive_v", kinds["impedance"]["conditions"])   # the file does not state it; the figure's caption is not proof
        self.assertIn("drawn at 2.83 V", kinds["impedance"]["note"])
        self.assertIn("4.21 ohm at 300 Hz, the datasheet states 4.2 ohm", kinds["impedance"]["note"])


class PageCharts(unittest.TestCase):
    """capture/sets_from_page_charts.py: a curve named by the colour of its legend line."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "capture"))
        import sets_from_page_charts as S
        self.S = S

    def test_colour_families(self):
        f = self.S.family
        self.assertEqual([f("#080808"), f("#282828"), f("#f80808"), f("#08f808"), f("#0808f8"), f("#2828f8"), f("#4848f8")], ["k", "k", "r", "g", "b", "b", None])  # a pale edge shade is not a curve
        self.assertIsNone(f("#d8d8f8"))                    # a light tint is not a curve
        self.assertIsNone(f("#b8b8b8"))                    # nor a grey grid line
        self.assertEqual(f("#88f888", strict=False), "g")  # a thin legend line is drawn lighter

    def test_series_by_legend_colour(self):
        pts = lambda y: [{"x": 100.0 * 2 ** (i / 24), "y": y} for i in range(80)]
        img = {"describe": {
            "legend_swatches": [{"angle": 0, "swatch": {"colour": "#080808"}}, {"angle": 15, "swatch": {"colour": "#88f888"}},
                                {"angle": 30, "swatch": {"colour": "#f88888"}}, {"angle": 60, "swatch": {"colour": "#8888f8"}}],
            "off_axis_read": {"curves": [
                {"colour": "#0808f8", "columns": 900, "points": pts(-6)}, {"colour": "#4848f8", "columns": 300, "points": pts(-9)},
                {"colour": "#f80808", "columns": 500, "points": pts(-3)}, {"colour": "#080808", "columns": 1400, "points": pts(0)},
                {"colour": "#d8d8f8", "columns": 1200, "points": pts(-20)}]}}}
        got = {a: (c, p[0]["y"] if p else None) for a, c, p, _ in self.S.chart_series(img)}
        self.assertEqual(got, {0: ("black", 0), 15: ("green", None), 30: ("red", -3), 60: ("blue", -6)})

    def test_gaps(self):
        pts = [{"x": 100.0 * 2 ** (i / 24), "y": 0} for i in range(24)] + [{"x": 400.0, "y": 0}]
        self.assertEqual(len(self.S.gaps_of(pts)), 1)


class ChartFloor(unittest.TestCase):
    """capture/chart_read.py reads down to the chart's floor line (the black bottom frame, one grid step below the
    last grey grid row), not only to the last grey row: a harmonic at -98 dB on a chart ending at -100 dB is read."""

    def test_curve_in_the_bottom_row(self):
        import shutil
        if not shutil.which("tesseract"):
            raise unittest.SkipTest("tesseract is not installed")
        try:
            from PIL import Image, ImageDraw, ImageFont
            sys.path.insert(0, str(ROOT / "capture"))
            import chart_read as CR
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        im = Image.new("RGB", (1276, 635), (0, 224, 0))
        d = ImageDraw.Draw(im)
        font = ImageFont.load_default(size=18)
        x0, x1, rows = 80, 1240, list(range(60, 589, 33))
        for i, y in enumerate(rows):
            d.line((x0, y, x1, y), fill=(0, 0, 0) if y in (rows[0], rows[-1]) else (128, 128, 128))
            d.text((20, y - 9), str(-20 - 5 * i), fill=(0, 0, 0), font=font)
        lx = lambda f: x0 + (math.log10(f) - math.log10(20)) / 3 * (x1 - x0)
        for f in (20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000,
                  6000, 7000, 8000, 9000, 10000, 20000):
            d.line((round(lx(f)), rows[0], round(lx(f)), rows[-1]), fill=(128, 128, 128))
        for f, label in ((20, "20"), (100, "100"), (1000, "1k"), (10000, "10k"), (20000, "20k")):
            d.text((round(lx(f)) - 10, rows[-1] + 12), label, fill=(0, 0, 0), font=font)
        curve = lambda f: -40 - 58 * math.exp(-((math.log10(f) - 2.3) ** 2) / 0.05)    # dips to -98 dB near 200 Hz
        ydb = lambda v: rows[0] + (-20 - v) / 5 * 33
        d.line([(lx(20 * 10 ** (i / 400 * 3)), ydb(curve(20 * 10 ** (i / 400 * 3)))) for i in range(401)], fill=(255, 0, 0), width=2)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic_315mm_4v_hpf2-60.png"
            im.save(p)
            rec = CR.read_chart(p, "harmonics")
        self.assertEqual(rec.get("plot_floor_row"), rows[-1])
        red = [c for c in rec["curves"] if c["colour"] == "#f80808"]
        self.assertTrue(red, rec.get("skipped"))
        low = min(red[0]["points"], key=lambda q: q["y"])
        self.assertLess(low["y"], -97)                       # below -95 dB: the row the reader used to cut off
        self.assertAlmostEqual(low["y"], curve(low["x"]), delta=0.5)


class DatabaseLayout(unittest.TestCase):
    """watch/common.py dumps_db: each curve's points on one line, the same data back."""

    def test_round_trip(self):
        sys.path.insert(0, str(ROOT / "watch"))
        from common import dumps_db
        db = {"drivers": [{"id": "x", "note": "a \u0000 NUL, \"quotes\", the word points", "measurements": [
            {"series": [{"name": "0°", "points": [{"x": 20.0, "y": -1.5}, {"x": 40.0, "y": None}]}]}, {"series": [{"points": []}]}]}]}
        text = dumps_db(db)
        self.assertEqual(json.loads(text), db)
        self.assertIn('"points": [{"x":20.0,"y":-1.5},{"x":40.0,"y":null}]', text)


class StrayPoints(unittest.TestCase):
    def test_islands(self):
        sys.path.insert(0, str(ROOT / "capture"))
        import sets_from_page_charts as S
        run = [{"x": 1000 * 2 ** (i / 24), "y": 0.0} for i in range(30)]
        kept, dropped = S.islands([{"x": 20.0, "y": -14.0}] + run + [{"x": 9000.0, "y": -34.0}])
        self.assertEqual(len(kept), 30)
        self.assertEqual([q["x"] for q in dropped], [20.0, 9000.0])
        self.assertEqual(S.islands(run), (run, []))


class LocalCapture(unittest.TestCase):
    """capture/file_curves.py and capture/read_local_charts.py, as used on David's computer."""

    def test_file_curves_keeps_rows_as_printed(self):
        sys.path.insert(0, str(ROOT / "capture"))
        import file_curves as FC
        text = "* HiFiCompass\n0 50 0\n20 80.1234 -12\n25.5,81.2,-10\nfreq db\n"
        self.assertEqual(FC.rows_of(text), [(20.0, 80.123), (25.5, 81.2)])

    def test_local_readings_replace_the_drivers_earlier_ones(self):
        import shutil
        if not shutil.which("tesseract"):
            raise unittest.SkipTest("tesseract is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            out = tmp / "chart_read.json"
            out.write_text(json.dumps({"date": "2026-09-01", "drivers": {"m74t-6": [
                {"file": "old_local.png", "read_on": "David’s computer", "curves": []},
                {"file": "from_github.png", "curves": []}]}}), encoding="utf-8")
            from PIL import Image
            Image.new("RGB", (400, 300), (255, 255, 255)).save(tmp / "blank_offaxis.png")
            (tmp / "charts.tsv").write_bytes("﻿blank_offaxis.png\toff-axis\thttps://example.invalid/a.png\n".encode("utf-8"))
            r = subprocess.run([sys.executable, str(ROOT / "capture" / "read_local_charts.py"), "--id", "m74t-6", "--dir", str(tmp),
                                "--out", str(out)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
            self.assertEqual(r.returncode, 0, r.stderr)
            files = [c["file"] for c in json.loads(out.read_text(encoding="utf-8"))["drivers"]["m74t-6"]]
            self.assertEqual(files, ["from_github.png", "blank_offaxis.png"])   # the old local reading is gone
