# API contract

FastAPI at `:8000`, interactive docs at `/docs`. **Every data endpoint takes `?company=<company_id>`** (list from `GET /companies`). Handlers stay thin: the logic lives in `afterlife/`.
**Every response gets a Pydantic model**, so the frontend gets generated types (`npm run types:api`).

| Method | Path | Thread (🛠 Brandon / 💲 Asher) | Returns | Status |
|---|---|---|---|---|
| GET | `/health` | shared | run time, companies, table row counts | ✅ done |
| GET | `/companies` | shared | company_id, name, industry, data_as_of | ✅ done |
| GET | `/overview` | 💲 spend | coverage (all / high-confidence), build vs. lifecycle cost per product, spare overspend, harmonization (incl. acquired plant), warranty % of revenue | ✅ done |
| GET | `/markups` | 💲 spend | part, production $/EA, service $/EA, ratio, overspend (period + per year); high-confidence links only | ✅ done |
| GET | `/compliance?finding=` | 💲 spend | paid vs the supplier's own agreement (price leakage, spares clause), with the agreement document and the contract price | ✅ done |
| GET | `/harmonization` | 💲 spend | lines paid above the best supplier × plant price: part, supplier, plant, price, best price, savings | ✅ done |
| GET | `/alerts` | 🛠 warranty | alert rows (see data contract) | todo |
| GET | `/claim-rates/{part_no}` | 🛠 warranty | **both views:** raw claims per 1,000 by build month, *and* MIS-window rates (mature months only) + heatmap | todo |
| GET | `/links?source=&q=&min_conf=` | shared | linking explorer rows: raw record + part + method + confidence | todo |
| GET | `/accuracy` | shared | precision and recall by company × source_table × method (prairie = tuned, others = **holdout**) | todo |
| POST | `/brief/{supplier_id}` | shared | streams markdown (`text/plain` chunks). Template if no API key | todo |

## Response shapes (agreed at CP0, tweak via a handoff note)
```jsonc
// GET /overview  💲
{ "company": "Prairie Utility Vehicles", "data_as_of": "2026-10-31",
  "coverage": { "production_spend_pct": 0.97, "service_spend_pct": 0.81, "claims_pct": 0.74 },
  "products": [ { "product_id": "UV-400", "build_cost": 2140.5, "spares_per_unit": 96.2,
                  "warranty_per_unit": 118.4, "lifecycle_cost": 2355.1 } ],
  "spare_overspend_usd": 412000 }

// GET /alerts  🛠
[ { "part_no": "200-1180-01", "description": "SEAL KIT,HYD CYL,40MM BORE",
    "supplier_id": "S-022", "supplier_name": "Keystone Seal Works",
    "products_affected": ["UV-400", "UV-600", "TR-250"],
    "start_build_month": "2026-04", "mis_window": 3,
    "baseline_rate": 4.1, "current_rate": 14.6, "ratio": 3.6,
    "claims": 29, "exposure_usd": 2100000,
    "recovery_opportunity_usd": { "low": 525000, "high": 1050000 },   // scenario 25–50% capture
    "status": "linked_pending_review" } ]

// GET /claim-rates/{part_no}  🛠  (both views, decided at CP0)
{ "mis_window": 3,
  "raw":  [ { "build_month": "2026-03", "units": 640, "claims": 3, "rate": 4.7 } ],          // intuitive but biased
  "mis":  [ { "build_month": "2026-03", "units": 640, "claims": 3, "rate": 4.7,
              "mature": true, "is_spike": false } ],                                          // what alerts use
  "heatmap": [ { "build_month": "2026-03", "mis": 1, "cum_rate": 1.6 } ] }
```
`exposure_usd` = cost of claims **linked** to this part/supplier. `recovery_opportunity_usd` = exposure × a **scenario** capture rate (25–50%), always shown as a range with the label *"claims linked to a candidate part/supplier, pending engineering and contract review"*. Never call it "recoverable" or "owed" (see docs/plan/concept.md, "What Afterlife does NOT do").

## Screens (web/)
| Route | Screen | Thread | Calls |
|---|---|---|---|
| `/` | Overview | 💲 spend | `/overview`, `/accuracy` |
| `/links` | Linking explorer | shared | `/links` |
| `/alerts` | Early warning | 🛠 warranty | `/alerts`, `/claim-rates/{part}` |
| `/brief/[supplier]` | Supplier brief | shared | `POST /brief/{supplier}` |
