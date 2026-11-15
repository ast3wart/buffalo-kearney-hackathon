# Velocity (Growth Signals): required

## Equipment X-Ray (current project)
Log new research here, newest first. Ideas to run:
- What value do PE firms get from combining manufacturers (shared spares, pooled buying, standardizing equipment)?
- How do plants source discontinued industrial parts (controllers, drives, HMIs), and what goes wrong (counterfeits, lead times)?
- Equipment diligence and post-deal CapEx surprises: how often do they happen, and how big are they?

### Sat Nov 14, ~8 PM · 2 chats for Asher's thread (knowledge base + vision feasibility)
1. **Common PLC/drive/HMI families + lifecycle (KB check):** confirmed 1769-L32E discontinued Dec 16, 2020 and S7-300 PM410 Oct 1, 2025 (both in `kb.csv`). Pushback: no source gives installed-base prevalence by plant size, so the KB is an "audit shortlist, not a market-share ranking". **Plant age is a poor proxy for controls age** (lines get retrofitted), so the demo generator dates current parts on old machines as retrofits. Extra candidates: 1769-L33ER (active mature), Mitsubishi Q03UDCPU (discontinued Oct 30, 2026).
2. **Vision feasibility (narrowed rerun):**
   - No universal accuracy number exists for LLMs reading industrial labels. Building-nameplate study: 65.8% → **85.0%** character accuracy after post-processing (Park et al. 2022). Auto-parts part numbers: **94%** (Schlüter et al.). Control-cabinet detection: **> 95% mAP, > 97% OCR** on a purpose-built dataset (Scheck et al. 2026).
   - **Failure modes:** O/0, I/1/l, S/5; dropped series letters; cut-off text; reading the neighbouring label; confidently filling an illegible character.
   - **Design rules (we follow them):** a whole identifier is unverified if any character is ambiguous; never silently correct a serial or series letter; take close-ups, not one cabinet shot; route ambiguous or valuation-relevant facts to a person.
   - **USPAP:** an appraiser *may* use third-party/AI-collected data and must judge its reliability; **Advisory Opinion 41 (April 2026)** covers technology use; the appraiser keeps responsibility. **Don't claim:** touchless exact inventory from one photo, or "USPAP-compliant appraisal by AI".
   - **Our result to compare:** 12/12 exact reads on rendered test labels (incl. glare, blur, worn, cut-off), with "unclear" flagged on the cut-off label rather than guessed.

### Sat Nov 14, evening · 7 deep-dive Research chats (summary + model in [deep-dive-numbers.md](deep-dive-numbers.md), `scripts/market_model.py`)
1. **On-site M&E appraisal cost structure**: ~64 h / ~$12.8k mid-market; capture 19%, research 38%; photo ID saves only 2–5 h (~$400–1,000). Pushback: research + report dominate.
2. **US deal volume**: 1,667 US manufacturing deals (2024, measured); modeled ~385 appraisals + ~445 controls reviews → ~670 distinct deals (450–900); no published appraisal count.
3. **Own-plant market sizing**: Velocity could not complete it ("unable to complete the market estimate"); we pulled Census CBP 2022 directly: 25,799 plants with 100+ employees.
4. **Value per plant**: $10k / $30k / $60k recurring auditable + $100–400k one-time inventory release; downtime deliberately excluded; strong pushback on vendor ROI (identified ≠ verified).
5. **Consulting-firm investment**: conditional GO for a narrow expert-reviewed accelerator ($400–800k build), NO-GO for a broad platform; breakeven ~45 engagements/yr at $15k uplift; photo-only would need 450–1,125.
6. **Controls/obsolescence assessment cost structure**: ~104 person-h / ~$20k; physical inventory 31%; photo ID + lifecycle lookup saves 9/21/34 h ($1.4k/$3.4k/$5.5k); firmware not readable from labels.
7. **Feasibility + liability of photo ID** (accuracy benchmarks, lifecycle-database access, USPAP reliance): still running at time of writing.

### Sat Nov 14, afternoon · 3 Research chats for market validation (summary in [market-validation.md](market-validation.md))
1. **"Manufacturing Equipment Risk Costs"**: cost of not knowing equipment condition/obsolescence. Found: downtime is large (Siemens $1.4T / 11% revenue F500; 52% of smaller US firms ≥ $50k/h), one plant audit had 83% of automation assets discontinued or end-of-life, **no measured rate of surprise post-close CapEx**, no defensible emergency-parts premium.
2. **"Manufacturing Equipment Acquisition Diligence"**: how diligence is done and where it falls short. Found: appraisal $2–15k+, operational diligence $15–25k; specialist controls diligence (Joltek, 5–7 days) and OEM installed-base audits already exist; gap = fast, vendor-neutral, evidence-backed component + 3–5-yr CapEx that feeds advisers' reports; no published market size; sell as add-on through advisers.
3. **"Installed-Base Audits Market Opportunity"**: own-plant / PE-portfolio market. Found: US MRO ~$93B; 22% of MRO stock unused 5+ yrs; PLC lead times 10–24 wks; Section 232 machinery talks with tariffs in reserve; PE roll-up savings cases ($8.5M/yr spares, €10M/yr procurement). Verdict: recurring own-plant problem is bigger than one-off diligence.

---
## Afterlife (previous project): our earlier Velocity use, kept as a record

Workspace: https://kearney-perlab.growthsignals.com (team **Buffalo**).
Velocity has Research chat (explore a topic, compare approaches, find supporting evidence, explore patents), a **Source** library, **Concepts**, **Pipelines**, and four Guides.

**Budget: about 2 hours total.** Velocity keeps chat history, so just log each useful answer below. Screenshot the best 2–3 on Sat night for the deck.

## Prompts (claim one by putting your initial next to it)
| # | Owner | Feature | Prompt / action | Feeds |
|---|---|---|---|---|
| 1 | ✅ done Fri | Sources | Uploaded 11 files to the **Buffalo** team space (list below) | everything |
| 2 | | Research · Explore a topic | "How do manufacturers recover warranty costs from suppliers, and what prevents them?" | Problem slide |
| 3 | | Research · Find supporting evidence | "How much more do OEMs pay for spare parts than for the same parts in production?" | Savings ranges |
| 4 | | Research · Explore patents | "Methods linking warranty claims to causal parts and suppliers using BOM data" | "What's new" slide |
| 5 | | Research · Compare approaches | "Approaches to early detection of emerging field failures from warranty claims" | Judge Q&A |
| 6 | | Guide · Assess a market opportunity | Warranty and aftermarket analytics software market and who already sells it | "Why not SAP" answer |
| 7 | | Concepts + Pipeline | Add Afterlife, Teardown, and Tariff Radar as Concepts, then ask which is strongest | "How we chose" slide |
| 8 | | Guide · Make a Concept decision-ready | Run Afterlife through it Sat night | Closing slide |

## Sources uploaded (Buffalo team space, Fri Nov 13)
`00-afterlife-project-brief.md` (master context, copy in `docs/research/velocity-project-brief.md`) · `01-afterlife-concept.md` · `02-afterlife-scope-and-plan.md` · `03-afterlife-data-contract.md` · `04-research-and-design-decisions.md` · `05-data-sources-and-calibration.md` · `06-judge-questions.md` · `07-sec-warranty-payments-2024.csv` · `08-sample-warranty-claims.csv` · `09-sample-spare-part-purchases.csv` · `10-kearney-hackathon-tracks.pdf`

**Re-upload when they change:** the concept or data contract after big decisions, and the generated data (one company's CSVs) once the generators work.

## Log
### Sat Nov 14 · Research chat · supplier warranty recovery (prompt 2, with all sources attached)
- **Verdict: strong.** It read all 11 sources and ran code on `08-sample-warranty-claims.csv` (74 of 128 claims with no part number, $16,562.16; we verified both exactly).
- Verified: GM–LG Bolt deal, about $1.9B recovery vs $2.0B charges (Oct 2021). Suppliers bear ~10–15% of tracked auto warranty cost.
- **It corrected us:** 37% is a hypothetical ceiling (share of sales), not proof of fault. Afterlife produces *leads*, not findings of liability. Contract terms aren't in our data.
- ⚠️ Unverified: "APQC median supplier recovery rate 35% (604 companies)". We could only confirm APQC's metric definition, and IBM lists a 25% median. Don't put it on a slide until checked.
- **What we changed:** `recoverable_usd` → `recovery_opportunity_usd` (range, scenario), brief wording ("linked to", "request returned-part review"), a "What Afterlife does NOT do" section, the one-liner ("which supplier to take it to"), and new judge Q&A rows.
- Chat is saved in Velocity's history (Buffalo workspace). Grab a screenshot Sat night for the deck. **Deck story: we used Velocity critically, and it sharpened the claim.**

_(paste key findings + screenshot filenames here)_
