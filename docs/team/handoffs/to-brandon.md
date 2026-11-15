# Inbox: to Brandon

**Written by Asher, read by Brandon.** Newest on top. Brandon: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, ~9:15 PM · Asher's answers to your 5 questions (all agreed) + what's done
**Status:** 🆕 new · branch `asher/speed` (merges your money-model follow-ups + #23)
1. **Contract additions: accepted.** Your extra columns and optional arguments are documented in `interfaces.md` §1 ("Accepted additions") and `registry-format.md` §7.
2. **Price on screen = full-plant quote** (`full_plant=True`), labeled "extrapolated". The sample-only number is in a drill-down ("Evidence: only the parts scanned so far"). Toledo: ~$10k/yr (range $1.8–35k).
3. **Targets lowered to your model's output** (`interfaces.md` §2), and "20+ weeks" is out of the demo script. **Bigger numbers come from filling `kb.migration_cost_*` per controller family from research, not from inflating Tillman.**
4. **Velocity #1–3 plant finances are in** (`make_demo_data.py`). 100–249 employee band: maintenance $1.05M, spares $0.37M, rush ~$20k base, scaled by headcount ÷ 170; carrying 12–30%. Only `plant_financials.csv` changed, so components and photos still line up.
5. **Rare "no listings" part: please spend 5 min on eBay (sold + active) for these candidates, then tell me which has 0–2 listings.** I'll add it to the KB with its lifecycle source and put it in a Tillman machine:
   - Westinghouse Numa-Logic PC-1100 CPU
   - Square D SY/MAX Model 400 processor (8020 SCP-4xx)
   - Texas Instruments 5TI-1000 / TI 520 CPU
   - Reliance Electric AutoMax DCS 5000 processor (57C4xx)

- **Merged in my branch:** your money-model follow-ups (cost to serve, on-site capture add-on, full-plant quote, sensitivity grid, market model) and #23. All tests pass (33). **Steps 2 and 3: go.**
- **Deck slide A4 doesn't exist in `04-pitch-deck-mockup.html` yet**, so there's nothing to render. Tell me when it's in and I'll render it.
- **Run the app fast:** `./scripts/demo.sh` (production build; pages load in ~10–40 ms).

### Sat Nov 14, ~8:30 PM · Reviewed + merged your #21 and #22; it's live in the app. One thing to tune: the CapEx scale
**Status:** 🆕 new
- **Review:** clean. Pure functions, every assumption in `params.py` with a range and source, your tests pass, and all 7 functions run on the full 6-plant demo in < 0.5 s. Signatures match the API. Merged both to `main`. Your 42 real listings now replace the sample ones per part.
- **Live in the app:** CapEx cliff per plant, line-stopper exposure ($/yr), savings + price per plant (Toledo: $22.9k/yr auditable → $6.9k price, 3.6-month payback), the deal view on Tillman, and a per-part financial view (exposure + your sourcing call + part value from real listings).
- **To tune (your call, money thread):** CapEx and the deal view are **small**: Toledo $70–350k over 5 yrs; **Tillman price cut ≈ $61k on a $28–34M deal**, which won't impress on stage. Cause: CapEx counts control-part hardware + migration hours only; `kb.migration_cost_*` is blank, so it falls back to 40–80 h × $150–300. Real controls migrations usually include panel rework, I/O re-wiring, testing and commissioning, and often run $20k–$100k+ per PLC platform (verify with Velocity #16 before using). Options:
  1. fill `migration_cost_low/high` per KB family from research
  2. add **whole-machine end-of-life** (machines have `replacement_value_low/high` + `year_built`) as a CapEx line
  3. show downtime exposure next to the deal number

  Pick whichever you can defend.
- **Small one:** for_repair listings now sort last in the app's options list (a $112 broken unit was ranking 2nd).

### Sat Nov 14, ~10 PM · Part health + marketplace in the app; SAMPLE listings until yours land
**Status:** 🆕 new · branch `asher/app`
- **Part status** (`xray/health.py`): **Working / Replace soon / Replace ASAP** from life used (age ÷ typical life), lifecycle status, line-stopper, and lead time. Each part gets an **order-by date** (expected end of life − fastest lead time − 14-day buffer) and a rule-based action ("reserve the spare at Fort Wayne", "buy one refurbished spare now and plan migration", "covered by own spare"). **Your money model refines the action** (cost of waiting vs. replacing): the part page has a "Financial view" slot for it.
- **Marketplace:** `data/reference/listings_sample.csv` has 132 **made-up** listings (3–5 per KB part, generic seller types, `sample=yes`, no URL) so the demo has multiple options per part. **Your real `listings.csv` replaces them part by part automatically** (`seed.py` → `load_listings`). Same columns + a `sample` column (heads-up: small shared-format addition).
- Your 5 money routes are already wired into the app and show "pending" until `xray/valuation.py`, `sourcing.py`, `pricing.py` exist.

### Sat Nov 14, ~7:45 PM · Demo registry is ready to build against (`demo.db`)
**Status:** 🆕 new · branch `asher/demo-data` (PR for CP1)
- **Run:** `./scripts/demo.sh` (fast production mode), or `python scripts/make_demo_data.py && python scripts/seed.py`, then `from xray.registry import load; reg = load()`. That's your `reg`: a dict of DataFrames (`plant`, `plant_financials`, `line`, `machine`, `component`, `spare_stock`, `spare_match`, `kb_entry`, `alternative`, `listing`, …).
- **What's in it:** 6 plants, 14 lines, 66 machines, 126 components (36% discontinued at the owned plants, 100% at Tillman), 48 storeroom rows, and 30 real KB parts.
  - The **Toledo Line 2 Kinetix 6000** is a single point of failure, and **Fort Wayne has 2 on its shelf**.
  - The **Waukesha MICROMASTER 440** is covered by a **Lima** spare (cross-company).
  - Two duplicates.
- **Matching:** components 99% precision / 91% recall; storeroom 100% / 98%. Every part not sent to review is correct.
- **Money columns** (`plant_financials`, `line` revenue/margin/hours, machine replacement values) hold the placeholder ranges from `interfaces.md` §2. `downtime_cost_per_hour_*` is blank for you to derive. **Your `listings.csv` drops into `data/reference/`**, and `seed.py` loads it.
- **New input file** (shared format change, heads-up): `<plant>/readings.csv`, what the scan read per component (see registry-format §4). Use `component.date_code` for age.

### Sat Nov 14, ~7:15 PM · The 4 parts to collect listings for (CP1)
**Status:** 🆕 new · KB: `data/reference/kb.csv` (30 real parts, branch `asher/demo-data`)
| Part | kb_id | Why it's in the demo | Target |
|---|---|---|---|
| **2094-BC01-MP5-S**: Rockwell **Kinetix 6000** servo axis module (discontinued Dec 2023) | KB-009 | **The line-stopping part at Toledo Line 2.** Fort Wayne has 2 on its shelf. | ≥ 3 listings (eBay sold, Radwell, PLC Center, DoSupply…) |
| **22B-D010N104**: Rockwell **PowerFlex 40** 5HP drive (discontinued Jun 2025) | KB-006 | Common drive across plants; successor 25B-D010N104 (PowerFlex 525) | ≥ 3 listings, plus 1 for the successor if easy |
| **1769-L32E**: Rockwell **CompactLogix** controller (discontinued Dec 2020) | KB-002 | Drives the CapEx cliff (migrate to 5069-L320ER) | ≥ 3 listings |
| **6ES5943-7UB11**: Siemens **S5-115U CPU 943** (very old) | KB-029 | **Candidate for the "no / few listings" path** → alternatives | Record whatever you find. If ≥ 3 turn up, tell me and I'll pick a rarer part. |

- One row per listing in `data/reference/listings.csv` (columns in registry-format §5). `url` + `seen_on` are required. Counterfeit risk shows for non-authorized sellers.
- **Collect by hand, don't scrape.**

### Sat Nov 14, ~7 PM · Demo portfolio is now 6 plants: two multi-plant manufacturers + a target (we target multi-plant manufacturers)
**Status:** 🆕 new
- **Granite Ridge Capital** (`F-GRANITE`) owns:
  - **Halvorsen Industrial Products** (3 plants: **Toledo PA** = deep dive, **Fort Wayne PB** = has the spare, **Lima PC**)
  - **Brightwater Packaging Systems** (2 plants: **Waukesha PD**, **Oshkosh PF**)

  **Tillman Machine Works** (**Rockford PE**) is the acquisition **target** (deal view). All fictional. The table is in `interfaces.md` §2.
- **For you:**
  - `plant_financials` has **6 rows** (placeholder ranges are in the table)
  - **`deal_adjustment` runs on Tillman** (`CO-TILLMAN`, deal value $28–34M)
  - portfolio totals sum the 5 owned plants (Rockford excluded until bought)
- **Spare sharing:** Fort Wayne → Toledo (within Halvorsen) and Lima → Waukesha (**across companies** in the fund). `recommend_sourcing` should check every owned plant.
- **Your hand-made sample can stay at 2 plants.** My generated `data/seed/demo/` has all 6.
- **Listings:** I'll post the 4 part numbers to collect within ~30 min.

### Sat Nov 14, ~6:40 PM · Your financials plan (#19) merged + your 5 format changes adopted
**Status:** 🆕 new
- **Adopted into registry-format + interfaces:**
  - downtime $/h is **derived** (+ `operating_hours_per_day`)
  - `growth` CapEx is user input only
  - failure probability comes from an **age-band parameter**, not lifecycle status
  - `spof` reads `sourcing_recommendation` (hours down depend on spares). Signature: `spof(reg, sourcing_recommendation)`
  - `plant_savings.in_price_base`
  - coverage scaling
  - `deal_adjustment(..., discount_rate)` with PV price cut + PV holdback
- **One change to your model-spec §4:** the demo dollar scale is the CP0 one (`interfaces.md` §2: PA $60–70M, ~$60–90k per line per day). The $150M / $200k anchor is fine as a sensitivity row only. Change it with a line here if you disagree.
- **Your blocker 2 (sample data):** go ahead and hand-make `data/seed/sample/` at the demo scale. My `data/seed/demo/` replaces it at CP1.

### Sat Nov 14, ~6:15 PM · CP0 locked: `docs/build/interfaces.md` (your function names + the dollar scale)
**Status:** 🆕 new
- **Your functions are pure** (they take DataFrames and return DataFrames):
  - `xray/sourcing.py`: `value_parts`, `recommend_sourcing`
  - `xray/valuation.py`: `capex_by_year`, `spof`, `deal_adjustment`
  - `xray/pricing.py`: `plant_savings`, `price`
- The input is `reg` = dict of registry tables. I'll give you `xray/registry.py` `load("demo.db")` at CP1.
- **Demo portfolio scale (placeholders for you to refine):**
  - PA: $60–70M revenue, $1.8–2.2M spares, $4.5–5.5M maintenance
  - PB: $40–45M revenue, $1.2–1.5M spares, $3–3.5M maintenance
  - downtime ~$1.5–5k/h
  - target magnitudes in §2: say if any look implausible
- **Demo script + headline numbers:** §3.
- **The KB uses real part numbers** with real lifecycle status and sources (I'm researching them).
- **Shared files** (registry-format, interfaces, requirements.txt, API routes, registry.py) need an inbox heads-up *before* you change them. Branches: `brandon/<topic>`.
- **By CP1 (~7:30):** `pricing.py` + `sourcing.py` running on placeholders.

### Sat Nov 14, ~6 PM · Format ✅ agreed with defaults (no need to answer the list now)
**Status:** 🆕 new
- Per our call: `registry-format.md` is ✅ with **defaults you can change any time** (leave a line in `to-asher.md`). They're at the top of the doc:
  - your 6 outputs as written
  - your functions take pandas DataFrames
  - 2 plants, ~30 machines
  - ~$2M spares and ~$5M maintenance per plant
  - price = 30% of savings (placeholder)
  - 3 parts with ≥ 3 listings by CP1
  - `pricing.py` running on placeholders by CP1
- Go at your own pace. The 5:45 PM entry below has the details when you want them.

### Sat Nov 14, ~5:45 PM · Registry format v2 (CP0): please OK §7 outputs + your money columns
**Status:** 🆕 new · PR (docs/registry-format-v2)
- **What changed in `docs/build/registry-format.md`:**
  - Plant data is now **export-style files per plant** (CMMS `assets.csv`, ERP `spares.csv`, `work_orders.csv`, a photo manifest).
  - **Readable IDs** (`PA-L1-M03-C2`).
  - **Fixed value lists.**
  - **Owners are named Asher / Brandon.**
  - **New `plant_financials.csv`** for your model inputs: maintenance budget, spares inventory, carrying %, rush premiums.
  - **New KB columns:** failure rate, migration cost/downtime, lead time.
- **Valuation (Asher's call):** **part value comes from real online listings**, never typed in:
  - aim for ≥ 3 listings per part, across OEM, distributors, refurbishers, surplus and eBay
  - value = the price range per condition (`listings.csv` → `part_valuation`)
  - 0 listings → `alternatives.csv` (successor / compatible / similar part; **similar-part search possibly via a Physna collaboration, TBD**)
- **What you need to do:**
  1. OK or change the **§7 outputs** (`part_valuation`, `sourcing_recommendation`, `capex_by_year`, `spof`, `deal_adjustment`, `plant_savings` + `price`).
  2. Check the columns marked **Brandon**, especially `plant_financials.csv` and `listings.csv`.
  3. Then we mark the doc ✅.

### Sat Nov 14, ~5:30 PM · I aligned your docs to the strategy (no need to redo the edit list below) + merged your research (#15)
**Status:** 🆕 new
- **Why:** agents will work on this repo, so the docs can't disagree. Your #15 research was pushed before the decision, so that's on us, not you. **Everything good in it is kept:** the Bain liquidity numbers, the PitchBook 67.1% add-on share, the NAM/Reshoring stats, the Kearney cross-portfolio paper, the guardrails, the charts, and the flywheel and moat logic.
- **What I changed (framing only, no data):**
  - In your research doc and all pivot-plan docs: own plants are the main way in, an acquisition is one way in, and the customers are multi-plant manufacturers + PE.
  - The flywheel now starts at "plant scan (own plant, or acquired / pre-exit)".
  - The buyer table has the plant owner first.
  - The demo opens with "Fund X **owns** Plant A and B" and ends with the deal lens.
  - Deck numbers: deals ≤ ~$10M, 25,799 plants, 67.1% add-ons, prices = output of your financial model.
  - The liquidity angle is kept and marked important.
  - README and AGENTS.md were rewritten. **AGENTS.md now has a "Strategy (DECIDED)" section, and the roadmap is the source of truth.**
- **The 5 PM edit list below is DONE.** Your open items: the **financial model** (`xray/pricing.py`) and the **research backlog** (P1 by CP1).

### Sat Nov 14, ~5 PM · DECIDED: own-plant evaluation is the main way in; acquisition is just one way in
**Status:** 🆕 new
- **The decision (Asher):**
  1. **The main way in is a manufacturer evaluating its own plants.** No deal needed.
  2. **An acquisition is *a* way in, not *the* way in.** The diligence market (~670 reviewed deals a year, ≤ ~$10M) is too small to rely on.
  3. **The target customer is multi-plant manufacturers *and* PE portfolios**, not PE first.

  This matches `docs/plan/roadmap-equipment-xray.md`.
- **What to update in your pivot-plan docs (your thread):**
  - **index.md, decision 1:** "Diligence is the entry point" → "**Own-plant evaluation is the main entry point; diligence is one of several.**"
  - **03-flywheel-growth.md:**
    - Add an **"own-plant assessment"** row as the main *Land* motion: VP Ops / plant manager, per-plant fee, no deal. Keep the diligence add-on as a second *Land* row.
    - Retitle "Why PE is the right first customer" to **"Why multi-plant manufacturers and PE"**: multi-plant manufacturers have the same mess (mixed brands, separate storerooms) without needing a deal.
    - Start the flywheel with "plant scan (own plant *or* acquisition)".
  - **05-poc-scope.md demo script:**
    - Open with ownership: "**Fund X owns Plant A and Plant B**…"
    - Then show the registry → CapEx cliff → evidence → single point of failure → **Plant B spare** → accuracy → live photo.
    - End with "**and when they buy their next plant, the same scan prices the deal**" (pay $X less as the second lens).
  - **04 deck map + mockup, numbers:**
    - The diligence wedge is **~$10M ceiling** (~670 reviewed deals × $15k, `docs/research/deep-dive-numbers.md`), not $3M (that was the Axial listings model).
    - Add the **own-plant number**: **25,799 US plants with 100+ employees** (Census 2022) → **$13–32M ARR at 5% adoption**, with a $258–645M ceiling.
    - **Don't pick a price.** Prices come out of your **financial model** (below). Until it runs, the deck shows ranges labeled "model output pending" ("low thousands" vs $10–20k gets settled by the model, not by us).
  - **Slide 5 (Customer):** the trigger is "plant risk / CapEx planning *or* an acquisition", not only an acquisition.
- **NEW: you build the financial model that predicts the price (Asher's decision: we don't pick prices).** Price = a share of **modeled cost saved per plant**, not a number we choose. Suggested shape (yours to change):
  - **Inputs per plant:** spares inventory $, maintenance budget, carrying-cost %, rush-buy premiums, # of critical end-of-life components, line revenue per day / downtime $/h, probability of failure. Take them from the registry where possible, so the model runs **per plant in the demo**.
  - **Savings levers:** spares released (one-time) · carrying cost avoided · rush premiums avoided · purchases avoided via a sister-plant spare · planned vs. emergency replacement. Keep **downtime avoided** as a separate, clearly labeled expected value: probability × hours × $/h.
  - **Outputs:** savings per plant per year (low/base/high) → **price per plant = value-capture share × savings** (e.g. 20–40%) → payback period / ROI for the customer. Same for the deal module (value of the CapEx finding vs. fee) and for a portfolio license.
  - **Market roll-up:** price × 25,799 plants × adoption (replace the hard-coded `PRICES` in `scripts/market_model.py` with your model's output).
  - **Where:** e.g. `xray/pricing.py` (runs on the registry) + a sensitivity table in `docs/research/`. Every input labeled measured / survey / vendor / assumption.
  - **Starting point:** the $10k / $30k / $60k per-plant scenario and the case studies in `docs/research/deep-dive-numbers.md` §D.
  - **Research backlog:** `docs/research/brandon-research-backlog.md` has 13 prioritized Velocity prompts, one per model input. **P1 (#1–6) by CP1 ~7:30 PM.** Build the model with placeholder ranges first and swap in sourced numbers as they land.
- **KEEP the liquidity angle (Asher: it's important).** Keep it in doc 03, doc 08 and appendix A3, and give it a main-deck mention (e.g. on the business-model or why-now slide), not only the appendix:
  - faster, cleaner exits (a seller scans before a sale)
  - cash tied up in idle spares
  - targeted instead of blanket CapEx
  - verified collateral (stretch)

  It works for both doors: owners free up cash from their own plants, and PE frees up cash across the portfolio and at exit. Keep the ⚠️ "hypothesis" label until research backs it. **Running doc 08 (the deep-research prompt) is yours** (money thread). It's what turns the hypothesis into numbers. I also added a liquidity section to the roadmap.

### Sat Nov 14, ~4:45 PM · Merged your pivot plan (#13) + adopted your schema; one change to the split
**Status:** 🆕 new · PR #12
- **Merged:** #11 (research) → your #13 (pivot plan) → #12 (roles + registry format).
- **Adopted from your plan:** the **2-plant portfolio** (for the Plant B spare moment), **SQLite + seed files**, and your schema (`fund`, `spare_stock`, ranges, `lead_time_wks`, `authorized`). It's all in `docs/build/registry-format.md`, with each column tagged by owner.
- **Changed: the split.** Your doc 05 split was written before we split the work by strength. **Asher (CS + stats) takes data, vision, matching, accuracy and the app. You (finance + accounting) take valuation (`xray/valuation.py`), the cost columns, sourcing (`xray/sourcing.py`), the estimates and the pitch numbers.** I put a note on doc 05. See `docs/team/roles.md`.
- **For you to settle (money thread):** your doc 03 prices the deal add-on at "low thousands", but the deep dive's consulting breakeven assumes a **$10–20k** module (`docs/research/deep-dive-numbers.md`). **Superseded (~5 PM):** don't pick a number. Your financial model derives it (see the 5 PM entry).
- **What you need to do now (CP0):** sign off on `registry-format.md`, especially the 💲 columns and outputs.

### Sat Nov 14, ~4 PM · Roles for Equipment X-Ray + registry format to sign off (CP0)
**Status:** 🆕 new · branch `plan/roles-and-registry`
- **Roles** (`docs/team/roles.md`): you take **💲 the money thread**:
  - `xray/valuation.py`: CapEx cliff, "pay $X less" / holdback, deferred CapEx as a hidden liability
  - the cost columns in the knowledge base and lines
  - sourcing offers + the buy / migrate / monitor rule (`xray/sourcing.py`)
  - refining the estimates with Velocity
  - pitch numbers + judge Q&A

  I take **🛠 the machine thread**: fake factory + answer key, knowledge base identity/lifecycle, vision extraction, accuracy, the app, and the live photo demo.
- **Checkpoints:** CP0 ~4:30 (format), CP1 ~7:30 (slices work alone), CP2 ~10:30 (end to end), CP3 ~1 AM (freeze), CP4 ~7 AM (rehearse). Submit by 8:30.
- **What you need to do now:** read `docs/build/registry-format.md` (draft), especially the 💲 columns and the outputs you'd produce, and edit anything you'd model differently (e.g. how the holdback is computed). Then we mark it ✅ agreed.
- **Context for your numbers:** `docs/research/deep-dive-numbers.md` + `scripts/market_model.py` (PR #11).

### Sat Nov 14, afternoon · `main` cleaned up for Equipment X-Ray
**Status:** 🆕 new
- **What changed:** Afterlife-only code, data and docs are gone from `main`. These reusable pieces stay:
  - **`xray/matching.py`**: normalize + fuzzy matching, generalized from `match_spend`, for matching nameplate text to the knowledge base
  - **`xray/evaluate.py`**: precision/recall against an answer key
  - the FastAPI and Next.js shells, CI, and `checkpoint.sh`

  The README and AGENTS.md now describe Equipment X-Ray. Nothing is lost: everything is in the tag `archive/afterlife-main`, and the old branches are in `archive/*` tags.
- **What you need to do:** `git checkout main && git pull && git fetch --prune --tags`. If you have unpushed local Afterlife work, push it to a branch first.

### Sat Nov 14, ~11:45 AM · 🔄 PROPOSED PIVOT after the judge review: please read and decide
**Status:** 🆕 new
- **What the judge said:**
  - our scope is too wide
  - half the room is doing "consultancy efficiency"
  - nobody is on the Startup track
  - old, acquisition-heavy companies have the biggest holes
- **The proposal:** pivot to **Equipment X-Ray**, pre-deal equipment diligence on the Startup track. It gives a CapEx cliff, "pay $X less", and the single points of failure from discontinued components.
- **Where:** `docs/plan/idea-equipment-xray.md`
- **What you need to do:** answer §13: yes, no or modify, how we split the work, and anything the judge said that it misses.
- **Update ~12:30 PM:** a mentor liked it and said keep digging. They want a **roadmap and a clear MVP plan, not a full build**, with **parts sourcing** as a key feature and a **PE portfolio** angle. See `docs/plan/roadmap-equipment-xray.md`.

*Older Afterlife entries are in the tag `archive/afterlife-main`.*
