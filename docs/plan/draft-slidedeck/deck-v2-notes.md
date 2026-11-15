# Deck v2: what was left out, what Asher fills, and how the numbers are derived

**[deck-v2.html](deck-v2.html)** follows the mentor layout in [final-refinements/05](../../archive/planning-notes/05-feedback-notes.md): **8 main slides** (title, problem, solution ×2, demo, financials ×2, close) and **9 appendix slides**. v1 is kept as [deck-v1.html](deck-v1.html). Built Sat Nov 14, ~11:45 PM, numbers from a clean rebuild of `demo.db` on `brandon/downtime-horizon`.

| # | Slide | Status |
|---|---|---|
| 1 | Title | Done |
| 2 | Problem: owners do not know the health of their equipment | Done (stats, no named case) |
| 3 | Solution: the data ladder, hardware on top | Done |
| 4 | Solution: the hardware | **8 dashed boxes for Asher** |
| 5 | Demo (Asher): fund → plant → the part that can stop a line | Done; two demo steps are not in the app (below) |
| 6 | Financials (Brandon): direct savings counted vs downtime shown, never priced | Done; script in [financials-script.md](financials-script.md) |
| 7 | Financials (Brandon): business model, fee by what the customer can count | Done; sensor price to set |
| 8 | Close: pilots and what comes next | Done |
| A1–A9 | Formulas · proof · business case and price · customer and market · competition · objections · roadmap · deal view · sources | Done |

## 1. For Asher: the empty spots on slide 4
Search the file for `ASHER`. Replace the italic text in each dashed box; keep it to one line.

| Box | What goes in it |
|---|---|
| Device picture | A photo or drawing of the thermal camera on or inside a control cabinet |
| Cost per point | Device price + install, per cabinet |
| Works offline | How it runs with no plant internet (processing on the device?) |
| Where data goes | Stored where, synced how, who can see it |
| Impact | How much warning before a failure; which failures heat does and does not catch |
| Step 1 Sense | What is measured, how often, temperature range |
| Step 2 Know the part | Which rated limits from the registry the device uses |
| Step 3 Find anomalies | The rule or model, the threshold, the false-alarm rate |
| Step 4 Alert | How an alert leaves the device without internet |

The black text in steps 1–4 is my wording of the mentor's notes, not research. Change it if the research says otherwise. Step 5 (the registry shows the spare or the source) is built. After editing, open the file with `#check` on the end of the address to confirm nothing runs past the footer.

## 2. What was left out of the main deck, and why
| Left out | Where it went | Why |
|---|---|---|
| Named case study (TNPL paper mill, anonymous "Company X", ORAFOL, BART) | Dropped | Decided: none fit well. TNPL is small and not US; Company X is anonymous and vendor-reported; BART is transit. Slide 2 uses an illustration, labeled as one, plus four sourced stats. |
| 9.2-year average equipment age | Dropped | A fifth stat on a one-page problem slide; the other four carry the point |
| Worked example table (Kinetix 6000, part number, resale price) | Demo slide 5, in words | The live demo shows it; no need to show it twice |
| Proof numbers (127 / 129 read, 112 of 112 matches, 38 of 119 at risk) | Appendix A2; one line in the slide 5 footer | Mentor: problem, solution, demo. Accuracy is an answer to a question, not part of the story |
| Customer personas and market size ($7.6M–$152M, 25,799 plants) | Appendix A4 | Same reason. Have it ready for "how big is this?" |
| Competition 2×2 | Appendix A5 | Same |
| Price as 20% of savings | **Replaced** in appendix A3 | Mentor: conflict of interest. A3 now shows a flat yearly fee by plant size and keeps the savings as the customer's business case. See §4. |
| Objections table | Appendix A6 | For Q&A |
| Roadmap in six phases | Slide 6 as four words (now, pilots, then, later); detail in A7 | Mentor: platform expansion comes later; keep it to a line |
| Go-to-market, market sensitivity table, liquidity angle, unit economics table | Not in v2 (still in `deck-v1-long.html`) | Lowest value per second in a short pitch; liquidity is still an unproven hypothesis |
| Yearly downtime totals (portfolio, Waukesha) | Dropped | Subjective, and two of them do not reproduce ([final-refinements/04](../../archive/planning-notes/04-downtime-waukesha-discrepancy.md)). One Toledo event is shown instead. |
| Deal view ($429k pay less) | Appendix A8 | A second way in, not the story |
| "Condition sensing" slide marked hypothesis, with ⚠ cite flags | Replaced by slide 4 | Hardware is now the focus; the unknowns became fill-in boxes instead of caveats |

## 3. How the numbers on slide 5 are derived
### Health score: 54 / 100 at Toledo ⚠ proposed, not in the app
The app computes **part health** only (`xray/health.py`):
- Life used = age ÷ typical life (midpoint of the knowledge-base range).
- **Replace ASAP** if the life left is shorter than the time needed to get a replacement.
- **Replace soon** if 75% or more of typical life is used.
- Otherwise **working**. Parts we could not identify are not scored.

The roll-up to one score is **mine, written for this deck**:

`score = weighted average of (working 100, replace soon 50, replace ASAP 0)`, line-stopping parts count double, unidentified parts excluded.

| Plant | Working | Soon | ASAP | Not identified | Score |
|---|---|---|---|---|---|
| Toledo | 16 | 3 | 14 | 2 | **54** |
| Fort Wayne | 14 | 3 | 6 | 4 | 66 |
| Lima | 8 | 2 | 4 | 2 | 62 |
| Waukesha | 10 | 4 | 4 | 3 | 62 |
| Oshkosh | 7 | 3 | 7 | 3 | 44 |
| **5 owned plants** | 55 | 15 | 35 | 14 | **58** |
| Tillman (target) | 0 | 1 | 7 | 2 | **4** |

Things to know before presenting it:
- **It is not a screen in the app.** If the demo shows a health score, someone has to add the roll-up (small: it reuses `health.compute`).
- **The point values and the double weight are judgment calls.** Say so if asked.
- **It is based on age and lifecycle, not on measured condition.** That is exactly the gap slide 4 says the hardware closes, so the two slides support each other.
- Health depends on today's date, so the counts move slowly over time.

### Money saved: $47.7k a year at Toledo
From `xray/pricing.py`, base case, whole-plant quote. Four levers, summed:

| Lever | Formula | Toledo, base |
|---|---|---|
| Spares carrying cost avoided | excess spares (15% of stock value; range 10–25%) × carrying cost % | $16.6k |
| Rush premiums avoided | yearly rush premiums × 20% avoided (10–30%) | $7.8k |
| Purchases a sister-plant spare avoids | per covered part: failure chance per year × (part value − transfer cost) | $10.5k |
| Planned instead of emergency replacement | per at-risk part: failure chance × replacement cost × emergency premium (30%; 10–60%) × 50% haircut | $12.9k |
| **Total** | | **$47.7k** (range $9k–165k) |

- The last two levers are computed on the scanned parts and then **divided by the share of the plant scanned** (machines scanned ÷ estimated machines at 0.55 per employee). This is the "extrapolated" label. It is the largest assumption in the number.
- Failure chance per year by age: 3% under 10 years, 6% at 10–20, 8% over 20.
- **Not in the total:** $79k of spares cash freed once, and downtime avoided.

### Downtime: 176 h → 40 h, about $84k at stake
One event, the Toledo Line 2 servo drive (`PA-L2-M01-C1`):
- Without a spare: 48–176 hours down. With Fort Wayne's spare: 18–40 hours (transfer plus swap).
- At stake = hours saved × margin per hour × 60% of output not made up later = ~$84k (range $5k–249k).
- Margin per hour = line revenue per day ÷ 16 operating hours × contribution margin.
- Chance it fails within 3 years: about 17%. Expected value about $12k, which is why the yearly figure is small and is not the headline.

## 4. Which formulas go in the deck, which stay in the appendix
| Formula | Where | Why |
|---|---|---|
| Health score (points and double weight) | **Slide 5**, one line | Three numbers and one rule; a judge can check it in their head |
| Money saved (the four levers, as words) | **Slide 5**, one line | Shows the savings are countable things, not a guess |
| Downtime as one event | **Slide 5**, as a statement | No formula on the slide; the before and after hours are the message |
| Part health rule (ASAP / soon / working) | Appendix A1 | Needed only if someone asks what feeds the score |
| Each lever's inputs and ranges | Appendix A1 | Too many percentages for a main slide |
| Whole-plant scale-up | Appendix A1 | Important to disclose, distracting to lead with |
| Downtime expected value (failure chance, 3-year horizon, discount rate, outage cap) | Appendix A1 | Three judgment calls; the mentor called this number subjective |
| Failure chance by age | Appendix A1 | An input, not a result |

Rule used: **on a main slide, a formula has to fit on one line and use only things the audience can count.** Anything with a probability, a discount rate or a scale-up factor goes to the appendix.

## 5. Decisions made in v2 (change if you disagree)
- **Price:** appendix A3 shows "a flat yearly fee by plant size, about $4–10k per demo plant". The dollars are the same ones the 20%-of-savings model produced ($4.2k Waukesha to $9.5k Toledo); only the basis is reworded. `xray/pricing.py` and the app still compute 20% of savings. The hardware price per point is marked "to set".
- **Market size** in A4 still uses about $5.9k per plant and now says "registry only, no hardware".
- **Slide 5 names "live monitoring" and "health score" as demo steps.** Neither is in the app. Either add them, or say "next" when you reach those steps.
- **Slide 2's situation is an illustration**, and the footer says so.
