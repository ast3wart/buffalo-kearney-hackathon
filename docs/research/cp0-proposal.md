# CP0 proposal: contract changes from research

**Status: DECIDED at CP0 (Fri Nov 13, Asher + Brandon). Applied** to `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/check.py`, `scripts/make_sample.py`.

| # | Decision |
|---|---|
| 1 | ✅ **Both views:** raw claims-per-1,000 by build month shown as the intuitive chart, and the **MIS-window method drives the alerts**. Side by side in the app to show why raw misleads |
| 2–4 | ✅ `part_no` on spend lines, ✅ `info_records.csv`, ✅ `price_unit` |
| 5 | ✅ 12 `SYSTEM-MODE` failure codes |
| 6 | ✅ All 21 categories |
| 7 | ✅ Builds Jan 2025 – Sep 2026, data as of Oct 31 2026, 24-month warranty, MIS window 3 |
| 8–9 | ❌ Claim line items and BOM uom stay out (Q&A "next step") |
| API | ✅ Shapes accepted as drafted (`/claim-rates` returns both views) |
| Style | ✅ Clean industrial: light neutral, teal accent, red alerts, mono part numbers |
| Branches | ✅ `spend/...` and `warranty/...` |
| Companies | ✅ **Added after CP0: 3 companies, not 1** (`afterlife/profiles.py`). Prairie (tune), Ironridge (holdout), Northwind (holdout, no-spike control). One folder per company, same contract |

> **New: [CP0 addendum](#cp0-addendum-items-1020-proposed-decide-at-cp1-sat-900-am)** (items 10–20, *proposed*, decide at CP1). These items build on the decisions above: making the three companies genuinely different, SAP-shaped inputs, real supplier attribution, evidence on every link, and where AI fits. Reasoning and plan impact: [../plan/plan-updates.md](../plan/plan-updates.md).

🛠 = Brandon (Warranty) · 💲 = Asher (Spend)

## TL;DR
| # | Change | Who | Why it matters | Recommend |
|---|---|---|---|---|
| 1 | **Measure spikes by months-in-service, not raw claims by build month** | 🛠 | Our current method would flag a fake drop for recent builds and could hide the real spike. This is the one real flaw | ✅ must |
| 2 | Add a nullable `part_no` to spend lines (SAP "material number") | 💲 | Real POs carry the internal part number *most* of the time. The real gap is the free-text lines without one | ✅ |
| 3 | Add `info_records.csv` (part ↔ supplier part number crosswalk) | 💲 | That's how SAP links supplier PNs to internal parts. Production buys have it, service buys mostly don't | ✅ |
| 4 | Add `price_unit` to spend lines | 💲 | SAP prices are "per N units". A classic trap, cheap to add | ✅ |
| 5 | Failure codes = system + failure **mode** (ISO 14224 style) | 🛠 | Modes describe the symptom, not the part, which is *why* claims don't name a part | ✅ |
| 6 | Lock the part **category list** (below) | both | `failure_codes.likely_categories` depends on `part_master.category` | ✅ must |
| 7 | Add `dataset_info.csv` (`data_as_of`, company, currency) | both | Needed for #1, and shown in the app header | ✅ |
| 8 | Claim line items (SAP WTY style: parts / labor / sublet) | 🛠 | More realistic, but costs time | ❌ keep flat for MVP |
| 9 | BOM `uom` column | 💲 | Only matters for hoses/wire sold by length | ❌ skip (all EA) |

---

## 1. Months in service (the real flaw) 🛠
**What we found.** Warranty analysts group units by build month, but they compare claim rates **at the same months in service (MIS)**. A unit built last month has had one month to fail, while a unit built a year ago has had twelve. Counting raw claims per build month makes recent builds look artificially healthy. One quality forum notes build-month counts can take 18+ months to stabilize. The standard view is a build-period × failure-period (or × MIS) matrix, with alerts on cells well above expectation. SAS Field Quality Analytics' early-warning analysis works this way.

**What breaks in our plan.** `detect.py` was going to compare claims per 1,000 by build month against a baseline median. With a realistic generator, recent build months would show *fewer* claims just because they're young. That would cover up exactly the "since the March build" spike we want to show.

**Proposed fix (still simple):**
- `MIS = months between build_month and failure_date`
- Compare **claims within the first K months in service per 1,000 built** (K = 3), only for build months with at least K months of exposure as of `data_as_of`.
- Optionally show a small build-month × MIS heatmap. Judges from a quality background will recognize it immediately.
- Contract impact: no new claim columns. Needs `data_as_of` (#7).
- Generator impact (🛠): claims spread across MIS with a hazard curve (more early-life failures), and stop at `data_as_of`, so recent builds are genuinely immature.

**Pitch line:** "We compare like with like: claims in the first 3 months of service per 1,000 built, the way field-quality teams do it."

## 2. `part_no` on spend lines 💲
**What we found.** In SAP, a PO line *can* reference a material number. When it doesn't (a "text item"), the buyer types a short description and a material group by hand, the Material column is blank, and spend reports suffer because people pick material groups loosely. That free text is the main classification problem.

**Proposal:** add `part_no` (nullable) to `production_spend` and `service_spend`.
- Production: filled for about 85% of lines (stocked parts bought against the part number).
- Service: filled for about 15% (distributor buys are mostly free-text).

**Why it's better:** it makes the story honest. Production spend mostly ties already, and the *gap* is service spend plus claims, which is exactly Afterlife's pitch. The spend matcher's job becomes: trust `part_no` when present (check it), match the rest.

## 3. `info_records.csv` 💲
**What we found.** SAP keeps the supplier's own part number on the purchasing info record (EINA, field IDNLF, "Material Number Used by Vendor"), and it can flow into the PO line. That's the real-world crosswalk.

**Proposal:** a new table `info_records.csv`: `part_no, supplier_id, supplier_pn`. Present for production suppliers, **missing for the service distributor**. The matcher uses it as a high-confidence step.

## 4. `price_unit` 💲
**What we found.** SAP stores the net price (NETPR) per a **price unit** (PEINH), for example $58.90 *per 10*. The formula (value ≈ NETPR / PEINH × qty) is the standard interpretation, but our search didn't find official confirmation, so treat it as convention.

**Proposal:** add `price_unit` (int, default 1) to both spend tables. Price per EA = `unit_price / price_unit / pack_size(uom)`. Plant a few lines with `price_unit = 100` so a naive average breaks visibly. That's a nice "we know the traps" detail.

## 5. Failure codes as modes 🛠
**What we found.** ISO 14224 (the reliability-data standard) separates the **failure mode**, meaning the observed effect (external leakage `ELP`, vibration `VIB`, fail to start `FTS`, overheating `OHE`), from the **cause**. A claim records what the technician saw, not which part's supplier caused it. That's *why* the causal part is so often missing. We confirmed those four mode codes from secondary sources, not the standard itself.

**Proposal:** `failure_code = <SYSTEM>-<MODE>`, e.g. `HYD-ELP` (hydraulic external leak), `DRV-VIB`, `ELE-FTS`, `ENG-OHE`, `BRK-NOI`. Columns are unchanged. SAP's warranty module also has a "part that causes damage" flag on claim items, which is what our `causal_part_no` stands in for.

| failure_code | system | mode | likely_categories |
|---|---|---|---|
| HYD-ELP | hydraulic | external leakage | seal;hose;fitting;hydraulic_component |
| HYD-LOP | hydraulic | low output / pressure | hydraulic_component;seal;filter |
| DRV-VIB | drivetrain | vibration | bearing;belt;gear;wheel_tire |
| DRV-NOI | drivetrain | noise | bearing;gear;belt |
| ENG-ELP | engine | external leakage (oil) | filter;seal;gasket |
| ENG-OHE | engine | overheating | cooling;belt;sensor |
| ELE-FTS | electrical | fail to start | electrical;battery;fuel;sensor |
| ELE-INT | electrical | intermittent operation | electrical;sensor;harness |
| BRK-NOI | brakes | noise | brake |
| BRK-DEG | brakes | degraded performance | brake;hydraulic_component |
| BDY-STR | body | structural / cracking | structural;fastener;plastic |
| LGT-FTF | lighting | fails to function | lighting;harness |

## 6. Category list (lock it tonight) both
Owned by 💲 in `part_master.category`, consumed by 🛠 in `failure_codes.likely_categories`. Proposed 21:

`bearing, seal, gasket, hose, fitting, hydraulic_component, filter, belt, gear, wheel_tire, brake, cooling, fuel, electrical, harness, sensor, battery, lighting, fastener, structural, plastic`

Cut any we won't generate. `afterlife/check.py` already flags failure-code categories that don't exist in `part_master`.

We didn't map these to UNSPSC codes. We couldn't verify the official class codes, so don't put them on a slide.

## 7. `dataset_info.csv` both
`key,value` rows: `company_name` (Prairie Utility Vehicles), `data_as_of` (e.g. 2026-10-31), `currency` (USD), `warranty_months` (24). Read by `detect.py`, shown in the app header.

## 8–9. Rejected for MVP
- **Claim line items** (SAP warranty claims have item types: MAT = parts, FR = labor, SUBL = sublet/external). It's realistic, but it doubles 🛠's generator and matcher work. Mention it in Q&A as "the next step".
- **BOM unit of measure.** All quantities stay in EA.

---

## Draft API shapes (for CP0 sign-off)
```jsonc
// GET /overview  💲
{
  "company": "Prairie Utility Vehicles", "data_as_of": "2026-10-31",
  "coverage": { "production_spend_pct": 0.97, "service_spend_pct": 0.81, "claims_pct": 0.74 },
  "products": [
    { "product_id": "UV-400", "build_cost": 2140.5, "spares_per_unit": 96.2,
      "warranty_per_unit": 118.4, "lifecycle_cost": 2355.1 }
  ],
  "spare_overspend_usd": 412000
}

// GET /alerts  🛠
[
  { "part_no": "200-1180-01", "description": "SEAL KIT,HYD CYL,40MM BORE",
    "supplier_id": "S-022", "supplier_name": "Keystone Seal Works",
    "products_affected": ["UV-400", "UV-600", "TR-250"],
    "start_build_month": "2026-04", "mis_window": 3,
    "baseline_rate": 4.1, "current_rate": 14.6, "ratio": 3.6,   // claims per 1,000 built within 3 MIS
    "claims": 29, "exposure_usd": 2100000, "recoverable_usd": 1450000 }
]

// GET /claim-rates/{part_no}  🛠  (chart + optional heatmap)
{ "mis_window": 3,
  "by_build_month": [ { "build_month": "2026-03", "units": 640, "claims": 3, "rate": 4.7, "mature": true, "is_spike": false } ],
  "heatmap": [ { "build_month": "2026-03", "mis": 1, "cum_rate": 1.6 } ] }
```

## Pitch numbers from this research (for the deck)
From Warranty Week's analyses of US companies. Treat them as indicative, since they vary by year and company:
- Suppliers paid **about 10%** of industry warranty costs in 2019, while a "fair share" could be **as high as 37%**. That gap is the recovery opportunity Afterlife goes after.
- 2017: the OEM/supplier split was about **84% / 16%**.
- Big recoveries do happen: GM recovered **at least 90%** of the Chevy Bolt battery recall cost from its supplier.
- → Use a **conservative capture rate** (e.g. 25–50% of attributable cost) for `recoverable_usd`, and say so.

---

## CP0 addendum: items 10–20 (PROPOSED, decide at CP1, Sat 9:00 AM)

**Status: PROPOSAL.** Nothing here is applied yet. Mark each item ✅ / ❌ at CP1. Anything that changes the contract (items 10, 12, 13, 14) goes into `data-contract.md`, `check.py` `CONTRACT`, and `make_sample.py` in **one commit**, the same way as CP0.
**Inputs:** a review of the CP0 v2 branch, plus two research notes (`Afterlife Connectors, AI Approach & Plan Fixes`, `other-differentiating-notes`). Why each item exists and what it costs: [../plan/plan-updates.md](../plan/plan-updates.md).

### TL;DR
| # | Change | Who | Why it matters | Tier |
|---|---|---|---|---|
| 10 | **Each company gets its own vocabulary**, not just different weights. Abbreviations move out of `match.py` into data | both | Today all 3 companies share one category list, one failure-code list, and one hardcoded abbreviation list. "Three industries" is really one industry three times | **1 · contract** |
| 11 | **No-literals rule + test:** no company IDs, industry words, or part numbers hardcoded in `afterlife/` logic | both | Turns "not overfit" from a claim into something a test enforces | **1 · 15 min** |
| 12 | **Ironridge = the "acquired plant" company:** a second plant on a legacy part-numbering scheme | 💲 | Answers the SAP-savvy judge: "POs already carry MATNR, so why match?" | **1 · contract-lite** |
| 13 | **Real supplier attribution:** spike part is dual-sourced, plus `build_supply.csv` tying build months to supplier lots | 💲 makes, 🛠 uses | Without it, "which supplier?" answers itself (one part = one supplier) | **1 · contract** |
| 14 | **Link table v2:** add `evidence`, `source_system`, `run_id` to `links` | both | Every link shows *why*. A supplier won't pay on "the AI said so" | **1 · contract** |
| 15 | **SAP-column adapter:** raw extracts use real SAP field names, and a mapping renames them into our contract | 💲 | "Point us at a standard SAP extract" without building a connector | 2 |
| 16 | **AI in three narrow places**, cached and measured: description parsing, claim tie-break, brief | 💲 / 🛠 / shared | Rules decide, the model proposes and explains (Kearney's own "neurosymbolic" framing). Show accuracy *with vs. without* Claude | 2 |
| 17 | **Run record + confidence thresholds per use** | shared | Any number traces to a run. Recovery uses only high-precision links | 2 |
| 18 | **Evals as pytest** (accuracy floors, spike caught on several seeds, zero alerts for Northwind, brief numbers must exist in results) | each their own | Quality can't silently regress Saturday night | 2 |
| 19 | **Review queue:** accept/reject buttons on Linking explorer → `decisions` overrides | shared | Human oversight, and a system that improves with use | 3 · stretch |
| 20 | **Outputs positioning:** link table export "for Sievo / Tavant / SAP info records", compatible with Power BI and Spend.Pro | pitch | Shows where Afterlife fits in a client's existing tools | 3 · deck only |

Tier 1 = decide and apply at CP1 (cheap now, expensive after the generators exist). Tier 2 = inside each thread on Saturday. Tier 3 = only after CP5 is green.

### 10. Each company gets its own vocabulary 🛠💲
**Problem.** `taxonomy.py` has one global list of 21 categories and 12 failure codes, and `match.ABBREVIATIONS` is a hardcoded dict of vehicle terms (`HYD`, `CYL`, `BRG`). The three profiles differ only in `category_weights`, part counts and fill rates. Northwind (HVAC) would file claims as `HYD-ELP` / `ENG-OHE` with vehicle shorthand. A judge who opens two companies side by side will see the same words.

**Proposal.**
- `taxonomy.py` keeps the **union** (the global contract). Each profile picks a **subset** plus a few industry-specific extras:
  - Northwind adds `REF-ELP` (refrigerant leak), `CMP-FTS` (compressor fails to start), and `FAN-VIB`. It also adds categories `compressor`, `refrigerant_component` and `motor`, or maps these onto existing ones if we want to keep 21.
  - Northwind drops the hydraulic and brake codes.
- New per-company input `abbreviations.csv` (`abbr, expansion`). Prairie and Ironridge get `HYD, CYL, BRG, REPL`. Northwind gets `CMPR, COND, EVAP, TXV, CAP, RTU`. `normalize()` reads it from the tables instead of a constant. *Why an input file?* Real clients have their own shorthand. Treating it as client data, not code, is the honest design.
- Per-profile **style knobs** used by both generators:
  - `pn_format`: Prairie `100-4471-02`, Ironridge `IR-04471`, Northwind `NW4471A`
  - `desc_style`: ERP comma shorthand vs. plain words
  - `typo_rate`, `causal_blank_share`, `text_item_share`
- Contract impact: one new table (`abbreviations.csv`), and the failure-code check becomes "subset of the union".

### 11. No-literals rule 🛠💲
- `afterlife/match*.py`, `detect.py` and `cost.py` must not contain company IDs, industry words, part numbers, supplier IDs, or category names used as `if` conditions. Everything comes from the tables or the profile.
- `tests/test_no_literals.py` greps those files for every `company_id`, `part_no` and `supplier_id` in the generated data, plus the profile names, and fails if any appear.
- Scope it to **code, not comments or docstrings**: strip them with Python's `tokenize` module first. Category names like `seal` may legitimately appear in comments or in the taxonomy, so don't grep for categories. Grep for IDs and company names only.
- **Pitch line:** "Our matching code has never seen a company name. There's a test that fails if it does."

### 12. Ironridge = the acquired-plant company 💲
**Why.** In real SAP, production POs usually carry MATNR, so BOM ↔ production-spend matching is easy. The real hard cases are:
- a second plant or acquired company on another ERP
- service purchases made as free text
- warranty claims, which never come from purchasing at all

**Proposal.** Ironridge gets plant `P-TX2` (acquired). It has:
- its own legacy numbering (`part_no` blank, `supplier_pn` from a different supplier list)
- descriptions in another style
- its own price levels, so the same part costs differently across the two plants. That gives a second harmonization lever: *plant vs. plant*, alongside *production vs. spare*.

Contract impact: none (`plant` already exists). Only profile knobs change: `acquired_plant_share`, `acquired_plant_pn_fill = 0`.

### 13. Real supplier attribution 🛠💲
**Problem.** If each part has one production supplier, the alert already names the supplier. "Which supplier pays?" is trivial, and the brief has nothing to prove.

**Proposal.**
- The spike part is **dual-sourced**, e.g. Keystone 70% and a second seal supplier 30%.
- New table `build_supply.csv` (generated by 💲, consumed by 🛠), modeled on goods-receipt / batch records:

  | column | example |
  |---|---|
  | product_id | `UV-400` |
  | build_month | `2026-04` |
  | part_no | `200-1180-01` |
  | supplier_id | `S-022` |
  | po_line_id | `PO-450012-010` (the lot consumed) |
  | share | `0.7` |

- 🛠 plants the spike only on **Keystone lots from a specific PO onward**.
- **The supplier mix must vary, or attribution is impossible.** Claims don't record which supplier's part was fitted. If every product and month is 70/30, the two suppliers can't be told apart statistically. The generator must make the mix vary, e.g. Keystone supplies UV-400 and TR-250 while the second supplier supplies UV-600, *or* the split shifts between months. Then compare rates where Keystone's share is high vs. low.
- `detect.py` splits rates by supplier using the shares as exposure weights. Simplest honest version: for each (part, supplier), units exposed = Σ units_built × qty_per × share. Claims are allocated in proportion to share *only* inside cells that have a single supplier, and mixed cells are reported as "ambiguous". Optional extra: a 2-variable Poisson fit.
- In real data this link comes from serial-number ↔ batch traceability (goods issue to production order). Say so in Q&A: "with serial traceability, attribution becomes exact."
- **Brief line:** "Builds from April onward used Keystone's April 15 order (PO-450012). The other supplier's lots show no increase."
- Contract impact: a new table, and `truth_spikes` gains `from_po_line_id`. In `make_sample.py`, give the sample seal kit two suppliers.

### 14. Link table v2 🛠💲
Add three columns to the `links` output:

| column | example |
|---|---|
| `source_system` | `SAP-P-IA1` / `LEGACY-P-TX2` / `SERVICE-PORTAL` / `WTY` |
| `evidence` | JSON string of the signals that agreed, e.g. `{"spec_code":"6204","category":"bearing","supplier_pn":false,"fuzzy":0.91}` |
| `run_id` | links the row to the `runs` record (#17) |

- This table is the product's main export. The Linking explorer shows `evidence` as small chips.
- `method` gains `info_record` (supplier PN via the info-record crosswalk) and `spec_code` (spec code like `6204` or `M20X1.5` found in the description). The full set becomes `exact_pn` / `info_record` / `spec_code` / `failure_code_bom` / `fuzzy_text` / `llm`.

### 15. SAP-column adapter 💲 (Tier 2)
- Our contract stays snake_case internally. One company (proposal: Ironridge) is written in **SAP field names**:

  | SAP field | Our column | Meaning |
  |---|---|---|
  | EBELN + EBELP | `po_line_id` | PO number + line |
  | MATNR | `part_no` | Internal part number |
  | TXZ01 | `description` | Short text on the PO line |
  | LIFNR | `supplier_id` | Supplier number |
  | IDNLF | `supplier_pn` | Supplier's own part number |
  | MENGE | `qty` | Quantity |
  | MEINS | `uom` | Unit of measure |
  | NETPR | `unit_price` | Net price |
  | PEINH | `price_unit` | Price per N units |
  | BEDAT | `po_date` | PO date |
  | WERKS | `plant` | Plant |
  | MAKTX | (part_master) `description` | Material description |

- `afterlife/adapters/sap.py` is a column-map dict plus a rename, run by `io.load()` when it sees SAP headers. It's about 30 lines, plus the quirks a real SAP extract has. Plant a few of them so the adapter visibly earns its keep:
  - `MATNR` / `LIFNR` padded with **leading zeros** (`000000000100447102`). Strip them on input.
  - Dates as `YYYYMMDD` (`BEDAT = 20260211`).
  - `EBELN` (10 digits) + `EBELP` (5 digits, steps of 10), joined into `po_line_id`.
  - Optional: a decimal comma in prices from a European plant (`4,12`).
- Real extracts often have descriptive column labels (or German labels) instead of technical names, depending on how they were exported. The map should accept both, but generate only technical names.
- The demo moment: Ironridge "arrives as a standard SAP extract", and nothing else changes.
- **Don't** build live connectors (RFC, OData). No judge expects them this weekend.

### 16. AI in three narrow places (Tier 2)
| Where | Owner | What | Guardrails |
|---|---|---|---|
| Description parsing | 💲 | `BRG,BALL,6204-2RS,20MM` → `{type, size, spec_code}` once per unique description, cached | Structured JSON output; cache keyed by input hash; feeds fuzzy matching (replaces the embeddings we cut) |
| Claim tie-break | 🛠 | Only low-confidence claim links. Send the candidates and their evidence, get a pick and a reason | Runs **in the pipeline**, never live. Proposes only; result stored with `method = llm`. Serial numbers and dealer names redacted first |
| Supplier brief | shared | Already planned | Template first. Every number must come from `results.duckdb` (#18 checks this) |

- Pin the model ID and prompt version in config. Prompts live in git (`afterlife/prompts/`).
- **No LangGraph or agent framework.** The pipeline is a fixed sequence with 2–3 model calls. If we want something agent-like, the tie-breaker can call 2–3 lookup functions through Claude tool use.
- **The slide:** precision and recall *rules only* vs. *rules + Claude*, per company. A measured lift beats "we use agents".
- Don't compete with Sievo's 94% classification guarantee. Our number is measured against a known answer key, and we say exactly what it measures.

### 17. Run record + thresholds (Tier 2)
- `runs` table: `run_id, started_at, git_commit, seed, input_hashes, model_id, prompt_version, metrics_json`. About 30 lines in `run.py`.
- `config` thresholds per use: recovery uses links with `confidence ≥ 0.9`, pricing `≥ 0.7`, and the explorer shows everything. The recovery claim says "based on N high-confidence claims".
- **0.9 and 0.7 are placeholders.** Our confidence scores are heuristic, not probabilities. At CP3, use the answer key to pick each threshold by target precision (e.g. "≥ 97% precision for recovery" on Prairie), then confirm it holds on the holdout companies. Put the chosen precision on the slide, not the raw threshold.

### 18. Evals as pytest (Tier 2)
- `test_accuracy.py`: precision and recall floors per company and source_table (set at CP3 from the first real numbers, then ratchet up).
- `test_detect.py`:
  - the planted spike is caught on seeds 7, 8 and 9
  - **zero alerts for Northwind**
  - alerts name the planted supplier (#13)
- `test_brief.py`: every `$` and `×` number in a generated brief appears in `results.duckdb`. This is the cheap guard against made-up numbers, and worth a slide.
  - Simplest robust version: the template builds a dict of allowed numbers. The brief's numbers get parsed back (`$2.1M` → 2,100,000; `3.6×` → 3.6) and each must match an allowed value within rounding (±1 in the last shown digit).
  - Run it in a mode with no API key (template only) so CI doesn't need a key. Test the LLM-polished version manually before the pitch.
- Effort numbers in this addendum are **estimates**, not measurements. Re-check them at CP1.

### 19. Review queue (Tier 3, stretch)
- Accept/reject buttons on the Linking explorer, wired to `POST /decisions`, which writes `decisions.csv` (`source_table, source_id, part_no, verdict, reviewer, at`).
- The next `afterlife.run` applies decisions as overrides (`method = human`).
- **Commit the schema now** (Tier 1 cost: one line in the contract). Build the buttons only after CP5.

### 20. Outputs positioning (deck only)
- "Afterlife writes the link table that Sievo, Tavant and SAP each need":
  - service spend ↔ BOM, for spend analytics
  - inferred failed part + supplier mapping, for warranty-recovery tools
  - new info records, for SAP
- A CSV export is enough.
- Say **compatible with** Power BI and Kearney Spend.Pro, **not integrated**. Neither has a public API or trial we could check.
- **Path to production slide:**
  - same steps on the client's scheduler (Dagster or Prefect)
  - DuckDB → Snowflake / Databricks / Postgres
  - Splink (open-source record linkage on DuckDB) once descriptions are parsed into attributes (#16)

### Considered and rejected
- **LangGraph / agent frameworks.** No visible benefit for a fixed batch pipeline. Adds state and debugging time.
- **Graph database or OWL ontology.** Our taxonomy, failure-code map, abbreviations and link table *are* the ontology, kept as DuckDB tables. Call them that in the deck.
- **Splink this weekend.** It's a good fit later, but it's a new dependency after CP0 and needs attribute columns first. Keep rapidfuzz.
- **Live SAP / Sievo / Tavant connectors.** Unverifiable in a weekend, and judges won't expect them.

## Sources
- SAP EKPO fields (NETPR, PEINH): [leanx.eu EKPO](https://leanx.eu/en/sap/table/ekpo.html), [se80 PEINH](https://www.se80.co.uk/sap-data-element/?name=peinh)
- Vendor material number IDNLF / info records: [sapdatasheet IDNLF](https://www.sapdatasheet.org/abap/dtel/idnlf.html), [SAP Community](https://answers.sap.com/questions/397123/populating-vendor-material-number-ekpo-idnlf-again.html)
- PO text items without a material: [SAP Help: PO without master record](https://help.sap.com/saphelp_46C/helpdata/EN/75/ee0db555c811d189900000e8322d00/content.htm), [SAP Community Q&A](https://community.sap.com/t5/enterprise-resource-planning-q-a/procurement-of-a-material-without-a-material-master-in-sap-mm/qaa-p/13976755/highlight/true), [SAP learning: consumables](https://learning.sap.com/courses/business-processes-in-sap-s-4hana-sourcing-and-procurement/creating-a-purchase-order-for-consumable-material_ef18e834-009e-4b76-a138-8134b7f7bd53)
- BOM item table STPO: [leanx.eu STPO](https://leanx.eu/sap/table/stpo/), [sapstack STPO](https://www.sapstack.com/tables/tabledetails.php?table=STPO)
- SAP warranty (WTY) causal part / item types: [ERPLingo: part causing damage](https://www.erplingo.com/sap-glossary/en/lo-wty/part-causing-damage), [leanx PVWTY](https://leanx.eu/en/sap/table/pvwty.html), [SAP warranty claim process](https://blogs.sap.com/2022/07/06/sap-warranty-claim-creation-business-process/)
- Months in service / maturity / early warning: [SAS Global Forum 2019 paper](https://support.sas.com/resources/papers/proceedings19/3877-2019.pdf), [Elsmar quality forum](https://elsmar.com/elsmarqualityforum/threads/10-2-5-warranty-management-process-measures.89661/), [Umbrex warranty claim rate](https://umbrex.com/resources/company-analysis/product-management/warranty-claim-rate-by-product/), [ReliaSoft warranty analysis](https://help.reliasoft.com/reference/life_data_analysis/lda/warranty_data_analysis.html)
- ISO 14224 failure modes: [Fabrico](https://www.fabrico.io/blog/iso-14224-failure-taxonomy-codes/), [Tetra Pak](https://maintenance.tetrapak.com/service/tpms/help/b-features/ampc/maintenance-plan-development/failure-analysis-configuration/failure-modes/failure-modes.html)
- Supplier recovery: [Warranty Week 2019](https://www.warrantyweek.com/archive/ww20190418.html), [Warranty Week 2017](https://www.warrantyweek.com/archive/ww20170622.html), [Warranty Week 2013](https://warrantyweek.com/archive/ww20130411.html)
- Addendum (items 10–20): [Beroe: under the hood of Beroe MAX](https://www.beroeinc.com/resource-centre/insights/getting-under-the-hood-of-beroe-max-powered-by-kearney/), [Beroe MAX powered by Kearney](https://www.beroeinc.com/beroe-max-powered-by-kearney/), [Kearney procurement (SpendPro, Agent Kai, Contract IQ, NEXT)](https://www.kearney.com/industry/energy/chemicals/procurement), [SAP partner profile: Sievo](https://www.sap.com/partners/profile/sievo), [Tavant Supplier Recovery listing](https://platform.softwareone.com/product/supplier-recovery/PCP-1244-7498), [Splink on PyPI](https://pypi.org/project/splink/)
