"""Pull real warranty payments + revenue from SEC XBRL 'frames' API.

Usage: python scripts/fetch_sec_warranty.py [YEAR]
Writes data/reference/sec_warranty_<YEAR>.csv
SEC asks for a descriptive User-Agent; keep it generic.
"""
import csv, json, sys, urllib.request
from pathlib import Path

YEAR = sys.argv[1] if len(sys.argv) > 1 else "2024"
UA = {"User-Agent": "hackathon-research-script admin@example.com"}
BASE = "https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/CY{y}.json"
REVENUE_TAGS = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]


def frame(tag):
    req = urllib.request.Request(BASE.format(tag=tag, y=YEAR), headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {d["cik"]: d for d in json.load(r)["data"]}
    except Exception as e:  # tag may not exist for that year
        print(f"skip {tag}: {e}", file=sys.stderr)
        return {}


warranty = frame("ProductWarrantyAccrualPayments")
revenue = {}
for tag in REVENUE_TAGS:  # first tag wins per company
    for cik, d in frame(tag).items():
        revenue.setdefault(cik, d["val"])

rows = []
for cik, d in warranty.items():
    rev = revenue.get(cik)
    rows.append({
        "company": d["entityName"],
        "cik": cik,
        "warranty_payments_usd": d["val"],
        "revenue_usd": rev or "",
        "warranty_pct_revenue": round(100 * d["val"] / rev, 2) if rev else "",
    })
rows.sort(key=lambda r: -r["warranty_payments_usd"])

out = Path(__file__).resolve().parent.parent / "data" / "reference" / f"sec_warranty_{YEAR}.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} companies -> {out}")
