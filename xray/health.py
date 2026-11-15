"""Part health: Working / Replace soon / Replace ASAP, plus life used, order-by date and the best ways to get one.

Engineering rules (Asher's thread). Brandon's financial model (xray/pricing.py, valuation.py) refines the
*recommended action* with money once it lands; these rules are the identity/timing layer underneath.
No manufacturer or part names here: everything comes from the registry tables.
"""
from datetime import date, timedelta

import pandas as pd

AT_RISK = ("discontinued", "end_of_life")
BUFFER_DAYS = 14          # order this much earlier than strictly needed
TRANSFER_DAYS = 7         # move a spare between plants
MIGRATION_EXTRA_DAYS = 28  # engineering + programming when only the successor is available
TODAY = date.today()


def _lead_options(kb_id, listings, shelf):
    """Every way to get this part, fastest/most trusted first: shelf at another plant, then listings."""
    opts = []
    by_plant = {}
    for s in shelf.get(kb_id, []):  # one option per plant, quantities summed
        o = by_plant.setdefault(s["plant_id"], {"kind": "shelf", "where": s["plant_name"], "plant_id": s["plant_id"], "qty": 0,
                                                "price": 0.0, "lead_time_days": TRANSFER_DAYS, "condition": "on the shelf",
                                                "trust_score": 1.0, "detail": s["description"]})
        o["qty"] += int(float(s["qty"] or 0))
    opts.extend(by_plant.values())
    for l in listings.get(kb_id, []):
        opts.append({"kind": "listing", **l})
    return opts


def compute(reg: dict[str, pd.DataFrame], year: int | None = None) -> pd.DataFrame:
    year = year or TODAY.year
    comp = reg["component"].merge(reg["machine"][["machine_id", "line_id", "criticality"]], on="machine_id", how="left")
    comp = comp.merge(reg["line"][["line_id", "plant_id"]], on="line_id", how="left")
    kb = reg["kb_entry"].set_index("kb_id")
    plants = reg["plant"].set_index("plant_id")
    owned = set(plants[plants.status == "owned"].index)

    lst = reg.get("listing", pd.DataFrame())
    listings = {}
    if "kb_id" in lst:
        for r in lst.to_dict("records"):
            for k in ("price", "lead_time_days", "trust_score", "shipping"):
                r[k] = float(r[k]) if str(r.get(k, "")) not in ("", "nan") else None
            listings.setdefault(r["kb_id"], []).append(r)
    sm = reg["spare_match"][reg["spare_match"].kb_id != ""].merge(reg["spare_stock"], on="spare_id")
    shelf_all = {}
    for r in sm.to_dict("records"):
        if r["plant_id"] in owned:
            shelf_all.setdefault(r["kb_id"], []).append({**r, "plant_name": plants.loc[r["plant_id"], "plant_name"]})

    out = []
    for c in comp.to_dict("records"):
        kb_id = c.get("kb_id") or ""
        base = {"component_id": c["component_id"]}
        if not kb_id or kb_id not in kb.index:
            out.append({**base, "health": "unidentified", "life_used_pct": None, "action": "Re-photograph the label or confirm by hand"})
            continue
        k = kb.loc[kb_id]
        lo, hi = float(k.typical_life_years_low or 10), float(k.typical_life_years_high or 15)
        installed = int(float(c["date_code"])) if str(c.get("date_code", "")) not in ("", "nan") else year - int(lo)
        age = max(0, year - installed)
        life_pct = age / ((lo + hi) / 2)
        end_year = installed + int(lo)  # conservative: plan for the short end of the life range
        # shelf spares elsewhere in the portfolio (not this plant's own)
        shelf = {kb_id: [s for s in shelf_all.get(kb_id, []) if s["plant_id"] != c["plant_id"]]}
        own_spare = any(s["plant_id"] == c["plant_id"] for s in shelf_all.get(kb_id, []))
        options = _lead_options(kb_id, listings, shelf)
        buyable = [o for o in options if o["kind"] == "listing" and (o.get("trust_score") or 0) >= 0.6 and o.get("condition") != "for_repair"]
        best = min(buyable, key=lambda o: (o.get("price") or 1e12)) if buyable else None
        fastest = min(options, key=lambda o: o.get("lead_time_days") or 1e9) if options else None
        if fastest:
            lead = int(fastest["lead_time_days"])
        elif k.successor_part_no:
            lead = int(float(k.lead_time_wks_new or 16) * 7) + MIGRATION_EXTRA_DAYS
        else:
            lead = 120
        failure_date = date(end_year, 6, 30)
        order_by = failure_date - timedelta(days=lead + BUFFER_DAYS)
        status = k.lifecycle_status
        line_stop = c.get("criticality") == "line_stop"
        days_left = (order_by - TODAY).days
        critical = line_stop or status in AT_RISK
        if (life_pct >= 1.0 and critical and not own_spare) or (line_stop and status in AT_RISK and not own_spare and life_pct >= 0.8):
            health = "replace_asap"
        elif life_pct >= 0.85 or (critical and days_left <= 365) or (line_stop and status in AT_RISK and not own_spare):
            health = "replace_soon"
        else:
            health = "working"
        succ = k.successor_part_no
        order_txt = "now" if days_left <= 0 else f"by {order_by:%b %Y}"
        covered = own_spare and health != "working"
        if covered:
            action = (f"Covered: a spare is on this plant's own shelf. Swap it in when needed and restock one {order_txt}."
                      + (f" Plan migration to {succ}." if status in AT_RISK and succ else ""))
        elif health == "working":
            action = "Monitor. No action needed this year."
        elif shelf[kb_id]:
            s = shelf[kb_id][0]
            action = (f"Reserve the spare at {s['plant_name']} now; it can be here in ~{TRANSFER_DAYS} days."
                      + (f" Plan migration to {succ}." if status in AT_RISK and succ else ""))
        elif status in AT_RISK:
            action = ((f"Buy one {best['condition'].replace('_', ' ')} spare now (~${best['price']:,.0f}) and schedule migration to {succ}."
                       if best else f"No reliable spare on the market: start migration to {succ} now." if succ
                       else "No reliable spare and no successor: find an alternative part.")
                      if health == "replace_asap" else
                      f"Buy one spare {order_txt}" + (f" and budget migration to {succ}." if succ else "."))
        else:
            action = ("Order a replacement now." if health == "replace_asap" else f"Order a replacement {order_txt}.")
        out.append({**base, "health": health, "life_used_pct": round(life_pct, 2), "installed": installed,
                    "expected_end_year": end_year, "lead_time_days": lead, "order_by": order_by.isoformat(),
                    "order_now": days_left <= 0 and not covered, "covered_by_own_spare": covered, "action": action, "line_stop": line_stop,
                    "options": sorted(options, key=lambda o: (o["kind"] != "shelf", o.get("price") or 1e12)),
                    "best_price": best["price"] if best else None, "n_listings": len([o for o in options if o["kind"] == "listing"])})
    return pd.DataFrame(out)
