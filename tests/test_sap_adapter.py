"""v3 #15: a company delivered as a raw SAP extract loads into exactly our contract."""
import pandas as pd

from afterlife.adapters import sap
from afterlife.io import SAMPLE


def test_sap_round_trip_production_spend():
    ours = pd.read_csv(SAMPLE / "production_spend.csv", dtype=str, keep_default_na=False, na_values=[""])
    raw = sap.from_contract("production_spend", ours)
    assert {"EBELN", "EBELP", "MATNR", "LIFNR", "NETPR", "PEINH", "BEDAT"} <= set(raw.columns)
    assert raw.BEDAT.str.fullmatch(r"\d{8}").all()                  # YYYYMMDD like SAP
    assert sap.looks_like_sap(raw)
    back = sap.to_contract("production_spend", raw)
    assert set(ours.columns) <= set(back.columns)
    pd.testing.assert_series_equal(back.po_date.astype(str), ours.po_date.astype(str), check_names=False)
    assert pd.to_numeric(back.unit_price).round(2).tolist() == pd.to_numeric(ours.unit_price).round(2).tolist()
    assert back.supplier_id.tolist() == ours.supplier_id.tolist()
    # po_line_id changes form on the round trip, to exactly canonical_po_id (CP1 review finding)
    assert back.po_line_id.tolist() == sap.canonical_po_id(ours.po_line_id).tolist()


def test_sap_quirks_leading_zeros_and_decimal_comma():
    raw = pd.DataFrame({"EBELN": ["4500000012"], "EBELP": ["00010"], "MATNR": ["000000000100447102"],
                        "LIFNR": ["0000100011"], "NETPR": ["4,12"], "PEINH": ["1"], "BEDAT": ["20260211"],
                        "TXZ01": ["Deep groove ball bearing"]})
    out = sap.to_contract("production_spend", raw)
    assert out.loc[0, "part_no"] == "100447102"
    assert out.loc[0, "supplier_id"] == "100011"
    assert out.loc[0, "unit_price"] == 4.12
    assert out.loc[0, "po_date"] == "2026-02-11"
    assert out.loc[0, "po_line_id"] == "4500000012-00010"


def test_sap_company_still_joins_after_write_and_load(tmp_path):
    """Write the sample as if it were an SAP-format company, load it back, run the full contract check.
    Catches broken joins between spend (SAP ids) and build_supply / truth_links / truth_spikes."""
    from afterlife import check
    from afterlife.generate import write
    from afterlife.io import load
    tables = {f.stem: pd.read_csv(f, dtype=str, keep_default_na=False).to_dict("records")
              for f in SAMPLE.glob("*.csv")}
    write(tables, tmp_path, extract_format="sap")
    raw = pd.read_csv(tmp_path / "production_spend.csv", dtype=str)
    assert {"EBELN", "MATNR", "LIFNR"} <= set(raw.columns)          # really written as SAP
    check.results.clear()
    check.check(load(tmp_path), is_sample=True)
    fails = [m for s, m in check.results if s == "FAIL"]
    assert not fails, fails
