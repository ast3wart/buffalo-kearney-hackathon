# Kearney Hackathon Game Plan

> The interactive version (scorecard sliders and checklist) is [track-decision.html](track-decision.html).

## Recommendation: Corporate Track 3, BOM Cost Linkage

The "do hardware" emphasis was about the **Startup** track. The Corporate tracks each ask you to "build a tool", so software is exactly right there. BOM Cost Linkage is the track closest to what Kearney sells (procurement and cost transformation), and "spend cube" scares most teams off. That means fewer competitors and judges who care a lot.

**Confirm tonight:** ask a mentor whether the hardware emphasis applies only to the Startup track.

## Scorecard (1–5, default weights in parentheses)

| Option | Judge fit (5) | Doable in 35h (4) | Demo wow (3) | Few competitors (3) | Our interest (4) | Data available (2) | Weighted |
|---|---|---|---|---|---|---|---|
| **BOM Cost Linkage** | 5 | 4 | 4 | 5 | 5 | 3 | **4.48** |
| Rapid Platforming | 5 | 3 | 4 | 4 | 3 | 2 | 3.62 |
| Consumer Insights | 3 | 5 | 3 | 1 | 2 | 5 | 3.05 |
| Startup (hardware) | 3 | 2 | 4 | 3 | 3 | 2 | 2.81 |

## The real problem: matching

Engineering owns the BOM and procurement owns the spend cube. Both describe the same part in different ways.

| Source | Part ID | Description | UoM | Price |
|---|---|---|---|---|
| BOM · Pump P-200 | `100-4471-02` | `BRG,BALL,6204-2RS,20MM` | EA | none |
| Spend · SKF Dist. | `6204-2RSH` | `Deep groove ball bearing 20x47x14 sealed` | EA | $4.12 |
| Spend · Grainger | `1ZGU7` | `BEARING 6204 2RS C3` | BX/10 | $58.90 |
| Spend · Aftermarket | `SP-100-4471` | `SPARE BRG KIT P-200 (WARRANTY)` | KIT | $31.00 |

That's one bearing bought at three different unit prices. Once the BOM and spend data are linked, you can show:
- **True cost per BOM**: actual price paid for every component, including spare and warranty spend
- **Price variance**: the same part bought at different prices, and the $ gap to the best price
- **Shared-part leverage**: parts used in many BOMs and bought from several suppliers can be bundled (this also connects to Track 1)
- **Shock simulation**: if the tariff on country X goes up 25%, which products get hit?

## Five moves most teams won't make
1. **Measured accuracy.** A synthetic generator plants known links and adds noise, so we can report precision and recall.
2. **Confidence tiers plus a human review queue** for the gray zone.
3. **Lead with "spend coverage"**: the % of spend tied to a BOM.
4. **Kearney lever language**: price harmonization, volume bundling, supplier consolidation, spec standardization, aftermarket pricing. Give $ ranges, not single numbers.
5. **Pitch it as a week-1 diagnostic** that replaces weeks of Excel VLOOKUPs.

## Velocity (Growth Signals): required, so make it part of the story

| When | Feature | What to do |
|---|---|---|
| Tonight | Pipeline + Concepts | Add the four options as Concepts and ask the pipeline which is strongest |
| Tonight | Research · Compare approaches | Compare ways to match BOM part numbers to spend lines: rules, fuzzy matching, embeddings, LLM |
| Sat AM | Research · Explore patents | Prior art for a "what's new about ours" slide |
| Sat AM | Guide · Assess a market opportunity | The spend-analytics market (Coupa, Sievo, SpendHQ, Ariba) |
| Sat PM | Research · Find supporting evidence | Typical savings rates, which become our capture rates |
| Sat night | Guide · Make a Concept decision-ready | Upload the README and deck, then screenshot the result for the pitch |

## Matching pipeline
1. **Normalize**: expand abbreviations, convert units (BX/10 → 10 EA) and currency
2. **Exact keys**: internal PN, crosswalk table, manufacturer PN
3. **Attributes**: pull out spec codes (6204, M8x1.25), size, and material
4. **Fuzzy + embeddings**: compare within the same category
5. **LLM judge**: gray zone only, and it returns a reason
6. **Human review**: decisions feed back into the crosswalk

```
bom(product, parent, part_no, qty_per, uom, level)
spend(po_line, supplier, supplier_pn, desc, qty, uom, unit_price, ccy, date, plant, country, spend_type)
link(part_no, po_line, method, confidence, status)
```

**Stack:** Python, pandas, rapidfuzz, embeddings, an LLM API, Streamlit + Plotly (Sankey), SQLite or parquet.

## Schedule (A = data and matching, B = analytics, UI, and pitch)
| When | A | B |
|---|---|---|
| Fri → 11 PM | Schema, generator skeleton | Mentor questions, Streamlit shell |
| Sat 9–12:30 | Noise injection, matcher stages 1–3, eval script | Cost rollup and coverage metric |
| Sat 1:30–7 | Stages 4–5, tune thresholds | Savings levers, price variance, Sankey |
| Sat 7–11 | Review queue | Tariff simulator, feature freeze at 10 PM |
| Sat night | README, backup demo video | Deck, two run-throughs |
| **Sun 8:30 AM** | **Submit** | |

## 4-minute demo
1. **Hook:** "$180M of spend, and only 31% of it is tied to a product. What does the P-200 really cost?"
2. **Run the link:** coverage goes from 31% to 88%
3. **The bearing:** three suppliers, three prices, 12 products, a spare kit at 4× markup
4. **Savings:** the lever table with $ ranges, plus the Sankey
5. **Shock:** the tariff slider
6. **Trust:** accuracy on planted data, plus human review

## Ask a mentor
- Is there sample BOM or spend data?
- Does "hardware focus" apply to the corporate tracks?
- What are the judging criteria and weights?
- How long is the pitch, and does the demo have to be live?
- Are multi-level BOMs in scope? Are LLM APIs allowed?
- What counts as "using" Velocity?

## Judge questions to prep
- What happens to spend that never matches?
- How does this scale to 2M lines? (Answer: blocking by category, and the LLM only sees the gray zone.)
- Where does real data come from? (Answer: ERP flat-file exports.)
- How confident are the savings? (Answer: they're ranges plus a capture rate.)
- Why wouldn't SAP or Coupa already do this?
