"""[SPEND thread · Asher] Products, BOMs, builds, production + service purchase lines.

generate(seed, profile) -> {products (with avg_selling_price), part_master, bom, builds, production_spend, service_spend,
                            info_records, build_supply, truth_links, _spike_plan}
dataset_info, abbreviations and failure_codes are written by generate.py from the profile, and so is the
SAP formatting for extract_format='sap'. Keys starting with "_" are NOT written: `_spike_plan` tells the
claims generator (🛠) which part / supplier / lot to plant the spike on.

What makes the data realistic (and what the matchers have to cope with):
  - internal part descriptions in the company's style (ERP shorthand or plain words); suppliers and the
    service distributor describe the same part in their own words and with their own part numbers
  - spec codes (6204, M20X1.5, 40MM, 5 TON) survive in most wordings, so spec-code matching works
  - units of measure vary (EA / BX10 / BX100), and some prices are per 100 (SAP price unit)
  - part_no is filled on most production lines, rarely on service lines (free-text "text items")
  - dual-sourced parts with a supplier MIX that varies by product and quarter (build_supply), so a
    spike on one supplier's lot can be told apart from the other supplier
  - Ironridge: an acquired plant on a legacy system (no part numbers, own suppliers, plain wording,
    higher prices), and the whole company ships as a raw SAP extract (handled in generate.py)
"""
import math
import random

import pandas as pd

from afterlife import agreements
from afterlife.adapters import sap
from afterlife.profiles import COMMON
from afterlife.taxonomy import CATEGORIES

# ---------------------------------------------------------------------------------------------------------
# Part catalog: category -> list of (erp_template, plain_template, attribute options, cost range, packs)
# Templates use {attrs}. ERP shorthand uses the abbreviations in profiles._MOBILE_ABBR / _HVAC_ABBR.
# packs: list of (uom, pack_size) with weights; most parts are EA.
# ---------------------------------------------------------------------------------------------------------
BEARING_BORE = {"6202": 15, "6203": 17, "6204": 20, "6205": 25, "6206": 30, "6305": 25, "6308": 40}
CATALOG = {
    "bearing": [("BRG,BALL,{s}-2RS,{b}MM", "Deep groove ball bearing {s} sealed {b} mm bore",
                 lambda r: (lambda s: {"s": s, "b": BEARING_BORE[s]})(r.choice(list(BEARING_BORE))), (3, 18), [("EA", 1)]),
                ("BRG,TAPER ROLLER,{s}", "Tapered roller bearing {s}",
                 lambda r: {"s": r.choice(["30205", "30206", "32207", "30308"])}, (8, 35), [("EA", 1)])],
    "seal": [("SEAL KIT,HYD CYL,{b}MM BORE", "Hydraulic cylinder seal kit {b} mm bore",
              lambda r: {"b": r.choice([30, 40, 50, 63, 80])}, (8, 32), [("EA", 1)]),
             ("SEAL,OIL,{d}X{o}X{w}", "Oil seal {d} x {o} x {w} mm",
              lambda r: {"d": r.choice([25, 30, 35, 40]), "o": r.choice([47, 52, 62]), "w": r.choice([7, 8, 10])}, (1, 6), [("EA", 1), ("BX10", 10)])],
    "gasket": [("GSKT,{p}", "{pl} gasket", lambda r: r.choice([{"p": "VALVE COVER", "pl": "Valve cover"}, {"p": "OIL PAN", "pl": "Oil pan"},
                                                              {"p": "EXHAUST MANIFOLD", "pl": "Exhaust manifold"}]), (2, 15), [("EA", 1), ("BX10", 10)])],
    "hose": [("HOSE ASSY,HYD,{d},{l}IN", "Hydraulic hose assembly {d} in x {l} in",
              lambda r: {"d": r.choice(["1/4", "3/8", "1/2", "3/4"]), "l": r.choice([12, 18, 24, 36, 48, 60])}, (12, 48), [("EA", 1)])],
    "fitting": [("FTG,{t},{th}", "{tp} fitting {th}", lambda r: {**r.choice([{"t": "ELBOW 90", "tp": "90-degree elbow"}, {"t": "TEE", "tp": "Tee"},
                                                                          {"t": "STRAIGHT", "tp": "Straight"}]),
                                                             "th": r.choice(["M14X1.5", "M18X1.5", "M22X1.5", "7/16-20 JIC"])}, (2, 12), [("EA", 1), ("BX10", 10)])],
    "hydraulic_component": [("CYL,HYD,{b}X{st}", "Hydraulic cylinder {b} mm bore x {st} mm stroke",
                             lambda r: {"b": r.choice([40, 50, 63, 80]), "st": r.choice([200, 300, 400, 600])}, (120, 480), [("EA", 1)]),
                            ("VALVE,CTRL,HYD,{n} SPOOL", "{n}-spool hydraulic control valve", lambda r: {"n": r.choice([2, 3, 4])}, (180, 600), [("EA", 1)]),
                            ("PUMP,HYD,GEAR,{cc}CC", "Hydraulic gear pump {cc} cc", lambda r: {"cc": r.choice([8, 11, 16, 22])}, (150, 520), [("EA", 1)])],
    "filter": [("FLTR,OIL,SPIN-ON,{th}", "Spin-on oil filter {th}", lambda r: {"th": r.choice(["M20X1.5", "3/4-16 UNF", "M22X1.5"])}, (3, 12), [("EA", 1), ("BX10", 10)]),
               ("FLTR,HYD,RETURN,{m}MIC", "Hydraulic return filter {m} micron", lambda r: {"m": r.choice([10, 25])}, (12, 40), [("EA", 1)]),
               ("FLTR,AIR,PANEL,{w}X{h}", "Air filter panel {w} x {h} in", lambda r: {"w": r.choice([16, 20, 24]), "h": r.choice([20, 25])}, (6, 22), [("EA", 1), ("BX10", 10)])],
    "belt": [("BELT,CVT,DRIVE,{w}MM", "CVT drive belt {w} mm", lambda r: {"w": r.choice([28, 30, 32, 35])}, (25, 70), [("EA", 1)]),
             ("BELT,V,{c}", "V-belt {c}", lambda r: {"c": r.choice(["A42", "B55", "AX38", "BX60"])}, (8, 25), [("EA", 1)])],
    "gear": [("GEAR,SPUR,{t}T,M{m}", "Spur gear {t} teeth module {m}", lambda r: {"t": r.choice([18, 24, 32, 40]), "m": r.choice([2, 2.5, 3])}, (15, 120), [("EA", 1)]),
             ("GEAR,PINION,{t}T", "Pinion gear {t} teeth", lambda r: {"t": r.choice([11, 13, 15])}, (20, 90), [("EA", 1)])],
    "wheel_tire": [("TIRE,{sz}", "Tire {sz}", lambda r: {"sz": r.choice(["26X9-12", "10-16.5", "23X10.50-12", "12-16.5"])}, (60, 220), [("EA", 1)]),
                   ("WHEEL,STL,{sz}", "Steel wheel {sz}", lambda r: {"sz": r.choice(["12X7", "16.5X8.25", "14X7"])}, (40, 140), [("EA", 1)])],
    "brake": [("PAD SET,BRAKE,{p}", "{pp} brake pad set", lambda r: r.choice([{"p": "FRT", "pp": "Front"}, {"p": "RR", "pp": "Rear"}]), (10, 40), [("EA", 1)]),
              ("ROTOR,BRAKE,{d}MM", "Brake rotor {d} mm", lambda r: {"d": r.choice([200, 220, 240])}, (25, 80), [("EA", 1)])],
    "cooling": [("RADIATOR,{n}ROW", "Radiator {n}-row core", lambda r: {"n": r.choice([2, 3])}, (90, 320), [("EA", 1)]),
                ("THERMOSTAT,{t}C", "Thermostat {t} C", lambda r: {"t": r.choice([82, 88, 92])}, (6, 20), [("EA", 1)])],
    "fuel": [("PUMP,FUEL,ELEC,12V", "Electric fuel pump 12 V", lambda r: {}, (35, 110), [("EA", 1)]),
             ("INJECTOR,FUEL,{cc}CC", "Fuel injector {cc} cc", lambda r: {"cc": r.choice([210, 250, 310])}, (25, 90), [("EA", 1)])],
    "electrical": [("SW,IGN,KEYED,12V", "Keyed ignition switch 12 V", lambda r: {}, (6, 20), [("EA", 1)]),
                   ("RELAY,{a}A,12V", "Relay {a} A 12 V", lambda r: {"a": r.choice([30, 40, 70])}, (3, 12), [("EA", 1), ("BX10", 10)]),
                   ("CONTACTOR,{a}A,{v}V", "Contactor {a} A {v} V", lambda r: {"a": r.choice([30, 40, 50]), "v": r.choice([24, 240])}, (18, 60), [("EA", 1)]),
                   ("CAP,RUN,{uf}UF,{v}V", "Run capacitor {uf} uF {v} V", lambda r: {"uf": r.choice([35, 45, 55]), "v": r.choice([370, 440])}, (8, 30), [("EA", 1)])],
    "harness": [("HRNS,{a},{n}PIN", "{ap} wiring harness {n}-pin", lambda r: {**r.choice([{"a": "MAIN", "ap": "Main"}, {"a": "DASH", "ap": "Dash"},
                                                                                       {"a": "CTRL", "ap": "Control"}]), "n": r.choice([8, 12, 24])}, (25, 160), [("EA", 1)])],
    "sensor": [("SENS,TEMP,{t}", "Temperature sensor {t}", lambda r: {"t": r.choice(["NTC 10K", "PT100", "NTC 3K"])}, (8, 45), [("EA", 1)]),
               ("SENS,PRESS,{b}BAR", "Pressure sensor 0-{b} bar", lambda r: {"b": r.choice([10, 40, 250])}, (25, 90), [("EA", 1)])],
    "battery": [("BATTERY,12V,{ah}AH", "Battery 12 V {ah} Ah", lambda r: {"ah": r.choice([30, 55, 75, 100])}, (60, 190), [("EA", 1)])],
    "lighting": [("LAMP,LED,WORK,{w}W", "LED work lamp {w} W", lambda r: {"w": r.choice([18, 27, 40])}, (15, 70), [("EA", 1)])],
    "fastener": [("BOLT,HEX,M{d}X{l},{g}", "Hex bolt M{d} x {l} class {g}", lambda r: {"d": r.choice([8, 10, 12, 16]), "l": r.choice([25, 40, 60]), "g": r.choice(["8.8", "10.9"])}, (0.08, 0.9), [("BX100", 100)]),
                 ("NUT,LOCK,M{d}", "Lock nut M{d}", lambda r: {"d": r.choice([8, 10, 12, 16])}, (0.04, 0.4), [("BX100", 100)])],
    "structural": [("BRKT,{a},STL", "{ap} bracket, steel", lambda r: r.choice([{"a": "MTG", "ap": "Mounting"}, {"a": "ENG MTG", "ap": "Engine mounting"}, {"a": "CAB", "ap": "Cab"}]), (12, 90), [("EA", 1)]),
                   ("PANEL,{a},STL", "{ap} panel, steel", lambda r: r.choice([{"a": "SIDE", "ap": "Side"}, {"a": "ACCESS", "ap": "Access"}, {"a": "BASE", "ap": "Base"}]), (30, 260), [("EA", 1)])],
    "plastic": [("COVER,{a},PLASTIC", "{ap} cover, plastic", lambda r: r.choice([{"a": "FAN", "ap": "Fan"}, {"a": "DASH", "ap": "Dash"}, {"a": "SIDE", "ap": "Side"}]), (6, 60), [("EA", 1)])],
    "compressor": [("CMPR,SCROLL,{t}TON,{v}V", "Scroll compressor {t} ton {v} V", lambda r: {"t": r.choice([3, 5, 7.5, 10]), "v": r.choice([208, 460])}, (450, 1500), [("EA", 1)]),
                   ("CMPR,RECIP,{t}TON,{v}V", "Reciprocating compressor {t} ton {v} V", lambda r: {"t": r.choice([5, 10, 15]), "v": r.choice([208, 460])}, (600, 1700), [("EA", 1)])],
    "refrigerant_component": [("TXV,{t}TON,R410A", "Thermal expansion valve {t} ton R-410A", lambda r: {"t": r.choice([3, 5, 10])}, (35, 120), [("EA", 1)]),
                              ("COND COIL,{n}ROW,{t}TON", "Condenser coil {n}-row {t} ton", lambda r: {"n": r.choice([1, 2]), "t": r.choice([5, 10, 15])}, (180, 620), [("EA", 1)]),
                              ("DRIER,FLTR,{d}IN", "Filter drier {d} in", lambda r: {"d": r.choice(["3/8", "1/2", "5/8"])}, (12, 40), [("EA", 1)])],
    "motor": [("MTR,FAN,{hp}HP,{v}V", "Fan motor {hp} HP {v} V", lambda r: {"hp": r.choice([0.5, 0.75, 1]), "v": r.choice([208, 460])}, (90, 320), [("EA", 1)]),
              ("MTR,BLOWER,{hp}HP", "Blower motor {hp} HP", lambda r: {"hp": r.choice([1, 2, 3])}, (150, 480), [("EA", 1)])],
}
assert set(CATALOG) == set(CATEGORIES), "every taxonomy category needs a catalog entry"

# Real part lists are full of near-duplicates that differ only by a suffix (material, duty, hand, revision).
# When a catalog combination is already taken, the part becomes a variant: harder (and realistic) matching.
VARIANTS = [("HD", "heavy duty"), ("SS", "stainless steel"), ("ZP", "zinc plated"), ("VITON", "Viton"),
            ("HT", "high temp"), ("LH", "left hand"), ("RH", "right hand"), ("REV B", "rev B"), ("REV C", "rev C"),
            ("LONG", "long"), ("SHORT", "short"), ("XL", "extra large"), ("LOW PROFILE", "low profile")]

SUPPLIER_PREFIX = ["Great Lakes", "Keystone", "Bluewater", "Northfield", "Ridgeway", "Delta", "Summit", "Midland",
                   "Harbor", "Cedar", "Ironwood", "Silverline", "Pinecrest", "Redstone", "Lakeshore", "Granite",
                   "Westfield", "Oakmont", "Crescent", "Highland", "Riverbend", "Stonebridge", "Clearwater", "Eastgate"]
SUPPLIER_SUFFIX = {"bearing": "Bearing Co", "seal": "Seal Works", "gasket": "Gasket Co", "hose": "Hose & Fitting",
                   "fitting": "Fittings", "hydraulic_component": "Fluid Power", "filter": "Filtration", "belt": "Drive Systems",
                   "gear": "Gear Works", "wheel_tire": "Tire & Wheel", "brake": "Brake Supply", "cooling": "Thermal",
                   "fuel": "Fuel Systems", "electrical": "Electric", "harness": "Harness Co", "sensor": "Sensors",
                   "battery": "Battery", "lighting": "Lighting", "fastener": "Fasteners", "structural": "Fabrication",
                   "plastic": "Plastics", "compressor": "Compressors", "refrigerant_component": "Coil Co", "motor": "Motors"}
COUNTRIES = (["US"] * 5) + ["MX", "MX", "CN", "CN", "KR", "DE", "IN"]
QTY_PER = {"fastener": (8, 40), "bearing": (2, 8), "seal": (1, 4), "hose": (2, 6), "fitting": (4, 12),
           "wheel_tire": (4, 4), "brake": (2, 4), "gasket": (1, 3)}


def _months(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _quarter(month: str) -> str:
    y, m = month.split("-")
    return f"{y}-Q{(int(m) - 1) // 3 + 1}"


def _quarter_start(q: str) -> str:
    y, n = q.split("-Q")
    return f"{y}-{(int(n) - 1) * 3 + 1:02d}"


def _typo(text: str, rng: random.Random, rate: float) -> str:
    if rng.random() >= rate or len(text) < 6:
        return text
    i = rng.randrange(1, len(text) - 2)
    return text[:i] + text[i + 1] + text[i] + text[i + 2:]   # swap two letters


def _abbreviate(text: str, abbr: dict[str, str]) -> str:
    """Distributor-style wording: uppercase, single-word expansions replaced by the company's shorthand."""
    inv = {e: a for a, e in abbr.items() if " " not in e}
    return " ".join(inv.get(w, w) for w in text.upper().replace(",", " ").split())


def _supplier_wording(plain: str, rng: random.Random) -> str:
    """A supplier's own catalog wording of the same part: reordered / lightly reworded, spec kept."""
    words = plain.split()
    if len(words) > 3 and rng.random() < 0.5:
        words = words[-2:] + words[:-2]          # "6204 sealed Deep groove ball bearing ..."
    text = " ".join(words)
    for a, b in [(" mm", "mm"), (" in", "in"), ("Hydraulic", "Hyd."), (" x ", "x")]:
        if rng.random() < 0.3:
            text = text.replace(a, b)
    return text


def generate(seed: int, profile: dict) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    sapfmt = profile["extract_format"] == "sap"
    months = _months(COMMON["first_build_month"], COMMON["last_build_month"])
    quarters = sorted({_quarter(m) for m in months})
    abbr = profile["abbreviations"]
    typo = profile.get("typo_rate", 0.05) / 2

    # ---- products + builds -----------------------------------------------------------------------------
    products = [{"product_id": pid, "product_name": name, "family": fam} for pid, name, fam, _ in profile["products"]]
    pids = [p["product_id"] for p in products]
    builds = []
    for pid, _, _, base in profile["products"]:
        phase = rng.uniform(0, 2 * math.pi)
        for i, m in enumerate(months):
            season = 1 + 0.15 * math.sin(2 * math.pi * i / 12 + phase)
            builds.append({"product_id": pid, "build_month": m, "units_built": max(20, int(base * season * rng.uniform(0.9, 1.1)))})

    # ---- parts -----------------------------------------------------------------------------------------
    cats = [c for c in CATEGORIES if c not in profile.get("exclude_categories", [])]
    weights = [profile.get("category_weights", {}).get(c, 1.0) for c in cats]
    part_master, seen_desc = [], set()
    pn_n = rng.randint(1000, 4000)
    attempts = 0
    while len(part_master) < profile["n_parts"]:
        attempts += 1
        if attempts > profile["n_parts"] * 200:
            raise RuntimeError(f"{profile['company_id']}: could not make {profile['n_parts']} distinct parts; "
                               f"add catalog entries or VARIANTS")
        cat = rng.choices(cats, weights)[0]
        erp_t, plain_t, attrs_fn, (lo, hi), packs = rng.choice(CATALOG[cat])
        attrs = attrs_fn(rng)
        erp, plain = erp_t.format(**attrs), plain_t.format(**attrs)
        if erp in seen_desc:
            v_erp, v_plain = rng.choice(VARIANTS)
            erp, plain = f"{erp},{v_erp}", f"{plain}, {v_plain}"
            if erp in seen_desc:
                continue
        seen_desc.add(erp)
        pn_n += rng.randint(1, 37)
        pn = profile["pn_format"].format(a=100 + pn_n // 10000 * 100 + cats.index(cat), b=pn_n % 10000, c=rng.randint(0, 9),
                                         n=pn_n, rev=rng.choice("ABC"))
        uom, pack = rng.choice(packs)
        part_master.append({"part_no": pn, "description": erp if profile["desc_style"] == "erp_shorthand" else plain,
                            "category": cat, "std_cost": round(rng.uniform(lo, hi), 2),
                            "_plain": plain, "_uom": uom, "_pack": pack})

    # ---- BOMs: shared parts appear in 2+ products ------------------------------------------------------
    usage: dict[str, list[str]] = {}
    for p in part_master:
        if rng.random() < profile["shared_part_share"]:
            usage[p["part_no"]] = rng.sample(pids, rng.randint(2, len(pids)))
        else:
            usage[p["part_no"]] = [rng.choice(pids)]

    # spike part: a SHARED, dual-sourced part in the spike category, used by as many products as possible
    spike = profile.get("spike")
    spike_part = None
    if spike:
        cands = [p for p in part_master if p["category"] == spike["category"]]
        if not cands:
            raise ValueError(f"profile {profile['company_id']}: no parts in spike category {spike['category']}")
        spike_part = max(cands, key=lambda p: len(usage[p["part_no"]]))["part_no"]
        usage[spike_part] = list(pids)   # every product uses it: the cross-product story
    bom = []
    for p in part_master:
        lo, hi = QTY_PER.get(p["category"], (1, 2))
        for pid in usage[p["part_no"]]:
            bom.append({"product_id": pid, "part_no": p["part_no"], "qty_per": rng.randint(lo, hi),
                        "position": p["category"]})

    # avg_selling_price (21a / contract v4): average net selling price per unit = build cost (sum of
    # qty_per x std_cost) x markup, so warranty as a % of revenue can be compared with the SEC peers in profiles.py
    std = {p["part_no"]: p["std_cost"] for p in part_master}
    mk_lo, mk_hi = profile.get("price_markup", (1.45, 1.75))
    for prod in products:
        build_cost = sum(r["qty_per"] * std[r["part_no"]] for r in bom if r["product_id"] == prod["product_id"])
        prod["avg_selling_price"] = round(build_cost * rng.uniform(mk_lo, mk_hi), -1)

    # ---- suppliers: a pool per category, numeric LIFNR-style ids for SAP companies --------------------
    n_sup = 0
    prefixes = rng.sample(SUPPLIER_PREFIX, len(SUPPLIER_PREFIX))

    def new_supplier(cat: str, tag: str = "") -> dict:
        nonlocal n_sup
        n_sup += 1
        sid = str(100000 + n_sup * 7) if sapfmt else f"S-{n_sup:03d}"
        name = f"{prefixes[n_sup % len(prefixes)]} {SUPPLIER_SUFFIX[cat]}{tag}"
        return {"supplier_id": sid, "supplier_name": name, "country": rng.choice(COUNTRIES)}

    pool = {c: [new_supplier(c) for _ in range(rng.randint(1, 3))] for c in cats}
    sources: dict[str, list[dict]] = {}
    for p in part_master:
        dual = p["part_no"] == spike_part or rng.random() < profile["dual_source_share"]
        cat_pool = pool[p["category"]]
        while dual and len(cat_pool) < 2:
            cat_pool.append(new_supplier(p["category"]))
        sources[p["part_no"]] = rng.sample(cat_pool, 2 if dual else 1)

    # ---- production purchase lines: one lot per (part, supplier, quarter) ------------------------------
    seq = {"prod": 0, "acq": 0, "svc": 0}
    bases = {"prod": 4500000000, "acq": 4600000000, "svc": 4700000000}

    def new_po(kind: str) -> str:
        seq[kind] += 1
        n = bases[kind] + seq[kind] * 10
        return sap.canonical_po_id(pd.Series([f"{n}-10"]))[0] if sapfmt else f"PO-{n}-010"

    production_spend, service_spend, info_records, truth_links = [], [], [], []
    lot: dict[tuple[str, str, str], str] = {}
    per_month_units = {(b["product_id"], b["build_month"]): b["units_built"] for b in builds}
    for p in part_master:
        pn = p["part_no"]
        q_units = {}
        for r in (x for x in bom if x["part_no"] == pn):
            for m in months:
                q_units[_quarter(m)] = q_units.get(_quarter(m), 0) + r["qty_per"] * per_month_units[(r["product_id"], m)]
        for k, s in enumerate(sources[pn]):
            spn = f"{''.join(w[0] for w in s['supplier_name'].split()[:2]).upper()}-{rng.randint(1000, 99999)}"
            info_records.append({"part_no": pn, "supplier_id": s["supplier_id"], "supplier_pn": spn})
            level = 1.0 if k == 0 else rng.uniform(0.92, 1.12)        # second source priced differently
            # Under contract, a PO pays exactly the contract price. A minority of supplier-part pairs get an
            # unapproved price increase from some quarter on: that's the "price leakage" the compliance check finds
            leaks = rng.random() < profile.get("price_leak_share", 0.15)
            leak_from = rng.randint(1, len(quarters) - 1)
            leak_rate = rng.uniform(0.03, 0.08)
            wording = _supplier_wording(p["_plain"], rng)
            for qi, q in enumerate(quarters):
                pid = new_po("prod")
                lot[(pn, s["supplier_id"], q)] = pid
                drift = 1 + leak_rate if leaks and qi >= leak_from else 1.0
                price_unit = 100 if (p["std_cost"] < 1.5 and rng.random() < 0.5) or rng.random() < 0.03 else 1
                qty = max(1, int(q_units.get(q, 0) / (len(sources[pn]) or 1) / p["_pack"] * rng.uniform(1.0, 1.15)))
                production_spend.append({
                    "po_line_id": pid,
                    "part_no": pn if rng.random() < profile["prod_part_no_fill"] else "",
                    "supplier_id": s["supplier_id"], "supplier_name": s["supplier_name"], "supplier_pn": spn,
                    "description": _typo(wording, rng, typo), "qty": qty, "uom": p["_uom"],
                    "unit_price": round(p["std_cost"] * level * drift * p["_pack"] * price_unit, 2),
                    "price_unit": price_unit, "po_date": f"{_quarter_start(q)}-{rng.randint(1, 20):02d}",
                    "plant": "P-MAIN", "country": s["country"]})
                truth_links.append({"source_table": "production_spend", "source_id": pid, "part_no": pn})

    # ---- acquired plant (legacy ERP): no part numbers, own suppliers + wording + price level -------------
    acq = profile.get("acquired_plant")
    if acq:
        n_acq = int(len(production_spend) * acq["share_of_production_lines"] / (1 - acq["share_of_production_lines"]))
        legacy = {c: new_supplier(c, " (TX)") for c in cats}
        lo, hi = acq["price_level"]
        for _ in range(n_acq):
            p = rng.choice(part_master)
            s = legacy[p["category"]]
            pid = new_po("acq")
            words = p["_plain"].split()
            desc = ", ".join([words[-1].capitalize()] + [" ".join(words[:-1]).lower()]) if len(words) > 2 else p["_plain"]
            production_spend.append({
                "po_line_id": pid, "part_no": "", "supplier_id": s["supplier_id"], "supplier_name": s["supplier_name"],
                "supplier_pn": f"TX{rng.randint(100000, 999999)}", "description": _typo(desc, rng, typo),
                "qty": rng.randint(20, 400), "uom": "EA",
                "unit_price": round(p["std_cost"] * rng.uniform(lo, hi), 2), "price_unit": 1,
                "po_date": f"{rng.choice(months)}-{rng.randint(1, 28):02d}", "plant": acq["plant"], "country": s["country"]})
            truth_links.append({"source_table": "production_spend", "source_id": pid, "part_no": p["part_no"]})

    # ---- service purchases: distributor, markup, mostly free text ---------------------------------------
    distributors = [new_supplier("hose", "") for _ in range(2)]
    for d, name in zip(distributors, ["Parts Distribution", "Service Supply"]):
        d["supplier_name"] = f"{d['supplier_name'].split()[0]} {name}"
    mk_lo, mk_hi = profile["spare_markup"]                    # off-contract distributor buys
    ct_lo, ct_hi = profile.get("spare_contract_markup", (1.0, 1.25))   # bought near the contract price
    for p in part_master:
        if rng.random() > 0.6:
            continue
        on_contract = rng.random() < profile.get("spare_contract_share", 0.0)
        markup = rng.uniform(ct_lo, ct_hi) if on_contract else rng.uniform(mk_lo, mk_hi)
        d = rng.choice(distributors)
        for _ in range(rng.randint(1, 4)):
            pid = new_po("svc")
            service_spend.append({
                "po_line_id": pid,
                "part_no": p["part_no"] if rng.random() < profile["service_part_no_fill"] else "",
                "supplier_id": d["supplier_id"], "supplier_name": d["supplier_name"],
                "supplier_pn": f"{d['supplier_name'][:2].upper()}-{rng.randint(10000, 99999)}",
                "description": _typo(_abbreviate(p["_plain"], abbr), rng, typo),
                "qty": rng.randint(5, 80), "uom": "EA",
                "unit_price": round(p["std_cost"] * markup * rng.uniform(0.95, 1.05), 2), "price_unit": 1,
                "po_date": f"{rng.choice(months)}-{rng.randint(1, 28):02d}", "plant": "SVC", "country": d["country"],
                "channel": rng.choice(["spares", "spares", "warranty_repair"])})
            truth_links.append({"source_table": "service_spend", "source_id": pid, "part_no": p["part_no"]})

    # ---- build_supply: which lot each product/month consumed; dual-sourced mixes VARY ------------------
    patterns = ["a_only", "b_only", "a_then_mix", "b_then_mix", "mix"]
    build_supply = []
    for p in part_master:
        pn, srcs = p["part_no"], sources[p["part_no"]]
        users = usage[pn]
        if len(srcs) == 2:
            pats = rng.sample(patterns, len(patterns))
            if pn == spike_part:   # attribution must be possible: some products A-only, some with B
                pats = ["a_only", "b_then_mix", "a_only", "mix", "b_only"]
            pat = {u: pats[i % len(pats)] for i, u in enumerate(users)}
            switch_q = quarters[rng.randint(2, len(quarters) - 2)]
        for u in users:
            for m in months:
                q = _quarter(m)
                if len(srcs) == 1:
                    mix = {srcs[0]["supplier_id"]: 1.0}
                else:
                    a, bb = srcs[0]["supplier_id"], srcs[1]["supplier_id"]
                    late = q >= switch_q
                    mix = {"a_only": {a: 1.0}, "b_only": {bb: 1.0}, "mix": {a: 0.5, bb: 0.5},
                           "a_then_mix": {a: 0.5, bb: 0.5} if late else {a: 1.0},
                           "b_then_mix": {a: 0.5, bb: 0.5} if late else {bb: 1.0}}[pat[u]]
                for sid, share in mix.items():
                    build_supply.append({"product_id": u, "build_month": m, "part_no": pn, "supplier_id": sid,
                                         "po_line_id": lot[(pn, sid, q)], "share": share})

    spike_plan = None
    if spike_part:
        a = sources[spike_part][0]["supplier_id"]
        spike_plan = {"part_no": spike_part, "supplier_id": a, "start_build_month": spike["start_build_month"],
                      "from_po_line_id": lot[(spike_part, a, _quarter(spike["start_build_month"]))],
                      "multiplier": spike["multiplier"]}

    # ---- supplier agreements (v4 documents + price schedule) for every main-plant production supplier ----
    # separate RNG so adding agreements never changes any spend value above
    arng = random.Random(seed * 7919 + 1)
    by_supplier: dict[str, list] = {}
    for pn, srcs in sources.items():
        for k, s in enumerate(srcs):
            by_supplier.setdefault(s["supplier_id"], [s, []])[1].append((pn, k))
    spn_of = {(r["part_no"], r["supplier_id"]): r["supplier_pn"] for r in info_records}
    po_by_id = {r["po_line_id"]: r for r in production_spend}
    pm_by = {p["part_no"]: p for p in part_master}
    supplier_agreements, truth_terms, truth_prices = [], [], []
    valid_from, valid_to = f"{COMMON['first_build_month']}-01", "2026-12-31"
    for sid, (s, items) in sorted(by_supplier.items()):
        terms = agreements.warranty_terms(arng)
        spares_clause = arng.random() < profile.get("spares_clause_share", 0.5)
        rows = []
        for pn, k in sorted(items):
            p = pm_by[pn]
            # contract price = the supplier's base price per piece at signing (before the ~1%/quarter creep that
            # later lots carry: that creep is the "price leakage" the compliance check finds)
            first = po_by_id[lot[(pn, sid, quarters[0])]]
            contract_ea = round(first["unit_price"] / first["price_unit"] / p["_pack"], 4)
            rows.append({"part_no": pn, "supplier_pn": spn_of[(pn, sid)], "description": p["description"],
                         "price_ea": contract_ea, "valid_from": valid_from, "valid_to": valid_to})
        fname = agreements.doc_file_name(s["supplier_name"])
        supplier_agreements.append({"doc_file": fname, "text": agreements.render_agreement(
            profile["company_name"], s, terms, rows, spares_clause)})
        truth_terms.append({"doc_file": fname, "supplier_id": sid, "recovery_pct": terms["recovery_pct"],
                            "labor_covered": terms["labor_covered"],
                            "labor_rate_cap": terms["labor_rate_cap"] if terms["labor_rate_cap"] else "",
                            "recovery_window_months": terms["recovery_window_months"],
                            "filing_deadline_days": terms["filing_deadline_days"]})
        truth_prices += [{"doc_file": fname, "supplier_id": sid, "part_no": r["part_no"], "contract_price_ea": r["price_ea"],
                          "valid_from": r["valid_from"], "valid_to": r["valid_to"], "spares_at_series_price": spares_clause}
                         for r in rows]

    for p in part_master:
        for k in ("_plain", "_uom", "_pack"):
            p.pop(k)
    return {"products": products, "part_master": part_master, "bom": bom, "builds": builds,
            "production_spend": production_spend, "service_spend": service_spend, "info_records": info_records,
            "build_supply": build_supply, "truth_links": truth_links, "_spike_plan": spike_plan,
            "supplier_agreements": supplier_agreements, "truth_terms": truth_terms, "truth_prices": truth_prices}
