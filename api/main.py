"""Equipment X-Ray API (docs/build/interfaces.md §1). Reads the SQLite registry built by scripts/seed.py.

Asher's routes: portfolio, registry tree, evidence, shelf matches, accuracy, live scan.
Brandon's routes (capex, spof, sourcing, savings, deal) call his pure functions in xray/valuation.py,
xray/sourcing.py and xray/pricing.py; until those exist they return 501 with a clear "pending" message.
"""
import importlib
import json
import tempfile
from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from xray import registry
from xray.evaluate import score

ROOT = Path(__file__).resolve().parent.parent
TRUTH = ROOT / "data/truth/demo"
AT_RISK = ("discontinued", "end_of_life")

app = FastAPI(title="Equipment X-Ray API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@lru_cache(maxsize=1)
def reg() -> dict[str, pd.DataFrame]:
    db = registry.DEFAULT_DB
    if not db.exists():
        raise HTTPException(503, "demo.db missing. Run: python scripts/seed.py")
    return registry.load(db)


def components_full() -> pd.DataFrame:
    r = reg()
    c = r["component"].merge(r["machine"][["machine_id", "line_id", "machine_type", "make", "model", "description", "criticality", "year_built"]],
                             on="machine_id", how="left")
    c = c.merge(r["line"][["line_id", "plant_id", "line_name", "product"]], on="line_id", how="left")
    kb = r["kb_entry"][["kb_id", "manufacturer", "family", "part_no", "description", "successor_part_no", "source_url", "source_type"]]
    return c.merge(kb.rename(columns={"description": "kb_description"}), on="kb_id", how="left").fillna("")


def records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


# ---------------------------------------------------------------- models
class Health(BaseModel):
    ok: bool


class PlantTile(BaseModel):
    plant_id: str
    plant_name: str
    state: str
    company_id: str
    status: str
    employees: int
    lines: int
    machines: int
    components: int
    at_risk: int
    at_risk_pct: float
    needs_review: int
    line_stop_at_risk: int
    idle_spares: int


class Company(BaseModel):
    company_id: str
    company_name: str
    fund_id: str
    plants: list[str]


class ShelfMatch(BaseModel):
    component_id: str
    plant_id: str
    line_id: str
    machine: str
    part_no: str
    family: str
    lifecycle_status: str
    criticality: str
    spare_id: str
    spare_plant_id: str
    spare_plant_name: str
    spare_description: str
    spare_qty: int
    same_company: bool


class Portfolio(BaseModel):
    fund_name: str
    companies: list[Company]
    plants: list[PlantTile]
    totals: dict
    shelf_matches: list[ShelfMatch]


class Accuracy(BaseModel):
    components_precision: float
    components_recall: float
    components_records: int
    auto_accepted: int
    auto_accepted_correct: int
    needs_review: int
    spares_precision: float
    spares_recall: float
    photos_read: int
    photos_exact: int
    note: str


# ---------------------------------------------------------------- Asher's routes
@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(ok=True)


def _shelf_matches() -> pd.DataFrame:
    """At-risk components (discontinued / EOL) whose part sits on a shelf at another owned plant."""
    r = reg()
    c = components_full()
    risk = c[(c.lifecycle_status.isin(AT_RISK)) & (c.kb_id != "")]
    sm = r["spare_match"][r["spare_match"].kb_id != ""].merge(r["spare_stock"], on="spare_id")
    plants = r["plant"].set_index("plant_id")
    owned = set(plants[plants.status == "owned"].index)
    m = risk.merge(sm[["spare_id", "kb_id", "plant_id", "description", "qty"]].rename(
        columns={"plant_id": "spare_plant_id", "description": "spare_description", "qty": "spare_qty"}), on="kb_id")
    m = m[(m.spare_plant_id != m.plant_id) & m.spare_plant_id.isin(owned) & m.plant_id.isin(owned)]
    # skip parts the plant already stocks itself
    own = sm.groupby("plant_id").kb_id.apply(set).to_dict()
    m = m[[k not in own.get(p, set()) for k, p in zip(m.kb_id, m.plant_id)]]
    m["spare_plant_name"] = m.spare_plant_id.map(plants.plant_name)
    m["same_company"] = m.plant_id.map(plants.company_id) == m.spare_plant_id.map(plants.company_id)
    m["machine"] = m.make + " " + m.model
    m["spare_qty"] = pd.to_numeric(m.spare_qty, errors="coerce").fillna(0).astype(int)
    # one row per component: best spare = same company first, then the biggest quantity
    m = m.sort_values(["same_company", "spare_qty"], ascending=False).drop_duplicates("component_id")
    order = {"line_stop": 0, "degraded": 1, "none": 2}
    m = m.sort_values(by=["criticality", "plant_id"], key=lambda s: s.map(order) if s.name == "criticality" else s)
    return m[list(ShelfMatch.model_fields)]


@app.get("/portfolio", response_model=Portfolio)
def portfolio() -> Portfolio:
    r = reg()
    c = components_full()
    plants = r["plant"]
    spares = r["spare_stock"].copy()
    cutoff = f"{date.today().year - 5}"
    tiles = []
    for p in plants.itertuples():
        pc = c[c.plant_id == p.plant_id]
        risk = pc.lifecycle_status.isin(AT_RISK)
        tiles.append(PlantTile(
            plant_id=p.plant_id, plant_name=p.plant_name, state=p.state, company_id=p.company_id, status=p.status,
            employees=int(p.employees), lines=int((r["line"].plant_id == p.plant_id).sum()),
            machines=int(pc.machine_id.nunique()), components=len(pc), at_risk=int(risk.sum()),
            at_risk_pct=round(float(risk.mean()) if len(pc) else 0.0, 3),
            needs_review=int((pc.needs_review == "yes").sum()),
            line_stop_at_risk=int((risk & (pc.criticality == "line_stop")).sum()),
            idle_spares=int(((spares.plant_id == p.plant_id) & (spares.last_moved_on < cutoff)).sum())))
    comp = r["company"]
    companies = [Company(company_id=x.company_id, company_name=x.company_name, fund_id=x.fund_id or "",
                         plants=plants[plants.company_id == x.company_id].plant_id.tolist()) for x in comp.itertuples()]
    owned = [t for t in tiles if t.status == "owned"]
    totals = {"plants_owned": len(owned), "machines": sum(t.machines for t in owned), "components": sum(t.components for t in owned),
              "at_risk": sum(t.at_risk for t in owned), "line_stop_at_risk": sum(t.line_stop_at_risk for t in owned),
              "idle_spares": sum(t.idle_spares for t in owned)}
    totals["at_risk_pct"] = round(totals["at_risk"] / totals["components"], 3) if totals["components"] else 0
    fund = r["fund"].fund_name.iloc[0] if len(r["fund"]) else ""
    return Portfolio(fund_name=fund, companies=companies, plants=tiles, totals=totals,
                     shelf_matches=[ShelfMatch(**x) for x in records(_shelf_matches())])


@app.get("/plants/{plant_id}/registry")
def plant_registry(plant_id: str) -> dict:
    r = reg()
    plant = r["plant"][r["plant"].plant_id == plant_id]
    if plant.empty:
        raise HTTPException(404, f"no plant {plant_id}")
    c = components_full()
    c = c[c.plant_id == plant_id]
    lines = []
    for ln in r["line"][r["line"].plant_id == plant_id].itertuples():
        ms = r["machine"][r["machine"].line_id == ln.line_id]
        lines.append({"line_id": ln.line_id, "line_name": ln.line_name, "product": ln.product,
                      "machines": [{**m, "components": records(c[c.machine_id == m["machine_id"]][[
                          "component_id", "kb_id", "part_no", "part_no_read", "family", "manufacturer", "component_type",
                          "lifecycle_status", "date_code", "confidence", "method", "needs_review", "review_reason",
                          "successor_part_no", "evidence_id"]])} for m in records(ms)]})
    return {"plant": records(plant)[0], "lines": lines}


@app.get("/components/{component_id}/evidence")
def evidence(component_id: str) -> dict:
    r = reg()
    c = components_full()
    row = c[c.component_id == component_id]
    if row.empty:
        raise HTTPException(404, f"no component {component_id}")
    comp = records(row)[0]
    ev = r["evidence"][r["evidence"].evidence_id == comp["evidence_id"]]
    photo = r["photo"][r["photo"].component_id == component_id] if "component_id" in r["photo"] else pd.DataFrame()
    lst = r.get("listing", pd.DataFrame())
    listings = lst[lst.kb_id == comp["kb_id"]] if "kb_id" in lst else pd.DataFrame()
    alts = r["alternative"][r["alternative"].kb_id == comp["kb_id"]]
    return {"component": comp, "evidence": records(ev)[0] if len(ev) else None,
            "photo": records(photo)[0] if len(photo) else None, "listings": records(listings), "alternatives": records(alts)}


@app.get("/photos/{plant_id}/{photo_id}.jpg")
def photo_file(plant_id: str, photo_id: str):
    from fastapi.responses import FileResponse

    p = ROOT / "data/seed/demo" / plant_id / "photos" / f"{photo_id}.jpg"
    if not p.exists() or not p.resolve().is_relative_to((ROOT / "data/seed/demo").resolve()):
        raise HTTPException(404, "no such photo")
    return FileResponse(p, media_type="image/jpeg")


@app.get("/plants/{plant_id}/shelf-matches", response_model=list[ShelfMatch])
def plant_shelf_matches(plant_id: str) -> list[ShelfMatch]:
    m = _shelf_matches()
    return [ShelfMatch(**x) for x in records(m[m.plant_id == plant_id])]


@app.get("/accuracy", response_model=Accuracy)
def accuracy() -> Accuracy:
    r = reg()
    t = pd.read_csv(TRUTH / "components.csv", dtype=str).fillna("")
    c = r["component"]
    pred = c[c.kb_id != ""][["component_id", "kb_id"]]
    s = score(pred, t[t.kb_id != ""][["component_id", "kb_id"]], key=["component_id"], value="kb_id").iloc[0]
    acc = c[(c.kb_id != "") & (c.needs_review == "no")].merge(t[["component_id", "kb_id"]], on="component_id", suffixes=("", "_t"))
    st = pd.read_csv(TRUTH / "spare_matches.csv", dtype=str)
    sm = r["spare_match"]
    ss = score(sm[sm.kb_id != ""][["spare_id", "kb_id"]], st, key=["spare_id"], value="kb_id").iloc[0]
    v = c[c.method == "vision"].merge(t[["component_id", "kb_id"]], on="component_id", suffixes=("", "_t"))
    return Accuracy(components_precision=float(s.precision), components_recall=float(s.recall), components_records=int(s.records),
                    auto_accepted=len(acc), auto_accepted_correct=int((acc.kb_id == acc.kb_id_t).sum()),
                    needs_review=int((c.needs_review == "yes").sum()), spares_precision=float(ss.precision),
                    spares_recall=float(ss.recall), photos_read=len(v), photos_exact=int((v.kb_id == v.kb_id_t).sum()),
                    note="Synthetic demo portfolio with a planted answer key; photos are rendered test labels read by Claude.")


@app.post("/scan")
async def scan(file: UploadFile = File(...)) -> dict:
    """The live demo: a real photo -> Claude reads it -> matched to the knowledge base."""
    from xray.extract import read_photo
    from xray.pipeline import ExactIndex
    from xray.matching import Matcher

    suffix = Path(file.filename or "photo.jpg").suffix.lower() or ".jpg"
    if suffix not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(400, "upload a .jpg, .png or .webp photo")
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
    try:
        reading = read_photo(tmp.name)
    except Exception as e:  # noqa: BLE001 - surface any API/key problem to the demo screen
        raise HTTPException(502, f"could not read the photo: {e}")
    finally:
        Path(tmp.name).unlink(missing_ok=True)
    kb = reg()["kb_entry"]
    text = f"{reading.get('part_no', '')} {reading.get('description', '')}"
    idx = ExactIndex(kb).hit(reading.get("part_no", ""))
    conf, how = (0.97, "exact") if idx is not None else (0.0, "fuzzy")
    if idx is None:
        abbr = {a.upper(): e.upper() for a, e in pd.read_csv(ROOT / "data/reference/abbreviations.csv", dtype=str).itertuples(index=False)}
        idx, conf, _ = Matcher([f"{x.part_no} {x.aliases} {x.family} {x.description}" for x in kb.itertuples()], abbr).match(text)
    match = records(kb.iloc[[idx]])[0] if idx is not None else None
    review = match is None or min(conf, float(reading.get("confidence", 0))) < 0.8 or bool(reading.get("unclear"))
    return {"reading": reading, "match": match, "match_method": how if match else "none",
            "confidence": round(min(conf, float(reading.get("confidence", 0))), 3) if match else 0.0, "needs_review": review}


# ---------------------------------------------------------------- Brandon's routes (call his pure functions)
def _brandon(module: str, *funcs: str):
    try:
        mod = importlib.import_module(f"xray.{module}")
        return [getattr(mod, f) for f in funcs]
    except (ImportError, AttributeError):
        raise HTTPException(501, f"pending: xray/{module}.py ({', '.join(funcs)}) from Brandon's money thread")


def _sourcing_tables():
    value_parts, recommend_sourcing = _brandon("sourcing", "value_parts", "recommend_sourcing")
    pv = value_parts(reg())
    return pv, recommend_sourcing(reg(), pv)


@app.get("/plants/{plant_id}/sourcing")
def plant_sourcing(plant_id: str) -> dict:
    pv, rec = _sourcing_tables()
    c = components_full()
    rec = rec.merge(c[["component_id", "plant_id", "part_no", "family", "lifecycle_status", "criticality"]], on="component_id", how="left")
    return {"part_valuation": records(pv), "recommendations": records(rec[rec.plant_id == plant_id])}


@app.get("/plants/{plant_id}/capex")
def plant_capex(plant_id: str) -> dict:
    (capex_by_year,) = _brandon("valuation", "capex_by_year")
    pv, _ = _sourcing_tables()
    df = capex_by_year(reg(), pv)
    return {"capex_by_year": records(df[df.plant_id == plant_id])}


@app.get("/plants/{plant_id}/spof")
def plant_spof(plant_id: str) -> dict:
    (spof,) = _brandon("valuation", "spof")
    _, rec = _sourcing_tables()
    df = spof(reg(), rec).merge(components_full()[["component_id", "plant_id"]], on="component_id", how="left")
    return {"spof": records(df[df.plant_id == plant_id])}


@app.get("/plants/{plant_id}/savings")
def plant_savings_route(plant_id: str) -> dict:
    plant_savings, price = _brandon("pricing", "plant_savings", "price")
    _, rec = _sourcing_tables()
    s = plant_savings(reg(), rec)
    p = price(s)
    return {"plant_savings": records(s[s.plant_id == plant_id]), "price": records(p[p.plant_id == plant_id])}


@app.get("/companies/{company_id}/deal")
def company_deal(company_id: str) -> dict:
    capex_by_year, deal_adjustment = _brandon("valuation", "capex_by_year", "deal_adjustment")
    pv, _ = _sourcing_tables()
    return {"deal_adjustment": records(deal_adjustment(reg(), capex_by_year(reg(), pv), company_id, 0.10))}
