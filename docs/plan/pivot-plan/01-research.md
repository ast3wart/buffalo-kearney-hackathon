# 1 · Research behind the machinery pivot

[← index](index.md) · Full sources: [market-validation.md](../../research/market-validation.md) · Velocity log: [velocity.md](../../research/velocity.md)

## Why we pivoted
- **Kearney judge (on Afterlife):** our scope was too wide, half the room is building "make consulting more efficient", nobody is in the Startup track, and the biggest gaps are in **old companies that grew by buying smaller ones**.
- **What landed with the judge:** reading documents, and testing against a **planted answer key**. We keep both.
- **Mentor 1:** think like a PE firm. Show a platform roadmap: diagnose → registry → **sourcing** → portfolio. Don't try to build everything.
- **Mentor 2:** the market may be small, the tool **won't replace appraisers** (so it's an extra cost), and we should consider **companies' own plants**, not just acquisitions.

## What the research found
| Question | Finding | How solid |
|---|---|---|
| Is the pain real? | Downtime costs **$10k–$500k/hr** in most plants (ABB, n=3,600). **44%** of plants have equipment interruptions monthly, 14% weekly. **52%** of smaller US manufacturers say downtime costs ≥ $50k/hr. | Vendor-run surveys. The direction is strong. |
| Is the risk hidden? | In one Siemens plant audit, **699 of 843 automation assets (83%)** were discontinued or end-of-life. Only **55%** of plants have a plan for obsolete parts. US durable-goods equipment averages **9.2 yrs**, the oldest since 2011. | One case (not a prevalence rate) + Fed/BEA data |
| Do surprise costs show up in deals? | Cases: **+105% CapEx adjustment** found before close (EFESO). A 2-day controls check found **$4.1M** of near-term CapEx and was used to negotiate the price (Joltek). Sellers often **freeze CapEx 12–18 months before a sale**. | Vendor cases. **No study measures how often this happens.** |
| Is diligence alone a business? | **No.** ~1,670 manufacturing listings on Axial × 20% uptake × $10k ≈ **$3M/yr**. Appraisers ($2–15k), ops diligence ($15–25k) and specialist controls diligence already exist. | Mentor 2 was right |
| Where is the bigger market? | **Recurring:** US MRO spend ~**$93B** (~$42B industrial). **22%** of MRO stock hasn't moved in 5+ yrs. Add-ons are **~76%** of US buyout deals. Roll-up cases: **$8.5M/yr** spare-parts savings (5 sites), **~€10M/yr** procurement savings. | Market estimates + consultant cases |
| Why now? | Lead times: PLCs **10–24 wks**, drives **12–26 wks**, robots **14–30+ wks**. The Section 232 machinery proclamation (Oct 28, 2026) **opened talks with tariffs held in reserve**. Machine-tool orders are strong ($5.76B through Sept 2026). | Distributor data, EY, AMT |

## What we can and can't claim
- ✅ "Downtime costs tens of thousands to millions per hour. 44% of plants get equipment interruptions every month. In a real audit, 83% of automation assets were discontinued or end-of-life, and nearly half of manufacturers have no plan for it."
- ❌ Any headline "cost of not knowing" number. **No one has measured it. We measure it plant by plant.**
- ❌ A "typical emergency-parts premium". None we could defend.

## Where competitors fall short (short version)
An appraisal answers *what the equipment is worth*. A buyer also needs to know *what it costs to keep production running for the next 3–5 years*.
| Option | Gap |
|---|---|
| Appraisers (Hilco, Gordon Brothers, Kroll) | Value the asset. Don't list every PLC, drive and HMI, or its successor part |
| Ops diligence (VOR, EFESO) | Deep, but manual. Depends on access and budget |
| Specialist controls diligence (Joltek) | **Closest competitor.** A people service that starts from scratch each deal and doesn't keep the data |
| OEM audits (Rockwell, Siemens) | Cover their own brand only, and need access to the plant |
| Spare-parts data (SPARETECH, Verusen) | Start from storeroom records, not what's installed in each machine |
| Sensors (Augury), maintenance software (Maximo) | Need months of data or clean records |

## The pivot decision
**Before:** "an AI diligence tool for acquisitions."
**After:** "**installed-base risk and replacement planning for multi-plant manufacturers and PE portfolios**. Diligence is the entry point." The demo flow stays the same: photo → components → lifecycle → CapEx cliff → sourcing.
