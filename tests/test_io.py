from afterlife.io import load, SAMPLE


def test_sample_loads_all_input_tables():
    t = load(SAMPLE)
    for name in ["products", "part_master", "bom", "builds", "production_spend",
                 "service_spend", "failure_codes", "warranty_claims"]:
        assert name in t and len(t[name]) > 0, name


def test_bom_parts_exist_in_part_master():
    t = load(SAMPLE)
    assert set(t["bom"].part_no) <= set(t["part_master"].part_no)


def test_sample_agreements_load_as_documents():
    t = load(SAMPLE)
    docs = t["supplier_agreements"]
    assert list(docs.columns) == ["doc_file", "text"] and len(docs) > 0
    assert set(t["truth_terms"].doc_file) <= set(docs.doc_file)
    assert docs.text.str.len().min() > 100


def test_sample_passes_contract_check():
    from afterlife import check
    check.results.clear()
    check.check(load(SAMPLE), is_sample=True)
    assert not [m for s, m in check.results if s == "FAIL"]
