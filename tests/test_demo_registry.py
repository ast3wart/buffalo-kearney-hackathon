"""The demo registry: planted moments exist and matching stays above its accuracy floors."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seed  # noqa: E402

from xray.evaluate import score  # noqa: E402
from xray.registry import load  # noqa: E402

TRUTH = ROOT / "data/truth/demo"


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    db = tmp_path_factory.mktemp("db") / "demo.db"
    seed.main(ROOT / "data/seed/demo", db)
    return load(db)


def test_portfolio_shape(reg):
    assert len(reg["plant"]) == 6 and set(reg["plant"].status) == {"owned", "target"}
    assert 55 <= len(reg["machine"]) <= 75 and 100 <= len(reg["component"]) <= 150


def test_component_matching_floors(reg):
    t = pd.read_csv(TRUTH / "components.csv", dtype=str).fillna("")
    c = reg["component"]
    pred = c[c.kb_id != ""][["component_id", "kb_id"]]
    r = score(pred, t[t.kb_id != ""][["component_id", "kb_id"]], key=["component_id"], value="kb_id").iloc[0]
    assert r.precision >= 0.95 and r.recall >= 0.85
    assert not set(pred.component_id) & set(t[t.kb_id == ""].component_id), "non-catalog parts must stay unmatched"
    accepted = c[(c.kb_id != "") & (c.needs_review == "no")].merge(t, on="component_id", suffixes=("", "_t"))
    assert (accepted.kb_id == accepted.kb_id_t).all(), "anything not sent to review must be right"


def test_planted_spare_moments(reg):
    spof = pd.read_csv(TRUTH / "spof.csv", dtype=str)
    sm = reg["spare_match"].set_index("spare_id")
    comp = reg["component"].set_index("component_id")
    for row in spof.itertuples():
        assert comp.loc[row.component_id, "kb_id"] == sm.loc[row.shelf_spare_id, "kb_id"], row.why
        assert comp.loc[row.component_id, "needs_review"] == "no"
    toledo_spares = reg["spare_match"].merge(reg["spare_stock"][["spare_id", "plant_id"]])
    assert not ((toledo_spares.plant_id == "PA") & (toledo_spares.kb_id == comp.loc[spof.component_id.iloc[0], "kb_id"])).any()


def test_spare_matching_floor(reg):
    st = pd.read_csv(TRUTH / "spare_matches.csv", dtype=str)
    sm = reg["spare_match"]
    r = score(sm[sm.kb_id != ""][["spare_id", "kb_id"]], st, key=["spare_id"], value="kb_id").iloc[0]
    assert r.precision >= 0.95 and r.recall >= 0.9


def test_photo_readings_cached_and_exact():
    """Every component has a cached image-recognition reading (demo runs offline). Catalog parts on readable photos
    are read exactly; on cut-off photos the reader must flag it (unclear + low confidence) instead of guessing."""
    from xray.extract import read_photo

    truth = pd.read_csv(TRUTH / "components.csv", dtype=str).fillna("").set_index("component_id")
    photos = pd.concat(pd.read_csv(m, dtype=str).fillna("").assign(manifest_dir=str(m.parent)) for m in (ROOT / "data/seed/demo").glob("*/photos.csv"))
    assert len(photos) == len(truth), "every component should have a photo"
    for p in photos.itertuples():
        r = read_photo(Path(p.manifest_dir) / p.file, use_api=False)
        expected = truth.loc[p.component_id, "part_no"]
        if not expected:
            continue  # commodity part: not in the KB
        exact = r["part_no"].replace(" ", "").upper() == expected.replace(" ", "").upper()
        if p.quality == "cut_off":
            assert exact or (r["unclear"] and r["confidence"] <= 0.7), p.photo_id
        else:
            assert exact, (p.photo_id, r["part_no"], expected)


def test_health_model_finds_planted_problems(reg):
    """The health score must put every planted problem (failing fan, worn capacitors, current anomaly, hot
    connection) in poor health, while most parts stay healthy."""
    from xray import condition

    h = condition.compute(reg).set_index("component_id")
    planted = pd.read_csv(TRUTH / "condition_planted.csv").component_id
    assert (h.loc[planted, "health_score"] <= 40).all(), h.loc[planted, ["health_score", "drivers"]]
    assert h.health_score.median() >= 50, "most parts should look healthy (demo plants are old: median ~55)"
    assert set(h.confidence) <= {"high", "medium", "low", "none"}


def test_anomaly_detectors_catch_planted_patterns_with_few_false_alarms(reg):
    """Each planted time-series pattern is caught by the detector built for it; parts with no planted problem
    rarely fire (SPC false-alarm rate, measured, not assumed)."""
    from xray import anomaly

    a = anomaly.compute(reg).set_index("component_id")
    assert a.loc["PA-L2-M01-C1", "sev_shift"] > 0.5            # step: failing fan -> EWMA
    assert a.loc["PB-L1-M02-C3", "sev_drift"] > 0.5            # slow warming -> CUSUM
    assert a.loc["PA-L1-M01-C3", "sev_current"] > 0.5          # motor current -> Mahalanobis
    assert a.loc["PC-L1-M01-C1", "anomaly_severity"] > 0.5     # intermittent spikes
    planted = set(pd.read_csv(TRUTH / "condition_planted.csv").component_id)
    monitored = a[a.sigma_c.notna() & ~a.index.isin(planted)]
    assert len(monitored) >= 20
    assert (monitored.anomaly_severity > 0).mean() <= 0.10, monitored[monitored.anomaly_severity > 0]
