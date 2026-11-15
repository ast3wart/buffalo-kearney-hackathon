from fastapi.testclient import TestClient

from api.main import app

c = TestClient(app)


def test_health():
    assert c.get("/health").json() == {"ok": True}


def test_portfolio_and_planted_shelf_moments():
    p = c.get("/portfolio").json()
    assert p["fund_name"] and p["totals"]["plants_owned"] == 5
    m = {x["component_id"]: x for x in p["shelf_matches"]}
    assert m["PA-L2-M01-C1"]["spare_plant_name"] == "Fort Wayne" and m["PA-L2-M01-C1"]["same_company"]
    assert any(x["plant_id"] == "PD" and x["spare_plant_name"] == "Lima" and not x["same_company"] for x in p["shelf_matches"])


def test_registry_evidence_accuracy():
    r = c.get("/plants/PA/registry").json()
    assert len(r["lines"]) == 3
    e = c.get("/components/PA-L2-M01-C1/evidence").json()
    assert e["photo"]["photo_id"].startswith("PA-IMG") and e["component"]["lifecycle_status"] == "discontinued"
    a = c.get("/accuracy").json()
    assert a["components_precision"] >= 0.95 and a["auto_accepted"] == a["auto_accepted_correct"]
    assert c.get("/photos/PA/../../../.env.jpg").status_code == 404


def test_money_routes_pending_or_ok():
    for route in ["/plants/PA/capex", "/plants/PA/spof", "/plants/PA/sourcing", "/plants/PA/savings", "/companies/CO-TILLMAN/deal"]:
        assert c.get(route).status_code in (200, 501), route
