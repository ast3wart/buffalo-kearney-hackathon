# Interfaces, demo portfolio and demo script (CP0, items 3–8)

**Status: ✅ DEFAULTS LOCKED (Sat ~6:15 PM)** so both threads can build now.
- Brandon owns the money-side items (§1 function behavior, §2 dollar scale, §3 headline numbers). He may revise them, as long as he leaves a line in Asher's inbox.
- Data format: [registry-format.md](registry-format.md).
- **We're building a DEMO.** Build only what the demo needs.

---

## 1. How the code connects
### Rule
**Brandon's functions are pure.** They take pandas DataFrames, return DataFrames, and never read files, the database or globals. That way they run in a notebook, in tests, and behind the API, all the same way.

The input is **`reg: dict[str, pd.DataFrame]`**, the registry tables by name from [registry-format §6](registry-format.md): `plant`, `plant_financials`, `line`, `machine`, `component`, `spare_stock`, `kb_entry`, `listing`, `alternative`, … Asher's `xray/registry.py` builds it from SQLite: `reg = registry.load("demo.db")`. Money columns are always `_low` / `_high`.

### Brandon (money thread)
| Module | Function | Returns (columns in registry-format §7) |
|---|---|---|
| `xray/sourcing.py` | `value_parts(reg) -> part_valuation` | price range per part and condition, from listings (≥ 3 → high confidence) |
| | `recommend_sourcing(reg, part_valuation) -> sourcing_recommendation` | **shelf at any plant first**, then the best listing; `alt_id` if none |
| `xray/valuation.py` | `capex_by_year(reg, part_valuation, start_year=2027, years=5) -> capex_by_year` | low/high per plant, per year, per capex_type |
| | `spof(reg) -> spof` | line-stopping components + yearly downtime exposure (failure prob × hours × $/h) |
| | `deal_adjustment(reg, capex_by_year, company_id) -> deal_adjustment` | deal lens only: price reduction + holdback (no double counting) |
| `xray/pricing.py` | `plant_savings(reg, sourcing_recommendation) -> plant_savings` | savings per plant per lever, low/base/high, one-time vs yearly |
| | `price(plant_savings, value_capture_pct=0.30) -> price` | price per plant, customer payback months |

### Asher (machine thread)
| Module | Function | Returns |
|---|---|---|
| `xray/registry.py` | `load(db_path) -> dict[str, DataFrame]` | the registry tables |
| `scripts/seed.py` | `python scripts/seed.py data/seed/demo` → `demo.db` | |
| `xray/extract.py` | `read_photo(path) -> dict` | vision reading: make, model, part_no, serial, year, components seen, confidence (cached by image hash) |
| `xray/matching.py` | `Matcher(kb descriptions).match(text)` (exists) | kb index, confidence, evidence |
| `xray/evaluate.py` | `score(...)` (exists) → `accuracy` | precision/recall + confidence interval |

### API routes (Asher builds them; they call Brandon's functions)
| Route | Returns | Uses |
|---|---|---|
| `GET /health` | ok | |
| `GET /portfolio` | fund, companies, plants + tiles (machines, components, % end-of-life/discontinued, CapEx 5-yr range, single points of failure, idle spare value) | all |
| `GET /plants/{plant_id}/registry` | tree: lines → machines → components (status, age, confidence, needs_review) | registry |
| `GET /components/{component_id}/evidence` | photo, reading, KB source, listings, reviewer | registry |
| `GET /plants/{plant_id}/capex` | CapEx cliff | `capex_by_year` |
| `GET /plants/{plant_id}/spof` | line-stopping parts + exposure | `spof` |
| `GET /plants/{plant_id}/sourcing` | per at-risk part: shelf spare (any plant), listings, valuation, action | `value_parts`, `recommend_sourcing` |
| `GET /plants/{plant_id}/savings` | savings per lever + price per plant | `plant_savings`, `price` |
| `GET /companies/{company_id}/deal` | deal lens: "pay $X less" + holdback | `deal_adjustment` |
| `GET /accuracy` | precision/recall vs answer key | `evaluate` |
| `POST /scan` | upload a photo → reading → KB match → new component row (the live demo) | `extract`, `matching` |

## 2. Demo portfolio (scale + planted problems)
**Knowledge base uses REAL manufacturer part numbers** (e.g. Allen-Bradley SLC 500 / PLC-5 / ControlLogix / PowerFlex, Siemens S7-300 / MICROMASTER) with their **actual lifecycle status and a source link for each** (Asher researches and cites). Plants, companies and the fund are fictional, and we say so.

| | Plant A (`PA`) | Plant B (`PB`) |
|---|---|---|
| Owner | Fund X (`F-FUNDX`) → company `CO-RIVERTON` | Fund X → company `CO-LAKESIDE` (an add-on) |
| Employees | 220 | 150 |
| Annual revenue | $60–70M | $40–45M |
| Lines | 3 (`PA-L1..L3`) | 3 (`PB-L1..L3`) |
| Machines | ~16 | ~14 |
| Components | ~30 | ~25 |
| Line revenue per day | $60–90k | $40–60k |
| Contribution margin | 30–40% | 30–40% |
| Downtime cost per hour (lost contribution + idle labor) | ~$2–5k | ~$1.5–3.5k |
| Spares inventory value | $1.8–2.2M | $1.2–1.5M |
| Maintenance budget / yr | $4.5–5.5M | $3.0–3.5M |
| Carrying cost / yr | 15–25% of inventory | 15–25% |
| Rush premiums / yr | $40–80k | $25–50k |

All dollar figures are **placeholders (Brandon's to refine from research)**, labeled as such in `plant_financials.source`.

**Planted problems (the answer key):**
1. **6–8 discontinued or end-of-life controllers/drives/HMIs** across both plants, plus some active parts (mixed brands).
2. **Line-stopping single point of failure:** `PA-L2` runs on a discontinued drive with **no spare at Plant A** and long lead time.
3. **The portfolio moment:** **Plant B has 2 of that drive on its shelf**, under a different description (so matching has to find it).
4. **A duplicate:** the same part stocked twice at Plant A under two names.
5. **One part with zero listings** → the alternatives path (successor / similar part).
6. **A CapEx cliff that peaks in 2027–2028**, driven by the discontinued controllers.
7. **A few low-confidence readings** (blurry/worn photos) → `needs_review`.

**Target magnitudes** (so the headline numbers land; Brandon checks they're plausible):
- PA 5-yr CapEx **~$1.5–3M**
- top single point of failure exposure **~$100–300k/yr**
- savings per plant **~$20–40k/yr + ~$150–300k one-time**
- deal lens on CO-RIVERTON **~$1–2M** price reduction

## 3. Demo script (~3 min) + headline numbers
1. **"Fund X owns Plant A and Plant B."** Portfolio page tiles: plants, machines, components scanned, **% end-of-life or discontinued**.
2. **Plant A registry:** lines → machines → components. Click one → evidence drawer (photo, reading, KB source).
3. **CapEx cliff:** low/high by year → click a bar → the components driving it.
4. **Single point of failure:** "Line 2 stops if this discontinued drive fails. Lead time 20+ weeks." **Exposure $/yr.**
5. **Sourcing:** "**Plant B already has 2 on the shelf.**" Then the listings range (≥ 3 listings) and buy / migrate / monitor.
6. **Savings + price per plant** (from Brandon's model) + **accuracy tile** (precision/recall on the answer key).
7. **Live photo** of a real nameplate → appears in the registry. Close with the deal lens: "**and when they buy their next plant, the same scan prices the deal**" → **pay $X less**.

**Headline numbers on screen (4 + 1):**
1. **5-yr CapEx** (range)
2. **top single-point-of-failure exposure per year**
3. **savings per plant per year** (+ one-time)
4. **accuracy %**
5. **deal lens:** pay $X less

## 4. Strategy (confirmed)
- Own plants are the main way in. Acquisitions and pre-exit scans are other ways in.
- Customers are multi-plant manufacturers + PE.
- The liquidity angle stays.
- Prices come from Brandon's model.

Full detail: [roadmap](../plan/roadmap-equipment-xray.md) and AGENTS.md.

## 5. Workflow (confirmed)
- Each person works on their own branch (`asher/<topic>`, `brandon/<topic>`). Merge to `main` at checkpoints through a PR.
- **Shared files need a heads-up in the other person's inbox *before* you change them:** `registry-format.md`, this file, `requirements.txt`, `api/main.py` route shapes, `xray/registry.py`.
- `./scripts/checkpoint.sh` must be green before every merge.

## 6. Checkpoints (confirmed)
| Time | Checkpoint |
|---|---|
| ~7:30 PM | **CP1:** Asher: `demo.db` seeded + photos → registry. Brandon: `pricing.py` + `sourcing.py` run on placeholders. |
| ~10:30 PM | **CP2:** end to end, first accuracy number, deck outline |
| ~1 AM | **CP3:** feature freeze |
| ~7 AM | **CP4:** rehearse; submit by 8:30 |
