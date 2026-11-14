"""Spend matcher: correct, measured on companies it was never tuned on, with meaningful confidence."""
import contextlib
import io
import json

import pandas as pd
import pytest

from afterlife.evaluate import score
from afterlife.generate import generate
from afterlife.io import SAMPLE, load
from afterlife.match_spend import link_spend, price_per_each
from afterlife.taxonomy import LINK_COLUMNS, LINK_METHODS

FRESH_SEED = 101   # never used while tuning: an honest holdout for every company


@pytest.fixture(scope="module")
def fresh(tmp_path_factory):
    d = tmp_path_factory.mktemp("fresh")
    with contextlib.redirect_stdout(io.StringIO()):
        generate(FRESH_SEED, d)
    return {c: load(d / c) for c in ("prairie", "ironridge", "northwind")}


def test_output_shape_and_evidence():
    t = load(SAMPLE)
    links = link_spend(t)
    assert list(links.columns) == LINK_COLUMNS
    assert set(links.method) <= set(LINK_METHODS)
    assert all(isinstance(json.loads(e), dict) for e in links.evidence)
    assert links.source_id.is_unique


def test_sample_all_correct():
    t = load(SAMPLE)
    s = score(link_spend(t), t["truth_links"])
    assert (s.precision == 1).all() and (s.recall == 1).all(), s


@pytest.mark.parametrize("company", ["prairie", "ironridge", "northwind"])
def test_holdout_accuracy_floor(fresh, company):
    """Floor from the first real numbers (Sat AM): all >= 0.978 on 3 fresh seeds. Ratchet up, never down."""
    t = fresh[company]
    s = score(link_spend(t), t["truth_links"])
    assert (s.precision >= 0.97).all() and (s.recall >= 0.97).all(), s


def test_high_confidence_links_are_right(fresh):
    """Recovery will use links with confidence >= 0.8; those must be ~always right."""
    frames = []
    for t in fresh.values():
        L = link_spend(t)
        truth = t["truth_links"].astype(str).set_index("source_id").part_no
        frames.append(L.assign(ok=L.part_no == L.source_id.map(truth)))
    L = pd.concat(frames)
    assert L[L.confidence >= 0.8].ok.mean() >= 0.995


def test_price_per_each():
    df = pd.DataFrame({"unit_price": [58.90, 404.93, 4.12], "price_unit": [1, 100, 1], "uom": ["BX10", "EA", "EA"]})
    assert price_per_each(df).round(4).tolist() == [5.89, 4.0493, 4.12]
