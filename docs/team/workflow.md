# Git workflow: batch reviews at checkpoints (decided Sat AM)

Two people and about 30 hours, so **no PR for every file.** Each thread works on one long-running branch, and review happens in batches at checkpoints.

## The rules
1. **One long-running branch per thread:** `spend/<topic>` (Asher) and `warranty/<topic>` (Brandon). Commit and push as often as you like.
2. **Before every push: `./scripts/checkpoint.sh` must be green.** GitHub also runs the same checks on every push (`.github/workflows/checks.yml`, ✅/❌ next to each commit). A ❌ on your branch is yours to fix before anything else.
3. **One PR per thread at each review checkpoint**, reviewed and merged together:
   - **CP3 (Sat 12:30)**, **CP5 (Sat 6 PM)**, **CP6 (Sat 9:30 PM, before feature freeze)**
   - The reviewer skims the whole diff. Then both run `./scripts/checkpoint.sh` on the merged `main`.
   - Merge with **"Create a merge commit"**. After merging, start a fresh branch from `main`.
4. **Shared files: tell the other person the moment you push.** Changes to `io.py`, `match.py`, `check.py`, `taxonomy.py`, `profiles.py`, `generate.py`, `make_sample.py`, `data-contract.md`, or `api.md` get a line in the other person's inbox **when you push**, not at the next checkpoint. If the change affects their code *now*, message them as well. Branch from the latest `main`, and merge `main` into your branch often.
5. **Contract changes** (new or renamed columns/tables) get agreed *before* building: a quick message, then the change. Two people adding the same field under different names costs an hour of merging.
6. Never commit `data/generated/`, `.env`, or API keys (gitignored). API keys go in `.env`.

## Setup (once)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
(cd web && npm install)
cp .env.example .env                    # then add ANTHROPIC_API_KEY (optional: brief falls back to a template)
cp web/.env.example web/.env.local      # API URL for the Next.js app
```

## Every session
```bash
python -m afterlife.run                      # rebuild results.duckdb
uvicorn api.main:app --reload --port 8000    # API → localhost:8000/docs
cd web && npm run dev                        # app → localhost:3000
pytest -q                                    # before pushing
./scripts/checkpoint.sh                      # at every checkpoint (docs/team/checkpoints.md)
```
After changing an API response model: `python scripts/export_openapi.py && (cd web && npm run types:api)`
