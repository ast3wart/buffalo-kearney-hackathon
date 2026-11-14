# Data contract

**This file is the agreement between the 🛠 Warranty and 💲 Spend threads.** Both sides code against it. Changing a column means updating this file *and* telling the other person (log it in [../team/handoffs.md](../team/handoffs.md)).

All files are CSV and UTF-8. Dates are `YYYY-MM-DD`, months are `YYYY-MM`, money is USD.
Column names follow common SAP tables (noted in brackets) so Kearney judges recognize them.

## Inputs (what a client would give us)

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
| category | str | `bearing` |
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
| supplier_id | str | `S-017` |
| supplier_name | str | `Great Lakes Bearing Co` |
| supplier_pn | str | `6204-2RSH` |
| description | str | `Deep groove ball bearing 20x47x14 sealed` |
| qty | float | `5000` |
| uom | str | `EA` / `BX10` |
| unit_price | float | `4.12` (per uom) |
| po_date | date | `2026-02-11` |
| plant | str | `P-IA1` |
| country | str | `US` |

### `service_spend.csv`: spares and repair parts, same columns as production_spend plus:
| column | type | example |
|---|---|---|
| channel | str | `spares` / `warranty_repair` |

### `failure_codes.csv`
| column | type | example |
|---|---|---|
| failure_code | str | `H-21` |
| system | str | `hydraulic` |
| description | str | `Hydraulic leak at cylinder` |
| likely_categories | str | `seal;hose;fitting` (semicolon list) |

### `warranty_claims.csv`
| column | type | example |
|---|---|---|
| claim_id | str | `WC-2026-00431` |
| product_id | str | `UV-400` |
| serial_no | str | `UV4-26-03-01188` |
| build_month | str | `2026-03` |
| failure_date | date | `2026-07-19` |
| failure_code | str | `H-21` |
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
| start_build_month | str | `2026-03` |
| multiplier | float | `3.0` |

## Outputs (tables in results.duckdb)
### `links`: both threads (spend rows from match_spend, claim rows from match_claims)
| column | type | notes |
|---|---|---|
| source_table | str | as above |
| source_id | str | |
| part_no | str | best match |
| method | str | `exact_pn` / `failure_code_bom` / `fuzzy_text` / `llm` |
| confidence | float | 0–1 |

### `alerts`: 🛠 Warranty thread
| column | type |
|---|---|
| part_no, supplier_id | str |
| products_affected | int |
| start_build_month | str |
| baseline_rate, current_rate | float (claims per 1,000 units) |
| ratio | float |
| exposure_usd | float |
