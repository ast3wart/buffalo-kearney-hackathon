# Equipment X-Ray (working name)

**Kearney × PERLab Hackathon · Startup track · Team Buffalo (Asher + Brandon)**

> Anyone can ask an AI what a machine is. We tell a buyer which hidden parts will stop which production lines, what it'll cost and when, and we show the evidence behind every number.

Old manufacturers grow by buying smaller companies, often for their production capacity. Before signing, a buyer rarely sees that the target's machines run on **controllers, drives and screens the manufacturer stopped making**. One failure there can stop a line for weeks.

Equipment X-Ray takes the target plant's equipment list and **photos of nameplates and control cabinets**, and turns them into:
- a **CapEx cliff** (equipment spending needed, year by year)
- **how much less to pay**
- the **single points of failure**
- **where to source every part**

The evidence sits behind every number. After the deal, the same scan becomes a **central registry of every machine and every part** (age, value, replacement date, sourcing). Across a private equity portfolio, companies can then **share spares and buy together**.

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
| Handoffs between us (two inboxes) | [docs/team/handoffs/](docs/team/handoffs/README.md): [to Brandon](docs/team/handoffs/to-brandon.md) · [to Asher](docs/team/handoffs/to-asher.md) |
| Git workflow | [docs/team/workflow.md](docs/team/workflow.md) |
| **Is the problem big enough? Market validation + recommendation** | [docs/research/market-validation.md](docs/research/market-validation.md) |
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
uvicorn api.main:app --reload --port 8000    # API: localhost:8000/docs
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
