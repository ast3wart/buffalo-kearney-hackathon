# Equipment X-Ray: platform roadmap and how the system works

**Status:** DRAFT (Sat Nov 14, ~12:30 PM), written after a mentor conversation. Companion to [idea-equipment-xray.md](idea-equipment-xray.md). **Brandon: review and edit freely.**

## What the mentor told us
- **Think like a private equity firm:** the value is in **bringing manufacturing companies together** (a PE firm owns several), not in a one-off tool.
- **Have a clear plan for the MVP (the AI diagnostic tool) and how the whole system works. Show a ROADMAP, don't try to build everything.**
- **Sourcing parts is a VERY important part:** a central database of every machine and every part inside it, and for each part, where to get it (manufacturer, distributors, refurbishers, eBay, other reputable sites).
- **The all-in-one is what makes it valuable to companies:** diagnose → register → know every part's age, value and replacement date → source it.

## The platform in one picture
```
 CAPTURE                 UNDERSTAND                    REGISTRY (the core asset)             ACT
 ───────                 ──────────                    ─────────────────────────             ───
 photos of nameplates ─┐                               Company                               • CapEx cliff + deal price (diligence)
 + control cabinets    ├─► vision AI reads ──► match ─► └─ Plant                             • replacement plan per plant
 equipment lists       │   make/model/serial,  to KB     └─ Line                             • SOURCING: where to buy each part
 maintenance logs      │   components inside             └─ Machine                            (OEM, distributors, refurbishers,
 (later) sensors      ─┘   + confidence                    └─ Component (part no., age,         surplus, eBay), price, lead time,
                                                              value, lifecycle, remaining life)   condition, seller trust
                                ▲                                         │                    • PORTFOLIO (PE): pooled spares,
                                └──── human review of low-confidence ─────┘                      shared buying, standardization
```

## How the system works (components)
| # | Component | What it does | Notes |
|---|---|---|---|
| 1 | **Capture** | Guided collection of nameplate + cabinet photos and the target's equipment list; quality check (blur, glare, cut-off) | Starts as a web upload; later a field tool for site walks |
| 2 | **Vision extraction** | Off-the-shelf vision AI (Claude) reads fields + lists components, each with confidence | No training at first (see idea doc §8) |
| 3 | **Normalization + matching** | Cleans manufacturer/model names and catalog numbers; matches to known products | Reuses our existing matching approach |
| 4 | **Knowledge base (KB)** | Per product: lifecycle status (active / discontinued), typical lifespan, replacement cost, successor/migration path, spare availability | **The moat.** Seeded from manufacturer lifecycle tools + curated research; grows with every scan |
| 5 | **Machine registry** | The central database: Company → Plant → Line → Machine → Component, with age, value, remaining life, evidence | **The core asset** the mentor described |
| 6 | **Risk + valuation engine** | Remaining useful life, single points of failure per line, CapEx cliff by year, value ranges | Ranges + evidence, never fake precision |
| 7 | **Sourcing engine** | For each part: search reputable channels, compare price / lead time / condition / seller trust, suggest successors when discontinued | See "Sourcing" below |
| 8 | **Portfolio layer (PE)** | One view across many companies: shared spares, pooled buying, standardizing on common machines/parts, benchmarks | The "bring manufacturers together" value |
| 9 | **Human review** | Flags low-confidence readings, big-ticket items, counterfeit risk | Required before anything drives a deal or purchase |

### Data model (registry)
| Entity | Key fields |
|---|---|
| **Company** | name, owner (e.g. PE fund), acquisition date |
| **Plant** | location, lines, production value per day |
| **Line** | product, revenue per day of production (for downtime cost) |
| **Machine** | make, model, serial, year, photos, condition, value range, remaining life |
| **Component** | part no., manufacturer, type (controller, drive, HMI, motor…), install/date code, lifecycle status, replacement cost, successor, spares on hand |
| **Sourcing offer** | part no., channel, seller, price, condition (new / refurbished / used), lead time, seller trust score, link, seen-at |
| **Evidence** | photo, reading, source document, confidence, reviewer |

## Sourcing (the feature the mentor called out)
For every component in the registry:
1. **Status first:** active, or discontinued? If discontinued, what's the official successor and migration path?
2. **Search channels**, in order of trust:
   - the manufacturer and its **authorized distributors** (new, warrantied)
   - **specialist refurbishers / repair houses** (tested, often warrantied)
   - **industrial surplus dealers**
   - **marketplaces like eBay** (cheapest, highest counterfeit and condition risk)
3. **Compare** price, lead time, condition, warranty, and a **seller trust score** (history, returns, certifications).
4. **Recommend** per part: *buy a spare now* (single point of failure + scarce), *migrate to successor* (discontinued + spares drying up), or *monitor* (active, plentiful).
5. **Watch:** alert when a scarce part appears in stock somewhere, or when the price moves.

**Design rules:** use official APIs and partner feeds where they exist, and respect each site's terms of use (no unlicensed scraping); always show **counterfeit risk** for non-authorized sellers; a person approves purchases.

**Portfolio twist (PE):** before buying outside, check whether **another company in the same portfolio already has the spare** sitting on a shelf.

## Roadmap
| Phase | What | Who pays / why | Proof point |
|---|---|---|---|
| **0 · MVP (hackathon)** | **AI diagnostic tool**: photos + equipment list → machines and components identified → lifecycle check → **CapEx cliff, "pay $X less", single points of failure**, with evidence and measured accuracy on a planted-answer test factory | Demo for judges | Live photo of a real machine on stage; accuracy number |
| **1 · Diligence product** | Field capture for site walks; bigger KB; reports for investment memos | PE deal teams, corporate M&A: **fee per diligence** | Used on real deals; findings change prices |
| **2 · Machine registry** | Every scanned plant becomes a living registry: every machine, every part, age, value, replacement dates | Owners after the deal: **subscription per plant** | Replacement plans; avoided downtime |
| **3 · Sourcing engine** | Where to buy every part; successor/migration advice; scarcity alerts | Same subscribers; possibly **take rate** on purchases through partners | Faster sourcing of discontinued parts; avoided outages |
| **4 · Portfolio network** | Across a PE firm's companies: pooled spares, shared buying, standardizing machines and parts, benchmarks | **PE firms (portfolio-wide license)** | Spares shared between companies; group purchasing savings |
| **5 · Predictive + new revenue** | Clip-on sensors for condition; failure history → our own trained detector and failure models; possibly financing/insurance partners | Premium tier; partners | Fewer surprise failures; better lifespan models than anyone |

**Flywheel:** every diligence → more labeled photos and components → better KB → better sourcing and predictions → more customers → more data.

## What we show at the hackathon
1. **The MVP working** (Phase 0), on a synthetic target factory with an answer key, plus one live photo of a real machine.
2. **The registry view** for that factory: every machine → every component, age, value, replacement date (a working slice).
3. **Sourcing for 2–3 components** in the demo: clearly labeled as a prototype (curated or live-searched offers), with the trust score and the buy / migrate / monitor recommendation.
4. **This roadmap** as a slide, with the flywheel and the PE portfolio vision.
5. **Business model** by phase (per diligence → per plant → portfolio license).

## Risks and open questions
- **Sourcing data access:** which channels have APIs or partner feeds; terms-of-use limits on searching sites.
- **Counterfeit and condition risk** on used marketplaces: how we score trust credibly.
- **KB coverage:** how fast we can cover the long tail of old machines.
- **Accuracy on worn nameplates:** measure, don't assume.
- **Who owns the data** in a PE portfolio (each company vs. the fund).
- **Track:** confirm the Startup track switch with organizers.

## Questions for Brandon
1. Does this match what you'd want to pitch? Anything to cut?
2. Which phase-0 pieces do you want to own?
3. Sourcing demo: curated offers (safe) vs. a live search (riskier, more wow)?
