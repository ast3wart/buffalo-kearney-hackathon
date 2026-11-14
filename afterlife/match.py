"""Linking engine (orchestrator + shared text helpers). Milestone M2.

  match_spend.py  [SPEND]    purchase lines -> part_no
  match_claims.py [WARRANTY] claims -> causal part_no
Output: links with taxonomy.LINK_COLUMNS
  (source_table, source_id, part_no, method, confidence, source_system, evidence, run_id).
`evidence` is a JSON string of the signals that agreed, e.g.
  {"spec_code": "6204", "category": "bearing", "info_record": false, "fuzzy": 0.91}

v3 #10/#11: abbreviations come from each company's abbreviations.csv (client data, not code),
and nothing in the matching code may mention a specific company, part or supplier
(tests/test_no_literals.py).
"""
import re
import pandas as pd


def abbreviation_map(tables: dict[str, pd.DataFrame]) -> dict[str, str]:
    """This company's shorthand -> expansion, from abbreviations.csv."""
    ab = tables.get("abbreviations")
    if ab is None or ab.empty:
        return {}
    return {str(a).upper(): str(e).upper() for a, e in zip(ab.abbr, ab.expansion)}


def normalize(text: str, abbreviations: dict[str, str]) -> str:
    """Uppercase, split on punctuation, expand this company's abbreviations. Shared by both matchers."""
    tokens = re.split(r"[^A-Z0-9.]+", str(text).upper())
    return " ".join(abbreviations.get(t, t) for t in tokens if t)


def link_all(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    from afterlife.match_spend import link_spend
    from afterlife.match_claims import link_claims
    parts = [link_spend(tables)]
    try:   # until match_claims exists, still return the spend links (cost.py / evaluate need them)
        parts.append(link_claims(tables))
    except NotImplementedError:
        pass
    return pd.concat(parts, ignore_index=True)
