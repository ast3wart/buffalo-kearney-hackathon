"""Shared taxonomy: the global contract (the UNION of every company's vocabulary).

v2 locked at CP0 (Fri Nov 13). v3 (Sat Nov 14, from Brandon's CP0 review, item #10):
each company uses a SUBSET of these codes/categories plus its own abbreviations,
chosen in afterlife/profiles.py. Change only with both people's OK + a line in
docs/team/handoffs.md.
"""

# part_master.category values. Every company's parts must use only these.
CATEGORIES = [
    # shared mechanical / electrical
    "bearing", "seal", "gasket", "hose", "fitting", "hydraulic_component", "filter", "belt", "gear",
    "wheel_tire", "brake", "cooling", "fuel", "electrical", "harness", "sensor", "battery", "lighting",
    "fastener", "structural", "plastic",
    # HVAC (v3, Northwind)
    "compressor", "refrigerant_component", "motor",
]

# failure codes = <SYSTEM>-<MODE>, modes after ISO 14224 (observed effect, not cause)
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
    # HVAC (v3, Northwind)
    {"failure_code": "REF-ELP", "system": "refrigerant", "description": "Refrigerant leakage", "likely_categories": "refrigerant_component;fitting;seal"},
    {"failure_code": "CMP-FTS", "system": "compressor", "description": "Compressor fails to start", "likely_categories": "compressor;electrical;sensor"},
    {"failure_code": "CMP-NOI", "system": "compressor", "description": "Compressor noise", "likely_categories": "compressor;motor;bearing"},
    {"failure_code": "FAN-VIB", "system": "air_handling", "description": "Fan vibration", "likely_categories": "motor;bearing;structural"},
]

FAILURE_CODE_IDS = [f["failure_code"] for f in FAILURE_CODES]

# links output (v3, item #14): every link says how it was made and why
LINK_METHODS = ["exact_pn", "info_record", "spec_code", "failure_code_bom", "fuzzy_text", "llm", "human"]
LINK_COLUMNS = ["source_table", "source_id", "part_no", "method", "confidence", "source_system", "evidence", "run_id"]

# Dataset window + per-company vocabularies, styles and knobs live in afterlife/profiles.py
