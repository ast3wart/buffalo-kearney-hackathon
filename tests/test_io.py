from afterlife.io import load, SAMPLE


def test_sample_loads_all_input_tables():
    t = load(SAMPLE)
    for name in ["products", "part_master", "bom", "builds", "production_spend",
                 "service_spend", "failure_codes", "warranty_claims"]:
        assert name in t and len(t[name]) > 0, name


def test_bom_parts_exist_in_part_master():
    t = load(SAMPLE)
    assert set(t["bom"].part_no) <= set(t["part_master"].part_no)


def test_sample_passes_contract_check():
    from afterlife import check
    check.results.clear()
    check.check(load(SAMPLE))
    assert not [m for s, m in check.results if s == "FAIL"]
