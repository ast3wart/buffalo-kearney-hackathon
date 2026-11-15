# 5 · Mentor feedback → deck layout to act on

[← index](index.md)

**Status:** Sat Nov 14, ~11 PM. Mentor conversation, turned into a layout. **Not yet applied to `deck-v1.html` or the app.** Raw notes are at the bottom, unchanged. Lines marked *(my reading)* are interpretation, not what the mentor said.

## What the mentor said, in five points
1. **The story is good.** Keep it, make it shorter.
2. **Three parts only: problem, solution, demo.** Tell it as situation → action → outcome *(my reading of "sao")*.
3. **Lead the solution with the hardware.** A thermal camera / sensor that diagnoses equipment health. Show what it measures, where the data goes, what it costs and what it changes. The wider platform comes later.
4. **Do not price as a percent of savings.** It is a conflict of interest: we would be measuring the savings we get paid on. Find another variable price.
5. **The downtime number is subjective.** Do not lean on it.

## Deck layout (3 parts, about 6 slides)
| # | Part | Slide | What goes on it | Source today |
|---|---|---|---|---|
| 1 | — | Title | Name, one line | Deck slide 1, as is |
| 2 | **Problem** (1 page) | "Owners do not know the health of their plant equipment" | **Situation:** one preventive-maintenance example, where the schedule was followed and an unmonitored part still stopped the line. Then the chain: unknown health → failures → lost output → lost revenue. One health figure (share of parts at risk). | Deck slide 2, rewritten. Use stats in place of a named case (decided): 83% discontinued in one audit, only 55% have an obsolescence plan, 38 of 119 at risk in the demo |
| 3 | **Solution** | "Start with what the plant has; hardware closes the gap" | The **data ladder** as tiered steps: photos → lists → storeroom → maintenance history → sensing. Hardware is the top rung and the point of the slide. | Deck slide 5, with rung 4 promoted from "research in progress" to the focus |
| 4 | **Solution** | "How the hardware works" | **One diagram:** thermal camera on a cabinet → reading on the device → anomaly found against the part's spec and its own baseline → alert → action in the registry. State: works **without internet** on site, where the data is stored, who can see it, cost per point, expected impact. | Appendix A3, redrawn as a data-flow diagram. **Needs Asher's research for every number.** |
| 5 | **Demo** | In the app, slides embedded | Top down: **select Granite Ridge** (each company's data kept separate) → plant view → **health score** → **live monitoring** → an issue detected → **action and sourcing** → human review → cost savings and downtime reduction. | App. See "App changes" below |
| 6 | — | Close | Roadmap in one line (platform expansion comes later) and the ask: 3 paid plant pilots + 1 portfolio | Deck slides 9 and 11, merged |

**Move to appendix:** proof numbers (4), customer and market (6), competition (7), value capture (8), objections (10). Keep them for questions.

## Demo flow (what the app should show, in order)
1. **Portfolio, top down.** Pick the fund (Granite Ridge). Companies are separate; the fund sees totals.
2. **Plant view** with a **health score** per plant, line and machine.
3. **Live monitoring** *(my reading: a sensor feed on the highest-risk parts)*.
4. **Issue detected → action → sourcing.** Shelf at a sister plant first.
5. **Human review** of anything low-confidence.
6. **Outcome:** cost savings and downtime reduction for that plant.

Differentiators to say out loud: health score, live monitoring, detection through to sourcing, human review.

## App changes this implies
| Change | State today | Size |
|---|---|---|
| Open on fund selection, then drill down | Portfolio page exists; no "select fund" step | Small |
| **Health score** per plant / line / machine | Part health exists (Working / Replace soon / Replace ASAP, life used %); no rolled-up score | Medium: a roll-up of what is already computed |
| **Live monitoring** view | Nothing | Only as a clearly labeled mock-up, unless the thermal research gives real data |
| Slides embedded in the demo | Deck is a separate HTML file | Small: link or iframe from the app |
| Savings and downtime at the end of the flow | On the plant page already | Reorder only |

## Pricing: replace "20% of savings"
The mentor's point: a share of savings makes us the judge of our own fee. Options *(mine, not the mentor's)*:
| Option | Basis | Why it avoids the conflict |
|---|---|---|
| **Per plant, tiered by size** | Number of critical parts or machines in the registry | Countable by the customer; no savings estimate involved |
| **Per monitored point** | Each sensor / cabinet under live monitoring | Scales with the hardware, which is now the focus |
| **Flat platform fee + hardware** | Subscription per plant plus device cost | Simplest to explain |

The savings model stays useful as the **customer's business case** (payback), not as the price formula. Slide 8, appendix A4 and `xray/pricing.py` all currently say "20% of savings".

## Conflicts with what is built now
- **Hardware is the mentor's focus; in deck v1 it is an appendix slide marked "hypothesis".** We have no hardware, no thermal data and no cost per point yet. Everything on slide 4 depends on Asher's research. If it does not land, show the hardware as the next step with an honest label, not as a built product.
- **Pricing** (above).
- **Downtime:** already demoted in deck v1 to one event and a "shown, never priced" line. Consistent with the feedback.
- **Health score and live monitoring** are named as demo features but are not in the app.

## Open readings to confirm
- "sao" = situation, action, outcome?
- "built score": a score for how the equipment was built or specified, or a typo for "health score"?
- "no internet": the device works offline on site, or the data never leaves the plant?

---

## Raw notes (unchanged)
```
story is good

focus on the hardware product, where does data go, cost, impacts

make app proof of concept tell story begin with selecting the granite, then have it emphasize the cost savings, down time reduction, etc

model, dont make it percent of savings conflict of interest, better ways for variable pricing

pitch deck 
story

sao

situation give example of pm .

slides

embed in demo, 

subjective down time number, 

dont know the health of their plant equipment, capital assets

problem percent of health, problems leads to productivity x, y, z issues
lost revenue etc 1 page

solution, tiered data steps
hardware fixes the gap, diagram, thermal camera - > sensing 
for diagnostics
data flow, where data goes, etc, no internet, platform expansion comes later , hardware understands what its measuring, finds anomolies in data thermal etc

concise way 

ai to monitor health through hardware, photos, other data etc, anomoiles, specs 
platform to show what it looks like from a user perspective

portfolio , for pe firm application company segregated,

top down, 

plant view, operating, differentiator features, live monitoring, actions, issues detecting to sourcing, health score, human review, built score, 

problem, solution , demo (health score, key feature, live monitoring, strategic sourcing)
```
