# Architecture

**Stack:** Python (pandas, DuckDB, rapidfuzz) · FastAPI · Next.js 15 (App Router) + Tailwind + Recharts · Claude API for the brief.

**Key decision: precompute.** `python -m afterlife.run` runs the whole pipeline once and writes `results.duckdb`. The API mostly *reads* it. Only `POST /brief` does live work (an LLM call, with a template fallback). The demo stays fast and safe, and the pipeline can be rerun as often as we like without touching the frontend.

```
data/generated/ (or data/sample/)
        │
        ▼
afterlife/  ── python -m afterlife.run ──►  results.duckdb
  generate_spend / generate_claims             (raw tables + links, alerts, costs, markups)
  match_spend    / match_claims                        │
  detect (W) · cost (S) · evaluate · brief             ▼
                                              api/main.py (FastAPI, :8000)
                                                       │  openapi.json → web/src/lib/api-types.ts
                                                       ▼
                                              web/ (Next.js, :3000) — 4 screens
```

## Ownership by thread
| Piece | 🛠 WARRANTY thread | 💲 SPEND thread |
|---|---|---|
| Data | `generate_claims.py` | `generate_spend.py` |
| Matching | `match_claims.py` | `match_spend.py` |
| Insight | `detect.py` (spikes) | `cost.py` (lifecycle cost, markups) |
| Brief | `brief.warranty_section()` | `brief.pricing_section()` |
| API | `/alerts`, `/claim-rates/{part}` | `/overview`, `/markups` |
| Screen | Early warning | Overview |
| Shared | `match.py` (normalize), `evaluate.py`, `brief.make_brief`, `/links` + Linking explorer, `/brief` + Brief screen, app layout | |

## How claim matching works (warranty)
1. `causal_part_no` present and in that product's BOM → accept (high confidence).
2. Otherwise narrow down to parts in **that product's BOM** whose `category` is in the failure code's `likely_categories`.
3. Rank by fuzzy similarity of the normalized claim text vs. the part description.
4. One clear winner → high confidence. A close call → low confidence (LLM tie-break is stretch).

## How spend matching works (spend)
1. Supplier part number crosswalk, once one exists from earlier matches.
2. Spec codes in the description (`6204`, `M20X1.5`, `40MM`) that match the part master.
3. Fuzzy description match within category.
4. Convert units (`BX10` → per EA) before any price comparison.

## Spike detection (warranty)
For each (part_no, supplier_id), pool claims from **all products** using the part, and compute claims per 1,000 units built for each build_month. Baseline = median of earlier months. Flag ratio ≥ 2 and ≥ 10 claims.

## Running it
```bash
source .venv/bin/activate
python -m afterlife.run                      # → results.duckdb
uvicorn api.main:app --reload --port 8000    # → http://localhost:8000/docs
cd web && npm run dev                        # → http://localhost:3000
# after changing API response models:
python scripts/export_openapi.py && (cd web && npm run types:api)
```
