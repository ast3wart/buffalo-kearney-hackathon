# Data contract

**This file is the agreement between the 🛠 Warranty and 💲 Spend threads.** Both sides code against it. Changing a column means updating this file *and* telling the other person (log it in [../team/handoffs/](../team/handoffs/README.md) (the other person's inbox)).

**Multiple companies:** every company is its own folder, `data/generated/<company_id>/`, containing *all* the tables below with the same columns. Profiles are in `afterlife/profiles.py`. `afterlife.run` adds a `company_id` column when it loads them into `results.duckdb`. `data/sample/` is a single small company (`company_id = sample`).

All files are CSV and UTF-8. Dates are `YYYY-MM-DD`, months are `YYYY-MM`, money is USD.
Column names follow common SAP tables (noted in brackets) so Kearney judges recognize them.
**v3 (Sat Nov 14), from Brandon's CP0 review.** Applied by Asher, Brandon to confirm at CP1. Changes from v2:
- **Per-company vocabulary:** new `abbreviations.csv`. `failure_codes.csv` is the company's *subset* of `taxonomy.FAILURE_CODES`. 3 HVAC categories and 4 HVAC failure codes added.
- **Supplier attribution:** new `build_supply.csv` (which supplier lot each product/month consumed). The spike part is dual-sourced, and `truth_spikes` gains `from_po_line_id`.
- **Links v2:** `source_system`, `evidence`, `run_id` (see Outputs).
- **SAP extracts:** a company can arrive with raw SAP field names, which `afterlife/adapters/sap.py` maps on load (see "SAP extract format").
- **Acquired plant (Ironridge):** a second plant with no part numbers. It's a profile knob, with no column change.

**v4 (Sat Nov 14), accounting fields (PROPOSED by Brandon, Asher to confirm).** Changes from v3:
- **Claims:** `claim_date` (reporting lag), `paid_date` (blank = unpaid), `claim_type` (21c), `other_cost` (handling, freight, sublet), `recovered_usd`. Claims not yet reported by `data_as_of` are simply absent.
- **Products:** `avg_selling_price`, so warranty cost can be shown as % of revenue next to the SEC benchmarks.
- **Supplier agreements are documents, not columns:** new `supplier_agreements/` folder (one text file per production supplier). Recovery terms are *extracted* by `afterlife/extract_terms.py` (regex + Claude) into the `supplier_terms` output, scored against the new `truth_terms.csv` answer key.
- No change to the SAP adapter: none of these fields are in the EKKO/EKPO/MARA/EINA extract (see "Stored or extracted?").

Categories and failure codes live in `afterlife/taxonomy.py` (the union). Each company's subset and abbreviations are in `afterlife/profiles.py`. `python -m afterlife.check` enforces this file.

## Inputs (what a client would give us)

### `dataset_info.csv` (key/value)
| key | value (generated data) |
|---|---|
| company_id | `prairie` (= folder name) |
| company_name | `Prairie Utility Vehicles` |
| industry | `Utility vehicles and compact tractors` |
| data_as_of | `2026-10-31`: nothing happens after this date |
| first_build_month / last_build_month | `2025-01` / `2026-09` (sample: `2026-01` / `2026-06`) |
| currency | `USD` |
| warranty_months | `24` |
| mis_window | `3`: months in service used for spike detection |

### `products.csv`
| column | type | example |
|---|---|---|
| product_id | str | `UV-400` |
| product_name | str | `Ranger-style utility vehicle 400` |
| family | str | `utility_vehicle` |
| avg_selling_price | float | `14500.00`: average net selling price per unit [VBRP-NETWR / FKIMG] (v4) |

### `part_master.csv` [MARA]
| column | type | example |
|---|---|---|
| part_no | str | `100-4471-02` |
| description | str | `BRG,BALL,6204-2RS,20MM` |
| category | str | `bearing`: **must be one of the 24 in `taxonomy.CATEGORIES`** |
| std_cost | float | `4.10` |

### `bom.csv` [STKO/STPO], single level for MVP
| column | type | example |
|---|---|---|
| product_id | str | `UV-400` |
| part_no | str | `100-4471-02` |
| qty_per | float | `4` |
| position | str | `front_axle` |

### `builds.csv`: units built per product per month (denominator for claim rates)
| column | type | example |
|---|---|---|
| product_id | str | `UV-400` |
| build_month | str | `2026-03` |
| units_built | int | `1200` |

### `production_spend.csv` [EKKO/EKPO]
| column | type | example |
|---|---|---|
| po_line_id | str | `PO-450012-010` |
| part_no | str | internal part number [EKPO-MATNR]. **Nullable:** ~85% filled on production lines. Blank = free-text "text item" |
| supplier_id | str | `S-017` |
| supplier_name | str | `Great Lakes Bearing Co` |
| supplier_pn | str | `6204-2RSH` |
| description | str | `Deep groove ball bearing 20x47x14 sealed` |
| qty | float | `5000` |
| uom | str | `EA` / `BX10` |
| unit_price | float | `4.12`: price per **price_unit** of uom [NETPR] |
| price_unit | int | `1`, sometimes `100` [PEINH]. **Per-EA price = unit_price / price_unit / pack size of uom** |
| po_date | date | `2026-02-11` |
| plant | str | `P-IA1` |
| country | str | `US` |

### `service_spend.csv`: spares and repair parts, same columns as production_spend (part_no ~15% filled) plus:
| column | type | example |
|---|---|---|
| channel | str | `spares` / `warranty_repair` |

### `info_records.csv` [EINA/EINE]: supplier part number crosswalk
| column | type | example |
|---|---|---|
| part_no | str | `100-4471-02` |
| supplier_id | str | `S-011` |
| supplier_pn | str | `6204-2RSH` [IDNLF] |

Present for **production suppliers only**. The service distributor has none, which is why service spend is hard to link.

### `build_supply.csv`: which supplier lot each build consumed [modeled on goods-receipt / batch records] (v3)
| column | type | example |
|---|---|---|
| product_id | str | `UV-400` |
| build_month | str | `2026-04` |
| part_no | str | `200-1180-01` |
| supplier_id | str | `S-022` |
| po_line_id | str | `PO-450005-010`, the production PO line (lot) consumed |
| share | float | `0.5`. Shares sum to 1 per (product, month, part) |

One row per BOM line × build month × supplier. **The mix must vary** across products and/or months, or a spike can't be attributed to a supplier (claims never say which supplier's part was fitted). In real data this comes from serial ↔ batch traceability.

### `abbreviations.csv`: the company's shorthand (v3)
| column | type | example |
|---|---|---|
| abbr | str | `BRG` / `CMPR` |
| expansion | str | `BEARING` / `COMPRESSOR` |

Client data, not code. `match.normalize()` reads it, so no company's shorthand is hardcoded.

### `failure_codes.csv`: this company's subset of `taxonomy.FAILURE_CODES` (`SYSTEM-MODE`, modes after ISO 14224)
| column | type | example |
|---|---|---|
| failure_code | str | `HYD-ELP` (Northwind: `REF-ELP`, `CMP-FTS`, …) |
| system | str | `hydraulic` |
| description | str | `External leakage` (the observed symptom, not the cause) |
| likely_categories | str | `seal;hose;fitting;hydraulic_component` (semicolon list) |

### `warranty_claims.csv`
| column | type | example |
|---|---|---|
| claim_id | str | `WC-2026-00431` |
| product_id | str | `UV-400` |
| serial_no | str | `UV4-26-03-01188` |
| build_month | str | `2026-03` |
| failure_date | date | `2026-07-19`: between build month and `data_as_of`. **Months in service (MIS)** = months from build_month to failure_date |
| claim_date | date | `2026-08-02`: dealer submitted the claim, between failure_date and `data_as_of`. The gap is the **reporting lag**; recent build months are under-reported until it closes (v4) |
| paid_date | date | `2026-08-20`: we paid the dealer. **Blank = not yet paid.** Supplier recovery filing deadlines count from here (v4) |
| claim_type | str | `warranty` / `goodwill` / `campaign` (21c, v4). Only `warranty` is recoverable from the supplier; campaigns are reserved separately |
| failure_code | str | `HYD-ELP` |
| claim_text | str | `hyd leak boom cyl, replaced seal kit` |
| causal_part_no | str | often **blank** or wrong. This is what we infer |
| labor_hrs | float | `2.5` |
| parts_cost | float | `38.00` |
| labor_cost | float | `212.50` |
| other_cost | float | `24.00`: handling, freight, sublet (v4). Part of warranty cost, but **not** recoverable under the sample agreements |
| dealer_id | str | `D-118` |
| recovery_status | str | `none` / `submitted` / `recovered`. Only paid claims are submitted |
| recovered_usd | float | `152.80`: credit received from the supplier, `0` unless `recovered` (v4) |

### `supplier_agreements/`: one document per production supplier (v4, a folder, not a CSV)
Supplier quality agreements and amendments as `.md` / `.txt` (a real client sends PDFs; convert to text first). Loaded by `io.load_documents()` as `[doc_file, text]`. Wording varies on purpose: prose clauses, a terms table, and **amendments that supersede the original clause** (the latest one wins). The file name is not trusted: which supplier the document is for is extracted too.

#### Price schedule section (💲, generated companies, Sat Nov 14)
Every generated agreement also has a price schedule: **"## 5. Prices"** (formal / amended styles) or **"PRICE SCHEDULE (per piece, USD)"** (table style). One markdown table row per part: `| Buyer part no. | Supplier part no. | Description | Price per piece (USD) | Valid from | Valid to |`, followed by clause **5.3**: either *"Supplier supplies the parts above as spare parts at the current series price …"* or *"Spare parts are priced separately by quotation."* Agreements for generated companies are written by `generate_spend.py` via `afterlife/agreements.py` (the warranty section wording and `warranty_terms()` are 🛠 Brandon's to own). Acquired-plant (legacy) suppliers have no agreement in the system, which is realistic, so the check warns.

## Generated-only (answer key, never used by matching)
### `truth_links.csv`
| column | type | notes |
|---|---|---|
| source_table | str | `production_spend` / `service_spend` / `warranty_claims` |
| source_id | str | po_line_id or claim_id |
| part_no | str | the correct part |

### `truth_spikes.csv`
| column | type | example |
|---|---|---|
| part_no | str | `200-1180-01` |
| supplier_id | str | `S-022` |
| start_build_month | str | `2026-04` |
| from_po_line_id | str | `PO-450005-010`: the first affected lot of that supplier (v3) |
| multiplier | float | `3.0` |

### `truth_terms.csv`: what each agreement actually says (v4)
| column | type | example |
|---|---|---|
| doc_file | str | `sqa_keystone-seal-works.md` |
| supplier_id | str | `S-022` |
| recovery_pct | float | `0.8`: share of the recoverable cost the supplier reimburses |
| labor_covered | bool | `True` |
| labor_rate_cap | float | `90`: max USD per labor hour reimbursed. Blank = no cap / labor not covered |
| recovery_window_months | int | `18`: from the end unit's build month |
| filing_deadline_days | int | `45`: days after `paid_date` to file the recovery claim |

## Outputs (tables in results.duckdb)
### `links`: both threads (spend rows from match_spend, claim rows from match_claims)
| column | type | notes |
|---|---|---|
| source_table | str | as above |
| source_id | str | |
| part_no | str | best match |
| method | str | `exact_pn` / `info_record` / `spec_code` / `failure_code_bom` / `fuzzy_text` / `llm` / `human` (`taxonomy.LINK_METHODS`) |
| confidence | float | 0–1 (heuristic, not a probability; thresholds picked at CP3 by target precision) |
| source_system | str | `SAP-P-IA1` / `LEGACY-P-TX2` / `SERVICE-PORTAL` / `WTY` (v3) |
| evidence | str | JSON of the signals that agreed, e.g. `{"spec_code":"6204","category":"bearing","info_record":false,"fuzzy":0.91}` (v3) |
| run_id | str | ties the row to `runs` (v3) |

### `supplier_terms`: 🛠 Warranty thread, extracted from `supplier_agreements/` (v4)
The `truth_terms` columns plus `method` (`regex` / `llm` / `human`), `confidence` (0–1), `evidence` (JSON: the clause quoted for each field) and `run_id`. Blank fields = needs human review. Recoverable amount for a linked claim = `recovery_pct × (parts_cost + (labor_covered ? min(labor_cost, labor_hrs × labor_rate_cap) : 0))`, only inside the window and filing deadline.

### `runs` (v3 #17): one row per `python -m afterlife.run`
`run_id, started_at, git_commit, input_hashes, model_id, prompt_version, metrics_json`

### `decisions.csv` (v3 #19, schema reserved, stretch)
`source_table, source_id, part_no, verdict, reviewer, at`: human accept/reject, applied as overrides (`method = human`).

### `alerts`: 🛠 Warranty thread
| column | type |
|---|---|
| part_no, supplier_id | str |
| products_affected | int |
| start_build_month | str |
| mis_window | int (3) |
| baseline_rate, current_rate | float: claims within `mis_window` MIS per 1,000 built (mature build months only; v4: "mature" also allows for the reporting lag) |
| ratio | float |
| exposure_usd | float |
| p_value | float: one-sided significance of the step, corrected for picking the best split (detect v1) |
| q_value | float: Benjamini–Hochberg q over every (part, supplier) series tested in the company. Alert needs q < 0.05 |
| claims | int: claims linked + attributed to this part/supplier since `start_build_month` |
| excess_cost_usd | float: share of exposure above what the baseline predicts = exposure × (1 − 1/ratio) |
| open_exposure_usd | float: exposure from claims with `recovery_status = none` (and `claim_type = warranty` once 21c lands) |
| from_po_line_id | str: first affected supplier lot |
| attribution | str: weakest evidence after the start: `clean` / `deconvolved` / `ambiguous` |
| spike_claims | int: claims within the MIS window after the start (the numerator of `current_rate`) |

All `$` here are **analytics estimates, not accruals or receivables** ([../research/warranty-accounting.md](../research/warranty-accounting.md)). Accounting changes are tracked in [cp0-proposal.md item 21](../research/cp0-proposal.md#21-warranty-accounting-fit-proposed): the selling price (`products.avg_selling_price`, 21a) and the double-count rule (21b, "Cost rules" below) are applied; `claim_type` (21c) and supplier terms as documents (21g) are in contract v4.

## Cost rules (accounting)
**Double-count rule (21b, accepted Sat Nov 14).** For `cost.lifecycle_cost` and anything else that adds up cost:
- **Warranty cost = `warranty_claims.parts_cost + labor_cost + other_cost`** (v4 adds `other_cost`). The supplier-recovery basis is narrower: parts + covered labor per `supplier_terms`, `claim_type = warranty` only.
- `service_spend` with **`channel = warranty_repair`** is the purchasing side of those same repairs. It's used **only to reconcile** (e.g. "claims parts cost vs. warranty-repair purchases") and **never added** to cost.
- Only `service_spend` with **`channel = spares`** is added, as spare-part cost.
- All `$` from `detect.py` and `cost.py` are analytics estimates, not accruals or receivables.

## Stored or extracted? (v4)
Rule: if a real manufacturer has it as a **field in a system**, we model it as a column and assume it arrives in the extract. If it lives in **contract text**, we model it as a document and extract it with the AI step. That keeps the AI where it earns its place and keeps the numbers auditable.

| Data point | Where it lives at a real SAP client | Our model |
|---|---|---|
| claim_date, paid_date, labor/parts/other cost split | Warranty claim system: SAP Warranty Claim Processing (claim header and items), or a dealer portal | column on `warranty_claims` |
| recovery_status, recovered_usd | Same claim system, supplier-recovery claim/credit memo (FI vendor credit) | column on `warranty_claims` |
| avg_selling_price | SD billing documents (VBRK/VBRP), averaged per material | column on `products` |
| recovery %, labor coverage, labor cap, window, filing deadline | Supplier quality agreement / purchasing contract, PDF or long text. Rarely structured fields | **document** → `extract_terms.py` → `supplier_terms` |
| in-service (retail) date | Claim system / dealer registration | not modeled: MIS counts from build month (documented simplification) |

Warranty claims never come through the SAP spend adapter below; they keep contract columns for every company, including Ironridge (`source_system = WTY`).

### `truth_prices.csv` (💲, generated companies): the contract prices each agreement states
| column | type | example |
|---|---|---|
| doc_file | str | `sqa_delta-fluid-power.md` |
| supplier_id | str | `S-014` |
| part_no | str | `105-2563-08` |
| contract_price_ea | float | `527.31`: per piece, USD |
| valid_from, valid_to | date | `2025-01-01`, `2026-12-31` |
| spares_at_series_price | bool | clause 5.3 grants spares at series price |

### Outputs added Sat Nov 14 (💲)
- **`contract_prices`** (`extract_prices.py`): `doc_file, supplier_id, part_no, supplier_pn, contract_price_ea, valid_from, valid_to, spares_at_series_price, method, confidence, evidence, run_id`. Extracted from the documents, scored against `truth_prices` (100% on 3 fresh companies).
- **`contract_compliance`** (`cost.contract_compliance`): `finding` = `price_leakage` (production paid > contract price × 1.005 within validity) or `spares_clause` (spare paid > series price × 1.10, packaging allowance, where the clause applies), with `part_no, supplier_id, agreement_supplier_id, doc_file, plant, po_line_id, po_date, price_ea, contract_price_ea, qty_ea, gap_usd`. High-confidence links only. Estimates for review, not amounts owed.
- **Generator realism (after Velocity research):** spares are mostly bought near contract price (`spare_contract_share` 0.6 at 1.0–1.25×); only off-contract buys carry `spare_markup` (1.4–4.5×). Production pays exactly the contract price except `price_leak_share` (15%) of supplier-part pairs with an unapproved 3–8% increase from some quarter.

## SAP extract format (v3 #15, Ironridge)
A company with `extract_format: "sap"` in its profile ships `production_spend`, `service_spend`, `part_master` and `info_records` with **SAP technical field names and quirks**. `io.load()` detects the headers and `afterlife/adapters/sap.py` converts them to the columns above, so nothing downstream changes.

| SAP field | Our column | Table (SAP) | Quirk handled |
|---|---|---|---|
| EBELN + EBELP | `po_line_id` | EKKO/EKPO | joined `EBELN-EBELP` (EBELP 5 digits, steps of 10). For SAP-format companies **every** PO-line reference (`build_supply`, `truth_links`, `truth_spikes`) uses this form (`sap.canonical_po_id`), written by `generate.write()` |
| MATNR | `part_no` | EKPO / MARA | numeric values zero-padded to 18, stripped |
| TXZ01 | `description` | EKPO | short text on PO line |
| LIFNR | `supplier_id` | EKKO / LFA1 | numeric values zero-padded to 10, stripped |
| NAME1 | `supplier_name` | LFA1 | |
| LAND1 | `country` | LFA1 | |
| IDNLF | `supplier_pn` | EKPO / EINA | |
| MENGE | `qty` | EKPO | |
| MEINS | `uom` | EKPO | |
| NETPR | `unit_price` | EKPO | decimal comma accepted (`4,12`) |
| PEINH | `price_unit` | EKPO | |
| BEDAT | `po_date` | EKKO | `YYYYMMDD` → `YYYY-MM-DD` |
| WERKS | `plant` | EKPO | |
| MAKTX | `description` (part_master) | MAKT | |
| MATKL | `category` (part_master) | MARA | material group = our category |
| STPRS | `std_cost` (part_master) | MBEW | |

Descriptive labels (`Material`, `Vendor`, `Net Price`, …) are accepted on input too. The generator writes technical names only. Tested in `tests/test_sap_adapter.py`.
