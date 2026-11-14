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
### Sat Nov 14 · Brandon → Asher · Contract v4 proposal: accounting fields + supplier agreement documents
- What changed: `warranty_claims` gains `claim_date`, `paid_date`, `other_cost`, `recovered_usd`. `products` gains `avg_selling_price`. New `supplier_agreements/` folder (documents) + `truth_terms.csv`; new output `supplier_terms` from `afterlife/extract_terms.py` (stub, wired into `run.py`). Sample regenerated: every v3 value is identical, only 5 claims not yet reported by `data_as_of` dropped out.
- Where: branch `warranty/contract-v4-accounting`, `docs/build/data-contract.md` (v4 + "Stored or extracted?"), `afterlife/check.py`, `afterlife/io.py`, `scripts/make_sample.py`
- What you need to do: review the PR. One thing lands in your thread: `generate_spend` must emit `products.avg_selling_price` (docstring updated). The SAP adapter is unchanged.
- Known issues: none. `./scripts/checkpoint.sh` is green, 13 tests pass.

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
