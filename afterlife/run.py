"""Run the whole pipeline for EVERY company and save everything to results.duckdb.

    python -m afterlife.run            # all companies in data/generated/, else data/sample/

Every table gets a `company_id` column, so the API filters with ?company=<id>.
The API only READS results.duckdb, so the demo never runs heavy work live.
Steps that aren't built yet are skipped with a message, so this works from hour 0.
"""
from pathlib import Path
import duckdb
import pandas as pd
from afterlife.io import ROOT, companies, load

DB_PATH = ROOT / "results.duckdb"


def _try(name, fn, *args):
    try:
        out = fn(*args)
        print(f"    ✓ {name}: {len(out)} rows")
        return out
    except NotImplementedError:
        print(f"    · {name}: not built yet, skipped")
        return None


def run_company(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    from afterlife import match, detect, cost
    outputs: dict[str, pd.DataFrame | None] = {"links": _try("links", match.link_all, tables)}
    links = outputs["links"]
    if links is not None:
        rates = _try("claim_rates", detect.claim_rates, tables, links)
        outputs["claim_rates"] = rates
        if rates is not None:
            outputs["alerts"] = _try("alerts", detect.find_spikes, rates, tables)
        outputs["lifecycle_cost"] = _try("lifecycle_cost", cost.lifecycle_cost, tables, links)
        outputs["spare_markups"] = _try("spare_markups", cost.spare_markups, tables, links)
    return {k: v for k, v in outputs.items() if v is not None}


def run(db_path: Path = DB_PATH) -> None:
    combined: dict[str, list[pd.DataFrame]] = {}
    company_rows = []
    for cid, folder in companies():
        print(f"  {cid}  ({folder.relative_to(ROOT)})")
        tables = load(folder)
        info = dict(zip(tables["dataset_info"].key, tables["dataset_info"].value)) if "dataset_info" in tables else {}
        company_rows.append({"company_id": cid, "company_name": info.get("company_name", cid),
                             "industry": info.get("industry", ""), "data_as_of": info.get("data_as_of", ""),
                             "source": str(folder.relative_to(ROOT))})
        for name, df in {**tables, **run_company(tables)}.items():
            combined.setdefault(name, []).append(df.assign(company_id=cid))

    con = duckdb.connect(str(db_path))
    for name, dfs in combined.items():
        con.register("tmp", pd.concat(dfs, ignore_index=True))
        con.execute(f'CREATE OR REPLACE TABLE "{name}" AS SELECT * FROM tmp')
        con.unregister("tmp")
    con.register("tmp", pd.DataFrame(company_rows))
    con.execute("CREATE OR REPLACE TABLE companies AS SELECT * FROM tmp")
    con.unregister("tmp")
    con.execute("CREATE OR REPLACE TABLE meta AS SELECT now() AS run_at")
    con.close()
    print(f"wrote {db_path} ({len(company_rows)} companies)")


if __name__ == "__main__":
    run()
