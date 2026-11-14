# Inbox: to Brandon 🛠

**Written by Asher, read by Brandon.** Newest on top. Brandon: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, ~11:30 AM · ⚠️ Generated companies now HAVE supplier agreements (Asher went ahead) + your data map
**Status:** 🆕 new · branch `spend/cost` (CP3 batch)
- **Asher decided to go ahead with the agreements/price-schedule proposal** (sorry for not waiting; tell me what you'd change). What exists now:
  - `afterlife/agreements.py` writes one agreement per main-plant production supplier for each generated company (48 / 43 / 41 docs), in **your three styles** (formal / table / amended) with **your wording**, plus a **"5. Prices"** section and clause 5.3 (spares at series price, or by quotation).
  - **`warranty_terms()` and `_warranty_section()` in `agreements.py` are yours.** I mirrored your sample distribution; tune them freely.
  - `generate_spend` now returns `supplier_agreements`, **`truth_terms`** (your schema) and `truth_prices` (mine).
- **What this means for `generate_claims`:** **don't generate `supplier_agreements` / `truth_terms` again.** Read them from `spend["truth_terms"]` to value recovery. If your function returns those keys, they'll override mine in `generate.py` (`{**spend, **claims}`). Your `extract_terms.py` can be built and scored against these docs right away.
- **Shared files touched:** `io.py` (`truth_prices` in TABLES), `check.py` (truth_prices checks), `run.py` (`contract_prices`, `contract_compliance`), `profiles.py` (spare-pricing and leak knobs), `api/main.py` (`/compliance`, overview fields).
- **Velocity changed the spend story** (log in `docs/research/velocity.md`): 1.5–5× spare markups aren't a typical benchmark, so spares are now mostly near the contract price. The headline is **"paid vs the supplier's own contract"**: Prairie $2.3M leakage + $0.8M spares-clause gap, both shown on the Overview with the agreement document.
- **Notes on your "Afterlife Data Map" (in Velocity):** great for judges. Three small things:
  1. Add **spend assumptions** to the checklist: "spare markups are a scenario, not a benchmark (Velocity)", "production pays the contract price except ~15% of pairs with unapproved increases", "supplier part-number lookups are complete (to be made patchy)".
  2. It says **"contract (PR #6, in review)"**, but #6 is merged.
  3. The sample shows plant **`P-IA1`**, generated companies use **`P-MAIN`** (acquired plant `P-TX2`). Worth a footnote.

### Sat Nov 14, ~11 AM · Overview screen + spend endpoints live · shared-file changes you'll touch
**Status:** 🆕 new · branch `spend/cost` (batch PR at CP3)
- **What's ready:** `GET /overview`, `GET /markups`, `GET /harmonization` (all `?company=`), and the **Overview screen** (`web/src/app/page.tsx`): headline savings, after-sale cost chart, coverage bars, markup and harmonization tables. Tested in `tests/test_api.py` (44 tests pass).
- **Shared-file changes:**
  1. `afterlife/run.py` now runs **spend-only companies** too (`companies(require_claims=False)`) and **skips detection when a company has no claims**. Once your `generate_claims` writes claims, detection runs automatically.
  2. `run.py` also saves `price_harmonization`.
  3. `api/main.py` has `_has_table()` and `_company_or_404()` helpers. Reuse them for `/alerts` and `/claim-rates`, and follow the same pattern (Pydantic model, `?company=`, filter on `company_id`).
  4. `web/src/lib/api.ts` has **`resolveCompany(searchParams.company)`** plus `Overview` / `Markup` / `Harmonization` types. Copy the top of `page.tsx` for your Early-warning screen; it's the same company handling.
- **Reminder:** after adding endpoints, run `python scripts/export_openapi.py && (cd web && npm run types:api)`, otherwise the CI check "frontend API types match the API" fails.

### Sat Nov 14, late morning · cost.py done · shared-file change · PROPOSAL: agreements for generated companies + price schedule
**Status:** 🆕 new · branch `spend/cost` (batch PR at CP3)
- **What's ready:** `afterlife/cost.py` (build vs lifecycle cost, spare markups, price harmonization). 43 tests pass. On the default seed:
  | | Prairie | Ironridge |
  |---|---|---|
  | spare overspend | $2.15M ($1.24M/yr) | $4.30M ($2.48M/yr) |
  | price harmonization | $4.0M | $4.7M, of which **$2.7M is the acquired plant P-TX2** |

  Warranty per unit is $0 on generated companies until your `generate_claims` lands. On the sample it uses claims parts + labor + other_cost. The 21b rule is enforced and tested: `warranty_repair` service spend is reported as `warranty_repair_spend`, never added.
- **Shared-file change (heads-up, per the new rules):** `match.link_all()` now returns the spend links even while `link_claims` raises `NotImplementedError`, because cost.py and evaluate need them. When your `match_claims` exists, nothing changes. Also removed the duplicate avg_selling_price check in `check.py`, and `AGENTS.md` now points at the inboxes instead of `handoffs.md`.
- **PROPOSAL (contract change, please agree or push back before either of us builds it):**
  1. **Generated companies need `supplier_agreements/`** (check warns: 48 / 63 / 41 production suppliers have none). Proposal: **`generate_spend` writes them**, since it knows every supplier, part and price. It calls a function *you* own for the quality/warranty-terms section (recovery %, labor cap, window…, plus `truth_terms`), so the terms logic stays in your thread.
  2. Each agreement gets a second section, a **price schedule**: part, contracted price per piece, valid from/to, volume tiers, and a "spares at production price" clause yes/no. Answer key `truth_prices.csv`.
  3. `extract_terms.py` also outputs **`contract_prices`** (same regex + Claude approach, scored against `truth_prices`).
  4. That gives the spend side **price compliance** ("your agreement says $4.12 until Dec 2026, 37 POs paid $4.60") and a stronger brief ("your own contract §4 says spares are priced at production rate").

  Reply in `to-asher.md` (or just tell me). If it's a yes, I'll draft the exact document format and columns in `data-contract.md` for you to sign off.

### Sat Nov 14, morning · New process (batch reviews) + your contract-v4 branch overlaps mine
**Status:** 🆕 new · PR #5
- **New process (agreed by Asher, see `docs/team/workflow.md`):**
  - No PR per file. One long-running branch per thread. **Batch PRs at CP3 (12:30), CP5 (6 PM), CP6 (9:30 PM).**
  - `./scripts/checkpoint.sh` green before every push, and **GitHub now runs the checks on every push** (✅/❌ per commit).
  - Shared files and contract changes: tell the other person the moment you push, and **agree on contract changes before building**.
- **Your `warranty/contract-v4-accounting` overlaps my PR #5 in 6 files:** `check.py`, `generate_spend.py`, `data/sample/products.csv`, `data-contract.md`, `handoffs.md`, `make_sample.py`. Main point: we both added the selling price, you as **`products.avg_selling_price`** and me as **`products.net_price`** (21a). **Done: renamed mine to your `avg_selling_price`**, with the same column position, sample values (14,500 / 18,900 / 22,500), contract wording and check message as your v4 branch, so that part merges cleanly.
- **Suggested order:** merge PR #5 (my whole spend batch: generator, matcher, evaluate, inboxes, CI) into main first. Then merge main into your v4 branch, resolve the 6 files (move your `handoffs.md` entries into `to-asher.md`), and PR it at CP3.
- PR #3 is closed; it's fully contained in PR #5.

### Sat Nov 14, early AM · Spend matcher + evaluate.py ready, and an offer to take match_claims
**Status:** 🆕 new · PR #5 (stacked on PR #3)
- **What's ready:** `afterlife/match_spend.py` links every purchase line to a part (exact part number → supplier part-number crosswalk → shared numbers/spec codes → fuzzy text), with `evidence` JSON, `source_system`, `run_id`. `afterlife/evaluate.py` (shared) is implemented: `python -m afterlife.evaluate` prints precision/recall per company × table × method.
- **Accuracy on companies never used for tuning** (3 fresh seeds × 3 companies): precision and recall **≥ 97.8% everywhere** (production 99.7–100%, service 97.8–100%). Links with confidence ≥ 0.8 are **99.9–100% correct**, so recovery should use only those. Weak-but-clear matches are linked at confidence 0.4 for human review.
- **Shared code you'll want for `match_claims`:**
  - `match.normalize()` + `abbreviation_map()` (now with generic shop shorthand: `STL`, `ZP`, `HD`, … in every company's `abbreviations.csv`)
  - `match_spend.canon()`: also joins units/dimensions (`20 mm` → `20MM`, `35 x 47` → `35X47`)
  - `match_spend.numbers()`: unit-free numbers; comparing these beat comparing spec strings by a lot
- **Offer for CP1:** your list is long (PR #4 fixes → **`generate_claims` (critical path)** → `match_claims` → `/alerts` → screen). The matching approach is fresh in my head, so **I can take `match_claims.py`** and you focus on `generate_claims` and detection. Your call. Tell me at CP1 or in `to-asher.md`.
- **Merge order:** PR #3 first, then PR #5 (it contains PR #3's commits until #3 merges).

### Sat Nov 14, early AM · Your PR #4: review posted + 21a / 21b accepted
**Status:** 🆕 new · PR #4 (review comment) · PR #3 (21a, 21b)
- **Review of PR #4** is a comment on the PR. Compatible with the generated data. Two things to fix:
  1. **Multiple testing:** 60 false alarms across 9 full-size datasets at p < .05. With BH over all tested series it's 1 at q = .05 and 0 at q = .01, and every Prairie spike is still caught.
  2. **Ironridge spike mostly missed:** the measured ratio is 1.8 < 2.0. Use RATIO_MIN 1.5 (with BH), and a stronger or higher-volume spike (~4×) in `generate_claims`.
- **21a accepted and done in PR #3:** `products.avg_selling_price` (originally `net_price`, renamed to match your v4) (generator, sample, contract, check).
- **21b accepted and in the contract (PR #3):** see "Cost rules" in `data-contract.md`. Please mark 21a and 21b ✅ in `cp0-proposal.md` item 21 when you merge PR #4, and drop the "not applied yet" note in the alerts section.

### Sat Nov 14, early AM · 📬 How handoffs work now: one inbox each
**Status:** 🆕 new · PR #3
- **What changed:** `docs/team/handoffs.md` is gone. There are now **two inboxes** in `docs/team/handoffs/`:
  - **`to-brandon.md`** (this file): Asher writes, you read
  - **`to-asher.md`**: **you write**, Asher reads
  - `README.md`: rules, template, planned handoffs, and history
- **Why:** we both added entries to the top of one file from different branches, so every pair of PRs conflicted on it. Each inbox now has exactly one writer, so that can't happen.
- **What you need to do:**
  1. Put your handoffs in **`to-asher.md`**, newest on top, using the template in `README.md`, and always link the PR.
  2. In this file, only change the **Status** line (🆕 new → 👀 reviewing → ✅ done).
  3. Check this inbox at every checkpoint. It's now step 1 of each one in `checkpoints.md`.
  4. **Your PR #4 still adds to the old `handoffs.md`**, so it conflicts with PR #3 on that one file. When the second of the two PRs merges, move your PR #4 entry into `to-asher.md` and delete `handoffs.md`. I tested this: it's the only conflict, and the combined code passes all 26 tests.

### Sat Nov 14, early AM · Asher → Brandon · Spend generator ready (CP2 handoff, early)
**Status:** 🆕 new · PR #3
- **What's ready:** `afterlife/generate_spend.py` generates all 3 companies in about 2 s. `python -m afterlife.generate` writes `data/generated/<company>/` (spend tables only until your `generate_claims` exists; it prints a note). `python -m afterlife.check spend` checks the spend side: 0 failing.
  | | Prairie | Ironridge (SAP extract) | Northwind (HVAC) |
  |---|---|---|---|
  | parts / BOM lines | 300 / 490 | 380 / 768 | 260 / 405 |
  | production lines | 2,506 | 4,570 (1,371 acquired plant P-TX2) | 2,016 |
  | service lines | 414 | 610 | 407 |
  | spike | `101-2042-02` oil seal, supplier `S-003`, from lot `PO-4500003070-010`, 3.0× | `IR-04242` 6206 bearing, supplier `100007`, from lot `4500003820-00010`, 2.5× | none (control) |
- **What you need for `generate_claims`:**
  1. **`spend["_spike_plan"]`** (passed into your `generate(seed, spend, profile)`): `{part_no, supplier_id, start_build_month, from_po_line_id, multiplier}`, or `None` for Northwind. I already picked the dual-sourced shared part and the lot, so copy it into `truth_spikes`.
  2. Claim rate for a product/month = base × (1 + (multiplier−1) × share of that product/month's spike part coming from `from_po_line_id` onward). Use `spend["build_supply"]`.
  3. **Spike start months moved to quarter starts** (lots are bought quarterly): Prairie `2026-04`, Ironridge `2025-10`.
  4. Revenue for the warranty % calibration: **`products.avg_selling_price` now exists (21a, accepted; renamed from `net_price` to match your v4)**. Revenue = Σ units_built × avg_selling_price. Generated prices are build cost × 1.45–1.75.
- **Heads-up (shared code):** `io.load()` now reads **all ID columns as text** (`io.ID_COLUMNS`). Ironridge's numeric supplier IDs were loading as int in one table and str in another, and 17.5k `build_supply` rows silently failed to join. If you load CSVs yourself, use `dtype=str` for IDs.
- **Known issues:** none. 16 tests pass.

### Sat Nov 14, early AM · Asher → Brandon · Data contract v3 (from your CP0 review)
**Status:** ✅ done · reviewed + merged in PR #1 (CP1)
- What changed: merged your `plan/cp0-additions` into `test-data-batch`, then applied #10–15, #17, and the #19 schema. New tables: `build_supply.csv`, `abbreviations.csv`. `truth_spikes.from_po_line_id`, links v2 columns, `runs` table, SAP adapter. Northwind has HVAC codes and categories (24 categories, 16 failure codes in the union).
- Where: `docs/build/data-contract.md` (v3 section + SAP table), `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/adapters/sap.py`, `afterlife/check.py`, `scripts/make_sample.py`, `tests/`
- What you need to do:
  - **CP1 review (now):**
    1. `git fetch && git checkout test-data-batch && git pull`, then `./scripts/checkpoint.sh` (should be green)
    2. Read `docs/plan/plan-updates.md` → Update 4, and the status table at the top of the addendum in `docs/research/cp0-proposal.md`
    3. Look at `data/sample/build_supply.csv` + `truth_spikes.csv`. The seal kit is dual-sourced (Keystone S-022 / Bluewater S-023), and the spike is only on Keystone's April lot `PO-450005-010`. Is that usable for `detect.py`?
    4. Answer in a PR #1 comment: which Claude model ID to pin, and who has an API key
    5. All good → merge PR #1 with **"Create a merge commit"** (not rebase). Anything off → comment on the PR and tell Asher
  - **After the merge (your next task, not part of the review):** `git checkout main && git pull && git checkout -b warranty/detect`, then build `detect.py` against that sample spike
- Known issues: none. `./scripts/checkpoint.sh` is green, 7 tests pass.
