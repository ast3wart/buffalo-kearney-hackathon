# Interfaces, demo portfolio and demo script (CP0, items 3–8)

**Status: ✅ DEFAULTS LOCKED (Sat ~6:15 PM); Brandon's model-spec changes adopted (~6:40 PM)** so both threads can build now.
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
| `xray/valuation.py` | `capex_by_year(reg, part_valuation, start_year=2027, years=5) -> capex_by_year` | low/high per plant, per year, per capex_type (`maintenance` by age vs life; `deferred` = past life or discontinued with no spare, years 0–2; `growth` only if typed in by the user) |
| | `spof(reg, sourcing_recommendation) -> spof` | line-stopping components + yearly downtime exposure = P(fail by age band) × **hours down** × $/h. Hours down depend on sourcing: shelf spare (here or a sister plant) = swap (+ transfer) time; none = lead time; discontinued with no listings = lead time + migration. Redundant machines score 0. |
| | `deal_adjustment(reg, capex_by_year, company_id, discount_rate) -> deal_adjustment` | deal lens only: price cut = PV(deferred CapEx, low); holdback = PV(high − low); no double counting |
| `xray/pricing.py` | `plant_savings(reg, sourcing_recommendation) -> plant_savings` | savings per plant per lever, low/base/high, one-time vs yearly |
| | `price(plant_savings, value_capture_pct=0.20) -> price` | price = capture % × **auditable recurring** savings (`in_price_base`); payback months; flags failed price checks (ROI ≥ 3×, payback ≤ 12 mo, approval ceiling, comparables) |

### Asher (machine thread)
| Module | Function | Returns |
|---|---|---|
| `xray/registry.py` | `load(db_path) -> dict[str, DataFrame]` | the registry tables |
| `scripts/seed.py` | `python scripts/seed.py data/seed/demo` → `demo.db` | |
| `xray/extract.py` | `read_photo(path, use_api=True) -> dict` | Claude vision reading of a label: manufacturer, part_no, series, serial, date_code, description, unclear fields, confidence. Cached by image hash in `data/cache/vision/` (committed), so the demo runs offline. `scripts/read_photos.py` reads all demo photos. |
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
| `GET /plants/{plant_id}/lines` | lines → machines (parts, worst health, replacement value) | `xray/health.py` |
| `GET /machines/{machine_id}` | machine + its parts with health | `xray/health.py` |
| `GET /components/{component_id}/health` | Working / Replace soon / Replace ASAP, life used %, order-by date, action, options (shelf first, then listings) | `xray/health.py` (engineering rules; Brandon's money overlay refines the action) |
| `POST /scan` | upload a photo → reading → KB match → new component row (the live demo) | `extract`, `matching` |

### Accepted additions from Brandon's model (Sat ~9 PM)
- **Optional arguments:** `capex_by_year(..., sourcing_recommendation=None, growth=None, as_of_year)`, `plant_savings(reg, rec, full_plant=False)` (`True` = whole-plant quote, shown on screen with an "extrapolated" label; `False` = the parts in the registry, shown in the drill-down), `deal_adjustment(..., discount_rate=None)`, plus `pricing.deal_fee_check`. All parameters live in `xray/params.py` with ranges and sources.
- **Extra output columns** (additive, nothing removed):
  - `part_valuation.n_low_trust`
  - `sourcing_recommendation`: plant_id, kb_id, spare_plant_id, transfer_cost_low/high, part_value_low/high
  - `spof`: plant_id, kb_id, action, annual_failure_rate_low/high, downtime_cost_per_hour_low/high
  - `plant_savings.basis`
  - `price`: price_per_plant_base, recurring_savings_base

  The app shows `basis`, `part_value_*` and the spof `why` in the evidence/financial views.

## 2. Demo portfolio (scale + planted problems)
**Knowledge base uses REAL manufacturer part numbers** (e.g. Allen-Bradley SLC 500 / PLC-5 / ControlLogix / PowerFlex, Siemens S7-300 / MICROMASTER) with their **actual lifecycle status and a source link for each** (Asher researches and cites). Plants, companies and the fund are fictional, and we say so.

**6 plants: two multi-plant manufacturers in one PE fund, plus an acquisition target.** All names are fictional, and we say so on screen.

| Plant | Company | Status | Role in the demo |
|---|---|---|---|
| **PA · Toledo, OH** | **Halvorsen Industrial Products** (`CO-HALVORSEN`): metal stamping and assemblies, 3 plants. **The main story.** | owned | **Deep dive:** registry, CapEx cliff, the part that stops a line |
| **PB · Fort Wayne, IN** | Halvorsen | owned | **Has the spare** Toledo needs on its shelf (sharing **within** a company) |
| **PC · Lima, OH** | Halvorsen | owned | Its shelf spare covers a Waukesha component (sharing **across** companies in the fund) |
| **PD · Waukesha, WI** | **Brightwater Packaging Systems** (`CO-BRIGHTWATER`): packaging machinery, 2 plants, an add-on of **Granite Ridge Capital** (`F-GRANITE`), which owns both companies | owned | The PE layer: fund-wide totals |
| **PF · Oshkosh, WI** | Brightwater | owned | Fund-wide totals |
| **PE · Rockford, IL** | **Tillman Machine Works** (`CO-TILLMAN`) | **target** | **Deal view:** "pay $X less" |

| | PA Toledo | PB Fort Wayne | PC Lima | PD Waukesha | PF Oshkosh | PE Rockford (target) |
|---|---|---|---|---|---|---|
| Employees | 220 | 180 | 140 | 130 | 100 | 90 |
| Annual revenue | $60–70M | $48–55M | $35–40M | $32–37M | $24–28M | $22–26M |
| Lines | 3 | 3 | 2 | 2 | 2 | 2 |
| Machines | ~16 | ~14 | ~10 | ~10 | ~8 | ~8 |
| Components | ~30 | ~25 | ~20 | ~18 | ~15 | ~15 |
| Line revenue per day | $60–90k | $50–75k | $55–80k | $50–75k | $40–60k | $35–55k |
| Contribution margin | 30–40% | 30–40% | 30–40% | 30–40% | 30–40% | 28–38% |
| Downtime cost per hour (derived) | ~$2–5k | ~$1.5–4k | ~$1.5–4k | ~$1.5–4k | ~$1–3k | ~$1–3k |
| Spares inventory value | Velocity #1 ($0.37M base for ~170 people), × headcount ÷ 170, × 0.6–1.6 | | | | | |
| Maintenance budget / yr | Velocity #1 ($1.05M base), × headcount ÷ 170, × 0.7–1.4 | | | | | |
| Carrying cost / yr | 12–30% of inventory (Velocity #2, economic; cash part only 3.5–8%) | | | | | |
| Rush premiums / yr | Velocity #3 (~$20k base), × headcount ÷ 170, × 0.5–2.5 | | | | | |
| Deal value (deal view only) | — | — | — | — | — | $28–34M |

Totals: **~66 machines, ~123 components**. The KB (~30 real parts) is reused across plants, which is realistic, because plants share brands.

All dollar figures are **placeholders (Brandon's to refine from research)**, labeled as such in `plant_financials.source`. **This table is the demo scale.** Brandon's [model-spec §4](../plan/financials/model-spec.md) anchors point here. Downtime $/h is **derived**: revenue_per_day ÷ operating_hours_per_day (16 h) × contribution margin (+ idle labor). Plant-level money levers are **scaled by the share of the plant the register covers** (model-spec §2).

**Planted problems (the answer key):**
1. **~15–20 discontinued or end-of-life controllers/drives/HMIs** across the 6 plants, plus active parts (mixed brands).
2. **Line-stopping single point of failure:** `PA-L2` runs on a discontinued drive with **no spare at Plant A** and long lead time.
3. **The portfolio moment:** **Plant B has 2 of that drive on its shelf**, under a different description (so matching has to find it). **A second match:** a Lima (PC, Halvorsen) shelf spare covers a Waukesha (PD, Brightwater) component (sharing across companies in the fund).
4. **Duplicates:** the same part stocked twice at Plant A under two names (plus one at PC).
5. **One part with zero listings** → the alternatives path (successor / similar part).
6. **A CapEx cliff that peaks in 2027–2028**, driven by the discontinued controllers.
6b. **Target PE (Tillman, Rockford)** has deferred catch-up CapEx (discontinued controllers past life, no spares), which drives the deal view.
7. **A few low-confidence readings** (blurry/worn photos) → `needs_review`.

**Model output (Brandon's money model on this data, Sat ~9 PM; these replace the earlier targets):**
- 5-yr CapEx (control parts + migration engineering): Toledo ~$70–350k; fund (5 owned plants) up to ~$0.85M
- whole-plant price (extrapolated, 20% of auditable savings): Toledo ~$10k/yr (range $1.8–35k), others ~$5–6k
- Tillman deal view: deferred CapEx $73–230k → pay ~$73k less + ~$130k holdback
- bigger, defensible numbers come from filling `kb.migration_cost_*` per controller family (Brandon, research), not from inflating the demo plants

## 3. Demo script (~3 min) + headline numbers
1. **"Halvorsen Industrial runs 3 plants. Its owner, Granite Ridge Capital, also owns Brightwater (2 plants)."** Portfolio page tiles: plants, machines, components scanned, **% end-of-life or discontinued**, CapEx 5-yr, idle spares.
2. **Plant A registry:** lines → machines → components. Click one → evidence drawer (photo, reading, KB source).
3. **CapEx cliff:** low/high by year → click a bar → the components driving it.
4. **Single point of failure:** "Line 2 stops if this discontinued drive fails, and the manufacturer doesn't make it anymore." **Exposure $/yr.**
5. **Sourcing:** "**Fort Wayne already has 2 on the shelf.**" Then the listings range (≥ 3 listings) and buy / migrate / monitor. (The portfolio page also shows the Lima → Waukesha match across companies.)
6. **Savings + price per plant** (from Brandon's model) + **accuracy tile** (precision/recall on the answer key).
7. **Live photo** of a real nameplate → appears in the registry. Close with the deal view: "**Granite Ridge is about to buy Tillman Machine Works. The same scan prices the deal**" → **pay $X less**.

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
| ~7:30 PM | **CP1:** Asher: `demo.db` seeded (6 plants) + photos → registry. Brandon: `pricing.py` + `sourcing.py` run on placeholders. |
| ~10:30 PM | **CP2:** end to end, first accuracy number, deck outline |
| ~1 AM | **CP3:** feature freeze |
| ~7 AM | **CP4:** rehearse; submit by 8:30 |
