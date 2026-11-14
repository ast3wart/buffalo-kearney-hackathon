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
### Sat Nov 14, morning · Brandon → Asher · detect v1 + two accounting asks for the spend thread
- What changed / what's ready:
  - `afterlife/detect.py` v1 works on the sample. It finds Keystone's seal-kit spike from `PO-450005-010` and doesn't flag Bluewater.
  - `alerts` has new columns (`claims`, `p_value`, `excess_cost_usd`, `open_exposure_usd`, `attribution`, `spike_claims`). The data contract is updated.
  - New `docs/research/warranty-accounting.md` (accounting guardrails). The proposals are in `cp0-proposal.md` item 21.
- Where: branch `warranty/detect` (PR to main), `tests/test_detect.py`, `pytest.ini` (tests only collect from `tests/`)
- What I need from you (decide at CP2, cheap now):
  1. **21a:** add `net_price` to `products.csv` in `generate_spend` (warranty as a % of revenue needs it; the profiles already calibrate against it)
  2. **21b, double-count rule** for `cost.lifecycle_cost`: warranty cost = claim `parts_cost + labor_cost`. `service_spend` with `channel = warranty_repair` is for reconciliation only and **not added**. Only `spares` is added.
  3. Not mine, from the PR #1 review: the SAP adapter turns `PO-450001-010` into `0000450001-00010`, so Ironridge's `build_supply` / `truth_links` won't join its spend.
- Known issues: `detect` only runs in `afterlife.run` once `match_claims` produces links (next on my list). Tests use the answer-key links.

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
