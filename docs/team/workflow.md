# Git workflow (keep it simple)

- `main` must always run. Work on short branches named by thread: `warranty/claims-gen`, `spend/match`, and so on.
- Commit early and push often. Merge to `main` with a quick PR, or straight away if the other person is mid-task. Just say so in chat.
- Never commit `data/generated/`, `.env`, or API keys (they're gitignored).
- API keys go in `.env` (`ANTHROPIC_API_KEY=...`) and are loaded by `brief.py`.

## Setup (once)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
(cd web && npm install)
```

## Every session
```bash
python -m afterlife.run                      # rebuild results.duckdb
uvicorn api.main:app --reload --port 8000    # API → localhost:8000/docs
cd web && npm run dev                        # app → localhost:3000
pytest -q                                    # before pushing
```
After changing an API response model: `python scripts/export_openapi.py && (cd web && npm run types:api)`
