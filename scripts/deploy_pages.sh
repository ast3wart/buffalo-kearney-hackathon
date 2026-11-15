#!/usr/bin/env bash
# Publish a static snapshot of the app (pitch deck, demo, appendix) to GitHub Pages.   ./scripts/deploy_pages.sh
# Pages are pre-rendered from the local API, so the published site needs no server. Read-only snapshot.
set -e
cd "$(dirname "$0")/.."
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
BASE="/${PAGES_REPO:-buffalo-kearney-hackathon}"
REMOTE=$(git remote get-url origin)
OWNER=$(gh repo view --json owner -q .owner.login 2>/dev/null || echo "<owner>")

$PY scripts/seed.py >/dev/null
lsof -ti tcp:8000 | xargs kill 2>/dev/null || true
$PY -m uvicorn api.main:app --port 8000 > /tmp/xray-api-pages.log 2>&1 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT
until curl -s localhost:8000/health >/dev/null; do sleep 1; done

# label photos (served by the API locally) go next to the pages
rm -rf web/public/files && mkdir -p web/public/files/refphotos
for d in data/seed/demo/*/photos; do p=$(basename "$(dirname "$d")"); mkdir -p "web/public/files/photos/$p"; cp "$d"/*.jpg "web/public/files/photos/$p/"; done
cp data/reference/photos/*.{jpg,png} web/public/files/refphotos/ 2>/dev/null || true

(cd web && rm -rf .next out && STATIC_EXPORT=1 NEXT_PUBLIC_BASE_PATH="$BASE" npm run build)
rm -rf web/public/files
touch web/out/.nojekyll

# push web/out to the gh-pages branch
TMP=$(mktemp -d)
cp -R web/out/. "$TMP/"
cd "$TMP"
git init -q -b gh-pages
git add -A
git commit -qm "Static site snapshot $(date -u +%Y-%m-%dT%H:%MZ)"
git push -qf "$REMOTE" gh-pages
echo "Published: https://${OWNER}.github.io${BASE}/"
