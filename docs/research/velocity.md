# Velocity (Growth Signals): required

Workspace: https://kearney-perlab.growthsignals.com (team **Buffalo**).
Velocity has Research chat (explore a topic, compare approaches, find supporting evidence, explore patents), a **Source** library, **Concepts**, **Pipelines**, and four Guides.

**Budget: about 2 hours total.** Log every useful answer below, with a screenshot in `docs/research/velocity-screens/`, so it can go on a slide.

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
- Screenshot: `velocity-screens/` (save it!). **Deck story: we used Velocity critically, and it sharpened the claim.**

_(paste key findings + screenshot filenames here)_
