# 6 · Tech stack

[← index](index.md)

## Decision: keep the stack, swap the database for the demo
| Layer | Now | Decision | Why |
|---|---|---|---|
| Frontend | Next.js 15 + Tailwind + Recharts | **Keep** | The shell, generated API types and CI already work. Recharts handles the CapEx cliff. |
| API | FastAPI (Python) | **Keep** | Python is where the matching, evaluation and Anthropic SDK code lives |
| Vision | Anthropic SDK, `claude-sonnet-5-5` | **Keep** + **disk cache by image hash** | The demo works offline or if the API is slow. Only the live photo needs a real call. |
| Database | Postgres (planned; not in `requirements.txt`) | **SQLite via SQLModel/SQLAlchemy** | One file, no install step on Windows, can ship pre-seeded, and keeps the relational registry model. Fewer things break mid-demo. |
| Data | — | **CSV/JSON seed files + `scripts/seed.py`** | Rebuilds the database in seconds. Judges can see exactly what we generated. |
| Tests/CI | pytest + `checkpoint.sh` | **Keep** | Same as now |

**On stage:** "Postgres in production. The database URL is the only change." With SQLAlchemy, that's true.

## Why not the alternatives
- **Postgres now:** extra install and setup, and nothing in the demo needs it. Skip for the weekend.
- **DuckDB** (mentioned in idea doc §9): great for analytics, but the registry is relational CRUD + a tree view, so SQLite fits better. Update §9 once this is agreed.
- **Single-app rewrite (Next.js API routes only, or Streamlit):** throws away working code and Python. Not worth the hours.

## Minimal schema (matches the registry data model)
```
fund(id, name)
company(id, fund_id, name, acquired_on)
plant(id, company_id, name, location)
line(id, plant_id, name, revenue_per_day)
machine(id, line_id, make, model, serial, year, photo_path, value_low, value_high)
component(id, machine_id, kb_id, part_no, type, date_code, status, confidence, needs_review)
kb_entry(id, manufacturer, family, part_no, class_code, lifecycle_status, successor, cost_low, cost_high, lead_time_wks, source_url)
spare_stock(id, plant_id, kb_id, qty, bin, last_moved_on)
sourcing_offer(id, kb_id, channel, seller, authorized, price, condition, lead_time_wks, trust_score, url, seen_at)
evidence(id, entity_type, entity_id, photo_path, reading_json, source_url, confidence, reviewer)
```

## Install additions
`sqlmodel` (or `sqlalchemy`) in `requirements.txt`. Nothing new on the web side.

## Demo safety
- A seeded `demo.db` in the repo (or rebuilt by `seed.py`) + cached vision responses.
- A backup screen recording of the full demo.
- Run `./scripts/checkpoint.sh` before every merge.
