"""Seed files -> SQLite registry.   python scripts/seed.py [data/seed/demo] [demo.db]

Loads the export-style plant files + reference data (registry-format.md), runs the matching pipeline
(readings -> components, storeroom text -> KB), and writes every table to SQLite.
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from xray.pipeline import build_components, match_spares  # noqa: E402


def main(seed_dir: Path, db_path: Path) -> dict[str, pd.DataFrame]:
    ref = ROOT / "data/reference"
    kb = pd.read_csv(ref / "kb.csv", dtype=str).fillna("")
    abbr = {a.upper(): e.upper() for a, e in pd.read_csv(ref / "abbreviations.csv", dtype=str).itertuples(index=False)}
    plants = pd.read_csv(seed_dir / "plants.csv", dtype={"plant_id": str})
    per = {"machine": "assets.csv", "spare_stock": "spares.csv", "reading": "readings.csv", "photo": "photos.csv"}
    parts = {t: [] for t in per}
    for pid in plants.plant_id:
        for t, f in per.items():
            p = seed_dir / pid / f
            if p.exists():
                parts[t].append(pd.read_csv(p, dtype=str).fillna(""))
    tables = {t: pd.concat(v, ignore_index=True) if v else pd.DataFrame() for t, v in parts.items()}
    portfolio = pd.read_csv(seed_dir / "portfolio.csv", dtype=str).fillna("")
    tables.update({
        "fund": portfolio.loc[portfolio.fund_id != "", ["fund_id", "fund_name"]].drop_duplicates(),
        "company": portfolio[["company_id", "fund_id", "company_name", "owned_since", "deal_value_low", "deal_value_high"]],
        "plant": plants,
        "plant_financials": pd.read_csv(seed_dir / "plant_financials.csv"),
        "line": pd.read_csv(seed_dir / "lines.csv"),
        "kb_entry": kb,
        "alternative": pd.read_csv(ref / "alternatives.csv", dtype=str).fillna("") if (ref / "alternatives.csv").exists() else pd.DataFrame(),
        "listing": pd.read_csv(ref / "listings.csv", dtype=str).fillna("") if (ref / "listings.csv").exists() else pd.DataFrame(),
    })
    tables["component"], tables["evidence"] = build_components(tables["reading"], kb, abbr)
    tables["spare_match"] = match_spares(tables["spare_stock"], kb, abbr)
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(str(db_path)) as con:
        for name, df in tables.items():
            if len(df.columns):
                df.to_sql(name, con, index=False)
    print(f"{db_path.name}: " + ", ".join(f"{k} {len(v)}" for k, v in tables.items() if len(v.columns)))
    return tables


if __name__ == "__main__":
    seed = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/seed/demo"
    db = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "demo.db"
    main(seed, db)
