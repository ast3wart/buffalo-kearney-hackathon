# AGENTS.md

**Afterlife**: links BOMs, production spend, spare-part spend and warranty claims to spot a shared part failing across products early, then writes a supplier brief. (Kearney hackathon, Track 3: BOM Cost Linkage.)

## Layout
```
afterlife/     Python pipeline: generate*.py (synthetic data), match*.py (link lines/claims to parts),
               detect.py (spikes), cost.py, evaluate.py, brief.py, check.py (contract check), run.py
  io.py        shared loader: data/generated/<company_id>/, falls back to data/sample/
  profiles.py  per-company profiles · taxonomy.py  global categories + failure codes
  adapters/    sap.py maps raw SAP field names to contract columns on load
api/main.py    FastAPI, reads results.duckdb only
web/           Next.js 15 + Tailwind + Recharts (src/app, src/components, src/lib/api-types.ts)
data/sample/   small committed dataset (company_id = sample) · data/reference/  real SEC warranty data
data/generated/  generator output, gitignored
docs/          plan/, team/, build/ (data-contract.md, architecture.md, api.md), research/, pitch/
scripts/       checkpoint.sh, make_sample.py, fetch_sec_warranty.py, export_openapi.py
tests/         pytest
```

## Commands
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cp .env.example .env                        # ANTHROPIC_API_KEY optional (template fallback)
python -m afterlife.generate --seed 7       # -> data/generated/<company_id>/
python -m afterlife.check                   # validate data against the contract
python -m afterlife.run                     # -> results.duckdb
uvicorn api.main:app --reload --port 8000
cd web && npm install && npm run dev        # localhost:3000
python -m pytest -q tests                   # tests; ./scripts/checkpoint.sh runs everything
python scripts/export_openapi.py && (cd web && npm run types:api)   # after API changes
```

## Conventions
- `docs/build/data-contract.md` is the source of truth for CSV schemas; changing it means updating `CONTRACT` in `afterlife/check.py` and logging it in the other person's inbox (`docs/team/handoffs/to-asher.md` / `to-brandon.md`). Agree contract changes before building (`docs/team/workflow.md`).
- CSV, UTF-8; dates `YYYY-MM-DD`, months `YYYY-MM`, money USD. Column names follow SAP tables.
- ID examples: product `UV-400`, part `100-4471-02`, supplier `S-017`, PO line `PO-450012-010`, claim `WC-2026-00431`, plant `P-IA1`.
- Part categories and failure codes must come from `afterlife/taxonomy.py`.
- System fields are CSV columns; contract terms are documents in `<company>/supplier_agreements/`, extracted by `afterlife/extract_terms.py` (see "Stored or extracted?" in the data contract).
- Matching/detection/cost code must not hardcode company, part or supplier literals (`tests/test_no_literals.py`).
- Never commit `.env`, `results.duckdb` or `data/generated/`.
