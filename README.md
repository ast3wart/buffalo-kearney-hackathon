# Equipment Health Index

**Kearney × PERLab Hackathon · Startup track · Team Buffalo (Asher Stewart, Brandon Baarsma)**

> A live registry of every critical part across a PE portfolio of industrial plants. It scores each part's health, flags what will stop a production line, and turns that into dollars saved.

## The problem
Unplanned downtime costs the world's 500 largest companies about **$1.4 trillion a year** (Siemens, 2024). The parts that stop a line are usually small and old: a 20-year-old drive, a discontinued relay, a controller nobody makes anymore. Plants follow their maintenance schedules, but almost nobody tracks the **health of the electronics inside their control cabinets**. Most plants run a maintenance system, but only ~15% of those keep part-level records (Velocity research).

## What it does
We play a consulting firm hired by **Granite Ridge Capital**, a (fictional) Midwest private equity firm with two portfolio companies, five plants and one acquisition on the table.

1. **Identify.** Photos of nameplates and cabinet labels are read by Claude vision into part number, maker, serial and date code. Unclear characters are flagged, never guessed.
2. **Register.** Each part is matched to a lifecycle knowledge base (active / discontinued, rated life, successor) and placed in fund → company → plant → line → machine → part.
3. **Score health.** A survival model combines age, heat, sensor anomalies and drive fault logs into one number: the chance the part survives the next 12 months (0–100).
4. **Act.** Every at-risk part gets an order-by date and the best way to get one: a spare already at a sister plant first, then the manufacturer or its successor, then marketplaces flagged for counterfeit risk.
5. **Price it.** Auditable savings (spares carrying cost, planned vs emergency buys, rush premiums, sister-plant spares), plus **downtime avoided**, shown separately and never priced.

We also designed the **Cabinet Monitor**, a small DIN-rail box (thermal camera, clamp-on current sensors, cellular modem) that reads parts' temperature and motor current continuously, read-only and off the plant network. Its system diagram is in [docs/plan/hardware/](docs/plan/hardware/cabinet-monitor-diagram.tex) (TikZ).

**What's real and what isn't:** the plants, companies and sensor readings are **fictional / simulated**. Part numbers, lifecycle data, supplier listings and research numbers are **real**, and every number in the app shows its source.

---

## Run the Demo

### Option 1: open it in your browser (no setup)
**https://ast3wart.github.io/buffalo-kearney-hackathon/**

- **Pitch deck:** https://ast3wart.github.io/buffalo-kearney-hackathon/pitch/
- **Appendix** (every formula, assumption and source): https://ast3wart.github.io/buffalo-kearney-hackathon/appendix/

This is a read-only snapshot of the app: every page is pre-rendered, so it needs no server. To change the data and see the numbers move, use option 2.

### Option 2: run it on your computer (about 5 minutes)

**You need:** [Python 3.11+](https://www.python.org/downloads/) and [Node.js 20+](https://nodejs.org/). No API key is needed: the photo readings are cached, so the demo runs offline.

```bash
git clone https://github.com/ast3wart/buffalo-kearney-hackathon.git
cd buffalo-kearney-hackathon

# 1. Python backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Web app
(cd web && npm install)

# 3. Build the demo database and start everything
python scripts/seed.py
./scripts/demo.sh
```

Then open **http://localhost:3000**. (The API and its docs are at http://localhost:8000/docs.)

<details><summary>If <code>demo.sh</code> doesn't work (e.g. on Windows)</summary>

Run the two servers in two terminals:
```bash
uvicorn api.main:app --port 8000                 # terminal 1
cd web && npm run build && npm start             # terminal 2
```
</details>

---

## Watch the pitch
Click **Pitch** in the top bar. That's our presentation, built into the app.
- **← →** (or space) to move between slides, **F** for full screen.
- **Slide 7 is the live demo** running inside the slide: click inside it to use the app. Click outside it, then use the arrows to move on.
- **Slide 11 is the appendix**, also live: every formula, assumption and source, searchable.
- A small **V** next to a number means we found it with **Velocity**, the Kearney × PERLab research platform.

## A 3-minute tour
1. **Portfolio** (home page): Granite Ridge's two companies and five plants, how many critical parts are discontinued, and which spares are sitting idle at sister plants.
2. Click **Toledo, OH**: parts to replace ASAP / soon / working, the **CapEx cliff** (spending needed per year), **savings and our fee**, **downtime avoided**, and the line-stoppers ranked by risk.
3. Open **Line 1 → Komatsu OBS 150-2** (a stamping press): four parts, each with a health score. The **IDEC RH2B-U-AC120V relay** scores **1/100**. It's discontinued, overheating, and no plant has a spare.
4. Click the relay's **where to buy**: its health drivers, the anomaly statistics that caught it, the financial view, and five real distributors selling its successor part.
5. Back on the press, the **Kinetix servo drive** shows the opposite case: failing too, but a spare is on Toledo's own shelf.
6. **Sources** lists every headline number with its source. **Appendix** holds every formula; try searching "weibull", "28%" or "downtime".

## Mess around with the data
Everything is plain CSV files. Edit, rebuild, refresh.

| Try this | Edit | Then run |
|---|---|---|
| Change a part's lifecycle (e.g. mark a PLC discontinued) | `data/reference/kb.csv` (`lifecycle_status`) | `python scripts/seed.py` |
| Add or remove supplier listings | `data/reference/listings.csv` | `python scripts/seed.py` |
| Change a plant's size, spares or money inputs | `data/seed/demo/<plant>/*.csv`, `data/seed/demo/plant_financials.csv` | `python scripts/seed.py` |
| Plant a new failure in the sensor data (e.g. a part that suddenly runs hot) | the `patterns` dict in `scripts/make_condition_data.py` | `python scripts/make_condition_data.py && python scripts/seed.py` |
| Change model assumptions (failure odds, outage caps, discount rates) | `xray/params.py`, `xray/condition.py` (top of file) | restart the API |
| Read a new label photo with Claude (needs `ANTHROPIC_API_KEY` in `.env`) | add a photo to `data/seed/demo/<plant>/photos/` | `python scripts/read_photos.py` |

After `seed.py`, restart the API (`./scripts/demo.sh` does both servers) and refresh the browser. Plant IDs: PA Toledo, PB Fort Wayne, PC Lima, PD Waukesha, PE Rockford (the acquisition target), PF Oshkosh.

**Check nothing broke:** `./scripts/checkpoint.sh` runs the tests (accuracy floors against the planted answer key) and the type check.

**Republish the online version** (option 1) after changes: `./scripts/deploy_pages.sh` pre-renders every page from your local API and pushes it to the `gh-pages` branch.

---

## How it's built
- **Backend:** Python (pandas, numpy), FastAPI, SQLite. `xray/` holds the logic: `extract.py` (Claude vision), `matching.py` (part matching), `condition.py` (health model), `anomaly.py` (statistics), `health.py` (actions), `sourcing.py`, `valuation.py` and `pricing.py` (money).
- **Frontend:** Next.js 15, Tailwind, Recharts (`web/`). The deck is `web/src/components/Deck.tsx`.
- **Test factory:** six synthetic plants with planted answers (`data/truth/`), so accuracy is measured, not assumed: 127/129 labels read exactly, 100% matching precision, 5/5 planted failures caught.
- **Research:** 20+ Velocity research prompts, logged in [docs/research/velocity.md](docs/research/velocity.md).

| Where | What |
|---|---|
| [docs/plan/roadmap-equipment-xray.md](docs/plan/roadmap-equipment-xray.md) | strategy and roadmap |
| [docs/plan/cabinet-monitor.md](docs/plan/cabinet-monitor.md) · [docs/plan/hardware/](docs/plan/hardware/) | the Cabinet Monitor and its diagram |
| [docs/plan/financials/](docs/plan/financials/) | the money model spec |
| [docs/plan/draft-slidedeck/](docs/plan/draft-slidedeck/) | earlier HTML drafts of the deck and the financials speaker script |
| [docs/research/](docs/research/) | market validation, Velocity log, benchmarks |
| [docs/build/](docs/build/) | data format and interfaces |
| [docs/archive/](docs/archive/) | earlier planning notes |

## Previous project
Before pivoting we built **Afterlife** (BOM cost linkage). It's saved in the git tag `archive/afterlife-main`.
