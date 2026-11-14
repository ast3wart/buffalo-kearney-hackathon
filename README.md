# Buffalo · Kearney × PERLab Hackathon (Nov 13–15, 2026)

Team: Asher + Brandon

## Plan
Read **[docs/game-plan.md](docs/game-plan.md)**, or open **[docs/game-plan.html](docs/game-plan.html)** in a browser for the interactive version (download it, or enable GitHub Pages on `/docs`). It has the interactive track scorecard, the strategy, the build schedule, and the demo script.

**Pick:** Corporate Track 3, **BOM Cost Linkage**. This is a tool that links a company's BOMs to its spend cube (including spare and warranty parts), so you can see the true cost per BOM, find price variance across suppliers, and size savings.

## Key deadlines
- Sat 11 PM: venue closes
- **Sun 8:30 AM: submissions due**
- Sun 9:30 AM: judging · 3:30 PM: finalist pitches

## Must-dos
- [ ] Confirm with a mentor that the "hardware only" emphasis applies only to the Startup track
- [ ] Use Velocity (Growth Signals) and show it in the pitch (see the plan)
- [ ] Ask whether Kearney is providing sample BOM and spend data

## Planned layout
```
data/generate.py      synthetic BOMs + spend with planted links and noise
bomlink/              normalize, match, rollup, levers, evaluate
app/streamlit_app.py  UI
tests/
```
