# Plan updates: what changed, why, and what it costs

Running log of plan changes after the original plan (`docs/archive/track-decision.md`). The newest update goes at the top. Every change is either **decided** (already applied in the repo) or **proposed** (waiting for a checkpoint).

🛠 = Brandon (Warranty) · 💲 = Asher (Spend)

---

## Update 3 · Sat Nov 14, ~00:30 · CP0 addendum (PROPOSED, decide at CP1)
Detail and per-item specs: [../research/cp0-proposal.md, addendum items 10–20](../research/cp0-proposal.md#cp0-addendum-items-1020-proposed-decide-at-cp1-sat-900-am).

### Where things stand (branch status)
- **CP0 v2 lives on `test-data-batch`, not `main`.** Main reverted it in `ea5d00d` ("work moved to test-data-batch branch"). This proposal is on branch `plan/cp0-additions`, based on `test-data-batch`.
- **Decide at CP1** when `test-data-batch` merges to main. Until then, both threads should branch from `test-data-batch`, or they'll build against the old contract.
- Code status: the loader, run, check, profiles, taxonomy, `/health` and `/companies` work. Generators, matchers, detect, cost, evaluate and brief are all still placeholders.

### What the review found
CP0 already made the big call: **3 companies** (Prairie tune, Ironridge holdout, Northwind holdout + no-spike control), and **months-in-service** detection. That's the right structure. Four gaps would still let a sharp judge poke holes:

| Gap | Where it shows | Risk in the pitch |
|---|---|---|
| The three "industries" share one vocabulary | `taxonomy.py` (one failure-code list), `match.ABBREVIATIONS` (vehicle shorthand hardcoded), profiles that differ only by weights | "Your HVAC company has hydraulic leak codes." The generalization claim falls apart |
| Supplier attribution is trivial | One production supplier per part | "Which supplier pays?" answers itself, so the brief proves nothing |
| Production matching looks unnecessary to an SAP expert | CP0 #2 put MATNR on 85% of production lines | "If SAP already has the part number, why match?" |
| Links are a bare `part_no + confidence` | `links` output | "Why should a supplier accept that?" No evidence trail |

### The proposed fixes, ranked by when they must happen
**Tier 1: decide and apply at CP1.** These are cheap now and expensive once the generators exist.

| # | Change | Owner | Effort | Reasoning |
|---|---|---|---|---|
| 10 | Each company gets its own vocabulary: failure-code subset + extras, `abbreviations.csv`, part-number and description style knobs | both (generators), shared (taxonomy, normalize) | ~1 h total | Real generalization needs different *words*, not different *weights*. Abbreviations are client data, not code |
| 11 | No-literals test | either | 15 min | Turns "not overfit" into an enforced fact. A one-line pitch claim |
| 12 | Ironridge acquired plant (`P-TX2`, legacy numbering) | 💲 | 30 min of profile knobs | Points the matching effort at the case that actually happens after acquisitions, and adds a plant-vs-plant price lever |
| 13 | Dual-sourced spike part + `build_supply.csv` | 💲 makes, 🛠 uses | ~1 h split | Makes "which supplier, which lot" a real inference. The brief can name a PO |
| 14 | `links` gains `evidence`, `source_system`, `run_id`; `decisions` schema reserved | both | 20 min (contract) | The link table is the product's main export; evidence is what makes a recovery claim stick |

**Tier 2: inside each thread on Saturday.** No contract change.
- #15 SAP-column adapter (💲, ~30 lines)
- #16 AI in three narrow places (💲 description parsing, 🛠 tie-break, shared brief)
- #17 run record and confidence thresholds (shared)
- #18 evals as pytest (each owner)

**Tier 3: only after CP5 is green.**
- #19 review-queue buttons
- #20 is deck-only positioning, done Saturday night with the deck

### Why these and not others
- **The goal hasn't changed:** one closed loop judges remember. A shared part fails across products → it traces to one supplier's lot → recovery claim plus price harmonization → one dollar figure, with evidence at every step. Every Tier 1 item strengthens a link in that chain. None adds a new screen.
- **Rules decide, the model proposes.** This mirrors Kearney's own direction (Beroe MAX describes a "neurosymbolic" design). It also keeps the demo deterministic: AI runs in the pipeline, gets cached, and is measured against the answer key. It never runs live, except for the brief, which has a template fallback.
- **No LangGraph or agent framework.** It's a fixed batch pipeline with 2–3 model calls. A framework adds state, debugging time and a dependency, with nothing visible to show for it. What makes it durable is data contracts, re-runnable steps, versioned outputs and evals. None of that depends on an orchestration library.
- **No live connectors.** SAP / Sievo / Tavant connections can't be verified this weekend, and judges don't expect them. *SAP-shaped data plus an adapter* gives 90% of the credibility for 5% of the cost.
- **Splink later, not now.** It fits well (record linkage on DuckDB, per-signal weights). But it's a new dependency, and it needs parsed attribute columns first. It goes on the path-to-production slide.

### Impact on each thread
| | 🛠 Warranty (Brandon) | 💲 Spend (Asher) |
|---|---|---|
| New in generator | Per-company failure-code subset + claim-text vocabulary; spike only on one supplier's lots from a given PO | Per-company PN/description style, `abbreviations.csv`, Ironridge acquired plant, dual-sourced spike part, `build_supply.csv` |
| New in logic | `detect.py` splits rates by supplier using `build_supply` shares; tie-break via Claude (Tier 2) | Matcher steps `info_record` → `spec_code` → fuzzy; writes `evidence`; description parsing via Claude (Tier 2); SAP adapter (Tier 2) |
| New tests | Spike caught on 3 seeds, zero Northwind alerts, alert names the right supplier | Accuracy floors per company, including the acquired plant separately |
| Shared | `normalize()` reads abbreviations from the tables; `links` v2; `runs` table; brief number-check test | |

### Impact on schedule
| When | Change |
|---|---|
| CP1 (Sat 9:00) | Grows from 15 to **30 min**: decide items 10–14, apply them as one commit, and agree when `test-data-batch` merges to main |
| CP2 (Sat ~11:30) | Handoff now also includes `build_supply.csv` and Northwind's HVAC vocabulary. 🛠 checks the dual-source split is usable |
| CP3 (Sat 12:30) | Set the accuracy floors in `test_accuracy.py` from the first real numbers |
| CP5 (Sat 6:00) | Adds: "rules only vs. rules + Claude" numbers locked, and alert names the planted supplier and PO |
| Cut if behind | In order: #19 buttons → #15 SAP adapter → Claude description parsing (keep the tie-break) → Northwind's extra failure codes (keep its abbreviations) |

### Pitch and demo changes
- **Demo beat 3:05 ("Generalizes")** gets stronger:
  - Ironridge "arrives as an SAP extract"
  - its spike is caught *and attributed to the right supplier's lot*
  - Northwind shows zero alerts
  - accuracy table: rules vs. rules + Claude, tuned vs. holdout
- **New judge Q&A answers:**
  - *"Why match if SAP has MATNR?"* → acquired plants, service text items, and claims.
  - *"How do you know it's that supplier?"* → `build_supply` lots.
  - *"Is the AI making numbers up?"* → a test checks every number in the brief against the results.
- **New slide:** "Afterlife writes the link table that Sievo, Tavant and SAP each need". Compatible with Power BI and Spend.Pro, not integrated.

### Open questions for CP1
- [ ] When does `test-data-batch` merge to main?
- [ ] Northwind: add HVAC categories (`compressor`, `refrigerant_component`, `motor`), or map onto the existing 21 (`cooling`, `electrical`)? Adding them is more convincing but touches `taxonomy.py`.
- [ ] Which company is the SAP-column one? Proposal: Ironridge.
- [ ] Who has an Anthropic API key? Which model ID do we pin?
- [ ] Ask mentors: can Kearney give sandbox access to Spend.Pro, or sample exports in its format?

### Clarifications
- *"Velocity"* is the hackathon's required Growth Signals research workspace (`docs/research/velocity.md`). It is not a library or a framework.
- One research note flagged the Spend section as "half copied from Warranty". That duplication only existed in a pasted summary (`plan-1.0.1.md`), not in the repo. `docs/team/roles.md` is correct.

---

## Update 2 · Fri Nov 13, ~23:45 · CP0 contract lock (DECIDED)
Commit `25dfc27` on `test-data-batch`. Summary in [../research/cp0-proposal.md](../research/cp0-proposal.md) and the `docs/team/checkpoints.md` CP0 note.
- Data contract v2:
  - `part_no` and `price_unit` on spend lines
  - `info_records`, `dataset_info`
  - 12 `SYSTEM-MODE` failure codes and 21 categories in `afterlife/taxonomy.py`
- **3 companies instead of 1** (`afterlife/profiles.py`):
  - Prairie (tune), Ironridge (holdout), Northwind (holdout, no-spike control)
  - each in `data/generated/<company_id>/`
  - API takes `?company=`
- Spikes: shown two ways (raw by build month, and months in service); alerts use the months-in-service window of 3.
- Window: builds Jan 2025 – Sep 2026, data as of Oct 31 2026.
- App: clean industrial style, nav, company switcher, screen stubs.
- **Why:** months-in-service fixes a real flaw (recent builds look healthy just because they're young). Three companies with a holdout and a control answer the question "is it tuned to your own fake data?"

## Update 1 · Fri Nov 13, evening · Afterlife chosen, stack switched (DECIDED)
- Track pick moved from a plain BOM cost rollup to **Afterlife**:
  - BOMs ↔ production spend ↔ spare spend ↔ warranty claims
  - early warning across products
  - supplier brief
- **Why:** most teams will build the cost rollup. The money that falls between teams is in spares and warranty.
- Stack: Streamlit → **FastAPI + Next.js + DuckDB**, with everything precomputed into `results.duckdb`.
- Work split into threads: 🛠 Warranty = Brandon, 💲 Spend = Asher.
