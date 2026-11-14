"""The spend generator produces contract-valid, attributable data for every company profile."""
import pandas as pd
import pytest

from afterlife import check, generate_spend
from afterlife.generate import write
from afterlife.io import load
from afterlife.profiles import PROFILES, abbreviations_rows, dataset_info, failure_code_rows


@pytest.mark.parametrize("profile", PROFILES, ids=[p["company_id"] for p in PROFILES])
def test_spend_side_passes_contract_check(profile, tmp_path):
    spend = generate_spend.generate(7, profile)
    plan = spend.pop("_spike_plan")
    tables = {**spend, "abbreviations": abbreviations_rows(profile), "failure_codes": failure_code_rows(profile),
              "dataset_info": [{"key": k, "value": v} for k, v in dataset_info(profile).items()]}
    write(tables, tmp_path, profile["extract_format"])
    t = load(tmp_path)
    t["warranty_claims"] = pd.DataFrame(columns=check.CONTRACT["warranty_claims"])
    spikes = [plan] if plan else []
    t["truth_spikes"] = pd.DataFrame(spikes, columns=check.CONTRACT["truth_spikes"])
    if plan and profile["extract_format"] == "sap":   # write() would canonicalize this id for SAP companies
        from afterlife.adapters import sap
        t["truth_spikes"]["from_po_line_id"] = sap.canonical_po_id(t["truth_spikes"]["from_po_line_id"])
    check.results.clear()
    check.check(t)
    fails = [m for s, m in check.results if s == "FAIL"]
    assert not fails, fails
    assert len(t["part_master"]) == profile["n_parts"]
    assert (plan is None) == (profile["spike"] is None)


def test_generator_is_deterministic():
    a = generate_spend.generate(7, PROFILES[0])
    b = generate_spend.generate(7, PROFILES[0])
    assert a["production_spend"] == b["production_spend"] and a["build_supply"] == b["build_supply"]


def test_empty_table_is_written_with_header(tmp_path):
    """Northwind has no spike, so truth_spikes is empty; it must still load (found reviewing PR #4)."""
    write({"truth_spikes": []}, tmp_path)
    t = load(tmp_path)
    assert list(t["truth_spikes"].columns) == check.CONTRACT["truth_spikes"] and t["truth_spikes"].empty
