#!/usr/bin/env python3
"""Check drivers.json and drivers_survey_midbass.json against the driver-db
conventions, so a hand-made or automated addition cannot break index.html.

Rules (from meta.policy): ids are unique and never merged; every driver and every
measurement carries a source; each measurement set comes from exactly one source
family (watch/config.json 'families'), so sources are never blended; measurements
are line | bar | table with data the viewer can draw; comparisons only reference
drivers that exist; every measurement names its kind from schema/kinds.json, and kinds
taken at a sound pressure level state that level (conditions.spl_db or ref_spl_db); Thiele/Small
parameters are numbers.

Warnings (do not fail the check): curves on a logarithmic frequency axis captured
with fewer points per decade than 'capture.minimum_points_per_decade' (CAPTURE.md).

Usage: python3 watch/validate_db.py [files...]   (exit code 1 on any error)
"""
import json
import re
import numbers
import sys
from pathlib import Path

from common import family_kind, families_of, load_config, points_per_decade

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = [ROOT / "drivers.json", ROOT / "drivers_survey_midbass.json"]
CONFIDENCE = {"high", "medium", "low", "none"}
KINDS = {k["id"]: k for k in json.loads((ROOT / "schema" / "kinds.json").read_text())["kinds"]}


def level_of(m):
    c = m.get("conditions") or {}
    for key in ("spl_db", "ref_spl_db"):
        v = c.get(key)
        if isinstance(v, numbers.Number):
            return v
    return None


def check_set(where, m, errors, warnings, cfg):
    for f in ("type", "kind", "source", "chartType"):
        if not m.get(f):
            errors.append(f"{where}: missing '{f}'")
    kind = KINDS.get(m.get("kind"))
    if m.get("kind") and not kind:
        errors.append(f"{where}: kind {m['kind']!r} is not in schema/kinds.json ({', '.join(KINDS)})")
    elif kind and kind.get("level") in ("spl", "spl-near") and level_of(m) is None:
        errors.append(f"{where}: a {kind['id']} set must state its level as a number in conditions.spl_db")
    elif kind and kind.get("level") == "stated" and not any(isinstance((m.get("conditions") or {}).get(k), numbers.Number) for k in ("x_pk_mm", "drive_v")):
        errors.append(f"{where}: a {kind['id']} set must state its level as a number in conditions.x_pk_mm (mm) or conditions.drive_v (V)")
    fams = families_of(m.get("source"), cfg)
    if m.get("source") and not fams:
        errors.append(f"{where}: source {m['source'][:60]!r} names no known source family; name the source "
                      f"(for example 'HiFiCompass ...' or 'datasheet ...') or add a family to watch/config.json")
    elif len(fams) > 1:
        errors.append(f"{where}: source {m['source'][:60]!r} names several source families ({', '.join(fams)}); "
                      f"keep one measurement set per source")
    density = points_per_decade(m)
    floor = cfg.get("capture", {}).get("minimum_points_per_decade", 40)
    if density is not None and density < floor and not any(family_kind(f, cfg) == "derived" for f in fams):
        warnings.append(f"{where}: {density:.0f} points per decade, below the {floor} minimum (CAPTURE.md)")
    if m.get("confidence") not in CONFIDENCE:
        errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}, got {m.get('confidence')!r}")
    ct = m.get("chartType")
    if ct in ("line", "bar"):
        series = m.get("series")
        if not isinstance(series, list) or not series:
            errors.append(f"{where}: {ct} chart needs a non-empty 'series' list")
            return
        for si, s in enumerate(series):
            if not s.get("name"):
                errors.append(f"{where} series {si}: missing 'name'")
            for pi, p in enumerate(s.get("points") or []):
                if not (isinstance(p, dict) and isinstance(p.get("x"), numbers.Number)
                        and (p.get("y") is None or isinstance(p.get("y"), numbers.Number))):
                    # y may be null: a product below the noise floor, drawn as a gap
                    errors.append(f"{where} series '{s.get('name')}' point {pi}: x must be a number and y a number "
                                  f"or null, got {p!r}")
                    break
        if not isinstance(m.get("axes"), dict):
            errors.append(f"{where}: {ct} chart needs 'axes'")
    elif ct == "table":
        cols, rows = m.get("columns"), m.get("rows")
        if not isinstance(cols, list) or not cols or not isinstance(rows, list):
            errors.append(f"{where}: table needs 'columns' and 'rows' lists")
            return
        for ri, r in enumerate(rows):
            if not isinstance(r, list) or len(r) != len(cols):
                errors.append(f"{where} row {ri}: has {len(r) if isinstance(r, list) else '?'} cells, "
                              f"table has {len(cols)} columns")
    elif ct:
        errors.append(f"{where}: chartType must be line, bar or table, got {ct!r}")


def validate(paths):
    cfg = load_config()
    errors, warnings, ids = [], [], {}
    comparisons = []
    for path in paths:
        try:
            db = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{path}: cannot parse ({e})")
            continue
        name = Path(path).name
        if not isinstance(db.get("meta"), dict) or not db["meta"].get("updated"):
            errors.append(f"{name}: missing meta.updated")
        drivers = db.get("drivers")
        if not isinstance(drivers, list):
            errors.append(f"{name}: 'drivers' must be a list")
            continue
        for i, d in enumerate(drivers):
            did = d.get("id")
            where = f"{name} driver {did or '#' + str(i)}"
            if not did:
                errors.append(f"{where}: missing 'id'")
            elif not re.fullmatch(r"[A-Za-z0-9._-]+", str(did)):
                errors.append(f"{where}: id may only use letters, digits, '.', '-' and '_' (a comma, '@' or space would break the Compare link)")
            elif did in ids:
                errors.append(f"{where}: duplicate id (also in {ids[did]})")
            else:
                ids[did] = name
            for f in ("name", "manufacturer", "role"):
                if not d.get(f):
                    errors.append(f"{where}: missing '{f}'")
            if not isinstance(d.get("ts", {}), dict):
                errors.append(f"{where}: 'ts' must be an object")
            else:
                for k, v in (d.get("ts") or {}).items():
                    if isinstance(v, str):
                        try:
                            float(v)
                            errors.append(f"{where}: parameter {k} = {v!r} is text; write it as a number")
                        except ValueError:
                            warnings.append(f"{where}: parameter {k} = {v!r} is not a number (unknown value?)")
            ms = d.get("measurements")
            if not isinstance(ms, list):
                errors.append(f"{where}: 'measurements' must be a list")
                continue
            for mi, m in enumerate(ms):
                check_set(f"{where} measurement {mi} ({m.get('type', '?')})", m, errors, warnings, cfg)
        for c in db.get("comparisons", []):
            comparisons.append((name, c))
    for name, c in comparisons:
        where = f"{name} comparison {c.get('id') or c.get('title')}"
        if not c.get("id"):
            errors.append(f"{where}: missing 'id'")
        elif c["id"] in ids:
            errors.append(f"{where}: id clashes with a driver id")
        for ref in c.get("drivers", []):
            if ref not in ids:
                errors.append(f"{where}: references unknown driver id '{ref}'")
        check_set(where, c, errors, warnings, cfg)
    return errors, warnings, len(ids)


if __name__ == "__main__":
    paths = sys.argv[1:] or [p for p in DEFAULT if p.exists()]
    errors, warnings, n = validate(paths)
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")
    print(f"{n} drivers checked in {len(paths)} file(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)
