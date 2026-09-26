"""Shared helpers for the watch/ scripts: settings, model numbers and source families.

A *source family* is where a measurement came from (a manufacturer datasheet,
HiFiCompass, Erin's Audio Corner, audioXpress, audiohorn, diyAudio, or a model
derived from other data). Every measurement set in the database belongs to
exactly one family, so data from different sources is never blended.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "watch" / "config.json"
STATE = ROOT / "watch" / "state.json"
DATABASES = [ROOT / "drivers.json", ROOT / "drivers_survey_midbass.json"]


def dumps_db(db):
    """The database as text: indented for reading, but each curve's points on one line (a point per four lines
    made the file several times larger and slow to load on a phone). Same data, only the layout differs."""
    import uuid
    kept = []
    token = "@@points-" + uuid.uuid4().hex + "-"          # a marker no string in the database contains (checked below)

    def walk(o):
        if isinstance(o, dict):
            out = {}
            for k, v in o.items():
                if k == "points" and isinstance(v, list):
                    kept.append(json.dumps(v, ensure_ascii=False, separators=(",", ":")))
                    out[k] = f"{token}{len(kept) - 1}"
                else:
                    out[k] = walk(v)
            return out
        if isinstance(o, list):
            return [walk(x) for x in o]
        return o

    text = json.dumps(walk(db), indent=2, ensure_ascii=False)
    if text.count(token) != len(kept):
        raise ValueError("the database contains the layout marker itself")
    out = re.sub('"' + re.escape(token) + r'(\d+)"', lambda m: kept[int(m.group(1))], text) + "\n"
    return out


def load_config():
    cfg = json.loads(CONFIG.read_text())
    cfg["_patterns"] = {n: (p["brand"], re.compile(p["regex"], re.I)) for n, p in cfg["patterns"].items()}
    cfg["_families"] = [(f["name"], f["kind"], re.compile(f["match"], re.I)) for f in cfg["families"]]
    for s in cfg["sources"]:
        s["_measured"] = re.compile(s["measurement_url"], re.I)
    cfg["_aliases"] = {key_of(k): v for k, v in cfg.get("aliases", {}).items() if k != "comment"}
    return cfg


def key_of(model):
    """Canonical identity: upper-case letters and digits only (PTT6.5X04-NAA-08 == ptt6-5x04-naa-08)."""
    return re.sub(r"[^A-Z0-9]", "", model.upper())


def pretty(model):
    """Display form. Slugs such as ptt6-5x04-naa-08 get their decimal point back."""
    m = model.upper().replace(" ", "")
    m = re.sub(r"^PTT(\d{1,2})-(\d{1,2})(?=[A-Z])", r"PTT\1.\2", m)
    m = re.sub(r"^(PTT[\d.]+[A-Z])-(\d{2})", r"\1\2", m)          # ptt6.5m-08 -> PTT6.5M08
    return re.sub(r"^((?:WO|MW|MR|TW|WB)\d{2})-(?=[A-Z])", r"\1", m)  # MW19-TX-8 -> MW19TX-8


def match_models(pattern, text, aliases=None):
    """Model numbers in text; a named group 'model' narrows the match to just the model number.
    Short forms listed in the settings' 'aliases' are replaced by the full model number."""
    for m in pattern.finditer(text):
        model = m.group("model") if "model" in pattern.groupindex else m.group(0)
        yield (aliases or {}).get(key_of(model), model)


def families_of(source_text, cfg):
    """Names of the source families a measurement's `source` string matches (should be exactly one)."""
    return [name for name, _, rx in cfg["_families"] if rx.search(source_text or "")]


def family_kind(name, cfg):
    return next((k for n, k, _ in cfg["_families"] if n == name), None)


def load_databases():
    """[(file name, database dict)] for the database files that exist."""
    return [(p.name, json.loads(p.read_text())) for p in DATABASES if p.exists()]


def driver_keys(driver, cfg):
    """Model keys found in a driver's name and id, e.g. {'PTT65X04NAA08'}."""
    text = f"{driver.get('name', '')} {driver.get('id', '')}"
    return {key_of(m) for _, rx in cfg["_patterns"].values() for m in match_models(rx, text, cfg["_aliases"])}


def database_keys(cfg):
    """{model key: driver id} for every driver whose name or id carries a tracked model number."""
    keys = {}
    for _, db in load_databases():
        for d in db.get("drivers", []):
            for k in driver_keys(d, cfg):
                keys.setdefault(k, d.get("id"))
    return keys


def points_per_decade(m):
    """Lowest point density (points per decade) over the series of a line chart on a logarithmic
    frequency axis, or None when the idea does not apply (bar charts, tables, linear axes)."""
    if m.get("chartType") != "line" or (m.get("axes") or {}).get("x", {}).get("scale") != "log":
        return None
    worst = None
    for s in m.get("series") or []:
        xs = [p["x"] for p in s.get("points") or [] if isinstance(p.get("x"), (int, float)) and p["x"] > 0]
        if len(xs) < 2 or max(xs) <= min(xs):
            continue
        decades = math.log10(max(xs) / min(xs))
        density = (len(xs) - 1) / decades
        worst = density if worst is None else min(worst, density)
    return worst
