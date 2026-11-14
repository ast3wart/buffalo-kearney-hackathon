from fastapi.testclient import TestClient
from afterlife.run import run, DB_PATH
from api.main import app


def test_health_after_pipeline_run():
    run(DB_PATH)
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()["tables"]}
    assert {"bom", "warranty_claims", "production_spend"} <= names
