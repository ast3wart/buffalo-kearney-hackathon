"""Generate the synthetic demo portfolio (docs/build/interfaces.md §2, registry-format.md).

    python scripts/make_demo_data.py            # -> data/seed/demo/, data/truth/demo/, data/reference/alternatives.csv

Real: the part numbers (data/reference/kb.csv). Synthetic: the fund, companies, plants, lines, machines,
storerooms, what the scan "read", and all money (placeholders Brandon refines). Deterministic (seed 7).
Plants, companies and the fund are fictional.
"""
import random
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SEED_DIR, TRUTH_DIR, REF = ROOT / "data/seed/demo", ROOT / "data/truth/demo", ROOT / "data/reference"
R = random.Random(7)
SRC = ("Velocity #1-3 (100-249 employee band: maintenance $1.05M, spares $0.37M, rush ~$20k base; carrying 12-30% "
       "economic), scaled by headcount / 170; estimates, see docs/research/velocity.md")
VEL = {"maint": 1.05e6, "spares": 0.37e6, "rush": 20e3}  # base values for a ~170-person plant

KB = pd.read_csv(REF / "kb.csv", dtype=str).set_index("kb_id")

# ---------------------------------------------------------------- portfolio
FUND = ("F-STONEROSE", "Stone Rose Capital")
COMPANIES = [  # company_id, name, owned_since, deal_low, deal_high, in fund
    ("CO-HALVORSEN", "Halvorsen Industrial Products", "2019-04-01", "", "", True),
    ("CO-BRIGHTWATER", "Brightwater Packaging Systems", "2023-09-15", "", "", True),
    ("CO-TILLMAN", "Tillman Machine Works", "", 28_000_000, 34_000_000, False),
]
# plant_id, company, name, city, state, employees, status, revenue(lo,hi), spares(lo,hi), maint(lo,hi), rush(lo,hi), lines
PLANTS = [
    ("PA", "CO-HALVORSEN", "Toledo", "Toledo", "OH", 220, "owned", (60e6, 70e6), (1.8e6, 2.2e6), (4.5e6, 5.5e6), (40e3, 80e3),
     [("Progressive stamping", (60e3, 90e3)), ("Servo press + assembly", (65e3, 90e3)), ("Weld and finish", (60e3, 80e3))]),
    ("PB", "CO-HALVORSEN", "Fort Wayne", "Fort Wayne", "IN", 180, "owned", (48e6, 55e6), (1.4e6, 1.7e6), (3.5e6, 4.2e6), (30e3, 60e3),
     [("Stamping", (50e3, 75e3)), ("Machining", (50e3, 70e3)), ("Assembly", (50e3, 75e3))]),
    ("PC", "CO-HALVORSEN", "Lima", "Lima", "OH", 140, "owned", (35e6, 40e6), (1.0e6, 1.2e6), (2.6e6, 3.0e6), (25e3, 45e3),
     [("Machining", (55e3, 80e3)), ("Heat treat + finish", (55e3, 75e3))]),
    ("PD", "CO-BRIGHTWATER", "Waukesha", "Waukesha", "WI", 130, "owned", (32e6, 37e6), (0.9e6, 1.1e6), (2.4e6, 2.8e6), (20e3, 40e3),
     [("Case packer build", (50e3, 75e3)), ("Controls panel shop", (50e3, 70e3))]),
    ("PF", "CO-BRIGHTWATER", "Oshkosh", "Oshkosh", "WI", 100, "owned", (24e6, 28e6), (0.6e6, 0.8e6), (1.8e6, 2.1e6), (15e3, 30e3),
     [("Conveyor fabrication", (40e3, 60e3)), ("Final assembly", (40e3, 55e3))]),
    ("PE", "CO-TILLMAN", "Rockford", "Rockford", "IL", 90, "target", (22e6, 26e6), (0.5e6, 0.7e6), (1.6e6, 1.9e6), (15e3, 30e3),
     [("CNC machining", (35e3, 55e3)), ("Grinding + inspection", (35e3, 50e3))]),
]
MACHINES_PER_LINE = {"PA": [6, 5, 5], "PB": [5, 5, 4], "PC": [5, 5], "PD": [5, 5], "PF": [4, 4], "PE": [4, 4]}

# machine templates: type, makes/models, replacement value range (placeholder), component kb pools by company "era"
MACHINE_TYPES = {
    "press": [("Aida", "NC1-200"), ("Komatsu", "OBS 150-2"), ("Minster", "P2-200")],
    "cnc_mill": [("Haas", "VF-4"), ("Mazak", "VCN-530C"), ("Okuma", "MB-46VAE")],
    "cnc_lathe": [("Haas", "ST-30"), ("Okuma", "LB3000 EX"), ("Mazak", "QTN-250")],
    "robot_cell": [("Fanuc", "R-2000iC weld cell"), ("Yaskawa", "MH50 cell")],
    "conveyor": [("Hytrol", "E24 accumulation"), ("Dorner", "3200 series")],
    "packaging": [("Douglas Machines", "Axiom case packer"), ("Wexxar", "WFT case former")],
    "oven": [("Despatch", "PTC continuous oven"), ("Lindberg", "batch furnace")],
    "compressor": [("Atlas Copco", "GA 37"), ("Ingersoll Rand", "R37i")],
    "other": [("Miller", "PipePro welder"), ("Mitutoyo", "Crysta CMM")],
}
REPL_VALUE = {"press": (450e3, 900e3), "cnc_mill": (180e3, 420e3), "cnc_lathe": (160e3, 380e3), "robot_cell": (250e3, 500e3),
              "conveyor": (40e3, 120e3), "packaging": (150e3, 400e3), "oven": (120e3, 300e3), "compressor": (40e3, 90e3),
              "other": (30e3, 120e3)}
LINE_MACHINE_TYPES = {"stamp": ["press", "press", "robot_cell", "conveyor", "compressor", "other"],
                      "mach": ["cnc_mill", "cnc_lathe", "cnc_mill", "cnc_lathe", "other"],
                      "pack": ["packaging", "conveyor", "robot_cell", "conveyor", "other"],
                      "heat": ["oven", "oven", "conveyor", "other", "compressor"]}
# component pools per company (real KB ids): (kb_id, weight)
POOLS = {
    "CO-HALVORSEN": {"plc": ["KB-001", "KB-002", "KB-003", "KB-017", "KB-018", "KB-028", "KB-016"],
                     "drive": ["KB-006", "KB-007", "KB-019", "KB-020"], "hmi": ["KB-008", "KB-021"],
                     "servo_drive": ["KB-009", "KB-022"]},
    "CO-BRIGHTWATER": {"plc": ["KB-010", "KB-011", "KB-023", "KB-024"], "drive": ["KB-012", "KB-025", "KB-014", "KB-026"],
                       "hmi": ["KB-013", "KB-030"], "servo_drive": ["KB-022"]},
    "CO-TILLMAN": {"plc": ["KB-004", "KB-005", "KB-015", "KB-029", "KB-003"], "drive": ["KB-006", "KB-007", "KB-014"],
                   "hmi": ["KB-008"], "servo_drive": ["KB-009"]},
}
# non-KB parts the scan will also see (must stay unmatched): (text, type)
UNKNOWN_PARTS = [("PHOENIX CONTACT QUINT-PS/1AC/24DC/10", "power_supply"), ("IDEC RH2B-UL relay", "other"),
                 ("SICK WL12-3P2431 photoelectric", "other"), ("HOFFMAN A-24H2006 enclosure fan", "other")]


def rng(lo, hi):
    return round(R.uniform(lo, hi), -2)


def noisy(text, level):
    """What a scan reads off a worn label: OCR swaps, dropped dashes, stray chars, series suffixes."""
    s = text
    if level >= 1:
        s = R.choice([s, s.replace("-", ""), s.replace("-", " "), s.lower(), s + " SER B", "CAT " + s])
    if level >= 2:
        swaps = [("0", "O"), ("1", "I"), ("5", "S"), ("8", "B"), ("2", "Z")]
        a, b = R.choice(swaps)
        idx = [i for i, c in enumerate(s) if c == a]
        if idx:
            i = R.choice(idx)
            s = s[:i] + b + s[i + 1:]
    if level >= 3:
        cut = R.randint(len(s) // 2, max(len(s) // 2, len(s) - 2))
        s = s[:cut] + "…"
    return s


def main():
    for d in (SEED_DIR, TRUTH_DIR):
        d.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([{"fund_id": FUND[0] if inf else "", "fund_name": FUND[1] if inf else "", "company_id": c, "company_name": n,
                   "owned_since": since, "deal_value_low": lo, "deal_value_high": hi}
                  for c, n, since, lo, hi, inf in COMPANIES]).to_csv(SEED_DIR / "portfolio.csv", index=False)

    plants, fin, lines = [], [], []
    machines_all, comps_truth, readings_all, spares_all = {}, [], {}, {}
    for pid, co, name, city, state, emp, status, rev, spares, maint, rush, line_defs in PLANTS:
        plants.append({"plant_id": pid, "company_id": co, "plant_name": name, "city": city, "state": state,
                       "employees": emp, "status": status})
        f = emp / 170
        fin.append({"plant_id": pid, "annual_revenue_low": rev[0], "annual_revenue_high": rev[1],
                    "maintenance_budget_low": round(VEL["maint"] * f * 0.7, -3), "maintenance_budget_high": round(VEL["maint"] * f * 1.4, -3),
                    "spares_inventory_value_low": round(VEL["spares"] * f * 0.6, -3), "spares_inventory_value_high": round(VEL["spares"] * f * 1.6, -3),
                    "carrying_cost_pct_low": 0.12, "carrying_cost_pct_high": 0.30,
                    "rush_premium_annual_low": round(VEL["rush"] * f * 0.5, -2), "rush_premium_annual_high": round(VEL["rush"] * f * 2.5, -2),
                    "source": SRC})
        machines, readings = [], []
        for li, (lname, (rlo, rhi)) in enumerate(line_defs, start=1):
            lid = f"{pid}-L{li}"
            lines.append({"line_id": lid, "plant_id": pid, "line_name": f"Line {li}", "product": lname,
                          "revenue_per_day_low": rlo, "revenue_per_day_high": rhi, "contribution_margin_pct": 0.35,
                          "operating_hours_per_day": 16, "downtime_cost_per_hour_low": "", "downtime_cost_per_hour_high": ""})
            kind = ("stamp" if re.search("stamp|press|weld", lname, re.I) else "pack" if re.search("pack|conveyor|assembly|panel", lname, re.I)
                    else "heat" if re.search("heat", lname, re.I) else "mach")
            types = LINE_MACHINE_TYPES[kind]
            for mi in range(MACHINES_PER_LINE[pid][li - 1]):
                mid = f"{lid}-M{mi + 1:02d}"
                mtype = types[mi % len(types)]
                make, model = R.choice(MACHINE_TYPES[mtype])
                year = R.randint(1998, 2021) if co != "CO-TILLMAN" else R.randint(1992, 2010)
                crit = "line_stop" if mi < 2 and mtype not in ("compressor", "other") else R.choice(["degraded", "none", "degraded"])
                serial = f"{R.randint(10000, 999999)}" if R.random() > 0.15 else ""  # some serials missing, like real CMMS
                desc = R.choice([f"{make.upper()} {model.upper()} #{mi + 1}", f"{mtype.replace('_', ' ').upper()} {mi + 1} - {make}",
                                 f"{make[:4].upper()} {model.split()[0]}"])
                rv = REPL_VALUE[mtype]
                machines.append({"machine_id": mid, "line_id": lid, "asset_tag": f"{pid}{R.randint(1000, 9999)}", "description": desc,
                                 "machine_type": mtype, "make": make, "model": model, "serial": serial, "year_built": year,
                                 "condition": R.choice(["good", "fair", "fair", "poor"] if year < 2008 else ["good", "good", "fair"]),
                                 "criticality": crit, "redundant_with": "",
                                 "replacement_value_low": rv[0], "replacement_value_high": rv[1], "book_value": ""})
                # components inside this machine's cabinet
                pool = POOLS[co]
                slots = ["plc", "hmi"] if mtype in ("press", "packaging") else ["plc"]
                slots += ["drive"] if mtype in ("conveyor", "packaging", "compressor", "oven") else []
                slots += ["servo_drive"] if mtype in ("press", "robot_cell") and R.random() < 0.5 else []
                if R.random() < 0.15:
                    slots.append("unknown")
                for ci, slot in enumerate(slots, start=1):
                    cid = f"{mid}-C{ci}"
                    if slot == "unknown":
                        text, ctype = R.choice(UNKNOWN_PARTS)
                        kb_id, part_no, status_ = "", "", "unknown"
                    else:
                        # era: machines built 2012+ mostly carry current parts; older ones mostly discontinued/EOL
                        cur = [x for x in pool[slot] if KB.loc[x].lifecycle_status == "active"]
                        old = [x for x in pool[slot] if KB.loc[x].lifecycle_status != "active"]
                        p_old = 0.85 if co == "CO-TILLMAN" else (0.08 if year >= 2012 else 0.5)
                        kb_id = R.choice(old if (old and (R.random() < p_old or not cur)) else cur)
                        k = KB.loc[kb_id]
                        text, ctype, part_no, status_ = k.part_no, k.component_type, k.part_no, k.lifecycle_status
                    comps_truth.append({"component_id": cid, "kb_id": kb_id, "part_no": part_no, "lifecycle_status": status_})
                    installed = min(2026, year + R.choice([0, 0, 0, 3, 6]))
                    # a current part on an old machine is a retrofit: date it after the part existed (no 2006 CompactLogix 5380)
                    if status_ == "active" and installed < 2015:
                        installed = R.randint(2015, 2024)
                    level = R.choices([0, 1, 2, 3], weights=[35, 40, 18, 7])[0]
                    read = noisy(text, level)
                    readings.append({"reading_id": f"{cid}-R1", "plant_id": pid, "machine_id": mid, "component_id": cid,
                                     "photo_id": "", "raw_text": read, "component_type_hint": ctype,
                                     "method": "vision_sim" if R.random() < 0.6 else "list",
                                     "confidence": round({0: 0.96, 1: 0.9, 2: 0.68, 3: 0.5}[level] - R.uniform(0, 0.04), 2),
                                     "date_code": installed})
        machines_all[pid], readings_all[pid] = machines, readings

    # ------------------------------------------------------------ planted problems (override the random draws)
    comps = pd.DataFrame(comps_truth).set_index("component_id")
    reads = {pid: pd.DataFrame(r).set_index("component_id") for pid, r in readings_all.items()}
    mach = {pid: pd.DataFrame(m).set_index("machine_id") for pid, m in machines_all.items()}

    def plant(cid, kb_id, read_text=None, conf=None, date_code=None):
        pid = cid[:2]
        k = KB.loc[kb_id]
        comps.loc[cid, ["kb_id", "part_no", "lifecycle_status"]] = [kb_id, k.part_no, k.lifecycle_status]
        reads[pid].loc[cid, "raw_text"] = read_text or k.part_no
        reads[pid].loc[cid, "component_type_hint"] = k.component_type
        if conf is not None:
            reads[pid].loc[cid, "confidence"] = conf
        if date_code is not None:
            reads[pid].loc[cid, "date_code"] = date_code

    # 2) Toledo Line 2, machine 1 (servo press): line-stopping Kinetix 6000, no spare at Toledo
    spof_cid = "PA-L2-M01-C1"
    mach["PA"].loc["PA-L2-M01", ["machine_type", "make", "model", "criticality", "description", "year_built"]] = \
        ["press", "Aida", "NC1-200 servo", "line_stop", "AIDA NC1-200 SERVO PRESS #1", 2008]
    if spof_cid not in reads["PA"].index:
        raise SystemExit("planting failed: no component slot on PA-L2-M01")
    plant(spof_cid, "KB-009", read_text="2094-BC01-MP5-S SER C", conf=0.93, date_code=2008)
    # 6) Tillman: old discontinued controllers past life
    for cid, kb in [("PE-L1-M01-C1", "KB-004"), ("PE-L1-M02-C1", "KB-005"), ("PE-L2-M01-C1", "KB-015")]:
        if cid in comps.index:
            plant(cid, kb, date_code=R.randint(1996, 2004))
    # 7) a few low-confidence readings
    for pid in ("PA", "PD"):
        for cid in reads[pid].sample(2, random_state=7).index:
            reads[pid].loc[cid, "confidence"] = round(R.uniform(0.35, 0.6), 2)

    # ------------------------------------------------------------ storerooms
    spare_rows, spare_truth = [], []

    def spare(pid, kb_id, desc, qty, last_moved, part_no_recorded=True):
        sid = f"{pid}-S{len([s for s in spare_rows if s['plant_id'] == pid]) + 1:03d}"
        k = KB.loc[kb_id]
        spare_rows.append({"spare_id": sid, "plant_id": pid, "material_no": f"{R.randint(100000, 999999)}", "description": desc,
                           "manufacturer": k.manufacturer if part_no_recorded else "", "part_no": k.part_no if part_no_recorded else "",
                           "qty": qty, "bin": f"{R.choice('ABCDEFG')}{R.randint(1, 30):02d}-{R.randint(1, 6)}",
                           "last_moved_on": last_moved, "unit_cost_book": ""})
        spare_truth.append({"spare_id": sid, "kb_id": kb_id})
        return sid

    # 3) the portfolio moment: Fort Wayne has 2 Kinetix 6000 IAMs under a messy description, no part number recorded
    fw_spare = spare("PB", "KB-009", "SERVO DRV KIN6K IAM 460V 6KW", 2, "2019-08-14", part_no_recorded=False)
    # second match across companies: Lima holds a MICROMASTER 440 left from a retired line; Waukesha runs MM440s
    lima_spare = spare("PC", "KB-012", "VFD SIEMENS MM440 4KW 480", 1, "2017-03-02", part_no_recorded=False)
    # 4) duplicates: Toledo stocks PowerFlex 40 twice under two names; Lima stocks the L61 twice
    d1 = spare("PA", "KB-006", "DRIVE AB PF40 5HP 480V", 2, "2023-05-10")
    d2 = spare("PA", "KB-006", "VFD POWERFLEX40 5 HP", 1, "2021-11-02", part_no_recorded=False)
    d3 = spare("PC", "KB-001", "PROCESSOR CLX L61", 1, "2016-06-20")
    d4 = spare("PC", "KB-001", "CTRLLOGIX 5561 CPU 2MB", 1, "2018-01-09", part_no_recorded=False)
    # ordinary stock per plant (some idle 5+ years)
    for pid, co, *_ in PLANTS:
        for _ in range(R.randint(5, 8)):
            # keep the planted stories clean: Toledo has no Kinetix 6000 spare; Brightwater has no MM440 spare
            # (so the Waukesha drive's spare must come from Lima, across companies)
            blocked = {"PA": {"KB-009"}, "PD": {"KB-012"}, "PF": {"KB-012"}}.get(pid, set())
            kb_id = R.choice([x for x in sum(POOLS[co].values(), []) if x not in blocked])
            k = KB.loc[kb_id]
            spare(pid, kb_id, R.choice([k.description.upper()[:28], f"{k.family.upper()} {k.part_no}", k.aliases.split(";")[-1].upper()]),
                  R.randint(1, 3), f"{R.randint(2014, 2026)}-{R.randint(1, 12):02d}-{R.randint(1, 28):02d}", R.random() > 0.4)
    # make sure Waukesha actually runs a MICROMASTER 440 that Lima's spare covers
    wk = [c for c in comps.index if c.startswith("PD-") and comps.loc[c, "kb_id"]
          and KB.loc[comps.loc[c, "kb_id"]].component_type == "drive"]
    wk_cid = wk[0]
    plant(wk_cid, "KB-012", read_text="6SE6440-2UD24-0BA1", conf=0.9, date_code=2011)
    mach["PD"].loc[wk_cid.rsplit("-C", 1)[0], "criticality"] = "line_stop"
    # Toledo must NOT hold its own Kinetix 6000 spare
    spare_df = pd.DataFrame(spare_rows)
    tr = pd.DataFrame(spare_truth)
    assert not ((spare_df.plant_id == "PA") & (tr.kb_id == "KB-009")).any(), "Toledo must not stock its own SPOF spare"

    # ------------------------------------------------------------ write per-plant files
    for pid, *_ in PLANTS:
        d = SEED_DIR / pid
        d.mkdir(exist_ok=True)
        mach[pid].reset_index().to_csv(d / "assets.csv", index=False)
        spare_df[spare_df.plant_id == pid].to_csv(d / "spares.csv", index=False)
        reads[pid].reset_index()[["reading_id", "plant_id", "machine_id", "component_id", "photo_id", "raw_text",
                                  "component_type_hint", "method", "confidence", "date_code"]].to_csv(d / "readings.csv", index=False)
        if not (d / "photos.csv").exists():  # never overwrite: render_test_photos.py / real photos own this file
            pd.DataFrame(columns=["photo_id", "plant_id", "machine_id", "component_id", "file", "photo_kind", "taken_on",
                                  "quality", "rendered"]).to_csv(d / "photos.csv", index=False)
    pd.DataFrame(plants).to_csv(SEED_DIR / "plants.csv", index=False)
    pd.DataFrame(fin).to_csv(SEED_DIR / "plant_financials.csv", index=False)
    pd.DataFrame(lines).to_csv(SEED_DIR / "lines.csv", index=False)

    # ------------------------------------------------------------ alternatives (real successors from the KB + 1 similar-part placeholder)
    alts = []
    for kb_id, k in KB.iterrows():
        if isinstance(k.successor_part_no, str) and k.lifecycle_status in ("discontinued", "end_of_life"):
            alts.append({"alt_id": f"ALT-{len(alts) + 1:03d}", "kb_id": kb_id, "alt_part_no": k.successor_part_no,
                         "alt_manufacturer": k.manufacturer, "alternative_kind": "successor", "found_by": "oem_lifecycle",
                         "fit_notes": "migration: new firmware/program conversion, wiring and mounting check", "engineering_needed": "yes",
                         "source_url": k.source_url if isinstance(k.source_url, str) else ""})
    alts.append({"alt_id": f"ALT-{len(alts) + 1:03d}", "kb_id": "KB-029", "alt_part_no": "", "alt_manufacturer": "",
                 "alternative_kind": "similar", "found_by": "similar_part_search",
                 "fit_notes": "TBD: similar-part search (possible Physna collaboration)", "engineering_needed": "yes", "source_url": ""})
    pd.DataFrame(alts).to_csv(REF / "alternatives.csv", index=False)

    # ------------------------------------------------------------ answer key
    comps.reset_index().to_csv(TRUTH_DIR / "components.csv", index=False)
    tr.to_csv(TRUTH_DIR / "spare_matches.csv", index=False)
    pd.DataFrame([{"spare_id_a": d1, "spare_id_b": d2}, {"spare_id_a": d3, "spare_id_b": d4}]).to_csv(TRUTH_DIR / "duplicates.csv", index=False)
    pd.DataFrame([{"component_id": spof_cid, "why": "Toledo Line 2 servo press runs on a discontinued Kinetix 6000; no spare at Toledo",
                   "shelf_spare_id": fw_spare},
                  {"component_id": wk_cid, "why": "Waukesha line-stopping MICROMASTER 440 (discontinued); spare sits at Lima (other company, same fund)",
                   "shelf_spare_id": lima_spare}]).to_csv(TRUTH_DIR / "spof.csv", index=False)

    # ------------------------------------------------------------ summary + sanity checks
    allm = pd.concat(mach.values())
    print(f"plants {len(plants)} · lines {len(lines)} · machines {len(allm)} · components {len(comps)} · spares {len(spare_df)}")
    st = comps.lifecycle_status.value_counts().to_dict()
    print("component lifecycle:", st)
    assert 55 <= len(allm) <= 75 and 100 <= len(comps) <= 150, "portfolio size off target"
    assert st.get("discontinued", 0) >= 15, "too few discontinued parts"


if __name__ == "__main__":
    main()
