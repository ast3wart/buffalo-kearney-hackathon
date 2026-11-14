# API contract

FastAPI at `:8000`, interactive docs at `/docs`. Handlers stay thin: the logic lives in `afterlife/`.
**Every response gets a Pydantic model**, so the frontend gets generated types (`npm run types:api`).

| Method | Path | Thread | Returns | Status |
|---|---|---|---|---|
| GET | `/health` | shared | source, run time, table row counts | ✅ done |
| GET | `/overview` | 💲 spend | % linked (spend, claims), build vs. lifecycle cost per product | todo |
| GET | `/markups` | 💲 spend | part, production $/EA, service $/EA, ratio, annual overspend | todo |
| GET | `/alerts` | 🛠 warranty | alert rows (see data contract) | todo |
| GET | `/claim-rates/{part_no}` | 🛠 warranty | build_month, claims, units, rate_per_1000, is_spike | todo |
| GET | `/links?source=&q=&min_conf=` | shared | linking explorer rows: raw record + part + method + confidence | todo |
| GET | `/accuracy` | shared | precision and recall by source_table and method | todo |
| POST | `/brief/{supplier_id}` | shared | streams markdown (`text/plain` chunks). Template if no API key | todo |

## Screens (web/)
| Route | Screen | Thread | Calls |
|---|---|---|---|
| `/` | Overview | 💲 spend | `/overview`, `/accuracy` |
| `/links` | Linking explorer | shared | `/links` |
| `/alerts` | Early warning | 🛠 warranty | `/alerts`, `/claim-rates/{part}` |
| `/brief/[supplier]` | Supplier brief | shared | `POST /brief/{supplier}` |
