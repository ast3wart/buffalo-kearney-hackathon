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
| Handoffs between us | [docs/team/handoffs.md](docs/team/handoffs.md) |
| Git and setup | [docs/team/workflow.md](docs/team/workflow.md) |
| **The data formats (the contract between us)** | [docs/build/data-contract.md](docs/build/data-contract.md) |
| How the pieces fit | [docs/build/architecture.md](docs/build/architecture.md) |
| Real-world numbers (SEC, NHTSA) | [docs/research/data-sources.md](docs/research/data-sources.md) |
| Velocity prompts and log (required!) | [docs/research/velocity.md](docs/research/velocity.md) |
| Questions for mentors and for us | [docs/research/open-questions.md](docs/research/open-questions.md) |
| Demo script / judge Q&A | [docs/pitch/](docs/pitch/) |
| How we picked the track | [docs/archive/track-decision.md](docs/archive/track-decision.md) |

## 📁 Code layout
```
afterlife/            the pipeline (a Python package)
  io.py               shared loader: uses data/generated/, falls back to data/sample/
  generate.py   [A]   synthetic data with planted links and a failure spike
  match.py      [A]   linking engine
  evaluate.py   [A]   precision / recall vs planted answers
  detect.py     [B]   early-warning spikes
  cost.py       [B]   build vs lifecycle cost, spare-part markups
  brief.py      [B]   supplier brief
app/streamlit_app.py [B]  demo UI
data/
  sample/             small hand-shaped dataset (commit), to build against now
  generated/          output of generate.py (gitignored)
  reference/          real public data (SEC warranty 2024)
scripts/              make_sample.py, fetch_sec_warranty.py
tests/
```

## ▶️ Run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_sample.py        # (already committed) rebuild data/sample/
pytest -q
streamlit run app/streamlit_app.py
```
