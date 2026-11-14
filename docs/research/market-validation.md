# Is the problem big enough? Market validation (Sat Nov 14, afternoon)

> **Strategy decided after this doc (Sat 5 PM):** own-plant evaluation is the **main** way in; an acquisition is **one** way in; customers are multi-plant manufacturers **and** PE. Where this doc calls the acquisition "the entry point", read "one way in". Source of truth: [roadmap](../plan/roadmap-equipment-xray.md).

**Why:** a mentor pushed back on four points:
1. The market may be very small.
2. Our tool **won't replace appraisers**, so in a deal it is an **extra cost**.
3. Is this worth addressing, or is there a more addressable problem?
4. Consider evaluating your **own plants**, not just acquisitions.

**How:** three Velocity Research chats (team space Buffalo, Nov 14) plus web searches. **Labels:** *measured* = published counts, indexes or financials. *survey* = self-reported. *vendor* = a company selling a solution. *estimate* = analyst or market-research estimate.

---

## TL;DR (what we tell the judges)
1. **The pain is real and large, but nobody has measured the "cost of not knowing."** Downtime is huge, and aging automation is widespread. But no source says how much of that cost better equipment visibility would prevent, so we won't claim a headline number we can't defend.
2. **Acquisition diligence alone is a small market, and an extra cost.** The mentor is right. Specialist controls-diligence firms and OEM audits already exist. The fees are thousands to tens of thousands of dollars per deal, and nobody publishes a market size.
3. **The bigger market is recurring:** multi-plant manufacturers and **PE portfolios** keeping an **installed-base record** (every machine → every critical component → stock on the shelf → verified sourcing → a replace/repair/retrofit decision). An acquisition is **one way in**, not the business; the main way in is evaluating your own plants.
4. **The positioning answers the "extra cost" objection:** we **supplement** appraisers and operations consultants. They sign off, and our evidence-backed component and CapEx findings feed their report. A deal team pays once. A plant operator needs the record kept current, so it pays every month.

---

## 1. Current state: what does not knowing cost?
| Fact | Number | Quality |
|---|---|---|
| Unplanned downtime, world's 500 largest companies | **~$1.4T/yr, ~11% of revenue**. Automotive line **$2.3M per hour**. FMCG **$36k per hour**. | vendor estimate, extrapolated from 181 interviews ([Siemens TCOD 2024](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024_original.pdf)) |
| Smaller US manufacturers (< $500M revenue) | **52%** say downtime costs ≥ **$50k per hour**. **47%** say they lose ≥ **3% of revenue** a year. | survey of 200, vendor-run (SimuTech 2025, via Velocity) |
| How often equipment stops | **44%** have equipment-related interruptions at least **monthly**, and **14% weekly**. Most estimate **$10k–$500k per hour**. | survey of 3,600, vendor-run ([ABB 2025](https://www.worldpipelines.com/business-news/14102025/abb-industrial-downtime-costs-up-to-us500-000h-and-can-happen-every-week)) |
| No plan for aging components | Only **55%** have a proactive plan to modernize and manage out obsolete components. **58%** have no formal automation lifecycle plan. | survey (ABB 2025). Older ARC figure via [Rockwell](https://literature.rockwellautomation.com/idc/groups/literature/documents/wp/gmsa-wp002_-en-p.pdf) |
| How much automation is near end of life | **70%** of respondents say **20–60%** of their installed control systems are at or near end of useful life | older ARC survey (via Velocity/ISA) |
| One real plant audit | **699 of 843** assets from 17 manufacturers were **discontinued or end-of-life (83%)** | vendor case, one plant, not a prevalence rate (Siemens 2025, via Velocity) |
| Factory equipment age | US durable-goods equipment averaged **9.2 years** in 2022–23, the oldest since 2011 | measured, Fed/BEA data ([Silverado](https://silverado.org/publications/assessing-us-competitiveness-durable-goods-manufacturing-investment-trends/)) |
| Surprise CapEx in deals | **No study measures how often it happens or how big it is.** Cases: a PE buyer's pre-close review found a **+105% CapEx adjustment** (EFESO). A 2-day pre-LOI controls assessment found **$4.1M** near-term CapEx, including **two end-of-life control systems**, and the buyer used it in price negotiation (Joltek). | vendor cases (via Velocity) |
| Sellers defer spending | Sellers often freeze equipment spending **12–18 months before a sale**, which inflates cash flow ([Hebbia](https://www.hebbia.com/resources/private-equity-due-diligence)). Diligence practice treats deferred CapEx as a **hidden liability**, not an add-back. | practitioner guides |
| Emergency and obsolete parts | **No defensible "typical premium."** In ERAI's 2025 reports, **60%** of suspect counterfeit parts reported were **obsolete** parts. That is the mix of reports, not a counterfeit rate. | measured reports, selective (ERAI via Velocity) |

**What we can honestly say:** "Downtime costs manufacturers tens of thousands to millions per hour, and 44% get equipment interruptions every month. In a real plant audit, **83%** of the automation assets were discontinued or end-of-life, and **nearly half of manufacturers have no plan** for it. Nobody has measured how much of that cost is avoidable, so we measure it plant by plant."

## 2. Competition: where existing options fall short
Velocity's main correction: **the gap is *not* that appraisers ignore obsolescence.** An appraisal answers *what the equipment is worth*. A buyer also needs *what it costs to keep production running for the next 3–5 years*.

| Today | Cost and time | Where it falls short for us |
|---|---|---|
| **Machinery and equipment appraisal** (Hilco, Gordon Brothers, Kroll) | Desktop **$2–5k (1–2 weeks)**, on-site **$5–15k+ (3–5 weeks)** (provider benchmarks) | Values the asset. Doesn't catalog every PLC, drive or HMI, its successor, or its spares. |
| **Operational and technical diligence** (VOR, EFESO) | Focused single-site review **$15–25k + travel, ~2 weeks** (VOR) | Deep, but manual, and depth depends on access and budget |
| **Specialist controls diligence** (e.g. Joltek) | **5–7 business days**, 1–2 days on site | **The closest competitor.** It's a people service: every deal starts from scratch, and the data isn't kept afterward. |
| **OEM installed-base audits** (Rockwell Installed Base Evaluation, Siemens audit) | Field-service engagement | Run by a manufacturer, focused on its own brand, and needs physical access. Lifecycle flags aren't turned into vendor-neutral CapEx or production impact. |
| **Spare-parts data tools** (SPARETECH, Verusen) | Software | Start from **ERP/storeroom records**, and need manufacturer + article number. A storeroom list isn't a list of what's installed in each machine. |
| **Sensors** (Augury) and **maintenance software** (Maximo) | Subscription | Need months of data or clean records. A healthy vibration reading says nothing about an unsupported PLC. |

**How we're better:**
1. **Photo → verified part IDs** without a field engineer in every cabinet.
2. **Vendor-neutral** across all brands.
3. **Machine → line → revenue criticality**, so we know which failure stops which line.
4. A **bounded 3–5-year CapEx range** with evidence behind every number.
5. **Sourcing:** what's on the shelf, who sells it, the trust score, and the successor part.
6. **The record persists after the deal.** No service firm keeps it.

## 3. Is it worth it? Outcomes and market
**The mentor is right that acquisition diligence alone is small and an extra cost.**
- There's **no published market size** for equipment appraisal or operational diligence.
- One deal-flow anchor: **1,670 manufacturing companies** were listed on Axial in 2025 (one platform, listings rather than closed deals; via Velocity).
- *Illustration only:* 1,670 deals × a 20% uptake × $10k per deal ≈ **$3M a year**. That isn't a venture-scale business on its own.

**The recurring market is much bigger (own plants + PE portfolios):**
- **US MRO spend ~$93B (2025)**, of which ~45% is industrial (~$42B) ([Mordor](https://www.mordorintelligence.com/industry-reports/united-states-maintenance-repair-and-operations-mro-market/market-size), estimate; definitions vary widely). That's the spend pool, not our revenue. We target the avoidable slice: missing critical spares, rush buys, duplicate or stranded stock, and badly timed replacements.
- **22% of MRO inventory hasn't moved in 5+ years** (SPARETECH survey of 300, vendor).
- **Global industrial automation spares market ~$21.6B (2025)**, estimate.
- **PE buy-and-build:**
  - add-ons are **~76% of US buyout deal count** (PitchBook via [CapitalPad](https://capitalpad.com/private-equity-roll-up-statistics/))
  - each add-on brings its own equipment register, part names and storeroom
  - cases: 5 sites cut **spare-part spend $8.5M a year** through part consolidation (Perspect, consultant case); a portfolio procurement program saved **~€10M a year** (Efficio/Nordic Capital, adviser-reported)

**Timing (buy at the right price, get ahead of problems):**
- **Lead times:** PLCs **10–24 weeks**, drives **12–26 weeks**, robots **14–30+ weeks** (distributor estimates, Q1 2026). A failed obsolete controller with no spare means a long outage.
- **Tariffs:** on **Oct 28, 2026**, the Section 232 proclamation on robotics and industrial machinery **opened 180-day talks with tariffs held in reserve** ([EY](https://globaltaxnews.ey.com/news/2026-2306-us-concludes-section-232-investigation-into-robotics-and-industrial-machinery-imports-and-directs-trade-negotiations)). Separate steel and aluminum 232 duties already apply to machinery content.
- **Demand:** US machine-tool orders are strong, **$5.76B through Sept 2026** (AMT). The Fed held at **3.75–4.00%**.

So the decision of replace now, repair or retrofit, or stock a spare is live and expensive. A **decision record per critical asset** is the product, not "replace everything."

## 4. Recommendation
**Reposition:** *installed-base risk and replacement planning for multi-plant manufacturers and PE portfolios.*

| | Deal way in (one-time, secondary) | Core product: own plants (recurring, main) |
|---|---|---|
| Buyer | Deal team, **sold through appraisers and operations-diligence firms** as an add-on that makes them faster | Plant ops / VP Operations, PE operating partner |
| Answer to "extra cost" | Small fixed fee. The appraiser and engineer keep sign-off, and we cut their days on site. | It replaces rush buys, stranded stock and surprise outages, so it pays for itself |
| Output | Verified part IDs, end-of-life and spares flags, line criticality, 3–5-year CapEx range | Living registry + sourcing + alerts + cross-plant spare sharing |

**The demo stays the same** (photo → components → lifecycle → CapEx cliff → sourcing). The **story** shifts from "a diligence tool" to "**the system of record for aging equipment**" (own plants first; an acquisition is one way in).

**Next validation step (say this on stage):** paid pilots on live deals and plants. For each, record what the existing advisers missed, which findings changed a decision, and whether the buyer paid separately.
