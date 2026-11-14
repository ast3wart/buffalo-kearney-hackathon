"""Price schedules in generated supplier agreements: extracted exactly, and compliance finds the planted leaks."""
import contextlib
import io

import pandas as pd
import pytest

from afterlife import cost
from afterlife.extract_prices import PRICE_COLUMNS, extract_prices
from afterlife.generate import generate
from afterlife.io import load
from afterlife.match import link_all


@pytest.fixture(scope="module")
def companies(tmp_path_factory):
    d = tmp_path_factory.mktemp("fresh")
    with contextlib.redirect_stdout(io.StringIO()):
        generate(101, d)
    return {c: load(d / c) for c in ("prairie", "ironridge", "northwind")}


@pytest.mark.parametrize("company", ["prairie", "ironridge", "northwind"])
def test_every_scheduled_price_extracted_exactly(companies, company):
    t = companies[company]
    cp = extract_prices(t)
    assert list(cp.columns) == PRICE_COLUMNS
    tp = t["truth_prices"].astype({"part_no": str, "supplier_id": str})
    m = cp.merge(tp, on=["doc_file", "part_no"], suffixes=("", "_t"), how="right")
    assert m.contract_price_ea.notna().all(), "a scheduled price was not extracted"
    assert ((m.contract_price_ea - pd.to_numeric(m.contract_price_ea_t)).abs() < 1e-6).all()
    assert (m.supplier_id == m.supplier_id_t).all()          # supplier read from the text, not the file name
    assert (m.spares_at_series_price.astype(str).str.lower() == m.spares_at_series_price_t.astype(str).str.lower()).all()


@pytest.mark.parametrize("company", ["prairie", "ironridge", "northwind"])
def test_compliance_is_a_minority_and_realistic(companies, company):
    t = companies[company]
    cc = cost.contract_compliance(t, link_all(t), extract_prices(t))
    ps = t["production_spend"]
    spend = (pd.to_numeric(ps.qty) * pd.to_numeric(ps.unit_price) / pd.to_numeric(ps.price_unit)).sum()
    leak = cc[cc.finding == "price_leakage"]
    assert 0 < len(leak) < 0.15 * len(ps), "leakage should be a minority of lines"
    assert 0 < leak.gap_usd.sum() < 0.01 * spend, "leakage should be well under 1% of spend"
    assert (cc[cc.finding == "spares_clause"].gap_usd > 0).all()


def test_spare_markups_mostly_near_contract(companies):
    """Velocity research: no study supports 1.5-5x as TYPICAL; most spares near the contract price."""
    t = companies["prairie"]
    mk = cost.spare_markups(t, link_all(t))
    assert mk.ratio.median() < 1.5
    assert 0.2 < (mk.ratio >= 1.5).mean() < 0.6        # a minority bought off-contract at a real markup
