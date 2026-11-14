"""Linking engine (orchestrator + shared text helpers). Milestone M2.

  match_spend.py  [SPEND]    purchase lines -> part_no
  match_claims.py [WARRANTY] claims -> causal part_no
Output: links (source_table, source_id, part_no, method, confidence).
"""
import re
import pandas as pd

ABBREVIATIONS = {  # shared: both threads grow this list
    "BRG": "BEARING", "HYD": "HYDRAULIC", "CYL": "CYLINDER", "REPL": "REPLACED",
    "ASSY": "ASSEMBLY", "FLTR": "FILTER", "GSKT": "GASKET", "IGN": "IGNITION", "FRT": "FRONT",
}


def normalize(text: str) -> str:
    """Uppercase, split on punctuation, expand abbreviations. Shared by both matchers."""
    tokens = re.split(r"[^A-Z0-9.]+", str(text).upper())
    return " ".join(ABBREVIATIONS.get(t, t) for t in tokens if t)


def link_all(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    from afterlife.match_spend import link_spend
    from afterlife.match_claims import link_claims
    return pd.concat([link_spend(tables), link_claims(tables)], ignore_index=True)
