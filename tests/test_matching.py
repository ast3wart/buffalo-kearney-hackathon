import pandas as pd

from xray.evaluate import score
from xray.matching import Matcher, canon, numbers


def test_canon_units_and_dimensions():
    assert canon("motor 7.5 hp, 35 x 47") == "MOTOR 7.5HP 35X47"
    assert numbers("63X300") == {"63", "300"}


def test_matcher_finds_catalog_number_through_abbreviations():
    kb = ["ALPHA CONTROLS PROCESSOR 1756-L61", "ALPHA CONTROLS PROCESSOR 1756-L72", "BETA DRIVES VFD 22B-D010"]
    m = Matcher(kb, abbreviations={"AC": "ALPHA CONTROLS"})
    idx, conf, ev = m.match("AC 1756-L61 SER B processor")
    assert idx == 0 and conf > 0.5 and "1756" in ev["shared_numbers"]


def test_matcher_rejects_unrelated_text():
    m = Matcher(["ALPHA CONTROLS PROCESSOR 1756-L61", "BETA DRIVES VFD 22B-D010"])
    idx, conf, _ = m.match("coffee maker")
    assert idx is None and conf == 0.0


def test_score_precision_recall():
    truth = pd.DataFrame({"machine_id": ["M1", "M2", "M3", "M4"], "model": ["a", "b", "c", "d"]})
    pred = pd.DataFrame({"machine_id": ["M1", "M2", "M3"], "model": ["a", "b", "x"]})
    r = score(pred, truth, key=["machine_id"], value="model").iloc[0]
    assert (r.precision, r.recall) == (round(2 / 3, 3), 0.5)
