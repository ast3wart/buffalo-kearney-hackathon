# Equipment Health Index (working name)

**Kearney × PERLab Hackathon · Startup track · Team Buffalo (Asher + Brandon)**

> Anyone can ask an AI what a machine is. We tell a plant owner which hidden parts will stop which production lines, what it'll cost and when, and we show the evidence behind every number.

Factories run on **controllers, drives and screens their manufacturers stopped making**. One failure there can stop a line for weeks, and most plants don't have a full picture of what's inside their machines.

Equipment Health Index takes a plant's equipment list and **photos of nameplates and control cabinets**, and turns them into a **living registry of every machine and every critical part**. From that registry it produces:
- a **CapEx cliff** (equipment spending needed, year by year)
- the **single points of failure**
- **where to source every part**, checking the shelves at your other plants first

The evidence sits behind every number.

**Who it's for:** **multi-plant manufacturers and PE portfolios.**
- **Evaluating your own plants is the main way in.**
- **An acquisition is one way in:** the same scan prices the deal ("pay $X less") and becomes the acquired plant's registry. A seller's pre-exit scan is another.
- Across plants and portfolio companies, owners **share spares, buy together and free up cash**.

**Strategy source of truth:** [docs/plan/roadmap-equipment-xray.md](docs/plan/roadmap-equipment-xray.md).

## ⏰ Deadlines
| | |
|---|---|
| **Sun Nov 15, 8:30 AM** | **Submission due** |
| Sun 9:30 AM / 3:30 PM | Judging / finalist pitches |

## 🗺 Where things are
| If you want… | Go to |
|---|---|
| **The idea**: problem, user, workflow, competition, why us, weekend plan | [docs/plan/idea-equipment-xray.md](docs/plan/idea-equipment-xray.md) |
| **How the system works + roadmap**: registry, sourcing, PE portfolio, phases | [docs/plan/roadmap-equipment-xray.md](docs/plan/roadmap-equipment-xray.md) |
| **Who does what + checkpoints** | [docs/team/roles.md](docs/team/roles.md) |
| **Registry data format (CP0 sign-off)** | [docs/build/registry-format.md](docs/build/registry-format.md) |
| Handoffs between us (two inboxes) | [docs/team/handoffs/](docs/team/handoffs/README.md): [to Brandon](docs/team/handoffs/to-brandon.md) · [to Asher](docs/team/handoffs/to-asher.md) |
| Git workflow | [docs/team/workflow.md](docs/team/workflow.md) |
| **Is the problem big enough? Market validation + recommendation** | [docs/research/market-validation.md](docs/research/market-validation.md) |
| **Deep dive: defensible numbers, market model, consulting-firm breakeven** | [docs/research/deep-dive-numbers.md](docs/research/deep-dive-numbers.md) · `python scripts/market_model.py` |
| Velocity research log (required) | [docs/research/velocity.md](docs/research/velocity.md) |

## 🧭 Status
- **Plan and roadmap drafted.** Waiting on Brandon's yes, no or changes (§13 of the idea doc).
- **MVP not built yet.** It will be the AI diagnostic tool: photos and the equipment list go in; machines and components are identified; each is checked against lifecycle data; out comes the CapEx cliff. It runs on a test factory with planted answers, so we can measure accuracy.
- **Track switch** to Startup is still to be confirmed with the organizers.

## 🧱 What's already here (kept from our previous project)
```
xray/matching.py    name/catalog-number normalization + fuzzy matching (nameplate text → knowledge-base entry)
xray/evaluate.py    precision/recall against a planted answer key
api/main.py         FastAPI shell (/health)
web/                Next.js 15 + Tailwind + Recharts shell (types generated from the API)
tests/              pytest · scripts/checkpoint.sh runs the same checks as CI (.github/workflows/checks.yml)
```

## ▶️ Run
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cp .env.example .env                         # add ANTHROPIC_API_KEY
./scripts/demo.sh                            # FAST demo mode: production build + API (use this on stage)
uvicorn api.main:app --reload --port 8000    # dev API: localhost:8000/docs
cd web && npm install && npm run dev         # app: localhost:3000
./scripts/checkpoint.sh                      # tests + type check
python scripts/export_openapi.py && (cd web && npm run types:api)   # after API changes
```

## 🗄 Previous project (Afterlife)
Before the pivot we built **Afterlife** (Track 3, BOM Cost Linkage), which linked BOMs, spend and warranty claims. Its code and docs are saved in git tags, not on `main`:
```bash
git fetch --tags
git checkout -b afterlife archive/afterlife-main    # everything as it stood on main
git tag -l 'archive/*'                              # the old branches, one tag each
```
