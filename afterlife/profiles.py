"""Company profiles: the generator builds one dataset per company.

Why several companies (CP0) and why they must be genuinely DIFFERENT (v3, Brandon's review #10):
  - proves the tool generalizes: different words, part-number styles and data quirks, not just weights
  - holdout accuracy: tune matching on one company, report accuracy on the others
  - a company with NO planted spike tests false alarms
  - the matching code may not mention any of these companies (tests/test_no_literals.py, #11)
Each company is written to data/generated/<company_id>/ with the SAME data contract
(docs/build/data-contract.md). Warranty % of revenue is calibrated to real 2024 SEC filers.

Knob owners: 💲 Asher (spend) reads part/supplier/plant/style knobs; 🛠 Brandon (warranty)
reads failure_codes, claim style and spike knobs.
"""

COMMON = {
    "data_as_of": "2026-10-31",
    "first_build_month": "2025-01",
    "last_build_month": "2026-09",
    "currency": "USD",
    "warranty_months": "24",
    "mis_window": "3",
}

# vehicle / mobile-equipment shorthand (Prairie, Ironridge)
_MOBILE_ABBR = {
    "BRG": "BEARING", "HYD": "HYDRAULIC", "CYL": "CYLINDER", "REPL": "REPLACED", "ASSY": "ASSEMBLY",
    "FLTR": "FILTER", "GSKT": "GASKET", "IGN": "IGNITION", "FRT": "FRONT", "RR": "REAR", "TRANS": "TRANSMISSION",
    "SW": "SWITCH", "HRNS": "HARNESS", "BRKT": "BRACKET", "CUST": "CUSTOMER", "LKG": "LEAKING",
}
# HVAC shorthand (Northwind)
_HVAC_ABBR = {
    "CMPR": "COMPRESSOR", "COND": "CONDENSER", "EVAP": "EVAPORATOR", "TXV": "EXPANSION VALVE",
    "CAP": "CAPACITOR", "RTU": "ROOFTOP UNIT", "REFRIG": "REFRIGERANT", "CTRL": "CONTROL", "MTR": "MOTOR",
    "BRG": "BEARING", "REPL": "REPLACED", "LKG": "LEAKING", "SENS": "SENSOR", "HRNS": "HARNESS",
}

PROFILES = [
    {
        "company_id": "prairie",
        "company_name": "Prairie Utility Vehicles",
        "industry": "Utility vehicles and compact tractors",
        "benchmark": "Polaris (2.56% of revenue)",
        "role": "tune",
        "warranty_pct_revenue": 2.5,
        # parts and suppliers (💲)
        "n_products": 3, "n_parts": 300, "shared_part_share": 0.40,
        "category_weights": {"hydraulic_component": 2, "seal": 2, "hose": 2, "bearing": 2, "belt": 2, "fuel": 1.5},
        "exclude_categories": ["compressor", "refrigerant_component", "motor"],
        "pn_format": "{a:03d}-{b:04d}-{c:02d}",          # 100-4471-02
        "desc_style": "erp_shorthand",                      # BRG,BALL,6204-2RS,20MM
        "prod_part_no_fill": 0.85, "service_part_no_fill": 0.15, "spare_markup": (1.6, 4.5),
        "dual_source_share": 0.15,                          # share of parts with 2 production suppliers
        "acquired_plant": None,
        "extract_format": "contract",                       # columns as in the data contract
        # vocabulary
        "failure_codes": ["HYD-ELP", "HYD-LOP", "DRV-VIB", "DRV-NOI", "ENG-ELP", "ENG-OHE",
                          "ELE-FTS", "ELE-INT", "BRK-NOI", "BRK-DEG", "BDY-STR", "LGT-FTF"],
        "abbreviations": _MOBILE_ABBR,
        # claims (🛠)
        "causal_blank_share": 0.60, "causal_wrong_share": 0.10, "typo_rate": 0.05,
        "spike": {"category": "seal", "start_build_month": "2026-03", "multiplier": 3.0,
                  "dual_sourced": True},                    # the demo story: one supplier's lots only
    },
    {
        "company_id": "ironridge",
        "company_name": "Ironridge Compact Equipment",
        "industry": "Skid steers and mini excavators",
        "benchmark": "CNH Industrial (2.87% of revenue)",
        "role": "holdout",
        "warranty_pct_revenue": 2.9,
        "n_products": 4, "n_parts": 380, "shared_part_share": 0.45,
        "category_weights": {"hydraulic_component": 3, "hose": 3, "fitting": 2, "structural": 2, "gear": 1.5},
        "exclude_categories": ["compressor", "refrigerant_component", "motor", "lighting"],
        "pn_format": "IR-{n:05d}",                          # IR-04471
        "desc_style": "erp_shorthand",
        "prod_part_no_fill": 0.80, "service_part_no_fill": 0.10, "spare_markup": (1.8, 5.0),
        "dual_source_share": 0.20,
        # v3 #12: acquired plant on a legacy ERP. No MATNR, own supplier list, own description style,
        # own price level, so a plant-vs-plant harmonization lever exists alongside production-vs-spare
        "acquired_plant": {"plant": "P-TX2", "share_of_production_lines": 0.30, "part_no_fill": 0.0,
                           "desc_style": "plain_words", "price_level": (1.05, 1.25), "source_system": "LEGACY-P-TX2"},
        "extract_format": "sap",                            # v3 #15: arrives as a raw SAP extract (see adapters/sap.py)
        "failure_codes": ["HYD-ELP", "HYD-LOP", "DRV-VIB", "DRV-NOI", "ENG-ELP", "ENG-OHE",
                          "ELE-FTS", "ELE-INT", "BRK-NOI", "BRK-DEG", "BDY-STR"],
        "abbreviations": _MOBILE_ABBR,
        "causal_blank_share": 0.65, "causal_wrong_share": 0.08, "typo_rate": 0.07,
        "spike": {"category": "bearing", "start_build_month": "2025-11", "multiplier": 2.5,
                  "dual_sourced": True},
    },
    {
        "company_id": "northwind",
        "company_name": "Northwind Climate Systems",
        "industry": "Commercial rooftop HVAC units",
        "benchmark": "Carrier Global (1.54% of revenue)",
        "role": "holdout",
        "warranty_pct_revenue": 1.5,
        "n_products": 3, "n_parts": 260, "shared_part_share": 0.35,
        "category_weights": {"compressor": 3, "refrigerant_component": 3, "motor": 2, "electrical": 3, "sensor": 2,
                             "harness": 2},
        "exclude_categories": ["hydraulic_component", "brake", "fuel", "wheel_tire", "gear", "lighting", "battery"],
        "pn_format": "NW{n:04d}{rev}",                      # NW4471A
        "desc_style": "plain_words",                        # "Scroll compressor 5 ton 460V"
        "prod_part_no_fill": 0.90, "service_part_no_fill": 0.30, "spare_markup": (1.4, 3.5),
        "dual_source_share": 0.10,
        "acquired_plant": None,
        "extract_format": "contract",
        "failure_codes": ["REF-ELP", "CMP-FTS", "CMP-NOI", "FAN-VIB", "ELE-FTS", "ELE-INT", "BDY-STR"],
        "abbreviations": _HVAC_ABBR,
        "causal_blank_share": 0.50, "causal_wrong_share": 0.12, "typo_rate": 0.04,
        "spike": None,  # control company: alerts should come back EMPTY
    },
]


def dataset_info(profile: dict) -> dict:
    """Rows for dataset_info.csv for one company."""
    keys = ["company_id", "company_name", "industry"]
    return {**{k: profile[k] for k in keys}, **COMMON}


def abbreviations_rows(profile: dict) -> list[dict]:
    """Rows for abbreviations.csv (abbr, expansion): client data, not code (v3 #10)."""
    return [{"abbr": a, "expansion": e} for a, e in sorted(profile["abbreviations"].items())]


def failure_code_rows(profile: dict) -> list[dict]:
    """Rows for failure_codes.csv: this company's subset of taxonomy.FAILURE_CODES."""
    from afterlife.taxonomy import FAILURE_CODES
    keep = set(profile["failure_codes"])
    return [f for f in FAILURE_CODES if f["failure_code"] in keep]
