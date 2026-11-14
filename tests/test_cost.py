"""cost.py: double-count rule, markups match how the data was generated, acquired-plant premium shows up."""
import contextlib
import io

import pandas as pd
import pytest

from afterlife import cost
from afterlife.generate import generate
from afterlife.io import SAMPLE, load
from afterlife.match import link_all
from afterlife.profiles import PROFILES


@pytest.fixture(scope="module")
def fresh(tmp_path_factory):
    d = tmp_path_factory.mktemp("fresh")
    with contextlib.redirect_stdout(io.StringIO()):
        generate(101, d)
    out = {}
    for c in ("prairie", "ironridge"):
        t = load(d / c)
        out[c] = (t, link_all(t))
    return out


def test_double_count_rule_warranty_repair_never_added():
    """21b: warranty = claims; service 'warranty_repair' spend is reported for reconciliation, never added."""
    t = load(SAMPLE)
    L = link_all(t)
    lc = cost.lifecycle_cost(t, L).set_index("product_id")
    wc = t["warranty_claims"]
    claims_cost = sum(pd.to_numeric(wc[c]).fillna(0) for c in ("parts_cost", "labor_cost", "other_cost") if c in wc)
    assert lc.warranty_cost.sum() == pytest.approx(claims_cost.sum(), rel=1e-6)
    assert lc.warranty_repair_spend.sum() > 0                       # it exists...
    expected = lc.build_cost + lc.spares_per_unit + lc.warranty_per_unit
    assert (lc.lifecycle_cost - expected).abs().max() < 0.02        # ...but is not part of lifecycle cost


def test_lifecycle_and_revenue_shape():
    t = load(SAMPLE)
    lc = cost.lifecycle_cost(t, link_all(t))
    assert set(lc.product_id) == set(t["products"].product_id)
    assert (lc.lifecycle_cost >= lc.build_cost).all()
    assert (lc.revenue > 0).all() and (lc.warranty_pct_revenue >= 0).all()


@pytest.mark.parametrize("company", ["prairie", "ironridge"])
def test_measured_markups_match_generated_mix(fresh, company):
    t, L = fresh[company]
    prof = next(p for p in PROFILES if p["company_id"] == company)
    lo, hi = prof["spare_markup"]                      # off-contract buys
    c_lo, c_hi = prof["spare_contract_markup"]         # bought near the contract price
    mk = cost.spare_markups(t, L)
    assert len(mk) > 50
    assert c_lo * 0.85 <= mk.ratio.median() <= hi       # most near contract, a minority off-contract
    assert mk.ratio.max() <= hi * 1.15
    assert (mk.overspend_usd >= 0).all() and mk.overspend_usd.sum() > 0


def test_acquired_plant_premium_is_found(fresh):
    t, L = fresh["ironridge"]
    acq = next(p for p in PROFILES if p["company_id"] == "ironridge")["acquired_plant"]["plant"]
    ph = cost.price_harmonization(t, L)
    assert ph[ph.plant == acq].savings_usd.sum() > 0
    t2, L2 = fresh["prairie"]
    assert acq not in set(cost.price_harmonization(t2, L2).plant)


def test_build_cost_priced_from_actual_spend(fresh):
    t, L = fresh["prairie"]
    bc = cost.build_cost(t, L)
    assert (bc.build_cost > 0).all() and (bc.priced_from_spend > 0.95).all()
