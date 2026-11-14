# Git workflow (keep it simple)

- `main` must always run. Work on short branches: `a/generator`, `b/alerts`, and so on.
- Commit early and push often. Merge to `main` with a quick PR, or straight away if the other person is mid-task. Just say so in chat.
- Never commit `data/generated/`, `.env`, or API keys (they're gitignored).
- API keys go in `.env` (`ANTHROPIC_API_KEY=...`) and are loaded by `brief.py`.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m afterlife.generate          # writes data/generated/
python -m afterlife.evaluate          # prints accuracy
streamlit run app/streamlit_app.py
```
