"""Bottom-up numbers for the Equipment Health Index story. Run: python scripts/market_model.py

Every input is labeled MEASURED (published count), VELOCITY (Velocity Research model/assumption, Nov 14 2026),
or OURS (our assumption). Sources are in docs/research/deep-dive-numbers.md.
"""

# ---------- inputs ----------
US_MFG_DEALS = 1_667                 # MEASURED  Travelers/PitchBook, US manufacturing transactions 2024
DEALS_WITH_REVIEW = (450, 670, 900)  # VELOCITY  distinct deals getting an on-site M&E appraisal and/or controls review
APPRAISALS, CONTROLS_REVIEWS = 385, 445  # VELOCITY base-case events per year

APPRAISAL_FEE = 12_800               # VELOCITY  64 professional hours x $200/h, mid-market plant
APPRAISAL_SAVING = (400, 700, 1_000) # VELOCITY  2-5 hours of capture/reconciliation
CONTROLS_FEE = 20_000                # VELOCITY  104 person-hours, 2 engineers x 3 days + offsite
CONTROLS_SAVING = (1_400, 3_400, 5_500)  # VELOCITY  9 / 21 / 34 hours

PLANTS_100 = 16_807 + 5_727 + 2_254 + 1_011   # MEASURED  Census CBP 2022, NAICS 31-33, establishments with 100+ employees
PLANTS_250 = 5_727 + 2_254 + 1_011            # MEASURED  250+ employees
PLANT_VALUE = (10_000, 30_000, 60_000)        # VELOCITY  recurring, auditable value per plant per year (inventory carrying + rush premiums)
PLANT_ONE_TIME = (100_000, 200_000, 400_000)  # VELOCITY  one-time spares inventory reduction (not annual)
PRICES = (10_000, 25_000, 50_000)             # OURS      fallback annual price per plant to test
try:  # MODEL  portfolio-average full-plant price at 20% capture, low / base / high (scripts/sensitivity.py)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sensitivity import portfolio_price
    PRICES = tuple(round(p, -2) for p in portfolio_price())
    PRICE_SOURCE = "financial model, demo registry, full plant at 20% capture (low / base / high)"
except Exception as e:  # no demo.db or model error: keep the constants
    PRICE_SOURCE = f"fallback constants (model unavailable: {type(e).__name__})"
ADOPTION = (0.02, 0.05, 0.10)                 # OURS

BUILD, RUN, YEARS = 600_000, 250_000, 3       # VELOCITY  narrow accelerator for a consulting firm
FEE_UPLIFT, MARGIN, HOURS, RATE, REVIEW = 15_000, 0.60, 20, 150, 2_000  # VELOCITY base case


def m(x):
    if x >= 1e6:
        return f"${x / 1e6:,.1f}M"
    return f"${x / 1e3:,.0f}k" if x >= 1e4 else f"${x:,.0f}"


print("## A. Diligence channel: supplementing appraisals and controls reviews (per year, US)")
for name, events, saving in [("M&E appraisal capture", APPRAISALS, APPRAISAL_SAVING),
                             ("Controls/obsolescence review", CONTROLS_REVIEWS, CONTROLS_SAVING)]:
    lo, base, hi = (events * s for s in saving)
    print(f"- {name}: {events} events x {m(saving[0])}/{m(saving[1])}/{m(saving[2])} saved "
          f"= {m(lo)} / {m(base)} / {m(hi)} of labor freed per year")
for d in DEALS_WITH_REVIEW:
    print(f"- New paid module ({m(FEE_UPLIFT)}/deal) if EVERY reviewed deal bought it: {d} x {m(FEE_UPLIFT)} = {m(d * FEE_UPLIFT)}")

print("\n## B. Own-plant channel (recurring, US plants with 100+ employees)")
print(f"- Plants: {PLANTS_100:,} with 100+ employees, {PLANTS_250:,} with 250+ (Census CBP 2022)")
print(f"- Value per plant per year (Velocity): {m(PLANT_VALUE[0])} / {m(PLANT_VALUE[1])} / {m(PLANT_VALUE[2])}"
      f"  + one-time {m(PLANT_ONE_TIME[0])} / {m(PLANT_ONE_TIME[1])} / {m(PLANT_ONE_TIME[2])} inventory release")
print(f"- Prices tested: {PRICE_SOURCE}")
print("\n| Price / plant / yr | " + " | ".join(f"{a:.0%} adoption" for a in ADOPTION) + " | 100% (ceiling) |")
print("|---|" + "---|" * (len(ADOPTION) + 1))
for p in PRICES:
    print(f"| {m(p)} | " + " | ".join(m(PLANTS_100 * a * p) for a in ADOPTION) + f" | {m(PLANTS_100 * p)} |")

print("\n## C. Consulting firm: break-even for a narrow assessment accelerator")
hurdle = BUILD / YEARS + RUN
per = FEE_UPLIFT * MARGIN + HOURS * RATE - REVIEW
print(f"- Annual hurdle: {m(BUILD)} build / {YEARS} yrs + {m(RUN)} run = {m(hurdle)}")
print(f"- Contribution per engagement: {m(FEE_UPLIFT)} x {MARGIN:.0%} + {HOURS} h x ${RATE} - {m(REVIEW)} = {m(per)}")
print(f"- Break-even: {hurdle / per:.0f} engagements per year")
print(f"- Photo-capture savings only ({m(APPRAISAL_SAVING[1])}/job): {hurdle / APPRAISAL_SAVING[1]:,.0f} engagements per year (not viable)")
for conv, plants, price in [(0.3, 3, 25_000)]:
    extra = 50 * conv * plants * price
    print(f"- Follow-on: 50 deals x {conv:.0%} convert to a post-close program x {plants} plants x {m(price)}/yr "
          f"= {m(extra)}/yr recurring (stacks each year it renews)")
