# Velocity (Growth Signals): required

## Equipment X-Ray (current project)
Log new research here, newest first. Ideas to run:
- What value do PE firms get from combining manufacturers (shared spares, pooled buying, standardizing equipment)?
- How do plants source discontinued industrial parts (controllers, drives, HMIs), and what goes wrong (counterfeits, lead times)?
- Equipment diligence and post-deal CapEx surprises: how often do they happen, and how big are they?

### Sat Nov 14 → Sun Nov 15, night · money-thread inputs (velocity-prompts #1–6, #15–20, gaps G1–G3, backlog P2)
Each entry: **low / base / high** · source + label · → column it fills · ⚡ surprise or pushback. Labels: *measured / survey / vendor / estimate / assumption*. Chat titles are in Velocity's Research history (Buffalo).
**✅ All 18 done.** P2 #7, #8, #10, #14 were run by Brandon; the full exports are in this folder (`*_2026-11-15.md`, each with sources and a Growth Signals link).

**P2 #8 · Downtime $/h** → `valuation.py` downtime term · [Manufacturing_Downtime_Cost_Benchmarks_2026-11-15.md](Manufacturing_Downtime_Cost_Benchmarks_2026-11-15.md)
- Lost **contribution margin** per hour (*modeled*, not survey): $75–200M plant: auto **$4.5 / 9.0 / 13.5k**, food $2.5 / 5.0 / 7.5k, packaging $3 / 6 / 9k, metals and plastics $3.3 / 6.6 / 9.9k. A $25–75M plant is ~0.4× that; a $200–500M plant is ~2.5×. Low / high = 50% / 150% unrecoverable.
- Surveys are all **vendor-run**: ABB 2023 (n=3,215, global, all-in median $125k/h), Siemens 2024 (large firms; $2.3M/h auto), SimuTech (n=200 US, <$500M revenue: 52% say ≥$50k/h *engineering* downtime), L2L (n=607 US: 17 h a month unplanned per facility).
- ⚡ Our model-spec $3k/h fits a $25–75M plant. **Never use ABB or Siemens headline numbers** for a single line; use EV = avoided hours × share unrecoverable × contribution per hour.

**P2 #10 · PE spare pooling** → liquidity angle (hypothesis) · [Manufacturing_Portfolio_Procurement_Synergies_2026-11-15.md](Manufacturing_Portfolio_Procurement_Synergies_2026-11-15.md)
- Perspect Analytics, 5 sites after an M&A deal: spares inventory $84.8M → $49.2M (**~$7M per site, one-time**), purchases −$5.7M a year (~$1.1M per site) (*vendor*; its headline math is inconsistent).
- Maine Pointe, 9-business machining roll-up: $10.9M on $60M of selected spend, ~$1.2M per business (*consultant*). Plastics, 16 plants: $4.8M working capital, ~$0.3M per plant. LogicSource, 10 portcos: $50M realized, ~$5M each (*vendor*, not manufacturing-only). FourCentric, 12 portcos: £42–67M *identified* only.
- ⚡ **No case isolates value from standardizing equipment**; treat it as an enabler. Cash released from inventory is one-time, so don't multiply it by the exit multiple. Keep liquidity labeled a hypothesis.

**P2 #7 · Comparable prices** → `pricing.py` anchors · [Per_Site_MRO_Pricing_Benchmarks_2026-11-15.md](Per_Site_MRO_Pricing_Benchmarks_2026-11-15.md)
- CMMS with parts features, 10 users: **$6.6–9k per site per year** (MaintainX Premium $65, Fiix Pro $75, Limble Premium+ $69, UpKeep Premium $55 per user per month; *vendor list*). SPARETECH and Verusen publish no prices.
- Rockwell Installed Base Evaluation **$6–10k one-off** (HESCO distributor, *reported*). Rockwell SCADA support renewal $33.3k a year (one city contract, *observed*). Siemens PCS myExpert €2.2k a year. MRO consulting: $60–150k per site for inventory optimization, gain-share 15–30% (Apsentra guide, *consultant*).
- ⚡ **$10–25k per plant sits above CMMS and the IBE and below consulting**, so pitch it as "a recurring IBE plus sourcing for the price of a consulting diagnostic". One IBE at $6–10k sets the floor for a one-off scan.

**P2 #14 · Sizing by entry point** → deck market slide · [US_Manufacturing_Opportunity_Estimates_2026-11-15.md](US_Manufacturing_Opportunity_Estimates_2026-11-15.md)
- (a) Multi-plant manufacturers planning: **~8–18k companies** (*estimate*; Census 2022: 239,265 firms, ~285.5k establishments). (b) PE manufacturing portcos in hold: **~2–4k** (*estimate*; EY/AIC 2024: ~21k PE-backed companies across all sectors). (c) Acquisitions with equipment diligence: **~650–1,150 a year** (PitchBook via Travelers: 1,667 US manufacturing deals in 2024, *measured* × 40–70%). (d) Sell-side diligence: **~200–500 a year**, of which equipment-specific ~50–200 (EY 2025 exit study n=100, *survey*).
- ⚡ **Don't add these up**: (b) sits inside (a), and (c) and (d) are two sides of the same deal. Frame it as ~8–18k recurring accounts plus ~1k deal events, which matches the strategy (own plants = main way in). (c) is consistent with our ~670 figure from deep-dive-numbers.

**#20 · Sister-plant transfer** → `sourcing.py` / `pricing.py` `transfer_cost`
- **$100 / $355 / $1,260 per transfer** (*estimate*). Freight $25 / 145 / 250: FedEx 2026 list rates for a 5 lb box, Zone 4, are Ground $17.06, Standard Overnight $107.46, Priority Overnight $120.37 (*vendor list*). Admin 1 / 2 / 5 h (BLS May 2025 mean wages: clerks $22.50, EE technicians $38.79; *measured*). Bench check $30 / 120 / 770; the high case includes an outside repair from $650 (NJT Automation, *vendor*).
- Between separately owned portcos, add $40–200 per transaction for finance and procurement: arm's-length pricing (IRS §1.482-3) plus sales/use tax. Within one legal entity it's just a location transfer.
- Versus buying: Allen-Bradley 1769-L33ER PLC refurbished, landed $2,209 (DO Supply) → **the transfer saves ~$1.9–3.2k**. AB 25B-D4P0N104 drive refurbished, landed $670 (Replace Industrial) → saves only ~$0.3–0.5k.
- ⚡ Our fallback ($150–1,000 freight + $200 admin) is too high; use base $355. **Only route a transfer when the part is worth more than ~$1k.** Stored drives need capacitor reforming (Rockwell), and safety applications need revalidation.

**#19 · Approval limits** → `pricing.py` price-ceiling check
- Plant manager **$5–25k** (Summit Polymers' published signing policy: plant ops manager $10k, plant GM $25k, including software and services; *documented company policy*). VP Ops $50–150k for software (Tallyfy example $100k, *vendor example*; Summit corporate VP $150k). CFO $100–500k (Tallyfy). No measured survey medians.
- Competitive bidding at **$50k**: Armstrong (bids ≥$50k) and Stanley Black & Decker (3 quotes >$50k); both are *company policy*. A formal RFP is likely at $100–250k+ (*inference*).
- ⚡ Confirms the fallback: **$10–25k per plant per year is the quick-yes zone**, while >$50k pulls in procurement and IT/security. Watch **total contract value**: Summit counts lifetime payments, so a 3-year $10k deal counts as $30k.

**#18 · Cost to serve** → `pricing.py` margin, slide 7
- Year one with customer photos: **$2.4k / $6.7k / $18k** per plant. Initial review 25 h × $65 / 50 h × $85 / 100 h × $110 (*assumption*; BLS 2025 median for industrial engineers is $49.25/h, *measured*). On-site capture adds $1.3k / $3.4k / $8.8k. Annual upkeep $0.6k / $2k / $5.8k.
- Gross margin in year one (low / base / high cost): $10k → 76 / 33 / −80% · $25k → 90 / 73 / 28% · $50k → 95 / 87 / 64%. Later years at $10k: 94 / 80 / 42%.
- ⚡ Pushback: the API was priced on an OpenAI model, not `claude-sonnet-5-5`. It's roughly $1 a plant either way, so recompute it ourselves (option A). **Human review hours set the price floor:** $10k per plant only works if review stays near 25 hours, so Asher's real review times at CP2 decide it.
**Screenshots for the deck** (`velocity-screens/`): `xray-17-srs-escrow-debt-like.jpg` (SRS 2025 escrow medians + debt-like rule), `xray-05-planned-vs-emergency.jpg` (2.8× is mostly downtime), `xray-04-lifecycle-vs-failure.jpg` (lifecycle drives downtime, not failure odds). Raw per-prompt notes: [velocity-raw-notes-nov14.md](velocity-raw-notes-nov14.md).
**Bottom line for the model:** five fallbacks change (#1 plant baseline ↓, #3 rush ↑, #5 emergency multiplier ↓, #6 capture ↓, #15 deal rate ↑). The only slide-ready numbers with an exact report and year are Damodaran Jan 2026 (#15) and SRS Acquiom 2025 (#17). Almost everything else is Velocity's own estimate built on vendor anchors, so label it that way.

**#17 · Escrow / holdback / debt-like** → `valuation.py` (price-cut rule, holdback rule, escrow scenarios) ★ slide
- **SRS Acquiom, *2025 M&A Deal Terms Study* (2024 closings, all industries), measured:** median general indemnity escrow **10.0%** of deal value with no R&W insurance identified vs **0.35%** with R&W insurance (pp. 80, 83–84). Separate PPA escrow median **0.98%** (p. 22); present in 91% (RWI) vs 66% (no RWI) of deals with a PPA. Median survival of general reps is 12 months (p. 63).
- SRS Acquiom, *Lower Middle Market M&A Deals: What Makes Them Different?* ($5–50M deals): general escrow **12.5%**, PPA escrow **1.23%**. ❌ **Year can't be confirmed**: the article is undated and cites "2022–2023" market data and SRS's 2023 lower-middle-market report without tying the 12.5% to a closing year. The dated *2025 Special Report: Lower Middle-Market Deals* page publishes no escrow medians. **Keep 12.5% off the slides**; use the dated 2025 Deal Terms Study figures above.

**Cost to serve (API + review, computed Sun Nov 15)** → `params.COST_TO_SERVE` (the parameter is in PR #22 and isn't edited here)
- API at `claude-sonnet-5-5` list price ($2 / $10 per million tokens; *vendor list*), as `xray/extract.py` calls it: one image + ~250-token prompt + JSON schema, effort `low`, thinking billed as output. Image tokens ≈ width×height/750 after downscaling (*documented rule, not measured*; no API key here to run `count_tokens`). Low / base / high per photo: 1.85k in + 0.2k out = **$0.006** · 3.25k in + 0.5k out = **$0.012** · 2 passes × (5.05k in + 1.5k out) = **$0.05**. Per plant at 400 / 500 / 800 photos = **$2 / $6 / $40**. The Batch API halves that offline.
- Review **4 / 8 / 12 h × $75 / $112.50 / $150 = $300 / $900 / $1,800** (*assumption*, per the handoff).
- **Total ≈ $300 / $910 / $1,840 per plant**, without on-site capture. Adding 1 day of capture (~$2k) to the high case gives ~$3,840, which matches the current `P(350, 1100, 3850)`. The API is <1–2% of cost; review hours drive it.
- ABA, *2025 Private Target M&A Deal Points Study*: 139 deals (2024–Q1 2025, $25–900M), 63% referenced R&W insurance. The public summary has no escrow split, so attribute escrow figures to SRS, not ABA.
- Treatment: a known, quantified defect → price cut. Uncertain → specific indemnity plus a special escrow **sized to the exposure** (not to the 10% norm). Debt-like only if the SPA defines it. Future CapEx is not debt. R&W insurance excludes known issues (Horton Group 2026, broker).
- ⚡ **No evidence** that vendor diligence shrinks escrow or speeds the close. Keep the escrow-reduction scenarios labeled "not evidenced". Escrow duration of 12–18 months is practitioner convention, not measured.

**#15 · Discount rate** → `valuation.py` `discount_rate`
- Owner: **8 / 10 / 12%** (estimate). Anchor: **Damodaran, US cost of capital by industry, Jan 2026** (*measured*, public firms): Machinery 7.70% (105 firms), Diversified 7.30%, Electrical Equipment 8.99%.
- PE deal lens: **20 / 25 / 30%** gross deal IRR. Gompers, Kaplan & Mukharlyamov PE survey: median target 25%, mean 27% (*survey*); a later survey has median 24.8% (*survey*).
- ⚡ Our 15 / 20% deal-lens fallback is low. More important: practitioners **don't discount an identified pre-close shortfall**. It's a dollar-for-dollar price cut, seller cure or escrow (Holland & Knight; Akerman: law-firm *practitioner*). Spend in years 3–5 goes into the LBO cash flows, and the price is re-solved. → Change the rule from "price cut = PV(low)" to **undiscounted near-term backlog + PV of later items**. Don't double-count forecast and holdback.

**G1 · QoE and deferred CapEx** → `valuation.py`, pitch wording
- **Deferred CapEx inflates free cash flow, not EBITDA** (EBITDA already excludes CapEx). Deferred or wrongly capitalized *repairs* do inflate EBITDA. Avant Advisory case: −$1.683M capitalized R&M and −$545k deferred maintenance in an EBITDA bridge (*documented case*).
- Routes: a discrete overdue catch-up bill → debt-like, $-for-$ (Underridge, Anders: *practitioner*). Recurring opex shortfall → EBITDA correction × multiple. Higher ongoing maintenance CapEx → normalized FCF or a lower multiple (Mercer Capital: *provider guidance*). Growth CapEx → forecast, not backlog. Bedrock: deferred replacement is a hidden buyer cost, not an add-back.
- ⚡ Our output maps directly onto this: **backlog list → debt-like $; run-rate gap → normalized maintenance CapEx.** No measured data on how often each route is used. Fix any slide that says deferred CapEx "inflates EBITDA".

**G2 · Fixed-asset register vs the floor** → pitch (the problem), `registry`
- No defensible match rate. Kroll 2025: "studies" put ghost assets at **10–30%** of register entries, and >15% at one manufacturing client were no longer in service (*advisory claim*, not representative). Peeriosity poll: 14% of companies don't tag assets (*practitioner survey*, a share of companies, not assets).
- Which value is for what (ASA definitions): **NBV** = the books; **FMV in continued use** = appraisers and acquirers; **NOLV** = asset-based lenders' borrowing base; **RCN** = cost-approach input, insurance, CapEx planning. Purchase price allocation uses ASC 820 fair value.
- Gotham Consulting case: dry-ice maker, 150+ machines reconciled, **$2M capacity CapEx shortfall** at one plant (*consultant case*).
- ⚡ Register ≠ floor is our wedge, but "10–30% ghost assets" is an advisory-firm number. Label it.

**G3 · Spares and upgrades: CapEx vs opex** → `pricing.py` / sourcing (pooling)
- Routine spares = inventory, expensed when used (ASC 330, IAS 2). Significant reusable or insurance spares = PP&E if used over multiple periods (ASC 360; IAS 16.7–8); under IFRS, depreciation starts when available for use (PwC FAQ 4.4.4.1). Migration = CapEx if it creates or replaces an identifiable long-lived asset or betterment; troubleshooting and like-for-like = R&M. Split mixed projects. *Documented*: KPMG *Handbook: Inventory*, PwC PP&E guide, Deloitte IAS 16, EY GAAP–IFRS comparison.
- Capitalizing raises EBITDA now but FCF still takes the cash hit. The IASB declined to define EBITDA in IFRS 18.
- ⚡ **PE pooling creates no single accounting entity.** Moving spares between separately held portcos = related-party sales, with eliminations only inside a consolidated group. A part-level ownership register is needed, which is a product feature.

**#16 · Component prices + migration labor** → `kb.csv` cost columns
- Labor **$160–200/h** (Artisan Automation rate sheet: $160 programming, $180 engineering, $200 emergency; *vendor*). Hours are *estimates*.
- New / refurb / migration engineering: PLC small $150–2.5k / $0.4–2.5k / 24–80 h ($3.8–16k) · PLC large chassis $0.55–8k+ / $2–5k+ / 60–200 h ($9.6–40k) · digital I/O $100–300 / $90–200 / 4–16 h · VFD <10 HP $0.2–1.5k / $0.25–2k / 8–24 h · VFD 10–100 HP $0.65–8k / $1–6k / 16–40 h · VFD >100 HP $9–30k+ / $4–16k+ / 32–80 h · HMI small $340–3k / $0.75–2k / 12–40 h · HMI large $1.1–6.5k / $3–5k / 24–80 h · servo drive $0.5–4k+ / $1–3k+ / 24–80 h · 24 VDC PSU $70–550 / $50–250 / 2–8 h. Anchors are *vendor listings* (AutomationDirect, DO Supply, Radwell); e.g. GS4 125 HP $9,037.50, PanelView Plus 7 15" refurb $3,388.
- ⚡ The low new prices are AutomationDirect's ecosystem; Rockwell and Siemens cost far more. **Migration labor exceeds hardware**, so the KB needs separate hardware and labor columns.

**#4 · Installed components + failure probability** → `kb.annual_failure_rate`
- Per plant (*assumption*): PLC CPUs 20 / 60 / 150, drives 40 / 150 / 400, HMIs 15 / 50 / 120, other controllers 10 / 35 / 100. Annual hardware failure: PLC **0.5 / 2 / 5%**, drives and HMIs **1 / 4 / 10%**, other 0.5 / 2 / 6%.
- End-of-life or discontinued share **10 / 35 / 65%** (scenario). Siemens audits: 83% (699/843), 35% (of 3,686), 59% (of 914), 60% (of 388) (*vendor*, selected). ABB SPC700 MTBF 180,930 h ≈ 4.7%/yr at constant hazard (*vendor calc*). Aalto thesis: failures rise only slightly with age (*academic*).
- ✅ **Confirms model-spec:** lifecycle status doesn't cause failures. Age, duty, environment and maintenance drive the hazard; lifecycle and spares drive restoration time.
- ⚡ Our age-band fallback (10–20%/yr above 20 years) is higher than anything Velocity found support for. Base is 2–4% per device. Cap the high band around 10%.

**#1 · Plant baseline** → `plant_financials.csv` `maintenance_budget`, `spares_inventory_value`
- Maintenance budget: 100–249 emp **$0.35 / 1.05 / 2.1M** · 250–499 **$0.7 / 2.1 / 4.2M** · 500+ **$1.5 / 4.5 / 9.0M**. MRO purchases: $0.09 / 0.37 / 0.84M · $0.18 / 0.74 / 1.68M · $0.38 / 1.58 / 3.6M. Spares inventory: $0.04 / 0.37 / 1.12M · **$0.09 / 0.74 / 2.24M** · $0.19 / 1.58 / 4.8M.
- Built from shipments/employee $200 / 300 / 400k (*assumption*) × maintenance 1 / 2 / 3% of shipments, anchored on **NIST, *Economics of Manufacturing Machinery Maintenance*: 1.8% of shipments** (*survey*; tiny band samples of 17 / 6 / 3 plants). Turns 2 / 1 / 0.75: ScottMadden/Oniqua survey (>170 respondents), only 9% reach ≥3 turns (*survey*).
- Pushback: "2–5% of revenue" is too strong (Emerson, *vendor*). SMRP defines the RAV metric but sets no target.
- ⚡ **A base 250–499 plant has a $2.1M maintenance budget and $0.74M spares, well below our $5M / $2M registry defaults.** Lower the defaults or say we're targeting larger or more capital-intensive plants.

**#2 · Carrying cost** → `plant_financials.carrying_cost_pct`
- **12 / 18 / 30%** (*estimate*): capital 7 / 9 / 12, storage 3 / 4 / 6, insurance + tax 0.5 / 1 / 2, obsolescence + shrink 1.5 / 4 / 10. ISM: no consensus benchmark. UNITEC-D 18–25% (*vendor*), MRO Magazine 20–25% (*practitioner*).
- ⚡ 20–30% is a finished-goods rule of thumb. **The cash part is only 3.5 / 5 / 8%**, so show cash and the economic carrying cost on separate lines, and don't double-count write-offs.

**#3 · Rush / expedite premium** → `plant_financials.rush_premium_annual`
- Emergency share of POs 5 / 12 / 23%, combined premium 20 / 35 / 60%, overtime $50 / 100 / 150 per PO. On $1.5M MRO purchases: **$19k / $81k / $259k per plant per year** (*estimate*, excludes downtime).
- The whole range rests on one **iFactory six-plant beverage case** (23% of POs emergency, 34% over contract; *vendor*, unverified) and the SDI target of 1 rush order per 8–10 (*vendor*). SPARETECH 2026 survey (n=362): 12% of orders off-contract (*survey*, not an emergency measure). PMMI 2020 (n=98): no average.
- ⚡ Our $0 / 10k / 20k fallback is low, but scale it to #1: a 250–499 plant buys ~$0.74M a year → roughly **$9k / $40k / $130k**.

**#5 · Planned vs emergency** → `kb.migration_cost`, emergency multiplier
- One obsolete PLC, one line: **planned $45.6k vs emergency $126.6k = 2.8×** (*scenario*). Hardware $20k vs $26k; engineering 160 h × $135 vs +40 h × $175 (Knapp 2025 rate sheet, *vendor*); downtime 8 h × $500 vs 24 h × $3,000 (*assumption*). Sensitivity: 8 / 24 / 48 h down → 1.7× / 2.8× / 4.4×.
- Cases: Joltek $10–75k per small migration excluding downtime (*vendor*); Neuron CureWood S5 retrofit ~$10k (*vendor*); Taggart Brown 2-VFD public record $62.2k → $67.6k (1.09×).
- ⚡ **Before downtime, emergency is only ~1.3×** ($41.6k vs $54.6k). The "3×" is all downtime. Change the fallback from 1.5 / 2 / 3× to **1.1 / 1.3 / 1.6×** before downtime, with downtime hours modeled separately.

**#6 · Value-capture share** → `pricing.py` `value_capture_pct`
- Software: **10 / 15–20 / 25%** of annualized attributable value (Emergence Capital 10–30% heuristic, *investor opinion*). Gain-share services: 20–25% of verified first-year savings, 15–30% range (Pearl Lemon, *vendor*). Verusen's 3× in 12 months guarantee → **33% ceiling**; it claims a 10× average → ~10% (*vendor*). Verusen case: $20.9M identified vs $10.5M verified across 29 plants.
- Payback: LNS Research 2015 APM survey, >70% expect ≤18 months and 36% ≤12 months (*survey*, dated).
- ⚡ **There is no procurement-wide 3–5× rule.** 3–5× gross means a fee of 20–33% of savings. Our 20 / 30 / 40% is too high for software → use **10 / 20 / 30%** (40% exceeds Verusen's 33% ceiling).

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
