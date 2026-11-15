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


def pv_first_failure(p: float, years: int = P.HORIZON_YEARS, rate: float = P.OWNER_DISCOUNT_RATE.base) -> float:
    """PV-weighted chance the part fails (for the first time) within `years`: sum_t (1-p)^(t-1) p / (1+r)^t.
    A spare is used once, so only the first failure counts."""
    return sum((1 - p) ** (t - 1) * p / (1 + rate) ** t for t in range(1, years + 1))


def downtime_rescues(reg: dict, sourcing_recommendation: pd.DataFrame, spof_table: pd.DataFrame | None = None,
                     as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """One row per line-stopper that a sister-plant spare rescues: what one failure would cost with vs without it,
    the chance it fails within HORIZON_YEARS, and the expected PV avoided. Spares already on the plant's own shelf
    would have been used anyway, so they earn no credit. Low = low odds x fewest hours saved x low $/h (and so on)."""
    sr = sourcing_recommendation
    sp = spof_table if spof_table is not None else spof(reg, sr, as_of_year)
    cross = (sr.action == "use_shelf_spare") & (sr.spare_plant_id != sr.plant_id)
    sr_none = sr.copy()
    sr_none.loc[cross, ["action", "spare_id", "spare_plant_id"]] = ["monitor", "", ""]
    sp_none = spof(reg, sr_none, as_of_year)
    k = ["component_id", "hours_down_low", "hours_down_high", "loss_if_fails_low", "loss_if_fails_high"]
    m = sp_none.merge(sp[k], on="component_id", suffixes=("_none", ""))
    m = m.merge(sr[["component_id", "spare_id", "spare_plant_id"]], on="component_id", how="left")
    m = m[m.loss_if_fails_high_none > m.loss_if_fails_high]
    cols = ["component_id", "plant_id", "line_id", "spare_id", "spare_plant_id", "hours_down_without_low",
            "hours_down_without_high", "hours_down_with_low", "hours_down_with_high", "at_stake_low", "at_stake_base",
            "at_stake_high", "p_fail_horizon_low", "p_fail_horizon_base", "p_fail_horizon_high", "expected_pv_low",
            "expected_pv_base", "expected_pv_high", "horizon_years"]
    if m.empty:
        return pd.DataFrame(columns=cols)
    out = pd.DataFrame({"component_id": m.component_id, "plant_id": m.plant_id, "line_id": m.line_id,
                        "spare_id": m.spare_id, "spare_plant_id": m.spare_plant_id,
                        "hours_down_without_low": m.hours_down_low_none, "hours_down_without_high": m.hours_down_high_none,
                        "hours_down_with_low": m.hours_down_low, "hours_down_with_high": m.hours_down_high})
    # Loss avoided by one failure: low pairs the shortest outage without with the longest with (fewest hours saved).
    u = P.UNRECOVERED_SHARE
    save_lo = (m.hours_down_low_none - m.hours_down_high).clip(lower=0)
    save_hi = (m.hours_down_high_none - m.hours_down_low).clip(lower=0)
    save_base = ((m.hours_down_low_none + m.hours_down_high_none) - (m.hours_down_low + m.hours_down_high)) / 2
    out["at_stake_low"] = save_lo * m.downtime_cost_per_hour_low * u.low
    out["at_stake_high"] = save_hi * m.downtime_cost_per_hour_high * u.high
    out["at_stake_base"] = save_base * (m.downtime_cost_per_hour_low + m.downtime_cost_per_hour_high) / 2 * u.base
    T = P.HORIZON_YEARS
    for b, p in (("low", m.annual_failure_rate_low), ("base", m.annual_failure_rate), ("high", m.annual_failure_rate_high)):
        out[f"p_fail_horizon_{b}"] = 1 - (1 - p) ** T
        out[f"expected_pv_{b}"] = p.map(pv_first_failure) * out[f"at_stake_{b}"]
    out["horizon_years"] = T
    money = [c for c in cols if c.startswith(("at_stake", "expected_pv"))]
    out[money] = out[money].round(2)
    out[[c for c in cols if c.startswith("p_fail")]] = out[[c for c in cols if c.startswith("p_fail")]].round(3)
    return out[cols].sort_values("at_stake_base", ascending=False).reset_index(drop=True)


def _lever(plant_id, lever, lo, base, hi, one_time, in_base, basis):
    return {"plant_id": plant_id, "lever": lever, "savings_low": round(lo, 2), "savings_base": round(base, 2),
            "savings_high": round(hi, 2), "one_time": "yes" if one_time else "no",
            "in_price_base": "yes" if in_base else "no", "basis": basis}


def plant_savings(reg: dict, sourcing_recommendation: pd.DataFrame | None = None,
                  part_valuation: pd.DataFrame | None = None, spof_table: pd.DataFrame | None = None,
                  as_of_year: int = P.AS_OF_YEAR, full_plant: bool = False) -> pd.DataFrame:
    """Savings per owned plant per lever, low / base / high (per year unless one_time = yes).

    full_plant=True quotes a whole-plant scan: plant-level levers use 100% coverage, and register-level levers
    (sister spares, planned vs emergency) are extrapolated by 1 / coverage. Label it as extrapolated.
    Downtime avoided is never extrapolated: it only counts the rescues the register actually found."""
    pv = part_valuation if part_valuation is not None else value_parts(reg)
    sr = sourcing_recommendation if sourcing_recommendation is not None else recommend_sourcing(reg, pv, as_of_year)
    sp = spof_table if spof_table is not None else spof(reg, sr, as_of_year)
    rescues = downtime_rescues(reg, sr, sp, as_of_year)
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
        # Downtime avoided: expected PV over the horizon, one event per rescued part, shown per year. Not extrapolated.
        d, T = rescues[rescues.plant_id == plant_id], P.HORIZON_YEARS
        tot = d[["expected_pv_low", "expected_pv_base", "expected_pv_high"]].sum()
        rows.append(_lever(plant_id, "downtime_avoided", tot.expected_pv_low / T, tot.expected_pv_base / T,
                           tot.expected_pv_high / T, False, False,
                           f"{len(d)} sister-plant rescue(s): expected {T}-yr PV ${tot.expected_pv_base:,.0f} "
                           f"(per year shown), one failure per spare, outage capped, {P.UNRECOVERED_SHARE.base:.0%} of "
                           f"output unrecovered; scanned parts only, never extrapolated (shown, not priced)"))
    out = pd.DataFrame(rows)
    if full_plant:
        ext = out.lever != "downtime_avoided"
        out.loc[ext, "basis"] = "full plant, extrapolated from the register sample: " + out.loc[ext, "basis"]
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
