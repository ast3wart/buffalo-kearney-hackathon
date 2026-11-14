"""Linking engine. Owner: Role A. Milestone M2.

Output: links.csv (source_table, source_id, part_no, method, confidence).
Strategy: docs/build/architecture.md ("How the claim matching works").
"""
import pandas as pd

ABBREVIATIONS = {  # expand before fuzzy matching; grow this list from the data
    "BRG": "BEARING", "HYD": "HYDRAULIC", "CYL": "CYLINDER", "REPL": "REPLACED",
    "ASSY": "ASSEMBLY", "FLTR": "FILTER", "GSKT": "GASKET",
}


def normalize(text: str) -> str:
    """Uppercase, split punctuation, expand abbreviations."""
    raise NotImplementedError  # TODO(A)


def link_spend(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """production_spend + service_spend lines -> part_no."""
    raise NotImplementedError  # TODO(A)


def link_claims(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """warranty_claims -> causal part_no via causal_part_no / failure code + BOM / fuzzy text."""
    raise NotImplementedError  # TODO(A)


def link_all(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat([link_spend(tables), link_claims(tables)], ignore_index=True)
