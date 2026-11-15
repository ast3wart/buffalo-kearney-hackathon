"""Savings per plant per lever, and the price that follows from them (registry-format §7, model-spec §2).

price = value-capture % x auditable recurring savings (in_price_base = yes). The one-time spares release and
downtime avoided are shown, never priced. Parameters live in xray/params.py.
"""
import pandas as pd

from xray import params as P
from xray.sourcing import at_risk, component_view, num, recommend_sourcing, value_parts
from xray.valuation import failure_rate, replacement_cost, spof


def coverage_share(reg: dict) -> pd.DataFrame:
    """Share of each plant the register covers = machines in the register / estimated machines in the plant
    (employees x machines per employee). Plant-level levers are scaled by it (model-spec §2, coverage scaling)."""
    m = reg["machine"].merge(reg["line"][["line_id", "plant_id"]], on="line_id").groupby("plant_id").size().rename("n_machines")
    pl = reg["plant"].set_index("plant_id").join(m).fillna({"n_machines": 0})
    emp = num(pl.employees)
    est_lo, est_hi = emp * P.MACHINES_PER_EMPLOYEE.low, emp * P.MACHINES_PER_EMPLOYEE.high
    out = pd.DataFrame({"cov_low": (pl.n_machines / est_hi).clip(upper=1), "cov_high": (pl.n_machines / est_lo).clip(upper=1)})
    out["cov_base"] = (pl.n_machines / (emp * P.MACHINES_PER_EMPLOYEE.base)).clip(upper=1)
    return out.fillna(0)


def _lever(plant_id, lever, lo, base, hi, one_time, in_base, basis):
    return {"plant_id": plant_id, "lever": lever, "savings_low": round(lo, 2), "savings_base": round(base, 2),
            "savings_high": round(hi, 2), "one_time": "yes" if one_time else "no",
            "in_price_base": "yes" if in_base else "no", "basis": basis}


def plant_savings(reg: dict, sourcing_recommendation: pd.DataFrame | None = None,
                  part_valuation: pd.DataFrame | None = None, spof_table: pd.DataFrame | None = None,
                  as_of_year: int = P.AS_OF_YEAR, full_plant: bool = False) -> pd.DataFrame:
    """Savings per owned plant per lever, low / base / high (per year unless one_time = yes).

    full_plant=True quotes a whole-plant scan: plant-level levers use 100% coverage, and register-level levers
    (sister spares, planned vs emergency, downtime) are extrapolated by 1 / coverage. Label it as extrapolated."""
    pv = part_valuation if part_valuation is not None else value_parts(reg)
    sr = sourcing_recommendation if sourcing_recommendation is not None else recommend_sourcing(reg, pv, as_of_year)
    sp = spof_table if spof_table is not None else spof(reg, sr, as_of_year)
    # Downtime avoided = exposure without the sister-plant spares the register found, minus exposure with them.
    # A spare already on the plant's own shelf would have been used anyway, so it earns no credit.
    cross = (sr.action == "use_shelf_spare") & (sr.spare_plant_id != sr.plant_id)
    sr_none = sr.copy()
    sr_none.loc[cross, ["action", "spare_id", "spare_plant_id"]] = ["monitor", "", ""]
    sp_none = spof(reg, sr_none, as_of_year)
    cov = coverage_share(reg)
    fin = reg["plant_financials"].set_index("plant_id")
    cv = component_view(reg, as_of_year).set_index("component_id")
    rows = []
    for plant_id in reg["plant"].loc[reg["plant"].status == "owned", "plant_id"]:
        c, f = cov.loc[plant_id], fin.loc[plant_id]
        # Register-level levers scale up by 1 / coverage for a full-plant quote (low end uses the smaller factor).
        up = ((1 / max(c.cov_high, 1e-9), 1 / max(c.cov_base, 1e-9), 1 / max(c.cov_low, 1e-9)) if full_plant
              else (1, 1, 1))
        if full_plant:
            c = pd.Series({"cov_low": 1.0, "cov_base": 1.0, "cov_high": 1.0})
        inv = (num(pd.Series([f.spares_inventory_value_low])).iloc[0], num(pd.Series([f.spares_inventory_value_high])).iloc[0])
        carry = (float(f.carrying_cost_pct_low), float(f.carrying_cost_pct_high))
        rush = (float(f.rush_premium_annual_low), float(f.rush_premium_annual_high))
        ex = P.EXCESS_SPARES_PCT
        rel = (ex.low * inv[0] * c.cov_low, ex.base * sum(inv) / 2 * c.cov_base, ex.high * inv[1] * c.cov_high)
        rows.append(_lever(plant_id, "carrying_cost_avoided", rel[0] * carry[0], rel[1] * sum(carry) / 2, rel[2] * carry[1],
                           False, True, f"excess spares {ex.low:.0%}-{ex.high:.0%} x carrying % x coverage "
                                        f"{c.cov_low:.1%}-{c.cov_high:.1%}"))
        rs = P.RUSH_SHARE_AVOIDED
        rows.append(_lever(plant_id, "rush_premiums_avoided", rush[0] * rs.low * c.cov_low,
                           sum(rush) / 2 * rs.base * c.cov_base, rush[1] * rs.high * c.cov_high, False, True,
                           f"rush premiums x {rs.low:.0%}-{rs.high:.0%} avoided x coverage"))
        # Per event, annualised: P(fail) x (part value - transfer cost) for each sister-plant spare we'd use.
        sis = sr[(sr.plant_id == plant_id) & (sr.action == "use_shelf_spare") & (sr.spare_plant_id != plant_id)]
        lo = base = hi = 0.0
        for r in sis.itertuples():
            fr = failure_rate(cv.loc[r.component_id, "age"])
            net_lo = max((r.part_value_low if pd.notna(r.part_value_low) else 0) - r.transfer_cost_high, 0)
            net_hi = max((r.part_value_high if pd.notna(r.part_value_high) else 0) - r.transfer_cost_low, 0)
            lo, base, hi = lo + fr.low * net_lo, base + fr.base * (net_lo + net_hi) / 2, hi + fr.high * net_hi
        rows.append(_lever(plant_id, "sister_spare_purchases_avoided", lo * up[0], base * up[1], hi * up[2], False, True,
                           f"{len(sis)} sister-plant spare(s): P(fail) x (part value - transfer cost)"))
        # Planned vs emergency replacement for at-risk parts, haircut before it enters the price base.
        risk = cv[(cv.plant_id == plant_id) & at_risk(cv)]
        lo = base = hi = 0.0
        m = P.EMERGENCY_MULTIPLIER
        for comp in risk.itertuples():
            fr = failure_rate(comp.age)
            clo, chi = replacement_cost(comp, reg, pv)
            lo += fr.low * (m.low - 1) * clo
            base += fr.base * (m.base - 1) * (clo + chi) / 2
            hi += fr.high * (m.high - 1) * chi
        h = P.EMERGENCY_HAIRCUT
        rows.append(_lever(plant_id, "planned_vs_emergency", lo * h * up[0], base * h * up[1], hi * h * up[2], False, True,
                           f"{len(risk)} at-risk part(s): P(fail) x (emergency - planned), {h:.0%} haircut"))
        rows.append(_lever(plant_id, "spares_inventory_released", *rel, True, False,
                           "one-time cash freed: excess spares x coverage (not priced)"))
        d_with, d_none = sp[sp.plant_id == plant_id], sp_none[sp_none.plant_id == plant_id]
        lo = max(d_none.downtime_exposure_per_year_low.sum() - d_with.downtime_exposure_per_year_low.sum(), 0)
        hi = max(d_none.downtime_exposure_per_year_high.sum() - d_with.downtime_exposure_per_year_high.sum(), 0)
        lo, hi = lo * up[0], hi * up[2]
        rows.append(_lever(plant_id, "downtime_avoided", lo, (lo + hi) / 2, hi, False, False,
                           "expected value from spof, no defensible baseline (shown, not priced)"))
    out = pd.DataFrame(rows)
    if full_plant:
        out["basis"] = "full plant, extrapolated from the register sample: " + out.basis
    return out


def price(plant_savings: pd.DataFrame, value_capture_pct: float = P.VALUE_CAPTURE_PCT.base) -> pd.DataFrame:
    """Price per plant = capture % x auditable recurring savings; payback; and the plant-level price checks
    (model-spec §2: 1 ROI/payback, 2 approval ceiling, 3 comparables, 5 gross margin after cost to serve).
    Check 4 (deal fee vs what the scan finds) is per company: see deal_fee_check."""
    base = plant_savings[(plant_savings.in_price_base == "yes") & (plant_savings.one_time == "no")]
    s = base.groupby("plant_id")[["savings_low", "savings_base", "savings_high"]].sum()
    s = s.reindex(plant_savings.plant_id.unique()).fillna(0)
    rows = []
    for plant_id, r in s.iterrows():
        p_lo, p_base, p_hi = (value_capture_pct * r.savings_low, value_capture_pct * r.savings_base,
                              value_capture_pct * r.savings_high)
        payback = p_base / (r.savings_base / 12) if r.savings_base > 0 else float("inf")
        failed = []
        if r.savings_base < P.MIN_CUSTOMER_ROI * p_base or payback > P.MAX_PAYBACK_MONTHS or p_base <= 0:
            failed.append("roi_payback")
        if p_hi > P.APPROVAL_CEILING.high:
            failed.append("approval_ceiling")
        band_lo, band_hi = P.COMPARABLE_BAND
        if not band_lo * P.COMPARABLES.low <= p_base <= band_hi * P.COMPARABLES.high:
            failed.append("comparables")
        if p_base <= 0 or (p_base - P.COST_TO_SERVE.base) / p_base < P.MIN_GROSS_MARGIN:
            failed.append("gross_margin")
        rows.append({"plant_id": plant_id, "price_per_plant_low": round(p_lo, 2), "price_per_plant_high": round(p_hi, 2),
                     "value_capture_pct": value_capture_pct, "customer_payback_months": round(payback, 1),
                     "failed_checks": ";".join(failed), "price_per_plant_base": round(p_base, 2),
                     "recurring_savings_base": round(r.savings_base, 2)})
    return pd.DataFrame(rows)


def deal_fee_check(deal_adjustment: pd.DataFrame, deal_fee: float) -> pd.DataFrame:
    """Check 4: the deal fee should be a small share (<= MAX_DEAL_FEE_SHARE) of the price cut the scan finds."""
    d = deal_adjustment[["company_id", "suggested_price_reduction_low"]].copy()
    d["deal_fee"] = deal_fee
    d["fee_share"] = (deal_fee / d.suggested_price_reduction_low).round(3)
    d["failed_checks"] = d.fee_share.map(lambda x: "" if x <= P.MAX_DEAL_FEE_SHARE else "deal_fee_share")
    return d
