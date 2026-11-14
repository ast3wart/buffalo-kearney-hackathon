# Scope: what we build, what we cut

Two people, about 20 working hours each, submission due **Sun 8:30 AM**.

## Must-haves (MVP)
| # | Piece | Definition of done |
|---|---|---|
| M1 | Data generator | `python -m afterlife.generate` writes all tables in `docs/build/data-contract.md` to `data/generated/`, with planted links and **one planted failure spike** |
| M2 | Matching | Spend lines and claims → `links.csv` with method + confidence. Exact part number → failure code + BOM → fuzzy text |
| M3 | Accuracy | `python -m afterlife.evaluate` prints precision and recall vs. planted answers |
| M4 | Early warning | `alerts.csv`: parts whose claims per 1,000 units jump vs. baseline, across products, by build month |
| M5 | Cost | Build cost vs. lifecycle cost (spares + warranty) per product |
| M6 | Brief | Markdown supplier brief: spike, $ exposure, spare-part markup line |
| M7 | App | Next.js, 4 screens (Overview, Linking explorer, Early warning, Brief) over FastAPI. See `docs/build/api.md` |

## Stretch (only after M1–M7 work end to end)
- LLM tie-breaker for low-confidence claim matches
- Spare-part harmonization as its own screen
- CSV upload with column mapping
- Better charts (claim rate over build months with the spike highlighted)

## Cut (don't build)
Streamlit, embeddings, review UI, Sankey, auth, deploying (unless the submission requires a URL), tariff simulator, multi-level BOM explosion, a database server (DuckDB file only).

## Timeboxes
- Claim matching: **stop tuning at Sat 5 PM**, and ship whatever accuracy we have.
- Velocity: about 2 hours total, Sat night with the deck.
- **Feature freeze Sat 10 PM.** After that, only bug fixes, the deck, and a backup video.

## Risks
| Risk | Mitigation |
|---|---|
| Blocked waiting on the generator | `data/sample/` hand-made data exists from hour 0, same format |
| Claim matching eats the day | Timebox above, and failure-code → BOM matching alone is a valid fallback |
| Integration breaks Sat night | Integrate at **Sat 12:30** and **Sat 6 PM**, not just at the end |
| Live demo fails | Record a backup video Sat night |
