"""Write the SMALL hand-shaped sample dataset to data/sample/.

This is NOT the real generator (that's afterlife/generate.py, Role A).
It exists so Role B can build alerts / cost / brief / app from hour 0.
Fictional company: Prairie Utility Vehicles. Everything follows docs/build/data-contract.md.

Run: python scripts/make_sample.py
"""
import csv
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "sample"
rng = random.Random(42)


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


products = [
    {"product_id": "UV-400", "product_name": "Utility vehicle 400", "family": "utility_vehicle"},
    {"product_id": "UV-600", "product_name": "Utility vehicle 600", "family": "utility_vehicle"},
    {"product_id": "TR-250", "product_name": "Compact tractor 250", "family": "tractor"},
]

# part_no, ERP description, category, std_cost
parts = [
    ("100-4471-02", "BRG,BALL,6204-2RS,20MM", "bearing", 4.10),
    ("200-1180-01", "SEAL KIT,HYD CYL,40MM BORE", "seal", 11.50),   # <- planted spike part
    ("300-0912-00", "FLTR,OIL,SPIN-ON,M20X1.5", "filter", 3.20),
    ("400-2205-03", "BELT,CVT,DRIVE,32MM", "belt", 27.00),
    ("500-7731-01", "HOSE ASSY,HYD,3/8,24IN", "hose", 18.40),
    ("600-3310-00", "SWITCH,IGN,KEYED,12V", "electrical", 9.75),
    ("700-5520-02", "PAD SET,BRAKE,FRT", "brake", 14.20),
    ("800-1004-00", "PUMP,FUEL,ELEC,12V", "fuel", 46.00),
]
part_master = [{"part_no": p, "description": d, "category": c, "std_cost": s} for p, d, c, s in parts]

# which parts go in which product (seal kit + bearing + filter are shared by all 3)
bom_map = {
    "UV-400": [("100-4471-02", 4), ("200-1180-01", 2), ("300-0912-00", 1), ("400-2205-03", 1), ("600-3310-00", 1), ("700-5520-02", 2), ("800-1004-00", 1)],
    "UV-600": [("100-4471-02", 4), ("200-1180-01", 2), ("300-0912-00", 1), ("400-2205-03", 1), ("500-7731-01", 2), ("700-5520-02", 2), ("800-1004-00", 1)],
    "TR-250": [("100-4471-02", 6), ("200-1180-01", 4), ("300-0912-00", 1), ("500-7731-01", 4), ("600-3310-00", 1)],
}
positions = {"bearing": "axle", "seal": "hydraulic_cylinder", "filter": "engine", "belt": "drivetrain",
             "hose": "hydraulic_lines", "electrical": "dash", "brake": "front_brakes", "fuel": "fuel_system"}
cat = {p: c for p, _, c, _ in parts}
bom = [{"product_id": prod, "part_no": p, "qty_per": q, "position": positions[cat[p]]}
       for prod, items in bom_map.items() for p, q in items]

months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
builds = [{"product_id": p["product_id"], "build_month": m, "units_built": rng.randint(180, 260)}
          for p in products for m in months]

# suppliers: (id, name, country)
SUP = {"S-011": ("Great Lakes Bearing Co", "US"), "S-022": ("Keystone Seal Works", "MX"),
       "S-031": ("Northfield Filtration", "US"), "S-044": ("Ridgeway Drive Systems", "US"),
       "S-052": ("Delta Fluid Power", "CN"), "S-063": ("Summit Electric Parts", "CN"),
       "S-070": ("Midland Brake Supply", "US"), "S-081": ("Harbor Fuel Components", "KR"),
       "S-090": ("QuickServe Parts Distribution", "US")}  # S-090 = service-team distributor
# part -> (production supplier, supplier_pn, supplier wording, uom, pack size)
prod_src = {
    "100-4471-02": ("S-011", "6204-2RSH", "Deep groove ball bearing 20x47x14 sealed", "EA", 1),
    "200-1180-01": ("S-022", "KSW-HC40-K", "Hydraulic cylinder seal kit 40 mm bore", "EA", 1),
    "300-0912-00": ("S-031", "NF-M20-OS", "Spin-on oil filter M20 x 1.5", "BX10", 10),
    "400-2205-03": ("S-044", "RDS-CVT32", "CVT drive belt 32mm", "EA", 1),
    "500-7731-01": ("S-052", "DFP-3824", "Hydraulic hose assembly 3/8 in x 24 in", "EA", 1),
    "600-3310-00": ("S-063", "SEP-IGN12K", "Keyed ignition switch 12V", "EA", 1),
    "700-5520-02": ("S-070", "MBS-FP220", "Front brake pad set", "EA", 1),
    "800-1004-00": ("S-081", "HFC-EFP12", "Electric fuel pump 12 V", "EA", 1),
}
production_spend, service_spend, truth_links = [], [], []
n = 0
for p, (sid, spn, desc, uom, pack) in prod_src.items():
    std = next(x["std_cost"] for x in part_master if x["part_no"] == p)
    for i in range(2):  # two POs per part
        n += 1
        pid = f"PO-4500{n:02d}-010"
        production_spend.append({
            "po_line_id": pid, "supplier_id": sid, "supplier_name": SUP[sid][0], "supplier_pn": spn,
            "description": desc, "qty": rng.choice([500, 1000, 2000]) // pack, "uom": uom,
            "unit_price": round(std * pack * rng.uniform(0.97, 1.05), 2), "po_date": f"2026-0{i * 3 + 1}-15",
            "plant": "P-IA1", "country": SUP[sid][1]})
        truth_links.append({"source_table": "production_spend", "source_id": pid, "part_no": p})
    # service-team buys the same part from a distributor at a markup, with different wording
    n += 1
    sid2 = "S-090"
    pid = f"PO-7700{n:02d}-010"
    markup = rng.uniform(1.6, 4.5)
    service_spend.append({
        "po_line_id": pid, "supplier_id": sid2, "supplier_name": SUP[sid2][0],
        "supplier_pn": f"QS-{rng.randint(10000, 99999)}", "description": desc.upper().replace(" X ", "X"),
        "qty": rng.choice([20, 40, 60]), "uom": "EA", "unit_price": round(std * markup, 2),
        "po_date": "2026-05-02", "plant": "SVC-1", "country": "US",
        "channel": rng.choice(["spares", "warranty_repair"])})
    truth_links.append({"source_table": "service_spend", "source_id": pid, "part_no": p})

failure_codes = [
    {"failure_code": "H-21", "system": "hydraulic", "description": "Hydraulic leak at cylinder", "likely_categories": "seal;hose"},
    {"failure_code": "D-10", "system": "drivetrain", "description": "Noise / vibration in driveline", "likely_categories": "bearing;belt"},
    {"failure_code": "E-05", "system": "electrical", "description": "No start / intermittent power", "likely_categories": "electrical;fuel"},
    {"failure_code": "B-02", "system": "brakes", "description": "Brake noise / reduced braking", "likely_categories": "brake"},
    {"failure_code": "N-01", "system": "engine", "description": "Oil leak / low oil pressure", "likely_categories": "filter"},
]
texts = {
    "200-1180-01": ["hyd leak boom cyl, repl seal kit", "cust reports fluid under unit, cyl seals worn", "lift cyl weeping, resealed"],
    "500-7731-01": ["hyd hose chafed and leaking, repl hose", "burst hose at loader valve"],
    "100-4471-02": ["grinding noise rear axle, repl brg", "wheel brg play, replaced"],
    "400-2205-03": ["belt slipping under load, repl cvt belt", "drive belt glazed"],
    "600-3310-00": ["intermittent no start, ign switch replaced"],
    "800-1004-00": ["no start, no fuel pressure, repl pump"],
    "700-5520-02": ["front brake squeal, pads replaced"],
    "300-0912-00": ["oil leak at filter, filter gasket torn"],
}
code_for = {"200-1180-01": "H-21", "500-7731-01": "H-21", "100-4471-02": "D-10", "400-2205-03": "D-10",
            "600-3310-00": "E-05", "800-1004-00": "E-05", "700-5520-02": "B-02", "300-0912-00": "N-01"}
base_rate = {p: 0.004 for p in cat}  # claims per unit built per BOM occurrence (sample-sized)
SPIKE_PART, SPIKE_FROM, SPIKE_X = "200-1180-01", "2026-04", 3.0

claims, k = [], 0
for b in builds:
    for p, q in bom_map[b["product_id"]]:
        rate = base_rate[p] * (SPIKE_X if p == SPIKE_PART and b["build_month"] >= SPIKE_FROM else 1)
        expected = b["units_built"] * rate * (1 if q <= 2 else 1.5)
        count = int(expected) + (1 if rng.random() < expected % 1 else 0)
        for _ in range(count):
            k += 1
            cid = f"WC-2026-{k:05d}"
            y, mo = b["build_month"].split("-")
            fail_mo = min(int(mo) + rng.randint(1, 4), 12)
            r = rng.random()
            causal = p if r < 0.3 else ("" if r < 0.9 else rng.choice(list(cat)))  # 60% blank, 10% wrong
            labor = round(rng.uniform(0.8, 3.5), 1)
            claims.append({
                "claim_id": cid, "product_id": b["product_id"],
                "serial_no": f"{b['product_id'].replace('-', '')}-{y[2:]}-{mo}-{rng.randint(1, 999):05d}",
                "build_month": b["build_month"], "failure_date": f"{y}-{fail_mo:02d}-{rng.randint(1, 28):02d}",
                "failure_code": code_for[p], "claim_text": rng.choice(texts[p]), "causal_part_no": causal,
                "labor_hrs": labor, "parts_cost": round(next(x["std_cost"] for x in part_master if x["part_no"] == p) * rng.uniform(2, 4), 2),
                "labor_cost": round(labor * 85, 2), "dealer_id": f"D-{rng.randint(100, 140)}",
                "recovery_status": "none"})
            truth_links.append({"source_table": "warranty_claims", "source_id": cid, "part_no": p})

write("products", products)
write("part_master", part_master)
write("bom", bom)
write("builds", builds)
write("production_spend", production_spend)
write("service_spend", service_spend)
write("failure_codes", failure_codes)
write("warranty_claims", claims)
write("truth_links", truth_links)
write("truth_spikes", [{"part_no": SPIKE_PART, "supplier_id": "S-022", "start_build_month": SPIKE_FROM, "multiplier": SPIKE_X}])
print(f"sample written to {OUT}: {len(claims)} claims, {len(production_spend)} production POs, {len(service_spend)} service POs")
