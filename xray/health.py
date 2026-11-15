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
    from xray import condition

    cond = condition.compute(reg).set_index("component_id") if "condition" in reg else pd.DataFrame()
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
        hs = cond.loc[c["component_id"]].to_dict() if c["component_id"] in cond.index else {}
        if hs.get("life_used") is not None and hs.get("life_used") == hs.get("life_used"):
            life_pct = float(hs["life_used"])  # health model (diagnostics / records / thermal / current) beats age alone
        end_year = installed + round((lo + hi) / 2)  # middle of the typical life range
        # shelf spares elsewhere in the portfolio (not this plant's own)
        shelf = {kb_id: [s for s in shelf_all.get(kb_id, []) if s["plant_id"] != c["plant_id"]]}
        own_spare = any(s["plant_id"] == c["plant_id"] for s in shelf_all.get(kb_id, []))
        options = _lead_options(kb_id, listings, shelf)
        succ_kb = kb.index[kb.part_no == k.successor_part_no].tolist() if k.successor_part_no else []
        if k.lifecycle_status == "discontinued" and succ_kb:  # the official successor, bought new from the manufacturer side
            for l in listings.get(succ_kb[0], []):
                if l.get("authorized") == "yes":
                    options.append({"kind": "successor", **l, "part_no": k.successor_part_no})
        buyable = [o for o in options if o["kind"] == "listing" and (o.get("trust_score") or 0) >= 0.6 and o.get("condition") != "for_repair"]
        best = min(buyable, key=lambda o: (o.get("price") or 1e12)) if buyable else None
        fastest = min(options, key=lambda o: o.get("lead_time_days") or 1e9) if options else None
        if own_spare:
            lead = 1  # swap from this plant's own shelf
        elif fastest:
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
        # Asher's rule: ASAP if getting one takes longer than the life left; soon if >= 75% of life is used but
        # there's still time to get one; otherwise no action needed.
        life_mid = (lo + hi) / 2
        days_life_left = (date(installed, 6, 30) + timedelta(days=int(life_mid * 365)) - TODAY).days
        if hs.get("remaining_years_low") is not None and hs.get("remaining_years_low") == hs.get("remaining_years_low"):
            days_life_left = int(float(hs["remaining_years_low"]) * 365)  # conservative end of the health model's range
        if days_life_left < lead:
            health = "replace_asap"
        elif life_pct >= 0.75:
            health = "replace_soon"
        else:
            health = "working"
        succ = k.successor_part_no
        order_txt = "now" if days_left <= 0 else f"by {order_by:%b %Y}"
        mfr_same = sorted([o for o in options if o["kind"] == "listing" and o.get("authorized") == "yes"], key=lambda o: o.get("price") or 1e12)
        mfr_succ = sorted([o for o in options if o["kind"] == "successor"], key=lambda o: o.get("price") or 1e12)
        shelf_opts = [o for o in options if o["kind"] == "shelf"]
        rec = (shelf_opts[0] if shelf_opts else mfr_same[0] if status != "discontinued" and mfr_same
               else mfr_succ[0] if mfr_succ else best)
        for o in options:
            o["recommended"] = o is rec
        def cost(o):
            return f"~${o['price']:,.0f}, ~{int(o['lead_time_days'])} days" if o and o.get("price") else ""
        covered = own_spare and health != "working"
        if covered:
            action = (f"Covered: a spare is on this plant's own shelf. Swap it in when needed and restock one {order_txt}."
                      + (f" Plan migration to {succ}." if status in AT_RISK and succ else ""))
        elif health == "working":
            action = "No action needed."
        elif shelf[kb_id]:
            s = shelf[kb_id][0]
            action = (f"Reserve the spare at {s['plant_name']} now; it can be here in ~{TRANSFER_DAYS} days."
                      + (f" Plan migration to {succ}." if status in AT_RISK and succ else ""))
        elif status != "discontinued":  # still made: buy it the normal way
            action = f"Order from the manufacturer or your usual authorized distributor {order_txt} ({cost(rec)})." if rec else \
                     f"Order from the manufacturer or your usual authorized distributor {order_txt}."
        elif rec is not None and rec["kind"] == "successor":
            action = (f"Discontinued: order the successor {succ} from the manufacturer or your usual distributor {order_txt} "
                      f"({cost(rec)} + migration work). A used or refurbished {k.part_no} is only a stopgap.")
        elif rec is not None:
            action = f"Discontinued, no successor sold new: buy the best trusted spare {order_txt} ({rec.get('condition', '').replace('_', ' ')}, {cost(rec)})."
        else:
            action = "Discontinued, no reliable spare and no successor: find an alternative part."
        extra = {k2: hs.get(k2) for k2 in ("health_score", "remaining_years_low", "remaining_years_high", "confidence",
                                            "sources", "drivers", "age_basis", "simulated", "anomaly_severity", "resid_mean_c",
                                            "ewma_out_days", "cusum_max", "trend_c_per_month", "trend_t", "peer_z", "peer_n",
                                            "mahalanobis")} if hs else {}
        extra = {k2: (None if isinstance(v, float) and v != v else v) for k2, v in extra.items()}
        out.append({**base, **extra, "health": health, "life_used_pct": round(life_pct, 2), "installed": installed,
                    "expected_end_year": end_year, "lead_time_days": lead, "order_by": order_by.isoformat(),
                    "order_now": days_left <= 0 and not covered, "covered_by_own_spare": covered, "action": action, "line_stop": line_stop,
                    "options": sorted(options, key=lambda o: (not o.get("recommended"), o["kind"] != "shelf", o.get("condition") == "for_repair", o.get("price") or 1e12)),
                    "best_price": best["price"] if best else None, "n_listings": len([o for o in options if o["kind"] == "listing"])})
    return pd.DataFrame(out)
