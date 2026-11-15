# Final refinements: platform vision, objections, app polish

**Status:** DRAFT, Sat Nov 14, late evening. Written for both of us to edit. **Submission due Sun Nov 15, 8:30 AM; feature freeze ~1 AM.**

**Goal:** polish the final platform vision and remove the major objections a judge can raise, without adding much build.

> The [roadmap](../roadmap-equipment-xray.md) is still the source of truth. This folder **proposes** changes to it. Nothing here overrides it until we both agree and edit the roadmap.

| # | Doc | Answers |
|---|---|---|
| 1 | [01-standing-and-roadmap.md](01-standing-and-roadmap.md) | Where the project stands, what makes it a complete platform, plants with bad data, supporting tools, objections and answers |
| 2 | [02-roadmap-vs-expansion.html](02-roadmap-vs-expansion.html) | Three slides in the deck mockup's style: roadmap (committed) vs expansion vision (incl. the clip-on thermal sensor), and the data ladder. Open in a browser. |
| 3 | [03-app-updates.md](03-app-updates.md) | What to change in the app / proof of concept before freeze, in priority order, with files |
| 4 | [04-downtime-waukesha-discrepancy.md](04-downtime-waukesha-discrepancy.md) | **Open issue:** the Waukesha and portfolio downtime numbers in the rework report do not reproduce on a clean rebuild |
| 5 | [05-feedback-notes.md](05-feedback-notes.md) | **Mentor feedback turned into a deck layout:** problem, solution (hardware first), demo; pricing not as a percent of savings; app changes it implies. Not yet applied. Raw notes at the bottom. |

## The one idea that ties it together
**The data ladder.** A plant starts with whatever it has, even only a phone camera, and each rung narrows the ranges and unlocks more outputs:

| Rung | The plant gives us | What it unlocks |
|---|---|---|
| 0 | Photos only | Registry of critical parts, lifecycle status, CapEx range (wide) |
| 1 | + equipment list | Reconciliation (what the list misses), line-stopper ranking |
| 2 | + storeroom stock | Shelf-first sourcing, idle spares, duplicates |
| 3 | + maintenance history | Failure rates from the plant's own record, audited savings |
| 4 | + condition sensing (clip-on thermal, Asher's research) | Health by measured condition, not only by age |

It answers "what about plants with bad data?" (start at rung 0), "how does the registry stay current?" (rungs 3–4) and "where do sensors fit?" (rung 4, placed where the registry says the risk is).
