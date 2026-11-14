"""Afterlife API. Thin read layer over results.duckdb (+ live /brief later).

    uvicorn api.main:app --reload --port 8000
    docs: http://localhost:8000/docs   spec: /openapi.json (feeds web/ types)

Endpoint owners: see docs/team/roles.md. Keep handlers thin: logic lives in afterlife/.
"""
from contextlib import contextmanager
import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from afterlife.run import DB_PATH

app = FastAPI(title="Afterlife API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@contextmanager
def db():
    if not DB_PATH.exists():
        raise HTTPException(503, "results.duckdb missing. Run: python -m afterlife.run")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        yield con
    finally:
        con.close()


class TableCount(BaseModel):
    name: str
    rows: int


class Health(BaseModel):
    ok: bool
    source: str
    run_at: str
    tables: list[TableCount]


@app.get("/health", response_model=Health)
def health() -> Health:
    with db() as con:
        source, run_at = con.execute("SELECT source, CAST(run_at AS VARCHAR) FROM meta").fetchone()
        names = [r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_name <> 'meta' ORDER BY 1").fetchall()]
        tables = [TableCount(name=n, rows=con.execute(f'SELECT count(*) FROM "{n}"').fetchone()[0]) for n in names]
    return Health(ok=True, source=source, run_at=run_at, tables=tables)


# ---- Planned endpoints (see docs/build/api.md). Owners fill these in. ----
# GET  /overview            spend thread : coverage + build vs lifecycle cost per product
# GET  /links?source=&q=    both         : linking explorer rows
# GET  /markups             spend thread : spare vs production price per part
# GET  /alerts              warranty     : spike alerts
# GET  /claim-rates/{part}  warranty     : rate by build month for the chart
# POST /brief/{supplier_id} both         : streams the supplier brief (Claude API, template fallback)
