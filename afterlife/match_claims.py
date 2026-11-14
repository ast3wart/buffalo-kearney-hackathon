"""[WARRANTY thread · Brandon] warranty_claims -> causal part_no.

1. causal_part_no present AND in that product's BOM -> accept (high confidence)
2. else candidates = that product's BOM parts whose category is in failure code's likely_categories
3. rank candidates by fuzzy(normalize(claim_text), normalize(part description))
4. one clear winner -> high confidence; close call -> low (LLM tie-break = Tier 2, method "llm")
Output columns: taxonomy.LINK_COLUMNS, with evidence JSON (failure_code, category_match, fuzzy score, ...).
"""
import pandas as pd
from afterlife.match import normalize, abbreviation_map  # noqa: F401


def link_claims(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(WARRANTY)
