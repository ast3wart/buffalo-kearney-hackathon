"""Every money-model parameter in one place, as a low / base / high range with a source label.

Swap a Velocity answer in here (and change its `source`) and every function picks it up. Labels follow
model-spec: measured / survey / vendor / estimate / assumption. "velocity #N" = the prompt in
docs/plan/financials/velocity-prompts.md that will replace the fallback.
"""
from typing import NamedTuple


class P(NamedTuple):
    low: float
    base: float
    high: float
    source: str


AS_OF_YEAR = 2026          # ages are counted from here (date_code -> age)
DOMESTIC = {"US"}          # seller locations not counted as cross-border for the trust score

# --- failure probability by component age (velocity #4). Lifecycle status changes hours down, not the odds.
FAILURE_RATE_BY_AGE = [    # (age from, age to) in years -> annual failure probability
    ((0, 10), P(0.02, 0.03, 0.05, "estimate, velocity #4 (Nov 14): field rates, capped ~10%/yr")),
    ((10, 20), P(0.04, 0.06, 0.08, "estimate, velocity #4 (Nov 14): field rates, capped ~10%/yr")),
    ((20, 999), P(0.06, 0.08, 0.10, "estimate, velocity #4 (Nov 14): field rates, capped ~10%/yr")),
]
FAILURE_RATE_AGE_UNKNOWN = P(0.04, 0.06, 0.08, "estimate, velocity #4 (age unknown -> middle band)")

# --- hours down (spof)
SWAP_HOURS = P(2, 4, 8, "assumption: swap + re-commission a shelf spare")
TRANSFER_DAYS = P(1, 1.5, 2, "assumption, velocity #20: overnight to 2-day freight from a sister plant")
EMERGENCY_OVERHEAD_DAYS = P(1, 3, 5, "assumption: find, order, receive and commission a broker unit")
LEAD_TIME_WKS_NEW = P(1, 2.5, 4, "assumption: distributor stock for an active part (kb lead_time_wks_new blank)")
LEAD_TIME_WKS_SUCCESSOR = P(2, 5, 8, "assumption: successor hardware when the part itself can't be bought")
LEAD_TIME_WKS_UNLISTED = P(8, 14, 20, "assumption: broker search for a discontinued part with no listings")
MIGRATION_DOWNTIME_HOURS = P(40, 80, 120, "assumption, velocity #5 (kb migration_downtime_hours blank)")

# --- costs
TRANSFER_FREIGHT = P(100, 155, 400, "estimate, velocity #20 (Nov 14): ~$355 per transfer incl. admin")
TRANSFER_ADMIN = P(200, 200, 200, "estimate, velocity #20 (Nov 14)")
EMERGENCY_MULTIPLIER = P(1.1, 1.3, 1.6, "estimate, velocity #5 (Nov 14): emergency vs planned, before downtime")
EMERGENCY_HAIRCUT = 0.5    # share of planned-vs-emergency savings counted in the price base (model-spec §2)
MIGRATION_HOURS = {        # engineering hours to migrate to the successor, by component_type (velocity #16)
    "plc": P(40, 60, 80, "assumption, velocity #16"),
    "servo_drive": P(20, 40, 60, "assumption, velocity #16"),
    "drive": P(8, 16, 24, "assumption, velocity #16"),
    "hmi": P(16, 32, 48, "assumption, velocity #16"),
}
MIGRATION_HOURS_DEFAULT = P(20, 50, 80, "assumption, velocity #16")
ENGINEERING_RATE = P(150, 225, 300, "assumption, velocity #16 ($/h)")
UNIT_COST_BY_TYPE = {      # hardware fallback when a part has no trusted listings (velocity #16)
    "plc": P(3000, 8000, 15000, "assumption, velocity #16"),
    "plc_io": P(300, 800, 2000, "assumption, velocity #16"),
    "drive": P(1000, 5000, 20000, "assumption, velocity #16"),
    "servo_drive": P(2000, 5000, 12000, "assumption, velocity #16"),
    "hmi": P(1000, 4000, 8000, "assumption, velocity #16"),
}
UNIT_COST_DEFAULT = P(500, 2000, 5000, "assumption, velocity #16")

# --- part valuation
USABLE_CONDITIONS = ("new", "new_surplus", "refurbished")   # what a plant would actually install
HIGH_CONFIDENCE_LISTINGS = 3                                # registry-format §7
MIN_TRUST = 0.35           # listings below this are flagged (n_low_trust) and kept out of the price range

# --- plant savings (per plant per year)
EXCESS_SPARES_PCT = P(0.10, 0.15, 0.25, "vendor 15-60%, conservative range (model-spec §3)")
RUSH_SHARE_AVOIDED = P(0.10, 0.20, 0.30, "assumption, velocity #3")
MACHINES_PER_EMPLOYEE = P(0.4, 0.55, 0.7, "assumption, velocity #18 (~150 machines at a ~250-person plant)")

# --- discount rates (velocity #15)
OWNER_DISCOUNT_RATE = P(0.08, 0.10, 0.12, "assumption, velocity #15")
DEAL_DISCOUNT_RATE = P(0.20, 0.25, 0.30, "estimate, velocity #15 (Nov 14): PE hurdle ~25%")

# --- price + price checks (velocity #6, #7, #18, #19)
VALUE_CAPTURE_PCT = P(0.10, 0.20, 0.30, "estimate, velocity #6 (Nov 14)")
MIN_CUSTOMER_ROI = 3.0
MAX_PAYBACK_MONTHS = 12
APPROVAL_CEILING = P(10000, 17500, 25000, "assumption, velocity #19 (plant-manager quick-yes zone)")
COMPARABLES = P(6000, 8000, 10000, "assumption, velocity #7 (distributor installed-base evaluation)")
COMPARABLE_BAND = (0.5, 2.0)   # flag a price below 0.5x the low or above 2x the high comparable
COST_TO_SERVE = P(350, 1100, 3850, "assumption, velocity #18 (API + 4-12 h review, + on-site capture at high)")
MIN_GROSS_MARGIN = 0.60
MAX_DEAL_FEE_SHARE = 0.10      # deal fee should be <= 10% of what the scan finds (model-spec §2 check 4)
