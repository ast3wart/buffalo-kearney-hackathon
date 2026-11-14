"""Shared loader. Owner: shared. Formats: docs/build/data-contract.md"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample"
GENERATED = ROOT / "data" / "generated"

TABLES = [
    "products", "part_master", "bom", "builds", "production_spend",
    "service_spend", "failure_codes", "warranty_claims",
    "truth_links", "truth_spikes",
]


def data_dir(prefer_generated: bool = True) -> Path:
    """Use data/generated/ if it has files, else fall back to data/sample/."""
    if prefer_generated and (GENERATED / "warranty_claims.csv").exists():
        return GENERATED
    return SAMPLE


def load(directory: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load every contract table that exists in `directory` as strings-safe DataFrames."""
    d = directory or data_dir()
    out = {}
    for t in TABLES:
        p = d / f"{t}.csv"
        if p.exists():
            out[t] = pd.read_csv(p, keep_default_na=False, na_values=[""])
    return out
