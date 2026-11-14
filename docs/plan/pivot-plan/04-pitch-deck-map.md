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
| 2 | Problem | "Buyers pay for capacity they can't see is about to fail" | 3 pains: hidden obsolete parts · surprise CapEx after close · weeks-long outages. **Who decides:** PE operating partner + VP Ops | **83%** of automation assets discontinued/EOL in one real audit | Siemens 2025 case; ABB 2025 |
| 3 | Solution | "Photos in, a costed risk register out, with evidence behind every number" | Photos + equipment list → vision → KB match → registry → CapEx cliff / SPOFs / sourcing | Trust callout: **a person reviews low-confidence readings and big-ticket items** | — |
| 4 | Traction → **Proof** | "We measured it, we didn't assume it" | 3 tiles: accuracy on the planted-answer test factory · live photo on stage · Velocity research. Case: the Joltek $4.1M finding | [accuracy %] from `xray/evaluate.py` | Test factory; Joltek case |
| 5 | Customer | "Multi-plant manufacturers and PE portfolios, starting at the acquisition" | ICP + trigger (an acquisition or add-on). Personas: deal partner (price) · operating partner (portfolio savings) · plant manager (uptime) | Add-ons = **~76%** of buyout deals | PitchBook |
| 6 | Competition | "Everyone values the machine. No one keeps the record." | 2×2: *one-time ↔ persistent record* × *single brand / asset value ↔ vendor-neutral component risk*. Groups: appraisers, controls diligence, OEM audits, spare-parts data, sensors. Us: top right | Coming soon: cross-portfolio spare sharing | market-validation §2 |
| 7 | Business model → **Value capture** | "Paid once at the deal, every month after" | Per deal → per plant → portfolio license → sourcing take rate | ⚠️ Price points are hypotheses | doc 3 |
| 8 | Market | "Diligence is small. The installed base is not." | Funnel: diligence wedge ≈ **$3M** (we say it's small) → recurring pool → SAM → SOM | US MRO **~$93B**; automation spares **~$21.6B** | Mordor; market-validation §3 |
| 9 | GTM | "Sell through the advisers, then convert after close" | 3 steps: channel via appraisers → convert to registry → expand across the fund. Year-1 targets | 3 pilots · 1 portfolio | doc 3 |
| 10 | Use of funds → **Roadmap** | "Diagnose, register, source, then network" | Phases 0–5 + flywheel | We built Phase 0 this weekend | roadmap doc |
| 11 | *Added:* Risk + implementation | "What could go wrong, and how we'd know" | OT-security overlap · KB coverage · accuracy on worn nameplates · data ownership · terms of use for sourcing sites | Each risk gets a test | doc 2 |
| 12 | Ask → **Recommendation** | "Run 3 paid pilots and 1 portfolio" | What we measure: what advisers missed, which findings changed a decision, whether the buyer paid | — | — |
| A1 | Appendix | Unit economics assumptions | Price per stage, cost per scan (vision API + review time) | — | — |
| A2 | Appendix | Sensitivity: diligence-only vs. recurring | Downside = diligence-only ≈ $3M/yr. Base = recurring | — | — |
| A3 | Appendix | Liquidity angle | Sell-side readiness, freeing idle spares, targeted CapEx | ⚠️ after deep research | doc 8 |

**Why-us strip** (bottom of slide 10 or 12): Asher + Brandon. Measured accuracy against a planted answer key. Vendor-neutral matching code reused from a previous build (97.8–100% precision/recall on held-out data).

## Before submission
- [ ] Fill in [accuracy %] once `evaluate.py` runs on the test factory.
- [ ] Screenshot the CapEx cliff + evidence drawer for slides 3/4.
- [ ] Velocity screenshot for slide 4.
- [ ] Remove or verify every ⚠️ item.
- [ ] Rebuild in the final tool (the HTML is a layout mockup).
