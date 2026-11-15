"""Health score: combine every piece of evidence a part has into a 0-100 score + a remaining-life range.

Evidence, best first (a part uses whatever it has; more evidence = tighter range, higher confidence):
  1. Self-reported diagnostics (newer networked drives/PLCs): capacitor + fan life used, heatsink temp, faults.
  2. Plant records (CMMS work orders / purchase orders): the real install year. Part-level records count fully;
     machine-level records (machine install year, assuming the part is original) count half.
  3. Label date code (from the photo): manufacture year, a FLOOR on age when there are no records.
  4. Cabinet thermal camera: component temperature -> heat aging (Arrhenius 10-degree rule); continuous monitoring
     counts more than a one-time walk snapshot.
  5. Motor current (clamp-on current sensor on the drive output).
Anomalies (xray/anomaly.py): EWMA shift, CUSUM drift and trend test on expected-temperature residuals, robust z vs
identical parts, Mahalanobis distance on current features. Their max severity (0-1) x ANOMALY_PENALTY comes off health.
Rated life comes from the part's datasheet/manual (kb.typical_life_years) at a reference temperature.

Engineering assumptions are named constants with their basis; every output lists the sources and drivers used.
"""
import math

import pandas as pd

AS_OF_YEAR = 2026

# reference component temperature (degC) at which the datasheet/typical life applies, by component type
# (typical design points for industrial electronics; verify per manual)
T_REF = {"drive": 55.0, "servo_drive": 55.0, "power_supply": 50.0, "plc": 45.0, "plc_io": 45.0, "hmi": 45.0}
T_REF_DEFAULT = 45.0
ARRHENIUS_STEP_C = 10.0       # life roughly halves per +10 degC (electrolytic capacitor / fan rule of thumb, datasheets)
FAULT_PENALTY = 6.0           # health points per fault in the last 12 months (cap 30)
ANOMALY_PENALTY = 45.0        # (legacy, unused by the survival model)
WEIBULL_BETA = 3.0            # wear-out shape (>1: failure risk rises with age; typical for capacitors/fans) - assumption
WEIBULL_ETA_SHARE = 1.1       # scale = 1.1 x rated life, so ~1/3 of parts have failed by rated life - assumption
ANOMALY_HAZARD = 20.0         # hazard multiplier at anomaly severity 1.0 - assumption, calibrate in the pilot
FAULT_HAZARD = 0.3            # +30% hazard per logged fault (12 months, cap 5) - assumption
EVIDENCE_WEIGHT = {"diagnostics": 0.5, "records": 0.2, "machine_records": 0.1, "thermal_continuous": 0.2, "thermal_snapshot": 0.1,
                   "current_signature": 0.1, "thermal_trend": 0.1, "label_date_code": 0.05}
RANGE_BY_CONFIDENCE = {"high": 0.15, "medium": 0.30, "low": 0.50}   # +/- share of the remaining-life estimate


def _num(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def compute(reg: dict[str, pd.DataFrame], as_of_year: int = AS_OF_YEAR) -> pd.DataFrame:
    comp = reg["component"]
    kb = reg["kb_entry"].set_index("kb_id")
    cond = reg.get("condition", pd.DataFrame())
    cond = cond.set_index("component_id") if "component_id" in cond else pd.DataFrame()
    from xray import anomaly
    an = anomaly.compute(reg).set_index("component_id")

    rows = []
    for c in comp.to_dict("records"):
        cid, kb_id, ctype = c["component_id"], c.get("kb_id") or "", c.get("component_type") or ""
        e = cond.loc[cid].to_dict() if cid in cond.index else {}
        sources, drivers = [], []
        k = kb.loc[kb_id] if kb_id in kb.index else None
        rated = ((_num(k.typical_life_years_low) or 10) + (_num(k.typical_life_years_high) or 15)) / 2 if k is not None else 12.0
        t_ref = T_REF.get(ctype, T_REF_DEFAULT)

        # --- age: records beat the label date code (which is only a floor)
        rec_year, label_year = _num(e.get("install_year_record")), _num(c.get("date_code"))
        if rec_year and "machine" in str(e.get("install_year_basis", "")):
            install, age_basis = int(rec_year), "machine install record (assumes the original part)"
            sources.append("machine_records")
        elif rec_year:
            install, age_basis = int(rec_year), "plant records (part level)"
            sources.append("records")
        elif label_year:
            install, age_basis = int(label_year), "label date code (manufacture year, a floor)"
            sources.append("label_date_code")
        else:
            install, age_basis = None, "unknown"
        age = max(0.0, as_of_year - install) if install else None

        # --- temperature -> heat aging factor
        temp, amb = _num(e.get("temp_c")), _num(e.get("ambient_c"))
        af = 1.0
        if temp is not None:
            sources.append("thermal_continuous" if e.get("thermal_mode") == "continuous" else "thermal_snapshot")
            af = 2 ** ((temp - t_ref) / ARRHENIUS_STEP_C)
            if af > 1.3:
                drivers.append(f"runs at {temp:.0f}°C, {temp - t_ref:+.0f}°C vs. its {t_ref:.0f}°C design point: ages {af:.1f}× faster")

        # --- life used: the part's own estimate wins; else age x heat aging / rated life
        cap, fan = _num(e.get("diag_cap_life_used")), _num(e.get("diag_fan_life_used"))
        if cap is not None or fan is not None:
            sources.append("diagnostics")
            life_used = max(x for x in (cap, fan) if x is not None)
            drivers.append(f"self-reported: capacitor life used {cap:.0%}" if cap is not None else "")
            if fan is not None and fan >= 0.7:
                drivers.append(f"self-reported: fan life used {fan:.0%}")
        elif age is not None:
            # we only know TODAY's temperature, not the part's whole history: count half of the extra heat aging
            # for the past (af_hist), the full factor for the remaining life below
            af_hist = 1.0 + (af - 1.0) * 0.5 if af > 1 else af
            life_used = age * af_hist / rated
        else:
            life_used = None

        # --- anomalies on top of wear (statistical detectors, xray/anomaly.py)
        penalty = 0.0
        a = an.loc[cid].to_dict() if cid in an.index else {}
        if _num(a.get("sigma_c")) is not None:
            sources.append("thermal_trend")
        if _num(a.get("mahalanobis")) is not None:
            sources.append("current_signature")
        if (_num(a.get("sev_shift")) or 0) > 0:
            drivers.append(f"temperature shift: {int(a['ewma_out_days'])} day(s) above the EWMA control limit, now {a['resid_mean_c']:+.0f}°C vs. expected for its load and ambient")
        if (_num(a.get("sev_drift")) or 0) > 0:
            drivers.append(f"slow warming: CUSUM {a['cusum_max']:.0f} (alarm at {anomaly.CUSUM_H:.0f})")
        if (_num(a.get("sev_trend")) or 0) > 0:
            drivers.append(f"warming {a['trend_c_per_month']:+.1f}°C/month beyond expected (t = {a['trend_t']:.1f})")
        if (_num(a.get("sev_peer")) or 0) > 0:
            drivers.append(f"runs hot vs. {int(a['peer_n'])} identical parts in the portfolio (robust z = {a['peer_z']:.1f}): fan or connection?")
        if (_num(a.get("sev_current")) or 0) > 0:
            drivers.append(f"motor current pattern off its baseline (Mahalanobis {a['mahalanobis']:.1f}, alarm at {anomaly.MAHAL_ALERT:.0f}): bearing / alignment / load on the driven motor")
        sev = _num(a.get("anomaly_severity")) or 0.0
        penalty += ANOMALY_PENALTY * sev
        faults = _num(e.get("diag_faults_12m"))
        if faults:
            penalty += min(30.0, FAULT_PENALTY * faults)
            drivers.append(f"{int(faults)} fault(s) logged in the last 12 months")
        stats = {k: (None if pd.isna(a.get(k)) else a.get(k)) for k in
                 ("anomaly_severity", "resid_mean_c", "ewma_out_days", "cusum_max", "trend_c_per_month", "trend_t", "peer_z", "peer_n", "mahalanobis")}

        conf_score = sum(EVIDENCE_WEIGHT.get(s, 0) for s in set(sources))
        conf = "high" if conf_score >= 0.6 else "medium" if conf_score >= 0.3 else "low"
        if life_used is None:
            rows.append({"component_id": cid, "health_score": None, "life_used": None, "remaining_years_low": None,
                         "remaining_years_high": None, "confidence": "none", "confidence_score": round(conf_score, 2),
                         "sources": ";".join(sorted(set(sources))), "age_basis": age_basis, "drivers": ";".join(d for d in drivers if d),
                         "simulated": e.get("simulated", ""), **stats})
            continue
        # --- survival model (Weibull + proportional hazards): health = 100 x P(survives the next 12 months)
        # effective age = life used x rated life (heat aging and self-reported wear are already in life_used);
        # evidence multiplies the hazard: anomaly severity (up to x ANOMALY_HAZARD) and logged faults.
        a = life_used * rated
        eta = rated * WEIBULL_ETA_SHARE
        m = math.exp(math.log(ANOMALY_HAZARD) * sev) * (1 + FAULT_HAZARD * min(faults or 0, 5))
        surv = math.exp(-m * ((a + 1) ** WEIBULL_BETA - a ** WEIBULL_BETA) / eta ** WEIBULL_BETA)
        health = 100.0 * surv
        # remaining life = conditional median: S(t | survived to a) = 0.5
        remaining = (a ** WEIBULL_BETA + eta ** WEIBULL_BETA * math.log(2) / m) ** (1 / WEIBULL_BETA) - a
        spread = RANGE_BY_CONFIDENCE[conf]
        rows.append({"component_id": cid, "health_score": round(health), "life_used": round(life_used, 2),
                     "remaining_years_low": round(remaining * (1 - spread), 1), "remaining_years_high": round(remaining * (1 + spread), 1),
                     "confidence": conf, "confidence_score": round(conf_score, 2), "sources": ";".join(sorted(set(sources))),
                     "age_basis": age_basis, "drivers": ";".join(d for d in drivers if d), "simulated": e.get("simulated", ""), **stats})
    return pd.DataFrame(rows)
