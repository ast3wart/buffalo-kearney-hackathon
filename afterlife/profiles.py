"""Company profiles: the generator builds one dataset per company (decided Fri Nov 13).

Why several companies:
  - proves the tool generalizes instead of being tuned to one fake dataset
  - holdout accuracy: tune matching on one company, report accuracy on the others
  - a company with NO planted spike tests false alarms
Each company is written to data/generated/<company_id>/ with the SAME data contract.
Warranty % of revenue is calibrated to real 2024 SEC filers (data/reference/sec_warranty_2024.csv).
Spend thread (💲 Asher) reads products/parts/suppliers knobs; warranty thread (🛠 Brandon) reads warranty/spike knobs.
"""

COMMON = {
    "data_as_of": "2026-10-31",
    "first_build_month": "2025-01",
    "last_build_month": "2026-09",
    "currency": "USD",
    "warranty_months": "24",
    "mis_window": "3",
}

PROFILES = [
    {
        "company_id": "prairie",
        "company_name": "Prairie Utility Vehicles",
        "industry": "Utility vehicles and compact tractors",
        "benchmark": "Polaris (2.56% of revenue)",
        "warranty_pct_revenue": 2.5,
        "n_products": 3, "n_parts": 300, "shared_part_share": 0.40,
        "category_weights": {"hydraulic_component": 2, "seal": 2, "hose": 2, "bearing": 2, "belt": 2, "fuel": 1.5},
        "prod_part_no_fill": 0.85, "service_part_no_fill": 0.15, "spare_markup": (1.6, 4.5),
        "spike": {"category": "seal", "start_build_month": "2026-03", "multiplier": 3.0},  # the demo story
        "role": "tune",
    },
    {
        "company_id": "ironridge",
        "company_name": "Ironridge Compact Equipment",
        "industry": "Skid steers and mini excavators",
        "benchmark": "CNH Industrial (2.87% of revenue)",
        "warranty_pct_revenue": 2.9,
        "n_products": 4, "n_parts": 380, "shared_part_share": 0.45,
        "category_weights": {"hydraulic_component": 3, "hose": 3, "fitting": 2, "structural": 2, "gear": 1.5},
        "prod_part_no_fill": 0.80, "service_part_no_fill": 0.10, "spare_markup": (1.8, 5.0),
        "spike": {"category": "bearing", "start_build_month": "2025-11", "multiplier": 2.5},
        "role": "holdout",
    },
    {
        "company_id": "northwind",
        "company_name": "Northwind Climate Systems",
        "industry": "Commercial rooftop HVAC units",
        "benchmark": "Carrier Global (1.54% of revenue)",
        "warranty_pct_revenue": 1.5,
        "n_products": 3, "n_parts": 260, "shared_part_share": 0.35,
        "category_weights": {"cooling": 3, "electrical": 3, "sensor": 2, "harness": 2, "structural": 1.5},
        "prod_part_no_fill": 0.90, "service_part_no_fill": 0.30, "spare_markup": (1.4, 3.5),
        "spike": None,  # control company: alerts should come back EMPTY
        "role": "holdout",
    },
]


def dataset_info(profile: dict) -> dict:
    """Rows for dataset_info.csv for one company."""
    keys = ["company_id", "company_name", "industry"]
    return {**{k: profile[k] for k in keys}, **COMMON}
