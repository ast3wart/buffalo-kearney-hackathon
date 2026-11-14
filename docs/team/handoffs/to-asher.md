# Inbox: to Asher 💲

**Written by Brandon, read by Asher.** Newest on top. Asher: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, late morning · Contract v4: accounting fields + supplier agreements as documents
**Status:** 🆕 new · PR #6
- What changed: `warranty_claims` gains `claim_date`, `paid_date`, `claim_type` (21c), `other_cost`, `recovered_usd`. New `supplier_agreements/` folder (documents) + `truth_terms.csv`; new output `supplier_terms` from `afterlife/extract_terms.py` (stub, wired into `run.py`). `products.avg_selling_price` is already yours from PR #5 (thanks for the rename).
- **Touches your thread:** the double-count rule now reads warranty cost = `parts_cost + labor_cost + other_cost` (contract "Cost rules", `cost.py` docstring). `cost.py` isn't built yet, so nothing breaks.
- Where: branch `warranty/contract-v4-accounting` (main merged in, no rebase), `docs/build/data-contract.md` (v4 + "Stored or extracted?"), `afterlife/check.py`, `afterlife/io.py`, `scripts/make_sample.py`
- What you need to do: review and merge PR #6. The SAP adapter is unchanged.
- Known issues: none. Checkpoint green.

### Sat Nov 14, morning · detect v1 (+ your PR #4 review applied) and two accounting asks
**Status:** 🆕 new · PR #4
- What's ready / what changed:
  - `afterlife/detect.py` v1 works on the sample. It finds Keystone's seal-kit spike from `PO-450005-010` and doesn't flag Bluewater.
  - `alerts` has new columns (`claims`, `p_value`, `q_value`, `excess_cost_usd`, `open_exposure_usd`, `attribution`, `spike_claims`). The data contract is updated.
  - **Your review applied:** Benjamini–Hochberg over every tested (part, supplier) series (`FDR_Q`), `RATIO_MIN` 2.0 → 1.5, a 300-clean-series test (0 alerts), Ironridge's planted spike 2.5× → 4.0× in `profiles.py`.
  - New `docs/research/warranty-accounting.md` (accounting guardrails). Proposals are in `cp0-proposal.md` item 21; 21a and 21b are marked ✅ (you applied them in PR #5).
- Where: branch `warranty/detect` (PR #4), `tests/test_detect.py`, `pytest.ini` (tests only collect from `tests/`)
- What you need to do: nothing blocking. Your `_spike_plan` for Ironridge now reads 4.0× from the profile.
- Known issues: `detect` only runs in `afterlife.run` once `match_claims` produces links. Tests use the answer-key links.
