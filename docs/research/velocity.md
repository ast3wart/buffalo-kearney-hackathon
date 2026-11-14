# Velocity (Growth Signals): required

Workspace: https://kearney-perlab.growthsignals.com (team **Buffalo**).
Velocity has Research chat (explore a topic, compare approaches, find supporting evidence, explore patents), a **Source** library, **Concepts**, **Pipelines**, and four Guides.

**Budget: about 2 hours total.** Velocity keeps chat history, so just log each useful answer below. Screenshot the best 2–3 on Sat night for the deck.

## Prompts (claim one by putting your initial next to it)
| # | Owner | Feature | Prompt / action | Feeds |
|---|---|---|---|---|
| 1 | ✅ done Fri | Sources | Uploaded 11 files to the **Buffalo** team space (list below) | everything |
| 2 | | Research · Explore a topic | "How do manufacturers recover warranty costs from suppliers, and what prevents them?" | Problem slide |
| 3 | ✅ Asher (Sat 10:05) | Research · Find supporting evidence | "How much more do OEMs pay for spare parts than for the same parts in production?" | Savings ranges |
| 4 | | Research · Explore patents | "Methods linking warranty claims to causal parts and suppliers using BOM data" | "What's new" slide |
| 5 | | Research · Compare approaches | "Approaches to early detection of emerging field failures from warranty claims" | Judge Q&A |
| 6 | | Guide · Assess a market opportunity | Warranty and aftermarket analytics software market and who already sells it | "Why not SAP" answer |
| 7 | | Concepts + Pipeline | Add Afterlife, Teardown, and Tariff Radar as Concepts, then ask which is strongest | "How we chose" slide |
| 8 | | Guide · Make a Concept decision-ready | Run Afterlife through it Sat night | Closing slide |

## Sources uploaded (Buffalo team space, Fri Nov 13)
`00-afterlife-project-brief.md` (master context, copy in `docs/research/velocity-project-brief.md`) · `01-afterlife-concept.md` · `02-afterlife-scope-and-plan.md` · `03-afterlife-data-contract.md` · `04-research-and-design-decisions.md` · `05-data-sources-and-calibration.md` · `06-judge-questions.md` · `07-sec-warranty-payments-2024.csv` · `08-sample-warranty-claims.csv` · `09-sample-spare-part-purchases.csv` · `10-kearney-hackathon-tracks.pdf`

**Re-upload when they change:** the concept or data contract after big decisions, and the generated data (one company's CSVs) once the generators work.

## Log
### Sat Nov 14, 10:05 · Find supporting evidence · spare-part price gap + price harmonization (prompt 3, brief attached)
Chat title in Velocity: **"Spare Parts Pricing Evidence"** (Buffalo, Research history).
- **Verdict: it challenged us, and it was right.** No credible study supports **1.5–5×** as a *typical* production-vs-spare price gap for identical parts. Treat our range as a **synthetic stress-test scenario**, not a benchmark. Same for the $2–6M "overspend": it's a review opportunity whose value depends on contract terms, order size, packaging, freight and urgency.
- **Evidence it found (we fact-checked ✅):**
  - ✅ **GAO NSIAD-96-48 (1996):** 33 C-17 spare parts cost **4–56×** more after the contractor moved them from outside vendors to in-house production. GAO says this **can't be projected** to all spares. It's an outlier that shows the risk, not a typical number. https://www.gao.gov/products/NSIAD-96-48
  - ✅ **DRÄXLMAIER purchasing terms:** spare parts at the **last series price for 5 years after end of production** (plus agreed special packaging). POLYTEC's framework contract has a similar 15-year clause (not checked by us). So **1× is contractually normal**, which means any markup is a contract-compliance question. https://www.draexlmaier.com/fileadmin/Supplier/Dokumente/Zusammenarbeit/Vertragsdokumente/Purchase_en/R3/GTC_Annex_3_Spare_Parts_Requirements_R3_eng_180501.pdf
  - ⚠️ Not verified: **15–20% price variance** for identical parts across regions (YCP case study), a **29% spread** across plants and 5.25% MRO savings (MavenVista case), and **1–4% of spend** typical harmonization savings (Tungsten Network, a vendor claim). Quote these only as "case/vendor-reported".
- **Why a real gap exists (useful for the pitch):** different contracts and channels (service buys off-contract), fragmented item records (an OEM on 11 ERPs couldn't see identical parts at different prices, which supports our acquired-plant story), and real service costs (small batches, special packaging, end-of-production supply).
- **What this should change** (proposed, see Asher's notes): (1) label markups and overspend in the app as scenario estimates; (2) make the generator more realistic: most spares bought under contract near 1×, a minority off-contract at 1.5–4×; (3) it strongly supports the **price-schedule / "spares at production price" clause** proposal, because the brief can cite the supplier's own clause.

### Sat Nov 14 · Research chat · supplier warranty recovery (prompt 2, with all sources attached)
- **Verdict: strong.** It read all 11 sources and ran code on `08-sample-warranty-claims.csv` (74 of 128 claims with no part number, $16,562.16; we verified both exactly).
- Verified: GM–LG Bolt deal, about $1.9B recovery vs $2.0B charges (Oct 2021). Suppliers bear ~10–15% of tracked auto warranty cost.
- **It corrected us:** 37% is a hypothetical ceiling (share of sales), not proof of fault. Afterlife produces *leads*, not findings of liability. Contract terms aren't in our data.
- ⚠️ Unverified: "APQC median supplier recovery rate 35% (604 companies)". We could only confirm APQC's metric definition, and IBM lists a 25% median. Don't put it on a slide until checked.
- **What we changed:** `recoverable_usd` → `recovery_opportunity_usd` (range, scenario), brief wording ("linked to", "request returned-part review"), a "What Afterlife does NOT do" section, the one-liner ("which supplier to take it to"), and new judge Q&A rows.
- Chat is saved in Velocity's history (Buffalo workspace). Grab a screenshot Sat night for the deck. **Deck story: we used Velocity critically, and it sharpened the claim.**

_(paste key findings + screenshot filenames here)_
