from fastapi.testclient import TestClient
from afterlife.run import run, DB_PATH
from api.main import app


def test_health_after_pipeline_run():
    run(DB_PATH)
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()["tables"]}
    assert {"bom", "warranty_claims", "production_spend"} <= names


def test_overview_markups_harmonization_for_every_company():
    run(DB_PATH)
    c = TestClient(app)
    companies = [x["company_id"] for x in c.get("/companies").json()]
    assert companies
    for co in companies:
        o = c.get("/overview", params={"company": co})
        assert o.status_code == 200, o.text
        o = o.json()
        assert o["products"] and all(p["lifecycle_cost"] >= p["build_cost"] for p in o["products"])
        assert 0 <= o["coverage"]["service_spend_pct"] <= 1
        assert o["spare_overspend_usd"] >= 0 and o["harmonization_usd"] >= 0
        m = c.get("/markups", params={"company": co, "limit": 5}).json()
        assert m == sorted(m, key=lambda x: -x["overspend_usd"])
        assert c.get("/harmonization", params={"company": co, "limit": 5}).status_code == 200
    assert c.get("/overview", params={"company": "no-such-company"}).status_code == 404
