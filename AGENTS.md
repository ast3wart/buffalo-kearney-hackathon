# AGENTS.md

**Equipment X-Ray** (working name) does pre-deal equipment diligence for manufacturing acquisitions (Kearney × PERLab hackathon, Startup track):
1. Take photos of nameplates and control cabinets, plus the target's equipment list.
2. Identify the machines and their components with off-the-shelf Claude vision.
3. Check each one against a lifecycle knowledge base.
4. Output the CapEx cliff, "pay $X less", the single points of failure, and where to source every part.

## Read first
- `docs/plan/idea-equipment-xray.md`: problem, user, workflow, competition, weekend build
- `docs/plan/roadmap-equipment-xray.md`: system components, registry data model, sourcing rules, phases

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
