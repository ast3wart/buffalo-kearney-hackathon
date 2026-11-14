# Data contract

**This file is the agreement between the 🛠 Warranty and 💲 Spend threads.** Both sides code against it. Changing a column means updating this file *and* telling the other person (log it in [../team/handoffs.md](../team/handoffs.md)).

**Multiple companies:** every company is its own folder, `data/generated/<company_id>/`, containing *all* the tables below with the same columns. Profiles are in `afterlife/profiles.py`. `afterlife.run` adds a `company_id` column when it loads them into `results.duckdb`. `data/sample/` is a single small company (`company_id = sample`).

All files are CSV and UTF-8. Dates are `YYYY-MM-DD`, months are `YYYY-MM`, money is USD.
Column names follow common SAP tables (noted in brackets) so Kearney judges recognize them.
**v3 (Sat Nov 14), from Brandon's CP0 review.** Applied by Asher, Brandon to confirm at CP1. Changes from v2:
- **Per-company vocabulary:** new `abbreviations.csv`. `failure_codes.csv` is the company's *subset* of `taxonomy.FAILURE_CODES`. 3 HVAC categories and 4 HVAC failure codes added.
- **Supplier attribution:** new `build_supply.csv` (which supplier lot each product/month consumed). The spike part is dual-sourced, and `truth_spikes` gains `from_po_line_id`.
- **Links v2:** `source_system`, `evidence`, `run_id` (see Outputs).
- **SAP extracts:** a company can arrive with raw SAP field names, which `afterlife/adapters/sap.py` maps on load (see "SAP extract format").
- **Acquired plant (Ironridge):** a second plant with no part numbers. It's a profile knob, with no column change.

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
| failure_code | str | `HYD-ELP` |
| claim_text | str | `hyd leak boom cyl, replaced seal kit` |
| causal_part_no | str | often **blank** or wrong. This is what we infer |
| labor_hrs | float | `2.5` |
| parts_cost | float | `38.00` |
| labor_cost | float | `212.50` |
| dealer_id | str | `D-118` |
| recovery_status | str | `none` / `submitted` / `recovered` |

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
| baseline_rate, current_rate | float: claims within `mis_window` MIS per 1,000 built (mature build months only) |
| ratio | float |
| exposure_usd | float |

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
