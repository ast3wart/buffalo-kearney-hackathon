# Git workflow

1. **Work on a branch** named after the topic, e.g. `mvp/vision-extract`. Commit and push as often as you like.
2. **Before pushing, run `./scripts/checkpoint.sh`.** GitHub runs the same checks on every push (✅/❌ next to each commit).
3. **Merge to `main` with a PR** after a quick skim by the other person. Use "Create a merge commit", then delete the branch.
4. **Tell the other person when you change something they depend on** (data model, shared code, API shapes, demo script): one line in their inbox ([handoffs/](handoffs/README.md)).
5. **Never commit** `.env` or API keys (gitignored).

## Setup (once)
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
(cd web && npm install)
cp .env.example .env                    # add ANTHROPIC_API_KEY
cp web/.env.example web/.env.local      # API URL for the Next.js app
```

## Old work
Afterlife and its branches are saved as tags (`git tag -l 'archive/*'`). To restore one: `git checkout -b <name> archive/<tag>`.
