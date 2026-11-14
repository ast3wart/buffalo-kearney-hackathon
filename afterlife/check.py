"""Compatibility check: run this at the start of every checkpoint.

    python -m afterlife.check            # checks data/generated/ (or data/sample/ fallback)
    python -m afterlife.check sample     # force data/sample/

Checks the data against docs/build/data-contract.md, cross-table consistency
(the things that silently break the other person's code), and whether the
frontend's API types are stale. Exit code 1 if anything FAILS.
If you change the contract, update CONTRACT here in the same commit.
"""
import json
import sys
from afterlife.io import ROOT, SAMPLE, data_dir, load

CONTRACT = {
    "products": ["product_id", "product_name", "family"],
    "part_master": ["part_no", "description", "category", "std_cost"],
    "bom": ["product_id", "part_no", "qty_per", "position"],
    "builds": ["product_id", "build_month", "units_built"],
    "production_spend": ["po_line_id", "supplier_id", "supplier_name", "supplier_pn", "description",
                         "qty", "uom", "unit_price", "po_date", "plant", "country"],
    "service_spend": ["po_line_id", "supplier_id", "supplier_name", "supplier_pn", "description",
                      "qty", "uom", "unit_price", "po_date", "plant", "country", "channel"],
    "failure_codes": ["failure_code", "system", "description", "likely_categories"],
    "warranty_claims": ["claim_id", "product_id", "serial_no", "build_month", "failure_date", "failure_code",
                        "claim_text", "causal_part_no", "labor_hrs", "parts_cost", "labor_cost", "dealer_id",
                        "recovery_status"],
    "truth_links": ["source_table", "source_id", "part_no"],
    "truth_spikes": ["part_no", "supplier_id", "start_build_month", "multiplier"],
}

results: list[tuple[str, str]] = []


def ok(msg): results.append(("PASS", msg))
def fail(msg): results.append(("FAIL", msg))
def warn(msg): results.append(("WARN", msg))


def check(t):
    # 1. every table present with exactly the contract's columns
    for name, cols in CONTRACT.items():
        if name not in t:
            fail(f"{name}: missing file")
            continue
        have = list(t[name].columns)
        missing, extra = [c for c in cols if c not in have], [c for c in have if c not in cols]
        if missing:
            fail(f"{name}: missing columns {missing}")
        elif extra:
            warn(f"{name}: extra columns {extra} (add them to the contract or drop them)")
        else:
            ok(f"{name}: {len(t[name])} rows, columns match")
    if any(r[0] == "FAIL" and "missing" in r[1] for r in results):
        return

    parts = set(t["part_master"].part_no)
    prods = set(t["products"].product_id)
    # 2. keys line up across the spend side (Asher) and claims side (Brandon)
    (ok if set(t["bom"].part_no) <= parts else fail)("bom parts all exist in part_master")
    (ok if set(t["bom"].product_id) <= prods else fail)("bom products all exist in products")
    (ok if set(t["warranty_claims"].product_id) <= prods else fail)("claim products all exist in products")
    built = set(zip(t["builds"].product_id, t["builds"].build_month))
    claim_keys = set(zip(t["warranty_claims"].product_id, t["warranty_claims"].build_month))
    missing_builds = claim_keys - built
    (ok if not missing_builds else fail)(
        "every claim's (product, build_month) has a builds row" if not missing_builds
        else f"{len(missing_builds)} claim (product, build_month) pairs have no builds row, e.g. {sorted(missing_builds)[:3]}")
    codes = set(t["failure_codes"].failure_code)
    (ok if set(t["warranty_claims"].failure_code) <= codes else fail)("claim failure codes all defined")
    cats = set(t["part_master"].category)
    fc_cats = {c for s in t["failure_codes"].likely_categories for c in str(s).split(";")}
    (ok if fc_cats <= cats else warn)(
        "failure-code categories all exist in part_master" if fc_cats <= cats
        else f"failure-code categories not in part_master: {sorted(fc_cats - cats)}")

    # 3. answer key covers everything and points at real parts
    tl = t["truth_links"]
    for src, idcol in [("production_spend", "po_line_id"), ("service_spend", "po_line_id"), ("warranty_claims", "claim_id")]:
        ids, keyed = set(t[src][idcol]), set(tl[tl.source_table == src].source_id)
        (ok if ids == keyed else fail)(f"truth_links covers all {src}" if ids == keyed
                                       else f"truth_links mismatch for {src}: {len(ids - keyed)} unkeyed, {len(keyed - ids)} orphan")
    (ok if set(tl.part_no) <= parts else fail)("truth_links parts all exist in part_master")
    sp = t["truth_spikes"]
    (ok if set(sp.part_no) <= set(t["bom"].part_no) else fail)("spike part is in a BOM")
    shared = t["bom"].groupby("part_no").product_id.nunique()
    if len(sp) and shared.get(sp.part_no.iloc[0], 0) < 2:
        warn("spike part is used in only 1 product, so the cross-product story won't show")

    # 4. realism sanity (warnings, not failures)
    blank = t["warranty_claims"].causal_part_no.isna().mean()
    (ok if 0.4 <= blank <= 0.8 else warn)(f"claims with blank causal_part_no: {blank:.0%} (target ~60%)")
    share = (shared >= 2).mean()
    (ok if 0.25 <= share <= 0.6 else warn)(f"parts shared across products: {share:.0%} (target ~40%)")


def check_api_types():
    spec_file = ROOT / "web" / "openapi.json"
    try:
        from api.main import app
        live = app.openapi()
    except Exception as e:  # noqa: BLE001
        warn(f"could not import API to compare types: {e}")
        return
    if not spec_file.exists() or json.loads(spec_file.read_text()) != live:
        fail("web/openapi.json is stale. Run: python scripts/export_openapi.py && (cd web && npm run types:api)")
    else:
        ok("frontend API types match the API")


def main():
    d = SAMPLE if "sample" in sys.argv[1:] else data_dir()
    print(f"Checking {d.relative_to(ROOT)}\n")
    check(load(d))
    check_api_types()
    for status, msg in results:
        print(f"  {'✓' if status == 'PASS' else '✗' if status == 'FAIL' else '!'} {status}  {msg}")
    n_fail = sum(s == "FAIL" for s, _ in results)
    print(f"\n{n_fail} failing, {sum(s == 'WARN' for s, _ in results)} warnings")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
