"""detect.py against the sample's planted spike (truth_spikes) using truth claim links.

The sample's seal kit is dual-sourced; the spike is on one supplier's lot only, and one product
mixes both suppliers 50/50 after the spike starts. The other supplier must NOT be flagged.
"""
import pandas as pd

from afterlife import detect
from afterlife.io import SAMPLE, load


def _truth_claim_links(t):
    tl = t["truth_links"]
    return tl[tl.source_table == "warranty_claims"][["source_table", "source_id", "part_no"]]


def test_sample_spike_found_and_attributed():
    t = load(SAMPLE)
    rates = detect.claim_rates(t, _truth_claim_links(t))
    alerts = detect.find_spikes(rates, t)
    truth = t["truth_spikes"].iloc[0]

    assert len(alerts) == 1, alerts
    a = alerts.iloc[0]
    assert a.part_no == truth.part_no
    assert a.supplier_id == truth.supplier_id
    assert a.start_build_month == truth.start_build_month
    assert a.from_po_line_id == truth.from_po_line_id
    assert a.attribution == "clean"
    assert a.ratio >= detect.RATIO_MIN
    assert a.products_affected == 3
    assert a.exposure_usd > 0


def test_alert_columns_match_contract():
    t = load(SAMPLE)
    alerts = detect.find_spikes(detect.claim_rates(t, _truth_claim_links(t)), t)
    for c in ["part_no", "supplier_id", "products_affected", "start_build_month", "mis_window",
              "baseline_rate", "current_rate", "ratio", "exposure_usd", "from_po_line_id"]:
        assert c in alerts.columns, c


def test_months_in_service_and_maturity():
    assert detect.months_between("2026-03", "2026-03-31") == 0
    assert detect.months_between("2026-03", "2026-06-01") == 3
    t = load(SAMPLE)
    rates = detect.claim_rates(t, _truth_claim_links(t))
    # sample data_as_of 2026-10-31, mis_window 3 -> builds through 2026-07 are mature
    assert rates.mature.all()
    assert {"part_no", "supplier_id", "build_month", "units_built", "raw_claims", "raw_rate",
            "mis_claims", "mis_rate", "mature"} <= set(rates.columns)


def test_immature_months_never_alert():
    t = load(SAMPLE)
    t = {**t, "dataset_info": t["dataset_info"].assign(
        value=lambda d: d.value.where(d.key != "data_as_of", "2026-05-31"))}
    rates = detect.claim_rates(t, _truth_claim_links(t))
    assert not rates[rates.build_month > "2026-02"].mature.any()
    assert detect.find_spikes(rates, t).empty


def test_no_links_no_alerts():
    t = load(SAMPLE)
    empty = pd.DataFrame(columns=["source_table", "source_id", "part_no"])
    assert detect.find_spikes(detect.claim_rates(t, empty), t).empty


# ---- synthetic datasets (item #18): spike caught on several seeds, no false alarms without one ----
import numpy as np


def _synthetic(seed: int, spike_from: int | None, months: int = 12, units: int = 500,
               base_per_1000: float = 4.0, multiplier: float = 3.0):
    """3 products share one part from one supplier; claims ~ Poisson within the MIS window."""
    rng = np.random.default_rng(seed)
    ms = [f"2025-{m:02d}" for m in range(1, 13)][:months]
    prods = ["P1", "P2", "P3"]
    builds = pd.DataFrame([{"product_id": p, "build_month": m, "units_built": units} for p in prods for m in ms])
    supply = pd.DataFrame([{"product_id": p, "build_month": m, "part_no": "X-1", "supplier_id": "SUP-A",
                            "po_line_id": f"PO-{i // 3:03d}", "share": 1.0}
                           for p in prods for i, m in enumerate(ms)])
    claims, links = [], []
    for p in prods:
        for i, m in enumerate(ms):
            rate = base_per_1000 * (multiplier if spike_from is not None and i >= spike_from else 1)
            for _ in range(rng.poisson(rate * units / 1000)):
                mis = int(rng.integers(0, 4))
                y, mo = divmod(int(m[5:]) - 1 + mis, 12)
                cid = f"C{len(claims):05d}"
                claims.append({"claim_id": cid, "product_id": p, "build_month": m,
                               "failure_date": f"{2025 + y}-{mo + 1:02d}-15", "parts_cost": 40.0,
                               "labor_cost": 160.0, "recovery_status": "none"})
                links.append({"source_table": "warranty_claims", "source_id": cid, "part_no": "X-1"})
    t = {"builds": builds, "build_supply": supply, "bom": supply[["product_id", "part_no"]].drop_duplicates(),
         "warranty_claims": pd.DataFrame(claims),
         "dataset_info": pd.DataFrame({"key": ["data_as_of", "mis_window"], "value": ["2026-06-30", "3"]})}
    return t, pd.DataFrame(links)


def test_synthetic_spike_caught_on_several_seeds():
    for seed in (7, 8, 9):
        t, links = _synthetic(seed, spike_from=6)
        alerts = detect.find_spikes(detect.claim_rates(t, links), t)
        assert len(alerts) == 1, (seed, alerts)
        assert alerts.iloc[0].start_build_month in {"2025-06", "2025-07", "2025-08"}, (seed, alerts.iloc[0])


def test_no_false_alarms_without_a_spike():
    """Realistic volume (~18 claims/month pooled): no alerts on 30 datasets without a spike."""
    false_alarms = 0
    for seed in range(30):
        t, links = _synthetic(seed, spike_from=None, units=1500)
        false_alarms += len(detect.find_spikes(detect.claim_rates(t, links), t))
    assert false_alarms == 0, false_alarms


def test_open_exposure_excludes_recovered_and_goodwill():
    t, links = _synthetic(7, spike_from=6)
    base = detect.find_spikes(detect.claim_rates(t, links), t).iloc[0]
    assert base.open_exposure_usd == base.exposure_usd  # all claims open
    assert 0 < base.excess_cost_usd < base.exposure_usd
    wc = t["warranty_claims"].copy()
    wc["claim_type"] = ["goodwill" if i % 4 == 0 else "warranty" for i in range(len(wc))]
    wc.loc[wc.index % 4 == 1, "recovery_status"] = "recovered"
    t2 = {**t, "warranty_claims": wc}
    a = detect.find_spikes(detect.claim_rates(t2, links), t2).iloc[0]
    assert a.exposure_usd == base.exposure_usd  # exposure counts every linked claim
    assert a.open_exposure_usd < 0.6 * a.exposure_usd  # ~half excluded (goodwill + already recovered)


def test_step_p_value():
    assert abs(detect.binom_cdf(0, 3, 0.5) - 0.125) < 1e-12
    assert detect.binom_cdf(3, 3, 0.5) == 1.0
    assert detect.step_p_value(5, 1000, 5, 1000) > 0.5      # same rate -> not significant
    assert detect.step_p_value(2, 1000, 30, 1000) < 0.001   # 15x jump -> significant
