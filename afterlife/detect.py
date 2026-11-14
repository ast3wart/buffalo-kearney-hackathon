"""Early-warning spike detection. [WARRANTY thread · Brandon] Milestone M4.

Pool claims across ALL products sharing a part. Two views (decided at CP0):
  raw  : claims per 1,000 built by build_month (intuitive chart, biased toward recent builds)
  mis  : claims within MIS_WINDOW months in service per 1,000 built, MATURE build months only
         (build_month + MIS_WINDOW <= data_as_of). Alerts use THIS view.
         v4: claims arrive with a reporting lag (claim_date - failure_date). Count by claim_date <= data_as_of
         (that's all we can see), and treat a build month as mature only once build_month + MIS_WINDOW
         + typical lag (e.g. the 90th percentile lag in the data) <= data_as_of, or the latest months look falsely clean.
Flag mis rate / baseline >= RATIO_MIN with >= MIN_CLAIMS.

v3 #13 supplier attribution: claims don't say which supplier's part was fitted. Use build_supply:
exposure for (part, supplier) = sum(units_built x qty_per x share). Compare rates where a supplier's
share is high vs low (cells with a single supplier are clean; mixed cells = "ambiguous").
The alert should name the supplier and the first affected PO line (lot).
Output columns: see alerts.csv in docs/build/data-contract.md.
"""
import pandas as pd

RATIO_MIN = 2.0
MIN_CLAIMS = 10
MIS_WINDOW = 3  # dataset_info.mis_window


def claim_rates(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """-> part_no, supplier_id, build_month, units_built, raw_claims, raw_rate, mis_claims, mis_rate, mature"""
    raise NotImplementedError  # TODO(WARRANTY)


def find_spikes(rates: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(WARRANTY)
