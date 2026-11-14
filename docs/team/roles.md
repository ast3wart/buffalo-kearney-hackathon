# Roles: who does what

> **Decide tonight:** put a name next to each role. Then each of you reads your section and the [data contract](../build/data-contract.md).

## Role A: Data & Matching (owner: **TBD**)
*Builds the "is it real and does it work" half. Best fit: whoever is stronger at Python and data wrangling.*
- [ ] `afterlife/generate.py`: realistic data with planted links and a failure spike (M1)
- [ ] `afterlife/match.py`: exact → failure code + BOM → fuzzy (M2)
- [ ] `afterlife/evaluate.py`: accuracy numbers (M3)
- [ ] `scripts/fetch_sec_warranty.py` → calibration numbers for the generator and the SEC slide
- [ ] README "how to run" section
- [ ] Pitch: presents the **"how it works + accuracy"** part

## Role B: Signals, Brief & App (owner: **TBD**)
*Builds the "so what" half people see. Best fit: whoever is stronger at UI, storytelling, and LLM prompting.*
- [ ] `afterlife/detect.py`: early-warning alerts (M4)
- [ ] `afterlife/cost.py`: build vs. lifecycle cost (M5)
- [ ] `afterlife/brief.py`: supplier brief (M6)
- [ ] `app/streamlit_app.py`: 3 screens (M7)
- [ ] Deck
- [ ] Pitch: presents the **hook, demo, and $ impact**

## Shared
- [ ] Agree on the data contract (Fri night, together, 30 min)
- [ ] Integration #1 (Sat 12:30) and #2 (Sat 6 PM)
- [ ] Velocity: split the prompts in [../research/velocity.md](../research/velocity.md)
- [ ] Mentor questions (see [../research/open-questions.md](../research/open-questions.md))
- [ ] Two full practice runs of the pitch
- [ ] Submission (Sun 8:30 AM)

## Rules of thumb
- If you're blocked for more than 20 min, say so in chat. Don't grind silently.
- Anything that changes the data contract gets logged in [handoffs.md](handoffs.md).
- Code against `data/sample/` until the generator is ready.
