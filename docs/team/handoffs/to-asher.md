# Inbox: to Asher

**Written by Brandon, read by Asher.** Newest on top. Asher: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, ~11:30 PM · Downtime number rebuilt (PR `brandon/downtime-horizon`) + final deck v1 + ⚠️ Waukesha numbers don't reproduce
**Status:** 🆕 new
- **Shared files touched:** `api/main.py` (`/plants/{id}/savings` now also returns `downtime_rescues`; additive), `web/src/app/plants/[plantId]/page.tsx` (top three rescues), `web/src/app/sources/page.tsx` (price, downtime and Tillman rows).
- **Downtime avoided is much smaller and no longer extrapolated:** only rescues we found, one failure per spare over 3 years, outage capped at 10–25 operating days, 40–80% of output counted. Toledo ~$19k / yr. Line-stopper exposure drops too. Not priced, as before.
- **⚠️ Open:** the rework report quoted Waukesha $22k and portfolio $61k; a clean rebuild gives $3.8k and $51k. See `docs/plan/final-refinements/04-downtime-waukesha-discrepancy.md`. Don't quote those two until it's closed.
- **Rebuild `demo.db`** (`python scripts/seed.py data/seed/demo demo.db`) before rehearsing.
- **New docs:** `docs/plan/final-refinements/` (objections, data ladder, app to-do list) and `docs/plan/final-slidedeck/deck-v1.html` (11 slides + appendix; the case study slot on slide 2 is still empty, and the thermal slide needs your sources).

### Sat Nov 14, ~11 PM · Rare part picked: Westinghouse Numa-Logic PC-1100 (0 listings)
**Status:** 🆕 new
- **eBay active + sold: 0** exact matches; **Radwell: not found**. Results in `data/reference/listings_raw/rare-part-check.md`.
- #4 AutoMax is out (Radwell lists 57C431A under ABB / Baldor Reliance); #3 TI 5TI-1000 also not on Radwell but not checked on eBay; #2 not checked.
- **For you:** add it to `kb.csv` with its lifecycle source and put it in a Tillman (Rockford) machine. No `listings.csv` rows (that's the point), so `value_parts` gives confidence `none` → alternatives path. Please add an `alternatives.csv` row (successor / similar) so the app has something to show.

### Sat Nov 14, ~10:30 PM · Final numbers (PR #27) + deal lens now includes end-of-life machines + ⚠️ ~110 duplicate "* 2.*" files on main
**Status:** 🆕 new · PR #27 (`brandon/final-numbers`)
- **Your option 2 is in:** `valuation.machine_capex(reg, capex_by_year, part_valuation)` = whole machines past typical life (by machine_type, in params) or past the low end and `poor`; low = rebuild at 40% of replacement value, high = replace new; controls on those machines are netted out. `deal_adjustment` includes it by default (`include_machines=True`) and adds `controls_deferred_low/high`, `machine_deferred_low/high`, `machine_ids`. **No API change needed**: `/companies/CO-TILLMAN/deal` picks it up.
- **Tillman now:** price cut **$429k** (controls $79k + 6 machines from 1992–99 at rebuild cost $350k) + holdback **~$1.3M at 25%** (your route passes 10% → ~$1.7M). Suggest the deal page shows the two lines separately ("control parts" vs "machines at end of life"). Owned plants' CapEx chart is unchanged (controls only); `machine_capex` is there if you want a second series.
- **Velocity #16 migration costs** in `kb.csv` (large-chassis PLCs $9.6–40k, small + Kinetix $3.8–16k). Price per plant base **$5.9k** (Toledo $9.5k) on the new plant finances; ARR at 5% ~$7.6M (a floor, demo plants are the smallest size band).
- **⚠️ Duplicates:** `git ls-files | grep " 2\."` shows ~110 files like `xray/valuation 2.py`, `tests/test_money_model 2.py`, photos, `web/.../page 2.tsx` (macOS/iCloud sync copies). Pytest collects `tests/* 2.py` too. Please delete them in a cleanup PR (I didn't touch them).
- **Rare part:** I'm checking your 4 candidates now (`data/reference/listings_raw/rare-part-check.md`).

### Sat Nov 14, ~9:30 PM · 5 answers I need before slides + merge order #21 → #22 → #23
**Status:** 🆕 new · details in the entries below
1. **Contract:** OK to add the extra output columns and optional arguments (entry "Money model is in")? If yes, add them to registry-format §7 / interfaces §1.
2. **Which price the app shows:** I suggest the full-plant quote (`plant_savings(full_plant=True)`, labeled "extrapolated") on screen, with the sample-only number in the drill-down.
3. **Targets + demo script:** lower interfaces §2 to the model's numbers and drop "20+ weeks" (entry "~9 PM"), or add components to Tillman.
4. **⚠️ Spares inventory (most important):** carrying cost is 66% of the price base, and it comes from the $1.8–2.2M spares placeholder in `make_demo_data.py`. Velocity #1 says ~$0.74M, which would roughly halve the $11.5k base price. You change the ranges or I do? (Also carrying 12/18/30%, rush ~$40k.)
5. **⚠️ No-listings part:** the S5 has 7 listings, and the MicroLogix 1764-LSP stand-in only looks unlisted because nobody searched it. Please pick a genuinely rare part; I'll confirm it has 0–2 listings.

**Current slide numbers (pending #4):** $10–20k per plant per year (base $11.5k at 20% capture), payback < 3 months, ~$15M ARR at 5% adoption, ~$297M ceiling. Details in `docs/research/price-sensitivity.md`.

### Sat Nov 14, ~9 PM · Please lower the target magnitudes in interfaces.md §2 (the model, on your demo.db, lands well below them)
**Status:** ✅ done (answered in to-brandon.md, ~9:15 PM entry + ~9:30 PM follow-up) · PR #22
- **Model output on your `demo.db`** (Velocity values swapped in, see PR #22):
  - **Toledo 5-yr CapEx:** $70–351k (target said $1.5–3M)
  - **Top single-point-of-failure exposure:** up to ~$200k/yr (PA-L2-M02-C2, PA-L2-M01-C2); the Kinetix with the Fort Wayne spare is far lower
  - **Tillman:** price cut $72k (deferred CapEx low case at face value) + holdback ~$156k (PV of the high–low gap at 25%), vs target $1–2M
  - **Price per plant, full-plant quote** (extrapolated from the register sample): base $7–19k, payback ~2.4 months. Sample-only (2–4% coverage) is $1–2.5k.
- **Why:** 7–30 components per plant, and **real listings show broker units in 2–9 days**, not the "20+ weeks" in the demo script (20 weeks is a new OEM unit, which a discontinued part doesn't have). I'm keeping the real lead times.
- **Proposed new §2 targets:** PA 5-yr CapEx **~$0.1–0.4M**; top SPOF **≤ ~$200k/yr**; Tillman **~$70k cut + ~$150k holdback**; price per plant **$7–19k (full-plant quote)**.
- **Proposed demo-script change (§3 step 5):** drop "20+ weeks"; say "**a broker has it in days, at $4.3–6.5k refurbished, more than the successor; Fort Wayne has 2 on the shelf**". Or, if you want bigger deal numbers, add more components to Tillman (it's a $28–34M company with only ~10 components scanned).
- **plant_financials (mine, your generator writes it):** Velocity #1 says ~$2.1M maintenance and ~$0.74M spares per plant, below the $1.8–2.2M spares placeholder. Tell me whether you want me to edit `make_demo_data.py` or you'll change the ranges; it cuts the one-time spares release by ~60%.

### Sat Nov 14, late · Money model is in (PR `brandon/money-model`) + PROPOSED contract additions (additive only, nothing renamed)
**Status:** ✅ done (answered in to-brandon.md, ~9:15 PM entry + ~9:30 PM follow-up) · `xray/params.py`, `sourcing.py`, `valuation.py`, `pricing.py`, `tests/test_money_model.py`. Smoke-tested on your `demo.db` too (seeded from `asher/demo-data`): runs, no code changes needed on your side.
- **Proposed: extra columns after the §7 ones** (the §7 columns are unchanged and come first):
  - `part_valuation` + `n_low_trust` (listings with trust_score < 0.35: flagged, kept out of the price range)
  - `sourcing_recommendation` + `plant_id, kb_id, spare_plant_id, transfer_cost_low/high, part_value_low/high`
  - `spof` + `plant_id, kb_id, action, annual_failure_rate_low/high, downtime_cost_per_hour_low/high` (`annual_failure_rate` = base)
  - `plant_savings` + `basis` (one-line formula text); `price` + `price_per_plant_base, recurring_savings_base`
- **Proposed: optional kwargs on the §1 signatures** (the documented calls still work): `capex_by_year(..., sourcing_recommendation=None, growth=None)`, `deal_adjustment(reg, capex_by_year, company_id=None, discount_rate=None)` (None → every target company), `plant_savings(reg, sourcing_recommendation, part_valuation=None, spof_table=None)`. Price check 4 (deal fee) is per company: `pricing.deal_fee_check(deal_adjustment, deal_fee)`.
- **Zero-listing part in the sample is KB-003** (MicroLogix 1764-LSP → `migrate`), not KB-029.

### Sat Nov 14, ~8:15 PM · Listings are in (42 real, 6 parts) + the S5 isn't a "no listings" part
**Status:** ✅ done (answered in to-brandon.md, ~9:15 PM entry + ~9:30 PM follow-up) · branch `brandon/sample-data`
- **`data/reference/listings.csv`**: 42 hand-collected listings (eBay sold, Radwell, DO Supply), 2026-11-14, all `authorized = no`. Parts: KB-009 Kinetix 6000, KB-006 PowerFlex 40, KB-002 CompactLogix L32E, KB-029 S5 CPU 943, plus the successors **KB-022** (2198-D006-ERS3) and **KB-019** (25B-D010N104). Raw page text + screenshots: `data/reference/listings_raw/`. 3 bundles excluded; one "for parts" Kinetix kept as `for_repair`.
- **⚠️ KB-029 (S5 CPU 943) has 7 listings** (Radwell has 64 refurbished in stock at ~$949). Per your note: **please pick a rarer part for the alternatives path** (or tell me which one and I'll check it has 0–2 listings). Until then the zero-listing case has no real part.
- **Demo line:** a refurbished Kinetix 6000 costs **$4.3–6.5k**, more than a new-surplus successor Kinetix 5700 (~$4.3k, + migration). Fort Wayne's 2 shelf spares ≈ $9–13k at refurbished prices.
- **`data/seed/sample/`**: my small stand-in (Toledo, Fort Wayne, Rockford target; rows copied from your `demo/`, same IDs). Copies of your KB/alternatives rows sit in `data/seed/sample/reference/` so nothing collides with your `data/reference/kb.csv`. Answer key in `data/truth/sample/`.
- **Next from me:** `xray/sourcing.py`, `valuation.py`, `pricing.py` on the sample, then on your `demo.db` once `asher/demo-data` merges. `recommend_sourcing` checks every **owned** plant's shelf and skips `status = target` plants (Rockford's Kinetix spares don't count until it's bought).

*(Older Afterlife entries are in the tag `archive/afterlife-main`.)*
