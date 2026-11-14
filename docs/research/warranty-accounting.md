# Warranty accounting: guardrails, data needs, and who decides what

🛠 Warranty thread (Brandon) owns this doc. Status: **research notes + design rules.** The accounting-standard references below are **not yet verified** (research is running, see the last section). Don't put them on a slide until they're cited.

How this changes the plan and the data contract: [../plan/plan-updates.md, Update 5](../plan/plan-updates.md) and [cp0-proposal.md, item 21](cp0-proposal.md#21-warranty-accounting-fit-proposed).

## Why accounting matters for Afterlife
The tool turns linked claims into dollar figures. A Kearney or finance judge will check whether those figures are counted honestly:
- Is an alert being presented as a booked liability?
- Is supplier money being counted before the supplier has agreed to pay?
- Is the same part being counted twice?

Getting these right is cheap, and it reads as "built by people who understand how finance works."

## Guardrails (design rules, not just pitch caveats)
1. **Analytics estimate ≠ booked accrual.** For a standard product warranty (one that only promises the product works), US GAAP generally books an estimated liability at the time of sale, once claims are probable and can be estimated, and updates it as claims come in. Afterlife's cross-product alerts can *inform* that update. They never post journal entries.
2. **Warranty types differ.** Separately sold or extended coverage is a service. Revenue for it may be recognized over the coverage period, not just accrued as repair cost. Tag the coverage or claim type in the data.
3. **Supplier recovery isn't money until it's settled.** Track each stage as a separate amount:
   - potential (the Velocity reframe calls it "recovery opportunity")
   - contract-eligible
   - submitted
   - accepted or disputed
   - settled
   - recognized by finance

   Only the last two are money.
4. **No double counting in "true cost".** A part bought to restock warranty repairs shows up in `service_spend` (`channel = warranty_repair`) *and* in the claim's `parts_cost`. Reconcile parts, labor, freight, accruals, claims and recoveries before rolling them into lifecycle cost.
5. **Traceability.** Keep the build-month group, product, part, supplier, lot, claim and run IDs on every output, so finance can trace any dashboard number back to its transactions. Contract v3 already has most of this (`build_supply`, `links.evidence`, `runs`).

### Wording (consistent with the Velocity reframe in `docs/plan/concept.md`)
| Term | Meaning | Where Afterlife uses it |
|---|---|---|
| exposure | cost of claims **linked** to a part/supplier (our estimate) | `alerts.exposure_usd` |
| excess cost | the part of exposure above what the baseline rate predicts | `alerts.excess_cost_usd` |
| open exposure | exposure from claims not already submitted or recovered, and not goodwill or campaign | `alerts.open_exposure_usd` |
| recovery opportunity | a scenario range (25–50% capture today), clearly labelled | API, brief |
| contract-eligible | what the supplier's warranty terms allow (needs `supplier_warranty_terms`, proposed) | future |
| accrual | finance's booked liability. **We only inform it** | never an output |
| receivable | settled with the supplier, or recognized by finance | never an output |

Never call an alert an accrual. Never call an opportunity "recoverable" or "owed".

## Accounting factors worth tracking
| Stage | Factor | Why | In contract v3? |
|---|---|---|---|
| Claim cost | parts (dealer price + handling), labor (flat-rate hours × dealer rate) | Gross cost the OEM pays, and what it could recover | ✅ `parts_cost`, `labor_cost`, `labor_hrs` |
| Claim cost | freight / sublet | Often claimable from suppliers | ❌ (claim line items were rejected at CP0; mention in Q&A) |
| Claim type | `warranty` / `goodwill` / `campaign` | Goodwill usually can't be recovered; recalls/campaigns are reserved separately | ❌ **proposed** |
| Recovery stage | `recovery_status` | Don't claim money that's already submitted or recovered | ✅ (`none / submitted / recovered`) |
| Exposure | units in warranty by build group, cost per unit by months in service, expected remaining cost | The forward estimate that informs the accrual review | partial (inputs exist; output `projected_remaining_usd` proposed) |
| Attribution | causal part, supplier lot (`build_supply`), confidence, evidence | Who is responsible, and how sure we are | ✅ |
| Net cost | gross claims − settled recoveries, as a % of revenue vs. SEC peers | The headline number | ❌ needs **`products.net_price`** (proposed) |
| Lifecycle cost | build + spares + **net** warranty, with no double counting | Coordinate with the spend thread | rule **proposed** |
| Contract terms | recovery %, labor rate cap, handling %, submission window, parts-return requirement, no-fault-found rate | Turns the flat scenario into a calculation, and enables "$X expires in 30 days" | ❌ decide after research |
| Warranty start | in-service / delivery date | Real warranties start at sale, not build | ❌ simplification: months in service counted from `build_month` |

**Skip this weekend:** an accrual or rollforward table (opening balance + accruals − payments ± changes in estimate), coverage type (base vs. extended), currency conversion, paid date or accounting period. A rollforward needs finance data we don't simulate, so cover it in Q&A. Our SEC reference file uses the "payments" line of that disclosure.

## Who decides what
| | What | Notes |
|---|---|---|
| **Fixed rules** | cost component totals, months in service, claim rates per 1,000 units, cost per unit by build group, deadline aging, the double-count rule, rollforward math, confidence gates, excess / open exposure | Same input, same output. Every number in the brief comes from here |
| **Statistics** (a fixed method, uncertain answer) | spike detection (Poisson change point + significance test), projecting each build group to the end of warranty, splitting claims between suppliers when sourcing is mixed (`attribution = deconvolved / ambiguous`) | Show ranges or flag weak evidence. Never present as exact |
| **AI proposes** | causal part for ambiguous claims (tie-break), normalizing claim text into symptom and cause, brief wording, *(stretch)* extracting terms from a supplier agreement PDF | **AI never sets an amount, an accounting status or a recognition decision** |
| **Evaluation** (pytest) | accuracy vs. answer key, spike caught on several seeds, no false alarms on data with no spike, open exposure excludes goodwill and recovered claims, rollforward balances, lifecycle cost ≤ sum of parts, every number in the brief exists in results | Runs without an API key |
| **Human review** | low-confidence links before they feed recovery (supplier quality engineer); submitting a claim to a supplier (procurement / supplier quality); any accrual change (finance / controller); deciding whether a spike becomes a field campaign (quality); disputes; checking AI-extracted contract terms | Stage gates go through the `decisions` table (v3 #19) |

**Pitch line:** "Afterlife computes and proposes. People approve anything that touches money or the books."

## What's built (detect.py v1)
`alerts` now carries `exposure_usd`, `excess_cost_usd` and `open_exposure_usd`, plus `claims`, `p_value` and `attribution`. Open exposure already excludes `recovery_status != none`. It also excludes `claim_type != warranty` once that column exists, so detect doesn't need to change when the proposed `claim_type` lands.

## References to verify (research running)
Each one needs a verdict, the exact paragraph, and safe slide wording:
- [ ] US GAAP: standard product warranties under ASC 460 (accrue when probable and estimable, at sale); service-type or separately sold warranties under ASC 606.
- [ ] ASC 460 warranty rollforward disclosure; is `ProductWarrantyAccrualPayments` the XBRL tag for the payments line?
- [ ] IFRS (IAS 37): a reimbursement is a separate asset only when "virtually certain". US GAAP: loss recoveries count when probable, up to the loss, with any excess a gain contingency (ASC 450-30). Which applies to supplier warranty recovery?
- [ ] Recalls and field campaigns are reserved separately from the ordinary warranty accrual.
- [ ] Goodwill repairs are generally not recoverable from suppliers.
- [ ] Spend-side factors with accounting impact, for the spend thread: purchase price variance (PPV), landed cost (freight, duty, tariffs), rebates, payment-term discounts, currency rate choice, inventory valuation method, transfer prices between plants or to dealers. Which of these could double count with warranty?
- [ ] Field availability in real enterprise systems (SAP WTY / dealer portals, MM, FI/CO, batch traceability): supplier warranty terms, `claim_type`, in-service date, paid date, cost by component, serial-to-batch, product net price.

Sources the notes were built from: PwC (US warranty guidance), IAS 37, Deloitte (US loss recoveries). Add exact links when verified.
