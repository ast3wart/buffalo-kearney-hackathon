# Registry data format (v2: CP0)

**Status: ✅ AGREED (Sat ~6 PM) with defaults.** Brandon may revise the money-side items (the §7 outputs, his columns, the defaults below) at any time, as long as he leaves a line in Asher's inbox.

**Defaults (Brandon owns these and can change them):**
- **His outputs:** the six §7 tables as written.
- **His functions take pandas DataFrames** read from SQLite. They don't need a database connection, so his code runs without the app.
- **Demo portfolio:** 6 plants (see interfaces.md §2).
- **Money per plant:** ~$2M spares inventory, ~$5M maintenance budget.
- **Price = 30% of modeled savings per plant.** Placeholder until `xray/pricing.py` computes it.
- **Listings:** ≥ 3 listings for **3 parts by CP1**, more later.
- **By CP1:** `xray/pricing.py` runs on placeholder inputs. The research fills them in afterward.

**Rule:** after CP0, changing this doc means a line in the other person's inbox **before** you build.

**Function names, API routes, demo portfolio scale and demo script:** [interfaces.md](interfaces.md).

**Source of truth for strategy:** [roadmap](../plan/roadmap-equipment-xray.md). Builds on Brandon's schema ([pivot-plan/06](../plan/pivot-plan/06-tech-stack.md)) and integrations ([pivot-plan/07](../plan/pivot-plan/07-integrations.md)).

## ⚠️ We are building a DEMO, not the full product
This doc describes the full data model, so the pitch and the roadmap hang together. **For the hackathon, build only the demo minimum below.** Every other column may stay blank, and every other file may be skipped. Don't build features for them.

| Needed for the demo | Minimum |
|---|---|
| Plants / lines / machines | **6 plants** (Halvorsen: Toledo, Fort Wayne, Lima; Brightwater: Waukesha, Oshkosh; target Tillman: Rockford; see interfaces.md §2), ~14 lines, ~66 machines. Identity, criticality, line downtime $/h (ranges) |
| Components | ~123, with ~10 photographed (nameplate or cabinet) for the vision step. The rest come from the equipment list. |
| Spares | a short storeroom list per plant with **the planted Plant B spare** and **one duplicate** |
| KB | ~30 parts: lifecycle status, successor, failure rate, migration cost (ranges) |
| Listings | **3 parts with ≥ 3 real listings each**, plus 1 part with none (shows the alternatives path) |
| `plant_financials` | one row per plant (6), placeholder ranges |
| Outputs | CapEx cliff, single points of failure, sourcing for 3 parts, accuracy, price per plant (placeholder model), deal view for one plant |
| **Skip for the demo** | work orders, book value, seller trust beyond a simple score, `alternatives` beyond 1–2 rows, migration downtime, multi-currency, real CMMS/ERP connectors |

---

## 1. Storage and layout
- **Seed files → `scripts/seed.py` → SQLite** (`demo.db`, via SQLModel/SQLAlchemy). "Postgres in production; the database URL is the only change."
- **Plant data is export-style:** each plant's files look like what a real plant would hand over (a CMMS asset export, an ERP storeroom export, photos). `seed.py` maps them into the registry tables in §4.
- **Formats:** CSV, UTF-8, header row, comma separated. Dates `YYYY-MM-DD`. Money in **USD**. Empty cell = unknown, never 0.

```
data/seed/<portfolio_id>/                 e.g. data/seed/demo/   (hand-made sample: data/seed/sample/)
  portfolio.csv                           fund + companies
  plants.csv                              one row per plant
  plant_financials.csv                    money inputs per plant (Brandon's financial model)
  lines.csv                               production lines, revenue + downtime cost
  <plant_id>/                             e.g. PA/, PB/
    assets.csv                            CMMS / equipment-list export: one row per machine
    spares.csv                            ERP storeroom export: what's on the shelf
    work_orders.csv                       maintenance history (optional; failures, repairs)
    photos.csv                            photo manifest: what each photo shows
    readings.csv                          what the scan read per component (raw text, confidence, date code). Simulates vision for parts without a real photo; the matcher runs on it
    photos/                               the images (nameplates, cabinets)
data/reference/
  kb.csv                                  knowledge base: one row per part (catalog) number
  listings.csv                            market listings found online (the basis for part value)
  alternatives.csv                        successor / similar parts when the exact part isn't available
data/truth/<portfolio_id>/                answer key (never read by the pipeline, only by evaluate.py)
  components.csv, spare_matches.csv, duplicates.csv, spof.csv
```

## 2. IDs (readable)
| Thing | Format | Example |
|---|---|---|
| Portfolio | short name | `demo` |
| Fund | `F-<name>` | `F-ACME` |
| Company | `CO-<name>` | `CO-RIVERTON` |
| Plant | `P` + letter | `PA`, `PB` |
| Line | `<plant>-L<n>` | `PA-L1` |
| Machine | `<line>-M<nn>` | `PA-L1-M03` |
| Component | `<machine>-C<n>` | `PA-L1-M03-C2` |
| Spare (shelf row) | `<plant>-S<nnn>` | `PB-S014` |
| Photo | `<plant>-IMG<nnnn>` | `PA-IMG0042` |
| Work order | `<plant>-WO<nnnnn>` | `PA-WO00117` |
| KB entry | `KB-<nnn>` | `KB-014` |
| Listing | `LS-<nnnn>` | `LS-0031` |
| Alternative | `ALT-<nnn>` | `ALT-007` |
| Evidence | `EV-<nnnnn>` | `EV-00042` |

## 3. Fixed value lists (use exactly these)
| List | Values |
|---|---|
| `component_type` | `plc`, `plc_io`, `drive`, `hmi`, `servo_drive`, `servo_motor`, `motor`, `power_supply`, `network`, `safety_relay`, `other` |
| `machine_type` | `cnc_mill`, `cnc_lathe`, `press`, `injection_molder`, `conveyor`, `packaging`, `robot_cell`, `compressor`, `oven`, `pump`, `other` |
| `lifecycle_status` | `active`, `active_mature`, `end_of_life` (discontinuation announced), `discontinued` (no longer made), `unknown` |
| `condition` (machine) | `good`, `fair`, `poor`, `unknown` |
| `criticality` | `line_stop` (line stops if it fails), `degraded` (line slows), `none` (redundant or non-critical) |
| `listing_channel` | `oem`, `authorized_distributor`, `refurbisher`, `surplus`, `marketplace` (eBay etc.), `broker` |
| `listing_condition` | `new`, `new_surplus`, `refurbished`, `used`, `for_repair` |
| `capex_type` | `maintenance` (normal), `deferred` (overdue catch-up), `growth` (optional upgrade) |
| `method` (how a component was identified) | `vision`, `list`, `manual`, `seed` |
| `photo_kind` | `nameplate`, `cabinet`, `component_label`, `overview` |
| `alternative_kind` | `successor` (official replacement), `compatible` (drop-in equivalent), `similar` (needs engineering; e.g. found via a similar-part search) |
| `action` (sourcing) | `use_shelf_spare`, `buy_spare`, `migrate`, `monitor` |

## 4. Plant data files (export-style)
**Owners:** **Asher** = what's installed (identity, photos, lists). **Brandon** = what it costs (money, financial inputs, listings).

### `portfolio.csv` (one row per company)
| Column | Meaning | Owner |
|---|---|---|
| fund_id, fund_name | the PE fund (blank if not PE-owned) | Asher |
| company_id, company_name | the manufacturer | Asher |
| owned_since | date acquired or founded | Asher |
| deal_value_low, deal_value_high | only for the deal lens (an acquisition being priced) | Brandon |

### `plants.csv`
| Column | Meaning | Owner |
|---|---|---|
| plant_id, company_id, plant_name, city, state | where it is | Asher |
| employees | headcount (ties to the Census size bands) | Asher |
| status | `owned` or `target` (being acquired: the deal lens) | Asher |

### `plant_financials.csv` (inputs to Brandon's financial model, one row per plant)
| Column | Meaning | Owner |
|---|---|---|
| plant_id | | Brandon |
| annual_revenue_low, annual_revenue_high | plant revenue | Brandon |
| maintenance_budget_low, maintenance_budget_high | yearly maintenance spend | Brandon |
| spares_inventory_value_low, spares_inventory_value_high | value of the storeroom | Brandon |
| carrying_cost_pct_low, carrying_cost_pct_high | yearly cost of holding spares, % of value | Brandon |
| rush_premium_annual_low, rush_premium_annual_high | extra paid each year for emergency buys | Brandon |
| source | where each number came from (research doc or assumption) | Brandon |

### `lines.csv`
| Column | Meaning | Owner |
|---|---|---|
| line_id, plant_id, line_name, product | | Asher |
| revenue_per_day_low, revenue_per_day_high | output value of the line | Brandon |
| contribution_margin_pct | share of revenue actually lost when the line stops | Brandon |
| operating_hours_per_day | scheduled run hours (e.g. 16) | Brandon |
| downtime_cost_per_hour_low, downtime_cost_per_hour_high | **derived** = revenue_per_day ÷ operating_hours_per_day × contribution margin (+ idle labor); fill only to override | Brandon |

### `<plant>/assets.csv` (CMMS / equipment-list export: one row per machine)
| Column | Meaning | Owner |
|---|---|---|
| machine_id, line_id | | Asher |
| asset_tag | the plant's own tag (as the CMMS has it; may be messy) | Asher |
| description | free text as exported (e.g. "HAAS VF2 MILL #3") | Asher |
| machine_type, make, model, serial, year_built | identity (may be blank or wrong: that's the point) | Asher |
| condition | good / fair / poor / unknown | Asher |
| criticality | line_stop / degraded / none | Asher |
| redundant_with | machine_id that can cover for it (blank if none) | Asher |
| replacement_value_low, replacement_value_high | cost to replace the whole machine | Brandon |
| book_value | net book value, if known (never equals replacement value) | Brandon |

### `<plant>/spares.csv` (ERP storeroom export: what's on the shelf)
| Column | Meaning | Owner |
|---|---|---|
| spare_id, plant_id | | Asher |
| material_no | the plant's own stock number | Asher |
| description | as the ERP has it (often abbreviated; duplicates hide here) | Asher |
| manufacturer, part_no | if recorded (often blank) | Asher |
| qty, bin | how many, where | Asher |
| last_moved_on | last issue/receipt date (idle-stock signal) | Asher |
| unit_cost_book | what the ERP says it cost | Brandon |

### `<plant>/work_orders.csv` (optional maintenance history)
| Column | Meaning | Owner |
|---|---|---|
| wo_id, machine_id, opened_on, closed_on | | Asher |
| type | `breakdown`, `preventive`, `repair`, `replace` | Asher |
| component_id | if known | Asher |
| downtime_hours | how long the line was down | Asher |
| parts_cost, labor_cost, rush (yes/no) | | Brandon |
| notes | free text | Asher |

### `<plant>/readings.csv` (what the scan read: one row per component)
| Column | Meaning | Owner |
|---|---|---|
| reading_id, plant_id, machine_id, component_id | | Asher |
| photo_id | blank when simulated (no real photo) | Asher |
| raw_text | exactly what was read off the label (typos, missing dashes, cut-offs) | Asher |
| component_type_hint | plc / drive / hmi / … as seen | Asher |
| method | `vision_sim` (simulated scan), `vision` (real photo), `list` (equipment list) | Asher |
| confidence | read confidence 0–1 | Asher |
| date_code | year on the label / install year (drives age → CapEx timing) | Asher |

### `<plant>/photos.csv` (manifest)
| Column | Meaning | Owner |
|---|---|---|
| photo_id, plant_id, machine_id | which machine | Asher |
| file | path under `photos/` | Asher |
| photo_kind | nameplate / cabinet / component_label / overview | Asher |
| taken_on, quality (`ok` / `blurry` / `glare` / `cut_off`) | | Asher |

## 5. Reference data
### `data/reference/kb.csv` (knowledge base: one row per part number)
| Column | Meaning | Owner |
|---|---|---|
| kb_id, manufacturer, family, part_no, description | identity | Asher |
| component_type | from §3 | Asher |
| aliases | other ways the part is written, separated by `;` (e.g. "1756L61;1756-L61/B") | Asher |
| lifecycle_status, status_date | from §3, with the date it took effect | Asher |
| typical_life_years_low, typical_life_years_high | | Asher |
| annual_failure_rate_low, annual_failure_rate_high | optional override. **The default failure probability comes from an age-band parameter in `valuation.py`** (age, condition, duty), not lifecycle status. Discontinued raises *hours down*, not the odds. | Brandon |
| successor_part_no | official replacement (also a row in alternatives.csv) | Asher |
| migration_cost_low, migration_cost_high | engineering + install to move to the successor | Brandon |
| migration_downtime_hours | planned downtime to migrate | Brandon |
| lead_time_wks_new | lead time for a new unit from the manufacturer | Brandon |
| source_url, checked_on | where the lifecycle info came from | Asher |

**Part value is not typed into the KB.** It's computed from listings (below).

### `data/reference/listings.csv` (market listings: the basis for part value)
**How we value a part:** search several online sources (OEM and authorized distributors, refurbishers, surplus dealers, eBay and other marketplaces) and record **every listing found**, aiming for **at least 3 listings per part**. Value = the price range across listings, per condition.

| Column | Meaning | Owner |
|---|---|---|
| listing_id, kb_id, part_no | which part (part_no as listed, may differ slightly) | Brandon |
| channel | from §3 | Brandon |
| seller, seller_location | | Brandon |
| authorized | yes / no (authorized by the manufacturer) | Brandon |
| condition | new / new_surplus / refurbished / used / for_repair | Brandon |
| price, currency, qty_available | asking price for one unit | Brandon |
| sold_price | if it's a completed sale (stronger evidence than an ask) | Brandon |
| shipping, lead_time_days, warranty_months | | Brandon |
| seller_rating, seller_sales_count, returns_accepted | inputs to the trust score | Brandon |
| trust_score | 0–1, computed by `xray/sourcing.py` from the above | Brandon |
| url, seen_on | evidence; required | Brandon |

### `data/reference/alternatives.csv` (when the exact part isn't available)
| Column | Meaning | Owner |
|---|---|---|
| alt_id, kb_id | the part we need | Asher |
| alt_part_no, alt_manufacturer | the candidate | Asher |
| alternative_kind | successor / compatible / similar | Asher |
| found_by | `oem_lifecycle`, `distributor`, `manual`, `similar_part_search` (**TBD: possible Physna collaboration**) | Asher |
| fit_notes | what changes (mounting, wiring, firmware, programming) | Asher |
| engineering_needed | yes / no | Asher |
| source_url | | Asher |

## 6. Registry tables (built by `seed.py` and the pipeline, inside SQLite)
`fund`, `company`, `plant`, `plant_financials`, `line`, `machine`, `component`, `spare_stock`, `work_order`, `photo`, `evidence`, `kb_entry`, `listing`, `alternative`, mapped 1:1 from the files above. Plus:

| Table | Columns | Built by |
|---|---|---|
| `component` | component_id, machine_id, kb_id (blank if unmatched), part_no_read (as read), component_type, date_code, confidence (0–1), method, needs_review (yes/no), review_reason, evidence_id | Asher (vision + matching) |
| `evidence` | evidence_id, entity_type, entity_id, photo_id, reading_json (raw vision output), source_url, confidence, reviewer, reviewed_on | Asher |
| `spare_match` | spare_id → kb_id link (normalized from messy storeroom text), confidence | Asher (matching) |

## 7. Outputs (pending Brandon's OK)
| Output | Columns | Produced by |
|---|---|---|
| `part_valuation` | kb_id, condition, n_listings, price_low (25th pct), price_mid (median), price_high (75th pct), sold_n, confidence (`high` ≥ 3 listings, `low` 1–2, `none` 0 → see alternatives), as_of | Brandon `xray/sourcing.py` |
| `sourcing_recommendation` | component_id, action (use_shelf_spare / buy_spare / migrate / monitor), spare_id (if on a shelf at any plant), best_listing_id, alt_id, reason | Brandon `xray/sourcing.py` (**shelf first, then outside**) |
| `capex_by_year` | company_id, plant_id, year, capex_type (`growth` only if typed in by the user), capex_low, capex_high, driver_component_ids | Brandon `xray/valuation.py` |
| `spof` | component_id, line_id, criticality, annual_failure_rate, hours_down_low/high (depends on sourcing: shelf / lead time / migration), downtime_exposure_per_year_low/high (prob × hours × $/h), why | Brandon `xray/valuation.py` (reads `sourcing_recommendation`) |
| `deal_adjustment` (deal lens only) | company_id, deferred_capex_low/high, suggested_price_reduction_low/high, suggested_holdback, rationale | Brandon `xray/valuation.py` |
| `plant_savings` + `price` | plant_id, lever, savings_low/base/high, one_time (yes/no), in_price_base (yes/no; one-time release and downtime avoided are shown separately); price_per_plant_low/high, value_capture_pct, customer_payback_months, failed_checks | Brandon `xray/pricing.py` |
| `accuracy` | field, records, predicted, correct, precision, recall, ci_low, ci_high | Asher `xray/evaluate.py` |

## 8. Answer key (`data/truth/<portfolio_id>/`, read only by evaluate.py)
| File | Columns |
|---|---|
| `components.csv` | component_id, kb_id, part_no, lifecycle_status |
| `spare_matches.csv` | spare_id, kb_id (what each messy shelf row really is) |
| `duplicates.csv` | spare_id_a, spare_id_b (same part under different names) |
| `spof.csv` | component_id, why (planted line-stopping single points of failure) |
| planted moments | a Plant B spare that Plant A needs; obsolete controllers; a duplicate part; one part with no listings (tests the alternatives path) |

## 9. Rules
- **Every number shown traces to a row:** evidence, `kb.source_url`, or `listings.url`. The evidence drawer shows it.
- **Money is always a range.** Part value comes from listings (≥ 3 where possible), never typed in.
- **Confidence < 0.8, a big-ticket item, or a part with < 3 listings → `needs_review`.** Never silently used.
- **No manufacturer, part or plant names in logic code.** They live in the data.
- **Listings:** use official APIs and partner feeds where available, respect each site's terms of use, and always show counterfeit risk for non-authorized sellers.
- **Vision responses are cached by image hash.** Only the live photo needs a real API call.
