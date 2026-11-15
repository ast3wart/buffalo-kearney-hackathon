"""Single points of failure, the CapEx cliff and the deal lens (registry-format §7, model-spec §1-2).

Pure functions: `reg` + upstream outputs in, DataFrames out. Parameters live in xray/params.py.
"""
import numpy as np
import pandas as pd

from xray import params as P
from xray.sourcing import (AT_RISK_STATUS, component_view, num, recommend_sourcing, scored_listings, unit_cost)


def downtime_cost_per_hour(reg: dict) -> pd.DataFrame:
    """Derived $/h per line = revenue_per_day / operating_hours_per_day x contribution margin; a typed-in
    downtime_cost_per_hour_low/high overrides it (registry-format §4)."""
    ln = reg["line"].copy()
    hours = num(ln.operating_hours_per_day)
    for b in ("low", "high"):
        derived = num(ln[f"revenue_per_day_{b}"]) / hours * num(ln.contribution_margin_pct)
        ln[f"dph_{b}"] = num(ln.get(f"downtime_cost_per_hour_{b}")).fillna(derived)
    return ln.assign(op_hours=hours)[["line_id", "plant_id", "op_hours", "dph_low", "dph_high"]]


def failure_rate(age: float, kb_low=np.nan, kb_high=np.nan) -> P.P:
    """Annual failure probability: the KB override if typed in, else the age band (velocity #4)."""
    if pd.notna(kb_low) and pd.notna(kb_high):
        return P.P(kb_low, (kb_low + kb_high) / 2, kb_high, "kb override")
    if pd.isna(age):
        return P.FAILURE_RATE_AGE_UNKNOWN
    return next(p for (lo, hi), p in P.FAILURE_RATE_BY_AGE if lo <= age < hi)


def hours_down(comp, rec: dict, lead_days: pd.Series, op_hours: float, kb_row: dict) -> tuple[float, float, str]:
    """(low, high, how) hours the line is down after a failure, given what sourcing says is available."""
    if rec.get("action") == "use_shelf_spare":
        if rec.get("spare_plant_id") in ("", comp.plant_id):
            return P.SWAP_HOURS.low, P.SWAP_HOURS.high, f"swap in shelf spare {rec['spare_id']}"
        return (P.SWAP_HOURS.low + P.TRANSFER_DAYS.low * op_hours, P.SWAP_HOURS.high + P.TRANSFER_DAYS.high * op_hours,
                f"ship spare {rec['spare_id']} from {rec['spare_plant_id']} and swap")
    if len(lead_days):   # buy on failure from the market (broker / refurbisher)
        d = lead_days.fillna(P.TRANSFER_DAYS.base)
        return ((d.min() + P.EMERGENCY_OVERHEAD_DAYS.low) * op_hours, (d.max() + P.EMERGENCY_OVERHEAD_DAYS.high) * op_hours,
                "no spare: emergency buy from a listing")
    if comp.lifecycle_status in AT_RISK_STATUS:   # nothing to buy: wait for the successor and migrate
        mig = num(pd.Series([kb_row.get("migration_downtime_hours")])).iloc[0]
        mig_lo, mig_hi = (mig, mig) if pd.notna(mig) else (P.MIGRATION_DOWNTIME_HOURS.low, P.MIGRATION_DOWNTIME_HOURS.high)
        w = P.LEAD_TIME_WKS_SUCCESSOR
        return w.low * 7 * op_hours + mig_lo, w.high * 7 * op_hours + mig_hi, "no spare, no listings: successor lead time + migration"
    wk = num(pd.Series([kb_row.get("lead_time_wks_new")])).iloc[0]
    lo, hi = (wk, wk) if pd.notna(wk) else (P.LEAD_TIME_WKS_NEW.low, P.LEAD_TIME_WKS_NEW.high)
    return lo * 7 * op_hours, hi * 7 * op_hours, "no spare: new-unit lead time"


def spof(reg: dict, sourcing_recommendation: pd.DataFrame, as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """Line-stopping components and their yearly downtime exposure = P(fail by age) x hours down x $/h.
    Hours down follow the sourcing recommendation; components on redundant machines score 0."""
    cv = component_view(reg, as_of_year)
    cv = cv[cv.criticality == "line_stop"].merge(downtime_cost_per_hour(reg).drop(columns="plant_id"), on="line_id", how="left")
    recs = sourcing_recommendation.set_index("component_id").to_dict("index")
    kb = reg["kb_entry"].set_index("kb_id").to_dict("index")
    ls = scored_listings(reg)
    ls = ls[ls.condition.isin(P.USABLE_CONDITIONS) & (ls.trust_score >= P.MIN_TRUST)]
    rows = []
    for c in cv.itertuples():
        k = kb.get(c.kb_id, {})
        fr = failure_rate(c.age, num(pd.Series([k.get("annual_failure_rate_low")])).iloc[0],
                          num(pd.Series([k.get("annual_failure_rate_high")])).iloc[0])
        rec = recs.get(c.component_id, {})
        h_lo, h_hi, how = hours_down(c, rec, ls[ls.kb_id == c.kb_id].lead_days, c.op_hours, k)
        on = 0.0 if c.redundant else 1.0
        why = (f"{c.line_id} stops if it fails; {c.lifecycle_status}, age "
               + (f"{c.age:.0f}y" if pd.notna(c.age) else "unknown") + f"; {how}"
               + (f"; backed up by {c.redundant_with}, scores 0" if c.redundant else ""))
        rows.append({"component_id": c.component_id, "line_id": c.line_id, "criticality": c.criticality,
                     "annual_failure_rate": fr.base, "hours_down_low": h_lo, "hours_down_high": h_hi,
                     "downtime_exposure_per_year_low": round(on * fr.low * h_lo * c.dph_low, 2),
                     "downtime_exposure_per_year_high": round(on * fr.high * h_hi * c.dph_high, 2),
                     "why": why, "plant_id": c.plant_id, "kb_id": c.kb_id, "action": rec.get("action", ""),
                     "annual_failure_rate_low": fr.low, "annual_failure_rate_high": fr.high,
                     "downtime_cost_per_hour_low": round(c.dph_low, 2), "downtime_cost_per_hour_high": round(c.dph_high, 2)})
    return pd.DataFrame(rows).sort_values("downtime_exposure_per_year_high", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------- CapEx
def replacement_cost(comp, reg: dict, part_valuation: pd.DataFrame) -> tuple[float, float]:
    """Cost to replace one component. Active: like-for-like unit price (listings, else type fallback).
    Discontinued / end-of-life: successor hardware + migration engineering (KB override, else hours x rate)."""
    kb = reg["kb_entry"]

    def hardware(kb_id: str, ctype: str):
        v = unit_cost(part_valuation, kb_id) if kb_id else None
        f = P.UNIT_COST_BY_TYPE.get(ctype, P.UNIT_COST_DEFAULT)
        return v if v else (f.low, f.high)

    if comp.lifecycle_status not in AT_RISK_STATUS:
        return hardware(comp.kb_id, comp.component_type)
    succ = kb[(kb.part_no == comp.successor_part_no) & (kb.part_no.fillna("") != "")].kb_id
    hw = hardware(succ.iloc[0] if len(succ) else "", comp.component_type)
    row = kb[kb.kb_id == comp.kb_id].iloc[0]
    mlo, mhi = num(pd.Series([row.get("migration_cost_low")])).iloc[0], num(pd.Series([row.get("migration_cost_high")])).iloc[0]
    if pd.isna(mlo) or pd.isna(mhi):
        h = P.MIGRATION_HOURS.get(comp.component_type, P.MIGRATION_HOURS_DEFAULT)
        mlo, mhi = h.low * P.ENGINEERING_RATE.low, h.high * P.ENGINEERING_RATE.high
    return hw[0] + mlo, hw[1] + mhi


def capex_by_year(reg: dict, part_valuation: pd.DataFrame, start_year: int = 2027, years: int = 5,
                  sourcing_recommendation: pd.DataFrame | None = None, growth: pd.DataFrame | None = None,
                  as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """CapEx low/high per plant, year and capex_type.
    deferred    = already past typical life, or discontinued / end-of-life with no shelf spare: spread over years 0-2.
    maintenance = replacement falls due (date code + mid typical life) inside the window.
    growth      = only rows the user typed in (`growth`: plant_id, year, capex_low, capex_high)."""
    sr = sourcing_recommendation if sourcing_recommendation is not None else recommend_sourcing(reg, part_valuation, as_of_year)
    on_shelf = set(sr.loc[sr.action == "use_shelf_spare", "component_id"])
    cv = component_view(reg, as_of_year)
    cv = cv[cv.kb_id != ""]
    window = range(start_year, start_year + years)
    rows = []
    for c in cv.itertuples():
        lo, hi = replacement_cost(c, reg, part_valuation)
        past_life = pd.notna(c.age) and pd.notna(c.life_low) and c.age >= c.life_low
        if past_life or (c.lifecycle_status in AT_RISK_STATUS and c.component_id not in on_shelf):
            for y in window[:3]:
                rows.append((c.plant_id, y, "deferred", lo / 3, hi / 3, c.component_id))
        elif pd.notna(c.age) and pd.notna(c.life_low):
            due = int(round(as_of_year - c.age + (c.life_low + c.life_high) / 2))
            if due in window:
                rows.append((c.plant_id, due, "maintenance", lo, hi, c.component_id))
    out = pd.DataFrame(rows, columns=["plant_id", "year", "capex_type", "capex_low", "capex_high", "driver_component_ids"])
    out = (out.groupby(["plant_id", "year", "capex_type"])
           .agg(capex_low=("capex_low", "sum"), capex_high=("capex_high", "sum"),
                driver_component_ids=("driver_component_ids", lambda s: ";".join(sorted(s)))).reset_index())
    if growth is not None and len(growth):
        g = growth.assign(capex_type="growth", driver_component_ids="user input")
        out = pd.concat([out, g[out.columns]], ignore_index=True)
    out = out.merge(reg["plant"][["plant_id", "company_id"]], on="plant_id", how="left")
    out[["capex_low", "capex_high"]] = out[["capex_low", "capex_high"]].round(2)
    cols = ["company_id", "plant_id", "year", "capex_type", "capex_low", "capex_high", "driver_component_ids"]
    return out[cols].sort_values(["plant_id", "year", "capex_type"]).reset_index(drop=True)


# ---------------------------------------------------------------- deal lens
def pv(cash: pd.Series, year: pd.Series, rate: float, as_of_year: int) -> float:
    return float((cash / (1 + rate) ** (year - as_of_year)).sum())


def deal_adjustment(reg: dict, capex_by_year: pd.DataFrame, company_id: str | None = None,
                    discount_rate: float | None = None, as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """Deal lens, target companies only (a plant with status `target`). Deferred CapEx is a debt-like item:
    price cut = deferred low at face value; holdback = PV(deferred high - low), so nothing is counted twice.
    No discount_rate -> the holdback uses the base deal rate."""
    targets = set(reg["plant"].loc[reg["plant"].status == "target", "company_id"])
    if company_id is not None:
        targets &= {company_id}
    r_base = discount_rate if discount_rate is not None else P.DEAL_DISCOUNT_RATE.base
    rows = []
    for co in sorted(targets):
        d = capex_by_year[(capex_by_year.company_id == co) & (capex_by_year.capex_type == "deferred")]
        # Deferred CapEx is overdue catch-up spend, so the price cut takes the low case at face value
        # (velocity #15/#17: debt-like items aren't discounted); only the uncertain gap is discounted.
        cut_lo = cut_hi = float(d.capex_low.sum())
        hold = pv(d.capex_high - d.capex_low, d.year, r_base, as_of_year)
        rows.append({"company_id": co, "deferred_capex_low": round(d.capex_low.sum(), 2),
                     "deferred_capex_high": round(d.capex_high.sum(), 2),
                     "suggested_price_reduction_low": round(cut_lo, 2), "suggested_price_reduction_high": round(cut_hi, 2),
                     "suggested_holdback": round(hold, 2),
                     "rationale": (f"deferred CapEx {d.year.min() if len(d) else '-'}-{d.year.max() if len(d) else '-'} "
                                   f"from {len(set(';'.join(d.driver_component_ids).split(';')) - {''})} component(s); "
                                   f"price cut = low case at face value, holdback = PV of the "
                                   f"high-low gap at {r_base:.1%} ({P.DEAL_DISCOUNT_RATE.source})")})
    cols = ["company_id", "deferred_capex_low", "deferred_capex_high", "suggested_price_reduction_low",
            "suggested_price_reduction_high", "suggested_holdback", "rationale"]
    return pd.DataFrame(rows, columns=cols)
