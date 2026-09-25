#!/usr/bin/env python3
"""Records for drivers found by capture/inventory.py: one record per model, named as the page names it,
with the page address in `source`, the role from the model type and the measured parameters read from
the page's tables when their labels are recognised. Nothing else is invented: no band, no findings.

  python3 capture/new_from_inventory.py [--inventory capture/inventory.json] [--write]

Without --write it prints the records it would add. With --write it adds them through capture/add_set.py
(each is validated). A model whose record already exists (same id) is left alone.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# the T/S labels HiFiCompass uses (case-insensitive, unit stripped) -> keys of the record's `ts`
LABELS = {"fs": "Fs", "re": "Re", "qms": "Qms", "qes": "Qes", "qts": "Qts", "vas": "Vas", "sd": "Sd", "bl": "Bl", "mms": "Mms",
          "cms": "Cms", "rms": "Rms", "le": "Le", "xmax": "Xmax", "sensitivity": "sensitivity", "spl": "sensitivity", "pe": "Pe", "n0": "n0"}
ROLE = [("tw", "tweeter"), ("t2", "tweeter"), ("t3", "tweeter"), ("mr", "midrange"), ("m7", "midrange"), ("mw", "midwoofer"), ("wo", "woofer"), ("sw", "subwoofer")]


def role_of(model):
    m = model.lower().split()[-1]
    for pre, role in ROLE:
        if m.startswith(pre):
            return role
    return ""


def number(s):
    m = re.search(r"-?\d+(?:[.,]\d+)?", s.replace(" ", " "))
    return float(m.group(0).replace(",", ".")) if m else None


def ts_from_tables(tables):
    ts = {}
    for t in tables:
        for row in t:
            if len(row) < 2:
                continue
            label = re.sub(r"[\s,]*\(.*?\)|[\s,]*\[.*?\]|:$", "", row[0]).strip().lower()
            label = re.sub(r"[^a-z0-9]", "", label)
            key = LABELS.get(label)
            if key and number(row[1]) is not None:
                ts[key] = number(row[1])
    return ts


def records(inv):
    out = []
    for model, rec in inv["models"].items():
        pages = [p for p in rec["pages"] if not p.get("error")]
        if not pages:
            continue
        pg = pages[0]
        slug = pg["url"].rstrip("/").rsplit("/", 1)[-1]
        name = pg["h1"] or pg["title"].split("|")[0].strip() or model
        maker = " ".join(model.split()[:-1]) if " " in model else model
        if not name.lower().startswith(maker.split()[0].lower()):
            name = f"{maker} {name}"
        out.append({"id": re.sub(r"[^A-Za-z0-9._-]+", "-", slug.lower()).strip("-"), "name": name, "manufacturer": maker.replace(" Satori", ""),
                    "role": role_of(model), "band": "", "ts": ts_from_tables(pg["tables"]), "findings": "",
                    "source": pg["url"], "updated": inv["date"], "measurements": []})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", default=str(ROOT / "capture" / "inventory.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    inv = json.loads(Path(a.inventory).read_text())
    db = json.loads((ROOT / "drivers.json").read_text())
    have = {d["id"] for d in db["drivers"]}
    recs = [r for r in records(inv) if r["id"] not in have]
    for r in recs:
        print(json.dumps(r, ensure_ascii=False))
    if a.write:
        for r in recs:
            tmp = ROOT / "capture" / f"_new_{r['id']}.json"
            tmp.write_text(json.dumps(r, ensure_ascii=False))
            subprocess.run([sys.executable, str(ROOT / "capture" / "add_set.py"), "--new-driver", str(tmp)], check=True)
            tmp.unlink()
        print(f"{len(recs)} record(s) added")


if __name__ == "__main__":
    main()
