"""Build vs lifecycle cost, spare-part markups, price harmonization. [SPEND thread · Asher] Milestone M5.

All $ are analytics estimates (docs/research/warranty-accounting.md), never accruals or receivables.
Prices are compared per piece (match_spend.price_per_each: price unit + pack-size UoM).

  part_prices          per part: what we actually pay per piece in production (volume-weighted) and service
  build_cost           per product: sum(qty_per x actual production price per piece), std_cost as fallback
  lifecycle_cost       per product: build + spares + warranty per unit built, revenue, warranty % of revenue
  spare_markups        per part: service price vs production price for the SAME part -> spare overspend
  price_harmonization  per part: lines paid above the best (supplier, plant) price -> harmonization savings

Rules
  - Double-count rule (21b, data-contract.md "Cost rules"): warranty = claims parts_cost + labor_cost
    (+ other_cost, v4). service_spend with channel == "warranty_repair" is reconciliation only and is
    NEVER added; only channel == "spares" is added as spare cost.
  - $ that a savings ask relies on (markups, harmonization) only use links with confidence >= CONF_MIN:
    those are 99.9-100% correct on unseen companies (tests/test_match_spend.py).
No company, part or supplier is named in this file (tests/test_no_literals.py).
"""
import pandas as pd

from afterlife.match_spend import price_per_each

CONF_MIN = 0.8                  # links used for savings $
SPARES, WARRANTY_REPAIR = "spares", "warranty_repair"


def _lines(tables: dict[str, pd.DataFrame], links: pd.DataFrame, table: str, conf_min: float = 0.0) -> pd.DataFrame:
    """Spend lines of one table joined to their linked part, with per-piece price and quantity in pieces."""
    df = tables.get(table)
    if df is None or df.empty or links is None or links.empty:
        return pd.DataFrame()
    lk = links[(links.source_table == table) & (links.confidence >= conf_min)][["source_id", "part_no", "confidence"]]
    out = df.assign(po_line_id=df.po_line_id.astype(str)).drop(columns=["part_no"], errors="ignore").merge(
        lk.rename(columns={"source_id": "po_line_id"}), on="po_line_id")
    from afterlife.match_spend import pack_size
    out["price_ea"] = price_per_each(out)
    out["qty_ea"] = pd.to_numeric(out.qty, errors="coerce") * out.uom.map(pack_size)
    out["amount"] = out.price_ea * out.qty_ea
    return out


def _months_covered(*frames: pd.DataFrame) -> float:
    dates = pd.concat([pd.to_datetime(f.po_date, errors="coerce") for f in frames if len(f)])
    if dates.empty:
        return 12.0
    return max(1.0, (dates.max() - dates.min()).days / 30.44)


def part_prices(tables, links, conf_min: float = 0.0) -> pd.DataFrame:
    """part_no, prod_price_ea (volume-weighted), prod_qty_ea, best_price_ea (cheapest supplier x plant),
    svc_price_ea, svc_qty_ea, std_cost."""
    prod = _lines(tables, links, "production_spend", conf_min)
    svc = _lines(tables, links, "service_spend", conf_min)
    pm = tables["part_master"][["part_no", "std_cost"]].astype({"part_no": str})
    pm["std_cost"] = pd.to_numeric(pm.std_cost, errors="coerce")
    out = pm.copy()
    if len(prod):
        g = prod.groupby("part_no").agg(prod_amount=("amount", "sum"), prod_qty_ea=("qty_ea", "sum"))
        g["prod_price_ea"] = g.prod_amount / g.prod_qty_ea
        by_src = prod.groupby(["part_no", "supplier_id", "plant"]).agg(a=("amount", "sum"), q=("qty_ea", "sum"))
        g["best_price_ea"] = (by_src.a / by_src.q).groupby("part_no").min()
        out = out.merge(g[["prod_price_ea", "prod_qty_ea", "best_price_ea"]].reset_index(), on="part_no", how="left")
    if len(svc):
        s = svc.groupby("part_no").agg(svc_amount=("amount", "sum"), svc_qty_ea=("qty_ea", "sum"))
        s["svc_price_ea"] = s.svc_amount / s.svc_qty_ea
        out = out.merge(s[["svc_price_ea", "svc_qty_ea"]].reset_index(), on="part_no", how="left")
    for c in ["prod_price_ea", "prod_qty_ea", "best_price_ea", "svc_price_ea", "svc_qty_ea"]:
        if c not in out:
            out[c] = float("nan")
    return out


def build_cost(tables, links) -> pd.DataFrame:
    """product_id, build_cost (per unit), priced_from_spend (share of BOM cost priced from actual POs)."""
    pp = part_prices(tables, links)
    pp["unit_cost"] = pp.prod_price_ea.fillna(pp.std_cost)
    pp["from_spend"] = pp.prod_price_ea.notna()
    bom = tables["bom"].astype({"part_no": str}).merge(pp[["part_no", "unit_cost", "from_spend"]], on="part_no", how="left")
    bom["line_cost"] = pd.to_numeric(bom.qty_per) * bom.unit_cost
    g = bom.groupby("product_id")
    return pd.DataFrame({
        "build_cost": g.line_cost.sum().round(2),
        "priced_from_spend": (bom.line_cost.where(bom.from_spend, 0).groupby(bom.product_id).sum() / g.line_cost.sum()).round(3),
    }).reset_index()


def lifecycle_cost(tables, links) -> pd.DataFrame:
    """Per product: units_built, revenue, build_cost, spares_per_unit, warranty_per_unit, lifecycle_cost,
    warranty_pct_revenue, warranty_repair_spend (reconciliation only, NOT in lifecycle_cost)."""
    units = tables["builds"].assign(units_built=lambda d: pd.to_numeric(d.units_built)).groupby("product_id").units_built.sum()
    out = build_cost(tables, links).set_index("product_id")
    out["units_built"] = units
    asp = tables["products"].set_index("product_id").avg_selling_price.astype(float)
    out["revenue"] = (units * asp).round(2)

    # spares: allocate each part's spare spend to the products using it, by units x qty_per
    svc = _lines(tables, links, "service_spend")
    bom = tables["bom"].astype({"part_no": str})
    use = bom.assign(w=pd.to_numeric(bom.qty_per) * bom.product_id.map(units))
    use["w"] = use.w / use.groupby("part_no").w.transform("sum")
    spares = warranty_repair = pd.Series(0.0, index=out.index)
    if len(svc):
        by_part = svc.groupby(["part_no", "channel"]).amount.sum().unstack(fill_value=0.0)
        for channel in (SPARES, WARRANTY_REPAIR):
            if channel in by_part:
                alloc = use.merge(by_part[channel].rename("amt").reset_index(), on="part_no")
                s = (alloc.w * alloc.amt).groupby(alloc.product_id).sum().reindex(out.index, fill_value=0.0)
                if channel == SPARES:
                    spares = s
                else:
                    warranty_repair = s
    out["spares_per_unit"] = (spares / units).round(2)
    out["warranty_repair_spend"] = warranty_repair.round(2)   # 21b: reconciliation only, never added

    # warranty: the claims themselves (parts + labor + other), all claim types
    wc = tables.get("warranty_claims")
    if wc is not None and len(wc):
        cost = sum(pd.to_numeric(wc[c], errors="coerce").fillna(0) for c in ("parts_cost", "labor_cost", "other_cost") if c in wc)
        warranty = cost.groupby(wc.product_id).sum().reindex(out.index, fill_value=0.0)
    else:
        warranty = pd.Series(0.0, index=out.index)
    out["warranty_cost"] = warranty.round(2)
    out["warranty_per_unit"] = (warranty / units).round(2)
    out["lifecycle_cost"] = (out.build_cost + out.spares_per_unit + out.warranty_per_unit).round(2)
    out["warranty_pct_revenue"] = (100 * warranty / out.revenue).round(3)
    return out.reset_index()[["product_id", "units_built", "revenue", "build_cost", "spares_per_unit",
                              "warranty_per_unit", "lifecycle_cost", "warranty_pct_revenue", "warranty_cost",
                              "warranty_repair_spend", "priced_from_spend"]]


def spare_markups(tables, links) -> pd.DataFrame:
    """Same part bought by service vs production: part_no, description, prod_price_ea, svc_price_ea, ratio,
    svc_qty_ea, overspend_usd (whole period), overspend_usd_per_year. High-confidence links only."""
    pp = part_prices(tables, links, conf_min=CONF_MIN)
    m = pp[pp.prod_price_ea.notna() & pp.svc_price_ea.notna()].copy()
    m["ratio"] = (m.svc_price_ea / m.prod_price_ea).round(2)
    m["overspend_usd"] = ((m.svc_price_ea - m.prod_price_ea).clip(lower=0) * m.svc_qty_ea).round(2)
    months = _months_covered(_lines(tables, links, "service_spend"))
    m["overspend_usd_per_year"] = (m.overspend_usd * 12 / months).round(2)
    desc = tables["part_master"].astype({"part_no": str}).set_index("part_no").description
    m["description"] = m.part_no.map(desc)
    cols = ["part_no", "description", "prod_price_ea", "svc_price_ea", "ratio", "svc_qty_ea", "overspend_usd",
            "overspend_usd_per_year"]
    return m[cols].round({"prod_price_ea": 4, "svc_price_ea": 4}).sort_values("overspend_usd", ascending=False).reset_index(drop=True)


def price_harmonization(tables, links) -> pd.DataFrame:
    """Production lines paid above the best (supplier, plant) price for the same part: part_no, supplier_id,
    plant, price_ea, best_price_ea, qty_ea, savings_usd. Catches dual-source gaps and acquired-plant premiums."""
    prod = _lines(tables, links, "production_spend", CONF_MIN)
    if prod.empty:
        return pd.DataFrame(columns=["part_no", "supplier_id", "plant", "price_ea", "best_price_ea", "qty_ea", "savings_usd"])
    g = prod.groupby(["part_no", "supplier_id", "plant"]).agg(a=("amount", "sum"), qty_ea=("qty_ea", "sum")).reset_index()
    g["price_ea"] = g.a / g.qty_ea
    g["best_price_ea"] = g.groupby("part_no").price_ea.transform("min")
    g["savings_usd"] = ((g.price_ea - g.best_price_ea) * g.qty_ea).round(2)
    g = g[g.savings_usd > 0.005]
    return (g[["part_no", "supplier_id", "plant", "price_ea", "best_price_ea", "qty_ea", "savings_usd"]]
            .round({"price_ea": 4, "best_price_ea": 4}).sort_values("savings_usd", ascending=False).reset_index(drop=True))
