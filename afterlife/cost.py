"""Build vs lifecycle cost per product. Owner: Role B. Milestone M5."""
import pandas as pd


def build_cost(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """sum(qty_per * avg production unit price, after UoM conversion) per product."""
    raise NotImplementedError  # TODO(B)


def lifecycle_cost(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """build cost + (spares + warranty spend per unit built) per product."""
    raise NotImplementedError  # TODO(B)


def spare_markups(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """Same part: service unit price / production unit price."""
    raise NotImplementedError  # TODO(B)
