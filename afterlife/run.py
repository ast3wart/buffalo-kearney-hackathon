"""Run the whole pipeline once and save everything to results.duckdb.

    python -m afterlife.run            # uses data/generated/ if present, else data/sample/

The API only READS results.duckdb, so the demo never runs heavy work live.
Steps that aren't built yet are skipped with a message, so this works from hour 0.
"""
from pathlib import Path
import duckdb
import pandas as pd
from afterlife.io import ROOT, data_dir, load

DB_PATH = ROOT / "results.duckdb"


def _try(name, fn, *args):
    try:
        out = fn(*args)
        print(f"  ✓ {name}: {len(out)} rows")
        return out
    except NotImplementedError:
        print(f"  · {name}: not built yet, skipped")
        return None


def run(db_path: Path = DB_PATH) -> None:
    from afterlife import match, detect, cost
    src = data_dir()
    print(f"source: {src}")
    tables = load(src)
    outputs: dict[str, pd.DataFrame | None] = {}

    links = _try("links", match.link_all, tables)
    outputs["links"] = links
    if links is not None:
        rates = _try("claim_rates", detect.claim_rates, tables, links)
        outputs["claim_rates"] = rates
        if rates is not None:
            outputs["alerts"] = _try("alerts", detect.find_spikes, rates, tables)
        outputs["lifecycle_cost"] = _try("lifecycle_cost", cost.lifecycle_cost, tables, links)
        outputs["spare_markups"] = _try("spare_markups", cost.spare_markups, tables, links)

    con = duckdb.connect(str(db_path))
    for name, df in {**tables, **{k: v for k, v in outputs.items() if v is not None}}.items():
        con.register("tmp", df)
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM tmp")
        con.unregister("tmp")
    con.execute("CREATE OR REPLACE TABLE meta AS SELECT ? AS source, now() AS run_at", [str(src.relative_to(ROOT))])
    con.close()
    print(f"wrote {db_path}")


if __name__ == "__main__":
    run()
