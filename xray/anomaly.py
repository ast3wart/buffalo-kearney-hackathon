"""Statistical anomaly detection on the device's time series (temperature + motor current).

Per part with continuous monitoring:
  1. Expected-temperature model: OLS fit on a baseline window, (temp - ambient) ~ a + c*load (a component's temperature
     tracks ambient one-to-one; its rise above ambient scales with load). Residual = actual - expected, so a hot day or
     a busy shift isn't mistaken for a fault.
  2. EWMA control chart on the residuals (lambda 0.2, 3-sigma limits): catches sudden shifts (e.g. a fan dies).
  3. One-sided CUSUM on the residuals (k = 0.5 sigma, h = 5 sigma): catches slow drift (e.g. capacitors aging).
     Both are judged on the last 7 days (lowest value in the week), so only a sustained signal counts.
  4. Trend test: OLS slope of the post-baseline residuals in degC/month, with its t-statistic.
Cross-sectional, every part with a temperature:
  5. Robust z-score of temperature rise over ambient vs identical parts (same kb_id) across the portfolio (median/MAD).
Motor current (drives / servo drives):
  6. Mahalanobis distance of [load-normalized RMS current, sideband energy] vs the drive's own baseline.
Each detector returns a severity in [0, 1]; the part's anomaly severity is the max, which xray/condition.py turns into
a health penalty. Thresholds are standard SPC defaults; calibrate them in the pilot.
"""
import math

import numpy as np
import pandas as pd

BASELINE_DAYS = 30
RECENT_DAYS = 7         # detectors are judged on the last week (sustained, not a one-day blip)
EWMA_LAMBDA, EWMA_L = 0.2, 3.0
CUSUM_K, CUSUM_H = 0.5, 5.0
Z_ALERT = 3.0                  # robust z at which a detector starts to fire
SLOPE_ALERT_C_PER_MONTH = 1.0  # residual warming per month worth flagging (with |t| > 3)
MAHAL_ALERT = 3.0


def severity(stat: float, alert: float) -> float:
    """0 below the alert level, rising smoothly toward 1 (alert -> 0, 2x alert -> ~0.63, 3x -> ~0.86)."""
    return 0.0 if stat <= alert else 1.0 - math.exp(-(stat - alert) / alert)


def robust_z(x: float, sample: np.ndarray) -> float:
    med = np.median(sample)
    mad = np.median(np.abs(sample - med)) * 1.4826
    return 0.0 if mad < 1e-9 else (x - med) / mad


def temperature_series(g: pd.DataFrame) -> dict:
    g = g.sort_values("day")
    base, post = g[g.day < BASELINE_DAYS], g[g.day >= BASELINE_DAYS]
    if len(base) < 10 or len(post) < 5:
        return {}
    X = np.column_stack([np.ones(len(base)), base.load_pct])
    coef, *_ = np.linalg.lstsq(X, (base.temp_c - base.ambient_c).to_numpy(), rcond=None)
    def expected(df):
        return df.ambient_c.to_numpy() + np.column_stack([np.ones(len(df)), df.load_pct]) @ coef
    r_base = base.temp_c.to_numpy() - expected(base)
    sigma = max(float(np.std(r_base, ddof=2)), 0.3)
    r = post.temp_c.to_numpy() - expected(post)
    # EWMA chart (steady-state limits)
    z, ewma = 0.0, []
    for v in r:
        z = EWMA_LAMBDA * v + (1 - EWMA_LAMBDA) * z
        ewma.append(z)
    limit = EWMA_L * sigma * math.sqrt(EWMA_LAMBDA / (2 - EWMA_LAMBDA))
    out_days = int(np.sum(np.array(ewma) > limit))
    # judge the CURRENT state (last RECENT_DAYS), so a blip that already resolved doesn't lower today's health
    ewma_stat = float(np.min(ewma[-RECENT_DAYS:]) / (limit / EWMA_L))   # in units of the EWMA sigma
    # CUSUM (upper)
    s, cus = 0.0, []
    for v in r / sigma:
        s = max(0.0, s + v - CUSUM_K)
        cus.append(s)
    s_max = float(np.min(cus[-RECENT_DAYS:]))
    # trend on post-baseline residuals
    t_days = post.day.to_numpy(dtype=float)
    A = np.column_stack([np.ones(len(t_days)), t_days])
    b, res, *_ = np.linalg.lstsq(A, r, rcond=None)
    dof = max(len(r) - 2, 1)
    s2 = float(np.sum((r - A @ b) ** 2) / dof)
    se = math.sqrt(s2 / max(np.sum((t_days - t_days.mean()) ** 2), 1e-9))
    slope_month, t_stat = float(b[1] * 30), float(b[1] / se) if se > 0 else 0.0
    return {
        "resid_mean_c": round(float(np.mean(r[-7:])), 1), "sigma_c": round(sigma, 2),
        "ewma_out_days": out_days, "ewma_stat": round(ewma_stat, 1), "cusum_max": round(float(s_max), 1),
        "trend_c_per_month": round(slope_month, 2), "trend_t": round(t_stat, 1),
        "sev_shift": severity(ewma_stat, EWMA_L), "sev_drift": severity(s_max, CUSUM_H),
        "sev_trend": severity(abs(t_stat), 3.0) if slope_month >= SLOPE_ALERT_C_PER_MONTH else 0.0,
    }


def current_series(g: pd.DataFrame) -> dict:
    g = g.sort_values("day")
    base, post = g[g.day < BASELINE_DAYS], g[g.day >= BASELINE_DAYS]
    if len(base) < 10 or len(post) < 5:
        return {}
    F = ["rms_per_load", "sideband_db"]
    mu = base[F].mean().to_numpy()
    cov = np.cov(base[F].to_numpy().T) + np.eye(2) * 1e-6
    inv = np.linalg.inv(cov)
    recent = post[F].tail(7).mean().to_numpy() - mu
    d = float(math.sqrt(recent @ inv @ recent))
    return {"mahalanobis": round(d, 1), "sev_current": severity(d, MAHAL_ALERT)}


def compute(reg: dict[str, pd.DataFrame]) -> pd.DataFrame:
    comp = reg["component"][["component_id", "kb_id"]]
    out = {c: {"component_id": c} for c in comp.component_id}
    ts = reg.get("thermal_series", pd.DataFrame())
    if "component_id" in ts:
        ts = ts.astype({"day": int, "temp_c": float, "ambient_c": float, "load_pct": float})
        for cid, g in ts.groupby("component_id"):
            out.setdefault(cid, {"component_id": cid}).update(temperature_series(g))
    cs = reg.get("current_series", pd.DataFrame())
    if "component_id" in cs:
        cs = cs.astype({"day": int, "rms_per_load": float, "sideband_db": float})
        for cid, g in cs.groupby("component_id"):
            out.setdefault(cid, {"component_id": cid}).update(current_series(g))
    # cross-sectional: temperature rise vs identical parts across the portfolio
    cond = reg.get("condition", pd.DataFrame())
    if "temp_c" in cond:
        c2 = cond.merge(comp, on="component_id", how="left")
        c2["rise"] = pd.to_numeric(c2.temp_c, errors="coerce") - pd.to_numeric(c2.ambient_c, errors="coerce")
        for kb_id, g in c2[c2.kb_id.fillna("") != ""].groupby("kb_id"):
            if len(g) < 4:
                continue
            sample = g.rise.dropna().to_numpy()
            for row in g.itertuples():
                if pd.notna(row.rise):
                    z = robust_z(row.rise, sample)
                    out[row.component_id].update({"peer_z": round(z, 1), "peer_n": len(sample), "sev_peer": severity(z, Z_ALERT)})
    df = pd.DataFrame(list(out.values()))
    sev_cols = [c for c in df.columns if c.startswith("sev_")]
    df["anomaly_severity"] = df[sev_cols].fillna(0).max(axis=1).round(2) if sev_cols else 0.0
    return df


def residual_chart(g: pd.DataFrame) -> list[dict]:
    """Per day: residual (actual - expected for load + ambient), its EWMA and the EWMA control limit, for charts."""
    g = g.astype({"day": int, "temp_c": float, "ambient_c": float, "load_pct": float}).sort_values("day")
    base = g[g.day < BASELINE_DAYS]
    if len(base) < 10:
        return []
    X = np.column_stack([np.ones(len(base)), base.load_pct])
    coef, *_ = np.linalg.lstsq(X, (base.temp_c - base.ambient_c).to_numpy(), rcond=None)
    r = g.temp_c.to_numpy() - (g.ambient_c.to_numpy() + np.column_stack([np.ones(len(g)), g.load_pct]) @ coef)
    sigma = max(float(np.std(r[: len(base)], ddof=2)), 0.3)
    limit = EWMA_L * sigma * math.sqrt(EWMA_LAMBDA / (2 - EWMA_LAMBDA))
    z, out = 0.0, []
    for d, v in zip(g.day, r):
        z = EWMA_LAMBDA * v + (1 - EWMA_LAMBDA) * z if d >= BASELINE_DAYS else 0.0
        out.append({"day": int(d), "residual_c": round(float(v), 2), "ewma_c": round(z, 2) if d >= BASELINE_DAYS else None,
                    "limit_c": round(limit, 2), "baseline": bool(d < BASELINE_DAYS)})
    return out
