"""Price sensitivity: capture % x savings case, full-plant quote. Run: python scripts/sensitivity.py [demo.db]

Prints Markdown. Every input comes from xray/params.py; prices from xray/pricing.py (no logic here beyond the grid).
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from xray import params as P  # noqa: E402
from xray.pricing import plant_savings, price  # noqa: E402
from xray.registry import load  # noqa: E402

CAPTURES = (P.VALUE_CAPTURE_PCT.low, P.VALUE_CAPTURE_PCT.base, P.VALUE_CAPTURE_PCT.high)
CASES = ("low", "base", "high")


def savings(reg: dict) -> pd.DataFrame:
    return plant_savings(reg, full_plant=True)


def grid(ps: pd.DataFrame) -> pd.DataFrame:
    """One row per plant x capture % x savings case: price, payback, ROI, gross margin, quick-yes zone."""
    rows = []
    for cap in CAPTURES:
        pr = price(ps, cap).set_index("plant_id")
        for case in CASES:
            p = pr[f"price_per_plant_{case}"]
            s = p / cap  # savings in this case (price = capture x savings)
            rows.append(pd.DataFrame({
                "plant_id": pr.index, "capture": cap, "case": case, "price": p, "savings": s,
                "payback_months": 12 * p / s, "roi": s / p,
                "gross_margin": (p - P.COST_TO_SERVE.base) / p,
                "quick_yes": p.between(P.APPROVAL_CEILING.low, P.APPROVAL_CEILING.high)}))
    return pd.concat(rows, ignore_index=True)


def portfolio(g: pd.DataFrame) -> pd.DataFrame:
    """Mean across the owned plants for each capture % x case."""
    a = g.groupby(["capture", "case"], sort=False)[["price", "savings"]].mean().reset_index()
    a["payback_months"] = 12 * a.price / a.savings
    a["gross_margin"] = (a.price - P.COST_TO_SERVE.base) / a.price
    a["quick_yes"] = a.price.between(P.APPROVAL_CEILING.low, P.APPROVAL_CEILING.high)
    return a


def portfolio_price(db_path=None, capture: float = P.VALUE_CAPTURE_PCT.base) -> tuple[float, float, float]:
    """Portfolio-average full-plant price per plant per year (low, base, high) at one capture %."""
    reg = load(db_path) if db_path else load()
    pr = price(savings(reg), capture)
    return tuple(float(pr[f"price_per_plant_{c}"].mean()) for c in CASES)


def k(x):
    return f"${x / 1e3:,.1f}k"


def main(db_path=None):
    reg = load(db_path) if db_path else load()
    ps = savings(reg)
    g = grid(ps)
    a = portfolio(g)

    print("### Portfolio average (5 owned plants): price / payback / gross margin\n")
    print("| Capture % | " + " | ".join(f"{c} savings" for c in CASES) + " |")
    print("|---|" + "---|" * len(CASES))
    for cap in CAPTURES:
        cells = [a[(a.capture == cap) & (a.case == c)].iloc[0] for c in CASES]
        print(f"| {cap:.0%} | " + " | ".join(
            f"{k(r.price)} / {r.payback_months:.1f} mo / {r.gross_margin:.0%}{' (quick-yes)' if r.quick_yes else ''}"
            for r in cells) + " |")

    cap = P.VALUE_CAPTURE_PCT.base
    print(f"\n### Per plant at {cap:.0%} capture\n")
    print("| Plant | Recurring savings (base) | Price low / base / high | Payback | ROI | Gross margin | Quick-yes ($10-25k) |")
    print("|---|---|---|---|---|---|---|")
    gp = g[g.capture == cap].pivot(index="plant_id", columns="case")
    for pid, r in gp.iterrows():
        print(f"| {pid} | {k(r[('savings', 'base')])} | {k(r[('price', 'low')])} / {k(r[('price', 'base')])} / "
              f"{k(r[('price', 'high')])} | {r[('payback_months', 'base')]:.1f} mo | {r[('roi', 'base')]:.1f}x | "
              f"{r[('gross_margin', 'base')]:.0%} | {'yes' if r[('quick_yes', 'base')] else 'no'} |")
    m = a[(a.capture == cap)].set_index("case")
    print(f"| **Average** | {k(m.savings['base'])} | {k(m.price['low'])} / {k(m.price['base'])} / {k(m.price['high'])} | "
          f"{m.payback_months['base']:.1f} mo | {1 / cap:.1f}x | {m.gross_margin['base']:.0%} | "
          f"{'yes' if m.quick_yes['base'] else 'no'} |")
    # Stress: list at the base price, but only the low savings show up.
    stress = 12 * m.price["base"] / m.savings["low"]
    print(f"\nStress: list at the base price ({k(m.price['base'])}) and only low-case savings show up "
          f"({k(m.savings['low'])}/yr): payback {stress:.1f} months.")

    print("\n### One-time spares release (cash freed once, not priced)\n")
    print("| Plant | Low | Base | High |")
    print("|---|---|---|---|")
    rel = ps[ps.lever == "spares_inventory_released"].set_index("plant_id")
    for pid, r in rel.iterrows():
        print(f"| {pid} | {k(r.savings_low)} | {k(r.savings_base)} | {k(r.savings_high)} |")

    print("\n### Recurring savings by lever (portfolio average, base)\n")
    lv = ps[(ps.in_price_base == "yes") & (ps.one_time == "no")].groupby("lever")[
        ["savings_low", "savings_base", "savings_high"]].mean().sort_values("savings_base", ascending=False)
    tot = lv.savings_base.sum()
    print("| Lever | Low | Base | High | Share of base |")
    print("|---|---|---|---|---|")
    for name, r in lv.iterrows():
        print(f"| {name} | {k(r.savings_low)} | {k(r.savings_base)} | {k(r.savings_high)} | {r.savings_base / tot:.0%} |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
