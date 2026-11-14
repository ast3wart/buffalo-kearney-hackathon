# 5 · Proof of concept: what we build

[← index](index.md)

**Goal:** prove the **recurring / PE story**, not only diligence, without adding much scope.
**Main move:** make the synthetic data a **small portfolio of 2 plants** instead of 1 factory. That one change makes the registry, the cross-plant spare match and the "portfolio" pitch real.

## Must-have, in build order (the demo works if we stop after any step from 6 on)
| # | Piece | Details | Real or simulated | Reuses |
|---|---|---|---|---|
| 1 | **Synthetic portfolio + answer key** | 1 PE fund → 2 plants → ~3 lines each → ~25–40 machines → components. **Plant these answers:** obsolete controllers, one line where a single point of failure (SPOF) stops everything, a duplicate part under different names, and **a spare at Plant B that Plant A needs**. Line revenue/day for downtime cost. | Synthetic, and we say so | Afterlife generator + answer-key approach |
| 2 | **KB, ~30 components** | Lifecycle status (OEM-style categories), successor, replacement-cost range, lead time, source URL, `class_code` | Curated, sourced where possible | — |
| 3 | **Vision extraction** | Photo → JSON (make, model, catalog no., serial, year, components seen) + confidence + "unclear". `claude-sonnet-5-5`. Cached by image hash | **Real** | — |
| 4 | **Normalize + match** | Reading → KB entry. Low-confidence matches go to a review queue | Real | `xray/matching.py` |
| 5 | **Accuracy** | Precision/recall vs. the answer key, shown in the app | Real | `xray/evaluate.py` |
| 6 | **Registry view** | Fund → Plant → Line → Machine → Component tree: age, status, remaining life, value range | Real | Next.js shell |
| 7 | **Risk outputs** | **CapEx cliff** by year (range bands); SPOFs per line with $/day downtime exposure; **"pay $X less"** number | Real calculation | Recharts |
| 8 | **Evidence drawer** | Click any number → photo, reading, KB source, confidence, reviewer | Real | — |
| 9 | **Sourcing, 3 parts** | Curated offers: channel, authorized yes/no, price, lead time, condition, trust score → **buy / migrate / monitor**. Callout: **"Plant B has 2 on the shelf"** | Curated offers, real logic | — |
| 10 | **Live moment** | Photograph a real nameplate at the venue (HVAC, projector, vending machine) → it appears in the registry | Real | step 3 |

## Nice to have (only if ahead of schedule)
- An export (CSV/PDF) "for the appraiser's report". Supports the channel story.
- A portfolio dashboard: total CapEx cliff across both plants, SPOF count, idle spare value.
- A retake prompt for blurry or glare-covered photos.

## Cut, and name as roadmap on stage
Live marketplace search · sensors · login · mobile field app · trained component detector · real CMMS/ERP connectors · reading maintenance logs at scale.

## Demo script (~3 min)
1. "Fund X just bought Plant A." Open the registry: Plant A, lines, machines.
2. CapEx cliff → **"pay $X less"** → click a bar → evidence drawer (photo, KB source, confidence).
3. SPOF: "Line 2 stops if this discontinued drive fails. Lead time 20 weeks."
4. Sourcing → **"Plant B already has 2 on the shelf."** ← the portfolio moment
5. Accuracy tile: precision/recall on the planted answer key.
6. Live photo → it appears in the registry.

## Rough split (adjust to who's ahead)
| Asher | Brandon |
|---|---|
| 1 Synthetic portfolio + answer key, 2 KB | 3 Vision, 4 matching, 5 accuracy |
| 7 Risk outputs + API | 6 Registry view, 8 evidence drawer |
| 9 Sourcing data + deck | 10 Live flow, demo run-throughs, backup video |
