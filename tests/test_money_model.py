"""Money model on the hand-made sample (data/seed/sample): the planted moments come out right and the
guardrails hold (ranges ordered, one-time money never priced, deal lens only for targets)."""
import pandas as pd
import pytest

from xray.pricing import plant_savings, price
from xray.sourcing import recommend_sourcing, trust_scores, value_parts
from xray.valuation import capex_by_year, deal_adjustment, spof

KINETIX_L2 = "PA-L2-M01-C1"


@pytest.fixture(scope="module")
def model(reg):
    pv = value_parts(reg)
    sr = recommend_sourcing(reg, pv)
    sp = spof(reg, sr)
    cx = capex_by_year(reg, pv, sourcing_recommendation=sr)
    ps = plant_savings(reg, sr, pv, sp)
    return {"pv": pv, "sr": sr, "spof": sp, "capex": cx, "deal": deal_adjustment(reg, cx), "savings": ps,
            "price": price(ps)}


def test_shelf_spare_comes_from_owned_sister_plant_not_target(model):
    r = model["sr"].set_index("component_id").loc[KINETIX_L2]
    assert r.action == "use_shelf_spare" and r.spare_id == "PB-S001"
    assert 0 < r.transfer_cost_low <= r.transfer_cost_high
    assert "PE-S006" not in set(model["sr"].spare_id), "a target plant's shelf is not ours yet"


def test_listing_confidence_and_trust(model, reg):
    pv = model["pv"]
    for kb_id in ("KB-009", "KB-002", "KB-006"):
        assert (pv[pv.kb_id == kb_id].confidence == "high").any(), kb_id
    assert (pv[pv.kb_id == "KB-003"].confidence == "none").all(), "KB parts with no listings get a `none` row"
    t = trust_scores(reg["listing"])
    assert t.between(0, 1).all()
    assert pv.n_low_trust.sum() > 0, "low-trust listings are flagged, not silently dropped"
    ok = pv[pv.n_listings > 0]
    assert (ok.price_low <= ok.price_mid).all() and (ok.price_mid <= ok.price_high).all()


def test_shelf_spare_lowers_spof_exposure(model, reg):
    with_spare = model["spof"].set_index("component_id").loc[KINETIX_L2]
    no_spare = spof(reg, model["sr"].assign(action="monitor", spare_id="", spare_plant_id=""))
    no_spare = no_spare.set_index("component_id").loc[KINETIX_L2]
    assert with_spare.hours_down_high < no_spare.hours_down_high
    assert with_spare.downtime_exposure_per_year_high < no_spare.downtime_exposure_per_year_high
    assert with_spare.downtime_exposure_per_year_low < no_spare.downtime_exposure_per_year_low


def test_redundant_machine_scores_zero(model, reg):
    reg2 = dict(reg)
    reg2["machine"] = reg["machine"].assign(redundant_with=lambda d: d.redundant_with.mask(d.machine_id == "PA-L2-M01", "PA-L2-M09"))
    r = spof(reg2, model["sr"]).set_index("component_id").loc[KINETIX_L2]
    assert r.downtime_exposure_per_year_low == 0 and r.downtime_exposure_per_year_high == 0


def test_deal_lens_only_for_target(model, reg):
    d = model["deal"]
    assert list(d.company_id) == ["CO-TILLMAN"]
    assert deal_adjustment(reg, model["capex"], company_id="CO-HALVORSEN").empty
    r = d.iloc[0]
    assert 0 < r.suggested_price_reduction_low <= r.suggested_price_reduction_high <= r.deferred_capex_low
    assert r.suggested_holdback > 0


def test_capex_growth_only_from_user(model, reg):
    assert "growth" not in set(model["capex"].capex_type)
    g = pd.DataFrame({"plant_id": ["PA"], "year": [2028], "capex_low": [1.0], "capex_high": [2.0]})
    cx = capex_by_year(reg, model["pv"], sourcing_recommendation=model["sr"], growth=g)
    assert (cx.capex_type == "growth").sum() == 1


def test_money_ranges_ordered(model):
    pairs = {"capex": [("capex_low", "capex_high")],
             "spof": [("hours_down_low", "hours_down_high"),
                      ("downtime_exposure_per_year_low", "downtime_exposure_per_year_high")],
             "sr": [("transfer_cost_low", "transfer_cost_high"), ("part_value_low", "part_value_high")],
             "deal": [("deferred_capex_low", "deferred_capex_high")],
             "savings": [("savings_low", "savings_base"), ("savings_base", "savings_high")],
             "price": [("price_per_plant_low", "price_per_plant_high")]}
    for name, cols in pairs.items():
        df = model[name]
        for lo, hi in cols:
            ok = df[[lo, hi]].dropna()
            assert (ok[lo] <= ok[hi]).all(), f"{name}: {lo} > {hi}"


def test_nothing_one_time_in_price_base(model):
    s = model["savings"]
    assert not ((s.one_time == "yes") & (s.in_price_base == "yes")).any()
    assert (s.loc[s.lever.isin(["spares_inventory_released", "downtime_avoided"]), "in_price_base"] == "no").all()
    # price = capture % x only the in-base recurring levers
    p = model["price"].set_index("plant_id")
    base = s[s.in_price_base == "yes"].groupby("plant_id").savings_high.sum()
    for plant_id, v in base.items():
        assert p.loc[plant_id, "price_per_plant_high"] == pytest.approx(p.loc[plant_id, "value_capture_pct"] * v, abs=0.01)
    assert set(s.plant_id) == {"PA", "PB"}, "savings are for owned plants; the target gets the deal lens"


def test_full_plant_quote_scales_up_and_stays_unpriced_for_one_time(reg):
    sample = plant_savings(reg)
    full = plant_savings(reg, full_plant=True)
    assert full.savings_base.sum() > sample.savings_base.sum()
    assert full.basis.str.startswith("full plant").all()
    assert (full.loc[full.one_time == "yes", "in_price_base"] == "no").all()
    assert (full.savings_low <= full.savings_high).all()


def test_deal_lens_adds_end_of_life_machines_without_double_count(model, reg):
    d = model["deal"].iloc[0]
    assert d.suggested_price_reduction_low == pytest.approx(d.controls_deferred_low + d.machine_deferred_low, abs=1)
    assert d.machine_deferred_low <= d.machine_deferred_high
    only_controls = deal_adjustment(reg, model["capex"], include_machines=False).iloc[0]
    assert only_controls.machine_deferred_low == 0 and only_controls.suggested_price_reduction_low <= d.suggested_price_reduction_low
