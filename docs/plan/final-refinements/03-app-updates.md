# 3 · App / proof of concept: what to update before freeze

[← index](index.md)

**Rule:** build only what removes an objection on stage. Everything else goes on the roadmap slide. Stop after any item; the demo still works.

## Must do (small, high value)
| # | Change | Objection it removes | Where | Size |
|---|---|---|---|---|
| 1 | **README + AGENTS status.** Replace "MVP not built yet" with what runs; update the file layout. | "Is it real?" (judges open the repo first) | `README.md` §Status and §What's already here; `AGENTS.md` §Layout | 10 min |
| 2 | **Rare part.** Add Westinghouse Numa-Logic PC-1100 to the KB with its lifecycle source, one alternatives row, and place it in a Tillman machine. Re-seed. | Shows the "no listings anywhere → successor" path | `data/reference/kb.csv`, `data/reference/alternatives.csv`, `scripts/make_demo_data.py`, then `python scripts/seed.py data/seed/demo` | 30 min (Asher; see [to-asher](../../team/handoffs/to-asher.md)) |
| 3 | **One price, one ARR, one deal number.** Make the Sources page, the roadmap market row and the deck agree with the model. | "Your numbers don't agree" | `web/src/app/sources/page.tsx` (price ~$10k line, Tillman "$73k cut + $130k holdback" line); `docs/plan/roadmap-equipment-xray.md` market table | 20 min |
| 4 | **Deal view discount rate.** The route passes 10%; the model's default is 25%, which changes the holdback (~$1.7M vs ~$1.3M). Pass `None` to use the model's value, or agree on one. | Same | `api/main.py`, `company_deal` (last route) | 5 min |

## Should do (the bad-data answer, live)
| # | Change | Objection it removes | Where | Size |
|---|---|---|---|---|
| 5 | **Review queue page.** List the 17 flagged parts: photo, what was read, reason, confidence, link to the part. Split "no KB match" into *commodity, no risk* and *unknown, needs a person*. Read-only is enough; a Confirm button is a bonus. | "What about bad readings?" and "does a person check?" | New `GET /review` in `api/main.py` (filter `component.needs_review == "yes"`, columns already loaded for the registry route); new `web/src/app/review/page.tsx`; add to `LINKS` in `web/src/components/Nav.tsx`; make the "17 to review" text on the portfolio card a link | 45–60 min |
| 6 | **Data-ladder badge on each plant card.** Show which inputs the plant gave (photos, list, storeroom) and what the next rung unlocks. Derive it from which seed tables have rows for the plant. | "Plants have terrible data" | `GET /portfolio` tiles in `api/main.py`; `web/src/app/page.tsx` | 30 min |
| 7 | **Reconciliation counts on the plant page.** On the list but no photo · photo but not on the list · same spare under two names (already detected by spare matching). | Same; turns bad data into a finding | `api/main.py` (new small route or add to `/plants/{id}/registry`); `web/src/app/plants/[plantId]/page.tsx` | 45 min |

## Only if ahead
| # | Change | Why | Where | Size |
|---|---|---|---|---|
| 8 | **CSV export** of a plant's at-risk parts with an evidence column | "How does this reach the appraiser / CapEx committee?" | New `GET /plants/{id}/report.csv` | 20 min |
| 9 | **Deal view: two lines** ("control parts" vs "machines at end of life") | Explains why the cut is $429k, not $79k | `web/src/app/plants/[plantId]/page.tsx` (the `Deal` type and stats); columns `controls_deferred_*`, `machine_deferred_*` already returned | 20 min |
| 10 | **"Condition: not measured yet" slot** on the part health page, labeled as roadmap | Sets up the thermal expansion without faking it | `web/src/app/components/[componentId]/page.tsx` | 10 min |

## Do not build (name on the roadmap slide)
Live marketplace search · logins · maintenance-system connections · PDF reports · phone app · any sensor or thermal feature · editing the registry in the app.

## Wording to keep honest on screen
- Accuracy: keep "**on rendered test photos**" next to 127 / 129.
- Price and savings: keep "**extrapolated to a whole plant**".
- Thermal / sensors: "**research in progress**", never "coming soon" with a date.
- Data ladder rungs 3–4: "**roadmap**".

## After any change
```bash
./scripts/checkpoint.sh                                             # tests + type check
python scripts/export_openapi.py && (cd web && npm run types:api)   # if a route changed
./scripts/demo.sh                                                   # rehearse on the stage build
```
Heads-up rule still applies: `api/main.py` route shapes are a shared file, so leave a line in the other person's inbox first.
