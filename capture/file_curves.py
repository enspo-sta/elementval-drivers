#!/usr/bin/env python3
"""A measurement data file (.frd sound pressure, .zma impedance, or a text file of the same kind) as a series file
for capture/add_set.py: every row as the file prints it (frequency and level or ohm; the phase column and rows at
0 Hz are left out), written to six significant digits of frequency and 0.001 of a unit.

  python capture/file_curves.py incoming/<id>/<file>.frd --name "0°" --out incoming/<id>/frd_0deg.json
  python capture/file_curves.py incoming/<id>/<file>.zma --name Z --out incoming/<id>/zma.json

Then: python capture/add_set.py --driver <id> --set <meta.json> --series <that file> (python3 on Linux and macOS).
"""
import argparse
import json
import re
from pathlib import Path

NUM = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")


def rows_of(text):
    rows = []
    for ln in text.splitlines():
        cells = [c for c in re.split(r"[\s,;]+", ln.strip()) if c]
        if len(cells) >= 2 and all(NUM.match(c) for c in cells[:2]):
            f, v = float(cells[0]), float(cells[1])
            if f > 0:
                rows.append((float(f"{f:.6g}"), round(v, 3)))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--name", required=True, help="the series name: '0°', 'SPL', 'Z', ...")
    ap.add_argument("--out", required=True, help="the series file to write (UTF-8)")
    a = ap.parse_args()
    data = Path(a.file).read_bytes()
    text = data.decode("utf-8-sig", errors="replace") if not data.startswith((b"\xff\xfe", b"\xfe\xff")) else data.decode("utf-16")
    rows = rows_of(text)
    if len(rows) < 10:
        raise SystemExit(f"{a.file}: only {len(rows)} rows of numbers found; not a measurement file?")
    if any(b[0] <= a_[0] for a_, b in zip(rows, rows[1:])):
        raise SystemExit(f"{a.file}: the frequencies do not rise row by row; check the file")
    out = {"series": [{"name": a.name, "points": [{"x": f, "y": v} for f, v in rows]}]}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(rows)} rows, {rows[0][0]:g} Hz to {rows[-1][0]:g} Hz, written to {a.out}")


if __name__ == "__main__":
    main()
