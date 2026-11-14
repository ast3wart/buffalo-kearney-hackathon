# Handoffs

Use this when you hand something to the other person or change something they depend on. Newest entries go at the top. Keep each one short.

## Template
```
### <time> · <from> → <to> · <what>
- What changed / what's ready:
- Where it is (file, branch, command):
- What you need from them:
- Known issues:
```

## Planned handoffs
| When | From → To | What |
|---|---|---|
| Fri night | both | Data contract agreed (`docs/build/data-contract.md`) |
| Fri night | both | API contract agreed (`docs/build/api.md`), app layout committed |
| Sat ~12:30 | 💲 Asher → 🛠 Brandon | `generate_spend` output (bom, builds) so the claims generator can use the real BOM |
| Sat ~6 PM | both | Full `afterlife.run` on generated data, both screens live, accuracy numbers |
| Sat ~10 PM | 💲 Asher → 🛠 Brandon | Deck draft for review |

## Log
### Sat Nov 14, early AM · Asher → Brandon · Spend generator ready (CP2 handoff, early)
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
  4. Revenue for the warranty % calibration: there's no price column, so use build cost (Σ qty_per × std_cost) × ~1.6 as a list-price proxy.
- **Heads-up (shared code):** `io.load()` now reads **all ID columns as text** (`io.ID_COLUMNS`). Ironridge's numeric supplier IDs were loading as int in one table and str in another, and 17.5k `build_supply` rows silently failed to join. If you load CSVs yourself, use `dtype=str` for IDs.
- **Known issues:** none. 16 tests pass.

### Sat Nov 14, early AM · Asher → Brandon · Data contract v3 (from your CP0 review)
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

### Fri Nov 13 · both · CP0 contract lock
- What changed: data contract v2 (part_no + price_unit on spend, info_records, dataset_info, 12 SYSTEM-MODE failure codes, 21 categories). **Three companies** in `data/generated/<company_id>/`. API takes `?company=`.
- Where: `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/check.py`
- What you need: generators take a `profile` argument. Run `python -m afterlife.check` before pushing.
