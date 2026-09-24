#!/usr/bin/env python3
"""Open one GitHub issue per newly found driver, plus one digest issue for new
material (pages, PDFs, measurements) about drivers already in the database.

Reads the findings file written by watch_sources.py. Needs GITHUB_TOKEN and
GITHUB_REPOSITORY (both set automatically inside GitHub Actions). An issue
is never opened twice for the same model: every issue carries a hidden
'driver-key' marker, and all issues with the label (open or closed) are checked
first. Closing an issue therefore means "seen, not wanted"; to stop a model
being tracked at all, add it to "ignore" in watch/config.json.

Usage: python3 watch/open_issues.py findings.json
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
LABEL_NEW, LABEL_UPD = "new-driver", "driver-update"


def gh(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                                          "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "null")


def existing_keys(repo, label):
    keys, page = set(), 1
    while True:
        issues = gh("GET", f"/repos/{repo}/issues?labels={label}&state=all&per_page=100&page={page}")
        for i in issues:
            keys.update(re.findall(r"<!-- driver-key: ([A-Z0-9]+) -->", i.get("body") or ""))
        if len(issues) < 100:
            return keys
        page += 1


def ensure_label(repo, name, color, desc):
    try:
        gh("POST", f"/repos/{repo}/labels", {"name": name, "color": color, "description": desc})
    except urllib.error.HTTPError as e:
        if e.code != 422:        # 422 = already exists
            raise


def stub(d):
    slug = re.sub(r"[^a-z0-9]+", "-", f"{d['brand']} {d['display']}".lower()).strip("-")
    first = next(iter(d["sources"].values()))[0]
    return json.dumps({"id": slug, "name": f"{d['brand']} {d['display']}", "manufacturer": d["brand"],
                       "role": "", "band": "", "ts": {}, "findings": "stub - T/S not populated",
                       "source": first, "measurements": []}, indent=2, ensure_ascii=False)


def new_driver_body(d, date):
    links = "\n".join(f"- **{s}**: " + " · ".join(f"<{u}>" for u in urls[:6]) for s, urls in d["sources"].items())
    return f"""The weekly driver watch found a model that is not in `drivers.json` or the survey file.

**{d['brand']} {d['display']}** (first seen {date})

Where it was found:
{links}

### To add it
- [ ] Get the datasheet and any HiFiCompass or Erin's Audio Corner measurements linked above
- [ ] Extract T/S parameters and the distortion curves (harmonic and intermodulation), with a source on every measurement
- [ ] Add the record to `drivers.json` (the validation check runs on the pull request)
- [ ] Close this issue from the pull request with `Closes #<this issue>`

Not interested? Close the issue: it will not be reported again.

<details><summary>Empty record to start from</summary>

```json
{stub(d)}
```
</details>

<!-- driver-key: {d['key']} -->
"""


def main():
    findings = json.load(open(sys.argv[1]))
    repo = os.environ["GITHUB_REPOSITORY"]
    if findings.get("baseline"):
        print("Baseline run: no issues opened.")
        return 0
    ensure_label(repo, LABEL_NEW, "f0a44a", "Driver found by the weekly watch, not yet in the database")
    ensure_label(repo, LABEL_UPD, "6fd19a", "New source material for drivers already in the database")

    done = existing_keys(repo, LABEL_NEW)
    for d in findings["new_drivers"]:
        if d["key"] in done:
            continue
        i = gh("POST", f"/repos/{repo}/issues", {"title": f"New driver: {d['brand']} {d['display']}",
                                                 "body": new_driver_body(d, findings["date"]),
                                                 "labels": [LABEL_NEW]})
        print(f"opened #{i['number']} {d['brand']} {d['display']}")

    if findings["new_material"]:
        rows = "\n".join(
            f"- [ ] **{d['brand']} {d['display']}** (`{d['db_id']}`): " +
            "; ".join(f"{s}: " + " · ".join(f"<{u}>" for u in urls[:5]) for s, urls in d["sources"].items())
            for d in findings["new_material"])
        i = gh("POST", f"/repos/{repo}/issues", {
            "title": f"New source material for drivers in the database ({findings['date']})",
            "body": "Pages or PDFs mentioning these drivers appeared since the last scan "
                    "(a new datasheet revision, a new HiFiCompass or Erin's Audio Corner measurement, "
                    "or a page that simply moved). Check each and update the record if the data is new.\n\n"
                    + rows + "\n",
            "labels": [LABEL_UPD]})
        print(f"opened #{i['number']} update digest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
