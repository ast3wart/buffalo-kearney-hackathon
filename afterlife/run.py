"""Run the whole pipeline for EVERY company and save everything to results.duckdb.

    python -m afterlife.run            # all companies in data/generated/, else data/sample/

Every table gets a `company_id` column, so the API filters with ?company=<id>.
The API only READS results.duckdb, so the demo never runs heavy work live.
Steps that aren't built yet are skipped with a message, so this works from hour 0.
"""
import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
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
    from afterlife import match, detect, cost, extract_terms
    outputs: dict[str, pd.DataFrame | None] = {"links": _try("links", match.link_all, tables)}
    if "supplier_agreements" in tables:
        outputs["supplier_terms"] = _try("supplier_terms", extract_terms.extract_terms, tables)
    links = outputs["links"]
    if links is not None:
        has_claims = "warranty_claims" in tables and len(tables["warranty_claims"]) > 0
        if has_claims:   # spend-only companies (claims generator not built yet) skip detection
            rates = _try("claim_rates", detect.claim_rates, tables, links)
            outputs["claim_rates"] = rates
            if rates is not None:
                outputs["alerts"] = _try("alerts", detect.find_spikes, rates, tables)
        outputs["lifecycle_cost"] = _try("lifecycle_cost", cost.lifecycle_cost, tables, links)
        outputs["spare_markups"] = _try("spare_markups", cost.spare_markups, tables, links)
        outputs["price_harmonization"] = _try("price_harmonization", cost.price_harmonization, tables, links)
    return {k: v for k, v in outputs.items() if v is not None}


def _git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def _hash_inputs(folders: list[Path]) -> dict[str, str]:
    out = {}
    for d in folders:
        h = hashlib.sha256()
        for f in sorted(d.glob("*.csv")):
            h.update(f.name.encode()); h.update(f.read_bytes())
        out[str(d.relative_to(ROOT))] = h.hexdigest()[:12]
    return out


def run(db_path: Path = DB_PATH) -> None:
    """v3 #17: every run gets a run_id recorded in the `runs` table, so any number traces back to
    the code commit, inputs and model settings that produced it."""
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    os.environ["AFTERLIFE_RUN_ID"] = run_id  # matchers write this into links.run_id
    combined: dict[str, list[pd.DataFrame]] = {}
    company_rows = []
    for cid, folder in companies(require_claims=False):
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
    con.execute("CREATE OR REPLACE TABLE meta AS SELECT now() AS run_at, ? AS run_id", [run_id])
    con.execute("""CREATE TABLE IF NOT EXISTS runs (run_id VARCHAR, started_at TIMESTAMP, git_commit VARCHAR,
                   input_hashes VARCHAR, model_id VARCHAR, prompt_version VARCHAR, metrics_json VARCHAR)""")
    con.execute("INSERT INTO runs VALUES (?, now(), ?, ?, ?, ?, ?)", [
        run_id, _git_commit(), json.dumps(_hash_inputs([d for _, d in companies(require_claims=False)])),
        os.environ.get("AFTERLIFE_LLM_MODEL", ""), os.environ.get("AFTERLIFE_PROMPT_VERSION", ""), "{}"])
    con.close()
    print(f"wrote {db_path} ({len(company_rows)} companies)")


if __name__ == "__main__":
    run()
