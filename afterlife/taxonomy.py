"""Shared taxonomy, locked at CP0 (Fri Nov 13). Single source of truth for both threads.

Change only with both people's OK + a line in docs/team/handoffs.md.
"""

# part_master.category values (💲 Asher's parts must use only these)
CATEGORIES = [
    "bearing", "seal", "gasket", "hose", "fitting", "hydraulic_component", "filter", "belt", "gear",
    "wheel_tire", "brake", "cooling", "fuel", "electrical", "harness", "sensor", "battery", "lighting",
    "fastener", "structural", "plastic",
]

# failure codes = <SYSTEM>-<MODE>, modes after ISO 14224 (observed effect, not cause)  (🛠 Brandon)
FAILURE_CODES = [
    {"failure_code": "HYD-ELP", "system": "hydraulic", "description": "External leakage", "likely_categories": "seal;hose;fitting;hydraulic_component"},
    {"failure_code": "HYD-LOP", "system": "hydraulic", "description": "Low output / pressure", "likely_categories": "hydraulic_component;seal;filter"},
    {"failure_code": "DRV-VIB", "system": "drivetrain", "description": "Vibration", "likely_categories": "bearing;belt;gear;wheel_tire"},
    {"failure_code": "DRV-NOI", "system": "drivetrain", "description": "Noise", "likely_categories": "bearing;gear;belt"},
    {"failure_code": "ENG-ELP", "system": "engine", "description": "External leakage (oil)", "likely_categories": "filter;seal;gasket"},
    {"failure_code": "ENG-OHE", "system": "engine", "description": "Overheating", "likely_categories": "cooling;belt;sensor"},
    {"failure_code": "ELE-FTS", "system": "electrical", "description": "Fail to start", "likely_categories": "electrical;battery;fuel;sensor"},
    {"failure_code": "ELE-INT", "system": "electrical", "description": "Intermittent operation", "likely_categories": "electrical;sensor;harness"},
    {"failure_code": "BRK-NOI", "system": "brakes", "description": "Noise", "likely_categories": "brake"},
    {"failure_code": "BRK-DEG", "system": "brakes", "description": "Degraded performance", "likely_categories": "brake;hydraulic_component"},
    {"failure_code": "BDY-STR", "system": "body", "description": "Structural / cracking", "likely_categories": "structural;fastener;plastic"},
    {"failure_code": "LGT-FTF", "system": "lighting", "description": "Fails to function", "likely_categories": "lighting;harness"},
]

# Dataset window + per-company settings live in afterlife/profiles.py
