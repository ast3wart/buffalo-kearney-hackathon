#!/usr/bin/env bash
# Run the demo in FAST mode: production web build + API with warm caches.   ./scripts/demo.sh
set -e
cd "$(dirname "$0")/.."
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
[ -f demo.db ] || $PY scripts/seed.py
pkill -f "uvicorn api.main:app" 2>/dev/null || true
lsof -ti tcp:3000 | xargs kill 2>/dev/null || true
lsof -ti tcp:8000 | xargs kill 2>/dev/null || true
$PY -m uvicorn api.main:app --port 8000 > /tmp/xray-api.log 2>&1 &
(cd web && npm run build >/tmp/xray-build.log 2>&1 && npm start >/tmp/xray-web.log 2>&1) &
until curl -s localhost:8000/health >/dev/null && curl -s -o /dev/null localhost:3000; do sleep 1; done
echo "Equipment X-Ray running: http://localhost:3000  (API http://localhost:8000/docs)"
