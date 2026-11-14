# Financials (money thread): plan, steps, research

**Status:** Sat Nov 14, ~6:30 PM. Owner: Brandon (money thread, see [roles.md](../../team/roles.md)). The data contract is [registry-format.md](../../build/registry-format.md) (✅ agreed at CP0 with defaults; Brandon can change the money-side items with a line in `to-asher.md`).

| Doc | What |
|---|---|
| **index.md** (this) | Blockers, to-do steps up to CP1 and CP2 |
| [velocity-prompts.md](velocity-prompts.md) | **Every prompt to paste into Velocity**, with a fallback range for each so nothing waits on research |
| [model-spec.md](model-spec.md) | How the calculations chain together, what's real vs synthetic, formulas, guardrails |

## Blockers (as of ~6:30 PM)
| # | Blocker | Status | Fix |
|---|---|---|---|
| 1 | CP0 sign-off on the registry format | ✅ **Done** (PR #17, agreed with defaults) | Only revisit if the money-side changes in model-spec.md are adopted. Leave a line in `to-asher.md`. |
| 2 | **No sample registry** (`data/` doesn't exist yet) | 🔴 **Open** | Hand-make `data/seed/sample/` in the agreed format: 2 plants, 2 lines each, ~6 machines, ~10 components, 3 KB parts, **1 Plant B spare**, 1 duplicate. ~20 min. Don't wait for Asher's full generator. |
| 3 | P1 research answers | 🟡 Running / to start | Paste all P1 prompts now. Build on the fallbacks in velocity-prompts.md and swap in real numbers as they land. |
| 4 | Real listings for 3 parts | 🟡 To do | By hand, not scraped (see model-spec §3). 3 parts × ≥ 3 listings + 1 part with none. |
| 5 | Inputs missing from the old backlog (discount rate, component costs, escrow rules, cost to serve, approval limits, transfer cost) | 🟡 Prompts #15–20 | Fallbacks unblock the code. |

**Rule:** nothing waits on research. Every input starts as a labeled assumption range, and research narrows it.

## To-do: now → CP1 (~7:30 PM)
1. ☐ **Paste the Velocity prompts** at once: P1 #1–6 and #15–17 (velocity-prompts.md). Reply "use defaults, go" if Velocity asks scoping questions.
2. ☐ **Sample data:** `data/seed/sample/` (blocker 2).
3. ☐ **Listings:** 3 parts × ≥ 3 real listings (`data/reference/listings.csv`) + 1 part with none. Cover different lifecycle statuses.
4. ☐ **`xray/sourcing.py`**: `listings` → `part_valuation` (25th/50th/75th percentile per condition) → `sourcing_recommendation` (shelf at **any** plant first → buy → migrate → monitor).
5. ☐ **`xray/valuation.py`**: `spof` → `capex_by_year` → `deal_adjustment` (formulas in model-spec §1).
6. ☐ **`xray/pricing.py`**: `plant_savings` + `price` (levers → price = capture % × auditable savings → payback).
7. ☐ All functions take **pandas DataFrames in, DataFrames out**, with no database code. Each has a pytest test on the sample data.
8. ☐ `./scripts/checkpoint.sh` → PR → merge to `main` **before 7:30**. Post a line in `to-asher.md`.

**The CP1 bar (keep it small):** all six tables come out on placeholder numbers, plus listings for 3 parts. Full coverage and benchmark ranges come after.

## To-do: CP1 → CP2 (~10:30 PM)
1. ☐ Swap the P1 + #15–17 answers into the inputs (with a `source` label on every value).
2. ☐ Run #18–20, plus P2 #7–11 and #14 from the [backlog](../../research/brandon-research-backlog.md).
3. ☐ Listings: 10–15 parts total (each lifecycle status at least once).
4. ☐ A sensitivity table: capture % (20/30/40) × savings (low/base/high) → price and payback. Put it in `docs/research/`.
5. ☐ Replace the hard-coded `PRICES` in `scripts/market_model.py` with the model's price range.
6. ☐ Deck: problem, market and business-model slides (7 and 8) using model output. Liquidity appendix (A3).
7. ☐ Log every Velocity answer in [velocity.md](../../research/velocity.md).

## After CP2 (only if time)
Listings to 25–30 parts · the escrow scenario on the deal slide · judge Q&A numbers in `docs/pitch/`.
