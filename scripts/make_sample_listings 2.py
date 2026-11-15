"""SAMPLE marketplace listings (made up, realistic) for every KB part, until Brandon's real listings land.

    python scripts/make_sample_listings.py      # -> data/reference/listings_sample.csv

Every row is marked sample=yes and has no URL. Sellers are generic types, not real companies, so no real business
is shown with an invented price. Real rows in data/reference/listings.csv (Brandon) replace these per part.
Prices are anchored on rough street prices (estimates) and vary by condition and channel.
"""
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R = random.Random(23)

# rough street-price anchors in USD for one unit in "new" condition (estimates for the demo, not quotes)
ANCHOR = {
    "1756-L61": 6500, "1769-L32E": 3200, "1764-LSP": 1100, "1747-L542": 2400, "1785-L40B": 6000, "22B-D010N104": 1150,
    "22B-B8P0N104": 700, "2711P-T10C4D8": 5200, "2094-BC01-MP5-S": 4800, "6ES7315-2AG10-0AB0": 2300,
    "6ES7313-5BG04-0AB0": 1600, "6SE6440-2UD24-0BA1": 1400, "6AV6643-0CD01-1AX1": 3900, "ACS550-U1-012A-4": 2100,
    "FX2N-48MR-001": 900, "FX3U-32MR/ES-A": 750, "1756-L83E": 14500, "5069-L320ER": 6800, "25B-D010N104": 1350,
    "25B-B8P0N104": 820, "2711P-T10C22D9P": 6200, "2198-D006-ERS3": 3600, "6ES7515-2AM02-0AB0": 4400,
    "6ES7214-1AG40-0XB0": 520, "6SL3210-1KE21-3UF1": 1150, "ACS580-01-012A-4": 1900, "FX5U-32MR/ES": 680,
    "1766-L32BWA": 900, "6ES5943-7UB11": 2500, "6AV2124-0MC01-0AX0": 3300,
}
# channel: (seller label, authorized, condition options with price factor, lead time days, warranty months, trust)
CHANNELS = {
    "authorized_distributor": ("Authorized distributor", "yes", [("new", 1.0)], (5, 140), 12, (0.95, 0.99)),
    "oem": ("Manufacturer direct", "yes", [("new", 1.05)], (20, 180), 12, (0.97, 1.0)),
    "refurbisher": ("Industrial refurbisher", "no", [("refurbished", 0.55), ("new_surplus", 0.8)], (2, 10), 24, (0.8, 0.9)),
    "surplus": ("Surplus dealer", "no", [("new_surplus", 0.7), ("used", 0.4)], (3, 12), 3, (0.65, 0.8)),
    "marketplace": ("eBay seller", "no", [("used", 0.32), ("for_repair", 0.12), ("used", 0.38)], (4, 14), 0, (0.4, 0.75)),
}


def main():
    kb = pd.read_csv(ROOT / "data/reference/kb.csv", dtype=str).fillna("")
    rows = []
    for k in kb.itertuples():
        base = ANCHOR.get(k.part_no, 1500)
        active = k.lifecycle_status in ("active", "active_mature", "unknown")
        if k.part_no == "6ES5943-7UB11":  # the rare one: a single doubtful listing -> alternatives path
            plan = ["marketplace"]
        elif active:
            plan = ["authorized_distributor", "oem", "surplus", "marketplace"]
        elif k.lifecycle_status == "end_of_life":
            plan = ["authorized_distributor", "refurbisher", "surplus", "marketplace"]
        else:  # discontinued: no new units from the manufacturer, scarcer, scarcity premium on good stock
            plan = ["refurbisher", "refurbisher", "surplus", "marketplace", "marketplace"]
            base *= 1.25
        for ch in plan:
            label, auth, conds, (lt_lo, lt_hi), warranty, (t_lo, t_hi) = CHANNELS[ch]
            cond, factor = R.choice(conds)
            rating = round(R.uniform(97.0, 100.0), 1) if ch == "marketplace" else ""
            rows.append({
                "listing_id": f"LS-{len(rows) + 1:04d}", "kb_id": k.kb_id, "part_no": k.part_no, "channel": ch,
                "seller": f"{label} {chr(65 + R.randint(0, 5))}" if ch != "marketplace" else f"{label} ({rating}% positive, {R.randint(80, 4000)} sales)",
                "seller_location": R.choice(["OH", "IL", "TX", "PA", "MI", "NJ", "CA", "GA", "WI", "NC"]),
                "authorized": auth, "condition": cond, "price": round(base * factor * R.uniform(0.9, 1.15), -1),
                "currency": "USD", "qty_available": R.randint(1, 6), "sold_price": "",
                "shipping": R.choice([0, 25, 45, 80]), "lead_time_days": R.randint(lt_lo, lt_hi), "warranty_months": warranty,
                "seller_rating": rating, "seller_sales_count": "", "returns_accepted": R.choice(["yes", "no"]) if ch == "marketplace" else "yes",
                "trust_score": round(R.uniform(t_lo, t_hi), 2), "url": "", "seen_on": "2026-11-14", "sample": "yes",
            })
    out = ROOT / "data/reference/listings_sample.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"{len(rows)} sample listings for {kb.shape[0]} parts -> {out.name}")


if __name__ == "__main__":
    main()
