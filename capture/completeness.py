#!/usr/bin/env python3
"""Does every driver have every curve its sources publish? One line per chart.

For each record in drivers.json, its HiFiCompass measurement page (from capture/inventory.json, found by the
record's page address or its model number) is compared chart by chart with the sets stored: a chart is stored
when a set names its file (the automatic reading does), stored by hand when a hand-captured set of the same
kind and source exists (those do not name the chart), else missing, with the reason. The page's data files and
parameter tables are counted too. Writes watch/completeness.json (read by the viewer's driver page) and
watch/completeness.md.

  python3 capture/completeness.py
"""
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "capture"))
sys.path.insert(0, str(ROOT / "watch"))
import chart_probe as CP  # noqa: E402
from common import families_of, load_config  # noqa: E402
from sets_from_chart_read import conditions, KIND  # noqa: E402
from worklist import hifi_page, PUBLISHES  # noqa: E402

# the kinds a hand capture of a chart type is stored as (a hand capture does not name the chart it came from)
HAND_KINDS = {"response": {"frequency-response"}, "harmonics": {"hd-frequency"}, "current": {"hd-current"},
              "impedance": {"impedance"}, "intermodulation": {"imd-summary", "imd-spectrum"}}

READ = {"response", "near-response", "off-axis", "harmonics", "current", "impedance"}           # what capture/chart_read.py reads
SPECTRA = {"intermodulation", "spectrum"}                                  # what capture/imd_read.py reads
WHY = {
    "intermodulation": "an intermodulation spectrum: not read yet (capture/imd_read.py)",
    "spectrum": "a one-tone spectrum: not read yet (capture/imd_read.py)",
    "off-axis": "off-axis responses (several angles in one image): not read automatically",
    "near-field": "a near-field chart: not read automatically",
    "step": "a step response: not a frequency curve the database stores",
    "waterfall": "a waterfall: not a frequency curve the database stores",
    "etc": "an energy-time curve: not a frequency curve the database stores",
    "other": "the older one-image-per-quantity template: capture by hand (capture/CHROME_CAPTURE.md)",
}
LABEL = {"response": "on-axis response", "harmonics": "harmonics", "current": "current distortion", "impedance": "impedance",
         "intermodulation": "intermodulation", "off-axis": "off-axis", "near-field": "near field",
         "near-response": "near-field response", "spectrum": "one-tone spectrum", "step": "step response",
         "waterfall": "waterfall", "etc": "energy-time", "other": "older template"}


def main():
    cfg = load_config()
    inv = json.loads((ROOT / "capture" / "inventory.json").read_text())
    db = json.loads((ROOT / "drivers.json").read_text())
    read = {}
    rp = ROOT / "capture" / "chart_read.json"
    if rp.exists():
        for charts in json.loads(rp.read_text()).get("drivers", {}).values():
            for c in charts:
                read[c.get("file")] = c
    ip = ROOT / "capture" / "imd_read.json"
    if ip.exists():
        for charts in json.loads(ip.read_text()).get("drivers", {}).values():
            for c in charts:
                read[c.get("file")] = c
    pages = {pg["url"]: pg for rec in inv["models"].values() for pg in rec.get("pages", [])}
    # a picture that several drivers' pages share is not a chart of one driver: on the older pages it is HiFiCompass's
    # Premium notice (read from offaxis.jpg, nf.jpg, chd.jpg, spectra.jpg, imd.jpg, step.jpg and the on-axis and
    # impedance pictures on 26 September 2026: "This data is only available to users with a Premium account")
    shared = Counter(link for pg in pages.values() for link in {im["original"].split("?")[0] for im in pg.get("charts", [])})
    out = {"date": dt.date.today().isoformat(), "inventory_date": inv.get("date"), "drivers": {}}
    for d in db["drivers"]:
        # a proxy or a pair is made from another record: it has no measurement page of its own
        derived = bool(re.search(r"proxy|pair|×\s*\d", d["name"], re.I))
        url = None if derived else (d.get("source") if d.get("source") in pages else hifi_page(d))
        hifi = [m for m in d["measurements"] if (families_of(m.get("source"), cfg) or [""])[0] == "HiFiCompass" and not m.get("superseded_by")]
        files = {m.get("file") for m in hifi if m.get("file")}
        by_hand = {m.get("kind") for m in hifi if not m.get("file")}
        rec = {"name": d["name"], "page": url, "charts": [], "data_files": [], "table_rows": 0, "parameters": len(d.get("ts") or {}),
               "datasheet": d.get("datasheet") or None}
        if url:
            pg = pages[url]
            for im in pg.get("charts", []):
                if CP.SKIP.search(im["original"]):
                    continue
                link = im["original"].split("?")[0]
                name = link.rsplit("/", 1)[-1]
                t = CP.chart_type(link)
                cond = conditions(name)
                c = {"file": name, "url": link, "type": t, "label": LABEL.get(t, t)}
                if t == "harmonics" and re.search(r"_(?:5|20)mm_", name):
                    c["label"] = "near-field harmonics"
                if cond.get("drive_v") is not None:
                    c["volts"] = cond["drive_v"]
                older = name.lower().endswith((".jpg", ".jpeg"))       # the older one-image-per-quantity template
                if name in files:
                    c["state"] = "stored"
                elif HAND_KINDS.get(t, set()) & by_hand:
                    c["state"] = "by hand"
                    c["why"] = "a hand-captured set of this kind exists; it does not name the chart it came from"
                elif shared[link] > 1 and re.search(r"/sites/default/files/[^/]+$", link):
                    c["state"] = "premium only"
                    c["why"] = (f"the page shows HiFiCompass's Premium notice here ('This data is only available to users with a Premium "
                                f"account'), the same picture on {shared[link]} drivers' pages: capture by hand when logged in with Premium (capture/CHROME_CAPTURE.md)")
                else:
                    c["state"] = "missing"
                    if older and "castom_img_zamer" in link:
                        c["why"] = "a picture from the page's gallery (on the WO24P-8 page these are product photos, not charts)"
                        c["label"] = "gallery picture"
                    elif older:
                        c["why"] = WHY["other"]
                    elif t in READ or t in SPECTRA:
                        err = (read.get(name) or {}).get("error")
                        c["why"] = f"the automatic reading failed: {err}" if err else "readable automatically, not read yet"
                    else:
                        c["why"] = WHY.get(t, "not read")
                rec["charts"].append(c)
            rec["data_files"] = [f["href"] for f in pg.get("data_files", [])]
            rec["table_rows"] = sum(len(t) for t in pg.get("tables", []))
            rec["premium_or_login"] = pg.get("premium_or_login") or None
        if derived:
            rec["page_note"] = "made from another record (a proxy or a pair): no measurement page of its own"
        # a Purifi datasheet: which of the kinds a Purifi datasheet has are stored (the PDF's figures are not inventoried)
        have = {m.get("kind") for m in d["measurements"] if (families_of(m.get("source"), cfg) or [""])[0] == "Manufacturer datasheet"}
        if d.get("manufacturer") == "Purifi" and not derived and have:       # only where the datasheet is known (a set from it is stored)
            rec["datasheet_kinds"] = [{"kind": k, "what": w, "stored": k in have} for k, w in PUBLISHES["Manufacturer datasheet"]]
        cnt = Counter(c["state"] for c in rec["charts"])
        rec["summary"] = {"published": len(rec["charts"]), "stored": cnt["stored"], "by_hand": cnt["by hand"], "missing": cnt["missing"],
                          "premium_only": cnt["premium only"],
                          "missing_by_type": dict(Counter(c["label"] for c in rec["charts"] if c["state"] == "missing"))}
        out["drivers"][d["id"]] = rec
    (ROOT / "watch" / "completeness.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    lines = ["# Does every driver have every curve?", "",
             f"Written by `capture/completeness.py` on {out['date']} from the HiFiCompass inventory of {inv.get('date')} "
             "(`capture/inventory.json`). A chart is *stored* when a set names its file (the automatic reading does), "
             "*by hand* when a hand-captured set of the same kind exists (it does not name the chart), *Premium only* when the "
             "page shows HiFiCompass's Premium notice in its place, else *missing*.", "",
             "| Driver | HiFiCompass page | Charts | Stored | By hand | Premium only | Missing | Missing, by kind | Parameters stored / table rows |",
             "|---|---|---|---|---|---|---|---|---|"]
    for did, r in out["drivers"].items():
        s = r["summary"]
        miss = ", ".join(f"{k} {v}" for k, v in sorted(s["missing_by_type"].items())) or "—"
        lines.append(f"| {r['name']} | {('<' + r['page'] + '>') if r['page'] else 'none found'} | {s['published']} | {s['stored']} | {s['by_hand']} | {s['premium_only']} | {s['missing']} | {miss} | {r['parameters']} / {r['table_rows']} |")
    lines += ["", "## Every chart not stored, and why", ""]
    for did, r in out["drivers"].items():
        miss = [c for c in r["charts"] if c["state"] != "stored"]
        if not miss:
            continue
        lines.append(f"- **{r['name']}** (`{did}`), <{r['page']}>:")
        for c in miss:
            lines.append(f"  - [{c['file']}]({c['url']}) · {c['label']}{' · ' + str(c['volts']) + ' V' if 'volts' in c else ''}: {c['state']}, {c['why']}")
    ds = [(did, r) for did, r in out["drivers"].items() if r.get("datasheet_kinds")]
    if ds:
        lines += ["", "## Purifi datasheets: the figures a Purifi datasheet has, stored or not", "",
                  "| Driver | " + " | ".join(x["what"] for x in ds[0][1]["datasheet_kinds"]) + " |", "|---|" + "---|" * len(ds[0][1]["datasheet_kinds"])]
        for did, r in ds:
            lines.append(f"| {r['name']} | " + " | ".join("stored" if x["stored"] else "**missing**" for x in r["datasheet_kinds"]) + " |")
    nopage = [r["name"] for r in out["drivers"].values() if not r["page"]]
    lines += ["", "Records without a HiFiCompass measurement page in the inventory: " + (", ".join(nopage) if nopage else "none") + ".",
              "(Either HiFiCompass has not measured that exact variant, or its page is a review without charts, or the record "
              "is a proxy or a pair made from another record.)"]
    (ROOT / "watch" / "completeness.md").write_text("\n".join(lines) + "\n")
    tot = Counter()
    for r in out["drivers"].values():
        for k in ("published", "stored", "by_hand", "premium_only", "missing"):
            tot[k] += r["summary"][k]
    print(f"watch/completeness.md: {len(out['drivers'])} drivers, {tot['published']} charts published, {tot['stored']} stored, "
          f"{tot['by_hand']} by hand, {tot['premium_only']} Premium only, {tot['missing']} missing")


if __name__ == "__main__":
    main()
