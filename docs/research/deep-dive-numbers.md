# Deep dive: is there a defensible number? (Sat Nov 14, evening)

**Question from the mentor:** we won't replace appraisers, so in a deal we're an **extra cost**. Is supplementing part of the on-site work worth it? And is a tool for **evaluating your own plants as well as acquisitions** worth a consulting firm's time and money?

**Method:**
- 7 Velocity Research chats (Buffalo team space, Nov 14), each told to push back on our assumptions
- Census Bureau data pulled directly
- a model you can rerun: `python scripts/market_model.py`

**Labels:**
- **MEASURED**: a published count
- **VELOCITY**: Velocity's sourced model or assumption
- **OURS**: our assumption

---

## The 30-second answer
1. **Supplementing the M&E appraisal is NOT a defensible business.** Photo capture saves about **2–5 of ~64 hours (~$400–1,000 per appraisal)**, because research and the report are most of the work. Across all US deals, that's **~$270k a year**. Drop it as a pitch.
2. **Supplementing the *controls / obsolescence* review is real but modest.** It saves **~21 of ~104 hours (~$3,400 of a ~$20k job, 17%)**, about **$1.5M a year** across US deals. That's an efficiency story, not a business.
3. **The defensible number is the *decision*, not the hours.** Our output (part IDs → end-of-life and spares flags → line criticality → 3–5-year CapEx range) is a **new deliverable** a buyer pays **$10–20k** for. Vendor cases show it can move price by millions ($4.1M of CapEx found in a 2-day assessment). The cases show the stakes, not how often it happens.
4. **Using it on your own plants is the bigger market:**
   - **25,799 US plants with 100+ employees** (MEASURED)
   - **$10k / $30k / $60k** of recurring auditable value per plant per year, plus a **one-time $100–400k** in spares released (VELOCITY)
   - at a realistic **$10–25k per plant per year** and **5% adoption**, that's **$13–32M ARR**, with a **$258–645M ceiling**
5. **For a consulting firm (e.g. Kearney): conditional GO on a narrow, expert-reviewed "assessment accelerator", NO-GO on a broad AI platform.**
   - Breakeven is **~45 paid engagements a year** at a **$15k fee uplift**.
   - On photo savings alone, it would take 643 a year, which is not viable.
   - Post-close plant programs stack recurring revenue on top.

**So the story becomes:** *"We don't replace the appraiser. We give the deal team and the plant owner a decision they don't get today: which hidden parts stop which lines, what it costs, and when. The deal is where the record starts; owning the plant is where it pays."*

---

## A. Where the appraiser's hours actually go (VELOCITY, mid-market plant, ~150 assets)
| Work package | Hours | Share |
|---|---|---|
| Scope + pre-visit records review | 6 | 9% |
| On-site capture and observation | 12 | 19% |
| Register matching + exceptions | 8 | 13% |
| Market, cost and lifecycle research | 24 | 38% |
| Valuation analysis, report, review | 14 | 22% |
| **Total** | **64 (~$12,800 at $200/h)** | |

- Field productivity: about **15–30 substantial machines per appraiser-day** (one practitioner example: 20 CNCs in a day, 2 days of research, 1 day of report).
- Published fees: **$3.5–7.5k** for a small plant, **$8–18k** mid-market, **$18–40k+** large.
- **What photos can save:** the clerical part of capture and reconciliation, **2–5 hours**.
- **What they can't save:** existence and condition checks, valuation judgment, the signed USPAP report.
- Velocity's pushback: "a striking improvement in plate transcription may produce only a modest reduction in the client's overall appraisal bill."

## B. Where the controls-review hours go (VELOCITY, 60 panels, ~360 component records)
| Work package | Person-hours | Share |
|---|---|---|
| Physical inventory (access, photos, labels, recording) | 32 | 31% |
| Other onsite (orientation, interviews, dependencies) | 16 | 15% |
| Offsite transcription, normalization, reconciliation | 12 | 12% |
| Lifecycle lookup + exceptions | 10 | 10% |
| Risk + budgetary migration/CapEx estimate | 22 | 21% |
| Report, QA, readout | 12 | 12% |
| **Total** | **104 (~$20k incl. travel)** | |

- Price anchors:
  - Rockwell-style distributor IBE: **$5–15k** (most $6–10k), 1–2 days
  - Avanceon fixed-fee discovery: **$15k**, 3–5 days on site
  - remote assessment: $7.5k, plus **$2,800 per day** for a walkdown
  - Siemens engineers bill **$290–341 per hour**
- **Savings from photo ID + automatic lifecycle lookup:** 9 / 21 / 34 hours, worth **$1.4k / $3.4k / $5.5k** (7% / 17% / 28%).
- **Caveats:**
  - A label photo doesn't establish **firmware**.
  - Assessors don't open live panels; the plant handles access.
  - Rockwell and Siemens already have software for the lookup step.
- **Cadence:** about one pass per acquired plant. Owners re-walk **every 3–5 years**, or yearly under service contracts.

## C. How many deals (VELOCITY, anchored on a MEASURED count)
- **1,667 US manufacturing acquisitions in 2024** (Travelers/PitchBook, MEASURED).
- About **385 on-site M&E appraisals and ~445 controls reviews a year**, so **~670 distinct deals** (range **450–900**). These are modeled, because no body publishes the count.
- AMEA has ~250 equipment-appraiser members worldwide. A public directory shows **729 PE-backed US manufacturers**, a lower bound.

| Diligence lens (US per year) | Conservative | Base | Optimistic |
|---|---|---|---|
| Appraisal hours freed | $154k | $270k | $385k |
| Controls-review hours freed | $623k | $1.5M | $2.4M |
| New $15k decision module, if **every** reviewed deal bought it | $6.8M | $10.1M | $13.5M |

**Verdict:** diligence alone is a **~$10M ceiling**. It's a wedge, not the business.

## D. Your own plants (MEASURED plant counts × VELOCITY value)
- **Plants:**
  - **25,799** US manufacturing establishments with **100+ employees**, of which **8,992 have 250+**
  - 285,500 manufacturing establishments in total
  - Source: Census County Business Patterns 2022, NAICS 31-33
- **Value per plant per year (VELOCITY)**, on a $2M spares inventory and a $5M maintenance budget:

  | Lever | Conservative | Base | Optimistic |
  |---|---|---|---|
  | One-time spares inventory release | $100k | $200k | $400k |
  | Recurring carrying cost avoided | $10k | $20k | $40k |
  | Rush and expedite premiums avoided | $0 | $10k | $20k |
  | **Recurring auditable total** | **$10k** | **$30k** | **$60k** |

  Downtime avoided is excluded on purpose, since there's no defensible baseline. One avoided 8-hour outage at $5k per hour is $40k in that year.
- **Documented cases (vendor-reported):**
  - 5 sites: inventory **$84.8M → $49.2M**, purchases **−$5.7M a year** (Perspect). The headline and table disagree.
  - MANN+HUMMEL found a failed inverter at a sister plant, so the outage lasted "a few hours instead of a few days."
  - Verusen, 17 rigs: **$48M identified but only $3.3M verified**, a warning that identified value is not realized value.

| Price / plant / yr | 2% adoption | 5% | 10% | 100% ceiling |
|---|---|---|---|---|
| $10k | $5.2M | $12.9M | $25.8M | $258M |
| $25k | $12.9M | $32.2M | $64.5M | $645M |
| $50k | $25.8M | $64.5M | $129M | $1.29B |

- **Which price is plausible:**
  - **$10k** is safe: a third of base value, and in line with a $6–10k IBE done once.
  - **$25k** needs the base case to hold (close to the whole $30k base value).
  - **$50k** only works for big multi-line plants, or if downtime value is proven.
- **The PE twist:** the most defensible lever is "**don't buy it, a sister plant has it.**" The PO, the transfer and the inventory balance make it auditable. That only works with a **registry across plants**, which is our core asset.

## E. Is it worth it for a consulting firm? (VELOCITY)
- **Precedent:**
  - Kearney embeds accelerators in projects (PERLab, Spend.Pro)
  - McKinsey (Spendscape) and Bain (DealEdge, OPEXEngine) sell software alongside advisory work
  - Accenture bought engineering depth (T.A. Cook, umlaut, True North)
- **Build options:**

  | Option | Team and time | Build cost | Annual run cost |
  |---|---|---|---|
  | Pilot | 2–3 people, 3–4 months | $150–300k | $75–150k |
  | **Narrow accelerator (recommended)** | 4–6 people, 6–9 months | **$400–800k** | **$180–350k** |
  | Broad platform | 8–15 people, 12–24 months | $1.5–3M+ | $0.5–1M+ |

- **Breakeven (base):**
  - Hurdle: $600k build over 3 years + $250k a year to run = **$450k a year**.
  - Contribution per engagement: $15k fee uplift × 60% margin + 20 hours × $150 − $2k review = **$10k**.
  - So it needs **45 engagements a year**.

  | Commercial outcome | Contribution per engagement | Engagements needed per year |
  |---|---|---|
  | Photo savings only | $400–1,000 | 450–1,125 (not viable) |
  | $10k uplift | $7k | 65 |
  | $15k uplift (base) | $10k | 45 |
  | $20k uplift | $13k | 35 |

- **Follow-on (OURS):** 50 deals × 30% convert to a post-close program × 3 plants × $25k ≈ **$1.1M a year recurring**. That's more than double the hurdle, and it compounds as renewals stack.
- **Go / no-go gates:**
  - **GO** if paid pilots show **45–50 engagements a year**, a **$15k+ fee uplift**, and **~20 real hours saved** each.
  - **Keep as a toolkit or partner** if volume is 20–30.
  - **No-go on a broad platform now:** it needs ~110 engagements a year.
- **Competition:** Bain, Kearney, A&M and EFESO in operational diligence; KPMG and EY; DNV; OEMs (ABB, Siemens, Rockwell, IBM Maximo); appraisers with mobile capture apps.
- **Our wedge:** an independent, multi-brand, investment-committee-ready priority list that **stays useful after closing**.

## What to say on stage
- "Photo capture alone saves an appraiser about **$700**. We checked, and that's not our business."
- "The value is the **decision**:
  - which hidden components stop which lines
  - a 3–5-year CapEx range with evidence
  - what's on the shelf across your plants"
- "**~670 US deals a year** get an equipment or controls review today, and **25,799 US plants** have 100+ employees. Deals are the entry point; the plants are the business."
- "For a consulting firm, this pays back at **~45 engagements a year** with a $15k module, and every post-close plant program adds recurring revenue."
- "**Next step:** paid pilots that measure hours saved, findings the advisers missed, and whether the buyer pays separately."

## Weakest inputs (be ready for these questions)
- How many deals actually commission a controls review (**modeled**, 450–900).
- Willingness to pay $15k on top of existing diligence (**untested**).
- Value per plant is a **scenario**, and the cases are vendor-reported. Downtime avoided is deliberately excluded.
- Accuracy of photo identification on worn plates and crowded cabinets: we measure it on our test factory. Velocity's feasibility check is pending.
