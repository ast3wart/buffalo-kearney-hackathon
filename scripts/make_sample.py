"""Write the SMALL hand-shaped sample dataset to data/sample/ (contract v3).

This is NOT the real generator (that's afterlife/generate.py). It exists so both threads can
build detection, cost, brief, and screens from hour 0. Fictional company: Prairie Utility Vehicles.

v3 story baked in (Brandon's CP0 review, #13): the hydraulic seal kit 200-1180-01 is DUAL-SOURCED.
  - Keystone Seal Works (S-022) supplies UV-400 and TR-250 all along, and half of UV-600 from April.
  - Bluewater Seal Co (S-023) supplies UV-600 (all of it Jan-Mar, half from April).
  - The spike sits ONLY on Keystone's April PO lot onward, so claims jump on UV-400 / TR-250 from
    April, partly on UV-600 (50% Keystone), and not on Bluewater-only builds.
    That makes "which supplier, which lot" a real inference instead of a lookup.

v4 (accounting fields): claims carry claim_date / paid_date / other_cost / recovered_usd, products carry
avg_selling_price, and each production supplier has a supplier quality agreement DOCUMENT in
supplier_agreements/ (recovery terms are extracted from text, they are not ERP fields). All v4 values come
from a separate RNG so every v3 value stays identical; only claims not yet reported by data_as_of drop out.

Run: python scripts/make_sample.py
"""
import csv
import datetime as dt
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from afterlife.profiles import COMMON, PROFILES, dataset_info, abbreviations_rows, failure_code_rows  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "data" / "sample"
rng = random.Random(42)
rng4 = random.Random(4242)  # v4 fields only, so the v3 draws above don't shift
PROFILE = PROFILES[0]  # Prairie vocabulary


def write_doc(name, text):
    d = OUT / "supplier_agreements"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text)


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


products = [
    {"product_id": "UV-400", "product_name": "Utility vehicle 400", "family": "utility_vehicle", "avg_selling_price": 14500.0},
    {"product_id": "UV-600", "product_name": "Utility vehicle 600", "family": "utility_vehicle", "avg_selling_price": 18900.0},
    {"product_id": "TR-250", "product_name": "Compact tractor 250", "family": "tractor", "avg_selling_price": 22500.0},
]

# part_no, ERP description, category, std_cost
parts = [
    ("100-4471-02", "BRG,BALL,6204-2RS,20MM", "bearing", 4.10),
    ("200-1180-01", "SEAL KIT,HYD CYL,40MM BORE", "seal", 11.50),   # dual-sourced, spike on one supplier's lot
    ("300-0912-00", "FLTR,OIL,SPIN-ON,M20X1.5", "filter", 3.20),
    ("400-2205-03", "BELT,CVT,DRIVE,32MM", "belt", 27.00),
    ("500-7731-01", "HOSE ASSY,HYD,3/8,24IN", "hose", 18.40),
    ("600-3310-00", "SW,IGN,KEYED,12V", "electrical", 9.75),
    ("700-5520-02", "PAD SET,BRAKE,FRT", "brake", 14.20),
    ("800-1004-00", "PUMP,FUEL,ELEC,12V", "fuel", 46.00),
]
part_master = [{"part_no": p, "description": d, "category": c, "std_cost": s} for p, d, c, s in parts]
std = {p: s for p, _, _, s in parts}
cat = {p: c for p, _, c, _ in parts}

bom_map = {
    "UV-400": [("100-4471-02", 4), ("200-1180-01", 2), ("300-0912-00", 1), ("400-2205-03", 1), ("600-3310-00", 1), ("700-5520-02", 2), ("800-1004-00", 1)],
    "UV-600": [("100-4471-02", 4), ("200-1180-01", 2), ("300-0912-00", 1), ("400-2205-03", 1), ("500-7731-01", 2), ("700-5520-02", 2), ("800-1004-00", 1)],
    "TR-250": [("100-4471-02", 6), ("200-1180-01", 4), ("300-0912-00", 1), ("500-7731-01", 4), ("600-3310-00", 1)],
}
positions = {"bearing": "axle", "seal": "hydraulic_cylinder", "filter": "engine", "belt": "drivetrain",
             "hose": "hydraulic_lines", "electrical": "dash", "brake": "front_brakes", "fuel": "fuel_system"}
bom = [{"product_id": prod, "part_no": p, "qty_per": q, "position": positions[cat[p]]}
       for prod, items in bom_map.items() for p, q in items]

months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
builds = [{"product_id": p["product_id"], "build_month": m, "units_built": rng.randint(180, 260)}
          for p in products for m in months]

SUP = {"S-011": ("Great Lakes Bearing Co", "US"), "S-022": ("Keystone Seal Works", "MX"),
       "S-023": ("Bluewater Seal Co", "US"),
       "S-031": ("Northfield Filtration", "US"), "S-044": ("Ridgeway Drive Systems", "US"),
       "S-052": ("Delta Fluid Power", "CN"), "S-063": ("Summit Electric Parts", "CN"),
       "S-070": ("Midland Brake Supply", "US"), "S-081": ("Harbor Fuel Components", "KR"),
       "S-090": ("QuickServe Parts Distribution", "US")}  # S-090 = service-team distributor
# production sources: part -> list of (supplier, supplier_pn, supplier wording, uom, pack size)
prod_src = {
    "100-4471-02": [("S-011", "6204-2RSH", "Deep groove ball bearing 20x47x14 sealed", "EA", 1)],
    "200-1180-01": [("S-022", "KSW-HC40-K", "Hydraulic cylinder seal kit 40 mm bore", "EA", 1),
                    ("S-023", "BW-SK40H", "Seal kit, hyd. cylinder, 40mm", "EA", 1)],
    "300-0912-00": [("S-031", "NF-M20-OS", "Spin-on oil filter M20 x 1.5", "BX10", 10)],
    "400-2205-03": [("S-044", "RDS-CVT32", "CVT drive belt 32mm", "EA", 1)],
    "500-7731-01": [("S-052", "DFP-3824", "Hydraulic hose assembly 3/8 in x 24 in", "EA", 1)],
    "600-3310-00": [("S-063", "SEP-IGN12K", "Keyed ignition switch 12V", "EA", 1)],
    "700-5520-02": [("S-070", "MBS-FP220", "Front brake pad set", "EA", 1)],
    "800-1004-00": [("S-081", "HFC-EFP12", "Electric fuel pump 12 V", "EA", 1)],
}

production_spend, service_spend, info_records, truth_links = [], [], [], []
lot = {}  # (part, supplier, "Q1"/"Q2") -> po_line_id
n = 0
for p, sources in prod_src.items():
    for sid, spn, desc, uom, pack in sources:
        info_records.append({"part_no": p, "supplier_id": sid, "supplier_pn": spn})
        for i, q in enumerate(["Q1", "Q2"]):  # one PO lot per quarter: Jan and Apr
            n += 1
            pid = f"PO-4500{n:02d}-010"
            lot[(p, sid, q)] = pid
            price_unit = 100 if (p == "100-4471-02" and i == 1) else 1  # SAP trap: price is per 100
            production_spend.append({
                "po_line_id": pid, "part_no": p if rng.random() < 0.85 else "",  # ~85% carry the material number
                "supplier_id": sid, "supplier_name": SUP[sid][0], "supplier_pn": spn,
                "description": desc, "qty": rng.choice([500, 1000, 2000]) // pack, "uom": uom,
                "unit_price": round(std[p] * pack * price_unit * rng.uniform(0.97, 1.05), 2), "price_unit": price_unit,
                "po_date": f"2026-0{i * 3 + 1}-15", "plant": "P-IA1", "country": SUP[sid][1]})
            truth_links.append({"source_table": "production_spend", "source_id": pid, "part_no": p})
    # service team buys the same part from a distributor at a markup, with different wording
    n += 1
    sid2, desc = "S-090", sources[0][2]
    pid = f"PO-7700{n:02d}-010"
    service_spend.append({
        "po_line_id": pid, "part_no": p if rng.random() < 0.15 else "",  # mostly free-text buys
        "supplier_id": sid2, "supplier_name": SUP[sid2][0],
        "supplier_pn": f"QS-{rng.randint(10000, 99999)}", "description": desc.upper().replace(" X ", "X"),
        "qty": rng.choice([20, 40, 60]), "uom": "EA", "unit_price": round(std[p] * rng.uniform(1.6, 4.5), 2),
        "price_unit": 1, "po_date": "2026-05-02", "plant": "SVC-1", "country": "US",
        "channel": rng.choice(["spares", "warranty_repair"])})
    truth_links.append({"source_table": "service_spend", "source_id": pid, "part_no": p})

# build_supply: which supplier lot each product/month consumed (shares sum to 1)
SEAL, KEY, BLUE = "200-1180-01", "S-022", "S-023"
build_supply = []
for prod, items in bom_map.items():
    for m in months:
        q = "Q1" if m < "2026-04" else "Q2"
        for p, _ in items:
            if p == SEAL:
                if prod == "UV-600":
                    mix = {BLUE: 1.0} if q == "Q1" else {KEY: 0.5, BLUE: 0.5}
                else:
                    mix = {KEY: 1.0}
            else:
                mix = {prod_src[p][0][0]: 1.0}
            for sid, share in mix.items():
                build_supply.append({"product_id": prod, "build_month": m, "part_no": p, "supplier_id": sid,
                                     "po_line_id": lot[(p, sid, q)], "share": share})

SPIKE_SUPPLIER, SPIKE_FROM_PO, SPIKE_X = KEY, lot[(SEAL, KEY, "Q2")], 3.0
spike_share = {}  # (product, month) -> share of the seal kit coming from the affected lot
for r in build_supply:
    if r["part_no"] == SEAL and r["po_line_id"] == SPIKE_FROM_PO:
        spike_share[(r["product_id"], r["build_month"])] = r["share"]

# v4: supplier recovery terms. The truth lives here; the pipeline only sees the documents.
# supplier: (recovery_pct, labor_covered, labor_rate_cap, recovery_window_months, filing_deadline_days, doc style)
TERMS = {
    "S-011": (1.00, True, 95, 24, 60, "formal"), "S-022": (0.80, True, 90, 18, 45, "amended"),
    "S-023": (1.00, False, None, 24, 90, "table"), "S-031": (0.50, False, None, 12, 30, "formal"),
    "S-044": (1.00, True, 85, 24, 60, "table"), "S-052": (0.60, True, 75, 12, 30, "formal"),
    "S-063": (1.00, False, None, 18, 60, "table"), "S-070": (0.75, True, 90, 24, 45, "amended"),
    "S-081": (1.00, True, 100, 24, 90, "formal"),
}


def agreement_doc(sid):
    pct, labor, cap, window, filing, style = TERMS[sid]
    name, country = SUP[sid]
    cover = (f"parts and dealer labor, labor at the hours actually claimed and capped at USD {cap} per hour"
             if labor else "the parts only; dealer labor is excluded")
    if style == "table":
        return (f"PRAIRIE UTILITY VEHICLES · SUPPLIER WARRANTY TERMS\nVendor: {name} (vendor no. {sid}), {country}\n\n"
                f"| Term | Value |\n|---|---|\n| Warranty period | {window} months from end-unit build date |\n"
                f"| Recovery share | {pct:.0%} |\n| Labor reimbursed | {'yes, max $' + str(cap) + '/hr' if labor else 'no'} |\n"
                f"| Claim filing deadline | {filing} days after dealer claim is paid |\n"
                f"| Freight / handling | not recoverable |\n")
    body = (f"# Supplier Quality Agreement\nPrairie Utility Vehicles (\"Buyer\") and {name}, supplier no. {sid} "
            f"(\"Supplier\"), {country}. Effective 2025-01-01.\n\n## 4. Quality\n4.1 Supplier maintains IATF 16949 "
            f"certification and ships with a certificate of conformance per lot.\n\n## 7. Warranty\n"
            f"7.1 Supplier warrants each part for {window} months from the date of manufacture of the end unit "
            f"in which it is installed.\n")
    if style == "amended":
        return (body + f"7.2 For field failures attributable to Supplier's parts, Supplier reimburses 100% of {cover}.\n"
                f"7.3 Recovery claims are submitted within 90 days after Buyer pays the dealer claim.\n"
                f"7.4 Freight, handling and administrative fees are not recoverable.\n\n"
                f"## Amendment No. 1 (effective 2025-06-01)\nSections 7.2 and 7.3 are replaced as follows. "
                f"Supplier reimburses {pct:.0%} of {cover}. Recovery claims must be submitted within {filing} days "
                f"after Buyer pays the dealer claim; late claims are void. All other terms are unchanged.\n")
    return (body + f"7.2 For field failures attributable to Supplier's parts, Supplier reimburses {pct:.0%} of {cover}.\n"
            f"7.3 Recovery claims are submitted within {filing} days after Buyer pays the dealer claim.\n"
            f"7.4 Freight, handling and administrative fees are not recoverable.\n")


docs, truth_terms = {}, []
for sid in TERMS:
    pct, labor, cap, window, filing, _ = TERMS[sid]
    fname = "sqa_" + SUP[sid][0].lower().replace(" ", "-") + ".md"
    docs[fname] = agreement_doc(sid)
    truth_terms.append({"doc_file": fname, "supplier_id": sid, "recovery_pct": pct, "labor_covered": labor,
                        "labor_rate_cap": cap if cap else "", "recovery_window_months": window,
                        "filing_deadline_days": filing})
main_supplier = {}  # (product, month, part) -> supplier with the largest share (who a recovery claim goes to)
for r in build_supply:
    key = (r["product_id"], r["build_month"], r["part_no"])
    if r["share"] > main_supplier.get(key, (None, 0))[1]:
        main_supplier[key] = (r["supplier_id"], r["share"])

failure_codes = failure_code_rows(PROFILE)
texts = {
    "200-1180-01": ["hyd leak boom cyl, repl seal kit", "cust reports fluid under unit, cyl seals worn", "lift cyl weeping, resealed"],
    "500-7731-01": ["hyd hose chafed and lkg, repl hose", "burst hose at loader valve"],
    "100-4471-02": ["grinding noise rr axle, repl brg", "wheel brg play, replaced"],
    "400-2205-03": ["belt slipping under load, repl cvt belt", "drive belt glazed"],
    "600-3310-00": ["intermittent no start, ign sw replaced"],
    "800-1004-00": ["no start, no fuel pressure, repl pump"],
    "700-5520-02": ["frt brake squeal, pads replaced"],
    "300-0912-00": ["oil leak at fltr, fltr gskt torn"],
}
code_for = {"200-1180-01": "HYD-ELP", "500-7731-01": "HYD-ELP", "100-4471-02": "DRV-NOI", "400-2205-03": "DRV-VIB",
            "600-3310-00": "ELE-FTS", "800-1004-00": "ELE-FTS", "700-5520-02": "BRK-NOI", "300-0912-00": "ENG-ELP"}
BASE = 0.004  # claims per unit built per BOM line (sample-sized)

AS_OF = dt.date.fromisoformat(COMMON["data_as_of"])
claims, k, unreported = [], 0, 0
for b in builds:
    for p, q in bom_map[b["product_id"]]:
        mult = 1 + (SPIKE_X - 1) * spike_share.get((b["product_id"], b["build_month"]), 0) if p == SEAL else 1
        expected = b["units_built"] * BASE * mult * (1 if q <= 2 else 1.5)
        count = int(expected) + (1 if rng.random() < expected % 1 else 0)
        for _ in range(count):
            k += 1
            cid = f"WC-2026-{k:05d}"
            y, mo = b["build_month"].split("-")
            fail_mo = min(int(mo) + rng.randint(1, 4), 10)
            r = rng.random()
            causal = p if r < 0.3 else ("" if r < 0.9 else rng.choice(list(cat)))  # 60% blank, 10% wrong
            labor = round(rng.uniform(0.8, 3.5), 1)
            # same draw order as v3 (serial, date, text, parts cost, dealer) so v3 values don't change
            serial = f"{b['product_id'].replace('-', '')}-{y[2:]}-{mo}-{rng.randint(1, 999):05d}"
            failure_date = f"{y}-{fail_mo:02d}-{rng.randint(1, 28):02d}"
            text = rng.choice(texts[p])
            parts_cost, labor_cost = round(std[p] * rng.uniform(2, 4), 2), round(labor * 85, 2)
            dealer = f"D-{rng.randint(100, 140)}"
            # v4: reporting lag. A claim reaches us 2-40 days after the failure; later than data_as_of = not in the data yet.
            claim_date = dt.date.fromisoformat(failure_date) + dt.timedelta(days=rng4.randint(2, 40))
            paid = claim_date + dt.timedelta(days=rng4.randint(7, 45))
            other_cost = round(rng4.uniform(8, 40), 2)
            status, recovered = "none", 0.0
            if paid <= AS_OF:
                sid, _ = main_supplier[(b["product_id"], b["build_month"], p)]
                pct, labor_ok, cap, window, _, _ = TERMS[sid]
                in_window = (fail_mo - int(mo)) + 12 * (int(failure_date[:4]) - int(y)) <= window
                roll = rng4.random()
                if in_window and roll < 0.15:
                    status = "recovered"
                    recovered = round(pct * (parts_cost + (min(labor_cost, labor * cap) if labor_ok else 0)), 2)
                elif in_window and roll < 0.30:
                    status = "submitted"
            if claim_date > AS_OF:
                unreported += 1
                continue
            claims.append({
                "claim_id": cid, "product_id": b["product_id"],
                "serial_no": serial, "build_month": b["build_month"], "failure_date": failure_date,
                "claim_date": claim_date.isoformat(), "paid_date": paid.isoformat() if paid <= AS_OF else "",
                "failure_code": code_for[p], "claim_text": text, "causal_part_no": causal,
                "labor_hrs": labor, "parts_cost": parts_cost, "labor_cost": labor_cost, "other_cost": other_cost,
                "dealer_id": dealer, "recovery_status": status, "recovered_usd": recovered})
            truth_links.append({"source_table": "warranty_claims", "source_id": cid, "part_no": p})

info = {**dataset_info(PROFILE), "company_id": "sample", "first_build_month": months[0], "last_build_month": months[-1]}
write("products", products)
write("part_master", part_master)
write("bom", bom)
write("builds", builds)
write("production_spend", production_spend)
write("service_spend", service_spend)
write("info_records", info_records)
write("build_supply", build_supply)
write("abbreviations", abbreviations_rows(PROFILE))
write("failure_codes", failure_codes)
write("warranty_claims", claims)
write("dataset_info", [{"key": key, "value": v} for key, v in info.items()])
write("truth_links", truth_links)
write("truth_terms", truth_terms)
for fname, text in docs.items():
    write_doc(fname, text)
write("truth_spikes", [{"part_no": SEAL, "supplier_id": SPIKE_SUPPLIER, "start_build_month": "2026-04",
                        "from_po_line_id": SPIKE_FROM_PO, "multiplier": SPIKE_X}])
print(f"sample written to {OUT}: {len(claims)} claims ({unreported} not reported by data_as_of), {len(docs)} agreements, {len(production_spend)} production POs, "
      f"{len(service_spend)} service POs, {len(build_supply)} build_supply rows")
