# Model spec: how the money is calculated

[← index](index.md) · Data contract: [registry-format.md](../../build/registry-format.md) §5–7 (column names, `_low`/`_high` suffixes). **The column names there are the contract with Asher's code. Don't invent new ones without a line in `to-asher.md`.**

**Principle:** part prices, lifecycle status and lead times are **real**. Plant money is **synthetic, with ranges set from public benchmarks**. Every number carries a `source` label (measured / survey / vendor / estimate / assumption).

## 1. The calculation chain
Each table feeds the next. All are pandas DataFrames in → DataFrames out, with no database code (the app reads from and writes to SQLite).

```
listings ──► part_valuation ──► sourcing_recommendation ──► spof ──► capex_by_year ──► deal_adjustment (deal lens only)
                                        │                                          │
                                        └──────────────► plant_savings + price ◄──┘
```

| # | Table | File | How it's calculated |
|---|---|---|---|
| 1 | `part_valuation` | `sourcing.py` | Per part and condition: 25th / 50th / 75th percentile of listing prices → low / mid / high. Confidence: `high` ≥ 3 listings, `low` 1–2, `none` 0 (→ `alternatives`). |
| 2 | `sourcing_recommendation` | `sourcing.py` | **Shelf first, at any plant in the portfolio** (`use_shelf_spare`, minus transfer cost #20) → else `buy_spare` if it's a single point of failure (SPOF) and scarce → `migrate` if discontinued and few listings → else `monitor`. |
| 3 | `spof` | `valuation.py` | Yearly downtime exposure = P(fail) × **hours down** × **$/hour**, as low/high. **Hours down depend on step 2:** spare on the shelf (here or at a sister plant) = swap time (+ transfer time). No spare = lead time. Discontinued with no listings = lead time + migration time. A **redundant** machine (backed up) scores 0. |
| 4 | `capex_by_year` | `valuation.py` | `maintenance` = replacements due by age vs typical life. `deferred` = parts already past life or discontinued with no spare (catch-up spend, years 0–2). **`growth` can't be read off a nameplate**: leave it blank, or let the user type it in. |
| 5 | `deal_adjustment` | `valuation.py` | Only when a plant is being bought. **Price cut = PV(deferred CapEx, low).** **Holdback = PV(high − low)**: a verified register narrows that gap, which shrinks the holdback. Anchor escrow sizes to SRS Acquiom (#17, ⚠️ cite the exact report). |
| 6 | `plant_savings` + `price` | `pricing.py` | Savings per lever (below) → **price = capture % × auditable recurring savings** → payback = price ÷ (monthly savings). |

## 2. Formulas
**Downtime $/hour, calculated rather than typed in** (three separate inputs could contradict each other):
```
downtime_cost_per_hour = revenue_per_day / operating_hours_per_day × contribution_margin_pct  (+ idle labor, optional)
```
`lines.downtime_cost_per_hour_low/high` becomes a **derived** column (or a manual override). Tell Asher in `to-asher.md`.

**Failure probability:** set it by **age, condition and duty**, not by lifecycle status. A discontinued part isn't more likely to fail. It's harder to replace, so lifecycle status raises **hours down** (step 3), not the odds. Use datasheet MTBF only as an upper bound: it's a lab figure, not a field rate. Fallback bands are in velocity-prompts #4.

**Plant savings levers** (low / base / high, per plant per year):
| Lever | Formula | Recurring? | In the price base? |
|---|---|---|---|
| Carrying cost avoided | excess spares released × carrying % | yes | ✅ |
| Rush premiums avoided | rush_premium_annual × share avoided | yes | ✅ |
| Purchases avoided via a sister-plant spare | Σ (part value − transfer cost #20) | per event | ✅ (auditable: PO + transfer) |
| Planned vs emergency replacement | Σ P(fail) × (emergency − planned cost) | yes (expected) | ✅ with a haircut |
| Spares inventory released | excess % × spares inventory value | **one-time** | ❌ show it separately (it's cash freed, part of the liquidity story) |
| Downtime avoided | from `spof` | expected value | ❌ **show it separately, clearly labeled.** No defensible baseline. |

**Coverage scaling:** the $2M spares and $5M maintenance figures are **whole-plant** numbers, but the register covers only a sample of critical machines (~15 per plant). **Scale plant-level levers by the covered share**, or the results will be overstated ($2M ÷ 15 machines ≈ $130k each is only believable in heavy industry).

**Deal-lens value of a smaller holdback = time value, not the full amount:**
```
value = escrow points reduced × deal value × discount rate × years released earlier
```
Example: 1 point on a $50M deal = $500k released ~1 yr sooner ≈ **$50k at 10%**, not $500k. The claim that a register shrinks escrows is **not evidenced**, so run 0 / 0.5 / 1-point scenarios and label them.

**Price checks** (`pricing.py` flags any price that fails one):
1. Customer ROI ≥ 3× and payback ≤ 12 months (#6)
2. Plant price vs. the quick-approval ceiling, ~$10–25k (#19)
3. Plant price vs. comparables (distributor installed-base evaluation $6–10k, CMMS per site, #7)
4. Deal fee vs. (PV of the price cut + time value of the holdback): the fee should be a small share of what it finds
5. Gross margin after cost to serve (#18)

## 3. Real vs synthetic
| Real (collected or measured) | Synthetic (ranges set from benchmarks) |
|---|---|
| Part numbers (real parts inside the fake plants) | Plant financials: spares on hand, maintenance budget |
| Listing prices, sellers, authorized or not, URLs | Line revenue per day, contribution margin, operating hours |
| Lifecycle status (Rockwell / Siemens public lifecycle pages) | Failure probability by age band |
| Lead times (from listings / distributor pages) | Value-capture % (stays a variable) |
| Escrow figures (SRS Acquiom), deal multiples (PitchBook), ⚠️ cite exact reports | Excess-spares % (vendor sources 15–60%: use a conservative range, label it vendor) |
| Migration cost and downtime (OEM migration guides, labeled vendor) | Carrying cost % (assumption range until #2) |

**Listings, collected by hand, not scraped** (several sites forbid scraping in their terms):
- eBay sold listings (unauthorized, used)
- Radwell, PLC Center, EU Automation, DoSupply (surplus / refurbished, unauthorized)
- Authorized distributors for parts still sold new. AutomationDirect publishes prices; Rockwell and Siemens distributors often need a login, so expect gaps.
- Show counterfeit risk for every unauthorized seller.

**Coverage targets:** **3 parts by CP1** (+1 with no listings, to show the alternatives path). That's the registry default, and it's realistic alongside the coding. Then 10–15 by CP2 and up to ~30 (the KB size) only if there's time. Cover each lifecycle status at least once.

## 4. Demo-scale anchors (illustrative, label them)
- A plant with ~$150M revenue, 3 lines, 250 days/yr ≈ **$200k per line per day**.
- Deal value: EBITDA × a lower-middle-market multiple (PitchBook reports ~7x. ⚠️ Confirm the exact figure and date before putting it on a slide).
- Spares $2M, maintenance $5M per plant (registry defaults; whole-plant figures, see coverage scaling).

## 5. Guardrails
- Money is always low/high. Every row has a `source`.
- Don't put the one-time spares release or downtime avoided in the annual price base.
- Any figure marked ⚠️ stays off slides until its source is confirmed.
- Changing a column in registry-format.md means a line in `to-asher.md` before you build.

## Changes to tell Asher about (proposed, not yet in registry-format.md)
1. `lines.downtime_cost_per_hour` becomes derived (add `operating_hours_per_day`).
2. `capex_type = growth` is optional user input, not calculated.
3. `spof` hours depend on `sourcing_recommendation` (`valuation.py` reads the sourcing output).
4. Failure probability is set by age band (a parameter), not by lifecycle status.
5. `plant_savings` adds a column marking whether each lever is in the price base (`in_price_base`).
