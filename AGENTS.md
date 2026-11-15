# AGENTS.md

**Equipment Health Index** (working name) is the system of record for aging plant equipment (Kearney × PERLab hackathon, Startup track):
1. Take photos of nameplates and control cabinets, plus a plant's equipment list and storeroom stock.
2. Identify the machines and their components with off-the-shelf Claude vision.
3. Check each one against a lifecycle knowledge base and build a registry: fund/company → plant → line → machine → component.
4. Output the CapEx cliff, the single points of failure, and sourcing (shelf at any plant first, then outside). For a deal, also output "pay $X less".

## Strategy (DECIDED; follow it, don't contradict it)
- **Customers:** multi-plant manufacturers **and** PE portfolios (not PE first).
- **Main way in:** a manufacturer evaluating its **own plants**. No deal needed.
- **An acquisition is ONE way in**, not the main one. The deal market is too small to rely on (~670 reviewed US deals a year, ≤ ~$10M). A seller's pre-exit scan is another way in.
- **Keep the liquidity angle:** freeing up cash (idle spares, targeted CapEx, cleaner exits, verified collateral). Label it a hypothesis until research backs it.
- **Don't pick prices.** Prices come from Brandon's financial model. **No revenue share / share of savings** (decided Nov 15, mentor advice): "money saved" can't be audited, so a share of it is a conflict of interest for both the firm and the plant. Use fixed fees (e.g. per plant, per device).
- **Downtime avoided is the headline financial figure** (lost revenue is what industrial companies care about most).
- **We don't replace appraisers or engineers.** They keep the sign-off.
- **Source of truth:** `docs/plan/roadmap-equipment-xray.md`. If another doc disagrees, the roadmap wins. `docs/plan/idea-equipment-xray.md` is HISTORICAL (deal-only framing).

## Read first
- `docs/plan/roadmap-equipment-xray.md`: strategy, system components, sourcing rules, phases (**source of truth**)
- `docs/team/roles.md`: who owns what, checkpoints
- `docs/build/registry-format.md`: the data format
- `docs/build/interfaces.md`: function signatures, API routes, demo portfolio scale, demo script (**build the DEMO, not the full model**)
- `docs/plan/pivot-plan/`: POC scope, demo script, tech stack, deck map
- `docs/research/`: market validation, deep-dive numbers, Brandon's market/PE/flywheel research, research backlog

## Layout
```
xray/          Python package: matching.py (normalize + fuzzy match), evaluate.py (precision/recall vs answer key)
api/main.py    FastAPI
web/           Next.js 15 + Tailwind + Recharts (src/app, src/components, src/lib/api-types.ts)
tests/         pytest
scripts/       checkpoint.sh, export_openapi.py
docs/          plan/, team/ (workflow, handoffs inboxes), research/ (velocity.md)
```
The previous project (Afterlife) is in the tag `archive/afterlife-main`.

## Commands
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
cd web && npm install && npm run dev
./scripts/checkpoint.sh                   # tests + type check (same as CI)
python scripts/export_openapi.py && (cd web && npm run types:api)   # after API changes
```

## Conventions
- Work on a branch, and merge to `main` with a PR.
- Every number we show carries its evidence: photo, reading, source, confidence. Show ranges, not false precision.
- Measure accuracy against a synthetic test factory with planted answers. Don't assume it.
- Matching code must not hardcode manufacturer or part names. Abbreviations are data.
- Sourcing: use official APIs and partner feeds, and respect each site's terms of use. Show counterfeit risk for sellers that aren't authorized.
- Model: `claude-sonnet-5-5` (`XRAY_LLM_MODEL` in `.env.example`).
- Never commit `.env` or API keys.
