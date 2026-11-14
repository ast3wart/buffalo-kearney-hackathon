# Architecture

```
data/generated/*.csv  (or data/sample/ while the generator is being built)
        │
        ▼
afterlife/match.py ──► links.csv ──► afterlife/evaluate.py ──► precision / recall
        │                                  (vs truth_links.csv)
        ▼
afterlife/detect.py ──► alerts.csv
afterlife/cost.py   ──► lifecycle cost per product
        │
        ▼
afterlife/brief.py  ──► supplier brief (markdown, LLM-filled template)
        │
        ▼
app/streamlit_app.py: Linking summary → Alert → Brief
```

## Modules and owners
| Module | Owner | Notes |
|---|---|---|
| `afterlife/generate.py` | A | Realistic noise + planted spike. Calibrate with `data/reference/` |
| `afterlife/match.py` | A | Order: exact part number → failure code + product BOM → fuzzy text (rapidfuzz) |
| `afterlife/evaluate.py` | A | Precision and recall per source_table and per method |
| `afterlife/detect.py` | B | Claims per 1,000 units by (part, build_month), pooled across products. Flag ratio ≥ 2 with ≥ N claims |
| `afterlife/cost.py` | B | Build cost = Σ qty_per × production price. Lifecycle cost = build + spares + warranty per unit |
| `afterlife/brief.py` | B | Template first, LLM polish second |
| `afterlife/io.py` | shared | `load(dir)` → dict of DataFrames. Switches between sample and generated data |
| `app/streamlit_app.py` | B | |

## How the claim matching works (the novel part)
For each claim:
1. If `causal_part_no` is in that product's BOM, accept it (high confidence).
2. Otherwise narrow down: parts in **that product's BOM** whose `category` is in the failure code's `likely_categories`.
3. Rank the remaining candidates by fuzzy similarity between `claim_text` and the part description (with abbreviations expanded).
4. One candidate means high confidence. Several close candidates mean low confidence, which is where the LLM tie-breaker (stretch) would come in.

## Spike detection
For each (part_no, supplier_id), pool claims from **all products** that use the part, and compute claims per 1,000 units built for each build_month. Baseline = median of earlier months. Flag months where rate / baseline ≥ 2 and there are at least 10 claims. That's simple and explainable, and enough for the demo.
