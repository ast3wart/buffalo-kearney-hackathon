# Registry data format (DRAFT for CP0 sign-off)

**Status:** DRAFT. Asher and Brandon: edit, then mark it ✅ agreed. Changing it after CP0 means a line in the other person's inbox *before* you build.

All files are CSV, UTF-8, money in USD, dates `YYYY-MM-DD`. One folder per company: `data/factory/<company_id>/`. The hand-made sample is in `data/factory/sample/`.

**Owner key:**
- 🛠 **Asher** fills it (what's installed, read from photos and lists)
- 💲 **Brandon** fills it (what it costs)
- 🤝 **shared**

## Tables (the registry)
| Table | Columns | Owner |
|---|---|---|
| `companies.csv` | company_id, company_name, owner (e.g. a PE fund), acquisition_date, deal_value_usd | 🤝 (deal_value 💲) |
| `plants.csv` | plant_id, company_id, plant_name, location | 🛠 |
| `lines.csv` | line_id, plant_id, product, revenue_per_day_usd, downtime_cost_per_hour_usd | 🛠 ids, 💲 money |
| `machines.csv` | machine_id, line_id, machine_type, make, model, serial, year_built, photo, condition (good/fair/poor), is_redundant (another machine can cover it) | 🛠 |
| `components.csv` | component_id, machine_id, component_type (plc/drive/hmi/servo/motor/power_supply/other), manufacturer, catalog_no, date_code, kb_id (matched, blank if none), spares_on_hand, confidence (0–1), method (vision/list/manual), evidence_id | 🛠 |
| `evidence.csv` | evidence_id, photo, reading_json (what vision read), source, confidence, reviewer (blank until a person checks it) | 🛠 |

## Reference data
| Table | Columns | Owner |
|---|---|---|
| `data/kb/kb.csv` | kb_id, manufacturer, catalog_no, description, component_type, lifecycle_status (active/active_mature/end_of_life/discontinued), status_date, typical_life_years, successor_catalog_no, replacement_cost_usd, migration_cost_usd, migration_downtime_hours, source_url | 🛠 identity + lifecycle, 💲 the cost columns |
| `data/sourcing/offers.csv` | offer_id, catalog_no, channel (oem/authorized/refurbisher/surplus/marketplace), seller, price_usd, condition (new/refurbished/used), lead_time_days, warranty_months, trust_score (0–1), url, seen_at | 💲 |

## Answer key (for accuracy)
| Table | Columns | Owner |
|---|---|---|
| `truth_components.csv` | component_id, kb_id, catalog_no, lifecycle_status, is_spof (planted single point of failure) | 🛠 |

## Outputs (what the code produces, and what the app shows)
| Output | Columns | Produced by |
|---|---|---|
| `capex_by_year` | company_id, plant_id, year, capex_low_usd, capex_high_usd, driver (replace/migrate/catch_up) | 💲 `valuation.py` |
| `deal_adjustment` | company_id, deferred_capex_usd, suggested_price_reduction_usd, suggested_holdback_usd, rationale | 💲 `valuation.py` |
| `spof` | component_id, line_id, risk_score, annual_exposure_usd, why | 💲 `valuation.py` (uses 🛠 registry) |
| `sourcing_recommendation` | component_id, action (buy_spare/migrate/monitor), best_offer_id, reason | 💲 `sourcing.py` |
| `accuracy` | field, records, predicted, correct, precision, recall, ci_low, ci_high | 🛠 `evaluate.py` |

## Rules
- **Every number shown in the app traces to a row** in `evidence.csv`, `kb.csv` (source_url) or `offers.csv` (url).
- **Show money as ranges** (low/high), never a single falsely precise figure.
- **Low confidence** (< 0.8) or a big-ticket component → flagged for human review, never silently used.
- **No manufacturer or part names in the logic code.** They live in the data.
