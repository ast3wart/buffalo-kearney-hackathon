"""Part value from market listings, and what to do about each at-risk component (registry-format §7).

Pure functions: `reg` (dict of registry DataFrames) in, DataFrames out. Parameters live in xray/params.py.
No manufacturer, part or plant names here.
"""
import re

import numpy as np
import pandas as pd

from xray import params as P

AT_RISK_STATUS = {"end_of_life", "discontinued"}
ALT_ORDER = {"successor": 0, "compatible": 1, "similar": 2}


def num(s: pd.Series) -> pd.Series:
    """Registry columns may arrive as text from SQLite ('' = unknown): coerce to float, unknown -> NaN."""
    return pd.to_numeric(s, errors="coerce")


def year_of(date_code) -> float:
    m = re.search(r"(19|20)\d\d", str(date_code))
    return float(m.group(0)) if m else np.nan


def component_view(reg: dict, as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """component + machine + line + plant + KB in one frame: where it sits, how critical, how old, what status."""
    c = reg["component"].drop(columns=["lifecycle_status", "component_type"], errors="ignore")
    m = reg["machine"][["machine_id", "line_id", "criticality", "redundant_with"]]
    ln = reg["line"][["line_id", "plant_id"]]
    pl = reg["plant"][["plant_id", "company_id", "status"]].rename(columns={"status": "plant_status"})
    kb = reg["kb_entry"][["kb_id", "component_type", "lifecycle_status", "typical_life_years_low",
                          "typical_life_years_high", "successor_part_no"]]
    v = c.merge(m, on="machine_id", how="left").merge(ln, on="line_id", how="left").merge(pl, on="plant_id", how="left")
    v = v.merge(kb, on="kb_id", how="left")
    v["kb_id"] = v.kb_id.fillna("")
    v["lifecycle_status"] = v.lifecycle_status.fillna("unknown")
    v["redundant"] = v.redundant_with.fillna("").astype(str).str.strip() != ""
    v["age"] = as_of_year - v.date_code.map(year_of)
    v["life_low"], v["life_high"] = num(v.typical_life_years_low), num(v.typical_life_years_high)
    v["spof"] = (v.criticality == "line_stop") & ~v.redundant
    return v


def at_risk(cv: pd.DataFrame) -> pd.Series:
    """Matched to the KB and either discontinued / end-of-life or already past its typical life."""
    return (cv.kb_id != "") & (cv.lifecycle_status.isin(AT_RISK_STATUS) | (cv.age >= cv.life_low))


# ---------------------------------------------------------------- listings -> part value
def trust_scores(listing: pd.DataFrame) -> pd.Series:
    """0-1 trust per listing. Simple additive rule (registry-format: 'a simple score'):
    0.4 base; +0.4 authorized; +0.2 warranty >= 12 months; +0.1 returns accepted;
    +0.1 seller rating >= 98% with >= 100 sales; -0.3 rating < 90%; -0.2 seller outside DOMESTIC. Clipped to 0-1.
    Unknown inputs add nothing. Unauthorized sellers always carry counterfeit risk, whatever the score."""
    yes = lambda col: listing.get(col, pd.Series("", index=listing.index)).astype(str).str.lower().eq("yes")
    rating, sales = num(listing.get("seller_rating")), num(listing.get("seller_sales_count"))
    warranty = num(listing.get("warranty_months"))
    loc = listing.get("seller_location", pd.Series("", index=listing.index)).fillna("").astype(str).str.upper()
    t = (0.4 + 0.4 * yes("authorized") + 0.2 * (warranty >= 12) + 0.1 * yes("returns_accepted")
         + 0.1 * ((rating >= 98) & (sales >= 100)) - 0.3 * (rating < 90) - 0.2 * (loc.ne("") & ~loc.isin(P.DOMESTIC)))
    return t.clip(0, 1).round(2)


def scored_listings(reg: dict) -> pd.DataFrame:
    """listings with trust_score filled in and a usable all-in price (sold price beats an ask)."""
    ls = reg.get("listing", pd.DataFrame()).copy()
    if ls.empty:
        return pd.DataFrame(columns=["listing_id", "kb_id", "condition", "trust_score", "unit_price", "all_in", "lead_days"])
    ls["trust_score"] = trust_scores(ls)
    ls["unit_price"] = num(ls.sold_price).fillna(num(ls.price))
    ls["all_in"] = ls.unit_price + num(ls.shipping).fillna(0)
    ls["lead_days"] = num(ls.lead_time_days)
    return ls[ls.unit_price.notna() & (ls.get("currency", "USD").fillna("USD").replace("", "USD") == "USD")]


def value_parts(reg: dict) -> pd.DataFrame:
    """part_valuation: per kb_id x condition, 25th / 50th / 75th percentile of trusted listing prices.
    Low-trust listings stay visible as n_low_trust instead of moving the range. KB parts with no listings get
    one row with confidence `none` (-> alternatives)."""
    ls = scored_listings(reg)
    as_of = str(ls.seen_on.max()) if "seen_on" in ls and len(ls) else ""
    rows = []
    for (kb_id, cond), g in ls.groupby(["kb_id", "condition"]):
        ok = g[g.trust_score >= P.MIN_TRUST]
        q = ok.unit_price.quantile([0.25, 0.5, 0.75]) if len(ok) else pd.Series([np.nan] * 3, index=[0.25, 0.5, 0.75])
        n = len(ok)
        rows.append({"kb_id": kb_id, "condition": cond, "n_listings": n, "price_low": q[0.25], "price_mid": q[0.5],
                     "price_high": q[0.75], "sold_n": int(num(ok.sold_price).notna().sum()),
                     "confidence": "high" if n >= P.HIGH_CONFIDENCE_LISTINGS else ("low" if n else "none"),
                     "n_low_trust": len(g) - n, "as_of": as_of})
    listed = {r["kb_id"] for r in rows}
    for kb_id in reg["kb_entry"].kb_id:
        if kb_id not in listed:
            rows.append({"kb_id": kb_id, "condition": "", "n_listings": 0, "price_low": np.nan, "price_mid": np.nan,
                         "price_high": np.nan, "sold_n": 0, "confidence": "none", "n_low_trust": 0, "as_of": as_of})
    out = pd.DataFrame(rows)
    out[["price_low", "price_mid", "price_high"]] = out[["price_low", "price_mid", "price_high"]].round(2)
    return out.sort_values(["kb_id", "condition"]).reset_index(drop=True)


def unit_cost(part_valuation: pd.DataFrame, kb_id: str) -> tuple[float, float] | None:
    """Installable unit price range for a part: lowest 25th pct to highest 75th pct across usable conditions."""
    pv = part_valuation[(part_valuation.kb_id == kb_id) & part_valuation.condition.isin(P.USABLE_CONDITIONS)
                        & (part_valuation.n_listings > 0)]
    return (float(pv.price_low.min()), float(pv.price_high.max())) if len(pv) else None


def listing_confidence(part_valuation: pd.DataFrame, kb_id: str) -> str:
    """Best confidence over usable conditions: high / low / none."""
    c = set(part_valuation[(part_valuation.kb_id == kb_id) & part_valuation.condition.isin(P.USABLE_CONDITIONS)].confidence)
    return "high" if "high" in c else ("low" if "low" in c else "none")


# ---------------------------------------------------------------- shelf + sourcing
def shelf(reg: dict) -> pd.DataFrame:
    """Storeroom rows with their matched kb_id and the plant's status / company."""
    sm = reg["spare_match"][["spare_id", "kb_id"] + (["confidence"] if "confidence" in reg["spare_match"] else [])]
    s = reg["spare_stock"][["spare_id", "plant_id", "qty"]].merge(sm, on="spare_id")
    s = s.merge(reg["plant"][["plant_id", "company_id", "status"]], on="plant_id", how="left")
    s["qty"] = num(s.qty).fillna(1)
    return s[(s.kb_id.fillna("") != "") & (s.qty > 0)]


def shelf_candidates(sh: pd.DataFrame, comp) -> pd.DataFrame:
    """Shelf rows that can cover `comp`: its own plant always; other plants only if both are owned (never a target's).
    Ranked: same plant, same company, rest of the portfolio."""
    c = sh[(sh.kb_id == comp.kb_id) & (sh.remaining > 0)]
    c = c[(c.plant_id == comp.plant_id) | ((c.status == "owned") & (comp.plant_status == "owned"))]
    rank = np.where(c.plant_id == comp.plant_id, 0, np.where(c.company_id == comp.company_id, 1, 2))
    return c.assign(_rank=rank).sort_values(["_rank", "remaining"], ascending=[True, False])


def recommend_sourcing(reg: dict, part_valuation: pd.DataFrame, as_of_year: int = P.AS_OF_YEAR) -> pd.DataFrame:
    """sourcing_recommendation, one row per at-risk component. Shelf first at any owned plant (use_shelf_spare,
    net of transfer cost) -> buy_spare if a line-stopping single point of failure that is scarce and buyable ->
    migrate if discontinued / end-of-life with few or no listings -> monitor."""
    cv = component_view(reg, as_of_year)
    cv = cv[at_risk(cv)].sort_values(["spof", "component_id"], ascending=[False, True])
    sh = shelf(reg).assign(remaining=lambda d: d.qty)
    ls = scored_listings(reg)
    ls = ls[ls.condition.isin(P.USABLE_CONDITIONS) & (ls.trust_score >= P.MIN_TRUST)]
    alts = reg.get("alternative", pd.DataFrame(columns=["alt_id", "kb_id", "alternative_kind"]))
    rows = []
    for comp in cv.itertuples():
        best = ls[ls.kb_id == comp.kb_id].sort_values(["trust_score", "all_in"], ascending=[False, True])
        best_id = best.listing_id.iloc[0] if len(best) else ""
        conf = listing_confidence(part_valuation, comp.kb_id)
        value = unit_cost(part_valuation, comp.kb_id)
        scarce = comp.lifecycle_status in AT_RISK_STATUS
        r = {"component_id": comp.component_id, "plant_id": comp.plant_id, "kb_id": comp.kb_id, "action": "monitor",
             "spare_id": "", "spare_plant_id": "", "best_listing_id": best_id, "alt_id": "",
             "transfer_cost_low": 0.0, "transfer_cost_high": 0.0,
             "part_value_low": value[0] if value else np.nan, "part_value_high": value[1] if value else np.nan}
        cand = shelf_candidates(sh, comp)
        if len(cand):
            s = cand.iloc[0]
            sh.loc[sh.spare_id == s.spare_id, "remaining"] -= 1
            here = s.plant_id == comp.plant_id
            if not here:
                r["transfer_cost_low"] = P.TRANSFER_FREIGHT.low + P.TRANSFER_ADMIN.low
                r["transfer_cost_high"] = P.TRANSFER_FREIGHT.high + P.TRANSFER_ADMIN.high
            r.update(action="use_shelf_spare", spare_id=s.spare_id, spare_plant_id=s.plant_id,
                     reason=f"spare {s.spare_id} on the shelf at {'this plant' if here else 'sister plant ' + s.plant_id}"
                            + ("" if here else f" (transfer ${r['transfer_cost_low']:,.0f}-{r['transfer_cost_high']:,.0f})"))
        elif comp.spof and scarce and len(best):
            r.update(action="buy_spare", reason=f"line-stopping, {comp.lifecycle_status}, no shelf spare it can use; "
                                                f"{len(best)} trusted listing(s), buy one before it fails")
        elif scarce and conf != "high":
            r.update(action="migrate", reason=f"{comp.lifecycle_status} with {'few' if conf == 'low' else 'no'} "
                                              f"trusted listings: plan the move to an alternative")
        else:
            r.update(reason=f"{comp.lifecycle_status}, age {comp.age:.0f}y; listings confidence {conf}: watch it")
        if r["action"] == "migrate" or conf != "high":
            a = alts[alts.kb_id == comp.kb_id].assign(_o=lambda d: d.alternative_kind.map(ALT_ORDER).fillna(9)).sort_values("_o")
            r["alt_id"] = a.alt_id.iloc[0] if len(a) else ""
        rows.append(r)
    cols = ["component_id", "action", "spare_id", "best_listing_id", "alt_id", "reason", "plant_id", "kb_id",
            "spare_plant_id", "transfer_cost_low", "transfer_cost_high", "part_value_low", "part_value_high"]
    return pd.DataFrame(rows, columns=cols)
