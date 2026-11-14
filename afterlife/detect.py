"""Early-warning spike detection. [WARRANTY thread · Brandon] Milestone M4.

Pool claims across ALL products sharing a part. Two views (decided at CP0):
  raw  : claims per 1,000 built by build_month (intuitive chart, biased toward recent builds)
  mis  : claims within MIS_WINDOW months in service per 1,000 built, MATURE build months only
         (build_month + MIS_WINDOW <= data_as_of). Alerts use THIS view.

v3 #13 supplier attribution: claims don't say which supplier's part was fitted. build_supply says
which supplier lot each (product, build_month, part) consumed and in what share. Each cell is:
  clean       : one supplier (share = 1). Its claims belong to that supplier.
  deconvolved : mixed, but every OTHER supplier in the cell has a clean rate that month, so their
                expected claims are subtracted and the remainder is this supplier's.
  ambiguous   : mixed and can't be separated. Claims are split by share (weakest evidence).
A supplier-month's alert rate comes from its clean cells when it has any, otherwise from the
attributed claims.

Change point (per part x supplier, mature months only): pick the split that best explains the
counts as two Poisson rates (max log-likelihood), not the split with the biggest ratio (that one
chases noisy one-month baselines). Alert only if ALL hold:
  - at least MIN_BASELINE_MONTHS before the split
  - after/before rate >= RATIO_MIN, with >= MIN_CLAIMS claims after
  - two-sample test: given the total claims before + after, the chance that as few fell before as
    observed, if both periods shared one rate (conditional binomial). This accounts for the
    baseline being noisy too. p < P_MAX.
  Tuned on synthetic data (tests/test_detect.py): at realistic volume, 0 false alarms in 50 clean
  datasets and every 3x spike caught; at low volume (~6 claims/month pooled) ~5-8% false alarms.

Accounting (docs/research/warranty-accounting.md): $ here are analytics estimates, never accruals
or receivables.
  exposure_usd      : cost of claims linked + attributed to this part/supplier since the start month
  excess_cost_usd   : the part of that cost above what the baseline rate predicts (the conservative
                      starting point for a recovery review)
  open_exposure_usd : exposure from claims still open for recovery (recovery_status == "none", and
                      claim_type == "warranty" when the column exists: goodwill/campaign excluded)
Output columns: see alerts in docs/build/data-contract.md.
"""
import math

import numpy as np
import pandas as pd

RATIO_MIN = 2.0
MIN_CLAIMS = 10
MIN_BASELINE_MONTHS = 2
P_MAX = 0.05
MIS_WINDOW = 3  # default; dataset_info.mis_window wins
CLAIM_SOURCE = "warranty_claims"
PER = 1000.0  # rates are claims per 1,000 built
ZERO_BASELINE_PSEUDO_CLAIMS = 0.5  # a baseline with no claims is treated as half a claim, not zero
OPEN_RECOVERY_STATUS = "none"
RECOVERABLE_CLAIM_TYPE = "warranty"
CELL = ["product_id", "build_month", "part_no"]
_EVIDENCE_ORDER = ["clean", "deconvolved", "ambiguous"]  # strongest first


def months_between(build_month: str, date: str) -> int:
    """Whole calendar months from build_month (YYYY-MM) to date (YYYY-MM[-DD]). Same month = 0."""
    by, bm = int(build_month[:4]), int(build_month[5:7])
    y, m = int(date[:4]), int(date[5:7])
    return (y - by) * 12 + (m - bm)


def binom_cdf(x: float, n: float, p: float) -> float:
    """P(B <= x) for B ~ Binomial(n, p). x, n rounded to whole claims."""
    x, n = int(round(x)), int(round(n))
    if x < 0:
        return 0.0
    if x >= n or p >= 1:
        return 1.0
    if p <= 0:
        return 1.0
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                                 + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(x + 1)))


def step_p_value(bc: float, bu: float, ac: float, au: float) -> float:
    """One-sided two-sample test for a step UP in Poisson rate: under 'same rate', the before-period's
    share of all claims is Binomial(total, bu / (bu + au)). Small p = too few claims before."""
    return binom_cdf(bc, bc + ac, bu / (bu + au))


def _info(tables) -> dict:
    di = tables.get("dataset_info")
    return {} if di is None else dict(zip(di.key.astype(str), di.value.astype(str)))


def mis_window(tables) -> int:
    return int(float(_info(tables).get("mis_window", MIS_WINDOW)))


def _supply(tables) -> pd.DataFrame:
    """(product, build_month, part, supplier, po_line_id, share, units_built), one row per supplier in a cell."""
    builds = tables["builds"][["product_id", "build_month", "units_built"]]
    bs = tables.get("build_supply")
    if bs is None or bs.empty:  # no traceability: one unnamed supplier per BOM line
        bs = tables["bom"][["product_id", "part_no"]].merge(builds[["product_id", "build_month"]], on="product_id")
        bs = bs.assign(supplier_id="", po_line_id="", share=1.0)
    out = bs[CELL + ["supplier_id", "po_line_id", "share"]].merge(builds, on=["product_id", "build_month"])
    out["share"] = out.share.astype(float)
    out["units_built"] = out.units_built.astype(float)
    return out[out.share > 0]


def _cell_claims(tables, links: pd.DataFrame, window: int) -> pd.DataFrame:
    """Per (product, build_month, part): raw claims, claims within `window` MIS, their cost, and open cost."""
    cols = CELL + ["raw_claims", "mis_claims", "cost", "open_cost"]
    claims = tables["warranty_claims"]
    cl = links[links.source_table == CLAIM_SOURCE][["source_id", "part_no"]].drop_duplicates("source_id")
    c = claims.merge(cl, left_on="claim_id", right_on="source_id")
    if c.empty:
        return pd.DataFrame(columns=cols)
    c["mis"] = [months_between(b, f) for b, f in zip(c.build_month.astype(str), c.failure_date.astype(str))]
    c = c[c.mis >= 0].copy()
    c["in_window"] = (c.mis <= window).astype(int)
    c["cost"] = pd.to_numeric(c.parts_cost, errors="coerce").fillna(0) + pd.to_numeric(c.labor_cost, errors="coerce").fillna(0)
    is_open = c.recovery_status.astype(str).str.lower().eq(OPEN_RECOVERY_STATUS) if "recovery_status" in c else True
    if "claim_type" in c:
        is_open = is_open & c.claim_type.astype(str).str.lower().eq(RECOVERABLE_CLAIM_TYPE)
    c["open_cost"] = c.cost.where(is_open, 0.0)
    return (c.groupby(CELL).agg(raw_claims=("claim_id", "size"), mis_claims=("in_window", "sum"),
                                cost=("cost", "sum"), open_cost=("open_cost", "sum"))
            .reset_index())


def claim_rates(tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> pd.DataFrame:
    """-> part_no, supplier_id, build_month, units_built, raw_claims, raw_rate, mis_claims, mis_rate, mature,
    plus attribution (clean/deconvolved/ambiguous), po_line_id (main lot that month), products,
    rate_units / rate_mis_claims (the denominator and numerator behind mis_rate, for pooling),
    and cost_usd / open_cost_usd (attributed claim cost, and the part still open for recovery)."""
    window = mis_window(tables)
    sup = _supply(tables)
    cells = sup.merge(_cell_claims(tables, links, window), on=CELL, how="left").fillna(
        {"raw_claims": 0, "mis_claims": 0, "cost": 0.0, "open_cost": 0.0})
    cells["units"] = cells.units_built * cells.share
    cells["n_suppliers"] = cells.groupby(CELL).supplier_id.transform("size")
    cells["is_clean"] = cells.n_suppliers == 1

    # clean per-unit rates per (part, supplier, month), pooled over products
    key = ["part_no", "supplier_id", "build_month"]
    clean = (cells[cells.is_clean].groupby(key)
             .agg(clean_units=("units", "sum"), clean_raw=("raw_claims", "sum"), clean_mis=("mis_claims", "sum"))
             .reset_index())
    clean["r_raw"] = clean.clean_raw / clean.clean_units
    clean["r_mis"] = clean.clean_mis / clean.clean_units

    # attribute each cell's claims to each supplier in it
    cells = cells.merge(clean[key + ["r_raw", "r_mis"]], on=key, how="left")
    cells["exp_raw"] = cells.units * cells.r_raw
    cells["exp_mis"] = cells.units * cells.r_mis
    g = cells.groupby(CELL)
    cells["others_known"] = (g.r_raw.transform(lambda s: s.notna().sum()) - cells.r_raw.notna()) == cells.n_suppliers - 1
    cells["others_exp_raw"] = g.exp_raw.transform("sum") - cells.exp_raw.fillna(0)
    cells["others_exp_mis"] = g.exp_mis.transform("sum") - cells.exp_mis.fillna(0)
    cells["evidence"] = np.where(cells.is_clean, "clean", np.where(cells.others_known, "deconvolved", "ambiguous"))
    for v in ["raw", "mis"]:
        deconv = (cells[f"{v}_claims"] - cells[f"others_exp_{v}"]).clip(lower=0)
        split = cells[f"{v}_claims"] * cells.share
        cells[f"attr_{v}"] = np.select([cells.is_clean, cells.others_known],
                                       [cells[f"{v}_claims"], deconv], split)
    # cost follows the claims: the same fraction of the cell's cost goes to each supplier
    frac = np.where(cells.raw_claims > 0, cells.attr_raw / cells.raw_claims.where(cells.raw_claims > 0, 1), 0.0)
    cells["attr_cost"] = cells.cost * frac
    cells["attr_open_cost"] = cells.open_cost * frac

    lot = (cells.sort_values("units", ascending=False).drop_duplicates(key)[key + ["po_line_id"]])
    out = (cells.groupby(key)
           .agg(units_built=("units", "sum"), raw_claims=("attr_raw", "sum"), mis_claims=("attr_mis", "sum"),
                cost_usd=("attr_cost", "sum"), open_cost_usd=("attr_open_cost", "sum"),
                products=("product_id", "nunique"),
                attribution=("evidence", lambda s: min(s, key=_EVIDENCE_ORDER.index)))
           .reset_index()
           .merge(clean[key + ["clean_units", "clean_mis"]], on=key, how="left")
           .merge(lot, on=key, how="left"))
    has_clean = out.clean_units.notna()
    out["rate_units"] = np.where(has_clean, out.clean_units, out.units_built)
    out["rate_mis_claims"] = np.where(has_clean, out.clean_mis, out.mis_claims)
    out["raw_rate"] = PER * out.raw_claims / out.units_built
    out["mis_rate"] = PER * out.rate_mis_claims / out.rate_units

    as_of = _info(tables).get("data_as_of")
    out["mature"] = ([months_between(b, as_of) >= window for b in out.build_month] if as_of
                     else False)
    cols = ["part_no", "supplier_id", "build_month", "units_built", "raw_claims", "raw_rate", "mis_claims",
            "mis_rate", "mature", "attribution", "po_line_id", "products", "rate_units", "rate_mis_claims",
            "cost_usd", "open_cost_usd"]
    return out[cols].sort_values(key).reset_index(drop=True)


ALERT_COLUMNS = ["part_no", "supplier_id", "products_affected", "start_build_month", "mis_window",
                 "baseline_rate", "current_rate", "ratio", "p_value", "claims", "exposure_usd",
                 "excess_cost_usd", "open_exposure_usd", "from_po_line_id", "attribution", "spike_claims"]


def _loglik(c: float, u: float) -> float:
    """Poisson log-likelihood (up to a constant) of c claims on u units at the MLE rate c/u."""
    return c * math.log(c / u) - c if c > 0 else 0.0


def _best_change_point(g: pd.DataFrame):
    """Split a supplier's mature months (sorted) into before/after at the most likely step change.
    -> (start_index, baseline_rate, current_rate, ratio, after_claims, p_value) or None."""
    u, c = g.rate_units.to_numpy(float), g.rate_mis_claims.to_numpy(float)
    best, best_ll = None, -math.inf
    for k in range(MIN_BASELINE_MONTHS, len(g)):
        bu, bc, au, ac = u[:k].sum(), c[:k].sum(), u[k:].sum(), c[k:].sum()
        if bu <= 0 or au <= 0 or ac / au <= bc / bu:  # step UP only
            continue
        ll = _loglik(bc, bu) + _loglik(ac, au)
        if ll > best_ll:
            base = max(bc, ZERO_BASELINE_PSEUDO_CLAIMS) / bu
            best_ll = ll
            best = (k, PER * bc / bu, PER * ac / au, (ac / au) / base, ac, step_p_value(bc, bu, ac, au))
    return best


def find_spikes(rates: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """One alert per (part, supplier) whose mature mis rate steps up significantly (see module doc)."""
    window = mis_window(tables)
    mature = rates[rates.mature].sort_values("build_month")
    sup = _supply(tables)
    alerts = []
    for (part, supplier), g in mature.groupby(["part_no", "supplier_id"]):
        g = g.reset_index(drop=True)
        cp = _best_change_point(g)
        if cp is None:
            continue
        k, base, cur, ratio, spike_claims, p = cp
        if ratio < RATIO_MIN or spike_claims < MIN_CLAIMS or p >= P_MAX:
            continue
        start = g.build_month[k]
        since = rates[(rates.part_no == part) & (rates.supplier_id == supplier) & (rates.build_month >= start)]
        used = sup[(sup.part_no == part) & (sup.supplier_id == supplier) & (sup.build_month >= start)]
        exposure = float(since.cost_usd.sum())
        alerts.append({
            "part_no": part, "supplier_id": supplier,
            "products_affected": used.product_id.nunique(),
            "start_build_month": start, "mis_window": window,
            "baseline_rate": round(base, 2), "current_rate": round(cur, 2), "ratio": round(ratio, 2),
            "p_value": float(f"{p:.3g}"),
            "claims": int(round(since.raw_claims.sum())),
            "exposure_usd": round(exposure, 2),
            "excess_cost_usd": round(exposure * (1 - 1 / ratio), 2),
            "open_exposure_usd": round(float(since.open_cost_usd.sum()), 2),
            "from_po_line_id": g.po_line_id[k],
            "attribution": max(g.attribution.iloc[k:], key=_EVIDENCE_ORDER.index),
            "spike_claims": int(round(spike_claims)),
        })
    return pd.DataFrame(alerts, columns=ALERT_COLUMNS).sort_values("ratio", ascending=False).reset_index(drop=True)
