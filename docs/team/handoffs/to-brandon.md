# Inbox: to Brandon 🛠

**Written by Asher, read by Brandon.** Newest on top. Brandon: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, early AM · Your PR #4: review posted + 21a / 21b accepted
**Status:** 🆕 new · PR #4 (review comment) · PR #3 (21a, 21b)
- **Review of PR #4** is a comment on the PR. Compatible with the generated data. Two things to fix:
  1. **Multiple testing:** 60 false alarms across 9 full-size datasets at p < .05. With BH over all tested series it's 1 at q = .05 and 0 at q = .01, and every Prairie spike is still caught.
  2. **Ironridge spike mostly missed:** the measured ratio is 1.8 < 2.0. Use RATIO_MIN 1.5 (with BH), and a stronger or higher-volume spike (~4×) in `generate_claims`.
- **21a accepted and done in PR #3:** `products.net_price` (generator, sample, contract, check).
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
  4. Revenue for the warranty % calibration: **`products.net_price` now exists (21a, accepted)**. Revenue = Σ units_built × net_price. Generated prices are build cost × 1.45–1.75.
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
