# Registry data format (DRAFT for CP0 sign-off)

**Status:** DRAFT. Combines Asher's format with Brandon's schema from [pivot-plan/06-tech-stack.md](../plan/pivot-plan/06-tech-stack.md). Asher and Brandon: edit, then mark it ✅ agreed. Changing it after CP0 means a line in the other person's inbox *before* you build.

**Storage (from Brandon's plan):**
- **CSV/JSON seed files** in `data/seed/<portfolio_id>/` → `scripts/seed.py` → **SQLite** (`demo.db`, via SQLModel/SQLAlchemy).
- "Postgres in production; the database URL is the only change."
- Money in USD, dates `YYYY-MM-DD`.
- Hand-made sample for building against: `data/seed/sample/`.

**Demo data (from Brandon's plan):** a **2-plant synthetic portfolio**: 1 fund → 1–2 companies → **2 plants** → ~3 lines each → ~25–40 machines → components. The planted answers include **a spare at Plant B that Plant A needs**.

**Owner key:**
- 🛠 **Asher** fills it (what's installed, from photos and lists)
- 💲 **Brandon** fills it (what it costs)
- 🤝 **shared**

## Tables (the registry)
| Table | Columns | Owner |
|---|---|---|
| `fund` | id, name | 🤝 |
| `company` | id, fund_id, name, acquired_on, deal_value_usd | 🤝 (deal_value 💲) |
| `plant` | id, company_id, name, location | 🛠 |
| `line` | id, plant_id, name, product, revenue_per_day, downtime_cost_per_hour | 🛠 ids, 💲 money |
| `machine` | id, line_id, machine_type, make, model, serial, year, photo_path, condition (good/fair/poor), is_redundant, value_low, value_high | 🛠 identity, 💲 value range |
| `component` | id, machine_id, kb_id (blank if unmatched), part_no, type (plc/drive/hmi/servo/motor/power_supply/other), date_code, status (lifecycle, copied from the KB), confidence (0–1), method (vision/list/manual), needs_review, evidence_id | 🛠 |
| `spare_stock` | id, plant_id, kb_id, qty, bin, last_moved_on | 🛠 (from storeroom exports) |
| `evidence` | id, entity_type, entity_id, photo_path, reading_json, source_url, confidence, reviewer (blank until checked) | 🛠 |

## Reference data
| Table | Columns | Owner |
|---|---|---|
| `kb_entry` | id, manufacturer, family, part_no, description, type, class_code, lifecycle_status (active/active_mature/end_of_life/discontinued), status_date, typical_life_years, successor, cost_low, cost_high, migration_cost_low, migration_cost_high, migration_downtime_hours, lead_time_wks, source_url | 🛠 identity + lifecycle, 💲 cost / migration / lead time |
| `sourcing_offer` | id, kb_id, channel (oem/authorized/refurbisher/surplus/marketplace), seller, authorized (yes/no), price, condition (new/refurbished/used), lead_time_wks, warranty_months, trust_score (0–1), url, seen_at | 💲 |

## Answer key (for accuracy)
| Table | Columns | Owner |
|---|---|---|
| `truth_component` | component_id, kb_id, part_no, lifecycle_status, is_spof (planted single point of failure), duplicate_of (same part under another name) | 🛠 |
| `truth_spare_match` | needing_component_id, spare_stock_id (the planted Plant B spare) | 🛠 |

## Outputs (what the code produces, and what the app shows)
| Output | Columns | Produced by |
|---|---|---|
| `capex_by_year` | company_id, plant_id, year, capex_low, capex_high, driver (replace/migrate/catch_up) | 💲 `xray/valuation.py` |
| `deal_adjustment` | company_id, deferred_capex_low, deferred_capex_high, suggested_price_reduction, suggested_holdback, rationale | 💲 `xray/valuation.py` |
| `spof` | component_id, line_id, risk_score, downtime_exposure_per_day, why | 💲 `xray/valuation.py` (uses 🛠 registry) |
| `sourcing_recommendation` | component_id, action (use_shelf_spare/buy_spare/migrate/monitor), spare_stock_id, best_offer_id, reason | 💲 `xray/sourcing.py` (**shelf first**: any plant in the portfolio) |
| `accuracy` | field, records, predicted, correct, precision, recall, ci_low, ci_high | 🛠 `xray/evaluate.py` |

## Rules
- **Every number shown traces to a row:** `evidence`, `kb_entry.source_url` or `sourcing_offer.url`. The evidence drawer shows it.
- **Money is always a range** (low/high).
- **Confidence < 0.8 or a big-ticket item → `needs_review`**, never silently used.
- **No manufacturer, part or plant names in the logic code.** They live in the data.
- Vision responses are **cached by image hash**, so the demo works offline. Only the live photo needs a real API call.
