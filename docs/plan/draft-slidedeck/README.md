# Final slide deck

> **Current version: [deck-v2.html](deck-v2.html)** (6 slides + 9 appendix, mentor layout). Read **[deck-v2-notes.md](deck-v2-notes.md)** for what was left out, the boxes Asher fills on slide 4, and how the health score and savings are calculated. Everything below describes v1.

**[deck-v1.html](deck-v1.html)** is the v1 final, **shortened Sat ~11 PM: 11 slides + 7 appendix**. Open it in a browser. The longer first cut is kept as [deck-v1-long.html](deck-v1-long.html); the slide table below describes that longer cut.

**Short version, main slides:** 1 Title · 2 Why (case study slot) · 3 Solution · 4 Proof · 5 Bad data · 6 Customer and market · 7 Competition · 8 Value capture · 9 Roadmap vs expansion · 10 Objections · 11 Recommendation. **Appendix:** A1 Go-to-market · A2 Market sensitivity · A3 Condition sensing · A4 Unit economics · A5 Deal view · A6 Liquidity · A7 Sources.

**Downtime (updated to `brandon/downtime-horizon`, demo.db rebuilt from the seed files):** the deck no longer shows a yearly exposure figure. Slide 4 shows one event: Toledo Line 2 drive, worst-case outage 176 h → 40 h with Fort Wayne's spare, ~$84k at stake. Slide 8 and A4 show downtime avoided at Toledo (~$19k a year, range $2–71k) as shown, never priced.

- **← →** or space to move, **p** (or the Present button) for full screen, one slide at a time.
- **Print → Save as PDF** gives one 16:9 page per slide (turn on "Background graphics").
- Add `#check` to the address to list any slide whose content runs past its footer (shown in the tab title). Run it after every edit.

Built from [pivot-plan/04-pitch-deck-mockup.html](../../archive/pivot-plan/04-pitch-deck-mockup.html) (structure and style), [final-refinements/02-roadmap-vs-expansion.html](../../archive/planning-notes/02-roadmap-vs-expansion.html) (slides 5, 11, 12) and live numbers from the demo database (Sat Nov 14, ~10 PM, branch `brandon/rare-part`).

## Slides
| # | Slide | Changed from the mockup |
|---|---|---|
| 1 | Title | "plant owner", not "buyer"; real cabinet photo (Wikimedia, credited) |
| 2 | **Why** | Own-plant framing; new card "maintenance plans miss them"; **case study slot (empty)** |
| 3 | Solution | Worked example: the Kinetix 6000 on Toledo Line 2, photo to decision |
| 4 | Proof | Real accuracy and demo findings; states what is not proven |
| 5 | Plants with bad data | New: the data ladder |
| 6 | Customer | Plant owners first, deal partner last |
| 7 | Competition | Joltek precedent moved here |
| 8 | Value capture | Filled from the money model |
| 9 | Market | Filled from the market model |
| 10 | Go-to-market | Consulting-firm break-even added |
| 11 | Roadmap vs expansion | New: committed (0–3) vs vision (4–5, later) |
| 12 | Condition sensing | New: thermal clip-on, marked hypothesis |
| 13 | Risks and objections | Rewritten as 7 objections, each with a test |
| 14 | Recommendation | 3 paid plant pilots + 1 portfolio |
| A1–A4 | Unit economics · deal view · liquidity · sources | Filled; A4 is new |

## To fill before submission
1. **Slide 2, case study slot.** It needs a real, sourced case where a plant followed its maintenance plan and a discontinued electronic part still stopped the line. Leads already in our research (`docs/research/velocity.md` §migration costs and `velocity-raw-notes-nov14.md`), **all vendor cases, none verified for this use yet**:
   - Liberty Automation: a Siemens S5 failure, 3 days down
   - EU Automation: a 315 kW Siemens drive flown in on a 36-hour charter
   - Neuron Industries: CureWood S5 retrofit

   If none can be sourced well enough, delete the slot; the grid closes up to two columns by changing `1fr 250px 1.15fr` to `1.4fr 1fr` on that slide.
2. **Slide 12, two ⚠ cite tags.** Replace with sources from Asher's thermal research, or move the slide to the appendix.
3. **Slide 1.** Team names and date are as written; change if needed.

## Decisions made in this version (change if you disagree)
- **Price and market use the model's numbers:** $5.9k per plant base, **$7.6M** recurring revenue at 5% of plants, $152M at all plants. The roadmap doc still says $10–25k and $13–32M. The deck calls the model figure a floor and says why.
- **Deal numbers use the current model:** $429k price cut ($79k controls + $350k machines). The holdback is shown as **~$1.3–1.7M** because the app passes a 10% discount rate ($1.69M) and the model's own default is 25% (~$1.3M, from the handoff note, not rerun here).
- **Accuracy** is always shown with "rendered test photos".
- **"38 of 119 at risk"** uses the app's own at-risk count for the 5 owned plants.

## Numbers used and where they came from
| Number | Source |
|---|---|
| 127 / 129 · 100% / 98% · 112 of 112 · 17 to review | `GET /accuracy` |
| 119 parts · 38 at risk · 14 line stoppers · 23 idle shelf items | `GET /portfolio` totals |
| $58–232k / yr top line stopper, Toledo | `GET /plants/PA/spof` |
| $47.7k savings · $9.5k price · 2.4 months payback · $1.8–33k range | `GET /plants/PA/savings` |
| $429k · $79k + $350k · $1.69M holdback at 10% | `GET /companies/CO-TILLMAN/deal` |
| $5.9k base · $7.6M · $152M · sensitivity table · 45 engagements | `python scripts/market_model.py` |
| Everything else | the app's Sources page (`web/src/app/sources/page.tsx`) |

If the demo data is re-seeded (for example after adding the rare part), rerun these and update slides 4, 8, 9, A1, A2 and A4.
