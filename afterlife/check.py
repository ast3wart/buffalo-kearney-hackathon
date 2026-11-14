"""Compatibility check: run this at the start of every checkpoint.

    python -m afterlife.check            # checks every company in data/generated/ (or data/sample/ fallback)
    python -m afterlife.check sample     # force data/sample/
    python -m afterlife.check spend      # generated companies, spend side only (before the claims generator exists)

Checks the data against docs/build/data-contract.md, cross-table consistency
(the things that silently break the other person's code), and whether the
frontend's API types are stale. Exit code 1 if anything FAILS.
If you change the contract, update CONTRACT here in the same commit.
"""
import json
import sys
import pandas as pd
from afterlife.io import ROOT, SAMPLE, companies, load
from afterlife.taxonomy import CATEGORIES, FAILURE_CODES

CONTRACT = {
    "products": ["product_id", "product_name", "family", "avg_selling_price"],
    "part_master": ["part_no", "description", "category", "std_cost"],
    "bom": ["product_id", "part_no", "qty_per", "position"],
    "builds": ["product_id", "build_month", "units_built"],
    "production_spend": ["po_line_id", "part_no", "supplier_id", "supplier_name", "supplier_pn", "description",
                         "qty", "uom", "unit_price", "price_unit", "po_date", "plant", "country"],
    "service_spend": ["po_line_id", "part_no", "supplier_id", "supplier_name", "supplier_pn", "description",
                      "qty", "uom", "unit_price", "price_unit", "po_date", "plant", "country", "channel"],
    "info_records": ["part_no", "supplier_id", "supplier_pn"],
    "build_supply": ["product_id", "build_month", "part_no", "supplier_id", "po_line_id", "share"],
    "abbreviations": ["abbr", "expansion"],
    "dataset_info": ["key", "value"],
    "failure_codes": ["failure_code", "system", "description", "likely_categories"],
    "warranty_claims": ["claim_id", "product_id", "serial_no", "build_month", "failure_date", "claim_date",
                        "paid_date", "claim_type", "failure_code", "claim_text", "causal_part_no", "labor_hrs", "parts_cost",
                        "labor_cost", "other_cost", "dealer_id", "recovery_status", "recovered_usd"],
    "truth_links": ["source_table", "source_id", "part_no"],
    "truth_spikes": ["part_no", "supplier_id", "start_build_month", "from_po_line_id", "multiplier"],
    "truth_terms": ["doc_file", "supplier_id", "recovery_pct", "labor_covered", "labor_rate_cap",
                    "recovery_window_months", "filing_deadline_days"],
}
RECOVERY_STATUSES = {"none", "submitted", "recovered"}
CLAIM_TYPES = {"warranty", "goodwill", "campaign"}

results: list[tuple[str, str]] = []


def ok(msg): results.append(("PASS", msg))
def fail(msg): results.append(("FAIL", msg))
def warn(msg): results.append(("WARN", msg))


def check(t, is_sample: bool = False):
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
    asp = pd.to_numeric(t["products"].avg_selling_price, errors="coerce")
    (ok if (asp > 0).all() else fail)("products.avg_selling_price is positive (warranty % of revenue needs it)")
    if not is_sample:   # generated prices are build cost x markup; the sample BOM is only 8 parts
        pm_cost = pd.to_numeric(t["part_master"].set_index("part_no").std_cost)
        b = t["bom"].assign(c=lambda d: pd.to_numeric(d.qty_per) * d.part_no.map(pm_cost))
        build = b.groupby("product_id").c.sum()
        margin = t["products"].set_index("product_id").avg_selling_price.astype(float) / build
        (ok if (margin > 1).all() else fail)(f"avg_selling_price above build cost for every product (markup {margin.min():.2f}–{margin.max():.2f}x)")
    info = dict(zip(t["dataset_info"].key, t["dataset_info"].value))
    need = {"company_id", "company_name", "industry", "data_as_of", "first_build_month", "last_build_month", "currency", "warranty_months", "mis_window"}
    (ok if need <= set(info) else fail)("dataset_info has all keys" if need <= set(info) else f"dataset_info missing {sorted(need - set(info))}")

    # 1b. CP0 taxonomy is respected
    bad_cat = set(t["part_master"].category) - set(CATEGORIES)
    (ok if not bad_cat else fail)("part categories all in the CP0 list" if not bad_cat else f"categories not in CP0 list: {sorted(bad_cat)}")
    allowed_codes = {f["failure_code"] for f in FAILURE_CODES}
    bad_code = set(t["failure_codes"].failure_code) - allowed_codes
    (ok if not bad_code else fail)("failure codes are a subset of the taxonomy union" if not bad_code else f"failure codes not in taxonomy: {sorted(bad_code)}")
    ab = t["abbreviations"]
    (ok if len(ab) and ab.abbr.is_unique else fail)(f"abbreviations: {len(ab)} unique entries (company shorthand, v3 #10)")

    # 1c. spend-side SAP fields (💲)
    all_po = pd.concat([t["production_spend"].po_line_id, t["service_spend"].po_line_id]).astype("string")
    bad = all_po.isna() | (all_po.str.strip() == "")
    (ok if not bad.any() else fail)("every spend line has a po_line_id" if not bad.any()
                                    else f"{int(bad.sum())} spend lines have an empty po_line_id")
    dup = all_po[~bad].duplicated()
    (ok if not dup.any() else fail)("po_line_id is unique across production + service spend" if not dup.any()
                                    else f"{int(dup.sum())} duplicate po_line_ids, e.g. {all_po[~bad][dup].head(3).tolist()}")
    for src in ["production_spend", "service_spend"]:
        df = t[src]
        known = df.part_no.dropna()
        (ok if set(known) <= parts else fail)(f"{src}.part_no values (when present) exist in part_master")
        pu = pd.to_numeric(df.price_unit, errors="coerce")
        (ok if (pu >= 1).all() and (pu % 1 == 0).all() else fail)(f"{src}.price_unit is a whole number >= 1")
    fill_p = t["production_spend"].part_no.notna().mean()
    fill_s = t["service_spend"].part_no.notna().mean()
    (ok if fill_p > fill_s else warn)(f"part_no filled: production {fill_p:.0%} vs service {fill_s:.0%} (target ~85% vs ~15%)")
    ir = t["info_records"]
    (ok if set(ir.part_no) <= parts else fail)("info_records parts exist in part_master")

    # 1d. build_supply: lots consumed per product/month (v3 #13)
    bs = t["build_supply"]
    ps = t["production_spend"]
    bom_pairs = set(zip(t["bom"].product_id, t["bom"].part_no))
    (ok if set(zip(bs.product_id, bs.part_no)) <= bom_pairs else fail)("build_supply (product, part) pairs are all in the BOM")
    built_keys = set(zip(t["builds"].product_id, t["builds"].build_month))
    (ok if set(zip(bs.product_id, bs.build_month)) <= built_keys else fail)("build_supply months all exist in builds")
    po_sup = dict(zip(ps.po_line_id, ps.supplier_id))
    bad_po = [(po, s) for po, s in zip(bs.po_line_id, bs.supplier_id) if po_sup.get(po) != s]
    (ok if not bad_po else fail)("build_supply lots are production PO lines from the same supplier" if not bad_po
                                 else f"{len(bad_po)} build_supply rows point at a PO line from another supplier or none, e.g. {bad_po[:2]}")
    sums = pd.to_numeric(bs.share).groupby([bs.product_id, bs.build_month, bs.part_no]).sum()
    (ok if ((sums - 1).abs() < 1e-6).all() else fail)("build_supply shares sum to 1 per (product, month, part)")
    covered = set(zip(bs.product_id, bs.part_no))
    (ok if bom_pairs <= covered else warn)("every BOM line has build_supply rows" if bom_pairs <= covered
                                           else f"{len(bom_pairs - covered)} BOM lines have no build_supply rows")
    (ok if not (set(ir.supplier_id) & set(t["service_spend"].supplier_id) - set(t["production_spend"].supplier_id)) else warn)(
        "service-only distributors have no info records (that's the point)")
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
    # 2b. claim dates make sense for months-in-service (🛠)
    as_of = info.get("data_as_of")
    if as_of:
        fd = pd.to_datetime(t["warranty_claims"].failure_date)
        bm = pd.to_datetime(t["warranty_claims"].build_month + "-01")
        (ok if (fd <= pd.Timestamp(as_of)).all() else fail)(f"no claim fails after data_as_of ({as_of})")
        (ok if (fd >= bm).all() else fail)("no claim fails before its build month")
        # 2c. v4 accounting fields: reporting lag, payment, recovery (🛠)
        wc = t["warranty_claims"]
        cd, pd_ = pd.to_datetime(wc.claim_date), pd.to_datetime(wc.paid_date)
        (ok if ((cd >= fd) & (cd <= pd.Timestamp(as_of))).all() else fail)(
            "claim_date is between failure_date and data_as_of (claims not yet reported are absent)")
        (ok if (pd_.isna() | ((pd_ >= cd) & (pd_ <= pd.Timestamp(as_of)))).all() else fail)(
            "paid_date is blank (unpaid) or between claim_date and data_as_of")
        status = wc.recovery_status
        (ok if set(status) <= RECOVERY_STATUSES else fail)(f"recovery_status in {sorted(RECOVERY_STATUSES)}")
        (ok if not (pd_.isna() & (status != "none")).any() else fail)("only paid claims are submitted for recovery")
        (ok if set(wc.claim_type) <= CLAIM_TYPES else fail)(f"claim_type in {sorted(CLAIM_TYPES)} (21c)")
        (ok if not ((wc.claim_type != "warranty") & (status != "none")).any() else fail)(
            "goodwill and campaign claims are never submitted for supplier recovery")
        rec = pd.to_numeric(wc.recovered_usd)
        cost = pd.to_numeric(wc.parts_cost) + pd.to_numeric(wc.labor_cost) + pd.to_numeric(wc.other_cost)
        (ok if ((rec == 0) | (status == "recovered")).all() and (rec <= cost + 0.01).all() else fail)(
            "recovered_usd > 0 only on recovered claims, and never above the claim's total cost")
    # 2d. supplier agreements are documents; the answer key points at real files and production suppliers
    tt = t["truth_terms"]
    docs = set(t["supplier_agreements"].doc_file) if "supplier_agreements" in t else set()
    (ok if set(tt.doc_file) <= docs else fail)(
        f"every truth_terms doc_file exists in supplier_agreements/ ({len(docs)} documents)" if set(tt.doc_file) <= docs
        else f"truth_terms points at missing documents: {sorted(set(tt.doc_file) - docs)[:3]}")
    prod_sup = set(t["production_spend"].supplier_id)
    (ok if set(tt.supplier_id) <= prod_sup else fail)("truth_terms suppliers are production suppliers")
    (ok if prod_sup <= set(tt.supplier_id) else warn)(
        "every production supplier has an agreement" if prod_sup <= set(tt.supplier_id)
        else f"{len(prod_sup - set(tt.supplier_id))} production suppliers have no agreement (recovery can't be valued)")
    tp = t.get("truth_prices")
    if tp is not None and len(tp):   # price schedules in the agreements (💲, generated companies)
        (ok if set(tp.doc_file) <= docs else fail)("every truth_prices doc_file exists in supplier_agreements/")
        (ok if set(tp.part_no.astype(str)) <= set(t["part_master"].part_no) else fail)("truth_prices parts exist in part_master")
        (ok if set(tp.supplier_id.astype(str)) <= prod_sup else fail)("truth_prices suppliers are production suppliers")
        (ok if (pd.to_numeric(tp.contract_price_ea) > 0).all() else fail)("truth_prices.contract_price_ea is positive")
    pct = pd.to_numeric(tt.recovery_pct)
    (ok if ((pct > 0) & (pct <= 1)).all() else fail)("truth_terms.recovery_pct is in (0, 1]")
    codes = set(t["failure_codes"].failure_code)
    (ok if set(t["warranty_claims"].failure_code) <= codes else fail)("claim failure codes all defined")
    cats = set(t["part_master"].category)
    fc_cats = {c for s in t["failure_codes"].likely_categories for c in str(s).split(";")}
    if not is_sample:  # the tiny sample only uses 8 categories, so this only matters for generated data
        # a code may list categories this company doesn't make (e.g. ELE-FTS -> fuel at an HVAC maker);
        # what matters is that every code can point at SOME part
        dead = [r.failure_code for r in t["failure_codes"].itertuples()
                if not set(str(r.likely_categories).split(";")) & cats]
        (ok if not dead else fail)("every failure code has at least one category with parts" if not dead
                                   else f"failure codes with no matching parts at all: {dead}")

    # 3. answer key covers everything and points at real parts
    tl = t["truth_links"]
    for src, idcol in [("production_spend", "po_line_id"), ("service_spend", "po_line_id"), ("warranty_claims", "claim_id")]:
        ids, keyed = set(t[src][idcol]), set(tl[tl.source_table == src].source_id)
        (ok if ids == keyed else fail)(f"truth_links covers all {src}" if ids == keyed
                                       else f"truth_links mismatch for {src}: {len(ids - keyed)} unkeyed, {len(keyed - ids)} orphan")
    (ok if set(tl.part_no) <= parts else fail)("truth_links parts all exist in part_master")
    sp = t["truth_spikes"]
    (ok if set(sp.part_no) <= set(t["bom"].part_no) else fail)("spike part is in a BOM")
    for row in sp.itertuples():
        (ok if po_sup.get(row.from_po_line_id) == row.supplier_id else fail)(
            f"spike lot {row.from_po_line_id} is a production PO line from {row.supplier_id}")
        sup_rows = bs[bs.part_no == row.part_no]
        n_sup = sup_rows.supplier_id.nunique()
        (ok if n_sup >= 2 else warn)(f"spike part has {n_sup} suppliers (needs 2+ so 'which supplier' is a real question)")
        if n_sup >= 2:
            share = sup_rows[sup_rows.supplier_id == row.supplier_id].set_index(["product_id", "build_month"]).share
            varies = pd.to_numeric(share).nunique() > 1 or len(share) < len(sup_rows.groupby(["product_id", "build_month"]))
            (ok if varies else fail)("spiking supplier's share varies across products/months (else attribution is impossible)")
    shared = t["bom"].groupby("part_no").product_id.nunique()
    if len(sp) and shared.get(sp.part_no.iloc[0], 0) < 2:
        warn("spike part is used in only 1 product, so the cross-product story won't show")

    # 4. realism sanity (warnings, not failures)
    if len(t["warranty_claims"]):
        blank = t["warranty_claims"].causal_part_no.isna().mean()
        (ok if 0.4 <= blank <= 0.8 else warn)(f"claims with blank causal_part_no: {blank:.0%} (target ~60%)")
    if not is_sample:  # sample is too small for realism stats
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
    targets = [("sample", SAMPLE)] if "sample" in sys.argv[1:] else companies(require_claims=False)
    spend_only = "spend" in sys.argv[1:]   # claims generator not built yet: check the spend side only
    for cid, d in targets:
        before = len(results)
        tables = load(d)
        if spend_only or "warranty_claims" not in tables:
            if "warranty_claims" not in tables:
                warn(f"no claims yet (claims generator not built): checking the spend side only")
            for name in ["warranty_claims", "truth_spikes", "truth_terms"]:
                tables.setdefault(name, pd.DataFrame(columns=CONTRACT[name]))
        check(tables, is_sample=(d == SAMPLE))
        for i in range(before, len(results)):
            results[i] = (results[i][0], f"[{cid}] {results[i][1]}")
    check_api_types()
    for status, msg in results:
        print(f"  {'✓' if status == 'PASS' else '✗' if status == 'FAIL' else '!'} {status}  {msg}")
    n_fail = sum(s == "FAIL" for s, _ in results)
    print(f"\n{n_fail} failing, {sum(s == 'WARN' for s, _ in results)} warnings")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
