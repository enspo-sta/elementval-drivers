"""Tests for watch/pdf_curves.py on vector PDFs drawn here with known curves.

Run: python3 -m unittest discover -s tests -p "test_*.py"
Skips when PyMuPDF or matplotlib is missing (python3 -m pip install pymupdf matplotlib)."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "watch" / "pdf_curves.py"

dense = lambda f: -50 + 15 * math.sin(math.log10(f) * 2.3)                  # red: 500 points per decade
sparse_x = [20 * 10 ** (i / 60) for i in range(181)]                         # blue: 60 per decade, 20 Hz..20 kHz
sparse = lambda f: -65 + 8 * math.cos(math.log10(f) * 3.1)
sweep = lambda v: -95 + 60 * (v / 28.3) ** 1.5                              # black on a linear axis
grid_only = lambda v: -70 + 0.5 * v + 5 * math.sin(v / 7)


def run(*args, ok=True):
    out = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)
    if ok and out.returncode:
        raise AssertionError(out.stderr)
    return out


class SyntheticDatasheet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pymupdf  # noqa: F401
            import matplotlib
        except ImportError:
            raise unittest.SkipTest("PyMuPDF or matplotlib not installed")
        matplotlib.use("pdf")
        import matplotlib.pyplot as plt
        from matplotlib.patches import PathPatch
        from matplotlib.textpath import TextPath
        from matplotlib.transforms import Affine2D
        plt.rcParams["path.simplify"] = False
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)

        def glyphs(fig, x_px, y_px, text):
            p = TextPath((0, 0), text, size=8)
            fig.add_artist(PathPatch(p, facecolor="black", edgecolor="none", transform=Affine2D().translate(x_px, y_px)))

        # page 1: figure 7 (log frequency, grid, spines, legend, outlined tick labels) and figure 8 (linear x)
        fig = plt.figure(figsize=(6, 8), dpi=72)
        ax = fig.add_axes([0.12, 0.58, 0.8, 0.36])
        f = [20 * 10 ** (3 * i / 1500) for i in range(1501)]
        ax.semilogx(f, [dense(v) for v in f], color=(1, 0, 0), lw=1.44, label="H2")
        ax.semilogx(sparse_x, [sparse(v) for v in sparse_x], color=(0, 0, 1), lw=1.44, label="H3")
        ax.set_xlim(20, 20000); ax.set_ylim(-80, 0); ax.grid(True, which="both", color=(0.7, 0.7, 0.7))
        ax.legend(loc="upper right")
        ax.tick_params(labelbottom=False, labelleft=False)
        for i, lab in enumerate(["20", "200", "2k", "20k"]):
            glyphs(fig, 0.12 * 432 + i * 0.8 * 432 / 3 - 6, 0.58 * 576 - 12, lab)
        glyphs(fig, 0.12 * 432 - 22, 0.58 * 576 - 3, "-80")
        fig.text(0.12, 0.52, "Figure 7: current harmonic distortion at 2.83 V", fontsize=8)
        ax2 = fig.add_axes([0.12, 0.1, 0.8, 0.32])
        v = [28.3 * i / 800 for i in range(801)]
        ax2.plot(v, [sweep(x) for x in v], color=(0, 0, 0), lw=1.44)
        ax2.set_xlim(0, 28.3); ax2.set_ylim(-100, -20); ax2.grid(True)
        ax2.tick_params(labelbottom=False, labelleft=False)
        fig.text(0.12, 0.04, "Figure 8: current harmonic distortion at 1 kHz vs level", fontsize=8)
        cls.two = d / "two.pdf"
        fig.savefig(cls.two)
        plt.close(fig)

        # page 2: frame made only of grid lines (no outer rectangle), orange curve
        fig = plt.figure(figsize=(6, 4), dpi=72)
        ax = fig.add_axes([0.12, 0.2, 0.8, 0.7])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.patch.set_visible(False)
        v = [100 * i / 1000 for i in range(1001)]
        ax.plot(v, [grid_only(x) for x in v], color=(1, 0.655, 0.098), lw=1.44)
        ax.set_xlim(0, 100); ax.set_ylim(-80, 0)
        ax.set_xticks(range(0, 101, 10)); ax.set_yticks(range(-80, 1, 10)); ax.grid(True)
        ax.tick_params(length=0, labelbottom=False, labelleft=False)
        fig.text(0.12, 0.08, "Figure 3: grid only", fontsize=8)
        cls.grid = d / "grid.pdf"
        fig.savefig(cls.grid)
        plt.close(fig)

        # no frame at all: a curve and a caption
        fig = plt.figure(figsize=(6, 4), dpi=72)
        ax = fig.add_axes([0.1, 0.2, 0.8, 0.7])
        ax.axis("off")
        ax.plot(v, [grid_only(x) for x in v], color=(1, 0, 0), lw=1.44)
        fig.text(0.1, 0.08, "Figure 5: no frame", fontsize=8)
        cls.noframe = d / "noframe.pdf"
        fig.savefig(cls.noframe)
        plt.close(fig)

    def extract(self, pdf, *args):
        return json.loads(run(pdf, *args).stdout)

    def test_list_finds_both_figures_and_their_curves(self):
        figs = json.loads(run(self.two, "--list", "--json").stdout)
        by = {f["number"]: f for f in figs if f["number"]}
        self.assertEqual(sorted(by), [7, 8])
        self.assertEqual(sorted(c["name"] for c in by[7]["curves"]), ["blue", "red"])
        self.assertEqual([c["name"] for c in by[8]["curves"]], ["black"])
        self.assertIn("current harmonic distortion at 2.83 V", by[7]["caption"])

    def test_dense_log_curve_matches_and_is_thinned(self):
        out = self.extract(self.two, "--figure", 7, "--x", "20:20000:log", "--y=-80:0:lin", "--names", "red=H2,blue=H3")
        red = next(s for s in out["series"] if s["name"] == "H2")
        worst = max(abs(p["y"] - dense(p["x"])) for p in red["points"])
        self.assertLess(worst, 0.05, f"worst {worst:.4f} dB")
        self.assertLessEqual(len(red["points"]) / 3, 161)        # at most 160 per decade
        self.assertGreaterEqual(len(red["points"]) / 3, 150)
        self.assertLess(abs(red["points"][0]["x"] / 20 - 1), 0.005)
        self.assertLess(abs(red["points"][-1]["x"] / 20000 - 1), 0.005)

    def test_sparse_curve_keeps_its_points_exactly(self):
        out = self.extract(self.two, "--figure", 7, "--x", "20:20000:log", "--y=-80:0:lin", "--names", "blue=H3")
        blue = next(s for s in out["series"] if s["name"] == "H3")
        self.assertEqual(len(blue["points"]), len(sparse_x))
        for p, fx in zip(blue["points"], sparse_x):
            self.assertLess(abs(p["x"] / fx - 1), 0.005)
            self.assertLess(abs(p["y"] - sparse(fx)), 0.05)

    def test_linear_axis(self):
        out = self.extract(self.two, "--figure", 8, "--x", "0:28.3:lin", "--y=-100:-20:lin")
        pts = out["series"][0]["points"]
        self.assertLessEqual(len(pts), 402)
        worst = max(abs(p["y"] - sweep(p["x"])) for p in pts)
        self.assertLess(worst, 0.05, f"worst {worst:.4f} dB")

    def test_frame_from_grid_lines_only(self):
        out = self.extract(self.grid, "--figure", 3, "--x", "0:100:lin", "--y=-80:0:lin")
        pts = out["series"][0]["points"]
        self.assertEqual(out["series"][0]["name"], "orange")
        worst = max(abs(p["y"] - grid_only(p["x"])) for p in pts)
        self.assertLess(worst, 0.05, f"worst {worst:.4f} dB")
        self.assertLess(abs(pts[-1]["x"] - 100), 0.5)

    def test_no_frame_fails_clearly(self):
        out = run(self.noframe, "--figure", 5, "--x", "0:100:lin", "--y=-80:0:lin", ok=False)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("no plot frame", out.stderr)

    def test_bad_axis_spec_fails_clearly(self):
        out = run(self.two, "--figure", 7, "--x", "20:20000", "--y=-80:0:lin", ok=False)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("start:end:log", out.stderr)


if __name__ == "__main__":
    unittest.main()
