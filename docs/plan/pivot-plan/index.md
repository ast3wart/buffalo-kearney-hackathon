# Pivot plan: Equipment X-Ray (machinery pivot)

**Status:** DRAFT, Sat Nov 14 (afternoon). Asher + Claude. Builds on [market-validation.md](../../research/market-validation.md) (PR #11), [idea-equipment-xray.md](../idea-equipment-xray.md) and [roadmap-equipment-xray.md](../roadmap-equipment-xray.md). **Submission due Sun Nov 15, 8:30 AM.**

> **Positioning in one line:** the system of record for aging factory equipment, and the acquisition is how you start it.

## Read in this order
| # | Doc | Answers |
|---|---|---|
| 1 | [01-research.md](01-research.md) | What the research says: why we pivoted, what's proven, what isn't |
| 2 | [02-market-validity.md](02-market-validity.md) | Does the market hold up long term? Threats and moat |
| 3 | [03-flywheel-growth.md](03-flywheel-growth.md) | Flywheel, land-and-expand, revenue by stage |
| 4 | [04-pitch-deck-map.md](04-pitch-deck-map.md) + [04-pitch-deck-mockup.html](04-pitch-deck-mockup.html) | VC deck framework (`temp/vc-pitch-deck.md`) adapted to our consulting pitch, slide by slide + an HTML mockup (open in a browser, use ← → keys) |
| 5 | [05-poc-scope.md](05-poc-scope.md) | What we build tonight, in order, with cut lines |
| 6 | [06-tech-stack.md](06-tech-stack.md) | Keep Next.js + FastAPI. Use SQLite instead of Postgres for the demo |
| 7 | [07-integrations.md](07-integrations.md) | External software we assume we fit into (CMMS, ERP, OEM lifecycle, sourcing APIs) |
| 8 | [08-deep-research-prompt.md](08-deep-research-prompt.md) | Prompt for a deep-research run: reindustrialization, PE market, the liquidity angle |

## Decisions in this plan (Brandon: yes / no / change)
1. **Story:** recurring installed-base risk + replacement planning for multi-plant manufacturers and PE portfolios. **Diligence is the entry point**, not the business.
2. **Demo data:** a **2-plant synthetic portfolio** (not 1 factory), so the cross-plant spare-sharing moment is real.
3. **Stack:** keep Next.js + FastAPI. **SQLite + seed files** instead of Postgres for the demo.
4. **Sourcing:** curated offers for 3 parts. Live search goes on the roadmap.
5. **New angle to test:** the product **frees up cash for PE firms** (sell-side readiness, idle spare parts, verified collateral). See docs 3 and 8.

## Open items
- PR #11 is not merged yet.
- §9 of `idea-equipment-xray.md` says DuckDB. This plan says SQLite (see doc 6).
- Confirm the Startup-track switch with the organizers.
- Points marked ⚠️ in these docs need checking before they go on a slide.
