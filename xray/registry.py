"""Load the registry (SQLite) as a dict of DataFrames: the `reg` that Brandon's functions take (interfaces.md §1)."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "demo.db"


def load(db_path: str | Path = DEFAULT_DB) -> dict[str, pd.DataFrame]:
    with sqlite3.connect(str(db_path)) as con:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {n: pd.read_sql(f'SELECT * FROM "{n}"', con) for n in names}
