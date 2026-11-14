# Afterlife

**Kearney × PERLab Hackathon · Corporate Track 3: BOM Cost Linkage · Team Buffalo (Asher + Brandon)**

> Every BOM team will show you what a product costs. We show you the warranty problem coming before it costs you, and which supplier pays for it.

Afterlife links a manufacturer's **BOMs ↔ production spend ↔ spare-part spend ↔ warranty claims** (including claims with no part number), spots a **shared part failing across products** early, and writes a **supplier brief** covering warranty recovery and spare-part price harmonization.

## ⏰ Deadlines
| | |
|---|---|
| Sat 12:30 / 6 PM | Integration checkpoints |
| Sat 10 PM | Feature freeze |
| **Sun 8:30 AM** | **Submission due** |
| Sun 9:30 AM / 3:30 PM | Judging / finalist pitches |

## 🗺 Where things are
| If you want… | Go to |
|---|---|
| **Start here: BOMs, spend cubes, claims primer** (download and open in a browser) | [docs/learn/boms-and-spend-cubes.html](docs/learn/boms-and-spend-cubes.html) |
| What we're building and why | [docs/plan/concept.md](docs/plan/concept.md) |
| What's in and out of scope | [docs/plan/scope.md](docs/plan/scope.md) |
| The hour-by-hour plan | [docs/plan/schedule.md](docs/plan/schedule.md) |
| **Who does what** | [docs/team/roles.md](docs/team/roles.md) |
| **Checkpoints (when we stop and review each other)** | [docs/team/checkpoints.md](docs/team/checkpoints.md) |
| Handoffs between us | [docs/team/handoffs.md](docs/team/handoffs.md) |
| Git and setup | [docs/team/workflow.md](docs/team/workflow.md) |
| **The data formats (the contract between us)** | [docs/build/data-contract.md](docs/build/data-contract.md) |
| How the pieces fit | [docs/build/architecture.md](docs/build/architecture.md) |
| Real-world numbers (SEC, NHTSA) | [docs/research/data-sources.md](docs/research/data-sources.md) |
| Velocity prompts and log (required!) | [docs/research/velocity.md](docs/research/velocity.md) |
| Questions for mentors and for us | [docs/research/open-questions.md](docs/research/open-questions.md) |
| Demo script / judge Q&A | [docs/pitch/](docs/pitch/) |
| How we picked the track | [docs/archive/track-decision.md](docs/archive/track-decision.md) |

## 🧱 Stack
Python (pandas, DuckDB, rapidfuzz) → `results.duckdb` → FastAPI → Next.js 15 + Tailwind + Recharts · Claude API for the brief.
Details: [docs/build/architecture.md](docs/build/architecture.md) · endpoints and screens: [docs/build/api.md](docs/build/api.md)

## 📁 Code layout (🛠 = Warranty thread · Brandon, 💲 = Spend thread · Asher)
```
afterlife/                  Python pipeline
  io.py                     shared loader (data/generated/ → falls back to data/sample/)
  run.py                    runs everything → results.duckdb
  generate.py               orchestrates the two generators below
  generate_spend.py    💲   products, BOMs, builds, purchase lines
  generate_claims.py   🛠   failure codes, warranty claims, planted spike
  match.py                  shared normalize() + link_all()
  match_spend.py       💲   purchase line → part
  match_claims.py      🛠   claim → causal part
  detect.py            🛠   spike detection
  cost.py              💲   build vs lifecycle cost, spare-part markups
  evaluate.py               accuracy vs planted answers (shared)
  brief.py                  supplier brief (🛠 warranty section, 💲 pricing section)
api/main.py                 FastAPI (reads results.duckdb)
web/                        Next.js app (types generated from the API)
data/sample/                small dataset to build against now
data/reference/             real SEC warranty data
scripts/                    make_sample.py, fetch_sec_warranty.py, export_openapi.py
tests/
```

## ▶️ Run
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
(cd web && npm install)
python -m afterlife.run                      # → results.duckdb
uvicorn api.main:app --reload --port 8000    # API: localhost:8000/docs
cd web && npm run dev                        # app: localhost:3000
```
