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


class Company(BaseModel):
    company_id: str
    company_name: str
    industry: str
    data_as_of: str


class Health(BaseModel):
    ok: bool
    run_at: str
    companies: list[Company]
    tables: list[TableCount]


def _companies(con) -> list[Company]:
    rows = con.execute("SELECT company_id, company_name, industry, data_as_of FROM companies ORDER BY company_id").fetchall()
    return [Company(company_id=a, company_name=b, industry=c, data_as_of=d) for a, b, c, d in rows]


@app.get("/companies", response_model=list[Company])
def list_companies() -> list[Company]:
    with db() as con:
        return _companies(con)


@app.get("/health", response_model=Health)
def health() -> Health:
    with db() as con:
        run_at = con.execute("SELECT CAST(run_at AS VARCHAR) FROM meta").fetchone()[0]
        names = [r[0] for r in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name NOT IN ('meta','companies','runs') ORDER BY 1").fetchall()]
        tables = [TableCount(name=n, rows=con.execute(f'SELECT count(*) FROM "{n}"').fetchone()[0]) for n in names]
        return Health(ok=True, run_at=run_at, companies=_companies(con), tables=tables)


# ---- 💲 Spend thread: overview, markups, harmonization -------------------------------------------------
from fastapi import Query  # noqa: E402

HIGH_CONF = 0.8   # links used for savings $ (cost.CONF_MIN); 99.9-100% correct on unseen companies


def _has_table(con, name: str) -> bool:
    return bool(con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [name]).fetchone()[0])


def _company_or_404(con, company: str) -> Company:
    for c in _companies(con):
        if c.company_id == company:
            return c
    raise HTTPException(404, f"unknown company '{company}'. See GET /companies")


class Coverage(BaseModel):
    production_spend_pct: float          # share of production lines linked to a part
    service_spend_pct: float             # share of service lines linked to a part
    production_high_conf_pct: float      # ... with confidence >= 0.8 (usable for savings $)
    service_high_conf_pct: float
    claims_pct: float | None = None      # None until claims are generated and linked


class ProductCost(BaseModel):
    product_id: str
    product_name: str
    units_built: int
    revenue: float
    build_cost: float
    spares_per_unit: float
    warranty_per_unit: float
    lifecycle_cost: float
    warranty_pct_revenue: float


class Overview(BaseModel):
    company_id: str
    company: str
    industry: str
    data_as_of: str
    coverage: Coverage
    products: list[ProductCost]
    spare_overspend_usd: float
    spare_overspend_usd_per_year: float
    harmonization_usd: float
    acquired_plant_harmonization_usd: float   # part of harmonization_usd paid at non-main plants
    warranty_pct_revenue: float               # whole company; 0 until claims exist
    has_claims: bool
    contract_leakage_usd: float = 0.0         # production paid above the supplier's own contract price
    contract_leakage_lines: int = 0
    spares_clause_gap_usd: float = 0.0        # spares bought above series price despite a "spares at series price" clause
    agreements_read: int = 0                  # supplier agreement documents the prices were extracted from


def _pct(con, table: str, company: str, high: bool) -> float:
    if not _has_table(con, table) or not _has_table(con, "links"):
        return 0.0
    conf = f"AND l.confidence >= {HIGH_CONF}" if high else ""
    total, linked = con.execute(f"""
        SELECT count(*), count(l.source_id) FROM "{table}" s
        LEFT JOIN links l ON l.company_id = s.company_id AND l.source_table = '{table}'
             AND l.source_id = CAST(s.po_line_id AS VARCHAR) {conf}
        WHERE s.company_id = ?""", [company]).fetchone()
    return round(linked / total, 4) if total else 0.0


@app.get("/overview", response_model=Overview)
def overview(company: str = Query(..., description="company_id from GET /companies")) -> Overview:
    """💲 Coverage, build vs lifecycle cost per product, and the headline savings figures."""
    with db() as con:
        c = _company_or_404(con, company)
        has_claims = _has_table(con, "warranty_claims") and con.execute(
            "SELECT count(*) FROM warranty_claims WHERE company_id = ?", [company]).fetchone()[0] > 0
        claims_pct = None
        if has_claims and _has_table(con, "links"):
            n, k = con.execute("""SELECT count(*), count(l.source_id) FROM warranty_claims w
                LEFT JOIN links l ON l.company_id = w.company_id AND l.source_table = 'warranty_claims'
                     AND l.source_id = w.claim_id WHERE w.company_id = ?""", [company]).fetchone()
            claims_pct = round(k / n, 4) if n else None
        cov = Coverage(production_spend_pct=_pct(con, "production_spend", company, False),
                       service_spend_pct=_pct(con, "service_spend", company, False),
                       production_high_conf_pct=_pct(con, "production_spend", company, True),
                       service_high_conf_pct=_pct(con, "service_spend", company, True),
                       claims_pct=claims_pct)
        products = []
        if _has_table(con, "lifecycle_cost"):
            rows = con.execute("""SELECT l.product_id, p.product_name, l.units_built, l.revenue, l.build_cost,
                       l.spares_per_unit, l.warranty_per_unit, l.lifecycle_cost, l.warranty_pct_revenue
                FROM lifecycle_cost l JOIN products p ON p.company_id = l.company_id AND p.product_id = l.product_id
                WHERE l.company_id = ? ORDER BY l.product_id""", [company]).fetchall()
            products = [ProductCost(product_id=r[0], product_name=r[1], units_built=int(r[2]), revenue=r[3],
                                    build_cost=r[4], spares_per_unit=r[5], warranty_per_unit=r[6],
                                    lifecycle_cost=r[7], warranty_pct_revenue=r[8]) for r in rows]
        over = over_y = 0.0
        if _has_table(con, "spare_markups"):
            over, over_y = con.execute("""SELECT coalesce(sum(overspend_usd), 0), coalesce(sum(overspend_usd_per_year), 0)
                FROM spare_markups WHERE company_id = ?""", [company]).fetchone()
        harm = harm_acq = 0.0
        if _has_table(con, "price_harmonization"):
            harm, harm_acq = con.execute("""SELECT coalesce(sum(savings_usd), 0),
                       coalesce(sum(savings_usd) FILTER (WHERE plant <> (
                           SELECT plant FROM production_spend WHERE company_id = ? GROUP BY plant ORDER BY count(*) DESC LIMIT 1)), 0)
                FROM price_harmonization WHERE company_id = ?""", [company, company]).fetchone()
        leak = leak_n = clause = 0.0
        if _has_table(con, "contract_compliance"):
            leak, leak_n, clause = con.execute("""SELECT
                    coalesce(sum(gap_usd) FILTER (WHERE finding = 'price_leakage'), 0),
                    count(*) FILTER (WHERE finding = 'price_leakage'),
                    coalesce(sum(gap_usd) FILTER (WHERE finding = 'spares_clause'), 0)
                FROM contract_compliance WHERE company_id = ?""", [company]).fetchone()
        docs = 0
        if _has_table(con, "contract_prices"):
            docs = con.execute("SELECT count(DISTINCT doc_file) FROM contract_prices WHERE company_id = ?", [company]).fetchone()[0]
        rev = sum(p.revenue for p in products)
        warr = sum(p.warranty_pct_revenue * p.revenue / 100 for p in products)
        return Overview(company_id=c.company_id, company=c.company_name, industry=c.industry, data_as_of=c.data_as_of,
                        coverage=cov, products=products, spare_overspend_usd=round(over, 2),
                        spare_overspend_usd_per_year=round(over_y, 2), harmonization_usd=round(harm, 2),
                        acquired_plant_harmonization_usd=round(harm_acq, 2),
                        warranty_pct_revenue=round(100 * warr / rev, 3) if rev else 0.0, has_claims=has_claims,
                        contract_leakage_usd=round(leak, 2), contract_leakage_lines=int(leak_n),
                        spares_clause_gap_usd=round(clause, 2), agreements_read=int(docs))


class Markup(BaseModel):
    part_no: str
    description: str
    prod_price_ea: float
    svc_price_ea: float
    ratio: float
    svc_qty_ea: float
    overspend_usd: float
    overspend_usd_per_year: float


@app.get("/markups", response_model=list[Markup])
def markups(company: str = Query(...), limit: int = Query(25, ge=1, le=1000)) -> list[Markup]:
    """💲 Same part, service price vs production price (high-confidence links only), biggest overspend first."""
    with db() as con:
        _company_or_404(con, company)
        if not _has_table(con, "spare_markups"):
            return []
        cols = list(Markup.model_fields)
        rows = con.execute(f"""SELECT {", ".join(cols)} FROM spare_markups WHERE company_id = ?
                               ORDER BY overspend_usd DESC LIMIT ?""", [company, limit]).fetchall()
        return [Markup(**dict(zip(cols, r))) for r in rows]


class Harmonization(BaseModel):
    part_no: str
    description: str
    supplier_id: str
    supplier_name: str
    plant: str
    price_ea: float
    best_price_ea: float
    qty_ea: float
    savings_usd: float


@app.get("/harmonization", response_model=list[Harmonization])
def harmonization(company: str = Query(...), limit: int = Query(25, ge=1, le=1000)) -> list[Harmonization]:
    """💲 Production lines paid above the best supplier x plant price for the same part."""
    with db() as con:
        _company_or_404(con, company)
        if not _has_table(con, "price_harmonization"):
            return []
        rows = con.execute("""
            SELECT h.part_no, coalesce(pm.description, ''), CAST(h.supplier_id AS VARCHAR),
                   coalesce((SELECT any_value(supplier_name) FROM production_spend ps WHERE ps.company_id = h.company_id
                             AND CAST(ps.supplier_id AS VARCHAR) = CAST(h.supplier_id AS VARCHAR)), ''),
                   h.plant, h.price_ea, h.best_price_ea, h.qty_ea, h.savings_usd
            FROM price_harmonization h LEFT JOIN part_master pm ON pm.company_id = h.company_id AND pm.part_no = h.part_no
            WHERE h.company_id = ? ORDER BY h.savings_usd DESC LIMIT ?""", [company, limit]).fetchall()
        return [Harmonization(**dict(zip(Harmonization.model_fields, r))) for r in rows]


class Compliance(BaseModel):
    finding: str                 # price_leakage | spares_clause
    part_no: str
    description: str
    supplier_id: str             # who we paid
    agreement_supplier_id: str   # whose agreement sets the price
    doc_file: str                # the agreement the contract price was extracted from
    plant: str
    po_line_id: str
    po_date: str
    price_ea: float
    contract_price_ea: float
    qty_ea: float
    gap_usd: float


@app.get("/compliance", response_model=list[Compliance])
def compliance(company: str = Query(...), finding: str | None = Query(None, pattern="^(price_leakage|spares_clause)$"),
               limit: int = Query(25, ge=1, le=1000)) -> list[Compliance]:
    """💲 Paid vs the supplier's own agreement (prices extracted from the documents), biggest gap first."""
    with db() as con:
        _company_or_404(con, company)
        if not _has_table(con, "contract_compliance"):
            return []
        where, args = "c.company_id = ?", [company]
        if finding:
            where += " AND c.finding = ?"
            args.append(finding)
        rows = con.execute(f"""
            SELECT c.finding, c.part_no, coalesce(pm.description, ''), CAST(c.supplier_id AS VARCHAR),
                   CAST(c.agreement_supplier_id AS VARCHAR), c.doc_file, c.plant, CAST(c.po_line_id AS VARCHAR),
                   CAST(c.po_date AS VARCHAR), c.price_ea, c.contract_price_ea, c.qty_ea, c.gap_usd
            FROM contract_compliance c LEFT JOIN part_master pm ON pm.company_id = c.company_id AND pm.part_no = c.part_no
            WHERE {where} ORDER BY c.gap_usd DESC LIMIT ?""", [*args, limit]).fetchall()
        return [Compliance(**dict(zip(Compliance.model_fields, r))) for r in rows]


# ---- Planned endpoints (see docs/build/api.md). Owners fill these in. ----
# Every data endpoint takes ?company=<company_id> (see GET /companies) and filters WHERE company_id = ?
# GET  /links?source=&q=    both         : linking explorer rows
# GET  /alerts              warranty     : spike alerts
# GET  /claim-rates/{part}  warranty     : rate by build month for the chart
# POST /brief/{supplier_id} both         : streams the supplier brief (Claude API, template fallback)
