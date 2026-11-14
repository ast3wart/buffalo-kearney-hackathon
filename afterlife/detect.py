"""Early-warning spike detection. Owner: Role B. Milestone M4.

Pool claims across ALL products sharing a part; rate = claims per 1,000 units built
by build_month. Flag rate / baseline >= RATIO_MIN with >= MIN_CLAIMS.
Output columns: see alerts.csv in docs/build/data-contract.md.
"""
import pandas as pd

RATIO_MIN = 2.0
MIN_CLAIMS = 10


def claim_rates(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """-> part_no, supplier_id, build_month, claims, units_built, rate_per_1000"""
    raise NotImplementedError  # TODO(B)


def find_spikes(rates: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(B)
