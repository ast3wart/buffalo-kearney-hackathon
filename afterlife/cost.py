"""Build vs lifecycle cost per product. [SPEND thread · Asher] Milestone M5."""
import pandas as pd


def build_cost(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """sum(qty_per * avg production unit price, after UoM conversion) per product."""
    raise NotImplementedError  # TODO(SPEND)


def lifecycle_cost(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """build cost + (spares + warranty spend per unit built) per product.

    Double-count rule (21b, data-contract.md "Cost rules"): warranty = claims parts_cost + labor_cost + other_cost (v4);
    service_spend channel == "warranty_repair" is reconciliation only (NEVER added); only channel == "spares"
    is added as spare cost. Also report warranty as a % of revenue (units_built x products.avg_selling_price)."""
    raise NotImplementedError  # TODO(SPEND)


def spare_markups(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """Same part: service unit price / production unit price."""
    raise NotImplementedError  # TODO(SPEND)
