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
    """Every demo photo has a cached Claude reading (demo runs offline) that matches the true catalog number."""
    from xray.extract import read_photo

    truth = pd.read_csv(TRUTH / "components.csv", dtype=str).fillna("").set_index("component_id")
    n = sum(len(pd.read_csv(m)) for m in (ROOT / "data/seed/demo").glob("*/photos.csv"))
    assert n >= 10, f"only {n} demo photos listed: photos.csv files were emptied?"
    for manifest in (ROOT / "data/seed/demo").glob("*/photos.csv"):
        for p in pd.read_csv(manifest, dtype=str).fillna("").itertuples():
            r = read_photo(manifest.parent / p.file, use_api=False)
            assert r["part_no"].replace(" ", "").upper() == truth.loc[p.component_id, "part_no"].upper(), p.photo_id
