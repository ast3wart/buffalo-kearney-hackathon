"""SIMULATED condition data for the demo (every row is marked simulated=yes).

    python scripts/make_condition_data.py     # -> data/seed/demo/<plant>/condition.csv

What a plant would give us, plus what the X-Ray Monitor device would measure:
  - plant records: install year from CMMS work orders / purchase orders (formula below: ~28% of parts, by plant tier)
  - self-reported diagnostics: only newer, networked drives/PLCs (capacitor + fan life used, faults)
  - thermal: continuous (device on line-stopper cabinets) or a one-time snapshot from the walk (everything else)
  - motor current: on drives in device-equipped cabinets (clamp-on current sensor)
  - time series (device cabinets): thermal_series.csv + current_series.csv, 90 daily summaries per part
Planted for the model to find: Toledo's line-stopping Kinetix 6000 with a failing fan (runs hot vs identical
parts), a Fort Wayne drive with capacitors near end of life (self-reported), a press drive whose motor shows a
current-signature anomaly, and a hot connection with logged faults at Lima.
"""
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data/seed/demo"
R = random.Random(31)
R2 = random.Random(32)   # separate stream for the records formula, so the other simulated values stay as before

# --- How many parts have an install record: a formula from the Velocity research (docs/research/velocity.md,
# "Manufacturing Maintenance Data Adoption", Nov 15). Every input is labeled; low/high in the comment.
P_CMMS = 0.60            # plant uses a CMMS/EAM (45-75%; Plant Engineering 2018: 53%, 2019: 61%) - estimate
P_PART_LEVEL = 0.15      # of CMMS plants, keeps part-level records with install dates (5-30%) - estimate, low confidence
COMPLETENESS = 0.70      # a record that should exist is filled in and right (Lukens 2019: fields 20% -> 90%) - assumption
P_ORIGINAL = 0.60        # part is still the machine's original, so the machine install year is its age - assumption
# expected part coverage = P_CMMS * (P_PART_LEVEL*COMPLETENESS + (1-P_PART_LEVEL)*P_ORIGINAL*COMPLETENESS)
#                        = 0.60 * (0.105 + 0.357) = ~28% (6% part records + 21% machine records)
# Plants differ, so each plant gets a tier. The expected mix over 6 plants (40% none / 51% machine / 9% part level)
# rounds to 2 / 3 / 1; the part-level plant is rounded up from 0.54 so the demo shows that case.
RECORDS_TIER = {"PA": "part_level", "PB": "machine_level", "PD": "machine_level", "PF": "machine_level",
                "PC": "none", "PE": "none"}
# families that report their own health over the network (newer platforms)
SELF_REPORTING = {"PowerFlex 525", "ControlLogix 5580", "CompactLogix 5380", "Kinetix 5700", "SIMATIC S7-1500",
                  "SIMATIC S7-1200", "SINAMICS G120C", "ACS580", "MELSEC iQ-F"}
RISE = {"drive": (16, 24), "servo_drive": (16, 24), "power_supply": (10, 16), "plc": (8, 13), "plc_io": (6, 10), "hmi": (7, 11)}


def main():
    kb = pd.read_csv(ROOT / "data/reference/kb.csv", dtype=str).fillna("").set_index("kb_id")
    truth = pd.read_csv(ROOT / "data/truth/demo/components.csv", dtype=str).fillna("").set_index("component_id")
    reads = pd.concat(pd.read_csv(f, dtype=str) for f in SEED.glob("*/readings.csv")).set_index("component_id")
    assets = pd.concat(pd.read_csv(f, dtype=str) for f in SEED.glob("*/assets.csv")).set_index("machine_id")
    rows = []
    for cid, t in truth.iterrows():
        mid = cid.rsplit("-C", 1)[0]
        line_stop = assets.loc[mid, "criticality"] == "line_stop"
        k = kb.loc[t.kb_id] if t.kb_id else None
        ctype = k.component_type if k is not None else reads.loc[cid, "component_type_hint"]
        year = int(reads.loc[cid, "date_code"])
        amb = round(R.uniform(30, 38), 1)
        lo, hi = RISE.get(ctype, (5, 9))
        temp = amb + R.uniform(lo, hi) + max(0, 2026 - year - 10) * 0.3   # older parts run a bit warmer
        row = {"component_id": cid, "plant_id": cid[:2], "simulated": "yes",
               "install_year_record": "", "install_year_basis": "",
               "thermal_mode": "continuous" if line_stop else "snapshot", "days_observed": R.randint(30, 120) if line_stop else 1,
               "ambient_c": amb, "temp_c": round(temp, 1),
               "diag_cap_life_used": "", "diag_fan_life_used": "", "diag_heatsink_c": "", "diag_run_hours": "", "diag_faults_12m": "",
               "ctype": ctype}
        if ctype in ("drive", "servo_drive"):
            R.uniform(0.03, 0.2)   # keeps the random sequence (and the demo's other values) as before
        R.random()   # keeps the random sequence (and the demo's other values) as before
        tier = RECORDS_TIER.get(cid[:2], "none")
        if tier == "part_level" and R2.random() < COMPLETENESS:
            row["install_year_record"], row["install_year_basis"] = year, "part record"
        elif tier == "machine_level" and R2.random() < P_ORIGINAL * COMPLETENESS:
            row["install_year_record"], row["install_year_basis"] = year, "machine record (original part)"
        if k is not None and k.family in SELF_REPORTING:
            age = max(0, 2026 - year)
            row["diag_run_hours"] = int(age * R.uniform(5200, 7000))
            row["diag_faults_12m"] = R.choice([0, 0, 0, 0, 1])
            if ctype in ("drive", "servo_drive"):
                row["diag_cap_life_used"] = round(min(0.95, age / 12 * R.uniform(0.8, 1.2)), 2)
                row["diag_fan_life_used"] = round(min(0.97, age / 8 * R.uniform(0.8, 1.2)), 2)
                row["diag_heatsink_c"] = round(temp + R.uniform(3, 8), 1)
        rows.append(row)
    df = pd.DataFrame(rows).set_index("component_id")

    # --- planted problems (the patterns live in the time series below; the snapshot is their last-week mean)
    pb_drive = next((c for c in df.index if c.startswith("PB") and df.loc[c, "diag_cap_life_used"] != ""), None)
    if pb_drive:
        df.loc[pb_drive, ["diag_cap_life_used", "diag_fan_life_used"]] = [0.91, 0.62]
    press_drive = next((c for c in df.index if c.startswith("PA-L1") and df.loc[c, "ctype"] in ("drive", "servo_drive")), None)
    lima = next((c for c in df.index if c.startswith("PC") and truth.loc[c, "kb_id"]), None)
    if lima:
        df.loc[lima, "diag_faults_12m"] = 3
    patterns = {"PA-L2-M01-C1": "step", pb_drive: "drift", press_drive: "current", lima: "spikes"}
    for cid in patterns:
        if cid:
            df.loc[cid, ["thermal_mode", "days_observed"]] = ["continuous", 90]
    planted = {"PA-L2-M01-C1": "failing fan: temperature steps up ~18°C at day 70 (EWMA shift)", pb_drive: "capacitors 91% used (self-reported) + slow warming (CUSUM drift / trend)",
               press_drive: "motor current sideband energy rising (Mahalanobis on current features)", lima: "hot connection: intermittent temperature spikes + 3 faults"}

    # --- time series from the device (continuous cabinets only): 90 daily summaries per part
    therm, curr = [], []
    for cid in df.index[df.thermal_mode == "continuous"]:
        amb0, rise = float(df.loc[cid, "ambient_c"]), float(df.loc[cid, "temp_c"]) - float(df.loc[cid, "ambient_c"])
        pat = next((v for k_, v in patterns.items() if k_ == cid), "")
        temps = []
        for d in range(90):
            amb = amb0 + 2.5 * __import__("math").sin(d / 9) + R.gauss(0, 0.8)
            load = min(100, max(20, R.gauss(70, 12)))
            t = amb + rise * (0.6 + 0.4 * load / 70) + R.gauss(0, 0.8)
            if pat == "step" and d >= 70:
                t += 18
            if pat == "drift" and d >= 30:
                t += 0.12 * (d - 30)
            if pat == "spikes" and d >= 45 and R.random() < 0.35:
                t += R.uniform(10, 25)
            temps.append(t)
            therm.append({"component_id": cid, "plant_id": cid[:2], "day": d, "temp_c": round(t, 1), "ambient_c": round(amb, 1),
                          "load_pct": round(load), "simulated": "yes"})
            if df.loc[cid, "ctype"] in ("drive", "servo_drive"):
                sb = -48 + R.gauss(0, 1.0) + (0.35 * (d - 50) if pat == "current" and d >= 50 else 0)
                rpl = 1.0 + R.gauss(0, 0.02) + (0.003 * (d - 50) if pat == "current" and d >= 50 else 0)
                curr.append({"component_id": cid, "plant_id": cid[:2], "day": d, "rms_per_load": round(rpl, 3),
                             "sideband_db": round(sb, 1), "simulated": "yes"})
        df.loc[cid, "temp_c"] = round(sum(temps[-7:]) / 7, 1)
    df = df.drop(columns="ctype")
    for name, rows_ in (("thermal_series", therm), ("current_series", curr)):
        ts = pd.DataFrame(rows_)
        for pid, g in ts.groupby("plant_id"):
            g.drop(columns="plant_id").to_csv(SEED / pid / f"{name}.csv", index=False)
    for pid, g in df.reset_index().groupby("plant_id"):
        g.to_csv(SEED / pid / "condition.csv", index=False)
    pd.DataFrame([{"component_id": k_, "problem": v} for k_, v in planted.items() if k_]).to_csv(
        ROOT / "data/truth/demo/condition_planted.csv", index=False)
    print(f"{len(df)} condition rows (simulated); planted: {planted}")


if __name__ == "__main__":
    main()
