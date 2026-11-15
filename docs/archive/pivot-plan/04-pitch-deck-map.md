# 4 · Pitch deck map (VC framework → consulting hackathon)

[← index](index.md) · Mockup: [04-pitch-deck-mockup.html](04-pitch-deck-mockup.html) (open in a browser; ← → or click to move between slides) · Source framework: `E:\Kearney\temp\vc-pitch-deck.md`

## How we adapt the framework
The VC deck runs Problem → Solution → Proof → Customer → Competition → Business model → Market → GTM → Team → Financials → Ask. The framework's own notes for consulting judges:
- **Keep:** Problem, Solution flow, Customer/personas, Competition 2×2, Market funnel, GTM funnel, Ask.
- **Swap:** Traction → **proof** (accuracy, demo, research). Business model → **value capture**. Use of funds → **roadmap**.
- **Trim:** Financials go to the appendix. Team becomes a "why us" strip.
- **Add:** a **risk/implementation** slide and a clear **recommendation**. Consulting judges expect these.

**Reusable patterns we use:** titles that state the point, one big number per slide, groups of three, Input → Product → Output flow, a trust callout, source footnotes, hidden appendix.

## Slide by slide
| # | Framework role | Our slide title (states the point) | Content | Big number / callout | Source |
|---|---|---|---|---|---|
| 1 | Title | "Equipment X-Ray: the system of record for aging factory equipment" | Name, one-liner, cabinet photo | — | — |
| 2 | Problem | "Plants run on parts no one can see are about to fail" | 3 pains: hidden obsolete parts · surprise CapEx (in your own plants, and after an acquisition) · weeks-long outages. **Who decides:** PE operating partner + VP Ops | **83%** of automation assets discontinued/EOL in one real audit | Siemens 2025 case; ABB 2025 |
| 3 | Solution | "Photos in, a costed risk register out, with evidence behind every number" | Photos + equipment list → vision → KB match → registry → CapEx cliff / SPOFs / sourcing | Trust callout: **a person reviews low-confidence readings and big-ticket items** | — |
| 4 | Traction → **Proof** | "We measured it, we didn't assume it" | 3 tiles: accuracy on the planted-answer test factory · live photo on stage · Velocity research. Case: the Joltek $4.1M finding | [accuracy %] from `xray/evaluate.py` | Test factory; Joltek case |
| 5 | Customer | "Multi-plant manufacturers and PE portfolios" | ICP + trigger: **plant risk / CapEx planning (main)** or an acquisition / pre-exit. Personas: VP Ops / plant manager (uptime, CapEx) · operating partner (portfolio savings) · deal partner (price) | **25,799** US plants with 100+ employees; add-ons = **67.1%** of US mid-market PE deals | Census CBP 2022; PitchBook Q3 2026 |
| 6 | Competition | "Everyone values the machine. No one keeps the record." | 2×2: *one-time ↔ persistent record* × *single brand / asset value ↔ vendor-neutral component risk*. Groups: appraisers, controls diligence, OEM audits, spare-parts data, sensors. Us: top right | Coming soon: cross-portfolio spare sharing | market-validation §2 |
| 7 | Business model → **Value capture** | "Paid per plant, every year; deals and exits add one-time scans" | Per plant → portfolio license → sourcing take rate; per-deal scan as an add-on | Prices = share of modeled savings per plant (Brandon's financial model) | doc 3 |
| 8 | Market | "Deals are small. Your own plants are not." | Funnel: US MRO pool → **25,799 plants** → SAM/SOM from the financial model; deals ≈ **≤ $10M** (we say it's small) | **$13–32M ARR at 5% of plants** (placeholder until the model runs) | Census; deep-dive-numbers.md |
| 9 | GTM | "Sell to plant owners; deals and advisers are a second channel" | 3 steps: own-plant pilots at multi-plant manufacturers → registry subscription → expand across plants and the fund (advisers bring deal scans) | 3 own-plant pilots · 1 portfolio | doc 3 |
| 10 | Use of funds → **Roadmap** | "Diagnose, register, source, then network" | Phases 0–5 + flywheel | We built Phase 0 this weekend | roadmap doc |
| 11 | *Added:* Risk + implementation | "What could go wrong, and how we'd know" | OT-security overlap · KB coverage · accuracy on worn nameplates · data ownership · terms of use for sourcing sites | Each risk gets a test | doc 2 |
| 12 | Ask → **Recommendation** | "Run 3 paid pilots and 1 portfolio" | What we measure: what advisers missed, which findings changed a decision, whether the buyer paid | — | — |
| A1 | Appendix | Unit economics assumptions | Price per stage, cost per scan (vision API + review time) | — | — |
| A2 | Appendix | Sensitivity: deals-only vs. own-plant recurring | Downside = deals only ≈ ≤ $10M/yr. Base = own-plant recurring (from the financial model) | — | deep-dive-numbers.md |
| A3 | Appendix | Liquidity angle (also mention in the main deck, slides 1/7) | Sell-side readiness, freeing idle spares, targeted CapEx, verified collateral. Bain: 32,000 unsold PE companies, distributions < 15% of NAV | ⚠️ after deep research | doc 8; x-ray-research |

**Why-us strip** (bottom of slide 10 or 12): Asher + Brandon. Measured accuracy against a planted answer key. Vendor-neutral matching code reused from a previous build (97.8–100% precision/recall on held-out data).

## Before submission
- [ ] Fill in [accuracy %] once `evaluate.py` runs on the test factory.
- [ ] Screenshot the CapEx cliff + evidence drawer for slides 3/4.
- [ ] Velocity screenshot for slide 4.
- [ ] Remove or verify every ⚠️ item.
- [ ] Rebuild in the final tool (the HTML is a layout mockup).
