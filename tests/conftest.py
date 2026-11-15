"""Build `reg` from the hand-made sample (data/seed/sample) the way Asher's seed.py does, minus SQLite.
The matcher isn't under test here, so component.kb_id and spare_match come from the answer key."""
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
SAMPLE, TRUTH = ROOT / "data/seed/sample", ROOT / "data/truth/sample"


def _csv(p: Path, text: bool = True) -> pd.DataFrame:
    return pd.read_csv(p, dtype=str).fillna("") if text else pd.read_csv(p)


def load_sample() -> dict[str, pd.DataFrame]:
    plants = _csv(SAMPLE / "plants.csv")
    per = {"machine": "assets.csv", "spare_stock": "spares.csv", "reading": "readings.csv"}
    t = {k: pd.concat([_csv(SAMPLE / p / f) for p in plants.plant_id], ignore_index=True) for k, f in per.items()}
    portfolio = _csv(SAMPLE / "portfolio.csv")
    kb = _csv(SAMPLE / "reference/kb.csv")
    truth = _csv(TRUTH / "components.csv")
    r = t["reading"].merge(truth[["component_id", "kb_id"]], on="component_id", how="left")
    t["component"] = pd.DataFrame({
        "component_id": r.component_id, "machine_id": r.machine_id, "kb_id": r.kb_id.fillna(""),
        "part_no_read": r.raw_text, "component_type": r.component_type_hint, "date_code": r.date_code,
        "confidence": r.confidence.astype(float), "method": r.method, "needs_review": "no", "review_reason": "",
        "evidence_id": ""})
    t["spare_match"] = _csv(TRUTH / "spare_matches.csv").assign(confidence=1.0)
    t.update({
        "fund": portfolio.loc[portfolio.fund_id != "", ["fund_id", "fund_name"]].drop_duplicates(),
        "company": portfolio[["company_id", "fund_id", "company_name", "owned_since", "deal_value_low", "deal_value_high"]],
        "plant": plants,
        "plant_financials": _csv(SAMPLE / "plant_financials.csv", text=False),
        "line": _csv(SAMPLE / "lines.csv", text=False),
        "kb_entry": kb,
        "alternative": _csv(SAMPLE / "reference/alternatives.csv"),
        "listing": _csv(ROOT / "data/reference/listings.csv"),
    })
    return t


@pytest.fixture(scope="session")
def reg():
    return load_sample()
