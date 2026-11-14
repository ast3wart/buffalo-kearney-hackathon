# Roles: split by thread, not by layer

Each person owns **one complete thread**: fake data → matching → insight → API endpoint → screen → their half of the brief → their part of the pitch. Both write Python *and* TypeScript from hour one, and neither waits on the other.

> **Decided Fri night:** 🛠 Warranty = **Brandon** · 💲 Spend = **Asher**

## 🛠 Warranty thread (owner: **Brandon**)
*The novel part: claims with no part number, and the early-warning spike. Higher risk, bigger demo moment.*
- [ ] `afterlife/generate_claims.py`: messy claims in each company's own vocabulary, spike planted **on one supplier's lots from a given PO** (via `build_supply`), driven by each company profile (Northwind has no spike)
- [ ] `afterlife/match_claims.py`: claim → causal part
- [ ] `afterlife/detect.py`: claim rates (raw + MIS) and spike alerts, **split by supplier using `build_supply`** so the alert names supplier + lot
- [ ] `brief.warranty_section()`: warranty recovery *review* ask (linked claims + evidence, never "caused")
- [ ] API: `/alerts`, `/claim-rates/{part_no}`
- [ ] Screen: `/alerts` (Early warning, with the claim-rate chart)
- [ ] Pitch: **the alert moment**
- [ ] Velocity prompts: 2, 4, 5

## 💲 Spend thread (owner: **Asher**)
*The track's core: BOM ↔ spend linking, true cost, spare-part markups. Lower risk, the base everything sits on.*
- [ ] `afterlife/generate_spend.py`: products, BOMs, builds, production and service purchase lines, info records, **`build_supply` with dual-sourced parts and varying mix**, Ironridge's **acquired plant**, all driven by each company profile (`afterlife/profiles.py`). Ironridge is written as a raw SAP extract automatically by `generate.py`
- [ ] `afterlife/match_spend.py`: purchase line → part (exact → info_record → spec_code → fuzzy), unit and price-unit conversion, `evidence` JSON. Hard cases: service text items and Ironridge's acquired plant
- [ ] `afterlife/cost.py`: build vs. lifecycle cost, spare-part markups
- [ ] `brief.pricing_section()`: price harmonization ask
- [ ] API: `/overview`, `/markups`
- [ ] Screen: `/` (Overview)
- [ ] Pitch: **the hook + $ impact**
- [ ] Velocity prompts: 3, 6, 7

## Shared (split as you go)
- [ ] App layout, navigation, visual style (tonight, together, 30 min)
- [ ] `match.normalize` + abbreviation list
- [ ] `evaluate.py` + `/accuracy` (each scores their own source_table)
- [ ] `/links` + Linking explorer screen
- [ ] `brief.make_brief` + `POST /brief` + Brief screen
- [ ] Velocity prompts 1 and 8, deck, two practice runs, submission

## Why the threads are balanced
The warranty thread has the harder matching and the flashiest result. The spend thread has more data to generate (spend has to exist before claims can reference the BOM) and owns the screen people see first. **Dependency:** the claims generator needs `bom` + `builds` from the spend generator. Until then, the warranty thread uses `data/sample/`, which has the same columns.

## How to choose
- Whoever is more excited about **messy text + statistics**, and wants the "wow" demo beat → 🛠 Warranty.
- Whoever is more excited about **data modeling + money**, and wants to open the pitch → 💲 Spend.
- Whoever is stronger at **frontend** should also take the lead on the shared app layout, whichever thread they own.

## Rules of thumb
- If you're blocked for more than 20 min, say so in chat.
- A change to the data contract or the API contract gets logged in [handoffs.md](handoffs.md).
- Before pushing: `pytest -q`, and `npx tsc --noEmit` in `web/`.
