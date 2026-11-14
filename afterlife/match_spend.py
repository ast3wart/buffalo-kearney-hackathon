"""[SPEND thread · Asher] production_spend + service_spend lines -> part_no.

Order (v3 methods): exact_pn (part_no present + in part_master) -> info_record (supplier_pn via
info_records) -> spec_code (codes like 6204 / M20X1.5 in the text) -> fuzzy_text (rapidfuzz within
category). Fill source_system (e.g. from plant), evidence (JSON of the signals) and run_id.
Convert price_unit + UoM so prices compare per EA. Hard cases: service text items and acquired-plant lines.
"""
import pandas as pd
from afterlife.match import normalize, abbreviation_map  # noqa: F401


def link_spend(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(SPEND)
