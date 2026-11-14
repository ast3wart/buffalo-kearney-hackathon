# Equipment X-Ray: platform roadmap and how the system works

**Status:** UPDATED Sat Nov 14, ~4:30 PM, after the market research. Companion to [idea-equipment-xray.md](idea-equipment-xray.md). **Brandon: review and edit freely.**

> **What changed:** the research says **evaluating your own plants is the business; acquisitions are one way in.**
> - Supplementing an appraisal saves only ~$700 a job.
> - Deal diligence alone is worth about $10M a year at most.
> - **25,799 US plants** have 100+ employees, each with ~$10–60k a year of savings we can audit.
>
> Evidence: [market-validation.md](../research/market-validation.md) and [deep-dive-numbers.md](../research/deep-dive-numbers.md).

## Positioning
**Equipment X-Ray is the system of record for aging plant equipment.** It shows:
- every machine
- every critical component inside it
- what's on the shelf across your plants
- where to buy the rest
- when to replace, repair or retrofit

**Who uses it:**
- **Primary: plant owners.** VP Operations and maintenance/reliability leaders at **multi-plant manufacturers**, plus **PE operating partners** running portfolios.
- **Other ways in (not the main one):** an acquisition (a deal team, or the appraiser / operations-diligence firm working for it, runs the first scan, and after closing it becomes the acquired plant's registry) or a seller's pre-exit scan. The deal market alone is too small to rely on.

**What we don't do:** we **don't replace appraisers or engineers**. They keep the sign-off. We give them and the owner a faster, evidence-backed record and a decision.

## What the mentors told us
- Think like a **PE firm**: the value is in **bringing manufacturing companies together**.
- Have a clear **MVP plan and a ROADMAP**. Don't build everything.
- **Parts sourcing is VERY important:** a central database of every machine and part, and where to get each one.
- The **all-in-one** (diagnose → register → age, value, replacement date → source) is the value.
- **We won't replace appraisals soon, so in a deal we're an extra cost.** That's why the business is the recurring own-plant product, not the one-off diligence.

## Market (what the numbers say)
| Channel | Size | Quality |
|---|---|---|
| Appraisal time saved by photo capture | ~2–5 of ~64 h, **~$700/job**, **~$270k/yr** US-wide | Velocity model. **Not a business.** |
| Controls / obsolescence review time saved | ~21 of ~104 h, **~$3.4k/job**, **~$1.5M/yr** | Velocity model |
| New decision module in deals ($15k) | ~670 reviewed deals/yr (450–900), **~$10M/yr ceiling** | 1,667 deals/yr measured; the rest modeled |
| **Own plants (core)** | **25,799 US plants with 100+ employees**; at $10–25k/plant/yr and 5% adoption, **$13–32M ARR**; ceiling **$258–645M** | Plant count measured (Census 2022); value and price are scenarios |
| Value to each plant | **$10k / $30k / $60k a year** that can be audited (less spares carrying cost, fewer rush buys), plus **$100–400k one-time** spares released. **Downtime avoided not counted** (upside). | Velocity scenario; vendor cases |
| Upside beyond that | Downtime avoided, a sourcing take-rate on **~$93B US MRO spend**, PE portfolio licenses, smaller plants, international | Not yet sized |

## Freeing up cash (liquidity): a core value, still a hypothesis ⚠️
PE is in a low-liquidity period: exits are slow and LPs want cash back. Manufacturers want cash out of working capital. The registry frees up cash in four ways (from Brandon's [pivot-plan/03](pivot-plan/03-flywheel-growth.md); sizing in [pivot-plan/08](pivot-plan/08-deep-research-prompt.md)):
1. **Faster, cleaner exits:** a verified equipment record with an evidence trail cuts the buyer's diligence time and the "unknown CapEx" discount on price. **A seller scan before a sale is another way in.**
2. **Cash tied up in idle spares:** 22% of MRO stock hasn't moved in 5+ years. A cross-plant view moves or sells surplus spares and avoids duplicate buys (the $100–400k one-time release per plant).
3. **Targeted CapEx instead of blanket replacement:** replace / repair / stock-a-spare per asset, so cash goes only where the risk is.
4. **Verified collateral (stretch):** a current, evidence-backed equipment register could support asset-based or NAV lending.

**Doors in, in order:**
1. own-plant evaluation (main)
2. portfolio-wide rollout for PE
3. a seller scan before an exit
4. a buyer scan at an acquisition

Liquidity sells all four. **Status:** hypothesis until the doc 08 research backs it with numbers.

## The platform in one picture
```
 CAPTURE                 UNDERSTAND                    REGISTRY (the core asset)             ACT
 ───────                 ──────────                    ─────────────────────────             ───
 photos of nameplates ─┐                               Company / PE portfolio                • replace / repair / retrofit plan per plant
 + control cabinets    ├─► vision AI reads ──► match ─► └─ Plant                             • CapEx cliff by year (ranges + evidence)
 equipment lists       │   make/model/serial,  to KB     └─ Line ($/day, downtime $/h)       • SOURCING: shelf first (any plant), then
 maintenance / ERP     │   components inside             └─ Machine                            OEM, distributors, refurbishers, surplus,
 storeroom records     │   + confidence                    └─ Component (part no., age,         eBay; price, lead time, trust score
 (later) sensors      ─┘                                      lifecycle, spares, successor)    • alerts: part going end-of-life, spare found
                                ▲                                         │                    • DEALS: "pay $X less", holdback, 100-day plan
                                └──── human review of low-confidence ─────┘
```

## How the system works (components)
| # | Component | What it does | Notes |
|---|---|---|---|
| 1 | **Capture** | Guided photos of nameplates and cabinets, plus equipment lists and storeroom/ERP exports; quality check | Web upload first; a field tool for plant walks later |
| 2 | **Vision extraction** | Off-the-shelf Claude reads the fields and lists the components, each with a confidence | No training at first. It can't read firmware from a label; that needs other sources. |
| 3 | **Normalization + matching** | Cleans manufacturer/model names and catalog numbers, then matches them to the knowledge base | `xray/matching.py` |
| 4 | **Knowledge base** | Per product: lifecycle status, typical life, replacement and migration cost, successor, spares availability | **The moat.** Grows with every plant. |
| 5 | **Machine registry** | Company → Plant → Line → Machine → Component, with evidence | **The core asset.** Data format: [registry-format.md](../build/registry-format.md). |
| 6 | **Valuation + risk** | CapEx cliff by year, single points of failure per line, exposure in $, deal adjustment | Ranges, never false precision |
| 7 | **Sourcing** | Checks shelves at **every plant first**, then outside channels by trust; recommends buy a spare / migrate / monitor | See below |
| 8 | **Portfolio layer** | One view across plants and companies: shared spares, pooled buying, standard parts, benchmarks | The "bring manufacturers together" value |
| 9 | **Human review** | Flags low-confidence readings, big-ticket items, counterfeit risk | Engineer and appraiser keep the sign-off |

## Sourcing (the feature the mentor called out)
1. **Shelf first:** is a usable spare already sitting at **this plant or a sister plant**? This is the most defensible saving. The purchase order, the transfer and the inventory balance make it auditable.
2. **Status:** is the part active or discontinued? If discontinued, what's the successor and the migration path?
3. **Outside channels, by trust:**
   - manufacturer and authorized distributors
   - refurbishers and repair houses
   - surplus dealers
   - marketplaces like eBay
4. **Compare** price, lead time, condition, warranty and a **seller trust score**.
5. **Recommend:** *buy a spare now*, *migrate*, or *monitor*.
6. **Watch:** alerts when a scarce part appears or a price moves.

**Rules:**
- Use official APIs and partner feeds, and respect each site's terms of use.
- Always show counterfeit risk. In ERAI's 2025 reports, 60% of suspect counterfeit parts were obsolete parts.
- A person approves every purchase.

## Roadmap
| Phase | What | Who pays / how | Proof point |
|---|---|---|---|
| **0 · MVP (hackathon)** | AI diagnostic: photos + list → components → lifecycle → **CapEx cliff, single points of failure, sourcing**, measured on a fake factory with planted answers | Demo | Accuracy number; live photo of a real machine |
| **1 · Plant assessment** | Field capture + report for **your own plant**. The same product sold as a **deal module** through appraisers and operations-diligence firms. | **Per-plant assessment fee** (anchor: today's controls reviews cost $6–30k); deal-module price from the financial model | Hours saved against a real assessor; findings people act on |
| **2 · Living registry** | Every assessed plant stays current: lifecycle alerts, spares, a replacement plan | **Subscription per plant** (price = share of modeled savings per plant) | Fewer rush buys, less spares stock, fewer surprise outages (audited) |
| **3 · Sourcing** | Shelf-first across plants, outside offers, successor advice, scarcity alerts | Same subscribers; later a **take rate** through partners | Purchases avoided because a sister plant had the part; faster sourcing |
| **4 · Portfolio network** | Across a company's plants and a PE firm's companies: pooled spares, shared buying, standard parts | **Portfolio license** (one sale, 10–30 companies) | Spares shared between companies; group purchasing savings |
| **5 · Predictive** | Sensors and failure history → our own models for remaining life and failure risk | Premium tier; partners | Downtime avoided, measured. This is when downtime becomes a counted number. |

**Flywheel:** every plant scanned (own or acquired) → more labeled photos and components → better knowledge base → better sourcing and risk calls → more plants → more data.

**For a consulting firm (e.g. Kearney):**
- Build it as a narrow, expert-reviewed **assessment accelerator** ($400–800k).
- It breaks even at **~45 engagements a year** with a $15k module, and post-close plant programs add recurring revenue.
- **No broad platform yet** (that needs ~110 engagements a year).

## What we show at the hackathon
1. **The MVP working** on the fake factory with an answer key, plus one live photo.
2. **The registry view:** every machine → every component, with age, status, evidence.
3. **CapEx cliff + single points of failure**, plus the deal view ("pay $X less") as a second lens on the same data.
4. **Sourcing for 2–3 parts:** shelf-first, then outside offers with a trust score and buy / migrate / monitor.
5. **Market + business model:** $13–32M ARR at 5% of US plants (our floor), with upside from downtime, sourcing and PE portfolios; the consulting-firm breakeven.
6. **This roadmap**, with the flywheel and the PE portfolio vision.

## Risks and open questions
- **Price** comes from Brandon's financial model (share of cost saved per plant), not a chosen number. Willingness to pay is still untested. Next step: paid pilots.
- **Value is a scenario** from vendor cases, and downtime isn't counted yet. Prove it in pilots.
- **Incumbents:** Rockwell/Siemens/ABB installed-base services, SPARETECH/Verusen, CMMS tools. Our edge is multi-brand, from the photo and the panel (not only the ERP), and cross-plant.
- **Accuracy on worn plates and crowded cabinets:** measure it; firmware isn't readable from labels.
- **Sourcing data access** and terms of use; counterfeit risk.
- **Who owns the data** in a PE portfolio (each company or the fund).
