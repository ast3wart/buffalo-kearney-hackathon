"""[SPEND thread] production_spend + service_spend lines -> part_no.

Suggested order: supplier PN crosswalk -> spec codes in text (e.g. 6204, M20X1.5) ->
fuzzy description (rapidfuzz) within category. Convert UoM so prices compare per EA.
"""
import pandas as pd
from afterlife.match import normalize  # noqa: F401


def link_spend(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(SPEND)
