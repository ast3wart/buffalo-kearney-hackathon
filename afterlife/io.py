"""Shared loader. Owner: shared. Formats: docs/build/data-contract.md"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample"
GENERATED = ROOT / "data" / "generated"

TABLES = [
    "products", "part_master", "bom", "builds", "production_spend",
    "service_spend", "info_records", "build_supply", "abbreviations", "failure_codes",
    "warranty_claims", "dataset_info", "truth_links", "truth_spikes", "truth_terms",
]
DOCS = "supplier_agreements"  # v4: folder of contract documents (text), not a CSV


def companies(prefer_generated: bool = True) -> list[tuple[str, Path]]:
    """[(company_id, folder)] for every company in data/generated/<company_id>/.
    Falls back to [("sample", data/sample/)] until the generator has run."""
    if prefer_generated and GENERATED.exists():
        found = sorted((d.name, d) for d in GENERATED.iterdir() if (d / "warranty_claims.csv").exists())
        if found:
            return found
    return [("sample", SAMPLE)]


def data_dir(prefer_generated: bool = True) -> Path:
    """First company's folder (convenience for quick scripts)."""
    return companies(prefer_generated)[0][1]


def load(directory: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load every contract table that exists in `directory` as strings-safe DataFrames."""
    d = directory or data_dir()
    out = {}
    from afterlife.adapters import sap
    for t in TABLES:
        p = d / f"{t}.csv"
        if p.exists():
            df = pd.read_csv(p, keep_default_na=False, na_values=[""], dtype=str if t in sap.MAPS else None)
            if t in sap.MAPS:
                df = sap.to_contract(t, df) if sap.looks_like_sap(df) else df
                for col in ["qty", "unit_price", "price_unit", "std_cost"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
            out[t] = df
    docs = load_documents(d)
    if len(docs):
        out[DOCS] = docs
    return out


def load_documents(directory: Path) -> pd.DataFrame:
    """v4: supplier agreements as [doc_file, text]. Which supplier a document belongs to, and its
    recovery terms, are EXTRACTED from the text (afterlife/extract_terms.py), never read from the file name.
    Real clients send PDFs; convert to .md/.txt first (out of scope for the MVP)."""
    files = sorted(p for p in (directory / DOCS).glob("*") if p.suffix in (".md", ".txt"))
    return pd.DataFrame({"doc_file": [p.name for p in files], "text": [p.read_text() for p in files]},
                        columns=["doc_file", "text"])
