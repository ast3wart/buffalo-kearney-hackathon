"""Download openly licensed REAL photos from Wikimedia Commons for KB part families (credited on screen).

    python scripts/fetch_commons_photos.py     # -> data/reference/photos/*.jpg + data/reference/photos/credits.csv

Each photo is mapped to KB parts with an honest match level: exact_family (same product family), same_family
(same family, different model), brand_style (same manufacturer, same kind of product), part_type (same kind of
part, other brand). Licenses: CC BY-SA / public domain, so the author + license + source link are shown with the photo.
"""
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/reference/photos"
UA = {"User-Agent": "equipment-xray-hackathon/0.1 (student project; credits shown on screen)"}

PHOTOS = [  # (Commons file title, kb_ids, match level, what it shows)
    ("SIMATIC S7-150.jpg", ["KB-023"], "exact_family", "Siemens SIMATIC S7-1500 CPU"),
    ("Simatic S5-100U CPU103.jpg", ["KB-029"], "same_family", "Siemens SIMATIC S5 CPU (S5-100U)"),
    ("BMA Automation Allen Bradley PLC 3.JPG", ["KB-001", "KB-017"], "brand_style", "Allen-Bradley rack PLC in a production control panel"),
    ("00-bma-automation-allen-bradley-1.JPG", ["KB-001", "KB-017"], "brand_style", "Allen-Bradley PLC rack inside a machine cabinet"),
    ("PLC Control Panel.png", ["KB-001", "KB-017"], "exact_family", "Allen-Bradley ControlLogix CPU in a panel"),
    ("PLC Control Panel.jpg", ["KB-002", "KB-018"], "exact_family", "Allen-Bradley CompactLogix PLC in a field panel"),
    ("Programmable logic controller.jpg", ["KB-003", "KB-028", "KB-004", "KB-005"], "brand_style", "Allen-Bradley micro, mini and rack PLCs"),
    ("Allen Bradley PLC.jpeg", ["KB-003", "KB-028"], "brand_style", "Allen-Bradley PLC on a training panel"),
    ("Small variable-frequency drive.jpg", ["KB-006", "KB-007", "KB-012", "KB-014", "KB-019", "KB-020", "KB-025", "KB-026"],
     "part_type", "A real variable-frequency drive (VFD)"),
]


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))


def clean(md, k):
    return re.sub("<[^>]+>", "", md.get(k, {}).get("value", "")).strip()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    info = api({"action": "query", "prop": "imageinfo", "iiprop": "extmetadata|url", "iiurlwidth": 1024,
                "titles": "|".join("File:" + t for t, *_ in PHOTOS)})
    by_title = {p["title"][5:]: (p.get("imageinfo") or [{}])[0] for p in info["query"]["pages"].values()}
    rows = []
    for i, (title, kb_ids, level, shows) in enumerate(PHOTOS, start=1):
        ii = by_title.get(title) or by_title.get(title.replace("_", " "))
        if not ii:
            print("missing:", title)
            continue
        md = ii.get("extmetadata", {})
        lic = clean(md, "LicenseShortName")
        if not any(x in lic for x in ("CC BY", "CC0", "Public domain")):
            print("skipping (license):", title, lic)
            continue
        fname = f"commons_{i:02d}" + (".png" if ii["thumburl"].lower().endswith(".png") else ".jpg")
        req = urllib.request.Request(ii["thumburl"], headers=UA)
        (OUT / fname).write_bytes(urllib.request.urlopen(req, timeout=60).read())
        rows.append({"file": fname, "commons_title": title, "author": clean(md, "Artist") or "unknown", "license": lic,
                     "license_url": clean(md, "LicenseUrl"), "source_url": ii.get("descriptionurl", ""),
                     "kb_ids": ";".join(kb_ids), "match_level": level, "shows": shows})
        print(f"{fname}  {title}  ({lic}, {rows[-1]['author']})  {(OUT / fname).stat().st_size // 1024} KB")
        time.sleep(1.5)
    with open(OUT / "credits.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} photos, credits in {OUT / 'credits.csv'}")


if __name__ == "__main__":
    main()
