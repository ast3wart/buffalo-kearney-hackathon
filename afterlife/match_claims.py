"""[WARRANTY thread] warranty_claims -> causal part_no.

1. causal_part_no present AND in that product's BOM -> accept (high confidence)
2. else candidates = that product's BOM parts whose category is in failure code's likely_categories
3. rank candidates by fuzzy(normalize(claim_text), normalize(part description))
4. one clear winner -> high confidence; close call -> low (LLM tie-break = stretch)
"""
import pandas as pd
from afterlife.match import normalize  # noqa: F401


def link_claims(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(WARRANTY)
